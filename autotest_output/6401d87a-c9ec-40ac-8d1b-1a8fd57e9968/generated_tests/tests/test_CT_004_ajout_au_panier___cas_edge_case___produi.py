from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_ajout_au_panier_produit_sans_description(driver: WebDriver):
    # Étape 1 : Sélectionner un produit électronique avec une description vide
    produit_selector = "[href='/produit-sans-description']"
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

    # Étape 3 : Vérifier que le produit est ajouté au panier
    panier_selector = ".cart-quantity"
    panier = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, panier_selector)))
    assert panier.text == "1"

    # Étape 4 : Vérifier que le message de confirmation est affiché
    message_confirmation_selector = ".bar-notification"
    message_confirmation = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, message_confirmation_selector)))
    assert message_confirmation.text == "The product has been added to your shopping cart"

    # Étape 5 : Vérifier que le compteur du panier est mis à jour
    compteur_panier_selector = ".cart-quantity"
    compteur_panier = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, compteur_panier_selector)))
    assert compteur_panier.text == "1"