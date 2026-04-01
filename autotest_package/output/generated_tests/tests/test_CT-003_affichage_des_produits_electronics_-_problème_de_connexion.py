import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pages.electronics_page import ElectronicsPage
from pages.error_page import ErrorPage
import time

@pytest.mark.parametrize("url", ["https://demowebshop.tricentis.com/electronics"])
def test_CT_003(driver: WebDriver, url: str):
    # Étape 1 : Accéder à la page Electronics via l'URL correcte
    driver.get(url)

    # Étape 2 : Vérifier que l'erreur de connexion est affichée
    error_page = ErrorPage(driver)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, error_page.error_message_selector))
    )
    assert error_page.is_error_message_displayed(), "Erreur de connexion non affichée"

    # Vérification de l'erreur de connexion
    assert error_page.get_error_message() == "Erreur de connexion", "Erreur de connexion incorrecte"

    # Capture d'un screenshot en cas d'échec
    try:
        assert error_page.is_error_message_displayed()
    except AssertionError:
        driver.save_screenshot("CT-003_failure.png")
        raise

def test_CT_003_erreur(driver: WebDriver):
    # Étape 1 : Accéder à la page Electronics via l'URL correcte
    driver.get("https://demowebshop.tricentis.com/electronics")

    # Étape 2 : Vérifier que l'erreur de connexion est affichée
    error_page = ErrorPage(driver)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, error_page.error_message_selector))
        )
    except:
        driver.save_screenshot("CT-003_failure.png")
        assert False, "Erreur de connexion non affichée"