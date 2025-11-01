#!/usr/bin/env python3
"""
Test Fixed Formula File
Tests the corrected formula file with actual database structure
"""

from dynamic_formula_engine_enhanced import EnhancedDynamicFormulaEngine
from firebird_connector_enhanced import FirebirdConnectorEnhanced
import json
from datetime import datetime, timedelta

def main():
    print('=' * 80)
    print('TESTING FIXED FORMULA FILE')
    print('=' * 80)
    
    try:
        # Initialize the enhanced formula engine with fixed file
        engine = EnhancedDynamicFormulaEngine('pge2b_fixed_formula.json')
        
        print("✓ Formula file loaded successfully")
        
        # Test parameters
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        parameters = {
            'start_date': start_date,
            'end_date': end_date,
            'estate_name': 'PGE 2B',
            'estate_code': 'PGE_2B',
            'month': 10  # October data
        }
        
        print(f"Test parameters: {parameters}")
        print()
        
        # Test individual queries
        connector = FirebirdConnectorEnhanced()
        
        # Test 1: Employee mapping
        print("=== TEST 1: Employee Mapping ===")
        try:
            emp_query = 'SELECT DISTINCT "ID EMPCODE" as EMPID, "ID NAME" as EMPNAME FROM EMP WHERE "ID EMPCODE" IS NOT NULL'
            emp_result = connector.execute_query(emp_query)
            if emp_result and emp_result[0]['rows']:
                print(f"✓ Employee mapping: {len(emp_result[0]['rows'])} employees found")
                # Show sample
                sample_emp = emp_result[0]['rows'][:3]
                for emp in sample_emp:
                    print(f"  - {emp.get('EMPID', 'N/A')}: {emp.get('EMPNAME', 'N/A')}")
            else:
                print("✗ Employee mapping: No data found")
        except Exception as e:
            print(f"✗ Employee mapping failed: {e}")
        
        print()
        
        # Test 2: FFB Loading Data
        print("=== TEST 2: FFB Loading Data ===")
        try:
            ffb_query = f'''SELECT 
                "ID   SCANUSE" as SCANID, 
                "ID         O" as OPERATORID, 
                "ID VEHICLECO" as VEHICLEID, 
                "EID      FIEL" as FIELDID, 
                "ID      BUNC" as BUNCHES, 
                "ES   LOOSEFR" as LOOSEFRUIT, 
                "E     TRANS" as TRANSDATE 
                FROM FFBLOADINGCROP10 
                WHERE "E     TRANS" BETWEEN '{start_date}' AND '{end_date}'
                ORDER BY "ID   SCANUSE" 
                ROWS 1 TO 5'''
            
            ffb_result = connector.execute_query(ffb_query)
            if ffb_result and ffb_result[0]['rows']:
                print(f"✓ FFB Loading data: {len(ffb_result[0]['rows'])} sample records found")
                # Show sample
                for row in ffb_result[0]['rows']:
                    print(f"  - Scan: {row.get('SCANID')}, Bunches: {row.get('BUNCHES')}, Date: {row.get('TRANSDATE')}")
            else:
                print("✗ FFB Loading data: No data in date range")
                
                # Try without date filter
                simple_query = 'SELECT COUNT(*) as TOTAL FROM FFBLOADINGCROP10'
                simple_result = connector.execute_query(simple_query)
                if simple_result and simple_result[0]['rows']:
                    total = simple_result[0]['rows'][0]['TOTAL']
                    print(f"  Total records in FFBLOADINGCROP10: {total}")
                    
                    # Check date range in table
                    date_query = 'SELECT MIN("E     TRANS") as MIN_DATE, MAX("E     TRANS") as MAX_DATE FROM FFBLOADINGCROP10'
                    date_result = connector.execute_query(date_query)
                    if date_result and date_result[0]['rows']:
                        date_info = date_result[0]['rows'][0]
                        print(f"  Date range in table: {date_info.get('MIN_DATE')} to {date_info.get('MAX_DATE')}")
                        
        except Exception as e:
            print(f"✗ FFB Loading data failed: {e}")
        
        print()
        
        # Test 3: Daily Performance
        print("=== TEST 3: Daily Performance ===")
        try:
            daily_query = f'''SELECT 
                "E     TRANS" as TRANS_DATE, 
                COUNT(*) as TOTAL_TRANSACTIONS, 
                SUM("ID      BUNC") as TOTAL_BUNCHES, 
                SUM("ES   LOOSEFR") as TOTAL_LOOSEFRUIT 
                FROM FFBLOADINGCROP10 
                WHERE "E     TRANS" BETWEEN '{start_date}' AND '{end_date}' 
                GROUP BY "E     TRANS" 
                ORDER BY "E     TRANS"
                ROWS 1 TO 5'''
            
            daily_result = connector.execute_query(daily_query)
            if daily_result and daily_result[0]['rows']:
                print(f"✓ Daily performance: {len(daily_result[0]['rows'])} days found")
                for row in daily_result[0]['rows']:
                    print(f"  - {row.get('TRANS_DATE')}: {row.get('TOTAL_TRANSACTIONS')} trans, {row.get('TOTAL_BUNCHES')} bunches")
            else:
                print("✗ Daily performance: No data in date range")
        except Exception as e:
            print(f"✗ Daily performance failed: {e}")
        
        print()
        
        # Test 4: Use the formula engine
        print("=== TEST 4: Formula Engine Processing ===")
        try:
            # Process with the engine
            result = engine.process_template(parameters)
            
            if result and 'success' in result and result['success']:
                print("✓ Formula engine processing successful")
                
                # Show extracted data summary
                if 'extracted_data' in result:
                    extracted = result['extracted_data']
                    print(f"  Queries executed: {len(extracted)}")
                    
                    for query_name, data in extracted.items():
                        if isinstance(data, list):
                            print(f"  - {query_name}: {len(data)} records")
                        else:
                            print(f"  - {query_name}: {type(data).__name__}")
                
                # Show calculated variables
                if 'calculated_variables' in result:
                    variables = result['calculated_variables']
                    print(f"  Variables calculated: {len(variables)}")
                    
                    key_vars = ['total_transactions', 'total_bunches', 'total_loosefruit']
                    for var in key_vars:
                        if var in variables:
                            print(f"  - {var}: {variables[var]}")
                            
            else:
                print("✗ Formula engine processing failed")
                if 'error' in result:
                    print(f"  Error: {result['error']}")
                    
        except Exception as e:
            print(f"✗ Formula engine processing failed: {e}")
        
        print()
        print('=' * 80)
        print('TEST COMPLETED')
        print('=' * 80)
        
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == '__main__':
    main()