from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_acces_page_inexistante(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")
    
    # Étape 2 : Saisir une adresse URL avec un numéro de page inexistante
    url_inexistante = "https://demowebshop.tricentis.com/?page=1000"
    driver.get(url_inexistante)
    
    # Étape 3 : Vérifier que la page d'erreur ou la page par défaut est affichée
    try:
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".no-data")))
        assert element.text == "No products were found that matched your criteria."
    except:
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-header")))
        assert element.text == "Page not found"