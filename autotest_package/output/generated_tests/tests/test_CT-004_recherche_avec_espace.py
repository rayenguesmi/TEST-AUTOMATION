import pytest
from pages.electronics_page import ElectronicsPage
from pages.login_page import LoginPage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

@pytest.mark.usefixtures("driver")
class TestRechercheAvecEspace:
    def test_recherche_avec_espace(self, driver):
        login_page = LoginPage(driver)
        login_page.se_connecter("username", "password")

        electronics_page = ElectronicsPage(driver)
        electronics_page.saisir_recherche("phone portable")
        electronics_page.clique_bouton_recherche()

        try:
            produits = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-title"))
            )
            assert len(produits) > 0, "Aucun produit trouvé"
            for produit in produits:
                assert "phone" in produit.text.lower() or "portable" in produit.text.lower(), "Produit non pertinent"
        except AssertionError as e:
            driver.save_screenshot(f"CT-004_failure_{int(time.time())}.png")
            raise e