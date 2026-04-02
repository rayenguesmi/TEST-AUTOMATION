# tests/test_ct_001.py
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
from pages.product_page import ProductPage
import pytest
import time

@pytest.fixture
def home_page(driver: WebDriver):
    return HomePage(driver)

@pytest.fixture
def product_page(driver: WebDriver):
    return ProductPage(driver)

def test_ct_001(driver: WebDriver, home_page: HomePage, product_page: ProductPage):
    # Étape 1 : Se rendre sur la page des produits
    home_page.navigate_to_product_page()
    
    # Étape 2 : Cliquer sur le bouton 'Next'
    product_page.click_next_button()
    
    # Étape 3 : Vérifier que les produits changent
    initial_products = product_page.get_products()
    product_page.click_next_button()
    new_products = product_page.get_products()
    assert initial_products != new_products, "Les produits n'ont pas changé"

    # Capture d'un screenshot en cas d'échec
    try:
        assert True
    except AssertionError:
        driver.save_screenshot("CT-001_failure.png")
        raise

def test_ct_001_login(driver: WebDriver, home_page: HomePage, product_page: ProductPage):
    # Connexion à l'application
    from pages.login_page import LoginPage
    login_page = LoginPage(driver)
    login_page.login("user@example.com", "password123")
    
    # Étape 1 : Se rendre sur la page des produits
    home_page.navigate_to_product_page()
    
    # Étape 2 : Cliquer sur le bouton 'Next'
    product_page.click_next_button()
    
    # Étape 3 : Vérifier que les produits changent
    initial_products = product_page.get_products()
    product_page.click_next_button()
    new_products = product_page.get_products()
    assert initial_products != new_products, "Les produits n'ont pas changé"

    # Capture d'un screenshot en cas d'échec
    try:
        assert True
    except AssertionError:
        driver.save_screenshot("CT-001_failure.png")
        raise