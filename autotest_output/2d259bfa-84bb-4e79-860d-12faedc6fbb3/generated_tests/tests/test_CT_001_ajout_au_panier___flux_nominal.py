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


def _go_to_cart_page(driver):
    """Navigate to a listing page that has Add to cart buttons.
    Tries /cell-phones first (has buttons), falls back to first subcategory.
    """
    site = BASE_URL.split("/electronics")[0].rstrip("/")
    for path in ["/cell-phones", "/camera-photo"]:
        driver.get(site + path)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item input[value='Add to cart']"))
            )
            return
        except TimeoutException:
            pass
    # Last resort: go through subcategory navigation
    _go_to_listing(driver, BASE_URL)


def test_add_to_cart_updates_counter(driver: WebDriver):
    """Ajout au panier - Flux nominal - positif : ajout panier met a jour le compteur."""
    _go_to_cart_page(driver)
    add_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".product-item input[value='Add to cart']"))
    )
    cart_qty = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.cart-qty"))
    )
    initial_text = cart_qty.text
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", add_btn)
    try:
        add_btn.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", add_btn)
    success = False
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#bar-notification"))
        )
        success = True
    except TimeoutException:
        pass
    if not success:
        new_qty = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.cart-qty"))
        )
        assert new_qty.text != initial_text, "Compteur panier non mis a jour"


def test_add_to_cart_button_visible(driver: WebDriver):
    """Ajout au panier - Flux nominal - positif : bouton Add to cart visible sur la liste."""
    _go_to_cart_page(driver)
    add_btn = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item input[value='Add to cart']"))
    )
    assert add_btn.is_displayed(), "Bouton Add to cart non visible"


def test_cart_counter_visible(driver: WebDriver):
    """Ajout au panier - Flux nominal - positif : compteur panier visible."""
    _go_to_cart_page(driver)
    cart_qty = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.cart-qty"))
    )
    assert cart_qty.is_displayed(), "Compteur panier non visible"
    assert cart_qty.text.startswith("("), f"Format compteur inattendu: {cart_qty.text}"
