#!/usr/bin/env python3
"""
Script to find field mapping tables
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

def find_field_mapping():
    """Find tables that might contain field mapping"""
    
    # Initialize connector
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    connector = FirebirdConnectorEnhanced(db_path)
    
    print("=== Finding Field Mapping Tables ===")
    
    # Get all table names
    tables_query = "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0"
    tables_result = connector.execute_query(tables_query)
    
    table_names = []
    if isinstance(tables_result, list) and tables_result:
        for item in tables_result:
            if isinstance(item, dict):
                # Handle different possible key formats
                for key in item.keys():
                    if 'RELATION_NAME' in key:
                        table_names.append(item[key].strip())
                        break
            elif isinstance(item, str):
                table_names.append(item.strip())
    
    if not table_names:
        print("Could not get table names")
        return
    
    print(f"Total tables: {len(table_names)}")
    
    # Look for tables that might contain field information
    field_related_tables = []
    for table in table_names:
        if any(keyword in table.upper() for keyword in ['FIELD', 'AREA', 'BLOCK', 'LOCATION', 'PLACE']):
            field_related_tables.append(table)
    
    print(f"Field-related tables: {field_related_tables}")
    
    # Test each field-related table
    for table in field_related_tables:
        print(f"\n=== Testing {table} ===")
        try:
            count = get_table_count(connector, table)
            print(f"Records: {count}")
            
            if count > 0:
                sample_data = get_sample_data(connector, table, limit=3)
                if sample_data:
                    print("Sample data:")
                    for i, record in enumerate(sample_data):
                        print(f"  Record {i+1}: {record}")
                        
                        # Look for ID values in the 800-900 range
                        for key, value in record.items():
                            if isinstance(value, (int, str)):
                                try:
                                    int_val = int(value)
                                    if 800 <= int_val <= 1000:
                                        print(f"    ** Found ID in range: {key} = {int_val}")
                                except:
                                    pass
        except Exception as e:
            print(f"Error testing {table}: {e}")
    
    # Also test some common table names that might exist
    common_tables = ['OCFIELD', 'FIELD', 'FIELDS', 'LOCATION', 'AREA', 'BLOCK', 'ESTATE', 'PLANTATION']
    
    print(f"\n=== Testing Common Table Names ===")
    for table in common_tables:
        try:
            count = get_table_count(connector, table)
            if count > 0:
                print(f"\n{table}: {count} records")
                sample_data = get_sample_data(connector, table, limit=3)
                if sample_data:
                    for i, record in enumerate(sample_data):
                        print(f"  Record {i+1}: {record}")
                        
                        # Look for ID values in the 800-900 range
                        for key, value in record.items():
                            if isinstance(value, (int, str)):
                                try:
                                    int_val = int(value)
                                    if 800 <= int_val <= 1000:
                                        print(f"    ** Found ID in range: {key} = {int_val}")
                                except:
                                    pass
        except:
            pass
    
    # Check if FIELDID values exist in any table as ID
    print(f"\n=== Searching for FIELDID values (893, 849, 867) ===")
    fieldid_values = [893, 849, 867]
    
    # Test a few key tables that might contain these IDs
    test_tables = ['CRDIVISION', 'EMP', 'OCFIELD'] + field_related_tables
    
    for table in test_tables:
        try:
            for fieldid in fieldid_values:
                # Try different possible ID column names
                id_columns = ['ID', 'FIELDID', 'AREAID', 'BLOCKID', 'LOCATIONID']
                
                for id_col in id_columns:
                    try:
                        query = f"SELECT * FROM {table} WHERE {id_col} = {fieldid}"
                        results = execute_query_with_extraction(connector, query)
                        if results:
                            print(f"  Found FIELDID {fieldid} in {table}.{id_col}")
                            print(f"    Record: {results[0]}")
                    except:
                        pass
        except:
            pass
    
    print("\n=== Search Complete ===")

if __name__ == "__main__":
    find_field_mapping()