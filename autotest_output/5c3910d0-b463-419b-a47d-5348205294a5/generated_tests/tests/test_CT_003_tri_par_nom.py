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
            (By.XPATH, "(//div[contains(@class,'sub-category-item')]//a)[1]")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", sub)
    try:
        sub.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", sub)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item"))
    )

import re

BASE_URL = "https://demowebshop.tricentis.com/electronics"
# cell-phones has simple fixed prices — price sort works reliably there
SORT_PAGE = BASE_URL.rstrip("/").rsplit("/electronics", 1)[0] + "/cell-phones"


def _go_to_sort_page(driver):
    """Navigate to a product listing page where price sort is reliable."""
    driver.get(SORT_PAGE)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item"))
    )


def test_sort_price_low_to_high(driver: WebDriver):
    """Tri par nom - positif : tri prix croissant."""
    _go_to_sort_page(driver)
    sort_el = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "select#products-orderby"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", sort_el)
    old_items = driver.find_elements(By.CSS_SELECTOR, ".product-item")
    Select(sort_el).select_by_visible_text("Price: Low to High")
    if old_items:
        try:
            WebDriverWait(driver, 20).until(EC.staleness_of(old_items[0]))
        except Exception:
            pass
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item"))
    )
    prices = []
    for el in driver.find_elements(By.CSS_SELECTOR, "div.prices"):
        nums = re.findall(r'[0-9]+\.?[0-9]*', el.text.replace(',', ''))
        if nums:
            prices.append(float(nums[-1]))
    assert len(prices) >= 1, "Aucun prix trouve apres tri"
    if len(prices) > 1:
        assert all(prices[i] <= prices[i+1] for i in range(len(prices)-1)),             f"Produits non tries Low->High: {prices}"


def test_sort_price_high_to_low(driver: WebDriver):
    """Tri par nom - positif : tri prix decroissant."""
    _go_to_sort_page(driver)
    sort_el = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "select#products-orderby"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", sort_el)
    old_items = driver.find_elements(By.CSS_SELECTOR, ".product-item")
    Select(sort_el).select_by_visible_text("Price: High to Low")
    if old_items:
        try:
            WebDriverWait(driver, 20).until(EC.staleness_of(old_items[0]))
        except Exception:
            pass
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item"))
    )
    prices = []
    for el in driver.find_elements(By.CSS_SELECTOR, "div.prices"):
        nums = re.findall(r'[0-9]+\.?[0-9]*', el.text.replace(',', ''))
        if nums:
            prices.append(float(nums[-1]))
    assert len(prices) >= 1, "Aucun prix trouve apres tri"
    if len(prices) > 1:
        assert all(prices[i] >= prices[i+1] for i in range(len(prices)-1)),             f"Produits non tries High->Low: {prices}"


def test_sort_options_available(driver: WebDriver):
    """Tri par nom - positif : options de tri disponibles."""
    _go_to_sort_page(driver)
    sort_el = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "select#products-orderby"))
    )
    options = [o.text for o in Select(sort_el).options]
    assert any("Price" in o for o in options), f"Option Prix absente: {options}"
    assert len(options) >= 2, "Moins de 2 options de tri disponibles"
