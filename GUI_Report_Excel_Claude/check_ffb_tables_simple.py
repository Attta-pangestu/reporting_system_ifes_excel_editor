#!/usr/bin/env python3
"""
Simple check of FFB tables using built-in connector methods
READ-ONLY ACCESS - No data modification
"""

import sys
import os
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def check_ffb_tables_simple():
    """Check FFB tables using built-in connector methods"""
    
    try:
        # Initialize database connection
        connector = FirebirdConnectorEnhanced()
        
        # Test connection
        if not connector.test_connection():
            print("❌ Database connection failed")
            return False
            
        print("✅ Database connection successful")
        print("=" * 60)
        
        # Get all tables
        print("🔍 Getting table list...")
        tables = connector.get_table_list()
        
        if not tables:
            print("❌ No tables found")
            return False
            
        print(f"✅ Found {len(tables)} total tables")
        
        # Filter FFB scanner tables
        ffb_scanner_tables = [t for t in tables if 'FFBSCANNERDATA' in t.upper()]
        print(f"\n📡 FFBSCANNERDATA tables ({len(ffb_scanner_tables)}):")
        
        tables_with_data = []
        
        for table in ffb_scanner_tables:
            print(f"\n🔍 Checking {table}...")
            
            # Check if table exists
            if connector.check_table_exists(table):
                print(f"   ✅ Table exists")
                
                # Get row count
                try:
                    row_count = connector.get_row_count(table)
                    print(f"   📊 Row count: {row_count:,}")
                    
                    if row_count > 0:
                        tables_with_data.append((table, row_count))
                        
                        # Get sample data
                        print(f"   📄 Getting sample data...")
                        sample_data = connector.get_sample_data(table, limit=3)
                        
                        if sample_data:
                            print(f"   📋 Sample records ({len(sample_data)}):")
                            for i, record in enumerate(sample_data):
                                if isinstance(record, dict):
                                    # Show first few fields
                                    fields = list(record.items())[:6]
                                    field_str = ", ".join([f"{k}={v}" for k, v in fields])
                                    print(f"      Record {i+1}: {field_str}")
                                else:
                                    print(f"      Record {i+1}: {str(record)[:80]}...")
                        else:
                            print(f"   ⚠️  No sample data returned")
                    else:
                        print(f"   ⚪ Table is empty")
                        
                except Exception as e:
                    print(f"   ❌ Error getting row count: {str(e)}")
            else:
                print(f"   ❌ Table does not exist")
        
        print("\n" + "=" * 60)
        print(f"📈 Summary: {len(tables_with_data)} FFBSCANNERDATA tables contain data")
        
        if tables_with_data:
            print("\n🎯 Tables with data:")
            for table, count in tables_with_data:
                print(f"   - {table}: {count:,} records")
                
            # Focus on FFBSCANNERDATA04
            ffbscannerdata04_found = False
            for table, count in tables_with_data:
                if table == 'FFBSCANNERDATA04':
                    ffbscannerdata04_found = True
                    print(f"\n🎯 FFBSCANNERDATA04 found with {count:,} records!")
                    
                    # Get detailed sample from FFBSCANNERDATA04
                    print("   📋 Detailed sample from FFBSCANNERDATA04:")
                    detailed_sample = connector.get_sample_data('FFBSCANNERDATA04', limit=5)
                    
                    if detailed_sample:
                        for i, record in enumerate(detailed_sample):
                            if isinstance(record, dict):
                                print(f"      Record {i+1}:")
                                for key, value in record.items():
                                    print(f"         {key}: {value}")
                                print()
                    break
            
            if not ffbscannerdata04_found:
                print("\n⚠️  FFBSCANNERDATA04 not found or empty")
                
                # Check other month tables
                month_tables = [table for table, count in tables_with_data if 'FFBSCANNERDATA' in table]
                if month_tables:
                    print(f"   📅 Other FFBSCANNERDATA tables with data:")
                    for table, count in tables_with_data:
                        if 'FFBSCANNERDATA' in table:
                            print(f"      - {table}: {count:,} records")
        else:
            print("\n⚠️  No FFBSCANNERDATA tables contain data")
            
        return len(tables_with_data) > 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
        
    finally:
        if 'connector' in locals() and hasattr(connector, 'close'):
            connector.close()

if __name__ == "__main__":
    print("🔍 Simple check of FFB tables...")
    print("📖 READ-ONLY ACCESS - No data modification")
    print("=" * 60)
    
    success = check_ffb_tables_simple()
    
    if success:
        print("\n✅ Found FFB tables with data")
    else:
        print("\n❌ No FFB tables with data found")