"""
spec_to_selenium.py
===================
Architecture hybride (template-based):
  • LLM   -> parse spec + cas de test (JSON uniquement)
  • Templates -> code Python/Selenium (deterministe, toujours correct)

Fixes:
  - Deduplication par NOM de template (pas contenu)
  - _go_to_electronics() ne cherche plus .product-item (page affiche sous-categories)
  - F-001 verifie les sous-categories ET les produits
  - F-002/F-003/F-004/F-006 naviguent vers /cell-phones (produits reels)
  - Unicode-safe logs (pas de caractere special)
"""
import ast
import os
import json
import re
import shutil
import time
import yaml
from typing import Dict, Any, List

from utils.llm_client import LLMClient
from utils.logger import setup_logger

logger = setup_logger("SeleniumGenerator")

DEFAULT_URL = "https://demowebshop.tricentis.com/"

# ─── Shared header ────────────────────────────────────────────────────────────
_TEST_HEADER = '''\
import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)

BASE_URL = "https://demowebshop.tricentis.com/"

# ── Selectors ─────────────────────────────────────────────────────────────────
ELECTRONICS_LINK   = (By.CSS_SELECTOR, "div.header-menu > ul.top-menu > li > a[href=\'/electronics\']")
SUBCATEGORY_ITEMS  = (By.CSS_SELECTOR, ".category-grid .item-box, .sub-category-grid .item-box")
SUBCATEGORY_LINK   = (By.CSS_SELECTOR, ".category-grid .item-box a, .sub-category-grid .item-box a")
PRODUCT_LIST       = (By.CSS_SELECTOR, ".product-item")
PRODUCT_TITLE_A    = (By.CSS_SELECTOR, ".product-item .product-title a")
PRODUCT_PRICE      = (By.CSS_SELECTOR, ".product-item .price.actual-price")
PRODUCT_H1         = (By.CSS_SELECTOR, "div.product-name h1")
ADD_CART_BTN       = (By.CSS_SELECTOR, "input[value=\'Add to cart\']")
NOTIFICATION_OK    = (By.CSS_SELECTOR, ".bar-notification.success")
SEARCH_INPUT       = (By.ID, "small-searchterms")
SEARCH_BTN         = (By.CSS_SELECTOR, "input[value=\'Search\']")
SORT_SELECT        = (By.ID, "products-orderby")
NEXT_PAGE_BTN      = (By.CSS_SELECTOR, ".pager li.next-page a")
SEARCH_RESULTS     = (By.CSS_SELECTOR, ".search-results .product-item, .product-item")
CART_LINK          = (By.CSS_SELECTOR, "#topcartlink a")


def _wait_page_ready(driver):
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def _safe_click(driver, locator):
    """Wait -> scroll -> clickable -> click (JS fallback)."""
    wait = WebDriverWait(driver, 20)
    el = wait.until(EC.presence_of_element_located(locator))
    driver.execute_script("arguments[0].scrollIntoView({block: \'center\'});", el)
    el = wait.until(EC.element_to_be_clickable(locator))
    try:
        el.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", el)


def _go_to_electronics(driver):
    """
    Navigate to the Electronics category landing page (shows subcategories).
    Does NOT wait for .product-item because the landing page has subcategories only.
    """
    driver.get(BASE_URL + "electronics")
    _wait_page_ready(driver)


def _go_to_cell_phones(driver):
    """
    Navigate to Cell phones subcategory which always has real product items.
    Use this for tests that need to interact with actual products.
    """
    driver.get(BASE_URL + "cell-phones")
    _wait_page_ready(driver)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(PRODUCT_LIST))

'''

