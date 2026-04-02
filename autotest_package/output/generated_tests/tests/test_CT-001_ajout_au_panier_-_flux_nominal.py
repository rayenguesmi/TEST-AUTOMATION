# tests/test_ajout_au_panier.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
import pytest
import time

@pytest.fixture
def home_page(driver: WebDriver):
    return HomePage(driver)

@pytest.fixture
def product_page(driver: WebDriver):
    return ProductPage(driver)

@pytest.fixture
def cart_page(driver: WebDriver):
    return CartPage(driver)

def test_ajout_au_panier(home_page: HomePage, product_page: ProductPage, cart_page: CartPage, driver: WebDriver):
    # Étape 1 : Se rendre sur la page du produit
    home_page.se_rendre_sur_la_page_du_produit()
    product_page.attendre_chargement()

    # Étape 2 : Cliquer sur 'Add to cart'
    product_page.clique_sur_ajouter_au_panier()

    # Étape 3 : Vérifier que le produit est ajouté au panier
    assert product_page.produit_est_ajoute_au_panier()

    # Étape 4 : Vérifier que le message de confirmation est affiché
    assert product_page.message_de_confirmation_est_affiche()

    # Étape 5 : Vérifier que le compteur du panier est mis à jour
    assert cart_page.compteur_du_panier_est_mis_a_jour()

    try:
        assert all([
            product_page.produit_est_ajoute_au_panier(),
            product_page.message_de_confirmation_est_affiche(),
            cart_page.compteur_du_panier_est_mis_a_jour()
        ])
    except AssertionError:
        driver.save_screenshot(f"CT-001_failure.png")
        raise

    time.sleep(2)