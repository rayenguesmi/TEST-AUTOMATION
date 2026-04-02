# tests/test_electronics_page.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.electronics_page import ElectronicsPage
import pytest
import time

@pytest.fixture
def electronics_page(driver: WebDriver):
    """Ouvrir la page Electronics"""
    url = "https://example.com/electronics"
    driver.get(url)
    return ElectronicsPage(driver)

def test_affichage_produit_non_disponible(electronics_page: ElectronicsPage):
    """Vérifier que la page gère correctement l'affichage d'un produit non disponible"""
    # Rechercher un produit qui n'est pas disponible
    produit = "Produit Indisponible"
    electronics_page.rechercher_produit(produit)
    
    # Vérifier que le produit n'est pas affiché dans la liste ou qu'un message d'indisponibilité est affiché
    assert electronics_page.produit_non_disponible() == True
    
    # Capture un screenshot en cas d'échec
    try:
        assert electronics_page.produit_non_disponible() == True
    except AssertionError:
        electronics_page.driver.save_screenshot(f"CT-003_failure.png")
        raise

def test_affichage_message_indisponibilite(electronics_page: ElectronicsPage):
    """Vérifier que le message d'indisponibilité est affiché"""
    # Rechercher un produit qui n'est pas disponible
    produit = "Produit Indisponible"
    electronics_page.rechercher_produit(produit)
    
    # Vérifier que le message d'indisponibilité est affiché
    assert electronics_page.message_indisponibilite() == "Produit non disponible"
    
    # Capture un screenshot en cas d'échec
    try:
        assert electronics_page.message_indisponibilite() == "Produit non disponible"
    except AssertionError:
        electronics_page.driver.save_screenshot(f"CT-003_failure.png")
        raise