from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_consulter_detalis_produit(driver: WebDriver):
    # Étape 1 : Se rendre sur la page d'accueil du site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Cliquer sur le produit avec un nom très long
    produit_selector = "[href='/build-your-own-cheap-computer']"
    produit_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, produit_selector)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", produit_element)
    produit_element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, produit_selector)))
    try:
        produit_element.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", produit_element)

    # Étape 3 : Vérifier que la page produit s'affiche avec la description, le prix et le bouton 'Add to cart'
    description_selector = ".product-description"
    prix_selector = ".price"
    add_to_cart_selector = "[value='Add to cart']"
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, description_selector)))
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, prix_selector)))
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, add_to_cart_selector)))
    assert WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, description_selector))).is_displayed()
    assert WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, prix_selector))).is_displayed()
    assert WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, add_to_cart_selector))).is_displayed()