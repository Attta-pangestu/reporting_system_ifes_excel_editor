#!/usr/bin/env python3
"""
Simple Debug Analyzer untuk Excel Report Generator
Menganalisis setiap komponen secara mendalam untuk menemukan akar masalah rendering placeholder
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_console_output():
    """Setup console output untuk Windows compatibility"""
    import sys
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('cp850')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('cp850')(sys.stderr.buffer, 'strict')

def print_section(title):
    """Print section header"""
    print("="*60)
    print(f"DEBUG: {title}")
    print("="*60)

def print_subsection(title):
    """Print subsection header"""
    print(f"\n{title}:")
    print("-"*40)

def analyze_formula_json():
    """Analisis formula JSON structure"""
    print_section("FORMULA JSON ANALYSIS")

    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    formula_path = os.path.join(base_path, "laporan_ffb_analysis_formula.json")

    print(f"Formula JSON path: {formula_path}")

    if not os.path.exists(formula_path):
        print("ERROR: Formula JSON file not found!")
        return False

    try:
        with open(formula_path, 'r', encoding='utf-8') as f:
            formulas = json.load(f)

        print("SUCCESS: Formula JSON loaded successfully")

        # Analyze queries
        print_subsection("QUERIES ANALYSIS")
        queries = formulas.get('queries', {})
        print(f"Total queries defined: {len(queries)}")

        for query_name, query_config in queries.items():
            print(f"\nQuery: {query_name}")
            sql = query_config.get('sql', '')
            return_format = query_config.get('return_format', 'unknown')

            # Check for parameters
            has_start_date = '{start_date}' in sql
            has_end_date = '{end_date}' in sql
            has_month = '{month}' in sql

            print(f"  SQL Length: {len(sql)} chars")
            print(f"  Return Format: {return_format}")
            print(f"  Uses start_date: {'YES' if has_start_date else 'NO'}")
            print(f"  Uses end_date: {'YES' if has_end_date else 'NO'}")
            print(f"  Uses month: {'YES' if has_month else 'NO'}")

            # Show SQL sample
            sql_preview = sql[:150] + "..." if len(sql) > 150 else sql
            print(f"  SQL Preview: {sql_preview}")

        # Analyze variables
        print_subsection("VARIABLES ANALYSIS")
        variables = formulas.get('variables', {})
        total_vars = sum(len(category_vars) for category_vars in variables.values())
        print(f"Total variable categories: {len(variables)}")
        print(f"Total variables: {total_vars}")

        for category_name, category_vars in variables.items():
            print(f"\nCategory: {category_name} ({len(category_vars)} variables)")
            for var_name, var_config in list(category_vars.items())[:3]:  # Show first 3
                var_type = var_config.get('type', 'unknown')
                query = var_config.get('query', '')
                field = var_config.get('field', '')
                print(f"  {var_name}: {var_type}")
                if query:
                    print(f"    -> Query: {query}")
                if field:
                    print(f"    -> Field: {field}")

        return True

    except Exception as e:
        print(f"ERROR analyzing formula JSON: {e}")
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection"""
    print_section("DATABASE CONNECTION TEST")

    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    print(f"Database path: {db_path}")

    if not os.path.exists(db_path):
        print("ERROR: Database file not found!")
        return False

    try:
        # Import dan test connector
        from firebird_connector_enhanced import FirebirdConnectorEnhanced

        print("Creating Firebird connector...")
        connector = FirebirdConnectorEnhanced(db_path=db_path)

        print("Testing connection...")
        if connector.test_connection():
            print("SUCCESS: Database connection successful!")

            # Test basic query
            print("Testing basic query...")
            test_query = "SELECT 'CONNECTION_TEST' as STATUS, CURRENT_TIMESTAMP as TEST_TIME FROM RDB$DATABASE"
            result = connector.execute_query(test_query)

            print(f"SUCCESS: Basic query successful!")
            print(f"Result type: {type(result)}")

            if result and len(result) > 0:
                if isinstance(result[0], dict):
                    print(f"First result: {result[0]}")
                elif isinstance(result[0], dict) and 'rows' in result[0]:
                    print(f"Rows returned: {len(result[0]['rows'])}")
                    if result[0]['rows']:
                        print(f"First row: {result[0]['rows'][0]}")

            return True
        else:
            print("ERROR: Database connection failed!")
            return False

    except Exception as e:
        print(f"ERROR: Database test failed: {e}")
        traceback.print_exc()
        return False

