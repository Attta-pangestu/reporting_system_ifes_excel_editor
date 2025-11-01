#!/usr/bin/env python3
"""
Script untuk membuat proper template data yang sesuai dengan structure yang ada
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebird_connector_enhanced import FirebirdConnectorEnhanced
from formula_engine_enhanced import FormulaEngineEnhanced

def create_proper_template_data():
    """Buat data yang sesuai dengan template yang ada"""

    print("="*60)
    print("CREATING PROPER TEMPLATE DATA")
    print("="*60)

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
        'estate_name': 'PGE 2B',
        'estate_code': 'PGE_2B'
    }

    print(f"Test parameters: {test_params}")

    # Execute queries
    print("\nExecuting queries...")
    query_results = formula_engine.execute_all_queries(test_params)

    # Process variables
    print("Processing variables...")
    variables = formula_engine.process_variables(query_results, test_params)

    # Create proper data structure for template
    template_data = {}

    # Add basic variables
    template_data.update(variables)
    template_data.update(test_params)

    # Add structured data for repeating sections
    print("\nCreating structured data for template...")

    # Process daily performance data
    if 'daily_performance' in query_results and query_results['daily_performance']:
        daily_data = query_results['daily_performance']
        if isinstance(daily_data, list) and len(daily_data) > 0:
            if isinstance(daily_data[0], dict) and 'rows' in daily_data[0]:
                rows = daily_data[0]['rows']
                headers = daily_data[0].get('headers', [])
                print(f"Daily performance: {len(rows)} rows, headers: {headers}")

                # Create structured data for template
                template_data['daily_performance_rows'] = rows
                template_data['daily_performance_headers'] = headers

    # Process employee performance data
    if 'employee_performance' in query_results and query_results['employee_performance']:
        emp_data = query_results['employee_performance']
        if isinstance(emp_data, list) and len(emp_data) > 0:
            if isinstance(emp_data[0], dict) and 'rows' in emp_data[0]:
                rows = emp_data[0]['rows']
                headers = emp_data[0].get('headers', [])
                print(f"Employee performance: {len(rows)} rows, headers: {headers}")

                template_data['employee_performance_rows'] = rows
                template_data['employee_performance_headers'] = headers

    # Process field performance data
    if 'field_performance' in query_results and query_results['field_performance']:
        field_data = query_results['field_performance']
        if isinstance(field_data, list) and len(field_data) > 0:
            if isinstance(field_data[0], dict) and 'rows' in field_data[0]:
                rows = field_data[0]['rows']
                headers = field_data[0].get('headers', [])
                print(f"Field performance: {len(rows)} rows, headers: {headers}")

                template_data['field_performance_rows'] = rows
                template_data['field_performance_headers'] = headers

    # Process quality analysis data
    if 'quality_analysis' in query_results and query_results['quality_analysis']:
        quality_data = query_results['quality_analysis']
        if isinstance(quality_data, list) and len(quality_data) > 0:
            if isinstance(quality_data[0], dict) and 'rows' in quality_data[0]:
                rows = quality_data[0]['rows']
                headers = quality_data[0].get('headers', [])
                print(f"Quality analysis: {len(rows)} rows, headers: {headers}")

                template_data['quality_analysis_rows'] = rows
                template_data['quality_analysis_headers'] = headers

    # Add missing critical variables
    print("\nAdding missing critical variables...")

    # Get transaction summary
    if 'transaction_summary' in query_results and query_results['transaction_summary']:
        trans_data = query_results['transaction_summary']
        if isinstance(trans_data, list) and len(trans_data) > 0:
            if isinstance(trans_data[0], dict) and 'rows' in trans_data[0]:
                row = trans_data[0]['rows'][0]  # Get first row
                print(f"Transaction summary row: {row}")

                # Add individual fields
                template_data['TOTAL_TRANSAKSI'] = row.get('TOTAL_TRANSAKSI', 0)
                template_data['total_transactions_raw'] = row.get('TOTAL_TRANSAKSI', 0)

    # Fix verification rate
    if 'verification_rate' in query_results and query_results['verification_rate']:
        verif_data = query_results['verification_rate']
        if isinstance(verif_data, list) and len(verif_data) > 0:
            if isinstance(verif_data[0], dict) and 'rows' in verif_data[0]:
                row = verif_data[0]['rows'][0]
                template_data['verification_rate_raw'] = row.get('VERIFICATION_RATE', 0)
                template_data['VERIFICATION_RATE'] = row.get('VERIFICATION_RATE', 0)

    # Add synthetic data for missing fields
    template_data['SYNTHETIC_RIPE'] = 4500
    template_data['SYNTHETIC_UNRIPE'] = 350
    template_data['SYNTHETIC_BLACK'] = 150
    template_data['SYNTHETIC_ROTTEN'] = 75
    template_data['SYNTHETIC_LOOSE'] = 25

    print(f"\nTemplate data keys created: {list(template_data.keys())}")

    # Create enhanced variable mapping
    print("\nCreating enhanced variable mapping...")

    # Add specific field mappings for template
    field_mappings = {
        # Dashboard sheet mappings
        'total_ripe_bunches': template_data.get('SYNTHETIC_RIPE', 0),
        'total_unripe_bunches': template_data.get('SYNTHETIC_UNRIPE', 0),
        'verification_rate': template_data.get('verification_rate_raw', 95.0),

        # Repeating section mappings
        'TRANSDATE': 'daily_performance_rows',
        'JUMLAH_TRANSAKSI': 'daily_performance_rows',
        'RIPE_BUNCHES': 'daily_performance_rows',
        'UNRIPE_BUNCHES': 'daily_performance_rows',
        'BLACK_BUNCHES': 'daily_performance_rows',
        'ROTTEN_BUNCHES': 'daily_performance_rows',
        'LONGSTALK_BUNCHES': 'daily_performance_rows',
        'RAT_DAMAGE_BUNCHES': 'daily_performance_rows',
        'LOOSE_FRUIT_KG': 'daily_performance_rows',

        'EMPLOYEE_NAME': 'employee_performance_rows',
        'RECORDTAG': 'employee_performance_rows',
        'TOTAL_RIPE': 'employee_performance_rows',
        'TOTAL_UNRIPE': 'employee_performance_rows',
        'TOTAL_BLACK': 'employee_performance_rows',
        'TOTAL_ROTTEN': 'employee_performance_rows',
        'TOTAL_LONGSTALK': 'employee_performance_rows',
        'TOTAL_RATDAMAGE': 'employee_performance_rows',
        'TOTAL_LOOSEFRUIT': 'employee_performance_rows',

        'FIELDNAME': 'field_performance_rows',
        'JUMLAH_TRANSAKSI': 'field_performance_rows',
        'TOTAL_RIPE': 'field_performance_rows',
        'TOTAL_UNRIPE': 'field_performance_rows',
        'TOTAL_BLACK': 'field_performance_rows',
        'TOTAL_ROTTEN': 'field_performance_rows',
        'TOTAL_LONGSTALK': 'field_performance_rows',
        'TOTAL_RATDAMAGE': 'field_performance_rows',
        'TOTAL_LOOSEFRUIT': 'field_performance_rows',

        # Quality analysis mappings
        'TOTAL_RIPE': 'quality_analysis_rows',
        'TOTAL_BLACK': 'quality_analysis_rows',
        'TOTAL_ROTTEN': 'quality_analysis_rows',
        'TOTAL_RATDAMAGE': 'quality_analysis_rows',
        'PERCENTAGE_DEFECT': 'quality_analysis_rows'
    }

    # Add mappings to template data
    template_data['_field_mappings'] = field_mappings

    # Save template data
    output_file = os.path.join(os.path.dirname(__file__), "template_data.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(template_data, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nTemplate data saved to: {output_file}")

    return template_data

def analyze_template_requirements():
    """Analisis requirements template yang sebenarnya"""

    print_section("TEMPLATE REQUIREMENTS ANALYSIS")

    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_path, "templates")

    template_files = [f for f in os.listdir(templates_dir) if f.endswith(('.xlsx', '.xls'))]

    if template_files:
        template_file = template_files[0]
        template_path = os.path.join(templates_dir, template_file)

        print(f"Analyzing template: {template_file}")

        from template_processor_enhanced import TemplateProcessorEnhanced
        formula_path = os.path.join(base_path, "laporan_ffb_analysis_formula.json")

        processor = TemplateProcessorEnhanced(template_path, formula_path)
        placeholders = processor.get_placeholders()

        print("\nRequired variables by sheet:")
        required_vars = set()

        for sheet_name, sheet_placeholders in placeholders.items():
            print(f"\nSheet '{sheet_name}': {len(sheet_placeholders)} placeholders")
            sheet_vars = set()

            for ph in sheet_placeholders:
                placeholder = ph['placeholder']
                required_vars.add(placeholder)
                sheet_vars.add(placeholder)

                # Show first few per sheet
                if len(sheet_placeholders) <= 5:
                    print(f"  • {placeholder} at {ph['cell']}")
                elif ph == sheet_placeholders[0]:
                    print(f"  • {placeholder} at {ph['cell']}")
                    print(f"  ... and {len(sheet_placeholders)-1} more")

            print(f"  Unique variables: {len(sheet_vars)}")

        print(f"\nTotal unique variables required: {len(required_vars)}")
        print("\nAll required variables:")
        for var in sorted(required_vars):
            print(f"  • {var}")

        # Identify missing variables
        print("\nAnalyzing missing variables from current formula...")

        with open(formula_path, 'r', encoding='utf-8') as f:
            formulas = json.load(f)

        variables = formulas.get('variables', {})
        defined_vars = set()

        for category, category_vars in variables.items():
            for var_name in category_vars.keys():
                defined_vars.add(var_name)

        missing_vars = required_vars - defined_vars
        print(f"\nMissing variables in formula definition: {len(missing_vars)}")
        for var in sorted(missing_vars):
            print(f"  • {var}")

        return required_vars, defined_vars, missing_vars

def print_section(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f"ANALYSIS: {title}")
    print("="*60)

def main():
    """Main function"""
    try:
        # Create proper template data
        template_data = create_proper_template_data()

        # Analyze template requirements
        required_vars, defined_vars, missing_vars = analyze_template_requirements()

        print("\n" + "="*60)
        print("SUMMARY AND RECOMMENDATIONS")
        print("="*60)

        print(f"\n1. Required variables: {len(required_vars)}")
        print(f"2. Defined variables: {len(defined_vars)}")
        print(f"3. Missing variables: {len(missing_vars)}")

        if missing_vars:
            print(f"\nRECOMMENDATIONS:")
            print(f"1. Add missing variables to formula JSON:")
            for var in sorted(missing_vars):
                print(f"   - {var}")
            print(f"\n2. Update variable processing to handle repeating section data")
            print(f"3. Create proper data mapping for template fields")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)