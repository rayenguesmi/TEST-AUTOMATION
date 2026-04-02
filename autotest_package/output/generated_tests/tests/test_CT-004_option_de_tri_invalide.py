# tests/test_ct_004.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
from pages.tri_page import TriPage
from pages.error_page import ErrorPage
import pytest

@pytest.mark.usefixtures("driver")
class TestCT004:
    def test_ct_004(self, driver: WebDriver):
        # Étape 1 : Ouvrir le site
        home_page = HomePage(driver)
        home_page.open_url("https://www.google.com")

        # Étape 2 : Sélectionner une option de tri invalide
        tri_page = TriPage(driver)
        tri_page.select_tri_option("invalide")

        # Étape 3 : Vérifier que l'application affiche un message d'erreur
        error_page = ErrorPage(driver)
        assert error_page.is_error_message_displayed()

        # Capture d'un screenshot en cas d'échec
        try:
            assert error_page.is_error_message_displayed()
        except AssertionError:
            driver.save_screenshot("CT-004_failure.png")
            raise