def test_query_execution():
    """Test query execution dengan parameter substitution"""
    print_section("QUERY EXECUTION TEST")

    try:
        # Import required modules
        from firebird_connector_enhanced import FirebirdConnectorEnhanced
        from formula_engine_enhanced import FormulaEngineEnhanced

        # Setup paths
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        formula_path = os.path.join(base_path, "laporan_ffb_analysis_formula.json")
        db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"

        # Initialize components
        connector = FirebirdConnectorEnhanced(db_path=db_path)
        formula_engine = FormulaEngineEnhanced(formula_path, connector)

        # Test parameters
        test_params = {
            'start_date': '2024-10-01',
            'end_date': '2024-10-31',
            'estate_name': 'PGE 2B TEST'
        }

        print(f"Test parameters: {test_params}")

        # Load formulas
        with open(formula_path, 'r', encoding='utf-8') as f:
            formulas = json.load(f)

        queries = formulas.get('queries', {})
        print(f"Testing {len(queries)} queries...")

        successful_queries = 0
        query_results = {}

        for query_name, query_config in queries.items():
            print(f"\nTesting query: {query_name}")

            try:
                original_sql = query_config.get('sql', '')
                print(f"Original SQL: {original_sql[:100]}...")

                # Test parameter substitution manually
                test_sql = original_sql
                if '{start_date}' in test_sql:
                    test_sql = test_sql.replace('{start_date}', f"'{test_params['start_date']}'")
                if '{end_date}' in test_sql:
                    test_sql = test_sql.replace('{end_date}', f"'{test_params['end_date']}'")
                if '{month}' in test_sql:
                    test_sql = test_sql.replace('{month}', '10')

                print(f"After substitution: {test_sql[:100]}...")

                # Execute query
                result = formula_engine.execute_query(query_name, test_params)
                query_results[query_name] = result

                if result is not None:
                    successful_queries += 1
                    print(f"SUCCESS: Query returned data")

                    if isinstance(result, list) and len(result) > 0:
                        if isinstance(result[0], dict) and 'rows' in result[0]:
                            rows = result[0]['rows']
                            headers = result[0].get('headers', [])
                            print(f"  Headers: {headers}")
                            print(f"  Rows: {len(rows)}")
                            if rows:
                                print(f"  Sample row: {rows[0]}")
                        else:
                            print(f"  First item: {result[0]}")
                else:
                    print("ERROR: Query returned None")

            except Exception as e:
                print(f"ERROR: Query {query_name} failed: {e}")
                query_results[query_name] = None

        print(f"\nQuery execution summary: {successful_queries}/{len(queries)} successful")

        # Test variable processing
        print_subsection("VARIABLE PROCESSING TEST")
        try:
            variables = formula_engine.process_variables(query_results, test_params)
            print(f"SUCCESS: Variable processing completed")
            print(f"Total variables processed: {len(variables)}")

            for var_name, value in list(variables.items())[:5]:  # Show first 5
                print(f"  {var_name}: {value} (type: {type(value).__name__})")

            return True, query_results, variables

        except Exception as e:
            print(f"ERROR: Variable processing failed: {e}")
            traceback.print_exc()
            return True, query_results, {}

    except Exception as e:
        print(f"ERROR: Query execution test failed: {e}")
        traceback.print_exc()
        return False, {}, {}

def test_template_rendering():
    """Test template rendering dengan actual data"""
    print_section("TEMPLATE RENDERING TEST")

    try:
        # Import required modules
        from template_processor_enhanced import TemplateProcessorEnhanced

        # Setup paths
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        templates_dir = os.path.join(base_path, "templates")
        formula_path = os.path.join(base_path, "laporan_ffb_analysis_formula.json")

        # Find template files
        if not os.path.exists(templates_dir):
            print("ERROR: Templates directory not found!")
            return False

        template_files = [f for f in os.listdir(templates_dir) if f.endswith(('.xlsx', '.xls'))]

        if not template_files:
            print("ERROR: No Excel template files found!")
            return False

        template_file = template_files[0]
        template_path = os.path.join(templates_dir, template_file)

        print(f"Using template: {template_file}")

        # Load template processor
        processor = TemplateProcessorEnhanced(template_path, formula_path)

        # Get placeholders
        placeholders = processor.get_placeholders()
        print(f"Template loaded successfully!")
        print(f"Sheets: {processor.workbook.sheetnames}")
        print(f"Total placeholders: {sum(len(p) for p in placeholders.values())}")

        # Analyze placeholders per sheet
        for sheet_name, sheet_placeholders in placeholders.items():
            print(f"\nSheet '{sheet_name}': {len(sheet_placeholders)} placeholders")
            for i, ph in enumerate(sheet_placeholders[:3]):  # Show first 3
                print(f"  {i+1}. {ph['placeholder']} at {ph['cell']}")
                print(f"     Full text: {ph['original_value']}")

            if len(sheet_placeholders) > 3:
                print(f"  ... and {len(sheet_placeholders) - 3} more")

        return True, processor, placeholders

    except Exception as e:
        print(f"ERROR: Template rendering test failed: {e}")
        traceback.print_exc()
        return False, None, {}

