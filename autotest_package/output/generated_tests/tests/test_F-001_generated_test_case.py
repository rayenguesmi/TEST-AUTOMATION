import pytest
from pages.electronics_page import ElectronicsPage
from pages.product_detail_page import ProductDetailPage
from selenium.webdriver.remote.webdriver import WebDriver

@pytest.fixture
def driver():
    return WebDriver()

class TestElectronicsPage:
    @pytest.mark.parametrize("test_id, test_name", [
        ("F-001_1", "Flux positif: Affichage des produits Electronics"),
        ("F-001_2", "Flux négatif: Charger la page avec mauvaise URL")
    ])
    def test_electronics_page(self, driver, test_id, test_name):
        if test_name == "Flux positif: Affichage des produits Electronics":
            # Navigate to the electronics page
            electronics_page = ElectronicsPage(driver)
            electronics_page.navigate_to("https://demowebshop.tricentis.com/electronics")

            # Assert the product list is visible
            assert electronics_page.is_element_visible("//div[@class='product-list']")

            # Click on a product
            product_detail_page = ProductDetailPage(driver)
            product_detail_page.click_on("//a[@href='#'][contains(text(), 'Product 1')]")

        elif test_name == "Flux négatif: Charger la page avec mauvaise URL":
            # Navigate to the invalid URL
            driver.get("https://example.com/invalid-url")

            # Assert an error message is displayed
            assert electronics_page.is_element_visible("//div[@class='error-message']")

        else:
            raise ValueError(f"Unknown test name: {test_name}")

        # Capture a screenshot in case of failure
        if not driver.current_url.startswith("https://demowebshop.tricentis.com/"):
            driver.save_screenshot(f"{test_id}_failure.png")