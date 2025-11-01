#!/usr/bin/env python3
"""
Minimal Test - Simple Report Editor
==================================

Test minimal untuk memastikan sistem dasar bekerja.
"""

import os
import sys

def test_files_exist():
    """Test that required files exist"""
    print("Testing file existence...")

    required_files = [
        'formula_engine.py',
        'template_processor.py',
        'report_generator.py',
        'simple_report_editor.py',
        'firebird_connector.py',
        'config/app_config.json'
    ]

    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)

    if missing:
        print(f"[FAIL] Missing files: {missing}")
        return False
    else:
        print("[PASS] All required files exist")
        return True

def test_basic_functionality():
    """Test basic functionality without imports"""
    print("Testing basic functionality...")

    try:
        # Test file reading
        config_file = "config/app_config.json"
        with open(config_file, 'r') as f:
            content = f.read()

        if len(content) > 0:
            print("[PASS] Config file readable")
            return True
        else:
            print("[FAIL] Config file empty")
            return False

    except Exception as e:
        print(f"[FAIL] Error reading config: {e}")
        return False

def test_template_files():
    """Test template files"""
    print("Testing template files...")

    template_dir = "./templates"
    if not os.path.exists(template_dir):
        print("[FAIL] Templates directory not found")
        return False

    formula_files = [f for f in os.listdir(template_dir) if f.endswith('_formula.json')]
    excel_files = [f for f in os.listdir(template_dir) if f.endswith(('.xlsx', '.xls'))]

    print(f"[INFO] Found {len(formula_files)} formula files")
    print(f"[INFO] Found {len(excel_files)} Excel files")

    if len(formula_files) > 0:
        print("[PASS] Template files found")
        return True
    else:
        print("[WARN] No template files found")
        return False

def main():
    """Run minimal tests"""
    print("=" * 50)
    print("Simple Report Editor - Minimal Tests")
    print("=" * 50)

    tests = [
        ("File Existence", test_files_exist),
        ("Basic Functionality", test_basic_functionality),
        ("Template Files", test_template_files)
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            if test_func():
                passed += 1
                print(f"[RESULT] {name}: PASSED")
            else:
                print(f"[RESULT] {name}: FAILED")
        except Exception as e:
            print(f"[RESULT] {name}: ERROR - {e}")

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("SUCCESS! All minimal tests passed.")
        return True
    else:
        print(f"{total - passed} test(s) failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)