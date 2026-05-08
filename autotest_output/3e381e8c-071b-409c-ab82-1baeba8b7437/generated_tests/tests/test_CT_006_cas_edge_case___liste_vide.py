from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_CT_006(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Sélectionner une option de tri
    select_sort_by = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "products-orderby"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_sort_by)
    select_sort_by = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "products-orderby"))
    )
    try:
        select_sort_by.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", select_sort_by)

    # Sélectionner l'option "Prix: Bas à élevé"
    option_tri = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//option[text()='Prix: Bas à élevé']"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_tri)
    option_tri = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//option[text()='Prix: Bas à élevé']"))
    )
    try:
        option_tri.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", option_tri)

    # Étape 3 : Vérifier que l'application affiche un message indiquant que la liste est vide
    message_liste_vide = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[text()='No products were found that matched your criteria.']"))
    )
    assert message_liste_vide.text == "No products were found that matched your criteria."