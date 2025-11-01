#!/usr/bin/env python3
"""
Direct Column Check
Use the working firebird connector to get exact column names
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced
import json

def main():
    print('=' * 80)
    print('DIRECT COLUMN CHECK USING WORKING CONNECTOR')
    print('=' * 80)
    
    try:
        connector = FirebirdConnectorEnhanced()
        
        # Test 1: Get system table info for FFBLOADINGCROP01
        print("=== TEST 1: System Table Column Info ===")
        
        system_query = """SELECT 
            RDB$FIELD_NAME as COLUMN_NAME
            FROM RDB$RELATION_FIELDS 
            WHERE RDB$RELATION_NAME = 'FFBLOADINGCROP01'
            ORDER BY RDB$FIELD_POSITION"""
        
        result = connector.execute_query(system_query)
        if result and result[0]['rows']:
            print("✓ FFBLOADINGCROP01 columns from system tables:")
            columns = []
            for row in result[0]['rows']:
                col_name = row['COLUMN_NAME'].strip() if row['COLUMN_NAME'] else 'NULL'
                columns.append(col_name)
                print(f"  - '{col_name}'")
            
            print(f"\nTotal columns: {len(columns)}")
            
            # Test with first few columns
            if columns:
                print("\n=== TEST 2: Sample Data with First Columns ===")
                first_cols = columns[:5]  # First 5 columns
                col_list = ', '.join([f'"{col}"' for col in first_cols])
                
                sample_query = f"SELECT {col_list} FROM FFBLOADINGCROP01 ROWS 1 TO 3"
                sample_result = connector.execute_query(sample_query)
                
                if sample_result and sample_result[0]['rows']:
                    print(f"✓ Sample data with first {len(first_cols)} columns:")
                    for i, row in enumerate(sample_result[0]['rows']):
                        print(f"  Row {i+1}:")
                        for col in first_cols:
                            value = row.get(col, 'N/A')
                            print(f"    {col}: {value}")
                else:
                    print("✗ No sample data found")
        else:
            print("✗ Could not get column info from system tables")
        
        print()
        
        # Test 3: Try different column name patterns
        print("=== TEST 3: Testing Column Name Patterns ===")
        
        # Common patterns we've seen
        test_patterns = [
            'SCANUSE',
            'ID_SCANUSE', 
            'IDSCANUSE',
            'EMPCODE',
            'ID_EMPCODE',
            'IDEMPCODE',
            'TRANSDATE',
            'TRANS_DATE',
            'PROCESSDATE',
            'PROCESS_DATE',
            'BUNCHES',
            'BUNC',
            'LOOSEFRUIT',
            'LOOSE_FRUIT'
        ]
        
        for pattern in test_patterns:
            try:
                test_query = f'SELECT "{pattern}" FROM FFBLOADINGCROP01 ROWS 1 TO 1'
                test_result = connector.execute_query(test_query)
                if test_result and test_result[0]['rows']:
                    value = test_result[0]['rows'][0].get(pattern, 'NULL')
                    print(f"  ✓ '{pattern}' exists: {value}")
                else:
                    print(f"  ✗ '{pattern}' not found")
            except:
                print(f"  ✗ '{pattern}' failed")
        
        print()
        
        # Test 4: EMP table columns
        print("=== TEST 4: EMP Table Columns ===")
        
        emp_system_query = """SELECT 
            RDB$FIELD_NAME as COLUMN_NAME
            FROM RDB$RELATION_FIELDS 
            WHERE RDB$RELATION_NAME = 'EMP'
            ORDER BY RDB$FIELD_POSITION"""
        
        emp_result = connector.execute_query(emp_system_query)
        if emp_result and emp_result[0]['rows']:
            print("✓ EMP columns from system tables:")
            emp_columns = []
            for row in emp_result[0]['rows']:
                col_name = row['COLUMN_NAME'].strip() if row['COLUMN_NAME'] else 'NULL'
                emp_columns.append(col_name)
                print(f"  - '{col_name}'")
            
            # Test EMP sample data
            if emp_columns:
                print("\n=== TEST 5: EMP Sample Data ===")
                emp_first_cols = emp_columns[:3]  # First 3 columns
                emp_col_list = ', '.join([f'"{col}"' for col in emp_first_cols])
                
                emp_sample_query = f"SELECT {emp_col_list} FROM EMP ROWS 1 TO 3"
                emp_sample_result = connector.execute_query(emp_sample_query)
                
                if emp_sample_result and emp_sample_result[0]['rows']:
                    print(f"✓ EMP sample data with first {len(emp_first_cols)} columns:")
                    for i, row in enumerate(emp_sample_result[0]['rows']):
                        print(f"  Row {i+1}:")
                        for col in emp_first_cols:
                            value = row.get(col, 'N/A')
                            print(f"    {col}: {value}")
                else:
                    print("✗ No EMP sample data found")
        else:
            print("✗ Could not get EMP column info")
        
        print()
        
        # Test 6: Try to get actual working query
        print("=== TEST 6: Find Working Query Pattern ===")
        
        # Try simple SELECT * to see what we get
        try:
            simple_query = "SELECT * FROM FFBLOADINGCROP01 ROWS 1 TO 1"
            simple_result = connector.execute_query(simple_query)
            
            if simple_result and simple_result[0]['rows']:
                print("✓ SELECT * works, available keys:")
                row = simple_result[0]['rows'][0]
                for key in row.keys():
                    value = row[key]
                    print(f"  - '{key}': {value}")
            else:
                print("✗ SELECT * failed")
        except Exception as e:
            print(f"✗ SELECT * error: {e}")
        
        print()
        print('=' * 80)
        print('DIRECT COLUMN CHECK COMPLETED')
        print('=' * 80)
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()