#!/usr/bin/env python3
"""
Simple Placeholder Analysis - Shows what values replace which placeholders
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from formula_engine import FormulaEngine
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def main():
    print('=== SIMPLE PLACEHOLDER ANALYSIS ===')
    print('Menampilkan nilai aktual yang menggantikan placeholder\n')

    try:
        # Initialize components
        connector = FirebirdConnectorEnhanced()
        formula_engine = FormulaEngine('laporan_ffb_analysis_formula.json', connector)

        # Test parameters
        params = {
            'start_date': '2020-10-01',
            'end_date': '2020-10-10',
            'estate_name': 'PGE 2B',
            'estate_code': 'PGE_2B',
            'month': 10,
            'total_days': 10
        }

        print('STEP 1: Menjalankan query database...')
        all_results = formula_engine.execute_all_queries(params)

        print('Query Results:')
        for query_name, result in all_results.items():
            if result and isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and 'rows' in result[0]:
                    row_count = len(result[0]['rows'])
                    print(f'  {query_name}: {row_count} rows')
                    # Show sample data
                    if row_count > 0 and 'rows' in result[0]:
                        sample_row = result[0]['rows'][0]
                        print(f'    Sample: {sample_row}')
                else:
                    print(f'  {query_name}: {len(result)} results')
            else:
                print(f'  {query_name}: No data')

        print('\nSTEP 2: Memproses variables...')
        variables = formula_engine.process_variables(all_results, params)

        print(f'Total variables processed: {len(variables)}')

        print('\nSTEP 3: Nilai aktual untuk setiap placeholder:')
        print('=' * 70)

        # Show all variables with their actual values
        for var_name, var_value in sorted(variables.items()):
            if var_value is not None and var_value != '':
                print(f'{var_name:30} -> "{var_value}" (Type: {type(var_value).__name__})')
            else:
                print(f'{var_name:30} -> [EMPTY/NULL]')

        print('\nSTEP 4: Critical values validation:')
        print('-' * 40)

        critical_values = {
            'total_transactions': 'Jumlah total transaksi',
            'verification_rate': 'Tingkat verifikasi',
            'daily_average_transactions': 'Rata-rata transaksi harian',
            'report_title': 'Judul laporan',
            'report_period': 'Periode laporan',
            'generated_date': 'Tanggal generate'
        }

        for var_name, description in critical_values.items():
            if var_name in variables:
                value = variables[var_name]
                status = 'OK' if value and value != '' else 'MISSING'
                print(f'[{status}] {var_name:25} - {description}: "{value}"')
            else:
                print(f'[NOT FOUND] {var_name:25} - {description}')

        print('\nSTEP 5: Employee data check:')
        print('-' * 40)

        # Check if employee_performance query has data
        if 'employee_performance' in all_results and all_results['employee_performance']:
            emp_data = all_results['employee_performance']
            if isinstance(emp_data, list) and len(emp_data) > 0:
                if isinstance(emp_data[0], dict) and 'rows' in emp_data[0]:
                    rows = emp_data[0]['rows']
                    print(f'Employee query returned {len(rows)} rows')
                    for i, row in enumerate(rows[:3]):  # Show first 3 employees
                        if 'EMPLOYEE_NAME' in row:
                            print(f'  Employee {i+1}: {row["EMPLOYEE_NAME"]} - {row.get("JUMLAH_TRANSAKSI", "N/A")} transactions')

        print('\nSTEP 6: Field data check:')
        print('-' * 40)

        # Check if field_performance query has data
        if 'field_performance' in all_results and all_results['field_performance']:
            field_data = all_results['field_performance']
            if isinstance(field_data, list) and len(field_data) > 0:
                if isinstance(field_data[0], dict) and 'rows' in field_data[0]:
                    rows = field_data[0]['rows']
                    print(f'Field query returned {len(rows)} rows')
                    for row in rows:
                        if 'FIELDNAME' in row:
                            print(f'  Field: {row["FIELDNAME"]} - {row.get("JUMLAH_TRANSAKSI", "N/A")} transactions')

        print('\n=== ANALYSIS COMPLETE ===')
        print('Semua nilai placeholder telah diproses dengan data real dari database!')

        return True

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)