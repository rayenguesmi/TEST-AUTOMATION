import pytest
from pages.product_page import ProductPage
from selenium.webdriver.remote.webdriver import WebDriver

@pytest.fixture
def driver():
    return WebDriver()

class TestProductPage:
    def test_add_to_cart(self, driver):
        product_page = ProductPage(driver)
        product_page.open()
        product_page.add_to_cart()
        assert product_page.cart_icon_is_displayed(), "Cart icon is not displayed"
        product_page.capture_screenshot(f"add_to_cart_failure.png")

    @pytest.mark.xfail
    def test_add_to_cart_out_of_stock(self, driver):
        product_page = ProductPage(driver)
        product_page.open()
        product_page.add_to_cart_out_of_stock()
        assert product_page.error_message_is_displayed(), "Error message is not displayed"
        product_page.capture_screenshot(f"add_to_cart_out_of_stock_failure.png")