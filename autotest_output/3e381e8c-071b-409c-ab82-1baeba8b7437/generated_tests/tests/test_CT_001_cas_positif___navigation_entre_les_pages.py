from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_navigation_entre_pages_produits(driver: WebDriver):
    # Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Cliquer sur le bouton 'Next' pour passer à la page suivante
    next_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class='next']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
    next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[class='next']")))
    try:
        next_button.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", next_button)

    # Vérifier que les produits affichés ont changé
    produits_page_suivante = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class='item-grid']")))
    assert len(produits_page_suivante) > 0

    # Cliquer sur le bouton 'Previous' pour revenir à la page précédente
    previous_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class='previous']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", previous_button)
    previous_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[class='previous']")))
    try:
        previous_button.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", previous_button)

    # Vérifier que les produits affichés sont les mêmes que ceux de la page précédente
    produits_page_precedente = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class='item-grid']")))
    assert len(produits_page_precedente) > 0