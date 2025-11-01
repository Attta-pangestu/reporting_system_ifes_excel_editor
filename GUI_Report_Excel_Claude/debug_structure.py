#!/usr/bin/env python3
"""
Debug Structure Query
====================
Debug script to test the structure query specifically.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def debug_structure():
    """Debug the structure query"""
    print("🔍 Debugging structure query...")
    
    try:
        # Initialize connector
        connector = FirebirdConnectorEnhanced()
        
        # First, get a table name
        tables_query = "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0 AND RDB$RELATION_NAME LIKE '%FFB%'"
        
        print(f"📝 Getting FFB tables...")
        result = connector.execute_query(tables_query)
        print(f"🔍 Tables result: {result}")
        
        if result and len(result) > 0:
            result_data = result[0]
            if 'rows' in result_data and len(result_data['rows']) > 0:
                table_name = result_data['rows'][0]['RDB$RELATION_NAME'].strip()
                print(f"📋 Using table: {table_name}")
                
                # Now test structure query
                structure_query = f"""
                SELECT RDB$FIELD_NAME, RDB$FIELD_TYPE, RDB$FIELD_LENGTH 
                FROM RDB$RELATION_FIELDS 
                WHERE RDB$RELATION_NAME = '{table_name}'
                """
                
                print(f"📝 Structure query: {structure_query}")
                structure_result = connector.execute_query(structure_query)
                print(f"🔍 Structure result: {structure_result}")
                
                # Try simpler query
                simple_query = f"SELECT RDB$FIELD_NAME FROM RDB$RELATION_FIELDS WHERE RDB$RELATION_NAME = '{table_name}'"
                print(f"📝 Simple query: {simple_query}")
                simple_result = connector.execute_query(simple_query)
                print(f"🔍 Simple result: {simple_result}")
                
            else:
                print("❌ No FFB tables found")
        else:
            print("❌ No tables result")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("🚀 Structure Query Debugger")
    print("=" * 50)
    
    debug_structure()

if __name__ == "__main__":
    main()