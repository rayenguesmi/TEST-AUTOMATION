import pytest
from pages.electronics_page import ElectronicsPage
from selenium.webdriver.remote.webdriver import WebDriver

@pytest.fixture
def driver():
    return WebDriver()

class TestElectronicsPage:
    def test_electronics_page(self, driver):
        # Step 1: Navigate to the electronics page
        electronics_page = ElectronicsPage(driver)
        electronics_page.navigate_to("https://demowebshop.tricentis.com/electronics")

        # Step 2: Assert that the page displays a list of products
        assert electronics_page.is_product_list_displayed()

        # Step 3: Click on a product
        product = electronics_page.get_first_product()
        product.click()

    def test_invalid_url(self, driver):
        # Step 1: Navigate to an invalid URL
        driver.get("https://example.com/invalid-url")

        # Step 2: Assert that an error or redirection occurs
        assert "Erreur 404" in driver.title or "Redirection" in driver.current_url

@pytest.mark.parametrize("test_id", ["F-001"])
def test_electronics_page_failure(test_id):
    try:
        pytest.main([f"-k={test_id}"])
    except Exception as e:
        import os
        from selenium.common.exceptions import WebDriverException
        if isinstance(e, WebDriverException):
            driver = WebDriver()
            page = ElectronicsPage(driver)
            page.get_screenshot(f"{test_id}_failure.png")