import pytest
from pages.product_page import ProductPage
from selenium.webdriver.remote.webdriver import WebDriver

@pytest.fixture
def driver():
    return WebDriver()

class TestProduct:
    @pytest.mark.parametrize("test_id", ["F-003"])
    def test_product(self, driver, test_id):
        product_page = ProductPage(driver)
        driver.get("https://demowebshop.tricentis.com/electronics")

        # Step 1: Add a product to the cart
        product_page.add_to_cart()
        assert product_page.cart_icon_text() == "1 item"

        # Step 2: Try to add an out-of-stock product to the cart
        product_page.out_of_stock_product().add_to_cart()
        error_message = product_page.error_message_text()
        assert "Not available" in error_message

        if not all(assertion:
                   assertion and not driver.find_elements_by_css_selector("[role='alert']")):
            driver.save_screenshot(f"{test_id}_failure.png")