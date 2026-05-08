from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_ajout_au_panier(driver: WebDriver):
    # Étape 1 : Sélectionner un produit électronique
    produit_selector = "[href='/build-your-own-cheap-computer']"
    produit_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, produit_selector)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", produit_element)
    produit_element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, produit_selector)))
    try:
        produit_element.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", produit_element)

    # Étape 2 : Cliquer sur 'Add to cart'
    add_to_cart_selector = "[value='Add to cart']"
    add_to_cart_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, add_to_cart_selector)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_to_cart_element)
    add_to_cart_element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, add_to_cart_selector)))
    try:
        add_to_cart_element.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", add_to_cart_element)

    # Étape 3 : Vérifier que le produit est ajouté au panier
    panier_selector = ".cart-qty"
    panier_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, panier_selector)))
    assert panier_element.text == "1"

    # Étape 4 : Vérifier que le message de confirmation est affiché
    message_confirmation_selector = ".bar-notification"
    message_confirmation_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, message_confirmation_selector)))
    assert message_confirmation_element.text == "The product has been added to your shopping cart"

    # Étape 5 : Vérifier que le compteur du panier est mis à jour
    compteur_panier_selector = ".cart-qty"
    compteur_panier_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, compteur_panier_selector)))
    assert compteur_panier_element.text == "1"