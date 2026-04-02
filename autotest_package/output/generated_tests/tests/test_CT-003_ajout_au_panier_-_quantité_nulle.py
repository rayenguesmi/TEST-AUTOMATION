# tests/test_ct_003.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.error_page import ErrorPage
import pytest
import time

@pytest.mark.usefixtures("driver")
class TestCT003:
    def test_ct_003(self, driver: WebDriver):
        # Étape 1 : Se rendre sur la page du produit
        home_page = HomePage(driver)
        home_page.navigate_to_product_page()

        # Étape 2 : Saisir une quantité de 0
        product_page = ProductPage(driver)
        product_page.set_quantity(0)

        # Étape 3 : Cliquer sur 'Add to cart'
        product_page.add_to_cart()

        # Étape 4 : Vérifier que le produit n'est pas ajouté au panier
        cart_page = CartPage(driver)
        assert cart_page.get_product_count() == 0

        # Étape 5 : Vérifier que le message d'erreur est affiché
        error_page = ErrorPage(driver)
        assert error_page.is_error_message_displayed()

        # Capture d'un screenshot en cas d'échec
        try:
            assert True
        except AssertionError:
            driver.save_screenshot("CT-003_failure.png")
            raise