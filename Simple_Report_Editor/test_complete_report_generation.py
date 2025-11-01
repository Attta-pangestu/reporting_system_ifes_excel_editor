#!/usr/bin/env python3
"""
Test Complete Report Generation
Test script untuk men-generate report lengkap dengan placeholder replacement
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_complete_report_generation():
    """Test complete report generation dengan semua fix"""
    print("Testing Complete Report Generation...")
    print("=" * 60)

    try:
        from core.database_connector import FirebirdConnectorEnhanced
        from core.template_processor import TemplateProcessor
        from core.formula_engine import FormulaEngine

        # 1. Initialize components
        print("1. Initializing components...")
        connector = FirebirdConnectorEnhanced.create_default_connector()
        template_processor = TemplateProcessor()
        formula_engine = FormulaEngine()

        # 2. Test database connection
        print("2. Testing database connection...")
        if not connector.test_connection():
            print("FAIL: Database connection failed")
            return False
        print("PASS: Database connected")

        # 3. Load template
        print("3. Loading template...")
        template_files = []
        for file in os.listdir('templates'):
            if file.startswith('FFB_ScannerData04_Template_') and file.endswith('.xlsx'):
                template_files.append(file)

        if not template_files:
            print("FAIL: No template files found")
            return False

        template_path = os.path.join('templates', template_files[0])
        if not template_processor.load_template(template_path):
            print("FAIL: Template loading failed")
            return False
        print(f"PASS: Template loaded: {template_files[0]}")

        # 4. Load formula
        print("4. Loading formula...")
        if not formula_engine.load_formula('templates/ffb_scannerdata04_formula.json'):
            print("FAIL: Formula loading failed")
            return False
        print("PASS: Formula loaded")

        # 5. Execute queries
        print("5. Executing database queries...")
        formula_engine.database_connector = connector

        test_params = {
            'start_date': '2025-10-01',
            'end_date': '2025-10-31'
        }

        query_results = formula_engine.execute_queries(test_params)
        print(f"PASS: Queries executed - {len(query_results)} result sets")

        for query_name, result in query_results.items():
            if result:
                if isinstance(result, list):
                    print(f"  {query_name}: {len(result)} items")
                elif isinstance(result, dict) and 'rows' in result:
                    print(f"  {query_name}: {len(result.get('rows', []))} rows")
                else:
                    print(f"  {query_name}: {type(result)}")
            else:
                print(f"  {query_name}: No data")

        # 6. Process variables
        print("6. Processing variables...")
        variables = formula_engine.process_variables(query_results, test_params)
        print(f"PASS: Variables processed - {len(variables)} variables")

        # Show important variables
        important_vars = [
            'estate_name', 'report_period', 'report_date',
            'database_name', 'generated_by', 'generation_time'
        ]

        for var in important_vars:
            if var in variables:
                value = variables[var]
                print(f"  {var}: {value}")
            else:
                print(f"  {var}: NOT FOUND")

        # Show summary variables
        if 'summary' in variables and isinstance(variables['summary'], dict):
            summary = variables['summary']
            print(f"  Summary: {len(summary)} fields")
            for key, value in list(summary.items())[:5]:
                print(f"    {key}: {value}")

        # 7. Test placeholder replacement
        print("7. Testing placeholder replacement...")
        replacements = template_processor.replace_placeholders(variables)
        print(f"PASS: {replacements} placeholders replaced")

        # 8. Create test report
        print("8. Creating test report...")
        output_path = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        template_processor.save_template(output_path)
        print(f"PASS: Test report created: {output_path}")

        # 9. Validate output
        print("9. Validating output file...")
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"PASS: Output file exists - {file_size} bytes")

            if file_size > 0:
                print("SUCCESS: Complete report generation test passed!")
                return True
            else:
                print("FAIL: Output file is empty")
                return False
        else:
            print("FAIL: Output file not created")
            return False

    except Exception as e:
        print(f"FAIL: Error during report generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_placeholder_validation():
    """Test placeholder validation"""
    print("\nTesting Placeholder Validation...")

    try:
        from core.template_processor import TemplateProcessor
        from core.formula_engine import FormulaEngine

        processor = TemplateProcessor()
        engine = FormulaEngine()

        # Load template
        template_files = []
        for file in os.listdir('templates'):
            if file.startswith('FFB_ScannerData04_Template_') and file.endswith('.xlsx'):
                template_files.append(file)

        if template_files:
            template_path = os.path.join('templates', template_files[0])
            processor.load_template(template_path)
            engine.load_formula('templates/ffb_scannerdata04_formula.json')

            # Create test variables
            test_variables = {
                'estate_name': 'PGE 2B',
                'report_period': 'October 2025',
                'report_date': '01 November 2025',
                'database_name': 'PTRJ_P2B.FDB',
                'generated_by': 'System',
                'generation_time': '01-11-2025 12:08:30',
                'data_records': [
                    {'ID': '123', 'SCANUSERID': 'USER001', 'FIELDID': 'A001'},
                    {'ID': '124', 'SCANUSERID': 'USER002', 'FIELDID': 'A002'}
                ],
                'summary': {
                    'total_records': 2,
                    'total_ripe_bunch': 100,
                    'total_unripe_bunch': 20,
                    'date_range': '2025-10-01 to 2025-10-31'
                }
            }

            # Validate placeholders
            is_valid, missing = processor.validate_placeholders(test_variables)

            print(f"PASS: Placeholder validation - {'Valid' if is_valid else 'Invalid'}")
            if missing:
                print(f"  Missing placeholders: {len(missing)}")
                for miss in missing[:5]:  # Show first 5
                    print(f"    {miss}")
            else:
                print("  All placeholders have values")

            return is_valid

    except Exception as e:
        print(f"FAIL: Error in placeholder validation: {e}")
        return False

def main():
    """Main test function"""
    print("Complete Report Generation Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Complete Report Generation", test_complete_report_generation),
        ("Placeholder Validation", test_placeholder_validation),
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
        print("SUCCESS: Complete report generation is working!")
        print("INFO: All placeholder variables should be properly replaced.")
        print("INFO: Reports should be generated with actual data values.")
    else:
        print("WARNING: Some tests failed. Please check the implementation.")

    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()