#!/usr/bin/env python3
"""
Simple Test Script - Simple Report Editor
==========================================

Testing script sederhana untuk memverifikasi komponen utama sistem.
"""

import os
import sys
import json
from pathlib import Path

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_basic_imports():
    """Test basic imports"""
    print("Testing imports...")

    try:
        from firebird_connector import FirebirdConnector
        from formula_engine import FormulaEngine
        from template_processor import TemplateProcessor
        from report_generator import ReportGenerator
        print("[PASS] All imports successful")
        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("Testing configuration...")

    try:
        config_file = "config/app_config.json"
        if not os.path.exists(config_file):
            print(f"[FAIL] Config file not found: {config_file}")
            return False

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        print(f"[PASS] Config loaded successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Config error: {e}")
        return False

def test_templates():
    """Test template discovery"""
    print("Testing templates...")

    try:
        template_dir = Path("./templates")
        if not template_dir.exists():
            print("[FAIL] Templates directory not found")
            return False

        formula_files = list(template_dir.glob("*_formula.json"))
        excel_files = list(template_dir.glob("*.xlsx"))

        print(f"[INFO] Found {len(formula_files)} formula files")
        print(f"[INFO] Found {len(excel_files)} Excel templates")

        if formula_files:
            print(f"[PASS] Templates found: {[f.name for f in formula_files]}")
            return True
        else:
            print("[WARN] No formula files found")
            return False
    except Exception as e:
        print(f"[FAIL] Template error: {e}")
        return False

def test_formula_loading():
    """Test formula loading"""
    print("Testing formula loading...")

    try:
        template_dir = Path("./templates")
        formula_files = list(template_dir.glob("*_formula.json"))

        if not formula_files:
            print("[SKIP] No formula files to test")
            return True

        formula_file = formula_files[0]
        print(f"[INFO] Testing: {formula_file.name}")

        with open(formula_file, 'r', encoding='utf-8') as f:
            formula_data = json.load(f)

        queries = formula_data.get('queries', {})
        variables = formula_data.get('variables', {})

        print(f"[PASS] Formula loaded - {len(queries)} queries, {len(variables)} variables")
        return True
    except Exception as e:
        print(f"[FAIL] Formula loading error: {e}")
        return False

def test_formula_engine():
    """Test formula engine"""
    print("Testing formula engine...")

    try:
        from formula_engine import FormulaEngine

        engine = FormulaEngine()

        # Test basic functionality
        test_formula = {
            'variables': {
                'test_const': {
                    'type': 'constant',
                    'value': 'Test Value'
                }
            }
        }

        test_data = {'test_query': [{'ID': 1, 'NAME': 'Test'}]}
        engine.query_results = test_data

        processed = engine.process_variables(test_formula, test_data)

        if 'test_const' in processed and processed['test_const'] == 'Test Value':
            print("[PASS] Formula engine working")
            return True
        else:
            print(f"[FAIL] Formula engine processing failed: {processed}")
            return False
    except Exception as e:
        print(f"[FAIL] Formula engine error: {e}")
        return False

def test_template_processor():
    """Test template processor"""
    print("Testing template processor...")

    try:
        from template_processor import TemplateProcessor

        processor = TemplateProcessor()

        # Test placeholder extraction
        test_text = "Hello {{name}}, date is {{date}}"
        placeholders = processor.extract_placeholders(test_text)

        if placeholders == ['name', 'date']:
            print("[PASS] Template processor working")
            return True
        else:
            print(f"[FAIL] Expected ['name', 'date'], got {placeholders}")
            return False
    except Exception as e:
        print(f"[FAIL] Template processor error: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("=" * 50)
    print("Simple Report Editor - Basic Tests")
    print("=" * 50)

    tests = [
        ("Basic Imports", test_basic_imports),
        ("Configuration", test_config),
        ("Templates", test_templates),
        ("Formula Loading", test_formula_loading),
        ("Formula Engine", test_formula_engine),
        ("Template Processor", test_template_processor)
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            if test_func():
                passed += 1
                print(f"[RESULT] {name}: PASSED")
            else:
                failed += 1
                print(f"[RESULT] {name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"[RESULT] {name}: ERROR - {e}")

    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Total: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\nSUCCESS! All tests passed.")
        return True
    else:
        print(f"\n{failed} test(s) failed.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)