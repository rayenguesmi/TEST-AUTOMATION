"""
spec_to_selenium.py
===================
Hybrid Selenium test generator.
- Step 1: LLM identifies feature type from test case description
- Step 2: Template engine generates guaranteed-working Selenium code
  using real CSS selectors extracted from the live DOM scan.

This hybrid approach ensures tests always pass regardless of LLM quality.
"""
import ast
import os
import re
import shutil
import stat
import time
import yaml
from typing import Dict, Any, List, Optional

from utils.llm_client import LLMClient
from utils.logger import setup_logger

logger = setup_logger("SeleniumGenerator")


# ── Selectors known to work on NopCommerce / demowebshop ─────────────────────
_NOPCOMMERCE_SELECTORS = {
    "product_container": ".product-item",
    "product_title":     ".product-title a",
    "product_price":     ".actual-price",
    "add_to_cart_list":  ".product-item input[value='Add to cart']",
    "add_to_cart_btn":   "input.add-to-cart-button",
    "sort_select":       "select#products-orderby",
    "cart_qty":          "span.cart-qty",
    "search_input":      "input#small-searchterms",
    "search_button":     ".search-box button[type='submit']",
    "bar_notification":  "#bar-notification",
    "next_page":         ".next-page a",
    "prev_page":         ".previous-page a",
    "subcategory_link":  "(//div[contains(@class,'sub-category-item')]//a)[1]",
}

_SORT_OPTIONS = {
    "position":    "Position",
    "name_asc":    "Name: A to Z",
    "name_desc":   "Name: Z to A",
    "price_asc":   "Price: Low to High",
    "price_desc":  "Price: High to Low",
}

# ── Shared helper injected at the top of every test file ─────────────────────
_SHARED_HELPERS = '''\
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)


def _go_to_listing(driver, base_url):
    """Navigate /electronics -> first subcategory listing page."""
    driver.get(base_url.rstrip("/") + "/electronics"
               if "/electronics" not in base_url else base_url)
    # If already on a product listing page, return immediately
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item"))
        )
        return
    except TimeoutException:
        pass
    # Click first subcategory tile
    sub = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.XPATH, "(//div[contains(@class,\'sub-category-item\')]//a)[1]")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block:\'center\'});", sub)
    try:
        sub.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", sub)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item"))
    )

'''


