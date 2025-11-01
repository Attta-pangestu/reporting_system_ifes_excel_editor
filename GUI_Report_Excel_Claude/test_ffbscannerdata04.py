#!/usr/bin/env python3
"""
Test FFBSCANNERDATA04 table and validate reference-based queries
Focus on month 4 data as mentioned by user
READ-ONLY ACCESS - No data modification
"""

import sys
import os
import json
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def test_ffbscannerdata04():
    """Test FFBSCANNERDATA04 table and validate queries"""
    
    try:
        # Initialize database connection
        connector = FirebirdConnectorEnhanced()
        
        # Test connection
        if not connector.test_connection():
            print("❌ Database connection failed")
            return False
            
        print("✅ Database connection successful")
        print("=" * 60)
        
        # Check FFBSCANNERDATA04 specifically
        print("🔍 Checking FFBSCANNERDATA04 table...")
        
        # Get row count
        count_query = "SELECT COUNT(*) FROM FFBSCANNERDATA04"
        count_result = connector.execute_query(count_query)
        
        if not count_result or count_result[0][0] == 0:
            print("❌ FFBSCANNERDATA04 table is empty")
            return False
            
        row_count = count_result[0][0]
        print(f"✅ FFBSCANNERDATA04 contains {row_count:,} records")
        
        # Get table structure
        print(f"\n📊 FFBSCANNERDATA04 table structure:")
        columns_query = """
        SELECT TRIM(RDB$FIELD_NAME) 
        FROM RDB$RELATION_FIELDS 
        WHERE TRIM(RDB$RELATION_NAME) = 'FFBSCANNERDATA04'
        ORDER BY RDB$FIELD_POSITION
        """
        columns_result = connector.execute_query(columns_query)
        
        if columns_result:
            column_names = [col[0] for col in columns_result if col[0]]
            print(f"   Columns ({len(column_names)}): {', '.join(column_names)}")
        
        # Get sample data
        print(f"\n📄 Sample data from FFBSCANNERDATA04:")
        sample_query = """
        SELECT FIRST 5 
            SCANUSERID, DIVID, FIELDID, TRANSDATE,
            RIPEBCH, BLACKBCH, ROTTENBCH, EMPTYBCH
        FROM FFBSCANNERDATA04
        ORDER BY TRANSDATE DESC
        """
        sample_result = connector.execute_query(sample_query)
        
        if sample_result:
            print("   SCANUSERID | DIVID | FIELDID | TRANSDATE  | RIPEBCH | BLACKBCH | ROTTENBCH | EMPTYBCH")
            print("   " + "-" * 80)
            
            for row in sample_result:
                print(f"   {str(row[0]):<10} | {str(row[1]):<5} | {str(row[2]):<7} | {str(row[3]):<10} | {str(row[4]):<7} | {str(row[5]):<8} | {str(row[6]):<9} | {str(row[7])}")
        
        # Get date range
        print(f"\n📅 Date range in FFBSCANNERDATA04:")
        date_range_query = """
        SELECT MIN(TRANSDATE) as min_date, MAX(TRANSDATE) as max_date
        FROM FFBSCANNERDATA04
        WHERE TRANSDATE IS NOT NULL
        """
        date_result = connector.execute_query(date_range_query)
        
        if date_result and date_result[0][0]:
            min_date = date_result[0][0]
            max_date = date_result[0][1]
            print(f"   Date range: {min_date} to {max_date}")
        
        print("\n" + "=" * 60)
        
        # Test reference-based queries
        print("🧪 Testing reference-based queries...")
        
        # Load the reference-based queries
        try:
            with open('pge2b_reference_based_formula.json', 'r', encoding='utf-8') as f:
                queries = json.load(f)
            print(f"✅ Loaded {len(queries)} reference-based queries")
        except FileNotFoundError:
            print("❌ pge2b_reference_based_formula.json not found")
            return False
        
        # Test key queries with FFBSCANNERDATA04
        test_queries = [
            'raw_ffb_data',
            'daily_summary', 
            'employee_mapping',
            'field_mapping'
        ]
        
        successful_queries = 0
        
        for query_name in test_queries:
            if query_name in queries:
                print(f"\n🔍 Testing query: {query_name}")
                
                query_template = queries[query_name]['query']
                
                # Replace table placeholder with FFBSCANNERDATA04
                test_query = query_template.replace('{table_name}', 'FFBSCANNERDATA04')
                
                # Use sample date range for testing
                if date_result and date_result[0][0]:
                    test_query = test_query.replace('{start_date}', f"'{min_date}'")
                    test_query = test_query.replace('{end_date}', f"'{max_date}'")
                
                # Replace other common parameters
                test_query = test_query.replace('{estate_code}', "'01'")
                test_query = test_query.replace('{division_id}', "1")
                
                try:
                    print(f"   Query: {test_query[:100]}...")
                    
                    result = connector.execute_query(test_query)
                    
                    if result:
                        print(f"   ✅ Success: {len(result)} records returned")
                        
                        # Show sample result
                        if len(result) > 0:
                            first_row = result[0]
                            if isinstance(first_row, dict):
                                keys = list(first_row.keys())[:5]
                                print(f"   📊 Sample columns: {keys}")
                            else:
                                print(f"   📊 Sample data: {str(first_row)[:80]}...")
                        
                        successful_queries += 1
                    else:
                        print(f"   ⚠️  No data returned")
                        
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
            else:
                print(f"\n⚠️  Query '{query_name}' not found in reference queries")
        
        print(f"\n📈 Query test results: {successful_queries}/{len(test_queries)} queries successful")
        
        return successful_queries > 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
        
    finally:
        if 'connector' in locals() and hasattr(connector, 'close'):
            connector.close()

if __name__ == "__main__":
    print("🔍 Testing FFBSCANNERDATA04 and reference-based queries...")
    print("📖 READ-ONLY ACCESS - No data modification")
    print("=" * 60)
    
    success = test_ffbscannerdata04()
    
    if success:
        print("\n✅ FFBSCANNERDATA04 testing successful")
    else:
        print("\n❌ FFBSCANNERDATA04 testing failed")