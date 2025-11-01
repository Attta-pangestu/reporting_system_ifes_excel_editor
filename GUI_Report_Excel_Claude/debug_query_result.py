#!/usr/bin/env python3
"""
Debug script to understand the query result format from Firebird connector.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def debug_query_result():
    """Debug the query result format"""
    
    # Use the recommended database
    db_path = r'D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_ARE_C_24-10-2025\PTRJ_ARC.FDB'
    
    print("🔍 Debugging query result format")
    print(f"Database: {db_path}")
    
    try:
        connector = FirebirdConnectorEnhanced(db_path=db_path)
        
        if not connector.test_connection():
            print("❌ Failed to connect")
            return
        
        print("✅ Connected successfully")
        
        # Test simple count query
        table = "FFBSCANNERDATA01"
        count_query = f"SELECT COUNT(*) FROM {table}"
        
        print(f"\n🧪 Testing query: {count_query}")
        
        result = connector.execute_query(count_query)
        
        print(f"📊 Raw result: {result}")
        print(f"📊 Result type: {type(result)}")
        
        if result:
            print(f"📊 Result length: {len(result)}")
            if len(result) > 0:
                first_row = result[0]
                print(f"📊 First row: {first_row}")
                print(f"📊 First row type: {type(first_row)}")
                
                if isinstance(first_row, dict):
                    print(f"📊 Keys: {list(first_row.keys())}")
                    print(f"📊 Values: {list(first_row.values())}")
                elif isinstance(first_row, (list, tuple)):
                    print(f"📊 First row as list/tuple: {first_row}")
                    if len(first_row) > 0:
                        print(f"📊 First value: {first_row[0]}")
                        print(f"📊 First value type: {type(first_row[0])}")
        
        # Test with alias
        count_query_alias = f"SELECT COUNT(*) as TOTAL FROM {table}"
        print(f"\n🧪 Testing query with alias: {count_query_alias}")
        
        result_alias = connector.execute_query(count_query_alias)
        
        print(f"📊 Raw result with alias: {result_alias}")
        
        if result_alias and len(result_alias) > 0:
            first_row_alias = result_alias[0]
            print(f"📊 First row with alias: {first_row_alias}")
            print(f"📊 First row type with alias: {type(first_row_alias)}")
            
            if isinstance(first_row_alias, dict):
                print(f"📊 Keys with alias: {list(first_row_alias.keys())}")
                print(f"📊 Values with alias: {list(first_row_alias.values())}")
        
        # Test sample data query
        sample_query = f"SELECT FIRST 1 * FROM {table}"
        print(f"\n🧪 Testing sample query: {sample_query}")
        
        sample_result = connector.execute_query(sample_query)
        
        print(f"📊 Sample result: {sample_result}")
        
        if sample_result and len(sample_result) > 0:
            sample_row = sample_result[0]
            print(f"📊 Sample row type: {type(sample_row)}")
            
            if isinstance(sample_row, dict):
                print(f"📊 Sample columns: {list(sample_row.keys())[:10]}...")  # First 10 columns
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_query_result()