#!/usr/bin/env python3
"""
Debug script to analyze FFBLOADINGCROP tables structure and data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def analyze_ffb_tables():
    """Analyze FFBLOADINGCROP tables in the database"""
    
    # Connect to database
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    connector = FirebirdConnectorEnhanced(db_path)
    
    print("=== Analyzing FFBLOADINGCROP Tables ===")
    print(f"Database: {db_path}")
    print()
    
    # Check available FFBLOADINGCROP tables
    tables_query = "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE 'FFBLOADINGCROP%' AND RDB$SYSTEM_FLAG = 0"
    
    try:
        tables = connector.execute_query(tables_query)
        print(f"Found {len(tables)} FFBLOADINGCROP tables:")
        
        for table in tables:
            table_name = table[0].strip()
            print(f"\n--- Table: {table_name} ---")
            
            # Check table structure
            structure_query = f"SELECT RDB$FIELD_NAME FROM RDB$RELATION_FIELDS WHERE RDB$RELATION_NAME = '{table_name}' ORDER BY RDB$FIELD_POSITION"
            columns = connector.execute_query(structure_query)
            column_names = [col[0].strip() for col in columns]
            print(f"Columns ({len(column_names)}): {column_names}")
            
            # Check data count
            try:
                count_query = f"SELECT COUNT(*) FROM {table_name}"
                count_result = connector.execute_query(count_query)
                row_count = count_result[0][0] if count_result else 0
                print(f"Row count: {row_count}")
                
                if row_count > 0:
                    # Sample data with date info
                    sample_query = f"SELECT FIRST 3 * FROM {table_name}"
                    sample_data = connector.execute_query(sample_query)
                    print(f"Sample data: {len(sample_data)} rows")
                    
                    # Check date range if TRANSDATE exists
                    if 'TRANSDATE' in column_names:
                        date_query = f"SELECT MIN(TRANSDATE), MAX(TRANSDATE) FROM {table_name}"
                        date_result = connector.execute_query(date_query)
                        if date_result and date_result[0][0]:
                            print(f"Date range: {date_result[0][0]} to {date_result[0][1]}")
                    
                    # Show first row structure
                    if sample_data:
                        print("First row data:")
                        for i, col_name in enumerate(column_names[:10]):  # First 10 columns
                            if i < len(sample_data[0]):
                                print(f"  {col_name}: {sample_data[0][i]}")
                else:
                    print("No data in table")
                    
            except Exception as e:
                print(f"Error checking data: {e}")
    
    except Exception as e:
        print(f"Error querying tables: {e}")
    
    # Also check EMP table
    print("\n=== Checking EMP Table ===")
    try:
        emp_count_query = "SELECT COUNT(*) FROM EMP"
        emp_count = connector.execute_query(emp_count_query)
        print(f"EMP table row count: {emp_count[0][0] if emp_count else 0}")
        
        # EMP structure
        emp_structure_query = "SELECT RDB$FIELD_NAME FROM RDB$RELATION_FIELDS WHERE RDB$RELATION_NAME = 'EMP' ORDER BY RDB$FIELD_POSITION"
        emp_columns = connector.execute_query(emp_structure_query)
        emp_column_names = [col[0].strip() for col in emp_columns]
        print(f"EMP columns: {emp_column_names}")
        
        # Sample EMP data
        if emp_count and emp_count[0][0] > 0:
            emp_sample_query = "SELECT FIRST 3 * FROM EMP"
            emp_sample = connector.execute_query(emp_sample_query)
            print(f"EMP sample data: {len(emp_sample)} rows")
            if emp_sample:
                print("First EMP row:")
                for i, col_name in enumerate(emp_column_names[:5]):
                    if i < len(emp_sample[0]):
                        print(f"  {col_name}: {emp_sample[0][i]}")
        
    except Exception as e:
        print(f"Error checking EMP table: {e}")

if __name__ == "__main__":
    analyze_ffb_tables()