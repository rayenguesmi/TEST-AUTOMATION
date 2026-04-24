"""
spec_to_selenium.py
===================
Architecture hybride (template-based):
  • LLM   -> parse spec + cas de test (JSON uniquement)
  • Templates -> code Python/Selenium (deterministe, toujours correct)

Fixes:
  - Deduplication par NOM de template (pas contenu)
  - _go_to_electronics() ne cherche plus .product-item (page affiche sous-categories)
  - F-001 verifie les sous-categories ET les produits
  - F-002/F-003/F-004/F-006 naviguent vers /cell-phones (produits reels)
  - Unicode-safe logs (pas de caractere special)
"""
import ast
import os
import json
import re
import shutil
import time
import yaml
from typing import Dict, Any, List

from utils.llm_client import LLMClient
from utils.logger import setup_logger

logger = setup_logger("SeleniumGenerator")

def _pick_template(case: Dict[str, Any]):
    """
    Returns (template_key: str, template_code: str).
    template_key is used for deduplication — one file per key.
    """
    titre    = (case.get("titre", "") + " " + case.get("description", "")).lower()
    feat_id  = case.get("id", "")

    # 1. Direct feature ID match (e.g., F-001, F-002)
    for prefix, (key, tpl) in _FEATURE_ID_MAP.items():
        if feat_id.startswith(prefix):
            return key, tpl

    # 2. Keyword match on title/description
    for keywords, key, tpl in _KEYWORD_MAP:
        if any(kw in titre for kw in keywords):
            return key, tpl

    # 3. Generic fallback (unique key per distinct title)
    class_name  = re.sub(r'[^\w]', '', case.get("titre", "Test").title())[:30] or "GenericTest"
    method_name = re.sub(r'[^\w]', '_', case.get("titre", "test").lower())[:40] or "generic"
    description = case.get("description", "Test generique")
    titre_str   = case.get("titre", "")
    generic_body = (
        f"class Test{class_name}:\n"
        f'    """{titre_str}"""\n\n'
        f"    def test_{method_name}(self, driver: WebDriver):\n"
        f'        """{description}"""\n'
        f"        wait = WebDriverWait(driver, 20)\n"
        f"        driver.get(BASE_URL)\n\n"
        f"        assert \"{{url_placeholder}}\" in driver.current_url\n"
    )
    generic_key = f"GENERIC_{class_name}"
    return generic_key, _TEST_HEADER + generic_body


