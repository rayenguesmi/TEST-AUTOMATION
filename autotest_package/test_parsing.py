import os
import sys
import yaml
from spec_parser import SpecParser
from utils.logger import setup_logger

logger = setup_logger("TestLogger", log_level="DEBUG")
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")

parser = SpecParser(config_path)
print("Parsing electronics_spec.md...")
try:
    data = parser.parse("electronics_spec.md")
    print("Parsing successful!")
    print(data)
except Exception as e:
    print(f"Parsing failed: {e}")
