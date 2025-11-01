"""
Debug script to test the actual queries used by the GUI
"""
import json
from firebird_connector_enhanced import FirebirdConnectorEnhanced
from datetime import datetime

def test_gui_queries():
    """Test the actual queries used by the GUI"""
    print("=== Testing GUI Queries ===")
    
    # Create connector same as GUI
    connector = FirebirdConnectorEnhanced.create_default_connector()
    
    if not connector.test_connection():
        print(f"❌ Connection failed: {connector.last_error}")
        return
    
    print("✅ Connection successful")
    
    # Load template queries
    try:
        with open('ffb_analysis_single_estate_formula.json', 'r') as f:
            template = json.load(f)
        print("✅ Template loaded")
    except Exception as e:
        print(f"❌ Failed to load template: {e}")
        return
    
    # Test parameters (same as GUI would use)
    test_params = {
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'division_id': 'A01',
        'month': 1  # January
    }
    
    # Test each query
    queries_to_test = ['employee_mapping', 'divisions', 'analyze_division']
    
    for query_name in queries_to_test:
        print(f"\n--- Testing {query_name} ---")
        
        if query_name not in template['queries']:
            print(f"❌ Query {query_name} not found in template")
            continue
            
        query_info = template['queries'][query_name]
        query = query_info['sql']
        
        print(f"Description: {query_info.get('description', 'No description')}")
        
        # Substitute parameters
        try:
            final_query = query
            for param, value in test_params.items():
                if param == 'month':
                    # Handle month formatting
                    final_query = final_query.replace(f'{{{param}:02d}}', f'{value:02d}')
                else:
                    final_query = final_query.replace(f'{{{param}}}', str(value))
            
            print(f"Final query: {final_query[:200]}...")
            
            # Execute query
            result = connector.execute_query(final_query)
            
            if result:
                print(f"✅ Query successful: {len(result)} rows returned")
                if len(result) > 0:
                    print(f"Sample row keys: {list(result[0].keys())}")
                    print(f"Sample row: {result[0]}")
            else:
                print("⚠️ Query returned no data")
                
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    # Test table existence
    print(f"\n--- Testing Table Existence ---")
    tables_to_check = ['EMP', 'FFBLOADINGCROP01', 'FFBLOADINGCROP02', 'FFBLOADINGCROP03']
    
    for table in tables_to_check:
        try:
            exists = connector.check_table_exists(table)
            if exists:
                count = connector.get_row_count(table)
                print(f"✅ {table}: exists, {count} rows")
            else:
                print(f"❌ {table}: does not exist")
        except Exception as e:
            print(f"❌ {table}: error checking - {e}")

if __name__ == "__main__":
    test_gui_queries()