#!/usr/bin/env python3
"""
Test Corrected Queries Script
Verify that the fixed query structure returns data properly
"""

import json
from firebird_connector_enhanced import FirebirdConnectorEnhanced
from datetime import datetime

def test_queries():
    """Test the corrected queries to ensure they return data"""
    
    print("Testing Corrected Queries")
    print("=" * 50)
    
    # Initialize database connection
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    
    try:
        connector = FirebirdConnectorEnhanced(db_path)
        print(f"✓ Connected to database: {db_path}")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    
    # Load corrected query templates
    try:
        with open('pge2b_corrected_formula.json', 'r', encoding='utf-8') as f:
            template = json.load(f)
        print(f"✓ Loaded query template with {len(template['queries'])} queries")
    except Exception as e:
        print(f"✗ Failed to load query template: {e}")
        return False
    
    # Test parameters
    test_params = {
        'start_date': '2025-10-01',
        'end_date': '2025-10-31',
        'month': 10,
        'div_id': '1'  # Test with division 1
    }
    
    print(f"\nTest Parameters:")
    print(f"  Date Range: {test_params['start_date']} to {test_params['end_date']}")
    print(f"  Month: {test_params['month']}")
    print(f"  Division ID: {test_params['div_id']}")
    
    # Priority queries to test first
    priority_queries = [
        'employee_mapping',
        'division_list', 
        'raw_ffb_data',
        'daily_summary',
        'scanner_performance',
        'field_performance',
        'monthly_summary',
        'kerani_mandor_analysis'
    ]
    
    results = {}
    total_rows = 0
    
    print(f"\nTesting Priority Queries:")
    print("-" * 30)
    
    for query_name in priority_queries:
        if query_name not in template['queries']:
            print(f"⚠ Query '{query_name}' not found in template")
            continue
            
        query_info = template['queries'][query_name]
        sql = query_info['sql']
        
        # Format SQL with parameters
        try:
            formatted_sql = sql.format(**test_params)
        except KeyError as e:
            print(f"⚠ {query_name}: Missing parameter {e}")
            continue
        
        # Execute query
        try:
            result = connector.execute_query(formatted_sql)
            row_count = len(result) if result else 0
            results[query_name] = row_count
            total_rows += row_count
            
            status = "✓" if row_count > 0 else "⚠"
            print(f"  {status} {query_name}: {row_count} rows")
            
            # Show sample data for successful queries
            if row_count > 0 and row_count <= 3:
                print(f"    Sample: {result[0] if result else 'No data'}")
            elif row_count > 3:
                print(f"    Sample: {result[0] if result else 'No data'}")
                
        except Exception as e:
            print(f"  ✗ {query_name}: Error - {str(e)[:100]}...")
            results[query_name] = 0
    
    # Test remaining queries
    remaining_queries = [q for q in template['queries'].keys() if q not in priority_queries]
    
    if remaining_queries:
        print(f"\nTesting Remaining Queries:")
        print("-" * 30)
        
        for query_name in remaining_queries:
            query_info = template['queries'][query_name]
            sql = query_info['sql']
            
            # Format SQL with parameters
            try:
                formatted_sql = sql.format(**test_params)
            except KeyError as e:
                print(f"⚠ {query_name}: Missing parameter {e}")
                continue
            
            # Execute query
            try:
                result = connector.execute_query(formatted_sql)
                row_count = len(result) if result else 0
                results[query_name] = row_count
                total_rows += row_count
                
                status = "✓" if row_count > 0 else "⚠"
                print(f"  {status} {query_name}: {row_count} rows")
                
            except Exception as e:
                print(f"  ✗ {query_name}: Error - {str(e)[:100]}...")
                results[query_name] = 0
    
    # Summary
    print(f"\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    successful_queries = sum(1 for count in results.values() if count > 0)
    total_queries = len(results)
    success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0
    
    print(f"Total Queries Tested: {total_queries}")
    print(f"Successful Queries: {successful_queries}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Total Rows Retrieved: {total_rows}")
    
    # Detailed results
    print(f"\nDetailed Results:")
    for query_name, row_count in results.items():
        status = "SUCCESS" if row_count > 0 else "WARNING"
        print(f"  {status}: {query_name}: {row_count} rows")
    
    # Check for critical queries
    critical_queries = ['raw_ffb_data', 'daily_summary', 'monthly_summary']
    critical_success = all(results.get(q, 0) > 0 for q in critical_queries)
    
    print(f"\nCritical Query Status:")
    for query in critical_queries:
        status = "✓" if results.get(query, 0) > 0 else "✗"
        print(f"  {status} {query}: {results.get(query, 0)} rows")
    
    if critical_success:
        print(f"\n🎉 SUCCESS: All critical queries are returning data!")
        print(f"   The query structure fix appears to be working correctly.")
    else:
        print(f"\n⚠ WARNING: Some critical queries are still returning 0 rows.")
        print(f"   Further investigation may be needed.")
    
    return critical_success

def main():
    """Main function"""
    success = test_queries()
    
    if success:
        print(f"\n✅ Query testing completed successfully!")
        print(f"   Ready to test ETL report generation.")
    else:
        print(f"\n❌ Query testing revealed issues.")
        print(f"   Check database content and query structure.")

if __name__ == "__main__":
    main()