#!/usr/bin/env python3
"""
Test Exact Columns Formula
Comprehensive test of pge2b_exact_columns.json with exact database column names
"""

import json
from firebird_connector_enhanced import FirebirdConnectorEnhanced
from datetime import datetime, timedelta

def main():
    print('=' * 80)
    print('TESTING EXACT COLUMNS FORMULA')
    print('=' * 80)
    
    try:
        connector = FirebirdConnectorEnhanced()
        
        # Load formula file
        with open('pge2b_exact_columns.json', 'r') as f:
            formula = json.load(f)
        
        print(f"✓ Formula loaded: {formula['formula_name']} v{formula['version']}")
        print(f"  Queries: {len(formula['queries'])}")
        
        # Test parameters
        start_date = '2020-01-01'
        end_date = '2024-12-31'
        month = 1  # January
        
        print(f"\nTest parameters:")
        print(f"  Date range: {start_date} to {end_date}")
        print(f"  Month: {month:02d}")
        
        # Test 1: Employee Mapping
        print("\n=== TEST 1: Employee Mapping ===")
        emp_query = formula['queries']['employee_mapping']['sql']
        emp_result = connector.execute_query(emp_query)
        if emp_result and emp_result[0]['rows']:
            print(f"✓ Employee mapping: {len(emp_result[0]['rows'])} employees found")
            # Show sample
            for i, row in enumerate(emp_result[0]['rows'][:3]):
                print(f"  Sample {i+1}: {row['EMPCODE']} - {row['NAME']}")
        else:
            print("✗ Employee mapping: No data found")
        
        # Test 2: Division List
        print("\n=== TEST 2: Division List ===")
        div_query = formula['queries']['division_list']['sql'].format(month=month)
        div_result = connector.execute_query(div_query)
        if div_result and div_result[0]['rows']:
            print(f"✓ Division list: {len(div_result[0]['rows'])} divisions found")
            # Show sample
            for i, row in enumerate(div_result[0]['rows'][:5]):
                print(f"  Division {i+1}: {row['FIELDID']}")
        else:
            print("✗ Division list: No data found")
        
        # Test 3: Raw FFB Data
        print("\n=== TEST 3: Raw FFB Data ===")
        raw_query = formula['queries']['raw_ffb_data']['sql'].format(
            month=month, start_date=start_date, end_date=end_date
        )
        raw_result = connector.execute_query(raw_query)
        if raw_result and raw_result[0]['rows']:
            print(f"✓ Raw FFB data: {len(raw_result[0]['rows'])} records found")
            # Show sample
            sample_row = raw_result[0]['rows'][0]
            print(f"  Sample record:")
            for key, value in sample_row.items():
                print(f"    {key}: {value}")
        else:
            print("✗ Raw FFB data: No data found")
        
        # Test 4: Daily Summary
        print("\n=== TEST 4: Daily Summary ===")
        daily_query = formula['queries']['daily_summary']['sql'].format(
            month=month, start_date=start_date, end_date=end_date
        )
        daily_result = connector.execute_query(daily_query)
        if daily_result and daily_result[0]['rows']:
            print(f"✓ Daily summary: {len(daily_result[0]['rows'])} days found")
            # Show sample
            for i, row in enumerate(daily_result[0]['rows'][:3]):
                print(f"  Day {i+1}: {row['TRANS_DATE']} - {row['TOTAL_TRANSACTIONS']} transactions, {row['TOTAL_BUNCHES']} bunches")
        else:
            print("✗ Daily summary: No data found")
        
        # Test 5: Operator Performance
        print("\n=== TEST 5: Operator Performance ===")
        op_query = formula['queries']['operator_performance']['sql'].format(
            month=month, start_date=start_date, end_date=end_date
        )
        op_result = connector.execute_query(op_query)
        if op_result and op_result[0]['rows']:
            print(f"✓ Operator performance: {len(op_result[0]['rows'])} operators found")
            # Show sample
            for i, row in enumerate(op_result[0]['rows'][:3]):
                name = row['OPERATOR_NAME'] or 'Unknown'
                print(f"  Operator {i+1}: {row['SCANUSERID']} ({name}) - {row['TOTAL_SCANS']} scans, {row['TOTAL_BUNCHES']} bunches")
        else:
            print("✗ Operator performance: No data found")
        
        # Test 6: Field Performance
        print("\n=== TEST 6: Field Performance ===")
        field_query = formula['queries']['field_performance']['sql'].format(
            month=month, start_date=start_date, end_date=end_date
        )
        field_result = connector.execute_query(field_query)
        if field_result and field_result[0]['rows']:
            print(f"✓ Field performance: {len(field_result[0]['rows'])} fields found")
            # Show sample
            for i, row in enumerate(field_result[0]['rows'][:3]):
                print(f"  Field {i+1}: {row['FIELDID']} - {row['TOTAL_TRANSACTIONS']} transactions, {row['TOTAL_BUNCHES']} bunches")
        else:
            print("✗ Field performance: No data found")
        
        # Test 7: Driver Performance
        print("\n=== TEST 7: Driver Performance ===")
        driver_query = formula['queries']['driver_performance']['sql'].format(
            month=month, start_date=start_date, end_date=end_date
        )
        driver_result = connector.execute_query(driver_query)
        if driver_result and driver_result[0]['rows']:
            print(f"✓ Driver performance: {len(driver_result[0]['rows'])} drivers found")
            # Show sample
            for i, row in enumerate(driver_result[0]['rows'][:3]):
                print(f"  Driver {i+1}: {row['DRIVERID']} ({row['DRIVERNAME']}) - {row['TOTAL_TRIPS']} trips, {row['TOTAL_BUNCHES']} bunches")
        else:
            print("✗ Driver performance: No data found")
        
        # Test 8: Simple Count Test
        print("\n=== TEST 8: Simple Count Test ===")
        count_query = f"SELECT COUNT(*) as TOTAL FROM FFBLOADINGCROP{month:02d}"
        count_result = connector.execute_query(count_query)
        if count_result and count_result[0]['rows']:
            total = count_result[0]['rows'][0]['TOTAL']
            print(f"✓ Total records in FFBLOADINGCROP{month:02d}: {total}")
        else:
            print("✗ Count test failed")
        
        # Test 9: Date Range Test
        print("\n=== TEST 9: Date Range Test ===")
        date_query = f"SELECT MIN(TRANSDATE) as MIN_DATE, MAX(TRANSDATE) as MAX_DATE FROM FFBLOADINGCROP{month:02d} WHERE TRANSDATE IS NOT NULL"
        date_result = connector.execute_query(date_query)
        if date_result and date_result[0]['rows']:
            row = date_result[0]['rows'][0]
            print(f"✓ Date range in data: {row['MIN_DATE']} to {row['MAX_DATE']}")
        else:
            print("✗ Date range test failed")
        
        print()
        print('=' * 80)
        print('EXACT COLUMNS FORMULA TEST COMPLETED')
        print('=' * 80)
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()