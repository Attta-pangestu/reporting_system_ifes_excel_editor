#!/usr/bin/env python3
"""
Debug script to examine the raw headers and data structure of OCFIELD table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def debug_ocfield_raw():
    """Debug the raw headers and data structure of OCFIELD table"""
    
    # Initialize connector
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    connector = FirebirdConnectorEnhanced(db_path)
    
    print("=== Debugging OCFIELD Raw Structure ===")
    
    # Get raw data from OCFIELD
    print("\n1. Raw OCFIELD query:")
    raw_query = "SELECT FIRST 2 * FROM OCFIELD"
    
    try:
        raw_result = connector.execute_query(raw_query)
        print(f"   Raw result type: {type(raw_result)}")
        
        if isinstance(raw_result, dict):
            if 'headers' in raw_result:
                print(f"   Headers: {raw_result['headers']}")
                print(f"   Headers type: {type(raw_result['headers'])}")
                print(f"   Headers length: {len(raw_result['headers'])}")
            
            if 'rows' in raw_result:
                print(f"   Rows count: {len(raw_result['rows'])}")
                if raw_result['rows']:
                    print(f"   First row type: {type(raw_result['rows'][0])}")
                    print(f"   First row: {raw_result['rows'][0]}")
                    
                    # If it's a dict, show keys
                    if isinstance(raw_result['rows'][0], dict):
                        print(f"   First row keys: {list(raw_result['rows'][0].keys())}")
                        
                        # Look for ID and FIELDNAME related keys
                        keys = list(raw_result['rows'][0].keys())
                        id_keys = [k for k in keys if 'ID' in k.upper()]
                        field_keys = [k for k in keys if 'FIELD' in k.upper() or 'NAME' in k.upper()]
                        
                        print(f"   Keys containing 'ID': {id_keys}")
                        print(f"   Keys containing 'FIELD' or 'NAME': {field_keys}")
                        
                        # Show values for potential ID and FIELDNAME columns
                        for key in id_keys[:3]:  # Show first 3 ID-related keys
                            print(f"   {key}: {raw_result['rows'][0].get(key, 'N/A')}")
                        
                        for key in field_keys[:3]:  # Show first 3 field-related keys
                            print(f"   {key}: {raw_result['rows'][0].get(key, 'N/A')}")
                    
                    if len(raw_result['rows']) > 1:
                        print(f"   Second row: {raw_result['rows'][1]}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test with different table names that might be related
    print("\n2. Testing related table names:")
    related_tables = ["FIELD", "FIELDS", "DIVISION", "DIVISIONS", "CRDIVISION"]
    
    for table in related_tables:
        try:
            count_query = f"SELECT COUNT(*) as COUNT FROM {table}"
            count_result = connector.execute_query(count_query)
            if isinstance(count_result, dict) and 'rows' in count_result and count_result['rows']:
                count = count_result['rows'][0].get('COUNT', 0)
                print(f"   {table}: {count} records")
                
                if count > 0:
                    # Get sample data
                    sample_query = f"SELECT FIRST 1 * FROM {table}"
                    sample_result = connector.execute_query(sample_query)
                    if isinstance(sample_result, dict) and 'rows' in sample_result and sample_result['rows']:
                        sample_keys = list(sample_result['rows'][0].keys()) if isinstance(sample_result['rows'][0], dict) else []
                        print(f"     Sample keys: {sample_keys[:10]}")  # Show first 10 keys
        except Exception as e:
            print(f"   {table}: Error - {e}")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    debug_ocfield_raw()