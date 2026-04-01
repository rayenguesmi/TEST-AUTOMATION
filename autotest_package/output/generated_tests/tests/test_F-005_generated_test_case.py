import pytest
from pages.pagination_page import PaginationPage
from selenium.webdriver.remote.webdriver import WebDriver

@pytest.fixture
def driver():
    return WebDriver()

class TestPagination:
    @pytest.mark.parametrize("test_id, test_name", [
        ("F-005_0", "Flux positif: Pagination fonctionnelle"),
        ("F-005_1", "Flux négatif: Accès à une page inexistante")
    ])
    def test_pagination(self, driver, test_id, test_name):
        pagination_page = PaginationPage(driver)
        driver.get("https://demowebshop.tricentis.com/electronics")

        if test_name == "Flux positif: Pagination fonctionnelle":
            pagination_page.next_button.click()
            assert pagination_page.is_next_button_enabled(), f"Expected next button to be enabled, but it's not. {test_id}_failure.png"
        else:
            pagination_page.next_button.click()
            driver.implicitly_wait(1)
            try:
                pagination_page.next_button.click()
            except Exception as e:
                pytest.fail(f"{e}. {test_id}_failure.png")
            finally:
                driver.quit()

        if test_name == "Flux positif: Pagination fonctionnelle":
            assert True, f"Expected the next page to be displayed with expected products. {test_id}_failure.png"
        else:
            assert False, f"Expected an error message or redirect to homepage. {test_id}_failure.png"

    def teardown_method(self):
        if not hasattr(self, "_outcome"):  # added this line
            return

        test_result = self._outcome.exitstatus
        if test_result == 0:  # added this condition
            pytest.fail(f"Test failed. {self._testMethodName}_failure.png")