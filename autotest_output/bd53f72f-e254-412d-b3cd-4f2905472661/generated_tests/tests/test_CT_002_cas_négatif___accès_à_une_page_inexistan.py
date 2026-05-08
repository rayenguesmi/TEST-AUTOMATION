from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_acces_page_inexistante(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Saisir une URL avec un numéro de page inexistante
    url_inexistante = "https://demowebshop.tricentis.com/products?page=1000"
    driver.get(url_inexistante)

    # Vérification de la présence d'une erreur ou d'une page d'erreur
    try:
        element_erreur = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".error")))
        assert element_erreur.is_displayed()
    except Exception as e:
        assert False, f"Erreur lors de la vérification de la page d'erreur : {e}"

    # Vérification du contenu de la page d'erreur
    try:
        contenu_erreur = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".error")))
        assert "erreur" in contenu_erreur.text.lower()
    except Exception as e:
        assert False, f"Erreur lors de la vérification du contenu de la page d'erreur : {e}"