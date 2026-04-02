# tests/test_F-005.py
from pages.pagination_page import PaginationPage
from pages.error_page import ErrorPage
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

@pytest.fixture
def driver():
    return WebDriver()

class TestPagination:
    def test_pagination_positive(self, driver):
        pagination_page = PaginationPage(driver)
        pagination_page.navigate_to("https://demowebshop.tricentis.com/electronics")
        pagination_page.click_next()
        assert pagination_page.is_element_present("//div[@class='products-list']")

    def test_pagination_negative(self, driver):
        error_page = ErrorPage(driver)
        error_page.navigate_to("/non-existent-page")
        assert "Error 404: Page not found" in error_page.get_title()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_failurereports(report):
    if report.when == "call" and report.failed:
        driver = report.function.__wrapped__.driver
        driver.save_screenshot(f"{report.nodeid}_failure.png")