import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from pages.error_page import ErrorPage
from pages.electronics_page import ElectronicsPage
import time

@pytest.mark.parametrize("url", ["https://example.com/electronic"])
def test_CT_002(driver: WebDriver, url: str):
    # Étape 1 : Accéder à la page Electronics via une URL incorrecte
    driver.get(url)
    
    # Étape 2 : Vérifier que l'erreur ou la redirection est affichée
    error_page = ErrorPage(driver)
    assert error_page.is_error_page_displayed(), "Erreur ou redirection non affichée"
    
    # Capture d'un screenshot en cas d'échec
    try:
        assert error_page.is_error_page_displayed()
    except AssertionError:
        driver.save_screenshot(f"CT-002_failure_{time.time()}.png")
        raise