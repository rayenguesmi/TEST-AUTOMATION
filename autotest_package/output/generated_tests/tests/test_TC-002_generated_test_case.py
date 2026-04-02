from selenium.webdriver.remote.webdriver import WebDriver
from pages.product_page import ProductPage
from pages.error_page import ErrorPage

def test_product_details_nominal(driver):
    product_page = ProductPage(driver)
    product_page.open()
    
    # Step 2: Clic sur un produit disponible dans la liste des produits
    product_page.click_first_available_product()
    
    # Step 3: Vérifier que la redirection vers la page d'informations du produit est effectuée avec succès
    assert product_page.is_details_page_opened(), "La page de détails du produit n'est pas ouverte"
    
    # Step 4: Vérifier l'affichage de la description du produit
    assert product_page.is_product_description_visible(), "La description du produit n'est pas visible"
    
    # Step 5: Vérifier l'affichage du prix du produit
    assert product_page.is_product_price_visible(), "Le prix du produit n'est pas visible"
    
    # Step 6: Vérifier l'affichage du bouton 'Add to cart'
    assert product_page.is_add_to_cart_button_visible(), "Le bouton 'Add to cart' n'est pas visible"

def test_product_details_unavailable(driver):
    product_page = ProductPage(driver)
    product_page.open()
    
    # Step 2: Clic sur un produit indisponible dans la liste des produits
    product_page.click_first_unavailable_product()
    
    # Step 3: Vérifier que la redirection vers la page d'informations du produit est effectuée avec succès
    assert product_page.is_details_page_opened(), "La page de détails du produit n'est pas ouverte"
    
    # Step 4: Vérifier l'affichage d'un message indiquant que le produit n'est pas disponible
    assert product_page.is_product_unavailable_message_visible(), "Le message 'Produit indisponible' n'est pas visible"

def test_product_details_non_existing(driver):
    error_page = ErrorPage(driver)
    
    # Step 2: Clic sur un lien vers un produit qui n'existe pas
    driver.get("https://demowebshop.tricentis.com/electronics/non-existing-product")
    
    # Step 3: Vérifier que la redirection vers une page d'erreur est effectuée avec succès
    assert error_page.is_error_page_opened(), "La page d'erreur n'est pas ouverte"