def test_end_to_end():
    """Test complete end-to-end process"""
    print_section("END-TO-END INTEGRATION TEST")

    # Test database connection
    db_ok = test_database_connection()
    if not db_ok:
        print("FAILED: Database connection failed - cannot continue")
        return False

    # Test query execution
    query_ok, query_results, variables = test_query_execution()
    if not query_ok:
        print("FAILED: Query execution failed - cannot continue")
        return False

    # Test template loading
    template_ok, processor, placeholders = test_template_rendering()
    if not template_ok:
        print("FAILED: Template loading failed - cannot continue")
        return False

    # Test complete rendering
    print_subsection("COMPLETE RENDERING TEST")

    try:
        # Prepare test data
        test_params = {
            'start_date': '2024-10-01',
            'end_date': '2024-10-31',
            'estate_name': 'PGE 2B TEST'
        }

        all_data = {
            **test_params,
            **variables,
            **query_results
        }

        print(f"Complete data keys: {list(all_data.keys())}")

        # Test each placeholder
        total_placeholders = sum(len(p) for p in placeholders.values())
        successful_substitutions = 0

        for sheet_name, sheet_placeholders in placeholders.items():
            print(f"\nTesting sheet: {sheet_name}")
            sheet_success = 0

            for ph in sheet_placeholders:
                placeholder = ph['placeholder']
                cell_coord = ph['cell']

                # Try to get value
                try:
                    value = processor._get_placeholder_value(placeholder, all_data)

                    if value is not None:
                        print(f"  SUCCESS: {placeholder} at {cell_coord} = {value}")
                        successful_substitutions += 1
                        sheet_success += 1
                    else:
                        print(f"  FAILED: {placeholder} at {cell_coord} = NO VALUE FOUND")
                        print(f"    Available keys: {list(all_data.keys())[:10]}...")

                except Exception as e:
                    print(f"  ERROR: {placeholder} at {cell_coord} = {e}")

            print(f"  Sheet summary: {sheet_success}/{len(sheet_placeholders)} successful")

        print(f"\nOVERALL RENDERING SUMMARY:")
        print(f"  Total placeholders: {total_placeholders}")
        print(f"  Successful substitutions: {successful_substitutions}")
        print(f"  Success rate: {successful_substitutions/total_placeholders*100:.1f}%")

        # Test actual template processing
        print_subsection("ACTUAL TEMPLATE PROCESSING")

        try:
            template_instance = processor.create_copy()
            processed_sheets = 0

            for sheet_name in template_instance.workbook.sheetnames:
                try:
                    success = template_instance.process_sheet_placeholders(sheet_name, all_data)
                    if success:
                        processed_sheets += 1
                        print(f"  SUCCESS: Sheet '{sheet_name}' processed")
                    else:
                        print(f"  FAILED: Sheet '{sheet_name}' processing failed")
                except Exception as e:
                    print(f"  ERROR: Sheet '{sheet_name}' error: {e}")

            # Save test output
            output_path = os.path.join(os.path.dirname(__file__), "test_output.xlsx")
            template_instance.save_processed_template(output_path)
            print(f"\nSUCCESS: Test output saved to: {output_path}")

            print(f"\nTemplate processing summary:")
            print(f"  Sheets processed: {processed_sheets}/{len(template_instance.workbook.sheetnames)}")

            return successful_substitutions > 0

        except Exception as e:
            print(f"ERROR: Actual template processing failed: {e}")
            traceback.print_exc()
            return False

    except Exception as e:
        print(f"ERROR: End-to-end test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function"""
    # Setup console
    setup_console_output()

    print("Excel Report Generator - Simple Debug Analyzer")
    print("="*60)

    try:
        # Run all tests
        print("Running comprehensive debugging analysis...\n")

        # Test formula JSON
        formula_ok = analyze_formula_json()

        # Test database connection
        db_ok = test_database_connection()

        # Test query execution
        query_ok, _, _ = test_query_execution()

        # Test template loading
        template_ok, _, _ = test_template_rendering()

        # Test end-to-end
        e2e_ok = test_end_to_end()

        # Final summary
        print_section("FINAL DIAGNOSTIC SUMMARY")
        print(f"Formula JSON analysis: {'PASS' if formula_ok else 'FAIL'}")
        print(f"Database connection: {'PASS' if db_ok else 'FAIL'}")
        print(f"Query execution: {'PASS' if query_ok else 'FAIL'}")
        print(f"Template loading: {'PASS' if template_ok else 'FAIL'}")
        print(f"End-to-end rendering: {'PASS' if e2e_ok else 'FAIL'}")

        if all([formula_ok, db_ok, query_ok, template_ok, e2e_ok]):
            print("\nALL TESTS PASSED! System should be working correctly.")
            return True
        else:
            print("\nSOME TESTS FAILED! Issues need to be addressed.")
            return False

    except Exception as e:
        print(f"\nCRITICAL ERROR during analysis: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)