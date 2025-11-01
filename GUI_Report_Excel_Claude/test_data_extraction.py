#!/usr/bin/env python3
"""
Test script to verify the corrected data extraction is working properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced
from database_helper import (
    execute_query_with_extraction, 
    get_table_count, 
    get_sample_data,
    normalize_data_row,
    get_date_range_for_table
)

def test_data_extraction():
    """Test the corrected data extraction functionality"""
    
    # Initialize connector
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    connector = FirebirdConnectorEnhanced(db_path)
    
    print("=== Testing Data Extraction ===")
    
    # Test 1: Check FFBSCANNERDATA10 table count
    print("\n1. Testing FFBSCANNERDATA10 table count:")
    count = get_table_count(connector, "FFBSCANNERDATA10")
    print(f"   Total records: {count}")
    
    # Test 2: Get date range
    print("\n2. Testing date range for FFBSCANNERDATA10:")
    date_range = get_date_range_for_table(connector, "FFBSCANNERDATA10", "TRANSDATE")
    print(f"   Date range: {date_range}")
    
    # Test 3: Get sample data with normalization
    print("\n3. Testing sample data extraction:")
    sample_data = get_sample_data(connector, "FFBSCANNERDATA10", limit=3)
    print(f"   Sample records: {len(sample_data)}")
    for i, record in enumerate(sample_data):
        print(f"   Record {i+1}: {record}")
    
    # Test 4: Test employee mapping
    print("\n4. Testing EMP table:")
    emp_count = get_table_count(connector, "EMP")
    print(f"   EMP records: {emp_count}")
    
    emp_sample = get_sample_data(connector, "EMP", limit=2)
    print(f"   EMP sample records: {len(emp_sample)}")
    for i, record in enumerate(emp_sample):
        print(f"   EMP Record {i+1}: {record}")
    
    # Test 5: Test OCFIELD table
    print("\n5. Testing OCFIELD table:")
    ocfield_count = get_table_count(connector, "OCFIELD")
    print(f"   OCFIELD records: {ocfield_count}")
    
    ocfield_sample = get_sample_data(connector, "OCFIELD", limit=2)
    print(f"   OCFIELD sample records: {len(ocfield_sample)}")
    for i, record in enumerate(ocfield_sample):
        print(f"   OCFIELD Record {i+1}: {record}")
    
    # Test 6: Test simple JOIN query
    print("\n6. Testing JOIN query:")
    join_query = """
    SELECT f.SCANUSERID, f.TRANSDATE, o.FIELDNAME
    FROM FFBSCANNERDATA10 f
    LEFT JOIN OCFIELD o ON f.FIELDID = o.ID
    WHERE f.TRANSDATE IS NOT NULL
    LIMIT 3
    """
    
    try:
        join_results = execute_query_with_extraction(connector, join_query)
        print(f"   JOIN results: {len(join_results)} records")
        for i, record in enumerate(join_results):
            normalized = normalize_data_row(record)
            print(f"   JOIN Record {i+1}: {normalized}")
    except Exception as e:
        print(f"   JOIN query error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_data_extraction()