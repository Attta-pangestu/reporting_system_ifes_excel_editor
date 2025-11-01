#!/usr/bin/env python3
"""
Debug script to understand how to access structured data
"""

import sys
sys.path.append('.')
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def main():
    # Initialize connector
    connector = FirebirdConnectorEnhanced.create_default_connector()
    
    print('=== ANALYZING STRUCTURED DATA ACCESS ===')
    
    # Test with EMP table first (smaller dataset)
    try:
        result = connector.execute_query('SELECT FIRST 1 * FROM EMP')
        if result and len(result) > 0:
            first_item = result[0]
            print(f'EMP result structure: {type(first_item)}')
            print(f'EMP keys: {list(first_item.keys())}')
            
            if 'headers' in first_item:
                headers = first_item['headers']
                rows = first_item['rows']
                print(f'EMP Headers type: {type(headers)}')
                print(f'EMP Rows type: {type(rows)}')
                print(f'EMP Headers: {headers}')
                print(f'EMP Rows count: {len(rows) if rows else 0}')
                
                if rows and len(rows) > 0:
                    print(f'EMP First row: {rows[0]}')
                    print(f'EMP First row type: {type(rows[0])}')
                    
                    # Try to create proper dictionary
                    if headers and len(headers) > 0 and len(rows) > 0:
                        first_row = rows[0]
                        if isinstance(first_row, (list, tuple)) and len(first_row) >= len(headers):
                            emp_dict = dict(zip(headers, first_row))
                            print(f'EMP Reconstructed dict: {dict(list(emp_dict.items())[:5])}')
                            
                            # Look for employee code and name
                            for key, value in emp_dict.items():
                                if 'CODE' in str(key).upper() or 'EMP' in str(key).upper():
                                    print(f'  Employee code field: {key} = {value}')
                                if 'NAME' in str(key).upper():
                                    print(f'  Employee name field: {key} = {value}')
    except Exception as e:
        print(f'EMP analysis failed: {e}')
    
    print('\n=== ANALYZING FFBSCANNERDATA10 ===')
    try:
        result = connector.execute_query('SELECT FIRST 1 * FROM FFBSCANNERDATA10')
        if result and len(result) > 0:
            first_item = result[0]
            
            if 'headers' in first_item:
                headers = first_item['headers']
                rows = first_item['rows']
                print(f'FFBSCANNERDATA10 Headers: {headers}')
                print(f'FFBSCANNERDATA10 Rows count: {len(rows) if rows else 0}')
                
                if rows and len(rows) > 0:
                    first_row = rows[0]
                    print(f'FFBSCANNERDATA10 First row: {first_row}')
                    
                    # Try to create proper dictionary
                    if headers and len(headers) > 0:
                        if isinstance(first_row, (list, tuple)) and len(first_row) >= len(headers):
                            ffb_dict = dict(zip(headers, first_row))
                            print(f'FFBSCANNERDATA10 Reconstructed dict keys: {list(ffb_dict.keys())}')
                            
                            # Look for key fields
                            key_fields = ['TRANSDATE', 'SCANUSERID', 'FIELDID', 'RIPEBCH', 'UNRIPEBCH']
                            for field in key_fields:
                                if field in ffb_dict:
                                    print(f'  {field}: {ffb_dict[field]}')
    except Exception as e:
        print(f'FFBSCANNERDATA10 analysis failed: {e}')
    
    print('\n=== TESTING DIRECT QUERY APPROACH ===')
    # Test if we can query specific columns directly
    try:
        result = connector.execute_query('SELECT COUNT(*) as TOTAL FROM FFBSCANNERDATA10')
        print(f'Direct count query result: {result}')
    except Exception as e:
        print(f'Direct query failed: {e}')
    
    # Test with different table
    print('\n=== TESTING FFBLOADINGCROP10 ===')
    try:
        result = connector.execute_query('SELECT FIRST 1 * FROM FFBLOADINGCROP10')
        if result and len(result) > 0:
            first_item = result[0]
            print(f'FFBLOADINGCROP10 structure: {list(first_item.keys())}')
            
            if 'headers' in first_item:
                headers = first_item['headers']
                rows = first_item['rows']
                print(f'FFBLOADINGCROP10 Headers: {headers}')
                print(f'FFBLOADINGCROP10 Rows count: {len(rows) if rows else 0}')
    except Exception as e:
        print(f'FFBLOADINGCROP10 test failed: {e}')

if __name__ == "__main__":
    main()