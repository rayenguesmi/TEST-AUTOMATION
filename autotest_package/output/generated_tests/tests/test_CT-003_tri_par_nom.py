# tests/test_tri_par_nom.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
from pages.tri_page import TriPage
import pytest
import time

@pytest.mark.usefixtures("driver")
class TestTriParNom:
    def test_tri_par_nom(self, driver: WebDriver):
        # Étape 1 : Ouvrir le site
        home_page = HomePage(driver)
        home_page.open_url("https://www.google.com")

        # Étape 2 : Sélectionner l'option de tri 'Nom'
        tri_page = TriPage(driver)
        tri_page.select_tri_par_nom()

        # Étape 3 : Vérifier que les produits sont triés par nom
        produits = tri_page.get_produits()
        noms_produits = [produit.get_nom() for produit in produits]
        assert noms_produits == sorted(noms_produits)

        # Vérification du résultat attendu
        assert tri_page.get_resultat_attendu() == "Les produits sont triés par nom"

        # Capture d'un screenshot en cas d'échec
        try:
            assert True
        except AssertionError:
            driver.save_screenshot("CT-003_failure.png")
            raise