from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_pagination_avec_un_seul_produit(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Cliquer sur le bouton 'Next'
    next_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='next-button']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
    next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test='next-button']")))
    try:
        next_button.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", next_button)

    # Étape 3 : Vérifier que le bouton 'Next' est désactivé
    next_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='next-button']")))
    assert next_button.get_attribute("disabled") is not None

    # Étape 4 : Cliquer sur le bouton 'Previous'
    previous_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='previous-button']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", previous_button)
    previous_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test='previous-button']")))
    try:
        previous_button.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", previous_button)

    # Étape 5 : Vérifier que le bouton 'Previous' est désactivé
    previous_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='previous-button']")))
    assert previous_button.get_attribute("disabled") is not None