# tests/test_ct_002.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.pagination_page import PaginationPage
from pages.error_page import ErrorPage
import pytest
import time

@pytest.fixture
def driver():
    # Cette fixture est fournie, elle retourne une instance de WebDriver
    pass

def test_ct_002(driver: WebDriver):
    # Étape 1 : Se connecter
    login_page = LoginPage(driver)
    login_page.se_connecter("user@example.com", "password123")

    # Étape 2 : Se rendre sur la page des produits
    home_page = HomePage(driver)
    home_page.se_rendre_sur_la_page_des_produits()

    # Étape 3 : Entrer un numéro de page supérieur au nombre de pages existantes
    pagination_page = PaginationPage(driver)
    pagination_page.entrer_numero_de_page(100)

    # Étape 4 : Cliquer sur le bouton 'Go'
    pagination_page.cliquer_sur_bouton_go()

    # Étape 5 : Vérifier que le message d'erreur est affiché
    error_page = ErrorPage(driver)
    assert error_page.message_d_erreur_est_affiche()

    # Capture d'un screenshot en cas d'échec
    try:
        assert error_page.message_d_erreur_est_affiche()
    except AssertionError:
        driver.save_screenshot("CT-002_failure.png")
        raise