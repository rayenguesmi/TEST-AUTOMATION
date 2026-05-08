from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_ajouter_produit_au_panier(driver: WebDriver):
    # Étape 1 : Se rendre sur la page d'accueil du site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Cliquer sur le produit 'Build your own cheap computer'
    produit = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, "Build your own cheap computer")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", produit)
    produit = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "Build your own cheap computer")))
    try:
        produit.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", produit)

    # Étape 3 : Saisir une quantité très élevée dans le champ de quantité
    quantite = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='qty']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", quantite)
    quantite = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='qty']")))
    quantite.clear()
    quantite.send_keys("1000")

    # Étape 4 : Cliquer sur le bouton 'Add to cart'
    add_to_cart = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[value='Add to cart']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_to_cart)
    add_to_cart = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='Add to cart']")))
    try:
        add_to_cart.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", add_to_cart)

    # Étape 5 : Vérifier que le produit est ajouté au panier
    panier = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".cart")))
    assert "1000" in panier.text

    # Étape 6 : Vérifier que le message de confirmation est affiché
    message_confirmation = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".bar-notification")))
    assert "The product has been added to your shopping cart" in message_confirmation.text

    # Étape 7 : Vérifier que le compteur du panier est mis à jour
    compteur_panier = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".cart-qty")))
    assert "1000" in compteur_panier.text