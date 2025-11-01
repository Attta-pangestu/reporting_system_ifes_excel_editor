#!/usr/bin/env python3
"""
Test Corrected Final Formula
Test the final corrected formula file with exact column names
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced
import json

def main():
    print('=' * 80)
    print('TESTING FINAL CORRECTED FORMULA WITH EXACT COLUMN NAMES')
    print('=' * 80)
    
    try:
        connector = FirebirdConnectorEnhanced()
        
        # Test 1: Employee mapping with exact column names
        print("=== TEST 1: Employee Mapping ===")
        try:
            emp_query = 'SELECT DISTINCT EMPCODE, NAME FROM EMP WHERE EMPCODE IS NOT NULL AND NAME IS NOT NULL ROWS 1 TO 5'
            emp_result = connector.execute_query(emp_query)
            if emp_result and emp_result[0]['rows']:
                print(f"✓ Employee mapping: {len(emp_result[0]['rows'])} employees found")
                for emp in emp_result[0]['rows']:
                    empcode = emp.get('EMPCODE', 'N/A')
                    name = emp.get('NAME', 'N/A')
                    print(f"  - {empcode}: {name}")
            else:
                print("✗ Employee mapping: No data found")
        except Exception as e:
            print(f"✗ Employee mapping failed: {e}")
        
        print()
        
        # Test 2: FFB Loading Data with exact column names
        print("=== TEST 2: FFB Loading Data ===")
        try:
            ffb_query = '''SELECT 
                SCANUSE, 
                EMPCODE, 
                TRANSDATE, 
                PROCESSDATE, 
                BUNCHES, 
                LOOSEFRUIT 
                FROM FFBLOADINGCROP01 
                ORDER BY SCANUSE 
                ROWS 1 TO 5'''
            
            ffb_result = connector.execute_query(ffb_query)
            if ffb_result and ffb_result[0]['rows']:
                print(f"✓ FFB Loading data: {len(ffb_result[0]['rows'])} records found")
                for row in ffb_result[0]['rows']:
                    scanuse = row.get('SCANUSE', 'N/A')
                    empcode = row.get('EMPCODE', 'N/A')
                    bunches = row.get('BUNCHES', 'N/A')
                    transdate = row.get('TRANSDATE', 'N/A')
                    print(f"  - Scan: {scanuse}, Emp: {empcode}, Bunches: {bunches}, Date: {transdate}")
            else:
                print("✗ FFB Loading data: No data found")
                
        except Exception as e:
            print(f"✗ FFB Loading data failed: {e}")
        
        print()
        
        # Test 3: Date range analysis
        print("=== TEST 3: Date Range Analysis ===")
        try:
            date_query = '''SELECT 
                MIN(TRANSDATE) as MIN_DATE, 
                MAX(TRANSDATE) as MAX_DATE, 
                COUNT(*) as TOTAL_RECORDS 
                FROM FFBLOADINGCROP01 
                WHERE TRANSDATE IS NOT NULL'''
            
            date_result = connector.execute_query(date_query)
            if date_result and date_result[0]['rows']:
                date_info = date_result[0]['rows'][0]
                min_date = date_info.get('MIN_DATE', 'N/A')
                max_date = date_info.get('MAX_DATE', 'N/A')
                total = date_info.get('TOTAL_RECORDS', 'N/A')
                print(f"✓ Date range analysis:")
                print(f"  - Date range: {min_date} to {max_date}")
                print(f"  - Total records with dates: {total}")
                
                # Test with actual date range
                if min_date and max_date and min_date != 'N/A':
                    print(f"\n=== TEST 4: Query with Actual Date Range ===")
                    actual_query = f'''SELECT 
                        TRANSDATE, 
                        COUNT(*) as DAILY_COUNT, 
                        SUM(BUNCHES) as DAILY_BUNCHES 
                        FROM FFBLOADINGCROP01 
                        WHERE TRANSDATE BETWEEN '{min_date}' AND '{max_date}' 
                        GROUP BY TRANSDATE 
                        ORDER BY TRANSDATE 
                        ROWS 1 TO 5'''
                    
                    actual_result = connector.execute_query(actual_query)
                    if actual_result and actual_result[0]['rows']:
                        print(f"✓ Daily summary: {len(actual_result[0]['rows'])} days found")
                        for row in actual_result[0]['rows']:
                            date = row.get('TRANSDATE', 'N/A')
                            count = row.get('DAILY_COUNT', 'N/A')
                            bunches = row.get('DAILY_BUNCHES', 'N/A')
                            print(f"  - {date}: {count} transactions, {bunches} bunches")
                    else:
                        print("✗ Daily summary: No data found")
            else:
                print("✗ Date range analysis: No data found")
        except Exception as e:
            print(f"✗ Date range analysis failed: {e}")
        
        print()
        
        # Test 5: Operator performance with JOIN
        print("=== TEST 5: Operator Performance with JOIN ===")
        try:
            join_query = '''SELECT 
                f.EMPCODE, 
                e.NAME as OPERATOR_NAME, 
                COUNT(*) as TOTAL_TRANSACTIONS, 
                SUM(f.BUNCHES) as TOTAL_BUNCHES 
                FROM FFBLOADINGCROP01 f 
                LEFT JOIN EMP e ON f.EMPCODE = e.EMPCODE 
                WHERE f.EMPCODE IS NOT NULL 
                GROUP BY f.EMPCODE, e.NAME 
                ORDER BY TOTAL_BUNCHES DESC 
                ROWS 1 TO 5'''
            
            join_result = connector.execute_query(join_query)
            if join_result and join_result[0]['rows']:
                print(f"✓ Operator performance: {len(join_result[0]['rows'])} operators found")
                for row in join_result[0]['rows']:
                    empcode = row.get('EMPCODE', 'N/A')
                    name = row.get('OPERATOR_NAME', 'N/A')
                    bunches = row.get('TOTAL_BUNCHES', 'N/A')
                    transactions = row.get('TOTAL_TRANSACTIONS', 'N/A')
                    print(f"  - {empcode} ({name}): {bunches} bunches in {transactions} trips")
            else:
                print("✗ Operator performance: No data found")
        except Exception as e:
            print(f"✗ Operator performance failed: {e}")
        
        print()
        
        # Test 6: Load and validate formula file
        print("=== TEST 6: Formula File Validation ===")
        try:
            with open('pge2b_corrected_final.json', 'r') as f:
                formula = json.load(f)
            
            print("✓ Formula file loaded successfully")
            print(f"  - Formula name: {formula.get('formula_name', 'N/A')}")
            print(f"  - Version: {formula.get('version', 'N/A')}")
            print(f"  - Number of queries: {len(formula.get('queries', {}))}")
            
            # Test a sample query from the formula
            sample_query_key = 'employee_mapping'
            if sample_query_key in formula['queries']:
                sample_sql = formula['queries'][sample_query_key]['sql']
                print(f"\n  Testing sample query '{sample_query_key}':")
                print(f"  SQL: {sample_sql}")
                
                sample_result = connector.execute_query(sample_sql)
                if sample_result and sample_result[0]['rows']:
                    print(f"  ✓ Sample query works: {len(sample_result[0]['rows'])} results")
                else:
                    print(f"  ✗ Sample query failed: No results")
            
        except Exception as e:
            print(f"✗ Formula file validation failed: {e}")
        
        print()
        print('=' * 80)
        print('FINAL CORRECTED FORMULA TEST COMPLETED')
        print('=' * 80)
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()