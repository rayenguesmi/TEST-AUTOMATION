from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_ajout_au_panier_produit_en_rupture_de_stock(driver: WebDriver):
    # Étape 1 : Sélectionner un produit électronique en rupture de stock
    produit_selector = "[href='/14_1-inch-laptop']"
    produit = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, produit_selector)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", produit)
    produit = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, produit_selector)))
    try:
        produit.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", produit)

    # Étape 2 : Cliquer sur 'Add to cart'
    add_to_cart_selector = "[value='Add to cart']"
    add_to_cart = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, add_to_cart_selector)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_to_cart)
    add_to_cart = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, add_to_cart_selector)))
    try:
        add_to_cart.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", add_to_cart)

    # Étape 3 : Vérifier que le produit n'est pas ajouté au panier
    shopping_cart_badge_selector = ".shopping_cart_badge"
    shopping_cart_badge = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, shopping_cart_badge_selector)))
    assert shopping_cart_badge.text == "0"

    # Étape 4 : Vérifier que le message d'erreur est affiché
    error_message_selector = ".error-message"
    error_message = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, error_message_selector)))
    assert error_message.text == "The product is currently out of stock."