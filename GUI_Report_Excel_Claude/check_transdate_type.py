#!/usr/bin/env python3
"""
Check TRANSDATE Type
Check the exact data type and format of TRANSDATE column
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def main():
    print('=' * 80)
    print('CHECKING TRANSDATE COLUMN TYPE')
    print('=' * 80)
    
    try:
        connector = FirebirdConnectorEnhanced()
        
        # Test 1: Get column metadata
        print("=== TEST 1: Column Metadata ===")
        
        meta_query = """SELECT 
            RDB$FIELD_NAME as COLUMN_NAME,
            RDB$FIELD_TYPE as FIELD_TYPE,
            RDB$FIELD_SUB_TYPE as FIELD_SUB_TYPE,
            RDB$FIELD_LENGTH as FIELD_LENGTH,
            RDB$FIELD_SCALE as FIELD_SCALE
            FROM RDB$RELATION_FIELDS rf
            JOIN RDB$FIELDS f ON rf.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
            WHERE rf.RDB$RELATION_NAME = 'FFBLOADINGCROP01' 
            AND rf.RDB$FIELD_NAME = 'TRANSDATE'"""
        
        meta_result = connector.execute_query(meta_query)
        if meta_result and meta_result[0]['rows']:
            row = meta_result[0]['rows'][0]
            print("✓ TRANSDATE metadata:")
            for key, value in row.items():
                print(f"  {key}: {value}")
        else:
            print("✗ Could not get metadata")
        
        # Test 2: Sample TRANSDATE values
        print("\n=== TEST 2: Sample TRANSDATE Values ===")
        
        sample_query = "SELECT TRANSDATE FROM FFBLOADINGCROP01 WHERE TRANSDATE IS NOT NULL ROWS 1 TO 10"
        sample_result = connector.execute_query(sample_query)
        if sample_result and sample_result[0]['rows']:
            print("✓ Sample TRANSDATE values:")
            for i, row in enumerate(sample_result[0]['rows']):
                value = row['TRANSDATE']
                print(f"  {i+1}: {value} (type: {type(value)})")
        else:
            print("✗ Could not get sample values")
        
        # Test 3: Try different GROUP BY approaches
        print("\n=== TEST 3: Different GROUP BY Approaches ===")
        
        group_approaches = [
            ("Direct TRANSDATE", "SELECT TRANSDATE, COUNT(*) as TOTAL FROM FFBLOADINGCROP01 WHERE TRANSDATE IS NOT NULL GROUP BY TRANSDATE ORDER BY TRANSDATE ROWS 1 TO 3"),
            ("EXTRACT Year/Month/Day", "SELECT EXTRACT(YEAR FROM TRANSDATE) as YEAR, EXTRACT(MONTH FROM TRANSDATE) as MONTH, EXTRACT(DAY FROM TRANSDATE) as DAY, COUNT(*) as TOTAL FROM FFBLOADINGCROP01 WHERE TRANSDATE IS NOT NULL GROUP BY EXTRACT(YEAR FROM TRANSDATE), EXTRACT(MONTH FROM TRANSDATE), EXTRACT(DAY FROM TRANSDATE) ORDER BY YEAR, MONTH, DAY ROWS 1 TO 3"),
            ("Simple GROUP BY", "SELECT TRANSDATE, COUNT(*) FROM FFBLOADINGCROP01 GROUP BY TRANSDATE ROWS 1 TO 3")
        ]
        
        for name, query in group_approaches:
            try:
                result = connector.execute_query(query)
                if result and result[0]['rows']:
                    print(f"  ✓ {name}: {len(result[0]['rows'])} groups")
                    for row in result[0]['rows']:
                        print(f"    {list(row.values())}")
                else:
                    print(f"  ✗ {name}: No result")
            except Exception as e:
                print(f"  ✗ {name}: Error - {e}")
        
        # Test 4: Test without date filtering
        print("\n=== TEST 4: Aggregation Without Date Filtering ===")
        
        no_filter_query = "SELECT COUNT(*) as TOTAL_TRANSACTIONS, SUM(BUNCHES) as TOTAL_BUNCHES, SUM(LOOSEFRUIT) as TOTAL_LOOSEFRUIT FROM FFBLOADINGCROP01"
        
        try:
            result = connector.execute_query(no_filter_query)
            if result and result[0]['rows']:
                row = result[0]['rows'][0]
                print(f"  ✓ Total aggregation: {row}")
            else:
                print("  ✗ Total aggregation failed")
        except Exception as e:
            print(f"  ✗ Total aggregation error: {e}")
        
        # Test 5: Test with simple WHERE clause
        print("\n=== TEST 5: Simple WHERE Clause ===")
        
        where_query = "SELECT COUNT(*) as TOTAL_TRANSACTIONS, SUM(BUNCHES) as TOTAL_BUNCHES FROM FFBLOADINGCROP01 WHERE BUNCHES > 0"
        
        try:
            result = connector.execute_query(where_query)
            if result and result[0]['rows']:
                row = result[0]['rows'][0]
                print(f"  ✓ WHERE clause works: {row}")
            else:
                print("  ✗ WHERE clause failed")
        except Exception as e:
            print(f"  ✗ WHERE clause error: {e}")
        
        print()
        print('=' * 80)
        print('TRANSDATE TYPE CHECK COMPLETED')
        print('=' * 80)
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()