import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage
from pages.electronics_page import ElectronicsPage
from pages.product_page import ProductPage
import os

@pytest.mark.usefixtures("driver")
class TestCT001:
    def test_ct_001(self, driver: WebDriver):
        # Étape 1 : Se connecter au site web
        login_page = LoginPage(driver)
        login_page.go_to_url("https://demowebshop.tricentis.com/")
        login_page.click_login_link()
        login_page.set_email("user@example.com")
        login_page.set_password("password123")
        login_page.click_login_button()

        # Étape 2 : Cliquer sur le produit disponible
        electronics_page = ElectronicsPage(driver)
        electronics_page.click_electronics_link()
        product_page = ProductPage(driver)
        product_page.click_product_link("Produit 1")

        # Étape 3 : Vérifier que la page produit est affichée
        product_detail_page = ProductDetailPage(driver)
        assert product_detail_page.get_product_description() != "", "La description du produit n'est pas affichée"
        assert product_detail_page.get_product_price() != "", "Le prix du produit n'est pas affiché"
        assert product_detail_page.is_add_to_cart_button_visible(), "Le bouton 'Add to cart' n'est pas visible"

        # Vérification du résultat attendu
        assert product_detail_page.is_product_page_visible(), "La page produit n'est pas affichée"

    def test_ct_001_failure(self, driver: WebDriver):
        try:
            self.test_ct_001(driver)
        except AssertionError as e:
            screenshot_path = os.path.join(os.getcwd(), f"CT-001_failure.png")
            driver.save_screenshot(screenshot_path)
            raise AssertionError(f"Échec du test CT-001 : {e}")