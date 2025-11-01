#!/usr/bin/env python3
"""
Get Real Column Names
Use ISQL directly to get exact column names and sample data
"""

import subprocess
import os

def run_isql_command(sql_command):
    """Run ISQL command and return output"""
    isql_path = r"C:\Program Files (x86)\Firebird\Firebird_1_5\bin\isql.exe"
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    
    # Create temporary SQL file
    temp_sql = "temp_query.sql"
    with open(temp_sql, 'w') as f:
        f.write(f"CONNECT '{db_path}';\n")
        f.write(f"{sql_command};\n")
        f.write("EXIT;\n")
    
    try:
        # Run ISQL
        result = subprocess.run([isql_path, "-i", temp_sql], 
                              capture_output=True, text=True, timeout=30)
        
        # Clean up
        if os.path.exists(temp_sql):
            os.remove(temp_sql)
            
        return result.stdout, result.stderr
        
    except Exception as e:
        if os.path.exists(temp_sql):
            os.remove(temp_sql)
        return "", str(e)

def main():
    print('=' * 80)
    print('GETTING REAL COLUMN NAMES FROM DATABASE')
    print('=' * 80)
    
    # Test 1: Get column information from system tables
    print("=== TEST 1: Column Information from System Tables ===")
    
    # Get columns for FFBLOADINGCROP01
    sql = """SELECT 
        r.RDB$FIELD_NAME as COLUMN_NAME,
        f.RDB$FIELD_TYPE as FIELD_TYPE,
        f.RDB$FIELD_LENGTH as FIELD_LENGTH
        FROM RDB$RELATION_FIELDS r
        LEFT JOIN RDB$FIELDS f ON r.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
        WHERE r.RDB$RELATION_NAME = 'FFBLOADINGCROP01'
        ORDER BY r.RDB$FIELD_POSITION"""
    
    stdout, stderr = run_isql_command(sql)
    
    if stdout and "COLUMN_NAME" in stdout:
        print("✓ FFBLOADINGCROP01 columns found:")
        lines = stdout.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('=') and not line.startswith('COLUMN_NAME'):
                parts = line.split()
                if len(parts) >= 1:
                    column_name = parts[0].strip()
                    if column_name and column_name != 'COLUMN_NAME':
                        print(f"  - '{column_name}'")
    else:
        print("✗ Could not get FFBLOADINGCROP01 columns")
        if stderr:
            print(f"Error: {stderr}")
    
    print()
    
    # Test 2: Get sample data to see actual column names
    print("=== TEST 2: Sample Data with Column Names ===")
    
    sql = "SELECT FIRST 1 * FROM FFBLOADINGCROP01"
    stdout, stderr = run_isql_command(sql)
    
    if stdout:
        print("✓ Sample data output:")
        lines = stdout.split('\n')
        for i, line in enumerate(lines[:20]):  # Show first 20 lines
            if line.strip():
                print(f"  {i:2d}: {line}")
    else:
        print("✗ Could not get sample data")
        if stderr:
            print(f"Error: {stderr}")
    
    print()
    
    # Test 3: Get EMP table columns
    print("=== TEST 3: EMP Table Columns ===")
    
    sql = """SELECT 
        r.RDB$FIELD_NAME as COLUMN_NAME,
        f.RDB$FIELD_TYPE as FIELD_TYPE
        FROM RDB$RELATION_FIELDS r
        LEFT JOIN RDB$FIELDS f ON r.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
        WHERE r.RDB$RELATION_NAME = 'EMP'
        ORDER BY r.RDB$FIELD_POSITION"""
    
    stdout, stderr = run_isql_command(sql)
    
    if stdout and "COLUMN_NAME" in stdout:
        print("✓ EMP columns found:")
        lines = stdout.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('=') and not line.startswith('COLUMN_NAME'):
                parts = line.split()
                if len(parts) >= 1:
                    column_name = parts[0].strip()
                    if column_name and column_name != 'COLUMN_NAME':
                        print(f"  - '{column_name}'")
    else:
        print("✗ Could not get EMP columns")
        if stderr:
            print(f"Error: {stderr}")
    
    print()
    
    # Test 4: Get sample EMP data
    print("=== TEST 4: Sample EMP Data ===")
    
    sql = "SELECT FIRST 3 * FROM EMP"
    stdout, stderr = run_isql_command(sql)
    
    if stdout:
        print("✓ Sample EMP data:")
        lines = stdout.split('\n')
        for i, line in enumerate(lines[:15]):  # Show first 15 lines
            if line.strip():
                print(f"  {i:2d}: {line}")
    else:
        print("✗ Could not get EMP sample data")
        if stderr:
            print(f"Error: {stderr}")
    
    print()
    
    # Test 5: Try simple count queries
    print("=== TEST 5: Simple Count Queries ===")
    
    for table in ['FFBLOADINGCROP01', 'EMP']:
        sql = f"SELECT COUNT(*) FROM {table}"
        stdout, stderr = run_isql_command(sql)
        
        if stdout:
            lines = stdout.split('\n')
            for line in lines:
                if line.strip() and line.strip().isdigit():
                    print(f"✓ {table}: {line.strip()} records")
                    break
        else:
            print(f"✗ Could not count {table}")
    
    print()
    print('=' * 80)
    print('REAL COLUMN ANALYSIS COMPLETED')
    print('=' * 80)

if __name__ == '__main__':
    main()