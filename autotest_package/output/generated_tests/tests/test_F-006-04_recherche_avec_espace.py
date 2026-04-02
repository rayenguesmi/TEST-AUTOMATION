from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
import pytest
import time

@pytest.fixture
def home_page(driver: WebDriver):
    return HomePage(driver)

def test_recherche_avec_espace(home_page: HomePage, driver: WebDriver):
    # Étape 1 : Ouvrir le site
    home_page.open_url("https://www.google.com")

    # Étape 2 : Saisir 'phone portable' dans le champ de recherche
    home_page.search_input.send_keys("phone portable")

    # Étape 3 : Cliquez sur le bouton de recherche
    home_page.search_button.click()

    # Résultat attendu : Les résultats de recherche affichent des produits contenant le mot-clé 'phone portable'
    assert "phone portable" in home_page.search_results.text

    # Capture un screenshot en cas d'échec
    try:
        assert "phone portable" in home_page.search_results.text
    except AssertionError:
        driver.save_screenshot("F-006-04_failure.png")
        raise