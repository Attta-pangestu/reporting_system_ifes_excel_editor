#!/usr/bin/env python3
"""
Debug script to check database table structure and data availability
"""

import sys
sys.path.append('.')
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def main():
    # Initialize connector
    connector = FirebirdConnectorEnhanced.create_default_connector()
    
    print('=== CHECKING TABLE EXISTENCE ===')
    # Check if tables exist
    tables_to_check = ['FFBSCANNERDATA10', 'FFBSCANNERDATA11', 'EMP', 'OCFIELD', 'CRDIVISION']
    for table in tables_to_check:
        try:
            result = connector.execute_query(f'SELECT COUNT(*) FROM {table}')
            count = result[0]['COUNT'] if result and len(result) > 0 else 0
            print(f'{table}: {count} records')
        except Exception as e:
            print(f'{table}: ERROR - {str(e)}')
    
    print('\n=== CHECKING EMP TABLE COLUMNS ===')
    try:
        result = connector.execute_query('SELECT FIRST 3 * FROM EMP')
        if result:
            print(f'EMP sample data: {len(result)} rows')
            print(f'EMP columns: {list(result[0].keys())}')
            for i, row in enumerate(result[:2]):
                print(f'  Row {i+1}: {dict(list(row.items())[:3])}')
        else:
            print('EMP: No data found')
    except Exception as e:
        print(f'EMP check failed: {e}')
    
    print('\n=== CHECKING FFBSCANNERDATA10 COLUMNS ===')
    try:
        result = connector.execute_query('SELECT FIRST 2 * FROM FFBSCANNERDATA10')
        if result:
            print(f'FFBSCANNERDATA10 sample data: {len(result)} rows')
            print(f'FFBSCANNERDATA10 columns: {list(result[0].keys())}')
            for i, row in enumerate(result):
                transdate = row.get('TRANSDATE', 'N/A')
                scanuserid = row.get('SCANUSERID', 'N/A')
                fieldid = row.get('FIELDID', 'N/A')
                print(f'  Row {i+1}: TRANSDATE={transdate}, SCANUSERID={scanuserid}, FIELDID={fieldid}')
        else:
            print('FFBSCANNERDATA10: No data found')
    except Exception as e:
        print(f'FFBSCANNERDATA10 check failed: {e}')
    
    print('\n=== CHECKING DATE RANGE IN FFBSCANNERDATA10 ===')
    try:
        result = connector.execute_query('SELECT MIN(TRANSDATE) as MIN_DATE, MAX(TRANSDATE) as MAX_DATE FROM FFBSCANNERDATA10')
        if result:
            min_date = result[0].get('MIN_DATE', 'N/A')
            max_date = result[0].get('MAX_DATE', 'N/A')
            print(f'Date range: {min_date} to {max_date}')
        else:
            print('No date range data found')
    except Exception as e:
        print(f'Date range check failed: {e}')

if __name__ == "__main__":
    main()