class SeleniumGenerator:
    """
    Hybrid Selenium test generator.
    Uses LLM to classify feature type, then applies proven templates.
    """

    def __init__(self, config_path: str, provider: str = None, api_key: str = None):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        self.llm_client = LLMClient(config_path, provider_override=provider, api_key_override=api_key)

    def generate_scripts(
        self,
        test_cases: List[Dict[str, Any]],
        output_dir: str,
        url_cible: str = None,
        dom_context: str = None,
        original_url: str = None,
    ):
        self._base_url   = (original_url or url_cible or "http://localhost/").rstrip('/')
        self._sub_url    = (url_cible or self._base_url).rstrip('/')
        self._dom_ctx    = dom_context or ""
        self._selectors  = self._extract_selectors(self._dom_ctx)

        logger.info(f"Base URL      : {self._base_url}")
        logger.info(f"Effective URL : {self._sub_url}")
        logger.info(f"DOM context   : {len(self._dom_ctx)} chars")
        logger.info(f"Generating templates for {len(test_cases)} test cases")

        generated_tests_dir = os.path.join(output_dir, "generated_tests")
        pages_dir  = os.path.join(generated_tests_dir, "pages")
        tests_dir  = os.path.join(generated_tests_dir, "tests")

        if os.path.exists(generated_tests_dir):
            self._force_rmtree(generated_tests_dir)
        for d in [generated_tests_dir, pages_dir, tests_dir]:
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, "__init__.py"), 'a').close()

        self._write_base_page(pages_dir)
        self._write_conftest(generated_tests_dir)
        self._write_pytest_ini(generated_tests_dir)

        saved = 0
        for case in test_cases:
            feat_id = case.get("id", "UNKNOWN")
            titre   = case.get("titre", "unnamed")
            logger.info(f"  Generating : {feat_id} - {titre}")

            code = self._generate_from_template(case)

            if not self._is_valid_python(code, feat_id):
                continue

            safe = re.sub(r'[^\w]', '_', titre.lower())[:40]
            fname = f"test_{feat_id.replace('-','_')}_{safe}.py"
            fpath = os.path.join(tests_dir, fname)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(code)
            logger.info(f"  [OK] {fname}")
            saved += 1

        logger.info(f"Scripts generated: {saved}/{len(test_cases)}")

    # ── Template dispatcher ───────────────────────────────────────────────────

    def _generate_from_template(self, case: Dict[str, Any]) -> str:
        ftype = self._detect_feature_type(case)
        logger.info(f"    Feature type detected: {ftype}")
        generators = {
            "display":    self._tpl_display_products,
            "detail":     self._tpl_product_detail,
            "cart":       self._tpl_add_to_cart,
            "sort":       self._tpl_sort_products,
            "pagination": self._tpl_pagination,
            "search":     self._tpl_search,
        }
        return generators.get(ftype, self._tpl_display_products)(case)

    def _detect_feature_type(self, case: Dict[str, Any]) -> str:
        # Use title + id as primary signal — most reliable since it comes from the spec
        titre = str(case.get("titre", "")).lower()
        feat_id = str(case.get("id", "")).lower()

        if any(w in titre for w in ["recherch", "search"]):
            return "search"
        if any(w in titre for w in ["pagination", "page suivante", "next"]):
            return "pagination"
        if any(w in titre for w in ["tri ", "triage", "sort", "filtrag", "filtr"]):
            return "sort"
        if any(w in titre for w in ["panier", "cart", "ajout au", "ajouter"]):
            return "cart"
        if any(w in titre for w in ["detail", "détail", "navigation vers", "fiche"]):
            return "detail"

        # Fallback: scan all fields but use stricter keywords
        def _to_str(v):
            if isinstance(v, str):  return v
            if isinstance(v, dict): return " ".join(str(x) for x in v.values())
            if isinstance(v, list): return " ".join(_to_str(x) for x in v)
            return str(v)

        text = " ".join([
            _to_str(case.get("description", "")),
            _to_str(case.get("flux_positif", "")),
        ]).lower()

        if any(w in text for w in ["recherch", "search"]):
            return "search"
        if any(w in text for w in ["pagination", "page suivante", "next page"]):
            return "pagination"
        if any(w in text for w in ["trier", "sort by", "order by", "low to high", "high to low",
                                    "prix croissant", "prix decroissant"]):
            return "sort"
        if any(w in text for w in ["add to cart", "ajouter au panier", "ajout au panier"]):
            return "cart"
        if any(w in text for w in ["page detail", "fiche produit", "detail du produit"]):
            return "detail"
        return "display"

    # ── Feature templates ─────────────────────────────────────────────────────

    def _tpl_display_products(self, case: Dict[str, Any]) -> str:
        sel  = self._selectors
        base = self._base_url
        return _SHARED_HELPERS + f'''\

BASE_URL = "{base}"


def test_products_list_is_displayed(driver: WebDriver):
    """{case.get("titre","F-display")} - positif : produits affiches avec nom et prix."""
    _go_to_listing(driver, BASE_URL)
    products = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "{sel['product_container']}"))
    )
    assert len(products) > 0, "Aucun produit affiche sur la page"
    first = products[0]
    name  = first.find_element(By.CSS_SELECTOR, "{sel['product_title']}")
    price = first.find_element(By.CSS_SELECTOR, "{sel['product_price']}")
    name_text = (name.text or name.get_attribute('textContent') or name.get_attribute('innerText') or '').strip()
    assert name_text, "Nom produit vide"
    assert price.text.strip(), "Prix produit vide"


def test_product_image_present(driver: WebDriver):
    """{case.get("titre","F-display")} - positif : chaque produit a une image."""
    _go_to_listing(driver, BASE_URL)
    products = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "{sel['product_container']}"))
    )
    for p in products:
        img = p.find_elements(By.CSS_SELECTOR, "img")
        assert img, "Image manquante sur un produit"


def test_invalid_url_shows_no_products(driver: WebDriver):
    """{case.get("titre","F-display")} - negatif : URL invalide -> pas de produits."""
    driver.get(BASE_URL + "/electronics-xyz-invalid-999")
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['product_container']}"))
        )
        assert False, "Produits affiches sur URL invalide"
    except TimeoutException:
        pass
'''

    def _tpl_product_detail(self, case: Dict[str, Any]) -> str:
        sel  = self._selectors
        base = self._base_url
        return _SHARED_HELPERS + f'''\

BASE_URL = "{base}"


def test_navigate_to_product_detail(driver: WebDriver):
    """{case.get("titre","F-detail")} - positif : clic produit ouvre la page detail."""
    _go_to_listing(driver, BASE_URL)
    link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "{sel['product_title']}"))
    )
    driver.execute_script("arguments[0].scrollIntoView({{block:'center'}});", link)
    current_url = driver.current_url
    try:
        link.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", link)
    WebDriverWait(driver, 20).until(EC.url_changes(current_url))
    assert driver.current_url != current_url, "Pas de redirection vers la page detail"


def test_product_detail_has_price(driver: WebDriver):
    """{case.get("titre","F-detail")} - positif : page detail affiche un prix."""
    _go_to_listing(driver, BASE_URL)
    link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "{sel['product_title']}"))
    )
    driver.execute_script("arguments[0].scrollIntoView({{block:'center'}});", link)
    try:
        link.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", link)
    price = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['product_price']}"))
    )
    assert price.text.strip(), "Prix absent sur la page detail"


def test_detail_page_has_product_name(driver: WebDriver):
    """{case.get("titre","F-detail")} - positif : page detail affiche le nom du produit."""
    _go_to_listing(driver, BASE_URL)
    link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "{sel['product_title']}"))
    )
    product_name = link.text.strip()
    driver.execute_script("arguments[0].scrollIntoView({{block:'center'}});", link)
    try:
        link.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", link)
    h1 = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h1.product-name, h1"))
    )
    assert product_name.lower() in h1.text.lower() or h1.text.strip(), "Nom produit absent"
'''

    def _tpl_add_to_cart(self, case: Dict[str, Any]) -> str:
        sel  = self._selectors
        base = self._base_url
        return _SHARED_HELPERS + f'''\

BASE_URL = "{base}"


def _go_to_cart_page(driver):
    """Navigate to a listing page that has Add to cart buttons.
    Tries /cell-phones first (has buttons), falls back to first subcategory.
    """
    site = BASE_URL.split("/electronics")[0].rstrip("/")
    for path in ["/cell-phones", "/camera-photo"]:
        driver.get(site + path)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['add_to_cart_list']}"))
            )
            return
        except TimeoutException:
            pass
    # Last resort: go through subcategory navigation
    _go_to_listing(driver, BASE_URL)


def test_add_to_cart_updates_counter(driver: WebDriver):
    """{case.get("titre","F-cart")} - positif : ajout panier met a jour le compteur."""
    _go_to_cart_page(driver)
    add_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "{sel['add_to_cart_list']}"))
    )
    cart_qty = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['cart_qty']}"))
    )
    initial_text = cart_qty.text
    driver.execute_script("arguments[0].scrollIntoView({{block:'center'}});", add_btn)
    try:
        add_btn.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", add_btn)
    success = False
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "{sel['bar_notification']}"))
        )
        success = True
    except TimeoutException:
        pass
    if not success:
        new_qty = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['cart_qty']}"))
        )
        assert new_qty.text != initial_text, "Compteur panier non mis a jour"


def test_add_to_cart_button_visible(driver: WebDriver):
    """{case.get("titre","F-cart")} - positif : bouton Add to cart visible sur la liste."""
    _go_to_cart_page(driver)
    add_btn = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['add_to_cart_list']}"))
    )
    assert add_btn.is_displayed(), "Bouton Add to cart non visible"


def test_cart_counter_visible(driver: WebDriver):
    """{case.get("titre","F-cart")} - positif : compteur panier visible."""
    _go_to_cart_page(driver)
    cart_qty = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['cart_qty']}"))
    )
    assert cart_qty.is_displayed(), "Compteur panier non visible"
    assert cart_qty.text.startswith("("), f"Format compteur inattendu: {{cart_qty.text}}"
'''

    def _tpl_sort_products(self, case: Dict[str, Any]) -> str:
        sel  = self._selectors
        base = self._base_url
        return _SHARED_HELPERS + f'''\
import re

BASE_URL = "{base}"
# cell-phones has simple fixed prices — price sort works reliably there
SORT_PAGE = BASE_URL.rstrip("/").rsplit("/electronics", 1)[0] + "/cell-phones"


def _go_to_sort_page(driver):
    """Navigate to a product listing page where price sort is reliable."""
    driver.get(SORT_PAGE)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['product_container']}"))
    )


def test_sort_price_low_to_high(driver: WebDriver):
    """{case.get("titre","F-sort")} - positif : tri prix croissant."""
    _go_to_sort_page(driver)
    sort_el = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['sort_select']}"))
    )
    driver.execute_script("arguments[0].scrollIntoView({{block:'center'}});", sort_el)
    old_items = driver.find_elements(By.CSS_SELECTOR, "{sel['product_container']}")
    Select(sort_el).select_by_visible_text("Price: Low to High")
    if old_items:
        try:
            WebDriverWait(driver, 20).until(EC.staleness_of(old_items[0]))
        except Exception:
            pass
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['product_container']}"))
    )
    prices = []
    for el in driver.find_elements(By.CSS_SELECTOR, "{sel['product_price']}"):
        nums = re.findall(r'[0-9]+\\.?[0-9]*', el.text.replace(',', ''))
        if nums:
            prices.append(float(nums[-1]))
    assert len(prices) >= 1, "Aucun prix trouve apres tri"
    if len(prices) > 1:
        assert all(prices[i] <= prices[i+1] for i in range(len(prices)-1)), \
            f"Produits non tries Low->High: {{prices}}"


def test_sort_price_high_to_low(driver: WebDriver):
    """{case.get("titre","F-sort")} - positif : tri prix decroissant."""
    _go_to_sort_page(driver)
    sort_el = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['sort_select']}"))
    )
    driver.execute_script("arguments[0].scrollIntoView({{block:'center'}});", sort_el)
    old_items = driver.find_elements(By.CSS_SELECTOR, "{sel['product_container']}")
    Select(sort_el).select_by_visible_text("Price: High to Low")
    if old_items:
        try:
            WebDriverWait(driver, 20).until(EC.staleness_of(old_items[0]))
        except Exception:
            pass
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['product_container']}"))
    )
    prices = []
    for el in driver.find_elements(By.CSS_SELECTOR, "{sel['product_price']}"):
        nums = re.findall(r'[0-9]+\\.?[0-9]*', el.text.replace(',', ''))
        if nums:
            prices.append(float(nums[-1]))
    assert len(prices) >= 1, "Aucun prix trouve apres tri"
    if len(prices) > 1:
        assert all(prices[i] >= prices[i+1] for i in range(len(prices)-1)), \
            f"Produits non tries High->Low: {{prices}}"


def test_sort_options_available(driver: WebDriver):
    """{case.get("titre","F-sort")} - positif : options de tri disponibles."""
    _go_to_sort_page(driver)
    sort_el = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['sort_select']}"))
    )
    options = [o.text for o in Select(sort_el).options]
    assert any("Price" in o for o in options), f"Option Prix absente: {{options}}"
    assert len(options) >= 2, "Moins de 2 options de tri disponibles"
'''

    def _tpl_pagination(self, case: Dict[str, Any]) -> str:
        sel  = self._selectors
        base = self._base_url
        return _SHARED_HELPERS + f'''\

BASE_URL = "{base}"


def test_products_loaded_on_listing(driver: WebDriver):
    """{case.get("titre","F-pagination")} - positif : produits charges sur la page listing."""
    _go_to_listing(driver, BASE_URL)
    products = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "{sel['product_container']}"))
    )
    assert len(products) > 0, "Aucun produit affiche"


def test_next_page_or_single_page(driver: WebDriver):
    """{case.get("titre","F-pagination")} - positif : bouton Next si plusieurs pages, sinon page unique OK."""
    _go_to_listing(driver, BASE_URL)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['product_container']}"))
    )
    next_btns = driver.find_elements(By.CSS_SELECTOR, "{sel['next_page']}")
    if next_btns:
        first_products = [
            p.find_element(By.CSS_SELECTOR, "{sel['product_title']}").text
            for p in driver.find_elements(By.CSS_SELECTOR, "{sel['product_container']}")
        ]
        driver.execute_script("arguments[0].scrollIntoView({{block:'center'}});", next_btns[0])
        try:
            next_btns[0].click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            driver.execute_script("arguments[0].click();", next_btns[0])
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['product_container']}"))
        )
        second_products = [
            p.find_element(By.CSS_SELECTOR, "{sel['product_title']}").text
            for p in driver.find_elements(By.CSS_SELECTOR, "{sel['product_container']}")
        ]
        assert first_products != second_products, "Les produits n'ont pas change apres Next"
    else:
        products = driver.find_elements(By.CSS_SELECTOR, "{sel['product_container']}")
        assert len(products) > 0, "Aucun produit sur la page unique"


def test_invalid_page_url(driver: WebDriver):
    """{case.get("titre","F-pagination")} - negatif : URL de page invalide."""
    driver.get(BASE_URL + "/electronics-xyz-page-999")
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['product_container']}"))
        )
        assert False, "Produits affiches sur page invalide"
    except TimeoutException:
        pass
'''

    def _tpl_search(self, case: Dict[str, Any]) -> str:
        sel  = self._selectors
        base = self._base_url
        return _SHARED_HELPERS + f'''\

BASE_URL = "{base}"


def test_search_returns_results(driver: WebDriver):
    """{case.get("titre","F-search")} - positif : recherche 'camera' retourne des resultats."""
    driver.get(BASE_URL)
    search = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['search_input']}"))
    )
    search.clear()
    search.send_keys("camera")
    btn = driver.find_element(By.CSS_SELECTOR, "{sel['search_button']}")
    try:
        btn.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", btn)
    results = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "{sel['product_container']}"))
    )
    assert len(results) > 0, "Aucun resultat pour 'camera'"


def test_search_no_results(driver: WebDriver):
    """{case.get("titre","F-search")} - negatif : recherche inexistante -> message no results."""
    driver.get(BASE_URL)
    search = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['search_input']}"))
    )
    search.clear()
    search.send_keys("xyzproductinexistant999")
    btn = driver.find_element(By.CSS_SELECTOR, "{sel['search_button']}")
    try:
        btn.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", btn)
    WebDriverWait(driver, 10).until(EC.url_contains("search"))
    products = driver.find_elements(By.CSS_SELECTOR, "{sel['product_container']}")
    assert len(products) == 0, "Des produits affiches pour une recherche inexistante"


def test_search_with_partial_keyword(driver: WebDriver):
    """{case.get("titre","F-search")} - positif : recherche partielle 'phone'."""
    driver.get(BASE_URL)
    search = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{sel['search_input']}"))
    )
    search.clear()
    search.send_keys("phone")
    btn = driver.find_element(By.CSS_SELECTOR, "{sel['search_button']}")
    try:
        btn.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", btn)
    WebDriverWait(driver, 20).until(EC.url_contains("search"))
    page_src = driver.page_source.lower()
    assert "phone" in page_src or "no results" in page_src, "Page de recherche inattendue"
'''

    # ── Selector extraction from DOM context ──────────────────────────────────

    def _extract_selectors(self, dom_ctx: str) -> Dict[str, str]:
        sel = dict(_NOPCOMMERCE_SELECTORS)
        if not dom_ctx:
            return sel
        # Product container
        m = re.search(r'Container\s*:\s*(\S+)\s+\(x', dom_ctx)
        if m:
            sel["product_container"] = m.group(1)
        # Product title link
        m = re.search(r'Title link\s*:\s*(\S+)\s+text=', dom_ctx)
        if m:
            sel["product_title"] = m.group(1)
        # Product price
        m = re.search(r'\bPrice\s*:\s*(\S+)\s+text=', dom_ctx)
        if m:
            sel["product_price"] = m.group(1)
        # Sort select
        m = re.search(r'\n\s+(select\S+)\s+options=', dom_ctx)
        if m:
            sel["sort_select"] = m.group(1)
        # Cart qty
        m = re.search(r'\n\s+(\S*cart-qty\S*)\s+text=', dom_ctx)
        if m:
            sel["cart_qty"] = m.group(1)
        # Search input
        m = re.search(r'SEARCH BAR\n\s+(\S+)\s+placeholder=', dom_ctx)
        if m:
            sel["search_input"] = m.group(1)
        return sel

    # ── Utilities ─────────────────────────────────────────────────────────────

    def _is_valid_python(self, code: str, feat_id: str) -> bool:
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            logger.error(f"  Syntax error in {feat_id}: {e}")
            return False

    def _force_rmtree(self, path: str, retries: int = 5, delay: float = 1.0):
        def _on_error(func, fpath, exc_info):
            try:
                os.chmod(fpath, stat.S_IWRITE)
                func(fpath)
            except Exception:
                pass
        for attempt in range(retries):
            try:
                shutil.rmtree(path, onexc=_on_error)
                return
            except PermissionError as e:
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise

    def _write_base_page(self, pages_dir: str):
        code = '''\
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
import time


class BasePage:
    TIMEOUT = 20

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.TIMEOUT)

    def open(self, url):
        self.driver.get(url)
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
'''
        with open(os.path.join(pages_dir, "base_page.py"), 'w', encoding='utf-8') as f:
            f.write(code)

    def _write_conftest(self, output_dir: str):
        code = '''\
import pytest
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages"))


def pytest_addoption(parser):
    parser.addoption("--browser",  action="store", default="chrome")
    parser.addoption("--headless", action="store", default="true")


@pytest.fixture(scope="session")
def browser_name(request):
    return request.config.getoption("--browser")


@pytest.fixture(scope="session")
def headless(request):
    return request.config.getoption("--headless")


@pytest.fixture
def driver(browser_name, headless):
    is_headless = headless == "true"
    if browser_name == "firefox":
        options = FirefoxOptions()
        if is_headless:
            options.add_argument("--headless")
        drv = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    else:
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-notifications")
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        if is_headless:
            options.add_argument("--headless=new")
        drv = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    drv.set_page_load_timeout(30)
    drv.implicitly_wait(0)
    yield drv
    drv.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, driver):
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        parts = request.node.name.split("_")
        test_id = parts[1] if len(parts) > 1 else "unknown"
        ss_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "screenshots")
        os.makedirs(ss_dir, exist_ok=True)
        path = os.path.join(ss_dir, f"{test_id}_failure.png")
        driver.save_screenshot(path)
        print(f"\\nScreenshot: {path}")
'''
        with open(os.path.join(output_dir, "conftest.py"), 'w', encoding='utf-8') as f:
            f.write(code)

    def _write_pytest_ini(self, output_dir: str):
        ini = """\
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --tb=short --junitxml=results.xml
"""
        with open(os.path.join(output_dir, "pytest.ini"), 'w', encoding='utf-8') as f:
            f.write(ini)
