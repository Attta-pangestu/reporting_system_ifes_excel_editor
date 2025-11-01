#!/usr/bin/env python3
"""
Check Column Names and Data Types
Verifies exact column names and sample data from FFB and EMP tables
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def main():
    print('=' * 80)
    print('CHECKING COLUMN NAMES AND DATA TYPES')
    print('=' * 80)
    
    connector = FirebirdConnectorEnhanced()
    
    # Check EMP table structure
    print("=== EMP TABLE STRUCTURE ===")
    try:
        # Get column info
        emp_columns_query = '''SELECT 
            RDB$FIELD_NAME as COLUMN_NAME,
            RDB$FIELD_TYPE as FIELD_TYPE
            FROM RDB$RELATION_FIELDS 
            WHERE RDB$RELATION_NAME = 'EMP' 
            ORDER BY RDB$FIELD_POSITION'''
        
        emp_cols = connector.execute_query(emp_columns_query)
        if emp_cols and emp_cols[0]['rows']:
            print(f"EMP table has {len(emp_cols[0]['rows'])} columns:")
            for col in emp_cols[0]['rows']:
                col_name = col['COLUMN_NAME'].strip() if col['COLUMN_NAME'] else 'NULL'
                print(f"  - '{col_name}'")
        
        # Get sample data
        print("\nSample EMP data:")
        emp_sample = connector.execute_query('SELECT * FROM EMP ROWS 1 TO 3')
        if emp_sample and emp_sample[0]['rows']:
            for i, row in enumerate(emp_sample[0]['rows']):
                print(f"  Row {i+1}:")
                for key, value in row.items():
                    print(f"    '{key}': '{value}'")
                print()
        
    except Exception as e:
        print(f"Error checking EMP table: {e}")
    
    print()
    
    # Check FFBLOADINGCROP10 table structure
    print("=== FFBLOADINGCROP10 TABLE STRUCTURE ===")
    try:
        # Get column info
        ffb_columns_query = '''SELECT 
            RDB$FIELD_NAME as COLUMN_NAME,
            RDB$FIELD_TYPE as FIELD_TYPE
            FROM RDB$RELATION_FIELDS 
            WHERE RDB$RELATION_NAME = 'FFBLOADINGCROP10' 
            ORDER BY RDB$FIELD_POSITION'''
        
        ffb_cols = connector.execute_query(ffb_columns_query)
        if ffb_cols and ffb_cols[0]['rows']:
            print(f"FFBLOADINGCROP10 table has {len(ffb_cols[0]['rows'])} columns:")
            for col in ffb_cols[0]['rows']:
                col_name = col['COLUMN_NAME'].strip() if col['COLUMN_NAME'] else 'NULL'
                print(f"  - '{col_name}'")
        
        # Get sample data
        print("\nSample FFBLOADINGCROP10 data:")
        ffb_sample = connector.execute_query('SELECT * FROM FFBLOADINGCROP10 ROWS 1 TO 2')
        if ffb_sample and ffb_sample[0]['rows']:
            for i, row in enumerate(ffb_sample[0]['rows']):
                print(f"  Row {i+1}:")
                for key, value in row.items():
                    print(f"    '{key}': '{value}'")
                print()
        
        # Check date columns specifically
        print("\nChecking date columns:")
        date_check = connector.execute_query('''SELECT 
            "UPLOADDATETIME", 
            "HARVESTIN", 
            "PROCESSFL" 
            FROM FFBLOADINGCROP10 
            WHERE "UPLOADDATETIME" IS NOT NULL 
            ROWS 1 TO 3''')
        
        if date_check and date_check[0]['rows']:
            print("Date column samples:")
            for row in date_check[0]['rows']:
                print(f"  UPLOADDATETIME: {row.get('UPLOADDATETIME')}")
                print(f"  HARVESTIN: {row.get('HARVESTIN')}")
                print(f"  PROCESSFL: {row.get('PROCESSFL')}")
                print()
        
    except Exception as e:
        print(f"Error checking FFBLOADINGCROP10 table: {e}")
    
    print()
    
    # Test simple queries with correct column names
    print("=== TESTING SIMPLE QUERIES ===")
    
    # Test EMP query
    try:
        print("Testing EMP query...")
        emp_test = connector.execute_query('SELECT COUNT(*) as TOTAL FROM EMP')
        if emp_test and emp_test[0]['rows']:
            total = emp_test[0]['rows'][0]['TOTAL']
            print(f"✓ EMP table accessible: {total} records")
    except Exception as e:
        print(f"✗ EMP query failed: {e}")
    
    # Test FFB query
    try:
        print("Testing FFBLOADINGCROP10 query...")
        ffb_test = connector.execute_query('SELECT COUNT(*) as TOTAL FROM FFBLOADINGCROP10')
        if ffb_test and ffb_test[0]['rows']:
            total = ffb_test[0]['rows'][0]['TOTAL']
            print(f"✓ FFBLOADINGCROP10 table accessible: {total} records")
    except Exception as e:
        print(f"✗ FFBLOADINGCROP10 query failed: {e}")
    
    print()
    print('=' * 80)
    print('COLUMN CHECK COMPLETED')
    print('=' * 80)

if __name__ == '__main__':
    main()