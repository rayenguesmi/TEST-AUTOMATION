from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_ajouter_produit_sans_connexion(driver: WebDriver):
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

    # Étape 3 : Cliquer sur le bouton 'Add to cart'
    add_to_cart = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[value='Add to cart']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_to_cart)
    add_to_cart = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='Add to cart']")))
    try:
        add_to_cart.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", add_to_cart)

    # Étape 4 : Vérifier que l'utilisateur est redirigé vers la page de connexion
    WebDriverWait(driver, 20).until(EC.url_contains("login"))

    # Étape 5 : Vérifier que le produit n'est pas ajouté au panier
    shopping_cart = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".cart")))
    assert "0 item(s)" in shopping_cart.text