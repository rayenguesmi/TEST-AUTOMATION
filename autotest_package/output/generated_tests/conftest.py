import pytest
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages"))


def pytest_addoption(parser):
    parser.addoption("--browser",  action="store", default="chrome")
    parser.addoption("--headless", action="store", default="true")


@pytest.fixture(scope="session")
def browser_name(request):
    return request.config.getoption("--browser")


@pytest.fixture(scope="session")
def headless(request):
    return request.config.getoption("--headless")


@pytest.fixture
def driver(browser_name, headless):
    """Chrome - 1920x1080 - explicit waits only."""
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    if headless == "true":
        options.add_argument("--headless=new")

    drv = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    drv.set_page_load_timeout(30)
    drv.implicitly_wait(0)
    yield drv
    drv.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, driver):
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        parts   = request.node.name.split("_")
        test_id = parts[1] if len(parts) > 1 else "unknown"
        ss_dir  = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "screenshots"
        )
        os.makedirs(ss_dir, exist_ok=True)
        path = os.path.join(ss_dir, f"{test_id}_failure.png")
        driver.save_screenshot(path)
        print(f"\nScreenshot: {path}")
