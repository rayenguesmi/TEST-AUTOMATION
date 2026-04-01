import pytest
from pages.electronics_page import ElectronicsPage
from pages.product_page import ProductPage
from selenium.webdriver.remote.webdriver import WebDriver

@pytest.fixture
def driver():
    return WebDriver()

class TestElectronicsSearch:
    @pytest.mark.parametrize("search_query", ["phone", "camera"])
    def test_search_positive(self, driver):
        electronics_page = ElectronicsPage(driver)
        product_page = ProductPage(driver)

        # Step 1: Open URL
        electronics_page.open_url("https://demowebshop.tricentis.com/electronics")

        # Step 2: Input search query
        electronics_page.search_input(search_query)

        # Step 3: Submit search form
        product_page.submit_search_form()

        # Assert expected result
        assert product_page.get_products_count() > 0, "No products found"

    @pytest.mark.parametrize("search_query", ["inexistent_product"])
    def test_search_negative(self, driver):
        electronics_page = ElectronicsPage(driver)
        error_page = ErrorPage(driver)

        # Step 1: Open URL
        electronics_page.open_url("https://demowebshop.tricentis.com/electronics")

        # Step 2: Input search query
        electronics_page.search_input(search_query)

        # Step 3: Submit search form
        error_page.submit_search_form()

        # Assert expected result
        assert error_page.get_error_message() == "Aucun résultat trouvé", "Error message not found"

@pytest.mark.parametrize("search_query", ["phone", "camera"])
def test_search_failure(driver):
    electronics_page = ElectronicsPage(driver)
    product_page = ProductPage(driver)

    try:
        # Step 1: Open URL
        electronics_page.open_url("https://demowebshop.tricentis.com/electronics")

        # Step 2: Input search query
        electronics_page.search_input(search_query)

        # Step 3: Submit search form
        product_page.submit_search_form()

    except Exception as e:
        pytest.fail(f"Test failed: {e}")
        driver.save_screenshot(f"{test_id}_failure.png")