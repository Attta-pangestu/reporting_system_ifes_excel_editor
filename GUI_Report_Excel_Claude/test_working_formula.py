#!/usr/bin/env python3
"""
Test script for pge2b_working_formula.json
Tests all queries in the working formula file
"""

import json
import fdb
from datetime import datetime, timedelta

# Database connection parameters
DB_PATH = r"D:\Gawean Rebinmas\Monitoring Database\Ifes Auto report\excel_method\GUI_Report_Excel_Claude\IFESDB.FDB"
DB_USER = "SYSDBA"
DB_PASSWORD = "masterkey"

def connect_to_database():
    """Connect to Firebird database"""
    try:
        conn = fdb.connect(
            database=DB_PATH,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='UTF8'
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def load_formula(filename):
    """Load formula file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading formula file: {e}")
        return None

def execute_query(conn, query, description=""):
    """Execute a query and return results"""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        cursor.close()
        return results, columns
    except Exception as e:
        print(f"Query failed ({description}): {e}")
        return None, None

def test_working_formula():
    """Test all queries in the working formula"""
    print("=" * 80)
    print("TESTING WORKING FORMULA FILE")
    print("=" * 80)
    
    # Load formula
    formula = load_formula("pge2b_working_formula.json")
    if not formula:
        print("✗ Failed to load formula file")
        return
    
    print(f"✓ Formula loaded: {formula['formula_name']} v{formula['version']}")
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        print("✗ Database connection failed")
        return
    
    print("✓ Database connected")
    
    # Set date parameters
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    month = 1  # January for FFBLOADINGCROP01
    
    date_params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'month': month
    }
    
    print(f"Date range: {date_params['start_date']} to {date_params['end_date']}")
    print(f"Using table: FFBLOADINGCROP{month:02d}")
    print()
    
    # Test each query
    queries = formula.get('queries', {})
    
    for query_name, query_info in queries.items():
        print(f"=== TEST: {query_name.upper()} ===")
        print(f"Description: {query_info.get('description', 'N/A')}")
        
        # Format the SQL query
        sql = query_info['sql'].format(**date_params)
        print(f"SQL: {sql}")
        
        # Execute query
        results, columns = execute_query(conn, sql, query_name)
        
        if results is not None:
            print(f"✓ Success: {len(results)} rows returned")
            if columns:
                print(f"  Columns: {', '.join(columns)}")
            
            # Show sample data for some queries
            if results and len(results) > 0:
                if query_name in ['employee_mapping', 'division_list', 'scanner_users', 'drivers_list', 'vehicles_list']:
                    print(f"  Sample (first 3): {results[:3]}")
                elif query_name in ['total_summary', 'date_range_data', 'bunches_analysis', 'loosefruit_analysis', 'filtered_data_count']:
                    print(f"  Result: {results[0] if results else 'No data'}")
                elif query_name == 'raw_ffb_data':
                    print(f"  Sample record: {results[0] if results else 'No data'}")
            else:
                print("  No data found")
        else:
            print("✗ Query failed")
        
        print()
    
    # Close connection
    conn.close()
    print("=" * 80)
    print("WORKING FORMULA TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_working_formula()