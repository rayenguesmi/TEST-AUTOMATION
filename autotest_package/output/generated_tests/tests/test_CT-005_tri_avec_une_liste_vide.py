# tests/test_tri_page.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.tri_page import TriPage
from pages.home_page import HomePage
import pytest

@pytest.fixture
def tri_page(driver: WebDriver):
    home_page = HomePage(driver)
    home_page.open()
    return TriPage(driver)

def test_tri_avec_liste_vide(tri_page: TriPage, driver: WebDriver):
    # Sélectionner une option de tri
    tri_page.select_tri_option()

    # Vérifier que l'application affiche un message indiquant que la liste est vide
    assert tri_page.is_list_empty_message_displayed()

    # Capture un screenshot en cas d'échec
    try:
        assert True
    except AssertionError:
        driver.save_screenshot("CT-005_failure.png")
        raise