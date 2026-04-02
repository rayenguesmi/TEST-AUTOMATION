from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
import pytest
import time

@pytest.mark.usefixtures("driver")
class TestRechercheProduitExistant:
    def test_recherche_produit_existant(self, driver: WebDriver):
        home_page = HomePage(driver)
        home_page.navigate_to_url("https://www.google.com")
        
        # Saisir 'phone' dans le champ de recherche
        home_page.search_input.send_keys("phone")
        
        # Cliquez sur le bouton de recherche
        home_page.search_button.click()
        
        # Vérifier que les résultats de recherche affichent des produits contenant le mot-clé 'phone'
        assert "phone" in home_page.search_results.text
        
        # Capture un screenshot en cas d'échec
        try:
            assert "phone" in home_page.search_results.text
        except AssertionError:
            driver.save_screenshot(f"F-006-01_failure.png")
            raise

    def test_recherche_produit_existant_avec_attente(self, driver: WebDriver):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        home_page = HomePage(driver)
        home_page.navigate_to_url("https://www.google.com")
        
        # Saisir 'phone' dans le champ de recherche
        home_page.search_input.send_keys("phone")
        
        # Cliquez sur le bouton de recherche
        home_page.search_button.click()
        
        # Attendre que les résultats de recherche soient affichés
        search_results = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "rso"))
        )
        
        # Vérifier que les résultats de recherche affichent des produits contenant le mot-clé 'phone'
        assert "phone" in search_results.text
        
        # Capture un screenshot en cas d'échec
        try:
            assert "phone" in search_results.text
        except AssertionError:
            driver.save_screenshot(f"F-006-01_failure.png")
            raise