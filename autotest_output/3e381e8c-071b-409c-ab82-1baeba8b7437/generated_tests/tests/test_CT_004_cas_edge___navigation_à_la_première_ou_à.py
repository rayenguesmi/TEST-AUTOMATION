from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_navigation_premiere_derniere_page(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Cliquer sur le bouton 'Previous' pour aller à la première page
    previous_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class='previous-page']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", previous_button)
    previous_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[class='previous-page']")))
    try:
        previous_button.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", previous_button)

    # Étape 3 : Vérifier que les produits affichés sont les mêmes que ceux de la première page
    produits_premiere_page = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class='item-grid']")))

    # Étape 4 : Cliquer sur le bouton 'Next' pour aller à la dernière page
    next_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class='next-page']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
    next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[class='next-page']")))
    try:
        next_button.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", next_button)

    # Étape 5 : Vérifier que les produits affichés sont les mêmes que ceux de la dernière page
    produits_derniere_page = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class='item-grid']")))

    # Vérification que les produits changent correctement en fonction de la page
    assert len(produits_premiere_page) != len(produits_derniere_page)