from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_navigation_vers_detail_produit(driver: WebDriver):
    # Étape 1 : Navigation vers la page d'accueil
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Cliquer sur le produit 'Build your own cheap computer'
    produit = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, "Build your own cheap computer")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", produit)
    produit = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "Build your own cheap computer")))
    try:
        produit.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", produit)

    # Étape 3 : Vérifier que la page produit est affichée
    WebDriverWait(driver, 20).until(EC.url_contains("build-your-own-cheap-computer"))

    # Étape 4 : Vérifier que la description, le prix et le bouton 'Add to cart' sont affichés
    description = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".product-description")))
    prix = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".price")))
    bouton_ajouter_au_panier = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".add-to-cart-button")))
    assert description.is_displayed()
    assert prix.is_displayed()
    assert bouton_ajouter_au_panier.is_displayed()