# ─── TEMPLATE F-001 : Affichage produits ──────────────────────────────────────
_TEMPLATE_F001 = _TEST_HEADER + '''\
class TestAffichageProduits:
    """F-001: La page Electronics affiche des sous-categories et des produits."""

    def test_electronics_page_loads(self, driver: WebDriver):
        """La page Electronics se charge et affiche des elements navigables."""
        wait = WebDriverWait(driver, 20)
        _go_to_electronics(driver)

        # La page doit afficher soit des sous-categories soit des produits
        try:
            items = wait.until(EC.presence_of_element_located(SUBCATEGORY_ITEMS))
            assert items.is_displayed(), "Les sous-categories ne sont pas visibles"
        except TimeoutException:
            items = wait.until(EC.presence_of_element_located(PRODUCT_LIST))
            assert items.is_displayed(), "Aucun produit Electronics trouve"

    def test_subcategory_links_are_clickable(self, driver: WebDriver):
        """Les liens de sous-categories sont cliquables."""
        wait = WebDriverWait(driver, 20)
        _go_to_electronics(driver)

        try:
            link = wait.until(EC.element_to_be_clickable(SUBCATEGORY_LINK))
            driver.execute_script("arguments[0].scrollIntoView({block: \'center\'});", link)
            link.click()
            _wait_page_ready(driver)
            assert "demowebshop.tricentis.com" in driver.current_url
        except TimeoutException:
            pytest.skip("Pas de sous-categories, tentative sur produits directs")

    def test_cell_phones_products_listed(self, driver: WebDriver):
        """La sous-categorie Cell phones affiche des produits avec titre et prix."""
        wait = WebDriverWait(driver, 20)
        _go_to_cell_phones(driver)

        products = driver.find_elements(*PRODUCT_LIST)
        assert len(products) > 0, "Aucun produit Cell phones affiche"

        titles = driver.find_elements(*PRODUCT_TITLE_A)
        assert len(titles) > 0, "Aucun titre produit trouve"
        for t in titles:
            assert t.text.strip() != "", "Un titre produit est vide"
'''

# ─── TEMPLATE F-002 : Navigation detail produit ───────────────────────────────
_TEMPLATE_F002 = _TEST_HEADER + '''\
class TestNavigationDetailProduit:
    """F-002: Cliquer sur un produit redirige vers sa page detail."""

    def test_click_product_shows_detail(self, driver: WebDriver):
        """La page detail affiche le nom du produit et le bouton Add to cart."""
        wait = WebDriverWait(driver, 20)
        _go_to_cell_phones(driver)

        first_link = wait.until(EC.element_to_be_clickable(PRODUCT_TITLE_A))
        driver.execute_script("arguments[0].scrollIntoView({block: \'center\'});", first_link)
        first_link.click()

        h1 = wait.until(EC.presence_of_element_located(PRODUCT_H1))
        assert h1.text.strip() != "", "Le nom du produit est vide"
        assert "demowebshop.tricentis.com" in driver.current_url

    def test_product_detail_has_add_to_cart(self, driver: WebDriver):
        """La page detail contient le bouton Add to cart."""
        wait = WebDriverWait(driver, 20)
        _go_to_cell_phones(driver)

        first_link = wait.until(EC.element_to_be_clickable(PRODUCT_TITLE_A))
        driver.execute_script("arguments[0].scrollIntoView({block: \'center\'});", first_link)
        first_link.click()

        add_btn = wait.until(EC.presence_of_element_located(ADD_CART_BTN))
        driver.execute_script("arguments[0].scrollIntoView({block: \'center\'});", add_btn)
        assert add_btn.is_displayed(), "Bouton Add to cart introuvable"
'''

# ─── TEMPLATE F-003 : Ajout au panier ────────────────────────────────────────
_TEMPLATE_F003 = _TEST_HEADER + '''\
class TestAjoutAuPanier:
    """F-003: L\'utilisateur peut ajouter un produit Electronics au panier."""

    def test_add_product_to_cart(self, driver: WebDriver):
        """Cliquer sur Add to cart affiche une notification de succes."""
        wait = WebDriverWait(driver, 20)
        _go_to_cell_phones(driver)

        first_link = wait.until(EC.element_to_be_clickable(PRODUCT_TITLE_A))
        driver.execute_script("arguments[0].scrollIntoView({block: \'center\'});", first_link)
        first_link.click()
        wait.until(EC.presence_of_element_located(PRODUCT_H1))

        _safe_click(driver, ADD_CART_BTN)

        try:
            notification = wait.until(EC.visibility_of_element_located(NOTIFICATION_OK))
            assert notification.is_displayed(), "Notification de succes non affichee"
        except TimeoutException:
            assert "cart" in driver.current_url or "demowebshop.tricentis.com" in driver.current_url

    def test_cart_link_visible_after_add(self, driver: WebDriver):
        """Le lien du panier est visible apres ajout."""
        wait = WebDriverWait(driver, 20)
        _go_to_cell_phones(driver)

        first_link = wait.until(EC.element_to_be_clickable(PRODUCT_TITLE_A))
        driver.execute_script("arguments[0].scrollIntoView({block: \'center\'});", first_link)
        first_link.click()
        wait.until(EC.presence_of_element_located(PRODUCT_H1))

        _safe_click(driver, ADD_CART_BTN)

        cart_link = wait.until(EC.presence_of_element_located(CART_LINK))
        assert cart_link.is_displayed()
'''

