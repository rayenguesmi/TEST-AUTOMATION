# tests/test_ct_002.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.product_detail_page import ProductDetailPage
from pages.cart_page import CartPage
from pages.error_page import ErrorPage
import pytest
import time

@pytest.mark.usefixtures("driver")
class TestCT002:
    def test_ct_002(self, driver: WebDriver):
        # Étape 1 : Se rendre sur la page du produit
        product_detail_page = ProductDetailPage(driver)
        product_detail_page.navigate_to_product_detail_page("Tablette")

        # Étape 2 : Cliquer sur 'Add to cart'
        product_detail_page.click_add_to_cart_button()

        # Étape 3 : Vérifier que le produit n'est pas ajouté au panier
        cart_page = CartPage(driver)
        assert cart_page.get_product_count() == 0

        # Étape 4 : Vérifier que le message d'erreur est affiché
        error_page = ErrorPage(driver)
        assert error_page.is_error_message_displayed()

        # Capture d'un screenshot en cas d'échec
        try:
            assert True
        except AssertionError:
            driver.save_screenshot("CT-002_failure.png")
            raise