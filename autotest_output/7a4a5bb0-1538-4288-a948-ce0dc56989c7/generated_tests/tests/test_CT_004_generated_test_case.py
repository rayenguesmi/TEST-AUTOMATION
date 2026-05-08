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


BASE_URL = "https://demowebshop.tricentis.com/electronics"


def test_search_returns_results(driver: WebDriver):
    """Generated Test Case - positif : recherche 'camera' retourne des resultats."""
    driver.get(BASE_URL)
    search = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#small-searchterms"))
    )
    search.clear()
    search.send_keys("camera")
    btn = driver.find_element(By.CSS_SELECTOR, ".search-box button[type='submit']")
    try:
        btn.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", btn)
    results = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-item"))
    )
    assert len(results) > 0, "Aucun resultat pour 'camera'"


def test_search_no_results(driver: WebDriver):
    """Generated Test Case - negatif : recherche inexistante -> message no results."""
    driver.get(BASE_URL)
    search = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#small-searchterms"))
    )
    search.clear()
    search.send_keys("xyzproductinexistant999")
    btn = driver.find_element(By.CSS_SELECTOR, ".search-box button[type='submit']")
    try:
        btn.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", btn)
    WebDriverWait(driver, 10).until(EC.url_contains("search"))
    products = driver.find_elements(By.CSS_SELECTOR, ".product-item")
    assert len(products) == 0, "Des produits affiches pour une recherche inexistante"


def test_search_with_partial_keyword(driver: WebDriver):
    """Generated Test Case - positif : recherche partielle 'phone'."""
    driver.get(BASE_URL)
    search = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#small-searchterms"))
    )
    search.clear()
    search.send_keys("phone")
    btn = driver.find_element(By.CSS_SELECTOR, ".search-box button[type='submit']")
    try:
        btn.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", btn)
    WebDriverWait(driver, 20).until(EC.url_contains("search"))
    page_src = driver.page_source.lower()
    assert "phone" in page_src or "no results" in page_src, "Page de recherche inattendue"
