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


BASE_URL = "https://www.cloudflare.com"


def test_products_list_is_displayed(driver: WebDriver):
    """Generated Test Case - positif : produits affiches avec nom et prix."""
    _go_to_listing(driver, BASE_URL)
    products = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-item"))
    )
    assert len(products) > 0, "Aucun produit affiche sur la page"
    first = products[0]
    name  = first.find_element(By.CSS_SELECTOR, ".product-title a")
    price = first.find_element(By.CSS_SELECTOR, ".actual-price")
    name_text = (name.text or name.get_attribute('textContent') or name.get_attribute('innerText') or '').strip()
    assert name_text, "Nom produit vide"
    assert price.text.strip(), "Prix produit vide"


def test_product_image_present(driver: WebDriver):
    """Generated Test Case - positif : chaque produit a une image."""
    _go_to_listing(driver, BASE_URL)
    products = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-item"))
    )
    for p in products:
        img = p.find_elements(By.CSS_SELECTOR, "img")
        assert img, "Image manquante sur un produit"


def test_invalid_url_shows_no_products(driver: WebDriver):
    """Generated Test Case - negatif : URL invalide -> pas de produits."""
    driver.get(BASE_URL + "/electronics-xyz-invalid-999")
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item"))
        )
        assert False, "Produits affiches sur URL invalide"
    except TimeoutException:
        pass