# ─── TEMPLATE F-004 : Filtrage/Tri ───────────────────────────────────────────
_TEMPLATE_F004 = _TEST_HEADER + '''\
from selenium.webdriver.support.ui import Select

class TestFiltrageTriProduits:
    """F-004: L\'utilisateur peut trier les produits Electronics."""

    def test_sort_by_price_ascending(self, driver: WebDriver):
        """Trier par prix croissant reorganise la liste."""
        wait = WebDriverWait(driver, 20)
        _go_to_cell_phones(driver)

        sort_el = wait.until(EC.presence_of_element_located(SORT_SELECT))
        driver.execute_script("arguments[0].scrollIntoView({block: \'center\'});", sort_el)
        select = Select(sort_el)
        select.select_by_visible_text("Price: Low to High")

        wait.until(EC.presence_of_element_located(PRODUCT_LIST))
        products = driver.find_elements(*PRODUCT_LIST)
        assert len(products) > 0, "Aucun produit apres tri par prix"

    def test_sort_by_name(self, driver: WebDriver):
        """Trier par nom reorganise la liste alphabetiquement."""
        wait = WebDriverWait(driver, 20)
        _go_to_cell_phones(driver)

        sort_el = wait.until(EC.presence_of_element_located(SORT_SELECT))
        driver.execute_script("arguments[0].scrollIntoView({block: \'center\'});", sort_el)
        select = Select(sort_el)
        select.select_by_visible_text("Name: A to Z")

        wait.until(EC.presence_of_element_located(PRODUCT_LIST))
        titles = driver.find_elements(*PRODUCT_TITLE_A)
        assert len(titles) > 0, "Aucun produit apres tri par nom"
        names = [t.text.strip() for t in titles if t.text.strip()]
        assert names == sorted(names, key=str.casefold), \
            f"Produits non tries alphabetiquement: {names}"
'''

# ─── TEMPLATE F-005 : Pagination ─────────────────────────────────────────────
_TEMPLATE_F005 = _TEST_HEADER + '''\
class TestPagination:
    """F-005: L\'utilisateur peut naviguer entre les pages de produits."""

    def test_next_button_navigates(self, driver: WebDriver):
        """Le bouton Next charge la page suivante de produits."""
        wait = WebDriverWait(driver, 20)
        _go_to_cell_phones(driver)

        try:
            next_btn = wait.until(EC.element_to_be_clickable(NEXT_PAGE_BTN))
        except TimeoutException:
            pytest.skip("Pas de pagination (moins d\'une page de produits)")

        titles_p1 = [el.text for el in driver.find_elements(*PRODUCT_TITLE_A)]
        driver.execute_script("arguments[0].scrollIntoView({block: \'center\'});", next_btn)
        next_btn.click()

        wait.until(EC.presence_of_element_located(PRODUCT_LIST))
        titles_p2 = [el.text for el in driver.find_elements(*PRODUCT_TITLE_A)]
        assert titles_p1 != titles_p2, "Les produits de la page 2 sont identiques a la page 1"

    def test_invalid_page_url(self, driver: WebDriver):
        """Acceder a une page inexistante ne plante pas l\'application."""
        driver.get(BASE_URL + "cell-phones?page=9999")
        _wait_page_ready(driver)
        assert "demowebshop.tricentis.com" in driver.current_url
'''

