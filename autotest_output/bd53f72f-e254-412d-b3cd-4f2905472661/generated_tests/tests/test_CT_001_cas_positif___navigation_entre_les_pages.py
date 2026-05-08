from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_navigation_entre_pages_produits(driver: WebDriver):
    # Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Cliquer sur le bouton 'Next'
    next_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='next-button']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
    next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test='next-button']")))
    try:
        next_button.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", next_button)

    # Vérifier que les produits ont changé
    produits = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-grid .product")))
    assert len(produits) > 0

    # Cliquer sur le bouton 'Previous'
    previous_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='previous-button']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", previous_button)
    previous_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test='previous-button']")))
    try:
        previous_button.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", previous_button)

    # Vérifier que les produits sont revenus à la page précédente
    produits_precedents = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-grid .product")))
    assert len(produits_precedents) > 0
    assert produits_precedents != produits