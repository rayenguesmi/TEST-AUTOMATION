import pytest
from pages.electronics_page import ElectronicsPage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductDetailPage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

@pytest.mark.usefixtures("driver")
class TestRechercheProduitExistant:
    def test_recherche_produit_existant(self, driver):
        login_page = LoginPage(driver)
        login_page.se_connecter("username", "password")

        electronics_page = ElectronicsPage(driver)
        electronics_page.rechercher_produit("phone")

        try:
            produits = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-item"))
            )
            assert len(produits) > 0, "Aucun produit trouvé"
            for produit in produits:
                assert "phone" in produit.text.lower(), "Produit non lié au mot-clé 'phone'"
        except AssertionError as e:
            driver.save_screenshot(f"CT-001_failure_{time.time()}.png")
            raise e