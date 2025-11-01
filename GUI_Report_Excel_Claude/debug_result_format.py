#!/usr/bin/env python3
"""
Debug Result Format
==================
Debug script to understand the actual result format from FirebirdConnectorEnhanced.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def debug_result_format():
    """Debug the result format"""
    print("🔍 Debugging FirebirdConnectorEnhanced result format...")
    
    try:
        # Initialize connector
        connector = FirebirdConnectorEnhanced()
        
        # Simple test query
        test_query = "SELECT FIRST 1 RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0"
        
        print(f"📝 Executing query: {test_query}")
        result = connector.execute_query(test_query)
        
        print(f"🔍 Result type: {type(result)}")
        print(f"📋 Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        print(f"📊 Full result: {result}")
        
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"  {key}: {type(value)} = {value}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Result Format Debugger")
    print("=" * 50)
    
    result = debug_result_format()
    
    if result:
        print("\n✅ Debug completed successfully!")
    else:
        print("\n❌ Debug failed")

if __name__ == "__main__":
    main()