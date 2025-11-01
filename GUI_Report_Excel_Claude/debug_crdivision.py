#!/usr/bin/env python3
"""
Script to investigate CRDIVISION table structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced
from database_helper import (
    execute_query_with_extraction, 
    get_sample_data,
    normalize_data_row,
    get_table_count
)

def debug_crdivision():
    """Debug CRDIVISION table structure"""
    
    # Initialize connector
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    connector = FirebirdConnectorEnhanced(db_path)
    
    print("=== Debugging CRDIVISION Table ===")
    
    # Test 1: Get table count
    print("\n1. CRDIVISION table count:")
    count = get_table_count(connector, "CRDIVISION")
    print(f"   Total records: {count}")
    
    # Test 2: Get raw data
    print("\n2. Raw CRDIVISION query:")
    raw_query = "SELECT FIRST 3 * FROM CRDIVISION"
    
    try:
        raw_result = connector.execute_query(raw_query)
        print(f"   Raw result type: {type(raw_result)}")
        
        if isinstance(raw_result, dict) and 'headers' in raw_result and 'rows' in raw_result:
            print(f"   Headers: {raw_result['headers']}")
            print(f"   Rows count: {len(raw_result['rows'])}")
            
            if raw_result['rows']:
                for i, row in enumerate(raw_result['rows']):
                    print(f"   Row {i+1}: {row}")
                    if isinstance(row, dict):
                        # Look for ID and name-related keys
                        keys = list(row.keys())
                        id_keys = [k for k in keys if 'ID' in k.upper()]
                        name_keys = [k for k in keys if 'NAME' in k.upper() or 'DIV' in k.upper()]
                        
                        print(f"     ID-related keys: {id_keys}")
                        print(f"     Name-related keys: {name_keys}")
                        
                        # Show values for key columns
                        for key in (id_keys + name_keys)[:5]:
                            print(f"     {key}: {row.get(key, 'N/A')}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Use helper functions
    print("\n3. Using helper functions:")
    try:
        sample_data = get_sample_data(connector, "CRDIVISION", limit=3)
        print(f"   Sample records: {len(sample_data)}")
        
        for i, record in enumerate(sample_data):
            print(f"   Record {i+1}: {record}")
            
            # Look for potential field ID and name columns
            keys = list(record.keys())
            potential_id = None
            potential_name = None
            
            # Find ID column
            for key in keys:
                if key.upper() in ['ID', 'DIVID', 'FIELDID', 'DIVISIONID']:
                    potential_id = key
                    break
            
            # Find name column  
            for key in keys:
                if key.upper() in ['NAME', 'DIVNAME', 'FIELDNAME', 'DIVISIONNAME']:
                    potential_name = key
                    break
            
            if potential_id:
                print(f"     Potential ID column: {potential_id} = {record.get(potential_id)}")
            if potential_name:
                print(f"     Potential Name column: {potential_name} = {record.get(potential_name)}")
    
    except Exception as e:
        print(f"   Error with helper functions: {e}")
    
    # Test 4: Test JOIN with FFBSCANNERDATA10
    print("\n4. Testing JOIN with FFBSCANNERDATA10:")
    
    # First, let's see what FIELDID values we have in FFBSCANNERDATA10
    ffb_fieldids_query = "SELECT DISTINCT f.FIELDID FROM FFBSCANNERDATA10 f WHERE f.FIELDID IS NOT NULL ORDER BY f.FIELDID LIMIT 5"
    
    try:
        ffb_fieldids = execute_query_with_extraction(connector, ffb_fieldids_query)
        print(f"   Sample FIELDID values from FFBSCANNERDATA10: {[r['FIELDID'] for r in ffb_fieldids]}")
        
        # Now try to JOIN with CRDIVISION
        join_query = """
        SELECT f.SCANUSERID, f.FIELDID, c.*
        FROM FFBSCANNERDATA10 f
        LEFT JOIN CRDIVISION c ON f.FIELDID = c.ID
        WHERE f.SCANUSERID <= 3
        """
        
        join_results = execute_query_with_extraction(connector, join_query)
        print(f"   JOIN results: {len(join_results)} records")
        
        if join_results:
            for i, record in enumerate(join_results[:2]):
                normalized = normalize_data_row(record)
                print(f"   JOIN Record {i+1}: {normalized}")
        
    except Exception as e:
        print(f"   JOIN test error: {e}")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    debug_crdivision()