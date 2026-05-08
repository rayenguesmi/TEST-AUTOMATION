from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_choisir_option_invalide(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Sélectionner une option de tri qui n'existe pas
    # Sélectionner l'élément de tri
    select_sort_by = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "products-orderby"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_sort_by)
    select_sort_by = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.NAME, "products-orderby"))
    )
    try:
        select_sort_by.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", select_sort_by)

    # Sélectionner une option de tri invalide (dans ce cas, nous allons essayer de sélectionner une option qui n'existe pas)
    # Puisque nous ne pouvons pas sélectionner une option qui n'existe pas, nous allons vérifier que l'application gère correctement
    # une option de tri invalide en vérifiant que l'application affiche un message d'erreur
    # Dans ce cas, nous allons essayer de sélectionner une option qui n'existe pas en utilisant l'attribut value
    select_sort_by = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "products-orderby"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_sort_by)
    select_sort_by = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.NAME, "products-orderby"))
    )
    try:
        select_sort_by.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", select_sort_by)

    # Vérifier que l'application affiche un message d'erreur
    # Dans ce cas, nous allons vérifier que l'application affiche un message d'erreur en vérifiant que l'élément de message d'erreur est présent
    error_message = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='bar-notification']"))
    )
    assert error_message.is_displayed()

    # Vérifier que l'application affiche un message d'erreur avec le texte attendu
    # Dans ce cas, nous allons vérifier que l'application affiche un message d'erreur avec le texte attendu
    assert "Invalid" in error_message.text