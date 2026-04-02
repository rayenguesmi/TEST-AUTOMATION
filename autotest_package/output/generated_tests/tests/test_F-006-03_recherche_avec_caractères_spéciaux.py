# tests/test_recherche.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
import pytest
import time

@pytest.mark.usefixtures("driver")
class TestRecherche:
    def test_recherche_avec_caracteres_speciaux(self, driver: WebDriver):
        # Étape 1 : Ouvrir le site
        home_page = HomePage(driver)
        home_page.navigate_to("https://www.google.com")

        # Étape 2 : Saisir 'phone@' dans le champ de recherche
        home_page.search_input.send_keys("phone@")

        # Étape 3 : Cliquez sur le bouton de recherche
        home_page.search_button.click()

        # Résultat attendu : Les résultats de recherche affichent des produits contenant le mot-clé 'phone'
        assert "phone" in home_page.search_results.text

        # Capture un screenshot en cas d'échec
        try:
            assert "phone" in home_page.search_results.text
        except AssertionError:
            driver.save_screenshot(f"F-006-03_failure.png")
            raise