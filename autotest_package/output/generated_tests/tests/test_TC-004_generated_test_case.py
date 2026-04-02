from pages.tri_page import TriPage
from selenium.webdriver.remote.webdriver import WebDriver

def test_tri_prix_ascendant(driver: WebDriver):
    tri_page = TriPage(driver)
    tri_page.open()
    tri_page.select_sort_option('Prix (ascendant)')
    products_prices = [float(product.text.strip('$')) for product in tri_page.get_product_prices()]
    assert all(products_prices[i] <= products_prices[i + 1] for i in range(len(products_prices) - 1)), "Products not sorted by ascending price"

def test_tri_prix_descendant(driver: WebDriver):
    tri_page = TriPage(driver)
    tri_page.open()
    tri_page.select_sort_option('Prix (descendant)')
    products_prices = [float(product.text.strip('$')) for product in tri_page.get_product_prices()]
    assert all(products_prices[i] >= products_prices[i + 1] for i in range(len(products_prices) - 1)), "Products not sorted by descending price"

def test_tri_nom_ascendant(driver: WebDriver):
    tri_page = TriPage(driver)
    tri_page.open()
    tri_page.select_sort_option('Nom')
    products_names = [product.text for product in tri_page.get_product_names()]
    assert all(products_names[i] <= products_names[i + 1] for i in range(len(products_names) - 1)), "Products not sorted by ascending name"

def test_tri_nom_descendant(driver: WebDriver):
    tri_page = TriPage(driver)
    tri_page.open()
    tri_page.select_sort_option('Nom')
    products_names = [product.text for product in tri_page.get_product_names()]
    assert all(products_names[i] >= products_names[i + 1] for i in range(len(products_names) - 1)), "Products not sorted by descending name"

def test_tri_invalide(driver: WebDriver):
    tri_page = TriPage(driver)
    tri_page.open()
    try:
        tri_page.select_sort_option('Invalide')
    except Exception as e:
        assert str(e).find("Invalid option") != -1, "Error message not indicating invalid option"

def test_tri_prix_meme_prix_ascendant(driver: WebDriver):
    tri_page = TriPage(driver)
    tri_page.open()
    tri_page.select_sort_option('Prix (ascendant)')
    products_names = [product.text for product in tri_page.get_product_names()]
    assert all(products_names[i] <= products_names[i + 1] for i in range(len(products_names) - 1)), "Products not sorted by ascending name when prices are the same"

def test_tri_nom_meme_nom_ascendant(driver: WebDriver):
    tri_page = TriPage(driver)
    tri_page.open()
    tri_page.select_sort_option('Nom')
    products_names = [product.text for product in tri_page.get_product_names()]
    assert all(products_names[i] <= products_names[i + 1] for i in range(len(products_names) - 1)), "Products not sorted by ascending name when names are the same"