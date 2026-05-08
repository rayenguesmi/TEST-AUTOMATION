"""
dom_scanner.py
==============
Visits the target URL (+ relevant sub-pages found in navigation) with
Selenium and extracts real CSS selectors.  The combined context is
injected into the Selenium-generation prompt so the LLM uses verified
selectors and navigates to the correct pages.
"""

import time
from typing import List, Optional
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from utils.logger import setup_logger

logger = setup_logger("DOMScanner")

_MAX = 15  # max elements per category


class DOMScanner:
    """
    Scans one or more live pages and returns a structured DOM-context
    string.  Always scans the root URL; also scans navigation sub-pages
    whose link text/href matches keywords derived from the spec features.
    """

    def __init__(self, headless: bool = True, timeout: int = 15):
        self.headless = headless
        self.timeout = timeout

    # ── Public ───────────────────────────────────────────────────────────────

    def scan(self, url: str) -> str:
        """Simple single-page scan (kept for backward compat)."""
        return self.scan_with_navigation(url, keywords=None)

    def scan_with_navigation(self, url: str, keywords: Optional[List[str]] = None) -> str:
        """
        Scan *url* + up to 2 sub-pages.
        Sub-pages are found either by keyword matching against nav links, or
        automatically when the main page has no product listings (category overview).
        Returns the combined DOM context string.
        """
        driver = self._create_driver()
        contexts: List[str] = []

        try:
            # ── Main page ──────────────────────────────────────────────────
            main_ctx = self._scan_page(driver, url)
            contexts.append(main_ctx)

            # ── Find sub-pages ─────────────────────────────────────────────
            sub_urls: List[str] = []
            if keywords:
                sub_urls = self._find_matching_nav_urls(driver, keywords, base=url)

            # Fallback: if the main page has no product listing (category overview
            # page like /electronics that shows sub-category tiles only), find a
            # sub-page that has real product items.
            # In that case, REPLACE keyword-matched URLs with actual product sub-pages
            # so we don't waste scans on /cart, /checkout, etc.
            main_has_products = "Container :" in main_ctx
            if not main_has_products:
                logger.info(
                    f"[DOMScanner] No products on '{url}' — looking for product sub-pages"
                )
                product_sub_pages = self._find_product_subpages(driver, base=url)
                if product_sub_pages:
                    # Product sub-pages take full priority — discard keyword matches
                    sub_urls = product_sub_pages
                    logger.info(
                        f"[DOMScanner] Using product sub-pages instead of keyword matches: {sub_urls}"
                    )
                else:
                    # Keep keyword matches as last resort but skip obvious non-product URLs
                    _non_product = {"cart", "checkout", "login", "register", "wishlist",
                                    "compare", "contact", "account", "search", "blog"}
                    sub_urls = [
                        u for u in sub_urls
                        if not any(s in urlparse(u).path.lower() for s in _non_product)
                    ]

            for sub_url in sub_urls[:2]:
                try:
                    sub_ctx = self._scan_page(driver, sub_url)
                    contexts.append(sub_ctx)
                except Exception as exc:
                    logger.warning(f"[DOMScanner] Sub-page {sub_url} failed: {exc}")

        except (TimeoutException, WebDriverException, Exception) as exc:
            logger.error(f"[DOMScanner] Scan failed for {url}: {exc}")
            return ""
        finally:
            try:
                driver.quit()
            except Exception:
                pass

        sep = "\n\n" + "═" * 60 + "\n\n"
        return sep.join(contexts)

    # ── Driver ────────────────────────────────────────────────────────────────

    def _create_driver(self) -> webdriver.Chrome:
        opts = Options()
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        if self.headless:
            opts.add_argument("--headless=new")
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=opts,
        )

    # ── Sub-page discovery ────────────────────────────────────────────────────

    def _find_matching_nav_urls(
        self, driver, keywords: List[str], base: str
    ) -> List[str]:
        """
        Return hrefs of navigation links whose text or path segment matches
        any keyword word (≥4 chars, case-insensitive).
        """
        kw_words = set()
        for kw in keywords:
            for word in kw.lower().split():
                if len(word) >= 4:
                    kw_words.add(word)

        base_host = urlparse(base).netloc
        matched, seen = [], set()

        for el in driver.find_elements(
            By.CSS_SELECTOR,
            "nav a, .top-menu a, .header-links a, ul li a, .header a"
        ):
            href = (el.get_attribute("href") or "").strip()
            text = el.text.strip().lower()
            if not href or href in seen:
                continue
            # Stay on the same domain
            parsed = urlparse(href)
            if parsed.netloc and parsed.netloc != base_host:
                continue
            # Match any keyword word against link text or path
            path_lower = parsed.path.lower()
            for word in kw_words:
                if word in text or word in path_lower:
                    matched.append(href)
                    seen.add(href)
                    logger.info(f"[DOMScanner] Matched sub-page '{href}' via keyword '{word}'")
                    break

        return matched

    def _find_product_subpages(self, driver, base: str, max_count: int = 2) -> List[str]:
        """
        Find internal sub-pages that are likely to contain product listings.
        Used as fallback when the current page is a category overview (no products).
        Tries NopCommerce/Magento/WooCommerce category link selectors first,
        then falls back to generic internal links.
        """
        base_host = urlparse(base).netloc
        base_path = urlparse(base).path.rstrip("/")

        _skip = {
            "login", "register", "cart", "checkout", "wishlist", "compare",
            "contact", "about", "account", "privacy", "sitemap", "search",
            "blog", "news", "faq", "help", "javascript", "mailto",
        }
        matched, seen = [], set()

        # Priority 1 — category/sub-category blocks (NopCommerce, Magento, WC)
        priority_css = (
            ".sub-category-item a, .category-item a, "
            ".item-box a[href], .category-grid a[href], "
            "[class*='sub-categ'] a, .sub-categories a, "
            ".categories a, .category-box a"
        )
        # Priority 2 — any visible internal link with text
        fallback_css = "a[href]"

        def _collect(css: str):
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, css)
            except Exception:
                return
            for el in elements:
                href = (el.get_attribute("href") or "").strip()
                text = el.text.strip()
                if not href or href in seen:
                    continue
                parsed = urlparse(href)
                if parsed.netloc and parsed.netloc != base_host:
                    continue
                href_path = parsed.path.rstrip("/")
                if href_path in (base_path, "", "/"):
                    continue
                if any(s in href_path.lower() for s in _skip):
                    continue
                seen.add(href)
                matched.append(href)
                logger.info(
                    f"[DOMScanner] Sub-page candidate: {href}  ('{text[:40]}')"
                )
                if len(matched) >= max_count:
                    return

        _collect(priority_css)
        if len(matched) < max_count:
            _collect(fallback_css)

        return matched[:max_count]

    # ── Single-page scan ──────────────────────────────────────────────────────

    def _scan_page(self, driver, url: str) -> str:
        logger.info(f"[DOMScanner] Scanning → {url}")
        driver.get(url)
        WebDriverWait(driver, self.timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(1.5)

        parts: List[str] = [
            "╔══ DOM SNAPSHOT ══════════════════════════════════════════════",
            f"║  URL   : {url}",
            f"║  Title : {driver.title}",
            "╚══════════════════════════════════════════════════════════════",
            f"  ► Pour accéder aux éléments ci-dessous, naviguer vers : {url}",
        ]

        def _add(title: str, body: str):
            if body.strip():
                parts.append(f"\n▶ {title}\n{body}")

        _add("SEARCH BAR",       self._extract_search(driver))
        _add("DROPDOWNS/SORT",   self._extract_selects(driver))
        _add("FORM INPUTS",      self._extract_inputs(driver))
        _add("BUTTONS & CTAs",   self._extract_buttons(driver))
        _add("CART ELEMENTS",    self._extract_cart(driver))
        _add("PRODUCT LISTING",  self._extract_products(driver))
        _add("PAGINATION",       self._extract_pagination(driver))
        _add("NAVIGATION",       self._extract_navigation(driver))
        _add("PAGE HEADINGS",    self._extract_headings(driver))

        result = "\n".join(parts)
        logger.info(f"[DOMScanner] Page done — {len(result)} chars")
        return result

    # ── Selector helper ───────────────────────────────────────────────────────

    @staticmethod
    def _best_css(el) -> str:
        eid = (el.get_attribute("id") or "").strip()
        if eid:
            return f"#{eid}"
        for attr in ("data-testid", "data-test", "data-cy"):
            val = (el.get_attribute(attr) or "").strip()
            if val:
                return f"[{attr}='{val}']"
        name = (el.get_attribute("name") or "").strip()
        tag = el.tag_name
        if name:
            return f"{tag}[name='{name}']"
        if tag == "input":
            itype = (el.get_attribute("type") or "text").lower()
            value = (el.get_attribute("value") or "").strip()
            if itype in ("submit", "button") and value:
                return f"input[value='{value}']"
        classes = [
            c for c in (el.get_attribute("class") or "").split()
            if len(c) > 2 and not c.startswith(("js-", "is-", "has-"))
        ]
        if classes:
            return f"{tag}.{classes[0]}"
        return tag

    # ── Extractors ────────────────────────────────────────────────────────────

    def _extract_search(self, driver) -> str:
        css = (
            "input[type='search'], input[id*='search'], input[name*='search'], "
            "input[placeholder*='earch']"
        )
        lines, seen = [], set()
        for el in driver.find_elements(By.CSS_SELECTOR, css)[:5]:
            s = self._best_css(el)
            if s in seen:
                continue
            seen.add(s)
            ph = el.get_attribute("placeholder") or ""
            lines.append(f"  {s}  placeholder='{ph}'")
        return "\n".join(lines)

    def _extract_selects(self, driver) -> str:
        lines = []
        for el in driver.find_elements(By.TAG_NAME, "select")[:8]:
            s = self._best_css(el)
            opts = [
                o.text.strip()
                for o in el.find_elements(By.TAG_NAME, "option")[:10]
                if o.text.strip()
            ]
            lines.append(f"  {s}  options={opts}")
        return "\n".join(lines)

    def _extract_inputs(self, driver) -> str:
        _skip = ("hidden", "submit", "button", "image", "checkbox", "radio")
        lines, seen = [], set()
        for el in driver.find_elements(By.TAG_NAME, "input")[:_MAX]:
            t = (el.get_attribute("type") or "text").lower()
            if t in _skip:
                continue
            s = self._best_css(el)
            if s in seen:
                continue
            seen.add(s)
            ph = el.get_attribute("placeholder") or ""
            lines.append(f"  {s}  type='{t}'  placeholder='{ph}'")
        return "\n".join(lines)

    def _extract_buttons(self, driver) -> str:
        lines, seen = [], set()
        for el in driver.find_elements(
            By.CSS_SELECTOR,
            "button, input[type='submit'], input[type='button']"
        )[:_MAX]:
            s = self._best_css(el)
            if s in seen:
                continue
            seen.add(s)
            text = (el.text.strip() or el.get_attribute("value") or "")[:50]
            if text:
                lines.append(f"  {s}  text='{text}'")
        return "\n".join(lines)

    def _extract_cart(self, driver) -> str:
        lines, seen = [], set()
        for el in driver.find_elements(
            By.CSS_SELECTOR, "[id*='cart'], [class*='cart'], a[href*='cart']"
        )[:10]:
            s = self._best_css(el)
            if s in seen:
                continue
            seen.add(s)
            text = (el.text.strip() or "")[:50]
            lines.append(f"  {s}  text='{text}'")
            # Explicit note about cart counter format
            if "qty" in s.lower() or "qty" in (el.get_attribute("class") or "").lower():
                lines.append(
                    f"    NOTE: ce compteur affiche le format '(N)' ex: '(0)', '(1)'. "
                    f"Pour vérifier 1 article : assert '(1)' in element.text"
                )
        return "\n".join(lines)

    def _extract_products(self, driver) -> str:
        lines = []
        containers = [
            ".product-item", "[class*='product-item']",
            ".item.product", ".products-wrapper li",
            ".product-grid .item",
        ]
        for csel in containers:
            items = driver.find_elements(By.CSS_SELECTOR, csel)
            if len(items) < 2:
                continue
            lines.append(f"  Container : {csel}  (×{len(items)} items)")
            first = items[0]
            checks = [
                (".product-title a, h2 a, h3 a, .name a, [class*='title'] a", "Title link"),
                (".price, .actual-price, [class*='price']",                    "Price"),
                ("input[value*='art'], input[value*='Art'], .add-to-cart-button", "Add-to-cart"),
                (".picture a, .product-image-box a",                           "Image link"),
            ]
            for sel, label in checks:
                found = first.find_elements(By.CSS_SELECTOR, sel)
                if found:
                    real = self._best_css(found[0])
                    txt = (found[0].text.strip() or found[0].get_attribute("value") or "")[:40]
                    lines.append(f"    {label:16s} : {real}  text='{txt}'")
            break
        return "\n".join(lines)

    def _extract_pagination(self, driver) -> str:
        lines, seen = [], set()
        css = (
            ".next-page, .previous-page, [class*='next-page'], [class*='prev-page'], "
            ".pager a, .pagination a, li.next > a, li.prev > a, a[rel='next']"
        )
        for el in driver.find_elements(By.CSS_SELECTOR, css)[:8]:
            s = self._best_css(el)
            if s in seen:
                continue
            seen.add(s)
            text = (el.text.strip() or el.get_attribute("aria-label") or "")[:30]
            lines.append(f"  {s}  text='{text}'")
        for el in driver.find_elements(
            By.CSS_SELECTOR, ".current-page, [class*='current-page']"
        )[:2]:
            lines.append(
                f"  current-page : {self._best_css(el)}  text='{el.text.strip()}'"
            )
        return "\n".join(lines)

    def _extract_navigation(self, driver) -> str:
        lines, seen = [], set()
        # Note header: CSS a[href='https://...'] will NOT match relative hrefs in HTML source.
        # Always use PARTIAL_LINK_TEXT or XPath contains(text()) for nav links.
        lines.append(
            "  IMPORTANT: pour cliquer un lien de navigation, utilise TOUJOURS\n"
            "  By.PARTIAL_LINK_TEXT ou By.XPATH avec contains(text()) — JAMAIS\n"
            "  By.CSS_SELECTOR avec href absolu (ne matche pas les hrefs relatifs HTML)."
        )
        for el in driver.find_elements(
            By.CSS_SELECTOR, "nav a, .top-menu a, .header-links a, .header a"
        )[:15]:
            href = (el.get_attribute("href") or "").strip()
            text = el.text.strip()
            if not text or not href or href in seen:
                continue
            seen.add(href)
            lines.append(
                f"  text='{text}'  href='{href}'\n"
                f"    → By.PARTIAL_LINK_TEXT, '{text}'\n"
                f"    → By.XPATH, \"//a[contains(text(), '{text}')]\""
            )
        return "\n".join(lines)

    def _extract_headings(self, driver) -> str:
        lines = []
        for tag in ("h1", "h2"):
            for el in driver.find_elements(By.TAG_NAME, tag)[:3]:
                text = el.text.strip()
                if text:
                    lines.append(f"  <{tag}> {self._best_css(el)}  '{text[:60]}'")
        return "\n".join(lines)
