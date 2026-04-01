import pytest
from pages.electronics_page import ElectronicsPage
from pages.error_page import ErrorPage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductDetailPage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

@pytest.mark.usefixtures("driver")
class TestCT002:
    def test_navigation_vers_detail_produit_indisponible(self, driver):
        # Étape 1 : Se rendre sur la page d'accueil du site web
        login_page = LoginPage(driver)
        login_page.se_connecter("username", "password")

        # Étape 2 : Cliquer sur un produit indisponible
        electronics_page = ElectronicsPage(driver)
        electronics_page.clique_sur_produit_indisponible("iPhone 13")

        # Étape 3 : Vérifier que la page produit n'est pas affichée ou qu'un message d'erreur est affiché
        try:
            product_detail_page = ProductDetailPage(driver)
            assert product_detail_page.est_affichee() == False
        except:
            error_page = ErrorPage(driver)
            assert error_page.est_affichee() == True
            assert error_page.obtenir_message_erreur() != ""

        # Capture d'un screenshot en cas d'échec
        if not (product_detail_page.est_affichee() == False or error_page.est_affichee() == True):
            screenshot_path = os.path.join(os.getcwd(), "screenshots")
            if not os.path.exists(screenshot_path):
                os.makedirs(screenshot_path)
            driver.save_screenshot(os.path.join(screenshot_path, "CT-002_failure.png"))
            assert False, "La page produit est affichée ou le message d'erreur n'est pas affiché"