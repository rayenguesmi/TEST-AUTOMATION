from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
from pages.product_detail_page import ProductDetailPage
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

@pytest.mark.usefixtures("driver")
class TestNavigationVersDetailProduit:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.home_page = HomePage(driver)
        self.product_detail_page = ProductDetailPage(driver)

    def test_navigation_vers_detail_produit(self, driver: WebDriver):
        # Étape 1 : Se rendre sur la page d'accueil du site web.
        self.home_page.navigate_to("https://www.google.com")
        self.home_page.search_for_product("iPhone 14")

        # Étape 2 : Cliquer sur un produit disponible.
        self.home_page.click_on_product()

        # Étape 3 : Vérifier que la page produit est affichée avec les détails suivants : description, prix, bouton 'Add to cart'.
        assert self.product_detail_page.is_description_visible()
        assert self.product_detail_page.get_price() == "999,99 €"
        assert self.product_detail_page.is_add_to_cart_button_visible()

        # Vérification de la présence des éléments sur la page produit
        assert WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#description"))
        )
        assert WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#price"))
        )
        assert WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
        )

        # Capture d'un screenshot en cas d'échec
        try:
            assert True
        except AssertionError:
            self.driver.save_screenshot("CT-001_failure.png")
            raise

    def test_navigation_vers_detail_produit_echec(self, driver: WebDriver):
        # Étape 1 : Se rendre sur la page d'accueil du site web.
        self.home_page.navigate_to("https://www.google.com")
        self.home_page.search_for_product("Produit inconnu")

        # Étape 2 : Cliquer sur un produit disponible.
        self.home_page.click_on_product()

        # Étape 3 : Vérifier que la page produit n'est pas affichée.
        try:
            assert not self.product_detail_page.is_description_visible()
            assert not self.product_detail_page.is_add_to_cart_button_visible()
        except AssertionError:
            self.driver.save_screenshot("CT-001_failure.png")
            raise