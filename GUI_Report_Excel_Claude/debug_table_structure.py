#!/usr/bin/env python3
"""
Debug script to analyze the actual table structure
"""

import sys
sys.path.append('.')
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def main():
    # Initialize connector
    connector = FirebirdConnectorEnhanced.create_default_connector()
    
    print('=== ANALYZING FFBSCANNERDATA10 STRUCTURE ===')
    try:
        # Get raw result to see actual structure
        result = connector.execute_query('SELECT FIRST 1 * FROM FFBSCANNERDATA10', return_format='dict')
        if result:
            print(f'Raw result type: {type(result)}')
            print(f'Result length: {len(result)}')
            print(f'First item type: {type(result[0])}')
            print(f'First item keys: {list(result[0].keys())}')
            
            # Check if it has headers/rows structure
            first_row = result[0]
            if 'headers' in first_row and 'rows' in first_row:
                print('\n=== STRUCTURED DATA DETECTED ===')
                headers = first_row.get('headers', [])
                rows = first_row.get('rows', [])
                print(f'Headers: {headers}')
                print(f'Rows type: {type(rows)}')
                print(f'Number of rows: {len(rows) if rows else 0}')
                if rows:
                    print(f'First row sample: {rows[0] if len(rows) > 0 else "No rows"}')
            else:
                print('\n=== DIRECT COLUMN ACCESS ===')
                for key, value in first_row.items():
                    print(f'{key}: {value}')
        else:
            print('No data found in FFBSCANNERDATA10')
    except Exception as e:
        print(f'FFBSCANNERDATA10 analysis failed: {e}')
    
    print('\n=== CHECKING OTHER FFB TABLES ===')
    # Check for other FFB tables
    try:
        tables = connector.get_table_list()
        ffb_tables = [t for t in tables if 'FFB' in t.upper() or 'SCANNER' in t.upper()]
        print(f'Found FFB/Scanner tables: {ffb_tables}')
        
        for table in ffb_tables[:3]:  # Check first 3 tables
            try:
                result = connector.execute_query(f'SELECT COUNT(*) FROM {table}')
                count = result[0]['COUNT'] if result and len(result) > 0 else 0
                print(f'{table}: {count} records')
                
                if count > 0:
                    # Get sample data
                    sample = connector.execute_query(f'SELECT FIRST 1 * FROM {table}')
                    if sample:
                        print(f'  Sample columns: {list(sample[0].keys())[:10]}...')
            except Exception as e:
                print(f'{table}: ERROR - {str(e)}')
                
    except Exception as e:
        print(f'Table listing failed: {e}')
    
    print('\n=== CHECKING EMP TABLE STRUCTURE ===')
    try:
        # Check EMP table column names for employee mapping
        result = connector.execute_query('SELECT FIRST 1 * FROM EMP')
        if result:
            emp_columns = list(result[0].keys())
            print(f'EMP columns: {emp_columns}')
            
            # Look for ID columns
            id_columns = [col for col in emp_columns if 'ID' in col.upper()]
            print(f'ID-related columns: {id_columns}')
            
            # Check for employee code and name patterns
            code_columns = [col for col in emp_columns if 'CODE' in col.upper() or 'EMP' in col.upper()]
            name_columns = [col for col in emp_columns if 'NAME' in col.upper()]
            print(f'Code-related columns: {code_columns}')
            print(f'Name-related columns: {name_columns}')
            
    except Exception as e:
        print(f'EMP analysis failed: {e}')

if __name__ == "__main__":
    main()