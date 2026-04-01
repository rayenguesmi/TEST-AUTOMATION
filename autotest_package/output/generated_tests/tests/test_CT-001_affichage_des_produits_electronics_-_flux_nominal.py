import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from pages.electronics_page import ElectronicsPage
from pages.product_page import ProductPage
import time

@pytest.mark.usefixtures("driver")
class TestElectronicsPage:
    def test_affichage_des_produits_electronics(self, driver: WebDriver):
        # Étape 1 : Accéder à la page Electronics
        electronics_page = ElectronicsPage(driver)
        electronics_page.navigate_to("https://demowebshop.tricentis.com/electronics")

        # Étape 2 : Vérifier que la liste des produits électroniques est affichée
        assert electronics_page.is_product_list_visible(), "La liste des produits électroniques n'est pas affichée"

        # Étape 3 : Vérifier que chaque produit contient : nom, prix, image
        products = electronics_page.get_products()
        for product in products:
            assert product.get_name() != "", "Le nom du produit n'est pas affiché"
            assert product.get_price() != "", "Le prix du produit n'est pas affiché"
            assert product.get_image() != "", "L'image du produit n'est pas affichée"

        # Étape 4 : Cliquez sur un produit pour vérifier que les produits sont cliquables
        product = products[0]
        product.click()
        product_page = ProductPage(driver)
        assert product_page.is_product_detail_visible(), "La page détail du produit n'est pas affichée"

        # Vérification du résultat attendu
        assert True, "La liste des produits électroniques est affichée avec les informations requises et les produits sont cliquables"

    def test_affichage_des_produits_electronics_failure(self, driver: WebDriver):
        try:
            # Étape 1 : Accéder à la page Electronics
            electronics_page = ElectronicsPage(driver)
            electronics_page.navigate_to("https://demowebshop.tricentis.com/electronics")

            # Étape 2 : Vérifier que la liste des produits électroniques est affichée
            assert electronics_page.is_product_list_visible(), "La liste des produits électroniques n'est pas affichée"

            # Étape 3 : Vérifier que chaque produit contient : nom, prix, image
            products = electronics_page.get_products()
            for product in products:
                assert product.get_name() != "", "Le nom du produit n'est pas affiché"
                assert product.get_price() != "", "Le prix du produit n'est pas affiché"
                assert product.get_image() != "", "L'image du produit n'est pas affichée"

            # Étape 4 : Cliquez sur un produit pour vérifier que les produits sont cliquables
            product = products[0]
            product.click()
            product_page = ProductPage(driver)
            assert product_page.is_product_detail_visible(), "La page détail du produit n'est pas affichée"

            # Vérification du résultat attendu
            assert False, "La liste des produits électroniques est affichée avec les informations requises et les produits sont cliquables"
        except AssertionError as e:
            driver.save_screenshot("CT-001_failure.png")
            raise e