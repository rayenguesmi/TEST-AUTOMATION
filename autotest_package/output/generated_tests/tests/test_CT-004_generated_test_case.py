import pytest
from pages.electronics_page import ElectronicsPage
from pages.login_page import LoginPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

@pytest.mark.usefixtures("driver")
class TestCT004:
    def test_ct004(self, driver):
        # Étape 1 : Ouvrir le site et se connecter
        login_page = LoginPage(driver)
        login_page.se_connecter("username", "password")

        # Étape 2 : Accéder à la page des produits électroniques
        electronics_page = ElectronicsPage(driver)
        electronics_page.acceder_a_la_page()

        # Étape 3 : Sélectionner l'option de tri 'Prix : ascendant'
        electronics_page.selectionner_option_tri("Prix : ascendant")

        # Étape 4 : Vérifier que les produits avec des prix nuls sont affichés en premier
        produits = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".produit"))
        )
        prix_nuls = [produit for produit in produits if produit.find_element(By.CSS_SELECTOR, ".prix").text == "0"]
        assert prix_nuls == produits[:len(prix_nuls)], "Les produits avec des prix nuls ne sont pas affichés en premier"

        # Capture d'un screenshot en cas d'échec
        try:
            assert True
        except AssertionError:
            driver.save_screenshot("CT-004_failure.png")
            raise