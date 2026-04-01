import pytest
from pages.electronics_page import ElectronicsPage
from pages.login_page import LoginPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

@pytest.mark.usefixtures("driver")
class TestRechercheAvecCaracteresSpeciaux:
    def test_recherche_avec_caracteres_speciaux(self, driver):
        login_page = LoginPage(driver)
        login_page.se_connecter("username", "password")
        
        electronics_page = ElectronicsPage(driver)
        electronics_page.rechercher_produit("phone@")
        
        try:
            produits = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-item"))
            )
            assert len(produits) > 0, "Aucun produit trouvé"
            for produit in produits:
                nom_produit = produit.find_element(By.CSS_SELECTOR, ".product-title").text
                assert "phone" in nom_produit.lower(), f"Produit '{nom_produit}' ne contient pas 'phone'"
        except AssertionError as e:
            driver.save_screenshot(f"CT-003_failure.png")
            raise e