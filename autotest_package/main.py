import argparse
import os
import sys
import yaml
import shutil
from typing import List

# Ensure relative imports work by adding script directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logger
from spec_parser import SpecParser
from test_case_generator import TestCaseGenerator
from spec_to_selenium import SeleniumGenerator
from test_runner import TestRunner
from report_generator import ReportGenerator

def main():
    parser = argparse.ArgumentParser(description="AUTOTEST avec spec fonctionnelle")
    parser.add_argument("--spec", required=True, help="Chemin vers la spec fonctionnelle (.txt, .md, .pdf)")
    parser.add_argument("--url", required=True, help="URL du site à tester")
    parser.add_argument("--output-dir", default="./output", help="Dossier de sortie (défaut: ./output)")
    parser.add_argument("--headless", action="store_true", default=True, help="Mode headless (défaut: True)")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="Désactiver le mode headless")
    parser.add_argument("--browser", default="chrome", choices=["chrome", "firefox"], help="chrome | firefox (défaut: chrome)")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout en secondes par test (défaut: 30)")
    parser.add_argument("--loglevel", default="INFO", choices=["DEBUG", "INFO", "WARNING"], help="DEBUG | INFO | WARNING (défaut: INFO)")
    parser.add_argument("--keep-tests", action="store_true", help="Conserver les scripts générés après exécution")
    parser.add_argument("--dry-run", action="store_true", help="Générer les scripts sans les exécuter")
    
    args = parser.parse_args()

    # Setup logger
    logger = setup_logger("Main", log_level=args.loglevel)
    logger.info("Démarrage d'AUTOTEST Spec-Driven Pipeline")

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
    
    try:
        # Create output directories
        output_dir = os.path.abspath(args.output_dir)
        reports_dir = os.path.join(output_dir, "reports")
        generated_tests_dir = os.path.join(output_dir, "generated_tests")
        # clean if needed? Or let it append? For stability, let's start fresh if not dry-run
        # if not args.dry_run and os.path.exists(output_dir):
        #     shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        # STEP 1: Parsage de la spec
        parser_engine = SpecParser(config_path)
        logger.info(f"Étape 1: Lecture de la spec {args.spec}")
        parsed_spec = parser_engine.parse(args.spec)
        # Override URL if provided in CLI
        if args.url:
            parsed_spec['url_cible'] = args.url
        
        # STEP 2: Génération des cas de test
        case_gen = TestCaseGenerator(config_path)
        logger.info("Étape 2: Génération des scénarios de test avec le LLM")
        test_cases = case_gen.generate(parsed_spec)

        # STEP 3: Génération des scripts Selenium
        script_gen = SeleniumGenerator(config_path)
        logger.info("Étape 3: Création des scripts Selenium Python (POM)")
        script_gen.generate_scripts(test_cases, output_dir, url_cible=parsed_spec.get('url_cible'))
        
        if args.dry_run:
            logger.info("Mode --dry-run activé. Arrêt avant l'exécution.")
            sys.exit(0)

        # STEP 4: Exécution des tests
        runner = TestRunner(config_path)
        logger.info("Étape 4: Exécution de pytest")
        test_results = runner.run_tests(
            generated_tests_dir, 
            browser=args.browser, 
            headless=args.headless, 
            timeout_sec=args.timeout * len(test_cases)
        )

        # STEP 5: Génération du rapport
        report_gen = ReportGenerator(config_path)
        logger.info("Étape 5: Création du rapport final")
        report_gen.generate(test_results, parsed_spec, reports_dir)

        logger.info(f"Pipeline terminé avec succès. Rapport disponible dans {reports_dir}")

    except Exception as e:
        logger.error(f"Échec critique du pipeline: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