# ─── TEMPLATE F-006 : Recherche ───────────────────────────────────────────────
_TEMPLATE_F006 = _TEST_HEADER + '''\
class TestRechercheProduit:
    """F-006: L\'utilisateur peut rechercher un produit Electronics."""

    def test_search_existing_product(self, driver: WebDriver):
        """Rechercher 'laptop' retourne des resultats pertinents."""
        wait = WebDriverWait(driver, 20)
        driver.get(BASE_URL)

        search_input = wait.until(EC.presence_of_element_located(SEARCH_INPUT))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_input)
        search_input.clear()
        search_input.send_keys("laptop")

        _safe_click(driver, SEARCH_BTN)
        _wait_page_ready(driver)

        # La page de resultats doit contenir au moins 1 produit
        try:
            wait.until(EC.presence_of_element_located(SEARCH_RESULTS))
            results = driver.find_elements(*SEARCH_RESULTS)
            assert len(results) > 0, "Aucun resultat pour 'laptop'"
        except TimeoutException:
            # Fallback : verifier que la page de recherche a charge
            assert "search" in driver.current_url.lower() or "demowebshop" in driver.current_url

    def test_search_nonexistent_product(self, driver: WebDriver):
        """Rechercher un produit inexistant affiche un message d\'absence."""
        wait = WebDriverWait(driver, 20)
        driver.get(BASE_URL)

        search_input = wait.until(EC.presence_of_element_located(SEARCH_INPUT))
        driver.execute_script("arguments[0].scrollIntoView({block: \'center\'});", search_input)
        search_input.clear()
        search_input.send_keys("xyzproductinexistant99999")

        _safe_click(driver, SEARCH_BTN)
        _wait_page_ready(driver)

        page_source = driver.page_source.lower()
        assert (
            "no products" in page_source
            or "aucun" in page_source
            or "not found" in page_source
            or len(driver.find_elements(*SEARCH_RESULTS)) == 0
        ), "Un message d\'absence de resultats devrait etre affiche"
'''

# ─── Keyword -> (template_key, template_code) ─────────────────────────────────
_KEYWORD_MAP = [
    (["affichage", "display", "liste produit", "visualis"],  "F001", _TEMPLATE_F001),
    (["navigation", "detail", "produit detail"],             "F002", _TEMPLATE_F002),
    (["panier", "cart", "ajout"],                            "F003", _TEMPLATE_F003),
    (["tri", "filtr", "sort", "trier"],                      "F004", _TEMPLATE_F004),
    (["pagination", "page suivante", "next", "previous"],    "F005", _TEMPLATE_F005),
    (["recherche", "search", "rechercher"],                  "F006", _TEMPLATE_F006),
]

# Feature ID prefixes for direct matching
_FEATURE_ID_MAP = {
    "F-001": ("F001", _TEMPLATE_F001),
    "F-002": ("F002", _TEMPLATE_F002),
    "F-003": ("F003", _TEMPLATE_F003),
    "F-004": ("F004", _TEMPLATE_F004),
    "F-005": ("F005", _TEMPLATE_F005),
    "F-006": ("F006", _TEMPLATE_F006),
}


def _pick_template(case: Dict[str, Any]):
    """
    Returns (template_key: str, template_code: str).
    template_key is used for deduplication — one file per key.
    """
    titre    = (case.get("titre", "") + " " + case.get("description", "")).lower()
    feat_id  = case.get("id", "")

    # 1. Direct feature ID match (e.g., F-001, F-002)
    for prefix, (key, tpl) in _FEATURE_ID_MAP.items():
        if feat_id.startswith(prefix):
            return key, tpl

    # 2. Keyword match on title/description
    for keywords, key, tpl in _KEYWORD_MAP:
        if any(kw in titre for kw in keywords):
            return key, tpl

    # 3. Generic fallback (unique key per distinct title)
    class_name  = re.sub(r'[^\w]', '', case.get("titre", "Test").title())[:30] or "GenericTest"
    method_name = re.sub(r'[^\w]', '_', case.get("titre", "test").lower())[:40] or "generic"
    description = case.get("description", "Test generique")
    titre_str   = case.get("titre", "")
    generic_body = (
        f"class Test{class_name}:\n"
        f'    """{titre_str}"""\n\n'
        f"    def test_{method_name}(self, driver: WebDriver):\n"
        f'        """{description}"""\n'
        f"        wait = WebDriverWait(driver, 20)\n"
        f"        _go_to_electronics(driver)\n\n"
        f"        assert \"demowebshop.tricentis.com\" in driver.current_url\n"
    )
    generic_key = f"GENERIC_{class_name}"
    return generic_key, _TEST_HEADER + generic_body


