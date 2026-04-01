import pytest
from pages.electronics_page import ElectronicsPage

def test_CT001_navigation_electronics(driver):
    page = ElectronicsPage(driver)
    driver.get("https://demowebshop.tricentis.com/electronics")
    assert "Electronics" in driver.title
