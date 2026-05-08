from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import re
import uuid
import sys
import requests as http_requests
from typing import Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logger
from spec_parser import SpecParser
from test_case_generator import TestCaseGenerator
from spec_to_selenium import SeleniumGenerator
from test_runner import TestRunner
from report_generator import ReportGenerator
from dom_scanner import DOMScanner

app = FastAPI(title="AUTOTEST API Engine")
logger = setup_logger("API", log_level="INFO")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated reports as static files
_pkg_dir = os.path.dirname(os.path.abspath(__file__))
_autotest_output_dir = os.path.join(os.path.dirname(_pkg_dir), "autotest_output")
os.makedirs(_autotest_output_dir, exist_ok=True)
app.mount("/autotest-output", StaticFiles(directory=_autotest_output_dir), name="autotest-output")

# In-memory task registry
tasks = {}


# ─── Request models ───────────────────────────────────────────────────────────

class TestRequest(BaseModel):
    spec_content: str
    url: str
    api_key: Optional[str] = None
    provider: Optional[str] = "groq"
    browser: Optional[str] = "chrome"
    headless: Optional[bool] = True


class GenerateRequest(BaseModel):
    url: str
    specs: str
    callback_url: Optional[str] = None
    test_id: Optional[str] = None
    provider: Optional[str] = "groq"
    api_key: Optional[str] = None
    headless: Optional[bool] = True


# ─── Existing full pipeline (run-test) ───────────────────────────────────────

def run_test_pipeline(task_id: str, request: TestRequest):
    try:
        tasks[task_id] = {"status": "running", "progress": "Starting"}

        _pkg_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(_pkg_dir, "config.yaml")
        # Place output OUTSIDE autotest_package/ so uvicorn --reload never sees generated files
        output_dir = os.path.join(os.path.dirname(_pkg_dir), "autotest_output", task_id)
        os.makedirs(output_dir, exist_ok=True)

        if request.api_key:
            os.environ[f"{request.provider.upper()}_API_KEY"] = request.api_key

        spec_path = os.path.join(output_dir, "spec.md")
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(request.spec_content)

        _provider = getattr(request, 'provider', None) or 'groq'
        _api_key  = getattr(request, 'api_key', None) or None

        tasks[task_id]["progress"] = "Parsing Specification"
        parser_engine = SpecParser(config_path, provider=_provider, api_key=_api_key)
        parsed_spec = parser_engine.parse(spec_path)
        parsed_spec["url_cible"] = request.url

        tasks[task_id]["progress"] = "Generating Test Cases"
        case_gen = TestCaseGenerator(config_path, provider=_provider, api_key=_api_key)
        test_cases = case_gen.generate(parsed_spec)

        tasks[task_id]["progress"] = "Generating Selenium Scripts"
        script_gen = SeleniumGenerator(config_path, provider=_provider, api_key=_api_key)
        script_gen.generate_scripts(test_cases, output_dir, url_cible=request.url)

        tasks[task_id]["progress"] = "Running Tests"
        runner = TestRunner(config_path)
        generated_tests_dir = os.path.join(output_dir, "generated_tests")
        test_results = runner.run_tests(
            generated_tests_dir,
            browser=request.browser,
            headless=request.headless,
            timeout_sec=30 * len(test_cases),
        )

        tasks[task_id]["progress"] = "Generating Report"
        report_gen = ReportGenerator(config_path)
        reports_dir = os.path.join(output_dir, "reports")
        report_gen.generate(test_results, parsed_spec, reports_dir)

        tasks[task_id] = {
            "status": "completed",
            "progress": "Finished",
            "report_path": f"/reports/{task_id}/report.html",
            "results": test_results,
        }
        logger.info(f"Task {task_id} completed successfully")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        tasks[task_id] = {"status": "failed", "error": str(e)}


# ─── Generation-only pipeline (generate) ─────────────────────────────────────

