#!/usr/bin/env python3
"""
Debug script to investigate the raw structure of OCFIELD table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced
from database_helper import extract_structured_data

def debug_ocfield_structure():
    """Debug the raw structure of OCFIELD table"""
    
    # Initialize connector
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    connector = FirebirdConnectorEnhanced(db_path)
    
    print("=== Debugging OCFIELD Table Structure ===")
    
    # Test 1: Raw query to OCFIELD
    print("\n1. Raw query to OCFIELD:")
    raw_query = "SELECT FIRST 3 * FROM OCFIELD"
    
    try:
        raw_result = connector.execute_query(raw_query)
        print(f"   Raw result type: {type(raw_result)}")
        print(f"   Raw result: {raw_result}")
        
        if isinstance(raw_result, dict) and 'headers' in raw_result and 'rows' in raw_result:
            print(f"   Headers: {raw_result['headers']}")
            print(f"   Number of rows: {len(raw_result['rows'])}")
            if raw_result['rows']:
                print(f"   First row: {raw_result['rows'][0]}")
                print(f"   First row type: {type(raw_result['rows'][0])}")
        
        # Extract using our helper
        extracted = extract_structured_data(raw_result)
        print(f"   Extracted data: {len(extracted)} records")
        if extracted:
            print(f"   First extracted record: {extracted[0]}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Check table info
    print("\n2. Getting table info for OCFIELD:")
    try:
        table_info = connector.get_table_info("OCFIELD")
        print(f"   Table info: {table_info}")
    except Exception as e:
        print(f"   Error getting table info: {e}")
    
    # Test 3: Try different column names
    print("\n3. Testing different column access methods:")
    
    test_queries = [
        "SELECT ID, FIELDNAME FROM OCFIELD WHERE ID IS NOT NULL LIMIT 3",
        "SELECT * FROM OCFIELD WHERE ROWNUM <= 3",
        "SELECT FIRST 3 ID, FIELDNAME FROM OCFIELD",
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n   Test Query {i+1}: {query}")
        try:
            result = connector.execute_query(query)
            extracted = extract_structured_data(result)
            print(f"      Results: {len(extracted)} records")
            if extracted:
                print(f"      First record: {extracted[0]}")
        except Exception as e:
            print(f"      Error: {e}")
    
    # Test 4: Check if OCFIELD exists and has data
    print("\n4. Checking OCFIELD existence and data:")
    try:
        count_query = "SELECT COUNT(*) as RECORD_COUNT FROM OCFIELD"
        count_result = connector.execute_query(count_query)
        count_extracted = extract_structured_data(count_result)
        print(f"   OCFIELD record count: {count_extracted}")
    except Exception as e:
        print(f"   Error counting OCFIELD: {e}")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    debug_ocfield_structure()