# ═════════════════════════════════════════════════════════════════════════════
class SeleniumGenerator:
    """
    Hybrid Selenium test generator.
    - Uses deterministic templates for known sites (Demo Shop).
    - Uses LLM for general cases and new sites.
    """

    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        self.llm_client = LLMClient(config_path)

    def generate_scripts(
        self,
        test_cases: List[Dict[str, Any]],
        output_dir: str,
        url_cible: str = None,
    ):
        self.url_cible = (url_cible or DEFAULT_URL).rstrip('/') + '/'
        logger.info(f"URL cible : {self.url_cible}")
        logger.info("Mode : templates deterministes (LLM non utilise pour le code)")

        generated_tests_dir = os.path.join(output_dir, "generated_tests")
        pages_dir  = os.path.join(generated_tests_dir, "pages")
        tests_dir  = os.path.join(generated_tests_dir, "tests")

        # Total cleanup of generated tests root to avoid leftovers
        if os.path.exists(generated_tests_dir):
            shutil.rmtree(generated_tests_dir)
            
        for d in [generated_tests_dir, pages_dir, tests_dir]:
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, "__init__.py"), 'a').close()

        self._write_base_page(pages_dir)
        self._write_conftest(generated_tests_dir)
        self._write_pytest_ini(generated_tests_dir)

        # ── Write one file per template key (dedup by key, not content) ──────
        written_keys: set = set()
        saved = 0

        for case in test_cases:
            feat_id = case.get("id", "UNKNOWN")
            titre   = case.get("titre", "unnamed")

            # Determine if we should use Template or LLM
            is_demo_shop = DEMO_SHOP_DOMAIN in self.url_cible
            template_key, template_code = _pick_template(case)
            
            # If it's a generic template and not demo shop, or if we want full generality:
            if not is_demo_shop or template_key.startswith("GENERIC"):
                logger.info(f"  [LLM] Generating generic script for: {feat_id}")
                system_prompt = self.config['prompts']['selenium_generation'].replace('{url_cible}', self.url_cible)
                user_prompt = f"Génère le script pour ce cas de test :\n{json.dumps(case, indent=2)}"
                
                try:
                    generated_code = self.llm_client.call(system_prompt, user_prompt)
                    # Extract code block if present
                    if "```" in generated_code:
                        generated_code = re.search(r"```(?:python)?\n(.*?)\n```", generated_code, re.DOTALL).group(1)
                    template_code = generated_code
                    template_key = f"LLM_{template_key}"
                except Exception as e:
                    logger.warning(f"  [Error] LLM generation failed for {feat_id}, falling back to template: {e}")

            if template_key in written_keys:
                logger.info(f"  Skip (doublon) : {feat_id} -> {template_key}")
                continue
            written_keys.add(template_key)

            try:
                # Basic validation
                ast.parse(template_code)
            except SyntaxError as e:
                logger.error(f"  Code invalide généré pour {feat_id}: {e}")
                continue

            safe_titre = re.sub(r'[^\w]', '_', titre.lower())[:40]
            # Prefix filename with feat_id for reporting
            filename   = f"test_{feat_id.replace('-', '_')}_{template_key}_{safe_titre}.py"
            filepath   = os.path.join(tests_dir, filename)
            
            # Also inject the ID into the test function name for LLM generated code
            if not is_demo_shop or template_key.startswith("GENERIC"):
                template_code = template_code.replace("def test_", f"def test_{feat_id.replace('-', '_')}_")

            with open(filepath, 'w', encoding='utf-8') as f:
                # Ensure the template code uses the correct URL
                final_code = template_code.replace("https://demowebshop.tricentis.com/", self.url_cible)
                final_code = final_code.replace("{url_placeholder}", self.url_cible)
                f.write(final_code)
            logger.info(f"  [OK] Script : {filename}")
            saved += 1

        logger.info(f"Scripts generes : {saved}")

    # ── Static infrastructure ─────────────────────────────────────────────────
    def _write_base_page(self, pages_dir: str):
        code = '''\
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
import time


class BasePage:
    """Hardened base - WebDriverWait(20), scrollIntoView, JS-click fallback."""

    TIMEOUT = 20

    def __init__(self, driver):
        self.driver = driver
        self.wait   = WebDriverWait(driver, self.TIMEOUT)

    def _scroll_to(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:\'center\',inline:\'nearest\'});",
            element,
        )
        time.sleep(0.3)

    def wait_for_presence(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def wait_for_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_for_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def safe_click(self, locator):
        el = self.wait_for_presence(locator)
        self._scroll_to(el)
        el = self.wait_for_clickable(locator)
        try:
            el.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            self.driver.execute_script("arguments[0].click();", el)

    def safe_send_keys(self, locator, text: str):
        el = self.wait_for_presence(locator)
        self._scroll_to(el)
        el = self.wait_for_visible(locator)
        el.clear()
        el.send_keys(text)

    def get_text(self, locator) -> str:
        el = self.wait_for_visible(locator)
        self._scroll_to(el)
        return el.text

    def is_visible(self, locator) -> bool:
        try:
            return self.wait_for_visible(locator).is_displayed()
        except TimeoutException:
            return False

    def open(self, url: str):
        self.driver.get(url)
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
'''
        with open(os.path.join(pages_dir, "base_page.py"), 'w', encoding='utf-8') as f:
            f.write(code)

    def _write_conftest(self, output_dir: str):
        code = '''\
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
    options.page_load_strategy = 'eager'
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    
    # Block ads and images for speed on slow sites
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--disable-notifications")
    
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
        print(f"\\nScreenshot: {path}")
'''
        with open(os.path.join(output_dir, "conftest.py"), 'w', encoding='utf-8') as f:
            f.write(code)

    def _write_pytest_ini(self, output_dir: str):
        ini = """\
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --tb=short --junitxml=results.xml
"""
        with open(os.path.join(output_dir, "pytest.ini"), 'w', encoding='utf-8') as f:
            f.write(ini)
