# tests/test_tri_page.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.tri_page import TriPage
from pages.home_page import HomePage
import pytest
import time

@pytest.mark.usefixtures("driver")
class TestTriPage:
    def test_tri_prix_ascendant(self, driver: WebDriver):
        home_page = HomePage(driver)
        home_page.ouvrir_site("https://www.google.com")
        
        # Récupération de la page d'accueil
        tri_page = TriPage(driver)
        
        # Sélection de l'option de tri 'Prix ascendant'
        tri_page.selectionner_tri_prix_ascendant()
        
        # Vérification que les produits sont triés par prix ascendant
        prix_produits = tri_page.recuperer_prix_produits()
        assert all(prix_produits[i] <= prix_produits[i+1] for i in range(len(prix_produits)-1)), "Les produits ne sont pas triés par prix ascendant"
        
        # Vérification que les produits sont affichés dans le bon ordre
        noms_produits = tri_page.recuperer_noms_produits()
        assert noms_produits == ["Produit 2", "Produit 3", "Produit 1"], "Les produits ne sont pas affichés dans le bon ordre"
        
        # Capture d'un screenshot en cas d'échec
        try:
            assert True
        except AssertionError:
            driver.save_screenshot("CT-001_failure.png")
            raise

    def test_tri_prix_ascendant_avec_produits(self, driver: WebDriver):
        home_page = HomePage(driver)
        home_page.ouvrir_site("https://www.google.com")
        
        # Récupération de la page d'accueil
        tri_page = TriPage(driver)
        
        # Ajout de produits
        tri_page.ajouter_produit("Produit 1", 10.99)
        tri_page.ajouter_produit("Produit 2", 5.99)
        tri_page.ajouter_produit("Produit 3", 7.99)
        
        # Sélection de l'option de tri 'Prix ascendant'
        tri_page.selectionner_tri_prix_ascendant()
        
        # Vérification que les produits sont triés par prix ascendant
        prix_produits = tri_page.recuperer_prix_produits()
        assert all(prix_produits[i] <= prix_produits[i+1] for i in range(len(prix_produits)-1)), "Les produits ne sont pas triés par prix ascendant"
        
        # Vérification que les produits sont affichés dans le bon ordre
        noms_produits = tri_page.recuperer_noms_produits()
        assert noms_produits == ["Produit 2", "Produit 3", "Produit 1"], "Les produits ne sont pas affichés dans le bon ordre"
        
        # Capture d'un screenshot en cas d'échec
        try:
            assert True
        except AssertionError:
            driver.save_screenshot("CT-001_failure.png")
            raise