from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_charger_page_mauvaise_url(driver: WebDriver):
    """
    Test de chargement de la page avec une mauvaise URL.
    
    Étapes :
    1. Accéder à la page https://demowebshop.tricentis.com/electronic
    2. Vérifier que la page affiche une erreur ou une redirection
    
    Résultat attendu :
    La page affiche une erreur ou une redirection
    """
    
    # Étape 1 : Accéder à la page https://demowebshop.tricentis.com/electronic
    url = "https://demowebshop.tricentis.com/electronic"
    driver.get(url)
    
    # Étape 2 : Vérifier que la page affiche une erreur ou une redirection
    try:
        # Attendre la présence d'un élément indiquant une erreur ou une redirection
        error_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
        )
        
        # Vérifier si l'élément contient un message d'erreur
        if "404" in error_element.text or "Erreur" in error_element.text:
            assert True, "La page affiche une erreur ou une redirection"
        else:
            assert False, "La page ne affiche pas d'erreur ou de redirection"
    except Exception as e:
        assert False, f"Erreur lors du test : {str(e)}"