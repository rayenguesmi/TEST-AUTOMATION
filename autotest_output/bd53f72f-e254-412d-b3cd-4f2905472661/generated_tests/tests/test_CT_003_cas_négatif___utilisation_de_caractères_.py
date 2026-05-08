from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_CT_003(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Saisir une URL avec des caractères spéciaux
    url_malveillante = "https://demowebshop.tricentis.com/products?page=<script>alert('XSS')</script>"
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "small-searchterms")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "small-searchterms")))
    try:
        element.send_keys(url_malveillante)
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].value = arguments[1];", element, url_malveillante)

    # Étape 3 : Appuyer sur la touche 'Entrée' pour charger la page
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "small-searchterms")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "small-searchterms")))
    try:
        element.send_keys("\n")
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter'}));", element)

    # Vérification du résultat attendu
    try:
        WebDriverWait(driver, 10).until(EC.url_contains("error"))
        assert True
    except:
        assert False, "Erreur ou page d'erreur non affichée"