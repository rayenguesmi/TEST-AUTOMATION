import pytest
from pages.electronics_page import ElectronicsPage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductDetailPage
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

@pytest.mark.usefixtures("driver")
class TestCT001:
    def test_ajout_au_panier(self, driver):
        # Étape 1 : Se connecter
        login_page = LoginPage(driver)
        login_page.se_connecter("username", "password")

        # Étape 2 : Se rendre sur la page du produit
        electronics_page = ElectronicsPage(driver)
        electronics_page.se_rendre_sur_la_page_du_produit()

        # Étape 3 : Cliquer sur 'Add to cart'
        product_detail_page = ProductDetailPage(driver)
        product_detail_page.clique_sur_add_to_cart()

        # Étape 4 : Vérifier que le produit est ajouté au panier
        assert product_detail_page.produit_est_ajoute_au_panier() == True

        # Étape 5 : Vérifier que le message de confirmation est affiché
        assert product_detail_page.message_de_confirmation_est_affiche() == True

        # Étape 6 : Vérifier que le compteur du panier est mis à jour
        assert product_detail_page.compteur_du_panier_est_mis_a_jour() == True

        # Vérification finale
        assert product_detail_page.produit_est_ajoute_au_panier() == True

        # Capture d'un screenshot en cas d'échec
        try:
            assert product_detail_page.produit_est_ajoute_au_panier() == True
        except AssertionError:
            driver.save_screenshot("CT-001_failure.png")
            raise