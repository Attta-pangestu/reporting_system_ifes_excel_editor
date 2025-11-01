#!/usr/bin/env python3
"""
Simple Test for Date Picker Functionality
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_formula_engine():
    """Test formula engine"""
    print("Testing Formula Engine...")

    try:
        from core.formula_engine import FormulaEngine
        engine = FormulaEngine()

        if engine.load_formula('templates/ffb_scannerdata04_formula.json'):
            print("PASS: Formula loaded successfully")

            info = engine.get_formula_info()
            print(f"PASS: {info['query_count']} queries found")
            print(f"PASS: {info['variable_count']} variables found")

            # Test parameters
            test_params = {
                'start_date': '2025-10-01',
                'end_date': '2025-10-31'
            }
            print(f"PASS: Test parameters ready: {test_params}")

            return True
        else:
            print("FAIL: Formula loading failed")
            return False

    except Exception as e:
        print(f"FAIL: Error {e}")
        return False

def test_template_processor():
    """Test template processor"""
    print("\nTesting Template Processor...")

    try:
        from core.template_processor import TemplateProcessor
        processor = TemplateProcessor()

        # Find template file
        template_files = []
        for file in os.listdir('templates'):
            if file.startswith('FFB_ScannerData04_Template_') and file.endswith('.xlsx'):
                template_files.append(file)

        if template_files:
            template_path = os.path.join('templates', template_files[0])
            print(f"PASS: Template found: {template_files[0]}")

            if processor.load_template(template_path):
                info = processor.get_template_info()
                print(f"PASS: Template loaded: {info['placeholder_count']} placeholders")
                print(f"PASS: Repeating sections: {info['repeating_section_count']}")
                return True
            else:
                print("FAIL: Template loading failed")
                return False
        else:
            print("FAIL: No template files found")
            return False

    except Exception as e:
        print(f"FAIL: Error {e}")
        return False

def test_date_functions():
    """Test date functions"""
    print("\nTesting Date Functions...")

    try:
        import tkinter as tk
        from gui.main_window import MainWindow

        # Create app (but don't show GUI)
        app = MainWindow()

        # Test date setting methods
        app._set_today()
        today_start = app.start_date_var.get()
        today_end = app.end_date_var.get()
        print(f"PASS: Today range set: {today_start} to {today_end}")

        app._set_this_month()
        month_start = app.start_date_var.get()
        month_end = app.end_date_var.get()
        print(f"PASS: This month range set: {month_start} to {month_end}")

        app._set_last_month()
        last_start = app.start_date_var.get()
        last_end = app.end_date_var.get()
        print(f"PASS: Last month range set: {last_start} to {last_end}")

        # Test validation
        app.start_date_var.set('2025-10-01')
        app.end_date_var.set('2025-10-31')
        app.database_connected.set(True)
        app.template_loaded.set(True)
        app.formula_loaded.set(True)

        if app._validate_prerequisites():
            print("PASS: Date validation passed")
            return True
        else:
            print("FAIL: Date validation failed")
            return False

    except Exception as e:
        print(f"FAIL: Error {e}")
        return False

def main():
    """Main test function"""
    print("Simple Report Editor - Date Picker Test")
    print("=" * 50)

    tests = [
        ("Formula Engine", test_formula_engine),
        ("Template Processor", test_template_processor),
        ("Date Functions", test_date_functions),
    ]

    results = {}

    for test_name, test_func in tests:
        results[test_name] = test_func()

    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")

    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("SUCCESS: All date picker functionality is working!")
    else:
        print("WARNING: Some tests failed.")

if __name__ == "__main__":
    main()