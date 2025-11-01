#!/usr/bin/env python3
"""
Check what tables exist in the database and which ones have data
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def main():
    print("🔍 Checking Database Tables and Data")
    print("=" * 50)
    
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
    
    # Get all tables
    try:
        tables = connector.get_table_list()
        print(f"\n📋 Found {len(tables)} tables in database")
        
        # Filter for relevant tables
        ffb_tables = [t for t in tables if 'FFB' in t.upper()]
        scanner_tables = [t for t in tables if 'SCANNER' in t.upper()]
        field_tables = [t for t in tables if 'FIELD' in t.upper() or 'OCFIELD' in t.upper()]
        division_tables = [t for t in tables if 'DIV' in t.upper()]
        emp_tables = [t for t in tables if 'EMP' in t.upper()]
        
        print(f"\n🔍 Relevant Tables Found:")
        print(f"  FFB tables: {ffb_tables}")
        print(f"  Scanner tables: {scanner_tables}")
        print(f"  Field tables: {field_tables}")
        print(f"  Division tables: {division_tables}")
        print(f"  Employee tables: {emp_tables}")
        
        # Check data in each relevant table
        all_relevant_tables = set(ffb_tables + scanner_tables + field_tables + division_tables + emp_tables)
        
        print(f"\n📊 Checking data in relevant tables:")
        tables_with_data = []
        
        for table in all_relevant_tables:
            try:
                count = connector.get_row_count(table)
                if count > 0:
                    tables_with_data.append((table, count))
                    print(f"  ✅ {table}: {count:,} rows")
                    
                    # Get sample data for tables with data
                    sample = connector.get_sample_data(table, limit=3)
                    if sample:
                        print(f"     Sample columns: {list(sample[0].keys())}")
                else:
                    print(f"  ❌ {table}: 0 rows")
            except Exception as e:
                print(f"  ❌ {table}: Error - {e}")
        
        # Check all tables for any with data
        if not tables_with_data:
            print(f"\n🔍 Checking ALL tables for data:")
            for table in tables[:20]:  # Check first 20 tables
                try:
                    count = connector.get_row_count(table)
                    if count > 0:
                        tables_with_data.append((table, count))
                        print(f"  ✅ {table}: {count:,} rows")
                        
                        # Get sample data
                        sample = connector.get_sample_data(table, limit=2)
                        if sample:
                            print(f"     Sample columns: {list(sample[0].keys())[:5]}...")
                except Exception as e:
                    print(f"  ❌ {table}: Error checking")
        
        # Summary
        print(f"\n📈 Summary:")
        print(f"  Total tables: {len(tables)}")
        print(f"  Tables with data: {len(tables_with_data)}")
        
        if tables_with_data:
            print(f"\n📋 Tables with data:")
            for table, count in sorted(tables_with_data, key=lambda x: x[1], reverse=True):
                print(f"  • {table}: {count:,} rows")
        else:
            print(f"\n⚠️  No tables found with data!")
            
    except Exception as e:
        print(f"❌ Error getting table list: {e}")

if __name__ == "__main__":
    main()