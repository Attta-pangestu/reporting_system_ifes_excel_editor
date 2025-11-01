#!/usr/bin/env python3
"""
Debug script to investigate JOIN issues between FFBSCANNERDATA10 and OCFIELD
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced
from database_helper import (
    execute_query_with_extraction, 
    get_sample_data,
    normalize_data_row
)

def debug_join_issue():
    """Debug the JOIN issue between tables"""
    
    # Initialize connector
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    connector = FirebirdConnectorEnhanced(db_path)
    
    print("=== Debugging JOIN Issues ===")
    
    # Check FIELDID values in FFBSCANNERDATA10
    print("\n1. Checking FIELDID values in FFBSCANNERDATA10:")
    ffb_sample = get_sample_data(connector, "FFBSCANNERDATA10", limit=5)
    fieldids_ffb = []
    for i, record in enumerate(ffb_sample):
        fieldid = record.get('FIELDID', 'N/A')
        fieldids_ffb.append(fieldid)
        print(f"   Record {i+1} FIELDID: {fieldid}")
    
    # Check ID values in OCFIELD
    print("\n2. Checking ID values in OCFIELD:")
    ocfield_sample = get_sample_data(connector, "OCFIELD", limit=5)
    ids_ocfield = []
    for i, record in enumerate(ocfield_sample):
        id_val = record.get('ID', 'N/A')
        ids_ocfield.append(id_val)
        print(f"   Record {i+1} ID: {id_val}")
        print(f"   Record {i+1} FIELDNAME: {record.get('FIELDNAME', 'N/A')}")
    
    # Check if any FIELDID from FFB matches ID from OCFIELD
    print("\n3. Checking for matches:")
    matches = set(fieldids_ffb) & set(ids_ocfield)
    print(f"   Matching IDs: {matches}")
    
    # Try different JOIN approaches
    print("\n4. Testing different JOIN approaches:")
    
    # Test 1: Simple JOIN with CAST
    print("\n   Test 1: JOIN with CAST to INTEGER")
    query1 = """
    SELECT f.SCANUSERID, f.FIELDID, o.ID, o.FIELDNAME
    FROM FFBSCANNERDATA10 f
    JOIN OCFIELD o ON CAST(f.FIELDID AS INTEGER) = CAST(o.ID AS INTEGER)
    WHERE f.SCANUSERID <= 5
    """
    
    try:
        results1 = execute_query_with_extraction(connector, query1)
        print(f"      Results: {len(results1)} records")
        for record in results1[:2]:
            print(f"      {record}")
    except Exception as e:
        print(f"      Error: {e}")
    
    # Test 2: LEFT JOIN to see unmatched records
    print("\n   Test 2: LEFT JOIN to see unmatched records")
    query2 = """
    SELECT f.SCANUSERID, f.FIELDID, o.ID, o.FIELDNAME
    FROM FFBSCANNERDATA10 f
    LEFT JOIN OCFIELD o ON f.FIELDID = o.ID
    WHERE f.SCANUSERID <= 5
    """
    
    try:
        results2 = execute_query_with_extraction(connector, query2)
        print(f"      Results: {len(results2)} records")
        for record in results2[:2]:
            print(f"      {record}")
    except Exception as e:
        print(f"      Error: {e}")
    
    # Test 3: Check data types
    print("\n   Test 3: Check actual data types and ranges")
    
    # Get unique FIELDID values from FFBSCANNERDATA10
    query3 = "SELECT DISTINCT f.FIELDID FROM FFBSCANNERDATA10 f WHERE f.FIELDID IS NOT NULL ORDER BY f.FIELDID LIMIT 10"
    try:
        fieldid_results = execute_query_with_extraction(connector, query3)
        print(f"      Unique FIELDID values (first 10): {[r['FIELDID'] for r in fieldid_results]}")
    except Exception as e:
        print(f"      Error getting FIELDID values: {e}")
    
    # Get unique ID values from OCFIELD
    query4 = "SELECT DISTINCT o.ID FROM OCFIELD o WHERE o.ID IS NOT NULL ORDER BY o.ID LIMIT 10"
    try:
        id_results = execute_query_with_extraction(connector, query4)
        print(f"      Unique ID values (first 10): {[r['ID'] for r in id_results]}")
    except Exception as e:
        print(f"      Error getting ID values: {e}")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    debug_join_issue()