import pytest
from pages.electronics_page import ElectronicsPage
from pages.product_detail_page import ProductDetailPage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

@pytest.mark.usefixtures("driver")
class TestNavigationVersDetailProduit:
    def test_navigation_vers_detail_produit(self, driver):
        # Étape 1 : Se rendre sur la page d'accueil du site web
        electronics_page = ElectronicsPage(driver)
        electronics_page.navigate_to_electronics_page()

        # Étape 2 : Cliquer sur un produit disponible
        produit = "iPhone 14"
        electronics_page.click_on_product(produit)

        # Étape 3 : Vérifier que la page produit est affichée avec les détails suivants : description, prix, bouton 'Add to cart'
        product_detail_page = ProductDetailPage(driver)
        description = "Téléphone portable Apple"
        prix = "999,99 €"

        # Vérification de la présence des éléments
        assert WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#product_description"))
        )
        assert WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#product_price"))
        )
        assert WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
        )

        # Vérification des valeurs
        assert product_detail_page.get_product_description() == description
        assert product_detail_page.get_product_price() == prix

        # Capture d'un screenshot en cas d'échec
        try:
            assert True
        except AssertionError:
            driver.save_screenshot("CT-001_failure.png")
            raise

        # Vérification finale
        assert product_detail_page.is_product_detail_page_displayed()