import pytest
from pages.electronics_page import ElectronicsPage
from pages.error_page import ErrorPage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductDetailPage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

@pytest.mark.usefixtures("driver")
class TestCT003:
    def test_navigation_vers_detail_produit_permissions(self, driver):
        # Étape 1 : Se rendre sur la page d'accueil du site web
        electronics_page = ElectronicsPage(driver)
        electronics_page.navigate_to_electronics_page()

        # Étape 2 : Cliquer sur un produit
        product_name = "iPhone 14"
        electronics_page.click_on_product(product_name)

        # Étape 3 : Vérifier que la page de connexion est affichée ou qu'un message d'erreur est affiché
        try:
            login_page = LoginPage(driver)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#username"))
            )
            assert login_page.is_login_page_displayed()
        except:
            error_page = ErrorPage(driver)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".error-message"))
            )
            assert error_page.is_error_message_displayed()

        # Capture un screenshot en cas d'échec
        if not (login_page.is_login_page_displayed() or error_page.is_error_message_displayed()):
            driver.save_screenshot("CT-003_failure.png")
            assert False, "La page de connexion ou le message d'erreur n'est pas affiché"