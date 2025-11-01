#!/usr/bin/env python3
"""
Test script for reference-based queries
Tests the new query templates based on gui_multi_estate_ffb_analysis.py structure
"""

import json
import sys
import os
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def load_queries():
    """Load the reference-based query templates"""
    try:
        with open('pge2b_corrected_formula.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading queries: {e}")
        return None

def find_available_data_range(connector):
    """Find the actual available data range in the database"""
    print("\n🔍 Finding available data range...")
    
    # Check FFBSCANNERDATA tables for available months
    available_months = []
    for month in range(1, 13):
        table_name = f"FFBSCANNERDATA{month:02d}"
        try:
            query = f"SELECT COUNT(*) FROM {table_name}"
            result = connector.execute_query(query)
            if result and len(result) > 0 and result[0][0] > 0:
                available_months.append(month)
                print(f"  ✅ {table_name}: {result[0][0]} records")
        except Exception as e:
            print(f"  ❌ {table_name}: Not available")
    
    if not available_months:
        print("❌ No FFBSCANNERDATA tables found with data")
        return None, None
    
    # Find date range in the first available table
    first_table = f"FFBSCANNERDATA{available_months[0]:02d}"
    try:
        query = f"SELECT MIN(TRANSDATE), MAX(TRANSDATE) FROM {first_table}"
        result = connector.execute_query(query)
        if result and len(result) > 0:
            min_date, max_date = result[0]
            print(f"📅 Date range in {first_table}: {min_date} to {max_date}")
            return min_date, max_date
    except Exception as e:
        print(f"❌ Error getting date range: {e}")
    
    return None, None

def test_query_with_params(connector, query_name, query_template, params):
    """Test a single query with given parameters"""
    try:
        # Replace parameters in the query
        query = query_template
        for param, value in params.items():
            query = query.replace(f"{{{param}}}", str(value))
        
        print(f"\n🔍 Testing {query_name}...")
        print(f"   Query: {query[:100]}...")
        
        result = connector.execute_query(query)
        
        if result:
            row_count = len(result)
            print(f"   ✅ Success: {row_count} rows returned")
            
            # Show sample data for first few rows
            if row_count > 0:
                print(f"   📊 Sample data (first row): {result[0]}")
                if row_count > 1:
                    print(f"   📊 Sample data (second row): {result[1]}")
            
            return True, row_count
        else:
            print(f"   ⚠️  Query executed but returned no data")
            return True, 0
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False, 0

def main():
    print("🚀 Testing Reference-Based Queries")
    print("=" * 50)
    
    # Load queries
    queries = load_queries()
    if not queries:
        return
    
    print(f"📋 Loaded {len(queries)} query templates")
    
    # Connect to database
    try:
        connector = FirebirdConnectorEnhanced()
        if connector.test_connection():
            print("✅ Database connection established")
        else:
            print("❌ Database connection test failed")
            return
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Find available data range
    min_date, max_date = find_available_data_range(connector)
    if not min_date or not max_date:
        print("❌ No data available for testing")
        return
    
    # Use available date range for testing
    test_date = min_date
    test_month = test_date.month
    test_year = test_date.year
    
    print(f"\n📅 Using test parameters:")
    print(f"   Date: {test_date}")
    print(f"   Month: {test_month}")
    print(f"   Year: {test_year}")
    print(f"   Table: FFBSCANNERDATA{test_month:02d}")
    
    # Test parameters
    test_params = {
        'month_table': f'FFBSCANNERDATA{test_month:02d}',
        'start_date': test_date.strftime('%Y-%m-%d'),
        'end_date': (test_date + timedelta(days=7)).strftime('%Y-%m-%d'),
        'division_id': '1'
    }
    
    # Priority queries to test first
    priority_queries = [
        'employee_mapping',
        'raw_ffb_data', 
        'division_list',
        'daily_summary',
        'scanner_performance',
        'field_performance',
        'monthly_summary'
    ]
    
    successful_queries = 0
    total_queries = 0
    results_summary = {}
    
    print(f"\n🧪 Testing Priority Queries")
    print("-" * 30)
    
    # Test priority queries first
    for query_name in priority_queries:
        if query_name in queries:
            total_queries += 1
            success, row_count = test_query_with_params(
                connector, query_name, queries[query_name], test_params
            )
            if success:
                successful_queries += 1
            results_summary[query_name] = {'success': success, 'rows': row_count}
    
    print(f"\n🧪 Testing Remaining Queries")
    print("-" * 30)
    
    # Test remaining queries
    for query_name, query_template in queries.items():
        if query_name not in priority_queries:
            total_queries += 1
            success, row_count = test_query_with_params(
                connector, query_name, query_template, test_params
            )
            if success:
                successful_queries += 1
            results_summary[query_name] = {'success': success, 'rows': row_count}
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 50)
    print(f"Total queries tested: {total_queries}")
    print(f"Successful queries: {successful_queries}")
    print(f"Success rate: {(successful_queries/total_queries)*100:.1f}%")
    
    print(f"\n📋 Detailed Results:")
    for query_name, result in results_summary.items():
        status = "✅" if result['success'] else "❌"
        rows = result['rows'] if result['success'] else 0
        print(f"  {status} {query_name}: {rows} rows")
    
    # Check critical queries
    critical_queries = ['raw_ffb_data', 'daily_summary', 'monthly_summary']
    critical_success = all(
        results_summary.get(q, {}).get('success', False) and 
        results_summary.get(q, {}).get('rows', 0) > 0 
        for q in critical_queries
    )
    
    print(f"\n🎯 Critical Queries Status:")
    for query in critical_queries:
        result = results_summary.get(query, {})
        status = "✅" if result.get('success', False) and result.get('rows', 0) > 0 else "❌"
        rows = result.get('rows', 0)
        print(f"  {status} {query}: {rows} rows")
    
    if critical_success:
        print(f"\n🎉 SUCCESS: All critical queries are working!")
    else:
        print(f"\n⚠️  WARNING: Some critical queries still need attention")
    
    connector.close() if hasattr(connector, 'close') else None

if __name__ == "__main__":
    main()