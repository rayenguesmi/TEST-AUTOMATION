from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_acces_page_inexistante(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Saisir une URL avec un numéro de page supérieur au nombre de pages existantes
    url_inexistante = "https://demowebshop.tricentis.com/non-existent-page"
    driver.get(url_inexistante)

    # Vérification de la page d'erreur
    try:
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.TAG_NAME, "h1")))
        assert "404" in element.text or "Page not found" in element.text
    except (ElementClickInterceptedException, StaleElementReferenceException):
        assert False, "Erreur lors de la vérification de la page d'erreur"

    # Vérification de l'URL actuelle
    assert driver.current_url == url_inexistante, "L'URL actuelle ne correspond pas à l'URL attendue"

    # Vérification de la présence d'un message d'erreur
    try:
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "p")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.TAG_NAME, "p")))
        assert "The page you are looking for is not available" in element.text or "Page not found" in element.text
    except (ElementClickInterceptedException, StaleElementReferenceException):
        assert False, "Erreur lors de la vérification du message d'erreur"