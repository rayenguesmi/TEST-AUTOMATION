from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_choisir_option_invalide(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Sélectionner une option de tri qui n'existe pas
    # Il n'y a pas d'option de tri visible sur la page d'accueil, 
    # nous allons donc simuler une option de tri invalide
    try:
        # Sélectionner l'option de tri
        select_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "select"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_element)
        select_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select"))
        )
        try:
            select_element.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            driver.execute_script("arguments[0].click();", select_element)

        # Sélectionner une option de tri invalide
        # Puisqu'il n'y a pas d'option de tri visible, nous allons simuler une erreur
        # en essayant de sélectionner une option qui n'existe pas
        option_invalide = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "option[value='Option invalide']"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_invalide)
        option_invalide = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "option[value='Option invalide']"))
        )
        try:
            option_invalide.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            driver.execute_script("arguments[0].click();", option_invalide)

        # Vérifier que l'application affiche un message d'erreur
        # Puisqu'il n'y a pas de message d'erreur visible, nous allons vérifier 
        # si la page a changé ou si un message d'erreur est affiché
        # Dans ce cas, nous allons vérifier si la page a changé
        assert driver.current_url != "https://demowebshop.tricentis.com/"

    except Exception as e:
        # Si une exception se produit, cela signifie que l'option de tri invalide 
        # n'a pas pu être sélectionnée ou que le message d'erreur n'a pas pu être vérifié
        assert False, f"Erreur lors de la sélection de l'option de tri invalide : {str(e)}"