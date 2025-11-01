#!/usr/bin/env python3
"""
Get Exact Column Names
Uses SELECT * with ROWS 1 TO 1 to get column names
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def main():
    print('=' * 80)
    print('GETTING EXACT COLUMN NAMES')
    print('=' * 80)
    
    connector = FirebirdConnectorEnhanced()
    
    # Get EMP table columns
    print("=== EMP TABLE COLUMNS ===")
    try:
        emp_result = connector.execute_query('SELECT * FROM EMP ROWS 1 TO 1')
        if emp_result and emp_result[0]['rows']:
            print("EMP table columns:")
            sample_row = emp_result[0]['rows'][0]
            for i, (col_name, value) in enumerate(sample_row.items()):
                print(f"  {i+1:2d}. '{col_name}' = '{value}'")
        else:
            print("No data in EMP table")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Get FFBLOADINGCROP10 table columns
    print("=== FFBLOADINGCROP10 TABLE COLUMNS ===")
    try:
        ffb_result = connector.execute_query('SELECT * FROM FFBLOADINGCROP10 ROWS 1 TO 1')
        if ffb_result and ffb_result[0]['rows']:
            print("FFBLOADINGCROP10 table columns:")
            sample_row = ffb_result[0]['rows'][0]
            for i, (col_name, value) in enumerate(sample_row.items()):
                print(f"  {i+1:2d}. '{col_name}' = '{value}'")
        else:
            print("No data in FFBLOADINGCROP10 table")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test specific queries to find working column names
    print("=== TESTING SPECIFIC COLUMNS ===")
    
    # Test EMP columns
    emp_columns_to_test = [
        'EMPID', 'EMPCODE', 'EMPNAME', 'NAME', 
        'ID', 'CODE', 'EMPLOYEE_ID', 'EMPLOYEE_NAME'
    ]
    
    print("Testing EMP columns:")
    for col in emp_columns_to_test:
        try:
            test_query = f'SELECT "{col}" FROM EMP ROWS 1 TO 1'
            result = connector.execute_query(test_query)
            if result and result[0]['rows']:
                print(f"  ✓ '{col}' exists")
            else:
                print(f"  ✗ '{col}' no data")
        except Exception as e:
            print(f"  ✗ '{col}' error: {str(e)[:50]}...")
    
    print()
    
    # Test FFB columns
    ffb_columns_to_test = [
        'SCANID', 'SCAN_ID', 'ID', 'TRANSDATE', 'TRANS_DATE', 
        'DATE', 'BUNCHES', 'BUNCH', 'UPLOADDATETIME', 'UPLOAD_DATE'
    ]
    
    print("Testing FFBLOADINGCROP10 columns:")
    for col in ffb_columns_to_test:
        try:
            test_query = f'SELECT "{col}" FROM FFBLOADINGCROP10 ROWS 1 TO 1'
            result = connector.execute_query(test_query)
            if result and result[0]['rows']:
                print(f"  ✓ '{col}' exists")
            else:
                print(f"  ✗ '{col}' no data")
        except Exception as e:
            print(f"  ✗ '{col}' error: {str(e)[:50]}...")
    
    print()
    print('=' * 80)
    print('COLUMN TESTING COMPLETED')
    print('=' * 80)

if __name__ == '__main__':
    main()