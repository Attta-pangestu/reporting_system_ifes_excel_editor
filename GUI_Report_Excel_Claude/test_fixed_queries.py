#!/usr/bin/env python3
"""
Test script to verify that the fixed queries are working correctly.
This will test the key queries from the updated template file.
"""

import json
from firebird_connector_enhanced importfrom firebird_connector_enhanced import FirebirdConnectorEnhanced

def test_fixed_queries():
    """Test the fixed queries to ensure they return data."""
    
    # Initialize connector
    connector = FirebirdConnectorEnhanced()
    
    # Load the fixed template
    with open('pge2b_corrected_formula.json', 'r', encoding='utf-8') as f:
        template_data = json.load(f)
    
    # Test parameters
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    month = 10  # October data
    
    print(f"Testing queries with date range: {start_date} to {end_date}")
    print(f"Using month: {month:02d}")
    print("=" * 60)
    
    # Test key queries
    test_queries = [
        'employee_mapping',
        'raw_ffb_data', 
        'daily_summary',
        'scanner_performance',
        'field_performance',
        'monthly_summary'
    ]
    
    results = {}
    
    for query_name in test_queries:
        if query_name in template_data['queries']:
            query_info = template_data['queries'][query_name]
            sql = query_info['sql']
            
            # Format the SQL with parameters
            try:
                formatted_sql = sql.format(
                    start_date=start_date,
                    end_date=end_date,
                    month=month
                )
                
                print(f"\n--- Testing query: {query_name} ---")
                print(f"SQL: {formatted_sql[:100]}...")
                
                # Execute the query
                result = connector.execute_query(formatted_sql)
                
                if result:
                    row_count = len(result)
                    print(f"✓ SUCCESS: {row_count} rows returned")
                    
                    if row_count > 0:
                        # Show sample data
                        sample = result[0]
                        print(f"Sample data: {dict(list(sample.items())[:3])}")
                    
                    results[query_name] = {
                        'status': 'success',
                        'row_count': row_count,
                        'sample': result[0] if result else None
                    }
                else:
                    print(f"✗ FAILED: No results returned")
                    results[query_name] = {
                        'status': 'failed',
                        'row_count': 0,
                        'sample': None
                    }
                    
            except Exception as e:
                print(f"✗ ERROR: {str(e)}")
                results[query_name] = {
                    'status': 'error',
                    'error': str(e)
                }
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    
    successful = sum(1 for r in results.values() if r.get('status') == 'success' and r.get('row_count', 0) > 0)
    failed = sum(1 for r in results.values() if r.get('status') == 'failed' or r.get('row_count', 0) == 0)
    errors = sum(1 for r in results.values() if r.get('status') == 'error')
    
    print(f"Successful queries with data: {successful}")
    print(f"Queries with no data: {failed}")
    print(f"Queries with errors: {errors}")
    
    if successful > 0:
        print("\n✓ Data preview functionality is working!")
    else:
        print("\n✗ Data preview functionality still has issues!")
    
    return results

if __name__ == "__main__":
    print("Testing fixed queries without OCFIELD joins...")
    results = test_fixed_queries()
    print("\nTest completed!")