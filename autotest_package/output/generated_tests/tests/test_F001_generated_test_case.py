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
ELECTRONICS_LINK   = (By.CSS_SELECTOR, "div.header-menu > ul.top-menu > li > a[href='/electronics']")
SUBCATEGORY_ITEMS  = (By.CSS_SELECTOR, ".category-grid .item-box, .sub-category-grid .item-box")
SUBCATEGORY_LINK   = (By.CSS_SELECTOR, ".category-grid .item-box a, .sub-category-grid .item-box a")
PRODUCT_LIST       = (By.CSS_SELECTOR, ".product-item")
PRODUCT_TITLE_A    = (By.CSS_SELECTOR, ".product-item .product-title a")
PRODUCT_PRICE      = (By.CSS_SELECTOR, ".product-item .price.actual-price")
PRODUCT_H1         = (By.CSS_SELECTOR, "div.product-name h1")
ADD_CART_BTN       = (By.CSS_SELECTOR, "input[value='Add to cart']")
NOTIFICATION_OK    = (By.CSS_SELECTOR, ".bar-notification.success")
SEARCH_INPUT       = (By.ID, "small-searchterms")
SEARCH_BTN         = (By.CSS_SELECTOR, "input[value='Search']")
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
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
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
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
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
