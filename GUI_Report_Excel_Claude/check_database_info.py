#!/usr/bin/env python3
"""
Check database information and find tables with data
READ-ONLY ACCESS - No data modification
"""

import sys
import os
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def check_database_info():
    """Check database information and find tables with data"""
    
    try:
        # Initialize database connection
        connector = FirebirdConnectorEnhanced()
        
        # Show database path being used
        print(f"🗂️  Database path: {connector.db_path}")
        print("=" * 60)
        
        # Test connection
        if not connector.test_connection():
            print("❌ Database connection failed")
            return False
            
        print("✅ Database connection successful")
        
        # Get all tables
        print("\n🔍 Getting table list...")
        tables = connector.get_table_list()
        
        if not tables:
            print("❌ No tables found")
            return False
            
        print(f"✅ Found {len(tables)} total tables")
        
        # Check which tables have data
        print("\n🔍 Checking all tables for data...")
        tables_with_data = []
        
        for i, table in enumerate(tables):
            if i % 20 == 0:  # Progress indicator
                print(f"   Progress: {i}/{len(tables)} tables checked...")
            
            try:
                row_count = connector.get_row_count(table)
                if row_count > 0:
                    tables_with_data.append((table, row_count))
            except Exception as e:
                # Skip tables that can't be queried (system tables, etc.)
                continue
        
        print(f"\n📊 Found {len(tables_with_data)} tables with data:")
        
        if tables_with_data:
            # Sort by row count (descending)
            tables_with_data.sort(key=lambda x: x[1], reverse=True)
            
            print("\n🎯 Tables with data (sorted by row count):")
            for table, count in tables_with_data:
                print(f"   - {table}: {count:,} records")
            
            # Show sample from the table with most data
            if tables_with_data:
                largest_table, largest_count = tables_with_data[0]
                print(f"\n📋 Sample from largest table ({largest_table}):")
                
                try:
                    sample_data = connector.get_sample_data(largest_table, limit=2)
                    
                    if sample_data:
                        for i, record in enumerate(sample_data):
                            if isinstance(record, dict):
                                print(f"   Record {i+1}:")
                                # Show all fields for first record
                                if i == 0:
                                    for key, value in record.items():
                                        print(f"      {key}: {value}")
                                else:
                                    # Show just first few fields for other records
                                    fields = list(record.items())[:5]
                                    field_str = ", ".join([f"{k}={v}" for k, v in fields])
                                    print(f"      {field_str}")
                            else:
                                print(f"   Record {i+1}: {str(record)[:80]}...")
                except Exception as e:
                    print(f"   ❌ Error getting sample: {str(e)}")
            
            # Check if any tables contain date-related data
            print(f"\n📅 Looking for tables with date fields...")
            date_tables = []
            
            for table, count in tables_with_data[:5]:  # Check top 5 tables
                try:
                    sample = connector.get_sample_data(table, limit=1)
                    if sample and len(sample) > 0:
                        record = sample[0]
                        if isinstance(record, dict):
                            date_fields = [k for k in record.keys() if any(date_word in k.upper() 
                                         for date_word in ['DATE', 'TIME', 'TANGGAL', 'WAKTU'])]
                            if date_fields:
                                date_tables.append((table, date_fields))
                except:
                    continue
            
            if date_tables:
                print(f"   📅 Tables with date fields:")
                for table, date_fields in date_tables:
                    print(f"      - {table}: {', '.join(date_fields)}")
        else:
            print("\n⚠️  No tables contain data")
            print("\n🔍 Possible reasons:")
            print("   - This is a fresh/empty database")
            print("   - Data is in a different database file")
            print("   - Database needs to be populated first")
            
            # Check if database file exists and size
            if os.path.exists(connector.db_path):
                file_size = os.path.getsize(connector.db_path)
                print(f"   📁 Database file size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
            else:
                print(f"   ❌ Database file not found: {connector.db_path}")
        
        return len(tables_with_data) > 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
        
    finally:
        if 'connector' in locals() and hasattr(connector, 'close'):
            connector.close()

if __name__ == "__main__":
    print("🔍 Checking database information and data...")
    print("📖 READ-ONLY ACCESS - No data modification")
    print("=" * 60)
    
    success = check_database_info()
    
    if success:
        print("\n✅ Database contains data")
    else:
        print("\n❌ Database appears to be empty")