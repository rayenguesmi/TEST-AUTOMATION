from selenium.webdriver.remote.webdriver import WebDriver
from pages.electronics_page import ElectronicsPage
from pages.pagination_page import PaginationPage
from pages.product_detail_page import ProductDetailPage
from pages.tri_page import TriPage

def test_electronics_display(driver):
    electronics_page = ElectronicsPage(driver)
    electronics_page.open()
    
    assert electronics_page.is_products_listed(), "La page ne contient pas de produits"
    for product in electronics_page.get_products():
        assert product.has_name(), "Le produit n'a pas de nom"
        assert product.has_price(), "Le produit n'a pas de prix"
        assert product.has_image(), "Le produit n'a pas d'image"

def test_invalid_url_error_404(driver):
    driver.get("https://demowebshop.tricentis.com/electronics/invalid-url")
    
    error_page = ErrorPage(driver)
    assert error_page.is_404_error(), "La page ne contient pas d'erreur 404"

def test_invalid_url_redirection(driver):
    driver.get("https://demowebshop.tricentis.com/electronics/invalid-url")
    
    pagination_page = PaginationPage(driver)
    assert pagination_page.is_on_another_page(), "L'utilisateur n'est pas redirigé vers une autre page"

def test_electronics_display_with_price_filter(driver):
    electronics_page = ElectronicsPage(driver)
    electronics_page.open()
    
    tri_page = TriPage(driver)
    tri_page.apply_price_filter(100)
    
    assert all(product.price < 100 for product in electronics_page.get_products()), "La liste des produits ne respecte pas le filtre de prix"