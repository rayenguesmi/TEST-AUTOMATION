# tests/test_tri_prix_descendant.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
from pages.tri_page import TriPage
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

@pytest.mark.usefixtures("driver")
class TestTriPrixDescendant:
    def test_tri_prix_descendant(self, driver: WebDriver):
        # Étape 1 : Ouvrir le site
        home_page = HomePage(driver)
        home_page.ouvrir_site("https://www.google.com")

        # Étape 2 : Sélectionner l'option de tri 'Prix descendant'
        tri_page = TriPage(driver)
        tri_page.selectionner_tri_prix_descendant()

        # Étape 3 : Vérifier que les produits sont triés par prix descendant
        produits = tri_page.obtenir_prix_produits()
        assert all(produits[i] >= produits[i+1] for i in range(len(produits)-1)), "Les produits ne sont pas triés par prix descendant"

        # Vérification des prix des produits
        prix_produits = [10.99, 7.99, 5.99]
        assert produits == prix_produits, "Les prix des produits ne correspondent pas"

    def test_tri_prix_descendant_echec(self, driver: WebDriver):
        # Étape 1 : Ouvrir le site
        home_page = HomePage(driver)
        home_page.ouvrir_site("https://www.google.com")

        # Étape 2 : Sélectionner l'option de tri 'Prix descendant'
        tri_page = TriPage(driver)
        tri_page.selectionner_tri_prix_descendant()

        # Étape 3 : Vérifier que les produits sont triés par prix descendant
        produits = tri_page.obtenir_prix_produits()
        try:
            assert all(produits[i] >= produits[i+1] for i in range(len(produits)-1)), "Les produits ne sont pas triés par prix descendant"
        except AssertionError:
            driver.save_screenshot("CT-002_failure.png")
            raise