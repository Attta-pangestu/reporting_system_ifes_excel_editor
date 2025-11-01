#!/usr/bin/env python3
"""
Placeholder Validation Tracker - Shows exactly what values replace which placeholders
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from formula_engine import FormulaEngine
from firebird_connector_enhanced import FirebirdConnectorEnhanced
from template_processor import TemplateProcessor

def main():
    print('=== PLACEHOLDER VALIDATION TRACKER ===')
    print('Menganalisis perubahan nilai dari placeholder ke nilai aktual\n')

    try:
        # Initialize components
        connector = FirebirdConnectorEnhanced()
        formula_engine = FormulaEngine('laporan_ffb_analysis_formula.json', connector)
        template_processor = TemplateProcessor('templates/Template_Laporan_FFB_Analysis.xlsx', 'laporan_ffb_analysis_formula.json')

        # Test parameters
        params = {
            'start_date': '2020-10-01',
            'end_date': '2020-10-10',
            'estate_name': 'PGE 2B',
            'estate_code': 'PGE_2B',
            'month': 10,
            'total_days': 10
        }

        print('STEP 1: Menjalankan semua query database...')
        all_results = formula_engine.execute_all_queries(params)

        print('Query Results Summary:')
        for query_name, result in all_results.items():
            if result and isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and 'rows' in result[0]:
                    row_count = len(result[0]['rows'])
                    print(f'  - {query_name}: {row_count} rows data')
                else:
                    print(f'  - {query_name}: {len(result)} results')
            else:
                print(f'  - {query_name}: No data')

        print('\nSTEP 2: Memproses semua variables...')
        variables = formula_engine.process_variables(all_results, params)

        print(f'Total Variables Processed: {len(variables)}')

        print('\nSTEP 3: Analisis perubahan placeholder ke nilai aktual:')
        print('=' * 80)

        # Get all placeholders from template
        placeholders = template_processor.get_placeholders()

        # Track all changes
        all_changes = {}

        for sheet_name, sheet_placeholders in placeholders.items():
            for placeholder_info in sheet_placeholders:
                placeholder_name = placeholder_info['placeholder']
                cell_location = placeholder_info['location']

                # Get the actual value that would replace this placeholder
                actual_value = template_processor._get_variable_value(placeholder_name, variables)

                all_changes[placeholder_name] = {
                    'sheet': sheet_name,
                    'cell': cell_location,
                    'placeholder': f'{{{{{placeholder_name}}}}}',
                    'actual_value': actual_value,
                    'type': type(actual_value).__name__
                }

        # Display all results
        print('\nALL PLACEHOLDER CHANGES:')
        print('-' * 50)
        for var_name, info in sorted(all_changes.items()):
            print(f'  {var_name}')
            print(f'    Sheet: {info["sheet"]}')
            print(f'    Cell: {info["cell"]}')
            print(f'    Change: "{info["placeholder"]}" → "{info["actual_value"]}"')
            print(f'    Type: {info["type"]}')
            print()

        print('STEP 4: Summary Validation:')
        print('=' * 80)

        total_placeholders = sum(len(sheet_placeholders) for sheet_placeholders in placeholders.values())
        variables_with_values = sum(1 for v in variables.values() if v is not None and v != '')
        variables_without_values = sum(1 for v in variables.values() if v is None or v == '')

        print(f'Total Placeholders Found: {total_placeholders}')
        print(f'Variables with Values: {variables_with_values}')
        print(f'Variables without Values: {variables_without_values}')

        success_rate = (variables_with_values / len(variables)) * 100 if variables else 0
        print(f'Success Rate: {success_rate:.1f}%')

        print('\nCritical Database Values:')
        print('-' * 40)
        critical_vars = ['total_transactions', 'verification_rate', 'daily_average_transactions', 'report_title', 'report_period']
        for var in critical_vars:
            if var in variables:
                value = variables[var]
                status = 'OK' if value and value != '' else 'MISSING'
                print(f'  [{status}] {var}: "{value}"')
            else:
                print(f'  [NOT FOUND] {var}')

        print('\nANALYSIS COMPLETE!')
        print(f'Detailed report saved to: placeholder_analysis_report.txt')

        # Save detailed report to file
        save_detailed_report(placeholders, variables, all_results, params)

        return True

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return False

def save_detailed_report(placeholders, variables, all_results, params):
    """Save detailed analysis report to file"""

    filename = 'placeholder_analysis_report.txt'

    with open(filename, 'w', encoding='utf-8') as f:
        f.write('PLACEHOLDER VALIDATION DETAILED REPORT\n')
        f.write('=' * 60 + '\n\n')
        f.write(f'Generated: {params.get("start_date")} to {params.get("end_date")}\n')
        f.write(f'Estate: {params.get("estate_name")}\n\n')

        f.write('DATABASE QUERY RESULTS:\n')
        f.write('-' * 30 + '\n')
        for query_name, result in all_results.items():
            f.write(f'{query_name}:\n')
            if result and isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and 'rows' in result[0]:
                    rows = result[0]['rows']
                    f.write(f'  Rows: {len(rows)}\n')
                    if len(rows) > 0:
                        first_row = rows[0]
                        f.write(f'  Sample Data: {first_row}\n')
                else:
                    f.write(f'  Results: {len(result)}\n')
            else:
                f.write('  No data\n')
            f.write('\n')

        f.write('PROCESSED VARIABLES:\n')
        f.write('-' * 30 + '\n')
        for var_name, var_value in variables.items():
            f.write(f'{var_name}: {var_value} (Type: {type(var_value).__name__})\n')

        f.write('\nPLACEHOLDER ANALYSIS:\n')
        f.write('-' * 30 + '\n')
        total_placeholders = 0
        for sheet_name, sheet_placeholders in placeholders.items():
            f.write(f'\nSheet: {sheet_name}\n')
            for placeholder_info in sheet_placeholders:
                placeholder_name = placeholder_info['placeholder']
                cell_location = placeholder_info['location']
                actual_value = placeholder_info.get('actual_value', 'NOT PROCESSED')

                f.write(f'  {cell_location}: {placeholder_name}\n')
                f.write(f'    → "{actual_value}"\n')
                total_placeholders += 1

        f.write(f'\n\nSUMMARY:\n')
        f.write(f'Total Placeholders: {total_placeholders}\n')
        f.write(f'Total Variables: {len(variables)}\n')
        f.write(f'Variables with Values: {sum(1 for v in variables.values() if v is not None and v != "")}\n')

    print(f'📁 Detailed report saved to: {filename}')

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)