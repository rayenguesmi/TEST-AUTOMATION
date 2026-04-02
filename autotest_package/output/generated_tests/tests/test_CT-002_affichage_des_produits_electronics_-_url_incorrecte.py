# tests/test_ct_002.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.error_page import ErrorPage
import pytest
import time

def test_ct_002(driver: WebDriver):
    # Étape 1 : Tenter d'accéder à la page Electronics via une URL incorrecte
    url = "https://example.com/electronic"
    driver.get(url)

    # Étape 2 : Vérifier que la page retourne une erreur 404 ou redirige vers une page d'erreur
    error_page = ErrorPage(driver)
    assert error_page.is_error_page_displayed()

    # Vérifier le code d'erreur
    assert error_page.get_error_code() == "404"

    # Vérifier le message d'erreur
    assert error_page.get_error_message() == "Page non trouvée"

@pytest.fixture
def driver():
    # Cette fixture est fournie, nous n'avons pas besoin de la définir ici
    pass

def pytest_runtest_logreport(report):
    if report.failed:
        # Capture un screenshot en cas d'échec
        report.driver.save_screenshot(f"{report.nodeid}_failure.png")