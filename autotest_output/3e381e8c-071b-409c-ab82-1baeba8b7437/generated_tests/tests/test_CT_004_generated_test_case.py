from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_ajouter_plusieurs_produits_au_panier(driver: WebDriver):
    # Étape 1 : Se rendre sur la page d'accueil du site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Cliquer sur le produit 'Build your own cheap computer'
    produit1 = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, "Build your own cheap computer")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", produit1)
    produit1 = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "Build your own cheap computer")))
    try:
        produit1.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", produit1)

    # Étape 3 : Cliquer sur le bouton 'Add to cart'
    add_to_cart = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[value='Add to cart']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_to_cart)
    add_to_cart = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[value='Add to cart']")))
    try:
        add_to_cart.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", add_to_cart)

    # Étape 4 : Cliquer sur le produit '14.1-inch Laptop'
    driver.get("https://demowebshop.tricentis.com/")
    produit2 = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, "14.1-inch Laptop")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", produit2)
    produit2 = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "14.1-inch Laptop")))
    try:
        produit2.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", produit2)

    # Étape 5 : Cliquer sur le bouton 'Add to cart'
    add_to_cart = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[value='Add to cart']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_to_cart)
    add_to_cart = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[value='Add to cart']")))
    try:
        add_to_cart.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", add_to_cart)

    # Étape 6 : Vérifier que les deux produits sont ajoutés au panier
    panier = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".cart")))
    assert "2" in panier.text

    # Étape 7 : Vérifier que le compteur du panier est mis à jour
    compteur_panier = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".cart-qty")))
    assert compteur_panier.text == "2"