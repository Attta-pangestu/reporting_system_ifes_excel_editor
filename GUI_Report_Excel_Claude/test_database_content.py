#!/usr/bin/env python3
"""
Test database content to understand why queries return zero rows
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def test_database_content():
    """Test database content to understand the zero-row issue"""
    
    # Use the same database path as the GUI
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    
    print("=== Testing Database Content ===")
    print(f"Database: {db_path}")
    print()
    
    try:
        connector = FirebirdConnectorEnhanced(db_path)
        
        # Test 1: Check available tables
        print("1. Checking available tables...")
        tables_query = "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0 ORDER BY RDB$RELATION_NAME"
        tables_result = connector.execute_query(tables_query)
        
        if tables_result:
            print(f"Found {len(tables_result)} user tables:")
            ffb_tables = []
            emp_tables = []
            
            for table in tables_result:
                table_name = table[0].strip()
                print(f"  - {table_name}")
                
                if 'FFBLOADING' in table_name:
                    ffb_tables.append(table_name)
                elif 'EMP' in table_name:
                    emp_tables.append(table_name)
            
            print(f"\nFFB-related tables: {ffb_tables}")
            print(f"EMP-related tables: {emp_tables}")
        
        # Test 2: Check EMP table
        print("\n2. Testing EMP table...")
        try:
            emp_count_query = "SELECT COUNT(*) FROM EMP"
            emp_count_result = connector.execute_query(emp_count_query)
            
            if emp_count_result:
                count = emp_count_result[0][0]
                print(f"EMP table has {count} records")
                
                if count > 0:
                    # Get sample data
                    emp_sample_query = "SELECT FIRST 3 * FROM EMP"
                    emp_sample_result = connector.execute_query(emp_sample_query)
                    
                    if emp_sample_result:
                        print("Sample EMP data:")
                        for i, row in enumerate(emp_sample_result):
                            print(f"  Row {i+1}: {row}")
                else:
                    print("EMP table is empty!")
            
        except Exception as e:
            print(f"Error testing EMP table: {e}")
        
        # Test 3: Check FFBLOADINGCROP tables
        print("\n3. Testing FFBLOADINGCROP tables...")
        
        # Check for different naming patterns
        test_tables = [
            'FFBLOADINGCROP01', 'FFBLOADINGCROP02', 'FFBLOADINGCROP03',
            'FFBLOADINGCROP10', 'FFBLOADINGCROP11', 'FFBLOADINGCROP12',
            'FFBLOADINGCROP1', 'FFBLOADINGCROP2', 'FFBLOADINGCROP3'
        ]
        
        found_ffb_tables = []
        
        for table_name in test_tables:
            try:
                count_query = f"SELECT COUNT(*) FROM {table_name}"
                count_result = connector.execute_query(count_query)
                
                if count_result:
                    count = count_result[0][0]
                    print(f"{table_name}: {count} records")
                    
                    if count > 0:
                        found_ffb_tables.append(table_name)
                        
                        # Get sample data
                        sample_query = f"SELECT FIRST 1 * FROM {table_name}"
                        sample_result = connector.execute_query(sample_query)
                        
                        if sample_result:
                            print(f"  Sample data: {sample_result[0]}")
                            
                            # Check for date columns
                            if len(sample_result[0]) > 0:
                                # Try to identify date column
                                for i, value in enumerate(sample_result[0]):
                                    if isinstance(value, str) and ('2024' in str(value) or '2025' in str(value)):
                                        print(f"  Possible date in column {i}: {value}")
                
            except Exception as e:
                # Table doesn't exist, skip
                pass
        
        print(f"\nFound FFB tables with data: {found_ffb_tables}")
        
        # Test 4: Check current date and recent data
        print("\n4. Testing date ranges...")
        
        try:
            current_date_query = "SELECT CURRENT_DATE FROM RDB$DATABASE"
            current_date_result = connector.execute_query(current_date_query)
            
            if current_date_result:
                current_date = current_date_result[0][0]
                print(f"Database current date: {current_date}")
        
        except Exception as e:
            print(f"Error getting current date: {e}")
        
        # Test 5: Test the actual queries from the template
        print("\n5. Testing template queries...")
        
        # Test employee mapping query
        try:
            emp_query = "SELECT DISTINCT EMPID, EMPNAME, EMPTYPE, EMPPOSITION, DIVISIONID FROM EMP WHERE EMPSTATUS = 'A' ORDER BY EMPID"
            emp_result = connector.execute_query(emp_query)
            
            if emp_result:
                print(f"Employee mapping query returned {len(emp_result)} records")
                if len(emp_result) > 0:
                    print(f"  Sample: {emp_result[0]}")
            else:
                print("Employee mapping query returned no results")
        
        except Exception as e:
            print(f"Error testing employee mapping query: {e}")
        
        # Test divisions query for current month
        try:
            import datetime
            current_month = datetime.datetime.now().month
            
            divisions_query = f"SELECT DISTINCT DIVISIONID, DIVISIONNAME FROM FFBLOADINGCROP{current_month:02d} WHERE TRANSDATE BETWEEN '2024-10-01' AND '2024-10-31' AND DIVISIONID IS NOT NULL AND DIVISIONNAME IS NOT NULL ORDER BY DIVISIONID"
            divisions_result = connector.execute_query(divisions_query)
            
            if divisions_result:
                print(f"Divisions query (month {current_month:02d}) returned {len(divisions_result)} records")
                if len(divisions_result) > 0:
                    print(f"  Sample: {divisions_result[0]}")
            else:
                print(f"Divisions query (month {current_month:02d}) returned no results")
        
        except Exception as e:
            print(f"Error testing divisions query: {e}")
    
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    test_database_content()