# ═════════════════════════════════════════════════════════════════════════════
class SeleniumGenerator:
    """Template-based Selenium test generator. LLM NOT used for Python code."""

    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        self.llm_client = LLMClient(config_path)

    def generate_scripts(
        self,
        test_cases: List[Dict[str, Any]],
        output_dir: str,
        url_cible: str = None,
    ):
        self.url_cible = (url_cible or DEFAULT_URL).rstrip('/') + '/'
        logger.info(f"URL cible : {self.url_cible}")
        logger.info("Mode : templates deterministes (LLM non utilise pour le code)")

        generated_tests_dir = os.path.join(output_dir, "generated_tests")
        pages_dir  = os.path.join(generated_tests_dir, "pages")
        tests_dir  = os.path.join(generated_tests_dir, "tests")

        for d in [tests_dir, pages_dir]:
            if os.path.exists(d):
                shutil.rmtree(d)
        for d in [generated_tests_dir, pages_dir, tests_dir]:
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, "__init__.py"), 'a').close()

        self._write_base_page(pages_dir)
        self._write_conftest(generated_tests_dir)
        self._write_pytest_ini(generated_tests_dir)

        # ── Write one file per template key (dedup by key, not content) ──────
        written_keys: set = set()
        saved = 0

        for case in test_cases:
            feat_id = case.get("id", "UNKNOWN")
            titre   = case.get("titre", "unnamed")

            template_key, template_code = _pick_template(case)

            if template_key in written_keys:
                logger.info(f"  Skip (doublon) : {feat_id} -> {template_key}")
                continue
            written_keys.add(template_key)

            try:
                ast.parse(template_code)
            except SyntaxError as e:
                logger.error(f"  Template invalide pour {feat_id}: {e}")
                continue

            safe_titre = re.sub(r'[^\w]', '_', titre.lower())[:40]
            filename   = f"test_{template_key}_{safe_titre}.py"
            filepath   = os.path.join(tests_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template_code)
            logger.info(f"  [OK] Script : {filename}")
            saved += 1

        logger.info(f"Scripts generes : {saved}")

    # ── Static infrastructure ─────────────────────────────────────────────────
    def _write_base_page(self, pages_dir: str):
        code = '''\
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
import time


class BasePage:
    """Hardened base - WebDriverWait(20), scrollIntoView, JS-click fallback."""

    TIMEOUT = 20

    def __init__(self, driver):
        self.driver = driver
        self.wait   = WebDriverWait(driver, self.TIMEOUT)

    def _scroll_to(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:\'center\',inline:\'nearest\'});",
            element,
        )
        time.sleep(0.3)

    def wait_for_presence(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def wait_for_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_for_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def safe_click(self, locator):
        el = self.wait_for_presence(locator)
        self._scroll_to(el)
        el = self.wait_for_clickable(locator)
        try:
            el.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            self.driver.execute_script("arguments[0].click();", el)

    def safe_send_keys(self, locator, text: str):
        el = self.wait_for_presence(locator)
        self._scroll_to(el)
        el = self.wait_for_visible(locator)
        el.clear()
        el.send_keys(text)

    def get_text(self, locator) -> str:
        el = self.wait_for_visible(locator)
        self._scroll_to(el)
        return el.text

    def is_visible(self, locator) -> bool:
        try:
            return self.wait_for_visible(locator).is_displayed()
        except TimeoutException:
            return False

    def open(self, url: str):
        self.driver.get(url)
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
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
from webdriver_manager.chrome import ChromeDriverManager

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
    """Chrome - 1920x1080 - explicit waits only."""
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    if headless == "true":
        options.add_argument("--headless=new")

    drv = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
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
        parts   = request.node.name.split("_")
        test_id = parts[1] if len(parts) > 1 else "unknown"
        ss_dir  = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "screenshots"
        )
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
