from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_CT_006(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Sélectionner une option de tri
    option_tri = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[name='products-orderby']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_tri)
    option_tri = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[name='products-orderby']")))
    try:
        option_tri.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", option_tri)

    # Sélectionner l'option "Prix: Bas à élevé"
    option_tri_value = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[value='5']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_tri_value)
    option_tri_value = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[value='5']")))
    try:
        option_tri_value.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", option_tri_value)

    # Étape 3 : Vérifier que l'application affiche un message indiquant que la liste est vide
    message_vide = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".no-data")))
    assert message_vide.text == "No products were found that matched your criteria."