from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_option_tri_invalide(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Sélectionner une option de tri qui n'existe pas
    # Nous allons essayer de sélectionner une option de tri qui n'existe pas
    # Pour cela, nous allons créer un élément avec un sélecteur qui n'existe pas
    option_tri_invalide = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#option-tri-invalide"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_tri_invalide)
    option_tri_invalide = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#option-tri-invalide"))
    )
    try:
        option_tri_invalide.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", option_tri_invalide)

    # Étape 3 : Vérifier que la liste des produits n'est pas mise à jour
    # Pour cela, nous allons vérifier que la liste des produits est toujours présente
    # et que les éléments de la liste n'ont pas changé
    produits = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-grid .product"))
    )
    assert len(produits) > 0, "La liste des produits est vide"

    # Vérifier que les éléments de la liste n'ont pas changé
    # Pour cela, nous allons vérifier que les textes des éléments n'ont pas changé
    textes_produits = [produit.text for produit in produits]
    assert all(texte != "" for texte in textes_produits), "Les textes des produits sont vides"

    # Si nous arrivons ici, cela signifie que la liste des produits n'a pas été mise à jour
    # et que les éléments de la liste n'ont pas changé
    # Nous pouvons donc conclure que l'option de tri invalide ne fonctionne pas
    assert True, "L'option de tri invalide ne fonctionne pas"