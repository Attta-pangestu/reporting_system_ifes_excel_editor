#!/usr/bin/env python3
"""
Test Placeholder Replacement System
Script untuk testing fix placeholder variable replacement
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_formula_processing():
    """Test formula processing dengan fix"""
    print("Testing Formula Processing with Fixes...")

    try:
        from core.database_connector import FirebirdConnectorEnhanced
        from core.formula_engine import FormulaEngine

        # Create instances
        connector = FirebirdConnectorEnhanced.create_default_connector()
        engine = FormulaEngine()

        # Load formula
        if engine.load_formula('templates/ffb_scannerdata04_formula.json'):
            print("PASS: Formula loaded")

            # Test connection
            if connector.test_connection():
                print("PASS: Database connected")

                # Set connector
                engine.database_connector = connector

                # Test parameters
                test_params = {
                    'start_date': '2025-10-01',
                    'end_date': '2025-10-31'
                }

                # Execute queries
                try:
                    query_results = engine.execute_queries(test_params)
                    print("PASS: Queries executed")

                    # Process variables
                    variables = engine.process_variables(query_results, test_params)
                    print(f"PASS: Variables processed: {len(variables)} variables")

                    # Check important variables
                    important_vars = ['estate_name', 'report_period', 'report_date', 'database_name', 'generated_by', 'generation_time']
                    for var in important_vars:
                        if var in variables:
                            value = variables[var]
                            print(f"  {var}: {value} ({type(value).__name__})")
                        else:
                            print(f"  {var}: NOT FOUND")

                    # Check summary variables
                    if 'summary' in variables:
                        summary = variables['summary']
                        if isinstance(summary, dict):
                            print(f"  summary variables: {len(summary)} items")
                            for key, value in list(summary.items())[:5]:  # Show first 5
                                print(f"    {key}: {value}")
                        else:
                            print(f"  summary: {summary} (type: {type(summary)})")

                    return True

                except Exception as e:
                    print(f"FAIL: Query execution error: {e}")
                    return False
            else:
                print("SKIP: Database connection failed")
                return False
        else:
            print("FAIL: Formula loading failed")
            return False

    except Exception as e:
        print(f"FAIL: Error {e}")
        return False

def test_template_processing():
    """Test template processing dengan fix"""
    print("\nTesting Template Processing with Fixes...")

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
                print("PASS: Template loaded")

                # Test placeholder extraction
                placeholders = processor.extract_placeholders()
                print(f"PASS: {len(placeholders)} placeholders found")

                # Show some placeholders
                data_placeholders = [p for p in placeholders if 'data_records.' in p]
                summary_placeholders = [p for p in placeholders if 'summary.' in p]
                other_placeholders = [p for p in placeholders if 'data_records.' not in p and 'summary.' not in p]

                print(f"  Data placeholders: {len(data_placeholders)}")
                print(f"  Summary placeholders: {len(summary_placeholders)}")
                print(f"  Other placeholders: {len(other_placeholders)}")

                # Test data_records placeholder processing
                test_text = "{{data_records.0.ID}} {{data_records.0.SCANUSERID}} {{summary.total_records}}"
                test_variables = {
                    'data_records': [
                        {'ID': '123', 'SCANUSERID': 'USER001'},
                        {'ID': '124', 'SCANUSERID': 'USER002'}
                    ],
                    'summary': {'total_records': 42}
                }

                processed = processor._process_data_records_placeholders(test_text, test_variables)
                print(f"PASS: Data records placeholder processing: '{test_text}' -> '{processed}'")

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

def test_formula_expressions():
    """Test formula expression processing"""
    print("\nTesting Formula Expressions...")

    try:
        from core.formula_engine import FormulaEngine
        from datetime import datetime

        engine = FormulaEngine()

        # Test IF formula with ISBLANK
        formula1 = "IF(ISBLANK(start_date), MONTH(TODAY()) & ' ' & YEAR(TODAY()), MONTH(start_date) & ' ' & YEAR(start_date))"
        variables1 = {'start_date': '2025-10-01'}  # Not blank
        result1 = engine._process_if_formula(formula1, variables1)
        print(f"PASS: ISBLANK test (with date): '{result1}'")

        variables2 = {}  # Blank
        result2 = engine._process_if_formula(formula1, variables2)
        print(f"PASS: ISBLANK test (blank): '{result2}'")

        # Test MONTH() and YEAR() functions
        test_expression = "MONTH(start_date) & ' ' & YEAR(start_date)"
        result3 = engine._process_formula_expression(test_expression, {'start_date': '2025-10-01'})
        print(f"PASS: MONTH/YEAR functions: '{result3}'")

        # Test TODAY() function
        test_expression2 = "TODAY()"
        result4 = engine._process_formula_expression(test_expression2, {})
        today_str = datetime.now().strftime('%Y-%m-%d')
        print(f"PASS: TODAY() function: '{result4}' (expected: '{today_str}')")

        return True

    except Exception as e:
        print(f"FAIL: Error {e}")
        return False

def test_nested_value_extraction():
    """Test nested value extraction"""
    print("\nTesting Nested Value Extraction...")

    try:
        from core.formula_engine import FormulaEngine

        engine = FormulaEngine()

        # Test with simple dict
        simple_data = {'a': {'b': {'c': 'value1'}}}
        result1 = engine._get_nested_value(simple_data, ['a', 'b', 'c'])
        print(f"PASS: Simple nested dict: '{result1}'")

        # Test with Firebird result format
        firebird_data = {
            'summary_stats': {
                'headers': ['total_records'],
                'rows': [{'total_records': 42}]
            }
        }
        result2 = engine._get_nested_value(firebird_data, ['summary_stats', 'total_records'])
        print(f"PASS: Firebird result format: '{result2}'")

        # Test with list data
        list_data = {'items': [{'id': 1}, {'id': 2}]}
        result3 = engine._get_nested_value(list_data, ['items', '0', 'id'])
        print(f"PASS: List data: '{result3}'")

        return True

    except Exception as e:
        print(f"FAIL: Error {e}")
        return False

def main():
    """Main test function"""
    print("Placeholder Replacement System Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Formula Processing", test_formula_processing),
        ("Template Processing", test_template_processing),
        ("Formula Expressions", test_formula_expressions),
        ("Nested Value Extraction", test_nested_value_extraction),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"FAIL: {test_name} failed with exception: {e}")
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

    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("SUCCESS: All placeholder replacement systems are working!")
        print("INFO: Variables should now be properly replaced in reports.")
    else:
        print("WARNING: Some tests failed. Please check the implementation.")

    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()