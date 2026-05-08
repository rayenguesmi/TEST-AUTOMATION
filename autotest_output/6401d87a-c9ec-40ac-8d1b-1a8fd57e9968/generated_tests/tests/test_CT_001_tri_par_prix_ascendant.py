from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_tri_prix_ascendant(driver: WebDriver):
    # Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Sélectionner l'option de tri 'Prix: Bas à élevé'
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[name='products-orderby']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[name='products-orderby']")))
    try:
        element.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", element)

    # Sélectionner l'option 'Prix: Bas à élevé'
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//option[text()='Prix: Bas à élevé']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//option[text()='Prix: Bas à élevé']")))
    try:
        element.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", element)

    # Vérifier que les produits sont triés par prix ascendant
    elements = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-price")))
    prix = [float(element.text.replace("$", "").replace(",", "")) for element in elements]
    assert prix == sorted(prix), "Les produits ne sont pas triés par prix ascendant"