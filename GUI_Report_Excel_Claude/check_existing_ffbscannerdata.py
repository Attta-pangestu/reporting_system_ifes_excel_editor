#!/usr/bin/env python3
"""
Check existing FFBSCANNERDATA tables for actual data
Focus on month-specific tables like FFBSCANNERDATA04
READ-ONLY ACCESS - No data modification
"""

import sys
import os
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def check_ffbscannerdata_tables():
    """Check existing FFBSCANNERDATA tables for data"""
    
    try:
        # Initialize database connection
        connector = FirebirdConnectorEnhanced()
        
        # Test connection
        if not connector.test_connection():
            print("❌ Database connection failed")
            return False
            
        print("✅ Database connection successful")
        print("=" * 60)
        
        # Check for FFBSCANNERDATA tables
        print("🔍 Checking FFBSCANNERDATA tables...")
        
        # Get list of all tables
        tables_query = """
        SELECT TRIM(RDB$RELATION_NAME) 
        FROM RDB$RELATIONS 
        WHERE RDB$SYSTEM_FLAG = 0 
        AND TRIM(RDB$RELATION_NAME) STARTING WITH 'FFBSCANNERDATA'
        ORDER BY RDB$RELATION_NAME
        """
        
        tables_result = connector.execute_query(tables_query)
        
        if tables_result is None:
            print("❌ Error executing tables query")
            return False
        
        if not tables_result:
            print("❌ No FFBSCANNERDATA tables found")
            return False
            
        ffb_tables = [row[0] for row in tables_result if row[0]]  # Remove any None values
        print(f"📋 Found {len(ffb_tables)} FFBSCANNERDATA tables:")
        
        for table in ffb_tables:
            print(f"   - {table}")
        
        print("\n" + "=" * 60)
        
        # Check each table for data
        tables_with_data = []
        
        for table in ffb_tables:
            try:
                count_query = f"SELECT COUNT(*) FROM {table}"
                count_result = connector.execute_query(count_query)
                
                if count_result and count_result[0][0] > 0:
                    row_count = count_result[0][0]
                    tables_with_data.append((table, row_count))
                    print(f"✅ {table}: {row_count:,} records")
                    
                    # Show sample data for tables with records
                    if row_count > 0:
                        sample_query = f"SELECT FIRST 3 * FROM {table}"
                        sample_result = connector.execute_query(sample_query)
                        
                        if sample_result:
                            print(f"   📄 Sample data from {table}:")
                            
                            # Get column names
                            columns_query = f"""
                            SELECT RDB$FIELD_NAME 
                            FROM RDB$RELATION_FIELDS 
                            WHERE RDB$RELATION_NAME = '{table}'
                            ORDER BY RDB$FIELD_POSITION
                            """
                            columns_result = connector.execute_query(columns_query)
                            
                            if columns_result:
                                column_names = [col[0].strip() for col in columns_result]
                                print(f"   📊 Columns: {', '.join(column_names[:10])}{'...' if len(column_names) > 10 else ''}")
                                
                                # Show first few records
                                for i, row in enumerate(sample_result[:2]):
                                    print(f"   Record {i+1}: {str(row)[:100]}{'...' if len(str(row)) > 100 else ''}")
                            
                        print()
                else:
                    print(f"⚪ {table}: 0 records")
                    
            except Exception as e:
                print(f"❌ Error checking {table}: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"📈 Summary: {len(tables_with_data)} tables contain data")
        
        if tables_with_data:
            print("\n🎯 Tables with data:")
            for table, count in tables_with_data:
                print(f"   - {table}: {count:,} records")
                
            # Focus on FFBSCANNERDATA04 if it exists
            ffbscannerdata04_found = False
            for table, count in tables_with_data:
                if 'FFBSCANNERDATA04' in table:
                    ffbscannerdata04_found = True
                    print(f"\n🎯 FFBSCANNERDATA04 found with {count:,} records!")
                    
                    # Get detailed info about FFBSCANNERDATA04
                    try:
                        detail_query = f"""
                        SELECT FIRST 5 
                            SCANUSERID, DIVID, FIELDID, TRANSDATE,
                            RIPEBCH, BLACKBCH, ROTTENBCH
                        FROM {table}
                        ORDER BY TRANSDATE DESC
                        """
                        detail_result = connector.execute_query(detail_query)
                        
                        if detail_result:
                            print(f"   📋 Recent records from {table}:")
                            print("   SCANUSERID | DIVID | FIELDID | TRANSDATE | RIPEBCH | BLACKBCH | ROTTENBCH")
                            print("   " + "-" * 70)
                            
                            for row in detail_result:
                                print(f"   {str(row[0]):<10} | {str(row[1]):<5} | {str(row[2]):<7} | {str(row[3]):<10} | {str(row[4]):<7} | {str(row[5]):<8} | {str(row[6])}")
                                
                    except Exception as e:
                        print(f"   ❌ Error getting details: {str(e)}")
            
            if not ffbscannerdata04_found:
                print("\n⚠️  FFBSCANNERDATA04 not found, but other FFBSCANNERDATA tables have data")
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
    print("🔍 Checking existing FFBSCANNERDATA tables...")
    print("📖 READ-ONLY ACCESS - No data modification")
    print("=" * 60)
    
    success = check_ffbscannerdata_tables()
    
    if success:
        print("\n✅ Found existing data in FFBSCANNERDATA tables")
    else:
        print("\n❌ No data found in FFBSCANNERDATA tables")