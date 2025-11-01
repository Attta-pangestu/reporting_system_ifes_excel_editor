#!/usr/bin/env python3
"""
Debug FFB Columns
Check exact column names in FFBLOADINGCROP01 and test individual columns
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def main():
    print('=' * 80)
    print('DEBUGGING FFB TABLE COLUMNS')
    print('=' * 80)
    
    try:
        connector = FirebirdConnectorEnhanced()
        
        # Test 1: Get exact column names from system tables
        print("=== TEST 1: System Table Column Names ===")
        
        system_query = """SELECT 
            RDB$FIELD_NAME as COLUMN_NAME
            FROM RDB$RELATION_FIELDS 
            WHERE RDB$RELATION_NAME = 'FFBLOADINGCROP01'
            ORDER BY RDB$FIELD_POSITION"""
        
        result = connector.execute_query(system_query)
        if result and result[0]['rows']:
            print("✓ FFBLOADINGCROP01 columns:")
            columns = []
            for row in result[0]['rows']:
                col_name = row['COLUMN_NAME'].strip() if row['COLUMN_NAME'] else 'NULL'
                columns.append(col_name)
                print(f"  - '{col_name}'")
            
            print(f"\nTotal columns: {len(columns)}")
            
            # Test 2: Test individual columns
            print("\n=== TEST 2: Individual Column Tests ===")
            
            test_columns = ['SCANUSE', 'EMPCODE', 'TRANSDATE', 'PROCESSDATE', 'BUNCHES', 'LOOSEFRUIT']
            
            for col in test_columns:
                if col in columns:
                    try:
                        test_query = f'SELECT {col} FROM FFBLOADINGCROP01 WHERE {col} IS NOT NULL ROWS 1 TO 1'
                        test_result = connector.execute_query(test_query)
                        if test_result and test_result[0]['rows']:
                            value = test_result[0]['rows'][0].get(col, 'NULL')
                            print(f"  ✓ {col}: {value}")
                        else:
                            print(f"  ✗ {col}: No data")
                    except Exception as e:
                        print(f"  ✗ {col}: Error - {e}")
                else:
                    print(f"  ✗ {col}: Column not found")
            
            # Test 3: Try SELECT * with ROWS 1 TO 1
            print("\n=== TEST 3: SELECT * Test ===")
            try:
                select_all_query = 'SELECT * FROM FFBLOADINGCROP01 ROWS 1 TO 1'
                select_all_result = connector.execute_query(select_all_query)
                if select_all_result and select_all_result[0]['rows']:
                    print("✓ SELECT * works, returned keys:")
                    row = select_all_result[0]['rows'][0]
                    for key in sorted(row.keys()):
                        value = row[key]
                        print(f"  - '{key}': {value}")
                else:
                    print("✗ SELECT * failed")
            except Exception as e:
                print(f"✗ SELECT * error: {e}")
            
            # Test 4: Count total records
            print("\n=== TEST 4: Record Count ===")
            try:
                count_query = 'SELECT COUNT(*) as TOTAL FROM FFBLOADINGCROP01'
                count_result = connector.execute_query(count_query)
                if count_result and count_result[0]['rows']:
                    total = count_result[0]['rows'][0]['TOTAL']
                    print(f"✓ Total records: {total}")
                else:
                    print("✗ Count failed")
            except Exception as e:
                print(f"✗ Count error: {e}")
            
            # Test 5: Try with first available column
            print("\n=== TEST 5: Test with First Available Column ===")
            if columns:
                first_col = columns[0]
                try:
                    first_query = f'SELECT {first_col} FROM FFBLOADINGCROP01 ROWS 1 TO 3'
                    first_result = connector.execute_query(first_query)
                    if first_result and first_result[0]['rows']:
                        print(f"✓ First column '{first_col}' works:")
                        for i, row in enumerate(first_result[0]['rows']):
                            value = row.get(first_col, 'NULL')
                            print(f"  Row {i+1}: {value}")
                    else:
                        print(f"✗ First column '{first_col}' failed")
                except Exception as e:
                    print(f"✗ First column error: {e}")
        
        else:
            print("✗ Could not get column names")
        
        print()
        print('=' * 80)
        print('FFB COLUMN DEBUG COMPLETED')
        print('=' * 80)
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()