# tests/test_recherche_produit_inexistant.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
import pytest
import time

@pytest.mark.usefixtures("driver")
class TestRechercheProduitInexistant:
    def test_recherche_produit_inexistant(self, driver: WebDriver):
        home_page = HomePage(driver)
        home_page.navigate_to_url("https://www.google.com")
        
        # Saisir 'produit_inexistant' dans le champ de recherche
        home_page.search_input.send_keys("produit_inexistant")
        
        # Cliquez sur le bouton de recherche
        home_page.search_button.click()
        
        # Attendre que le message 'Aucun résultat' soit affiché
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        message_aucun_resultat = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@id='rso']//div[@class='card-section']//div[@class='yuRUbf']//a//h3"))
        )
        
        # Vérifier que le message 'Aucun résultat' est affiché
        assert message_aucun_resultat.text == "Aucun résultat"
        
        # Capture un screenshot en cas d'échec
        try:
            assert True
        except AssertionError:
            driver.save_screenshot("F-006-02_failure.png")
            raise