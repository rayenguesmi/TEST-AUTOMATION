# tests/test_ct_004.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
from pages.product_page import ProductPage
import pytest

@pytest.mark.usefixtures("driver")
class TestCT004:
    def test_ct_004(self, driver: WebDriver):
        # Étape 1 : Ouvrir le site
        home_page = HomePage(driver)
        home_page.navigate_to_url("https://www.google.com")

        # Étape 2 : Se rendre sur la page des produits
        # Note : Puisque l'URL du site est https://www.google.com, nous allons simuler la navigation vers la page des produits
        product_page = ProductPage(driver)
        product_page.navigate_to_url("https://www.example.com/products")

        # Étape 3 : Cliquer sur le bouton 'Next'
        next_button = product_page.get_next_button()
        next_button.click()

        # Résultat attendu : Le bouton 'Next' est désactivé
        assert product_page.is_next_button_disabled()

        # Capture d'un screenshot en cas d'échec
        try:
            assert product_page.is_next_button_disabled()
        except AssertionError:
            driver.save_screenshot("CT-004_failure.png")
            raise