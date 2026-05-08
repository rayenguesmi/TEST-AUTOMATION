import os
import json
import yaml
import time
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger("ReportGenerator")

class ReportGenerator:
    """Generates HTML and JSON reports based on execution results."""

    def __init__(self, config_path: str):
        """Initializes generator with templates and config."""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.output_formats = self.config.get('report', {}).get('format', ["html", "json"])
        self.include_screenshots = self.config.get('report', {}).get('include_screenshots', True)

    def generate(self, test_results: Dict[str, Any], parsed_spec: Dict[str, Any], output_reports_dir: str):
        """Generates HTML and JSON reports using template and results."""
        logger.info(f"Generating reports into: {output_reports_dir}")
        os.makedirs(output_reports_dir, exist_ok=True)
        
        # Merge spec information for traceability
        processed_data = self._merge_spec_and_results(test_results, parsed_spec)
        
        # 1. JSON Report
        if "json" in self.output_formats:
            json_report_path = os.path.join(output_reports_dir, "report.json")
            with open(json_report_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2)
        
        # 2. HTML Report
        if "html" in self.output_formats:
            html_report_path = os.path.join(output_reports_dir, "report.html")
            template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template("report_template.html")
            
            html_content = template.render(
                results=test_results,
                spec=parsed_spec,
                summary=processed_data['summary'],
                features=processed_data['features_with_results']
            )
            
            with open(html_report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
        logger.info(f"Report generation completed: {output_reports_dir}")

    def _merge_spec_and_results(self, results: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, Any]:
        """Merges spec's features with test result metrics."""
        summary = {
            "project_name": spec.get('project_name', 'Unknown'),
            "url_cible": spec.get('url_cible', 'Unknown'),
            "total_tests": results.get('total', 0),
            "passed": results.get('passed', 0),
            "failed": results.get('failed', 0),
            "errors": results.get('errors', 0),
            "duration_seconds": round(results.get('duration_seconds', 0), 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Build a lookup: test classname -> test result
        all_tests = results.get('tests', [])

        features_list = []
        features = spec.get('features', [])

        for feat_idx, feature in enumerate(features):
            fid = feature.get('id')           # e.g. 'F-001'
            # Numeric part with and without leading zeros: '001', '1'
            num_padded = fid.replace('F-', '')          # '001'
            num_bare   = num_padded.lstrip('0') or '0'  # '1'

            # 1. Exact match on extracted id (test_runner already normalises to 'F-001')
            feature_tests = [t for t in all_tests if t.get('id') == fid]

            # 2. Classname contains F_001 or F_1 (underscore variants)
            if not feature_tests:
                patterns_f = [f"f_{num_padded}", f"f_{num_bare}",
                              f"_f{num_padded}_",  f"_f{num_bare}_"]
                feature_tests = [
                    t for t in all_tests
                    if any(p in t.get('classname', '').lower() or
                           p in t.get('name', '').lower()
                           for p in patterns_f)
                ]

            # 3. Classname contains CT_NNN where NNN maps positionally to feature index
            #    e.g. first feature (idx=0) → CT_001, second (idx=1) → CT_002 …
            if not feature_tests:
                ct_tag = f"ct_{str(feat_idx + 1).zfill(3)}"
                feature_tests = [
                    t for t in all_tests
                    if ct_tag in t.get('classname', '').lower()
                ]

            if not feature_tests:
                status = "UNKNOWN"
            elif all(t['statut'] == "PASS" for t in feature_tests):
                status = "PASS"
            elif any(t['statut'] == "PASS" for t in feature_tests):
                status = "PARTIAL"
            else:
                status = "FAIL"

            features_list.append({
                "id": fid,
                "title": feature.get('titre'),
                "description": feature.get('description'),
                "status": status,
                "tests": feature_tests
            })

        return {
            "summary": summary,
            "features_with_results": features_list
        }
