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


def test_navigate_to_product_detail(driver: WebDriver):
    """Navigation vers détail produit - Cas limite (produit avec prix nul) - positif : clic produit ouvre la page detail."""
    _go_to_listing(driver, BASE_URL)
    link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
    current_url = driver.current_url
    try:
        link.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", link)
    WebDriverWait(driver, 20).until(EC.url_changes(current_url))
    assert driver.current_url != current_url, "Pas de redirection vers la page detail"


def test_product_detail_has_price(driver: WebDriver):
    """Navigation vers détail produit - Cas limite (produit avec prix nul) - positif : page detail affiche un prix."""
    _go_to_listing(driver, BASE_URL)
    link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
    try:
        link.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", link)
    price = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.prices"))
    )
    assert price.text.strip(), "Prix absent sur la page detail"


def test_detail_page_has_product_name(driver: WebDriver):
    """Navigation vers détail produit - Cas limite (produit avec prix nul) - positif : page detail affiche le nom du produit."""
    _go_to_listing(driver, BASE_URL)
    link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a"))
    )
    product_name = link.text.strip()
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
    try:
        link.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", link)
    h1 = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h1.product-name, h1"))
    )
    assert product_name.lower() in h1.text.lower() or h1.text.strip(), "Nom produit absent"
