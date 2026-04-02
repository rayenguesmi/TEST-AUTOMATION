# tests/test_electronics_page.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.electronics_page import ElectronicsPage
from pages.home_page import HomePage
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

@pytest.fixture
def electronics_page(driver: WebDriver):
    """Ouvrir la page Electronics"""
    home_page = HomePage(driver)
    home_page.open_url("https://example.com/electronics")
    return ElectronicsPage(driver)

def test_electronics_page(electronics_page: ElectronicsPage):
    """Vérifier que la page affiche correctement la liste des produits électroniques"""
    # Vérifier que la page affiche une liste de produits électroniques
    assert electronics_page.is_list_of_products_visible()

    # Sélectionner un produit aléatoire de la liste
    product = electronics_page.get_random_product()

    # Vérifier que le produit contient : nom, prix, image
    assert product.get_name() is not None
    assert product.get_price() is not None
    assert product.get_image() is not None

    # Clic sur le produit sélectionné pour vérifier qu'il est cliquable
    product.click()
    time.sleep(1)  # Attendre un peu pour voir si la page change

    # Vérifier que la page a changé
    assert electronics_page.driver.current_url != "https://example.com/electronics"

@pytest.mark.parametrize("url", ["https://example.com/electronics"])
def test_electronics_page_with_url(driver: WebDriver, url: str):
    """Vérifier que la page affiche correctement la liste des produits électroniques avec une URL spécifique"""
    home_page = HomePage(driver)
    home_page.open_url(url)
    electronics_page = ElectronicsPage(driver)

    # Vérifier que la page affiche une liste de produits électroniques
    assert electronics_page.is_list_of_products_visible()

    # Sélectionner un produit aléatoire de la liste
    product = electronics_page.get_random_product()

    # Vérifier que le produit contient : nom, prix, image
    assert product.get_name() is not None
    assert product.get_price() is not None
    assert product.get_image() is not None

    # Clic sur le produit sélectionné pour vérifier qu'il est cliquable
    product.click()
    time.sleep(1)  # Attendre un peu pour voir si la page change

    # Vérifier que la page a changé
    assert electronics_page.driver.current_url != url

def test_electronics_page_failure(electronics_page: ElectronicsPage):
    """Vérifier que la page affiche correctement la liste des produits électroniques en cas d'échec"""
    try:
        # Vérifier que la page affiche une liste de produits électroniques
        assert electronics_page.is_list_of_products_visible()

        # Sélectionner un produit aléatoire de la liste
        product = electronics_page.get_random_product()

        # Vérifier que le produit contient : nom, prix, image
        assert product.get_name() is not None
        assert product.get_price() is not None
        assert product.get_image() is not None

        # Clic sur le produit sélectionné pour vérifier qu'il est cliquable
        product.click()
        time.sleep(1)  # Attendre un peu pour voir si la page change

        # Vérifier que la page a changé
        assert electronics_page.driver.current_url != "https://example.com/electronics"
    except AssertionError as e:
        # Capture un screenshot en cas d'échec
        electronics_page.driver.save_screenshot("CT-001_failure.png")
        raise e