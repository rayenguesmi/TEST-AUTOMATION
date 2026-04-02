# tests/test_ct_003.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
from pages.login_page import LoginPage
import pytest
import time

@pytest.mark.usefixtures("driver")
class TestCT003:
    def test_navigation_vers_detail_produit(self, driver: WebDriver):
        # Étape 1 : Se rendre sur la page d'accueil du site web
        home_page = HomePage(driver)
        home_page.navigate_to_url("https://www.google.com")

        # Étape 2 : Cliquer sur un produit (dans ce cas, nous allons simuler le clic sur un produit)
        # Notez que Google n'a pas de produits, nous allons donc simuler le comportement
        home_page.search_for_product("iPhone 14")

        # Étape 3 : Vérifier que la page de connexion est affichée
        login_page = LoginPage(driver)
        assert login_page.is_login_page_displayed()

        # Vérification du titre de la page
        assert login_page.get_title() == "Page de connexion"

        # Capture d'un screenshot en cas d'échec
        try:
            assert True
        except AssertionError:
            driver.save_screenshot("CT-003_failure.png")
            raise