import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage
from pages.electronics_page import ElectronicsPage
from pages.error_page import ErrorPage
from pages.product_detail_page import ProductDetailPage
import time

@pytest.mark.usefixtures("driver")
class TestRechercheProduitInexistant:
    def test_recherche_produit_inexistant(self, driver):
        login_page = LoginPage(driver)
        login_page.se_connecter("username", "password")

        electronics_page = ElectronicsPage(driver)
        electronics_page.rechercher_produit("produit_inexistant")

        try:
            message_aucun_resultat = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@class='no-result']"))
            )
            assert message_aucun_resultat.text == "aucun résultat"
        except AssertionError:
            driver.save_screenshot(f"CT-002_failure.png")
            assert False, "Le message 'aucun résultat' n'est pas affiché"

        finally:
            driver.quit()