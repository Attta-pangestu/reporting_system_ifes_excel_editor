#!/usr/bin/env python3
"""
Debug Date Filtering
Check why aggregated queries with date filtering are failing
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def main():
    print('=' * 80)
    print('DEBUGGING DATE FILTERING')
    print('=' * 80)
    
    try:
        connector = FirebirdConnectorEnhanced()
        
        # Test 1: Check date column data types and values
        print("=== TEST 1: Date Column Analysis ===")
        
        date_query = """SELECT 
            TRANSDATE, 
            CAST(TRANSDATE AS DATE) as TRANS_DATE_CAST,
            TRANSTIME,
            HARVESTINGDATE
            FROM FFBLOADINGCROP01 
            WHERE TRANSDATE IS NOT NULL 
            ROWS 1 TO 5"""
        
        date_result = connector.execute_query(date_query)
        if date_result and date_result[0]['rows']:
            print("✓ Date column samples:")
            for i, row in enumerate(date_result[0]['rows']):
                print(f"  Row {i+1}:")
                for key, value in row.items():
                    print(f"    {key}: {value} (type: {type(value)})")
        else:
            print("✗ Date column analysis failed")
        
        # Test 2: Test simple date filtering
        print("\n=== TEST 2: Simple Date Filtering ===")
        
        simple_queries = [
            "SELECT COUNT(*) as TOTAL FROM FFBLOADINGCROP01 WHERE TRANSDATE >= '2020-01-01'",
            "SELECT COUNT(*) as TOTAL FROM FFBLOADINGCROP01 WHERE TRANSDATE <= '2024-12-31'",
            "SELECT COUNT(*) as TOTAL FROM FFBLOADINGCROP01 WHERE TRANSDATE >= '2020-01-01' AND TRANSDATE <= '2024-12-31'",
            "SELECT COUNT(*) as TOTAL FROM FFBLOADINGCROP01 WHERE CAST(TRANSDATE AS DATE) >= '2020-01-01'",
            "SELECT COUNT(*) as TOTAL FROM FFBLOADINGCROP01 WHERE CAST(TRANSDATE AS DATE) >= CAST('2020-01-01' AS DATE)"
        ]
        
        for i, query in enumerate(simple_queries):
            try:
                result = connector.execute_query(query)
                if result and result[0]['rows']:
                    count = result[0]['rows'][0]['TOTAL']
                    print(f"  ✓ Query {i+1}: {count} records")
                else:
                    print(f"  ✗ Query {i+1}: No result")
            except Exception as e:
                print(f"  ✗ Query {i+1}: Error - {e}")
        
        # Test 3: Test GROUP BY with date casting
        print("\n=== TEST 3: GROUP BY Date Casting ===")
        
        group_queries = [
            "SELECT CAST(TRANSDATE AS DATE) as TRANS_DATE, COUNT(*) as TOTAL FROM FFBLOADINGCROP01 WHERE TRANSDATE IS NOT NULL GROUP BY CAST(TRANSDATE AS DATE) ORDER BY TRANS_DATE ROWS 1 TO 3",
            "SELECT TRANSDATE, COUNT(*) as TOTAL FROM FFBLOADINGCROP01 WHERE TRANSDATE IS NOT NULL GROUP BY TRANSDATE ORDER BY TRANSDATE ROWS 1 TO 3"
        ]
        
        for i, query in enumerate(group_queries):
            try:
                result = connector.execute_query(query)
                if result and result[0]['rows']:
                    print(f"  ✓ Group Query {i+1}: {len(result[0]['rows'])} groups")
                    for row in result[0]['rows']:
                        print(f"    {list(row.values())}")
                else:
                    print(f"  ✗ Group Query {i+1}: No result")
            except Exception as e:
                print(f"  ✗ Group Query {i+1}: Error - {e}")
        
        # Test 4: Test SUM and aggregation functions
        print("\n=== TEST 4: Aggregation Functions ===")
        
        agg_queries = [
            "SELECT SUM(BUNCHES) as TOTAL_BUNCHES FROM FFBLOADINGCROP01 WHERE BUNCHES IS NOT NULL",
            "SELECT SUM(LOOSEFRUIT) as TOTAL_LOOSEFRUIT FROM FFBLOADINGCROP01 WHERE LOOSEFRUIT IS NOT NULL",
            "SELECT COUNT(*) as TOTAL, SUM(BUNCHES) as TOTAL_BUNCHES FROM FFBLOADINGCROP01 WHERE TRANSDATE >= '2020-01-01'"
        ]
        
        for i, query in enumerate(agg_queries):
            try:
                result = connector.execute_query(query)
                if result and result[0]['rows']:
                    row = result[0]['rows'][0]
                    print(f"  ✓ Agg Query {i+1}: {row}")
                else:
                    print(f"  ✗ Agg Query {i+1}: No result")
            except Exception as e:
                print(f"  ✗ Agg Query {i+1}: Error - {e}")
        
        # Test 5: Test the exact daily summary query
        print("\n=== TEST 5: Daily Summary Query Debug ===")
        
        daily_query = """SELECT 
            CAST(TRANSDATE AS DATE) as TRANS_DATE, 
            COUNT(*) as TOTAL_TRANSACTIONS, 
            SUM(BUNCHES) as TOTAL_BUNCHES, 
            SUM(LOOSEFRUIT) as TOTAL_LOOSEFRUIT 
            FROM FFBLOADINGCROP01 
            WHERE TRANSDATE >= '2020-01-01' AND TRANSDATE <= '2024-12-31' 
            GROUP BY CAST(TRANSDATE AS DATE) 
            ORDER BY TRANS_DATE 
            ROWS 1 TO 5"""
        
        try:
            daily_result = connector.execute_query(daily_query)
            if daily_result and daily_result[0]['rows']:
                print(f"  ✓ Daily summary works: {len(daily_result[0]['rows'])} days")
                for row in daily_result[0]['rows']:
                    print(f"    {row['TRANS_DATE']}: {row['TOTAL_TRANSACTIONS']} transactions, {row['TOTAL_BUNCHES']} bunches")
            else:
                print("  ✗ Daily summary failed")
        except Exception as e:
            print(f"  ✗ Daily summary error: {e}")
        
        print()
        print('=' * 80)
        print('DATE FILTERING DEBUG COMPLETED')
        print('=' * 80)
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()