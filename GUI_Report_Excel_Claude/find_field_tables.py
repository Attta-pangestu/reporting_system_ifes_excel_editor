#!/usr/bin/env python3
"""
Script to find all tables that might contain field information
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def find_field_tables():
    """Find all tables that might contain field information"""
    
    # Initialize connector
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    connector = FirebirdConnectorEnhanced(db_path)
    
    print("=== Finding Field-Related Tables ===")
    
    # Get all table names
    print("\n1. Getting all table names:")
    try:
        tables_query = """
        SELECT RDB$RELATION_NAME 
        FROM RDB$RELATIONS 
        WHERE RDB$VIEW_BLR IS NULL 
        AND (RDB$SYSTEM_FLAG IS NULL OR RDB$SYSTEM_FLAG = 0)
        ORDER BY RDB$RELATION_NAME
        """
        
        tables_result = connector.execute_query(tables_query)
        print(f"   Tables query result type: {type(tables_result)}")
        print(f"   Tables query result: {tables_result}")
        
        if isinstance(tables_result, list):
            print(f"   Found {len(tables_result)} tables")
            
            # Look for field-related tables
            field_related = []
            for table_name in tables_result:
                if isinstance(table_name, str):
                    name = table_name.strip()
                elif isinstance(table_name, dict) and 'RDB$RELATION_NAME' in table_name:
                    name = table_name['RDB$RELATION_NAME'].strip()
                else:
                    continue
                
                if any(keyword in name.upper() for keyword in ['FIELD', 'DIVISION', 'AREA', 'BLOCK', 'SECTOR']):
                    field_related.append(name)
            
            print(f"   Field-related tables: {field_related}")
            
            # Test each field-related table
            print("\n2. Testing field-related tables:")
            for table in field_related:
                print(f"\n   Testing table: {table}")
                try:
                    # Count records
                    count_query = f"SELECT COUNT(*) as COUNT FROM {table}"
                    count_result = connector.execute_query(count_query)
                    
                    if isinstance(count_result, dict) and 'rows' in count_result:
                        count = count_result['rows'][0].get('COUNT', 0) if count_result['rows'] else 0
                    elif isinstance(count_result, list) and count_result:
                        count = count_result[0].get('COUNT', 0) if isinstance(count_result[0], dict) else 0
                    else:
                        count = 0
                    
                    print(f"     Records: {count}")
                    
                    if count > 0:
                        # Get sample data
                        sample_query = f"SELECT FIRST 1 * FROM {table}"
                        sample_result = connector.execute_query(sample_query)
                        
                        if isinstance(sample_result, dict) and 'rows' in sample_result and sample_result['rows']:
                            sample_data = sample_result['rows'][0]
                            if isinstance(sample_data, dict):
                                keys = list(sample_data.keys())
                                print(f"     Sample keys: {keys[:10]}")
                                
                                # Look for ID and name columns
                                id_keys = [k for k in keys if k.upper().endswith('ID') or k.upper() == 'ID']
                                name_keys = [k for k in keys if 'NAME' in k.upper()]
                                
                                print(f"     ID columns: {id_keys}")
                                print(f"     Name columns: {name_keys}")
                                
                                # Show sample values
                                for key in (id_keys + name_keys)[:5]:
                                    value = sample_data.get(key, 'N/A')
                                    print(f"     {key}: {value}")
                        
                        elif isinstance(sample_result, list) and sample_result:
                            sample_data = sample_result[0]
                            if isinstance(sample_data, dict):
                                keys = list(sample_data.keys())
                                print(f"     Sample keys (list format): {keys[:10]}")
                
                except Exception as e:
                    print(f"     Error: {e}")
    
    except Exception as e:
        print(f"   Error getting tables: {e}")
    
    # Also test some common field table names directly
    print("\n3. Testing common field table names directly:")
    common_names = ['FIELD', 'FIELDS', 'DIVISION', 'DIVISIONS', 'CRDIVISION', 'AREA', 'BLOCK']
    
    for table in common_names:
        try:
            sample_query = f"SELECT FIRST 1 * FROM {table}"
            sample_result = connector.execute_query(sample_query)
            
            if sample_result:
                print(f"   {table}: Found data")
                if isinstance(sample_result, dict) and 'rows' in sample_result and sample_result['rows']:
                    keys = list(sample_result['rows'][0].keys()) if isinstance(sample_result['rows'][0], dict) else []
                    print(f"     Keys: {keys[:5]}")
                elif isinstance(sample_result, list) and sample_result:
                    keys = list(sample_result[0].keys()) if isinstance(sample_result[0], dict) else []
                    print(f"     Keys: {keys[:5]}")
            else:
                print(f"   {table}: No data")
                
        except Exception as e:
            print(f"   {table}: Error - {str(e)[:50]}")
    
    print("\n=== Search Complete ===")

if __name__ == "__main__":
    find_field_tables()