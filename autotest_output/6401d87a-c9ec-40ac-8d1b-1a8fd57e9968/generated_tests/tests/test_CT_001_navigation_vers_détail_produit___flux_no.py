from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_navigation_vers_detail_produit(driver: WebDriver):
    # Étape 1 : Navigation vers la page d'accueil
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Cliquer sur le produit 'Build your own cheap computer'
    produit_selector = "[href='/build-your-own-cheap-computer']"
    produit_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, produit_selector)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", produit_element)
    produit_element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, produit_selector)))
    try:
        produit_element.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", produit_element)

    # Étape 3 : Vérifier que la page produit est affichée
    url_attendue = "https://demowebshop.tricentis.com/build-your-own-cheap-computer"
    WebDriverWait(driver, 20).until(EC.url_to_be(url_attendue))

    # Étape 4 : Vérifier que la description, le prix et le bouton 'Add to cart' sont affichés
    description_selector = ".product-description"
    prix_selector = ".price"
    add_to_cart_selector = "[value='Add to cart']"
    description_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, description_selector)))
    prix_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, prix_selector)))
    add_to_cart_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, add_to_cart_selector)))
    assert description_element.is_displayed()
    assert prix_element.is_displayed()
    assert add_to_cart_element.is_displayed()