def run_generate_pipeline(task_id: str, request: GenerateRequest):
    """Parses specs → generates test cases → generates Selenium scripts.
    Skips test execution. Posts results to callback_url when done."""
    try:
        tasks[task_id] = {"status": "running", "progress": "Démarrage", "step": 0}

        # Inject user-supplied API key before any LLM call
        key_received = bool(request.api_key and len(request.api_key.strip()) > 5)
        logger.info(f"[{task_id}] provider={request.provider} api_key_received={key_received} key_preview={repr(request.api_key[:8]) if request.api_key else 'None'}")
        if request.api_key and request.api_key.strip():
            os.environ[f"{request.provider.upper()}_API_KEY"] = request.api_key.strip()

        _pkg_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(_pkg_dir, "config.yaml")
        # Place output OUTSIDE autotest_package/ so uvicorn --reload never sees generated files
        output_dir = os.path.join(os.path.dirname(_pkg_dir), "autotest_output", task_id)
        os.makedirs(output_dir, exist_ok=True)

        # Save Markdown specs to temp file
        spec_path = os.path.join(output_dir, "spec.md")
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(request.specs)

        _provider = request.provider or 'groq'
        _api_key  = request.api_key or None

        # STEP 1 — Parse spec via LLM
        tasks[task_id].update({"progress": "Analyse des specs", "step": 1})
        logger.info(f"[{task_id}] Parsing specification for {request.url}")
        parser = SpecParser(config_path, provider=_provider, api_key=_api_key)
        parsed_spec = parser.parse(spec_path)
        parsed_spec["url_cible"] = request.url

        # STEP 2 — Generate test cases via LLM
        tasks[task_id].update({"progress": "Consultation de Groq (génération des cas de test)", "step": 2})
        logger.info(f"[{task_id}] Generating test cases")
        case_gen = TestCaseGenerator(config_path, provider=_provider, api_key=_api_key)
        test_cases = case_gen.generate(parsed_spec)

        # STEP 3 — Scan the live DOM (main page + relevant sub-pages)
        tasks[task_id].update({"progress": "Scan du DOM réel", "step": 3})
        logger.info(f"[{task_id}] Scanning DOM of {request.url}")
        try:
            # Extract keywords from spec features so the scanner follows relevant nav links
            keywords = [parsed_spec.get("project_name", "")]
            for feat in parsed_spec.get("features", []):
                keywords.append(feat.get("titre", ""))
                keywords.append(feat.get("description", ""))
            keywords = [k for k in keywords if k]

            scanner = DOMScanner(headless=True)
            dom_context = scanner.scan_with_navigation(request.url, keywords=keywords)
        except Exception as scan_err:
            logger.warning(f"[{task_id}] DOM scan failed (non-blocking): {scan_err}")
            dom_context = ""

        # Extract the most specific sub-page URL found during DOM scan to use as url_cible.
        # This overrides the root URL so the LLM navigates to the correct page.
        effective_url = request.url
        if dom_context:
            urls_in_ctx = re.findall(r'║  URL\s*:\s*(.+)', dom_context)
            root_clean = request.url.rstrip('/')
            for found_url in urls_in_ctx:
                found_url = found_url.strip()
                if found_url.rstrip('/') != root_clean:
                    effective_url = found_url
                    logger.info(f"[{task_id}] URL effective pour génération Selenium: {found_url}")
                    break

        # STEP 4 — Generate Selenium scripts WITH real DOM selectors
        tasks[task_id].update({"progress": "Génération du script Selenium", "step": 4})
        logger.info(f"[{task_id}] Generating Selenium scripts ({len(test_cases)} cases)")
        script_gen = SeleniumGenerator(config_path, provider=_provider, api_key=_api_key)
        script_gen.generate_scripts(
            test_cases, output_dir,
            url_cible=effective_url,
            dom_context=dom_context,
            original_url=request.url,
        )

        # Collect generated .py files
        scripts: dict[str, str] = {}
        tests_dir = os.path.join(output_dir, "generated_tests", "tests")
        if os.path.exists(tests_dir):
            for fname in sorted(os.listdir(tests_dir)):
                if fname.endswith(".py"):
                    with open(os.path.join(tests_dir, fname), "r", encoding="utf-8") as fp:
                        scripts[fname] = fp.read()

        combined_script = (
            ("\n\n# " + "─" * 60 + "\n\n").join(
                f"# {name}\n\n{content}" for name, content in scripts.items()
            )
            if scripts
            else "# Aucun script généré"
        )

        # STEP 5 — Execute the generated tests with Selenium / pytest
        tasks[task_id].update({"progress": "Exécution des tests Selenium", "step": 5})
        logger.info(f"[{task_id}] Running {len(scripts)} test file(s)")
        runner = TestRunner(config_path)
        generated_tests_dir = os.path.join(output_dir, "generated_tests")
        # Each test function can wait up to 20 s × multiple waits = ~60 s/case minimum.
        # With 24 test cases → 24 × 120 = 2880 s (48 min) — generous but safe.
        test_results = runner.run_tests(
            generated_tests_dir,
            browser="chrome",
            headless=request.headless,
            timeout_sec=max(600, 120 * len(test_cases)),
        )

        # STEP 6 — Generate HTML + JSON report
        tasks[task_id].update({"progress": "Génération du rapport", "step": 6})
        logger.info(f"[{task_id}] Generating report")
        report_gen = ReportGenerator(config_path)
        reports_dir = os.path.join(output_dir, "reports")
        report_gen.generate(test_results, parsed_spec, reports_dir)

        tasks[task_id] = {
            "status": "completed",
            "progress": "Terminé",
            "step": 7,
            "script": combined_script,
            "test_cases_count": len(test_cases),
            "files_count": len(scripts),
            "test_results": test_results,
        }
        logger.info(
            f"[{task_id}] Completed — {len(scripts)} file(s) | "
            f"{test_results.get('passed', 0)} passed / {test_results.get('failed', 0)} failed"
        )

        # Notify Node.js
        if request.callback_url:
            fastapi_base = os.environ.get("FASTAPI_URL", "http://localhost:8000")
            report_html_url = f"{fastapi_base}/autotest-output/{task_id}/reports/report.html"
            _post_callback(request.callback_url, {
                "testId": request.test_id,
                "status": "completed",
                "script": combined_script,
                "report": test_results,
                "reportHtmlUrl": report_html_url,
                "logs": [
                    f"Parsed {len(parsed_spec.get('features', []))} feature(s)",
                    f"Generated {len(test_cases)} test case(s)",
                    f"Generated {len(scripts)} Selenium script file(s)",
                    f"Executed: {test_results.get('passed', 0)} passed, "
                    f"{test_results.get('failed', 0)} failed in "
                    f"{test_results.get('duration_seconds', 0):.1f}s",
                ],
            })

    except Exception as e:
        logger.error(f"[{task_id}] Generation failed: {e}")
        tasks[task_id] = {"status": "failed", "progress": "Erreur", "step": -1, "error": str(e)}
        if request.callback_url:
            _post_callback(request.callback_url, {
                "testId": request.test_id,
                "status": "failed",
                "error": str(e),
            })


def _post_callback(url: str, payload: dict):
    try:
        resp = http_requests.post(url, json=payload, timeout=10)
        logger.info(f"Callback to {url} → HTTP {resp.status_code}")
    except Exception as e:
        logger.warning(f"Callback to {url} failed: {e}")


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/run-test")
async def start_test(request: TestRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "pending", "progress": "Queued"}
    background_tasks.add_task(run_test_pipeline, task_id, request)
    return {"task_id": task_id, "status": "started"}


@app.post("/generate")
async def generate(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Script-generation-only endpoint called by the Node.js orchestrator."""
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "running", "progress": "En attente", "step": 0}
    background_tasks.add_task(run_generate_pipeline, task_id, request)
    return {"task_id": task_id, "status": "started"}


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
