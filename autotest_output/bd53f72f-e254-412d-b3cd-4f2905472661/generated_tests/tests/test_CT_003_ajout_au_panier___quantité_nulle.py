from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_ajout_au_panier_quantite_nulle(driver: WebDriver):
    # Étape 1 : Sélectionner un produit électronique
    produit_selector = "[href='/build-your-own-cheap-computer']"
    produit = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, produit_selector)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", produit)
    produit = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, produit_selector)))
    try:
        produit.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", produit)

    # Étape 2 : Saisir une quantité nulle (0)
    quantite_selector = "#qty"
    quantite = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, quantite_selector)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", quantite)
    quantite = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, quantite_selector)))
    quantite.clear()
    quantite.send_keys("0")

    # Étape 3 : Cliquer sur 'Add to cart'
    add_to_cart_selector = "[name='add-to-cart-button']"
    add_to_cart = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, add_to_cart_selector)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_to_cart)
    add_to_cart = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, add_to_cart_selector)))
    try:
        add_to_cart.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", add_to_cart)

    # Étape 4 : Vérifier que le produit n'est pas ajouté au panier
    panier_selector = ".cart-qty"
    panier = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, panier_selector)))
    assert panier.text == "(0)"

    # Étape 5 : Vérifier que le message d'erreur est affiché
    erreur_selector = ".validation-summary-errors"
    erreur = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, erreur_selector)))
    assert erreur.text != ""