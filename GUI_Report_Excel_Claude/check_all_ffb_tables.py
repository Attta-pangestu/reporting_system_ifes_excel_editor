#!/usr/bin/env python3
"""
Comprehensive check of all FFB-related tables
READ-ONLY ACCESS - No data modification
"""

import sys
import os
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def check_all_ffb_tables():
    """Check all FFB-related tables comprehensively"""
    
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
        
        # Filter all FFB-related tables
        ffb_related_keywords = ['FFB', 'SCANNER', 'LOADING', 'CROP']
        ffb_tables = []
        
        for table in tables:
            table_upper = table.upper()
            if any(keyword in table_upper for keyword in ffb_related_keywords):
                ffb_tables.append(table)
        
        print(f"\n📊 FFB-related tables ({len(ffb_tables)}):")
        for table in sorted(ffb_tables):
            print(f"   - {table}")
        
        print("\n" + "=" * 60)
        print("🔍 Checking each FFB table for data...")
        
        tables_with_data = []
        
        for table in sorted(ffb_tables):
            print(f"\n📋 Checking {table}...")
            
            try:
                # Get row count
                row_count = connector.get_row_count(table)
                print(f"   📊 Row count: {row_count:,}")
                
                if row_count > 0:
                    tables_with_data.append((table, row_count))
                    
                    # Get sample data
                    print(f"   📄 Getting sample data...")
                    sample_data = connector.get_sample_data(table, limit=2)
                    
                    if sample_data:
                        print(f"   📋 Sample records ({len(sample_data)}):")
                        for i, record in enumerate(sample_data):
                            if isinstance(record, dict):
                                # Show first few fields
                                fields = list(record.items())[:5]
                                field_str = ", ".join([f"{k}={v}" for k, v in fields])
                                print(f"      Record {i+1}: {field_str}")
                            else:
                                print(f"      Record {i+1}: {str(record)[:60]}...")
                    else:
                        print(f"   ⚠️  No sample data returned")
                else:
                    print(f"   ⚪ Table is empty")
                    
            except Exception as e:
                print(f"   ❌ Error checking table: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"📈 Summary: {len(tables_with_data)} FFB tables contain data")
        
        if tables_with_data:
            print("\n🎯 Tables with data:")
            for table, count in tables_with_data:
                print(f"   - {table}: {count:,} records")
                
            # Check for specific tables mentioned by user
            print("\n🔍 Checking for specific tables mentioned:")
            
            # Check FFBSCANNERDATA04
            ffbscannerdata04_found = False
            for table, count in tables_with_data:
                if table == 'FFBSCANNERDATA04':
                    ffbscannerdata04_found = True
                    print(f"   ✅ FFBSCANNERDATA04: {count:,} records")
                    break
            
            if not ffbscannerdata04_found:
                print(f"   ❌ FFBSCANNERDATA04: No data (table exists but empty)")
            
            # Show any FFBLOADINGCROP tables with data
            loading_tables = [(table, count) for table, count in tables_with_data if 'LOADING' in table.upper()]
            if loading_tables:
                print(f"\n📦 FFBLOADINGCROP tables with data:")
                for table, count in loading_tables:
                    print(f"   - {table}: {count:,} records")
                    
                    # Get detailed sample from first loading table
                    if table == loading_tables[0][0]:
                        print(f"   📋 Sample from {table}:")
                        detailed_sample = connector.get_sample_data(table, limit=1)
                        
                        if detailed_sample and len(detailed_sample) > 0:
                            record = detailed_sample[0]
                            if isinstance(record, dict):
                                for key, value in record.items():
                                    print(f"      {key}: {value}")
            
            # Show any other FFB tables with data
            other_tables = [(table, count) for table, count in tables_with_data 
                          if 'LOADING' not in table.upper() and 'SCANNER' not in table.upper()]
            if other_tables:
                print(f"\n📊 Other FFB tables with data:")
                for table, count in other_tables:
                    print(f"   - {table}: {count:,} records")
        else:
            print("\n⚠️  No FFB tables contain data")
            print("\n🔍 This could mean:")
            print("   - Database is empty/test environment")
            print("   - Data is in different tables")
            print("   - Different database file is used in production")
            
        return len(tables_with_data) > 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
        
    finally:
        if 'connector' in locals() and hasattr(connector, 'close'):
            connector.close()

if __name__ == "__main__":
    print("🔍 Comprehensive check of all FFB-related tables...")
    print("📖 READ-ONLY ACCESS - No data modification")
    print("=" * 60)
    
    success = check_all_ffb_tables()
    
    if success:
        print("\n✅ Found FFB tables with data")
    else:
        print("\n❌ No FFB tables with data found")