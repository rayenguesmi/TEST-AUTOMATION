import pytest
from pages.error_page import ErrorPage
from selenium.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os

@pytest.mark.test_id("CT-002")
def test_affichage_produits_electronics_url_invalide(driver: WebDriver):
    # Étape 1 : Accéder à la page avec une URL invalide
    url = "https://example.com/electronics-erreur"
    driver.get(url)

    # Étape 2 : Visualiser la page
    error_page = ErrorPage(driver)
    try:
        # Attendre que la page d'erreur soit affichée
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[text()='404']"))
        )
        # Vérifier que la page d'erreur est affichée
        assert error_page.is_error_page_displayed(), "La page d'erreur n'est pas affichée"
    except AssertionError as e:
        # Capture un screenshot en cas d'échec
        screenshot_path = f"{os.getcwd()}/screenshots/CT-002_failure.png"
        driver.save_screenshot(screenshot_path)
        raise AssertionError(f"Échec du test : {e}") from e