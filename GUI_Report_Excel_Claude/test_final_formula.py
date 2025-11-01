#!/usr/bin/env python3
"""
Test Final Formula File
Comprehensive testing of the final corrected formula file
"""

from dynamic_formula_engine_enhanced import EnhancedDynamicFormulaEngine
from firebird_connector_enhanced import FirebirdConnectorEnhanced
import json
from datetime import datetime, timedelta

def main():
    print('=' * 80)
    print('TESTING FINAL CORRECTED FORMULA FILE')
    print('=' * 80)
    
    try:
        # Initialize the enhanced formula engine with final file
        engine = EnhancedDynamicFormulaEngine('pge2b_final_formula.json')
        
        print("✓ Final formula file loaded successfully")
        
        # Test parameters - use dates that should have data
        parameters = {
            'start_date': '2020-01-01',  # Use dates from the sample data we saw
            'end_date': '2020-01-31',
            'estate_name': 'PGE 2B',
            'estate_code': 'PGE_2B',
            'month': 1  # January data (FFBLOADINGCROP01)
        }
        
        print(f"Test parameters: {parameters}")
        print()
        
        # Test individual queries with exact column names
        connector = FirebirdConnectorEnhanced()
        
        # Test 1: Employee mapping with exact column names
        print("=== TEST 1: Employee Mapping ===")
        try:
            emp_query = 'SELECT DISTINCT "ID EMPCODE" as EMPID, "ID NAME" as EMPNAME FROM EMP WHERE "ID EMPCODE" IS NOT NULL AND "ID NAME" IS NOT NULL ROWS 1 TO 5'
            emp_result = connector.execute_query(emp_query)
            if emp_result and emp_result[0]['rows']:
                print(f"✓ Employee mapping: {len(emp_result[0]['rows'])} sample employees found")
                for emp in emp_result[0]['rows']:
                    empid = emp.get('EMPID', 'N/A')
                    empname = emp.get('EMPNAME', 'N/A')
                    print(f"  - {empid}: {empname}")
            else:
                print("✗ Employee mapping: No data found")
        except Exception as e:
            print(f"✗ Employee mapping failed: {e}")
        
        print()
        
        # Test 2: FFB Loading Data with exact column names
        print("=== TEST 2: FFB Loading Data ===")
        try:
            ffb_query = '''SELECT 
                "ID   SCANUSE" as SCANID, 
                "ID         O" as OPERATORID, 
                "ID VEHICLECO" as VEHICLEID, 
                "EID      FIEL" as FIELDID, 
                "ID      BUNC" as BUNCHES, 
                "ES   LOOSEFR" as LOOSEFRUIT, 
                "DATE PROCESSFL" as PROCESS_DATE 
                FROM FFBLOADINGCROP01 
                WHERE "DATE PROCESSFL" BETWEEN '2020-01-01' AND '2020-01-31'
                ORDER BY "ID   SCANUSE" 
                ROWS 1 TO 5'''
            
            ffb_result = connector.execute_query(ffb_query)
            if ffb_result and ffb_result[0]['rows']:
                print(f"✓ FFB Loading data: {len(ffb_result[0]['rows'])} sample records found")
                for row in ffb_result[0]['rows']:
                    scanid = row.get('SCANID', 'N/A')
                    bunches = row.get('BUNCHES', 'N/A')
                    process_date = row.get('PROCESS_DATE', 'N/A')
                    print(f"  - Scan: {scanid}, Bunches: {bunches}, Date: {process_date}")
            else:
                print("✗ FFB Loading data: No data in date range")
                
                # Check total records
                count_query = 'SELECT COUNT(*) as TOTAL FROM FFBLOADINGCROP01'
                count_result = connector.execute_query(count_query)
                if count_result and count_result[0]['rows']:
                    total = count_result[0]['rows'][0]['TOTAL']
                    print(f"  Total records in FFBLOADINGCROP01: {total}")
                    
        except Exception as e:
            print(f"✗ FFB Loading data failed: {e}")
        
        print()
        
        # Test 3: Daily Summary Query
        print("=== TEST 3: Daily Summary ===")
        try:
            daily_query = '''SELECT 
                "DATE PROCESSFL" as PROCESS_DATE, 
                COUNT(*) as TOTAL_TRANSACTIONS, 
                SUM("ID      BUNC") as TOTAL_BUNCHES, 
                SUM("ES   LOOSEFR") as TOTAL_LOOSEFRUIT 
                FROM FFBLOADINGCROP01 
                WHERE "DATE PROCESSFL" BETWEEN '2020-01-01' AND '2020-01-31' 
                GROUP BY "DATE PROCESSFL" 
                ORDER BY "DATE PROCESSFL"
                ROWS 1 TO 5'''
            
            daily_result = connector.execute_query(daily_query)
            if daily_result and daily_result[0]['rows']:
                print(f"✓ Daily summary: {len(daily_result[0]['rows'])} days found")
                for row in daily_result[0]['rows']:
                    date = row.get('PROCESS_DATE', 'N/A')
                    trans = row.get('TOTAL_TRANSACTIONS', 'N/A')
                    bunches = row.get('TOTAL_BUNCHES', 'N/A')
                    print(f"  - {date}: {trans} transactions, {bunches} bunches")
            else:
                print("✗ Daily summary: No data in date range")
        except Exception as e:
            print(f"✗ Daily summary failed: {e}")
        
        print()
        
        # Test 4: Operator Performance Query
        print("=== TEST 4: Operator Performance ===")
        try:
            operator_query = '''SELECT 
                f."ID         O" as OPERATORID, 
                e."ID NAME" as OPERATOR_NAME, 
                COUNT(*) as TOTAL_TRANSACTIONS, 
                SUM(f."ID      BUNC") as TOTAL_BUNCHES 
                FROM FFBLOADINGCROP01 f 
                LEFT JOIN EMP e ON f."ID         O" = e."ID EMPCODE" 
                WHERE f."DATE PROCESSFL" BETWEEN '2020-01-01' AND '2020-01-31' 
                GROUP BY f."ID         O", e."ID NAME" 
                ORDER BY TOTAL_BUNCHES DESC
                ROWS 1 TO 5'''
            
            operator_result = connector.execute_query(operator_query)
            if operator_result and operator_result[0]['rows']:
                print(f"✓ Operator performance: {len(operator_result[0]['rows'])} operators found")
                for row in operator_result[0]['rows']:
                    op_id = row.get('OPERATORID', 'N/A')
                    op_name = row.get('OPERATOR_NAME', 'N/A')
                    bunches = row.get('TOTAL_BUNCHES', 'N/A')
                    print(f"  - {op_id} ({op_name}): {bunches} bunches")
            else:
                print("✗ Operator performance: No data found")
        except Exception as e:
            print(f"✗ Operator performance failed: {e}")
        
        print()
        
        # Test 5: Check date range in data
        print("=== TEST 5: Date Range Analysis ===")
        try:
            date_range_query = '''SELECT 
                MIN("DATE PROCESSFL") as MIN_DATE, 
                MAX("DATE PROCESSFL") as MAX_DATE, 
                COUNT(*) as TOTAL_RECORDS 
                FROM FFBLOADINGCROP01'''
            
            date_result = connector.execute_query(date_range_query)
            if date_result and date_result[0]['rows']:
                date_info = date_result[0]['rows'][0]
                min_date = date_info.get('MIN_DATE', 'N/A')
                max_date = date_info.get('MAX_DATE', 'N/A')
                total = date_info.get('TOTAL_RECORDS', 'N/A')
                print(f"✓ Date range analysis:")
                print(f"  - Date range: {min_date} to {max_date}")
                print(f"  - Total records: {total}")
                
                # Suggest better test dates
                if min_date and max_date:
                    print(f"  - Suggested test dates: {min_date} to {max_date}")
            else:
                print("✗ Date range analysis: No data found")
        except Exception as e:
            print(f"✗ Date range analysis failed: {e}")
        
        print()
        print('=' * 80)
        print('INDIVIDUAL QUERY TESTS COMPLETED')
        print('=' * 80)
        
        # Test 6: Test with better date range if available
        print("=== TEST 6: Test with Data Date Range ===")
        try:
            # Use the actual date range from the data
            better_params = {
                'start_date': '2020-01-02',  # From the sample data we saw
                'end_date': '2020-01-03',
                'estate_name': 'PGE 2B',
                'estate_code': 'PGE_2B',
                'month': 1
            }
            
            print(f"Testing with better parameters: {better_params}")
            
            # Test the raw FFB data query from the formula
            raw_query = '''SELECT 
                "ID   SCANUSE" as SCANID, 
                "ID         O" as OPERATORID, 
                "ID VEHICLECO" as VEHICLEID, 
                "EID      FIEL" as FIELDID, 
                "ID      BUNC" as BUNCHES, 
                "ES   LOOSEFR" as LOOSEFRUIT, 
                "IT TRANSNO" as TRANSNO, 
                "FFBTRANSN" as FFBTRANSNO, 
                "TRANSSTA" as TRANSSTATUS, 
                "US TRANSDA" as TRANSDATE, 
                "E     TRANS" as TRANSTIME, 
                "IME" as TIME_FIELD, 
                "UPLOADDATETIME LASTUSER" as UPLOAD_DATETIME, 
                "LASTUPDATED RECORDTAG" as LAST_UPDATED, 
                "DRIVERNAM" as DRIVER_NAME, 
                "DRIVE" as DRIVER_FULL, 
                "ID HARVESTIN" as HARVEST_ID, 
                "DATE PROCESSFL" as PROCESS_DATE, 
                "G" as STATUS_FLAG 
                FROM FFBLOADINGCROP01 
                WHERE "DATE PROCESSFL" BETWEEN '2020-01-02' AND '2020-01-03' 
                ORDER BY "DATE PROCESSFL", "ID   SCANUSE"
                ROWS 1 TO 3'''
            
            raw_result = connector.execute_query(raw_query)
            if raw_result and raw_result[0]['rows']:
                print(f"✓ Raw FFB query: {len(raw_result[0]['rows'])} records found")
                for i, row in enumerate(raw_result[0]['rows']):
                    print(f"  Record {i+1}:")
                    print(f"    - SCANID: {row.get('SCANID')}")
                    print(f"    - BUNCHES: {row.get('BUNCHES')}")
                    print(f"    - LOOSEFRUIT: {row.get('LOOSEFRUIT')}")
                    print(f"    - PROCESS_DATE: {row.get('PROCESS_DATE')}")
                    print(f"    - DRIVER_NAME: {row.get('DRIVER_NAME')}")
            else:
                print("✗ Raw FFB query: No data found")
                
        except Exception as e:
            print(f"✗ Better date range test failed: {e}")
        
        print()
        print('=' * 80)
        print('FINAL FORMULA TEST COMPLETED')
        print('=' * 80)
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()