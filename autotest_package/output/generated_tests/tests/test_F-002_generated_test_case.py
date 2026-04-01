import pytest
from pages.product_detail_page import ProductDetailPage
from pages.error_page import ErrorPage
from conftest import driver

@pytest.fixture
def product_url():
    return "https://example.com/product/12345"

@pytest.fixture
def unavailable_product_url():
    return "https://example.com/product/99999"

def test_flux_positif(driver, product_url):
    product_detail_page = ProductDetailPage(driver)
    product_detail_page.navigate_to(product_url)
    assert product_detail_page.is_displayed()
    driver.save_screenshot(f"{product_url}_success.png")

def test_flux_negatif(driver, unavailable_product_url):
    error_page = ErrorPage(driver)
    error_page.navigate_to(unavailable_product_url)
    assert error_page.is_displayed()
    driver.save_screenshot(f"{unavailable_product_url}_failure.png")