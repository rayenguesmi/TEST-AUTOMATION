import pytest
from pages.electronics_page import ElectronicsPage
from pages.product_detail_page import ProductDetailPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

@pytest.mark.usefixtures("driver")
class TestCT004:
    def test_navigation_vers_detail_produit(self, driver):
        # Étape 1 : Se rendre sur la page d'accueil du site web
        electronics_page = ElectronicsPage(driver)
        electronics_page.navigate_to_electronics_page()

        # Étape 2 : Cliquer sur un produit avec un nom trés long
        produit = "Téléphone portable Apple iPhone 14 Pro Max avec écran tactile et processeur A16 Bionic"
        electronics_page.click_on_product(produit)

        # Étape 3 : Vérifier que la page produit est affichée avec les détails du produit
        product_detail_page = ProductDetailPage(driver)
        assert product_detail_page.is_product_detail_page_displayed(), "La page produit n'est pas affichée"
        assert product_detail_page.get_product_name() == produit, "Le nom du produit est incorrect"
        assert product_detail_page.get_product_description() == "Téléphone portable Apple", "La description du produit est incorrecte"
        assert product_detail_page.get_product_price() == "999,99 €", "Le prix du produit est incorrect"

        # Vérification de la présence des éléments de la page produit
        assert WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#product-name"))
        ), "Le nom du produit n'est pas présent"
        assert WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#product-description"))
        ), "La description du produit n'est pas présente"
        assert WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#product-price"))
        ), "Le prix du produit n'est pas présent"

    def test_failure(self, driver):
        try:
            self.test_navigation_vers_detail_produit(driver)
        except AssertionError as e:
            driver.save_screenshot(f"CT-004_failure.png")
            raise e