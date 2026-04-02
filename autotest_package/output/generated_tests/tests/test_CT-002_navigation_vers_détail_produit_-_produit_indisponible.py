# tests/test_ct_002.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
from pages.product_detail_page import ProductDetailPage
import pytest
import time

@pytest.mark.usefixtures("driver")
class TestCT002:
    def test_ct_002(self, driver: WebDriver):
        # Étape 1 : Se rendre sur la page d'accueil du site web.
        home_page = HomePage(driver)
        home_page.navigate_to_url("https://www.google.com")

        # Étape 2 : Cliquer sur un produit indisponible.
        # Note : Puisque nous sommes sur Google, nous allons simuler une recherche pour un produit.
        home_page.search_for_product("Samsung Galaxy S22")

        # Étape 3 : Vérifier que le message d'indisponibilité est affiché.
        product_detail_page = ProductDetailPage(driver)
        product_detail_page.wait_for_product_to_load()
        message = product_detail_page.get_unavailability_message()

        # Vérification du message d'indisponibilité.
        assert message == "Ce produit est actuellement indisponible."

        # Capture d'un screenshot en cas d'échec.
        try:
            assert message == "Ce produit est actuellement indisponible."
        except AssertionError:
            driver.save_screenshot("CT-002_failure.png")
            raise