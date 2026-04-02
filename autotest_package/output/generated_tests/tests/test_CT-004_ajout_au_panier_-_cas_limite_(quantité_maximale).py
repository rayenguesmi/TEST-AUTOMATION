# tests/test_ct_004.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
from pages.product_detail_page import ProductDetailPage
from pages.cart_page import CartPage
import pytest
import time

@pytest.mark.usefixtures("driver")
class TestCT004:
    def test_ct_004(self, driver: WebDriver):
        # Étape 1 : Se rendre sur la page du produit
        home_page = HomePage(driver)
        home_page.se_rendre_sur_la_page_du_produit()

        # Étape 2 : Saisir la quantité maximale
        product_detail_page = ProductDetailPage(driver)
        product_detail_page.saisir_quantite_maximale(10)

        # Étape 3 : Cliquer sur 'Add to cart'
        product_detail_page.cliquer_sur_add_to_cart()

        # Étape 4 : Vérifier que le produit est ajouté au panier
        assert product_detail_page.produit_est_ajoute_au_panier()

        # Étape 5 : Vérifier que le message de confirmation est affiché
        assert product_detail_page.message_de_confirmation_est_affiche()

        # Étape 6 : Vérifier que le compteur du panier est mis à jour
        cart_page = CartPage(driver)
        assert cart_page.compteur_du_panier_est_mis_a_jour(10)

        # Capture d'un screenshot en cas d'échec
        try:
            assert True
        except AssertionError:
            driver.save_screenshot("CT-004_failure.png")
            raise