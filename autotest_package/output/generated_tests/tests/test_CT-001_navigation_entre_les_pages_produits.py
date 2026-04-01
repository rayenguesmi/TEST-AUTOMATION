import pytest
from pages.login_page import LoginPage
from pages.electronics_page import ElectronicsPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os

@pytest.fixture
def login(driver):
    login_page = LoginPage(driver)
    login_page.se_connecter("test@example.com", "password123")
    return login_page

def test_navigation_entre_pages_produits(driver, login):
    electronics_page = ElectronicsPage(driver)
    electronics_page.ouvrir_page_electronics()
    
    # Vérifier que les produits changent
    produits_initiaux = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#produits > div"))
    )
    
    # Cliquer sur le bouton 'Next'
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#next-button"))
    )
    next_button.click()
    
    # Vérifier que les produits changent
    produits_apres_clic = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#produits > div"))
    )
    
    # Vérifier que les produits sont différents
    assert produits_initiaux != produits_apres_clic
    
    # Cliquer sur le bouton 'Previous'
    previous_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#previous-button"))
    )
    previous_button.click()
    
    # Vérifier que les produits reviennent à l'état initial
    produits_apres_clic_previous = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#produits > div"))
    )
    
    # Vérifier que les produits sont identiques à l'état initial
    assert produits_initiaux == produits_apres_clic_previous

    # Vérifier que les boutons 'Next' et 'Previous' sont présents
    assert WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#next-button"))
    )
    assert WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#previous-button"))
    )

@pytest.mark.usefixtures("login")
def test_navigation_entre_pages_produits_echec(driver):
    try:
        test_navigation_entre_pages_produits(driver)
    except AssertionError as e:
        # Capture un screenshot en cas d'échec
        driver.save_screenshot(f"CT-001_failure.png")
        raise e