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


def test_products_loaded_on_listing(driver: WebDriver):
    """Pagination - Flux nominal - positif : produits charges sur la page listing."""
    _go_to_listing(driver, BASE_URL)
    products = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-item"))
    )
    assert len(products) > 0, "Aucun produit affiche"


def test_next_page_or_single_page(driver: WebDriver):
    """Pagination - Flux nominal - positif : bouton Next si plusieurs pages, sinon page unique OK."""
    _go_to_listing(driver, BASE_URL)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item"))
    )
    next_btns = driver.find_elements(By.CSS_SELECTOR, ".next-page a")
    if next_btns:
        first_products = [
            p.find_element(By.CSS_SELECTOR, "a").text
            for p in driver.find_elements(By.CSS_SELECTOR, ".product-item")
        ]
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", next_btns[0])
        try:
            next_btns[0].click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            driver.execute_script("arguments[0].click();", next_btns[0])
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item"))
        )
        second_products = [
            p.find_element(By.CSS_SELECTOR, "a").text
            for p in driver.find_elements(By.CSS_SELECTOR, ".product-item")
        ]
        assert first_products != second_products, "Les produits n'ont pas change apres Next"
    else:
        products = driver.find_elements(By.CSS_SELECTOR, ".product-item")
        assert len(products) > 0, "Aucun produit sur la page unique"


def test_invalid_page_url(driver: WebDriver):
    """Pagination - Flux nominal - negatif : URL de page invalide."""
    driver.get(BASE_URL + "/electronics-xyz-page-999")
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item"))
        )
        assert False, "Produits affiches sur page invalide"
    except TimeoutException:
        pass
