from selenium.webdriver.remote.webdriver import WebDriver
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.error_page import ErrorPage
import pytest

@pytest.mark.usefixtures('driver')
class TestAddToCart:

    @pytest.fixture(scope='function')
    def product_page(self, driver):
        return ProductPage(driver)

    @pytest.fixture(scope='function')
    def cart_page(self, driver):
        return CartPage(driver)

    @pytest.fixture(scope='function')
    def error_page(self, driver):
        return ErrorPage(driver)

    def test_add_to_cart_positive(self, product_page, cart_page):
        product_page.open_product_page()
        product_page.click_add_to_cart_button()
        assert "The product has been added to your shopping cart" in product_page.get_confirmation_message()
        assert product_page.is_product_in_cart()

    def test_add_to_cart_out_of_stock(self, product_page, error_page):
        product_page.open_product_page_with_out_of_stock()
        product_page.click_add_to_cart_button()
        assert "The product is out of stock" in error_page.get_error_message()
        assert not product_page.is_product_in_cart()

    def test_add_to_cart_invalid_quantity(self, product_page, error_page):
        product_page.open_product_page()
        product_page.set_quantity(-1)
        product_page.click_add_to_cart_button()
        assert "The quantity must be between 0 and 10" in error_page.get_error_message()
        assert not product_page.is_product_in_cart()

    def test_add_to_cart_not_logged_in(self, product_page, error_page):
        product_page.open_product_page()
        product_page.click_add_to_cart_button()
        assert "You must login to add products to your shopping cart." in error_page.get_error_message()
        assert not product_page.is_product_in_cart()

    def test_add_to_cart_max_quantity(self, product_page, cart_page):
        product_page.open_product_page()
        product_page.set_quantity(10)
        product_page.click_add_to_cart_button()
        assert "The product has been added to your shopping cart" in product_page.get_confirmation_message()
        assert product_page.is_product_in_cart_with_quantity(10)