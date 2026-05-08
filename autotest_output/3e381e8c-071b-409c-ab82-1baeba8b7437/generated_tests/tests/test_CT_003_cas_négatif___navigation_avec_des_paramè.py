from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_navigation_avec_parametres_invalides(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")
    
    # Étape 2 : Saisir une adresse URL avec un paramètre de page invalide
    url_invalide = "https://demowebshop.tricentis.com/?page=abc"
    driver.get(url_invalide)
    
    # Étape 3 : Vérifier que la page d'erreur ou la page par défaut est affichée
    try:
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-body")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".page-body")))
        assert element.is_displayed()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        assert driver.title == "Demo Web Shop"