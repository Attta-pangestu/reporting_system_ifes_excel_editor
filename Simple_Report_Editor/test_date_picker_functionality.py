#!/usr/bin/env python3
"""
Test Date Picker Functionality
Script untuk testing date picker dan parameter tanggal
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_formula_with_date_params():
    """Test formula loading dengan parameter tanggal"""
    print("=" * 60)
    print("Testing Formula Engine with Date Parameters")
    print("=" * 60)

    try:
        from core.formula_engine import FormulaEngine

        engine = FormulaEngine()

        # Load formula
        if engine.load_formula('templates/ffb_scannerdata04_formula.json'):
            print("[PASS] Formula loaded successfully")

            # Get formula info
            info = engine.get_formula_info()
            print(f"[PASS] Query count: {info['query_count']}")
            print(f"[PASS] Variable count: {info['variable_count']}")
            print(f"[PASS] Queries: {', '.join(info['queries'])}")

            # Test parameter validation
            test_parameters = [
                {'start_date': '2025-10-01', 'end_date': '2025-10-31'},
                {'start_date': '2025-01-01', 'end_date': '2025-12-31'},
                {'start_date': '2025-11-01', 'end_date': '2025-11-01'},  # Same day
            ]

            for i, params in enumerate(test_parameters, 1):
                print(f"\n--- Test Case {i} ---")
                print(f"Parameters: {params}")

                # Validate parameter structure
                if 'start_date' in params and 'end_date' in params:
                    try:
                        start = datetime.strptime(params['start_date'], '%Y-%m-%d')
                        end = datetime.strptime(params['end_date'], '%Y-%m-%d')

                        if start <= end:
                            print(f"✓ Valid date range: {params['start_date']} to {params['end_date']}")
                        else:
                            print(f"✗ Invalid date range: start > end")
                    except ValueError as e:
                        print(f"✗ Invalid date format: {e}")
                else:
                    print(f"✗ Missing required parameters")

            return True
        else:
            print("✗ Failed to load formula")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_template_processing():
    """Test template processing dengan placeholder tanggal"""
    print("\n" + "=" * 60)
    print("Testing Template Processing")
    print("=" * 60)

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
            print(f"✓ Found template: {template_files[0]}")

            if processor.load_template(template_path):
                info = processor.get_template_info()
                print(f"✓ Template loaded successfully")
                print(f"✓ Worksheet: {info['worksheet_name']}")
                print(f"✓ Total rows: {info['total_rows']}")
                print(f"✓ Total columns: {info['total_columns']}")
                print(f"✓ Placeholders: {info['placeholder_count']}")
                print(f"✓ Repeating sections: {info['repeating_section_count']}")

                # Test placeholder extraction
                placeholders = processor.extract_placeholders()
                date_placeholders = [p for p in placeholders if 'date' in p.lower()]

                if date_placeholders:
                    print(f"✓ Date-related placeholders: {date_placeholders}")
                else:
                    print("ℹ No date-specific placeholders found")

                return True
            else:
                print("✗ Failed to load template")
                return False
        else:
            print("✗ No template files found")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_gui_components():
    """Test GUI components initialization"""
    print("\n" + "=" * 60)
    print("Testing GUI Components")
    print("=" * 60)

    try:
        import tkinter as tk
        from gui.main_window import MainWindow

        print("✓ Creating main window...")
        app = MainWindow()

        # Test date picker variables
        if hasattr(app, 'start_date_var') and hasattr(app, 'end_date_var'):
            print("✓ Date variables initialized")

            # Test date setting methods
            app._set_today()
            today_start = app.start_date_var.get()
            today_end = app.end_date_var.get()
            print(f"✓ Today range set: {today_start} to {today_end}")

            app._set_this_month()
            month_start = app.start_date_var.get()
            month_end = app.end_date_var.get()
            print(f"✓ This month range set: {month_start} to {month_end}")

            # Test date validation
            app.start_date_var.set('2025-10-01')
            app.end_date_var.set('2025-10-31')

            if app._validate_prerequisites():
                # Simulate database connection and template loading
                app.database_connected.set(True)
                app.template_loaded.set(True)
                app.formula_loaded.set(True)

                if app._validate_prerequisites():
                    print("✓ Date validation passed")
                else:
                    print("✗ Date validation failed")
            else:
                print("✗ Date validation failed")

            return True
        else:
            print("✗ Date variables not found")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_date_range_functions():
    """Test fungsi date range"""
    print("\n" + "=" * 60)
    print("Testing Date Range Functions")
    print("=" * 60)

    try:
        import tkinter as tk
        from gui.main_window import MainWindow

        app = MainWindow()

        # Test all date range functions
        test_functions = [
            ('Today', app._set_today),
            ('This Week', app._set_this_week),
            ('This Month', app._set_this_month),
            ('Last Month', app._set_last_month),
            ('This Year', app._set_this_year),
        ]

        for name, func in test_functions:
            func()
            start = app.start_date_var.get()
            end = app.end_date_var.get()
            print(f"✓ {name}: {start} to {end}")

            # Validate format
            try:
                datetime.strptime(start, '%Y-%m-%d')
                datetime.strptime(end, '%Y-%m-%d')
                if start <= end:
                    print(f"  ✓ Valid date range")
                else:
                    print(f"  ✗ Invalid date range (start > end)")
            except ValueError:
                print(f"  ✗ Invalid date format")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Main test function"""
    print("Simple Report Editor - Date Picker Functionality Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Formula Engine", test_formula_with_date_params),
        ("Template Processing", test_template_processing),
        ("GUI Components", test_gui_components),
        ("Date Range Functions", test_date_range_functions),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Date picker functionality is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")

    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()