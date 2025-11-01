#!/usr/bin/env python3
"""
Check all existing tables in the database
Look for any tables that might contain FFB or scanner data
READ-ONLY ACCESS - No data modification
"""

import sys
import os
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def check_all_tables():
    """Check all existing tables in the database"""
    
    try:
        # Initialize database connection
        connector = FirebirdConnectorEnhanced()
        
        # Test connection
        if not connector.test_connection():
            print("❌ Database connection failed")
            return False
            
        print("✅ Database connection successful")
        print("=" * 60)
        
        # Get list of all user tables
        print("🔍 Getting all user tables...")
        
        tables_query = """
        SELECT TRIM(RDB$RELATION_NAME) 
        FROM RDB$RELATIONS 
        WHERE RDB$SYSTEM_FLAG = 0 
        AND RDB$RELATION_TYPE = 0
        ORDER BY RDB$RELATION_NAME
        """
        
        tables_result = connector.execute_query(tables_query)
        
        if tables_result is None:
            print("❌ Error executing tables query")
            return False
            
        if not tables_result:
            print("❌ No user tables found")
            return False
            
        all_tables = [row[0] for row in tables_result if row[0]]
        print(f"📋 Found {len(all_tables)} user tables")
        
        # Look for FFB-related tables
        ffb_related_tables = []
        scanner_related_tables = []
        
        for table in all_tables:
            table_upper = table.upper()
            if 'FFB' in table_upper:
                ffb_related_tables.append(table)
            if 'SCANNER' in table_upper:
                scanner_related_tables.append(table)
        
        print(f"\n🎯 FFB-related tables ({len(ffb_related_tables)}):")
        for table in ffb_related_tables:
            print(f"   - {table}")
            
        print(f"\n📡 Scanner-related tables ({len(scanner_related_tables)}):")
        for table in scanner_related_tables:
            print(f"   - {table}")
        
        # Check for tables with data
        print(f"\n📊 Checking tables for data...")
        tables_with_data = []
        
        # Focus on FFB and scanner tables first
        priority_tables = list(set(ffb_related_tables + scanner_related_tables))
        
        if not priority_tables:
            # If no FFB/scanner tables, check first 20 tables
            priority_tables = all_tables[:20]
            print(f"⚠️  No FFB/Scanner tables found, checking first {len(priority_tables)} tables...")
        
        for table in priority_tables:
            try:
                count_query = f"SELECT COUNT(*) FROM {table}"
                count_result = connector.execute_query(count_query)
                
                if count_result and count_result[0][0] > 0:
                    row_count = count_result[0][0]
                    tables_with_data.append((table, row_count))
                    print(f"✅ {table}: {row_count:,} records")
                    
                    # Show sample data for tables with records
                    if row_count > 0:
                        try:
                            sample_query = f"SELECT FIRST 2 * FROM {table}"
                            sample_result = connector.execute_query(sample_query)
                            
                            if sample_result:
                                print(f"   📄 Sample data from {table}:")
                                
                                # Get column names
                                columns_query = f"""
                                SELECT TRIM(RDB$FIELD_NAME) 
                                FROM RDB$RELATION_FIELDS 
                                WHERE TRIM(RDB$RELATION_NAME) = '{table}'
                                ORDER BY RDB$FIELD_POSITION
                                """
                                columns_result = connector.execute_query(columns_query)
                                
                                if columns_result:
                                    column_names = [col[0] for col in columns_result if col[0]]
                                    print(f"   📊 Columns ({len(column_names)}): {', '.join(column_names[:8])}{'...' if len(column_names) > 8 else ''}")
                                    
                                    # Show first record
                                    if sample_result:
                                        row_data = sample_result[0]
                                        print(f"   📝 Sample record: {str(row_data)[:120]}{'...' if len(str(row_data)) > 120 else ''}")
                                        
                        except Exception as e:
                            print(f"   ⚠️  Error getting sample data: {str(e)}")
                            
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
                
            # Look for month-specific patterns
            month_tables = []
            for table, count in tables_with_data:
                table_upper = table.upper()
                # Look for patterns like 01, 02, 03, 04, etc.
                if any(f'{i:02d}' in table_upper for i in range(1, 13)):
                    month_tables.append((table, count))
                    
            if month_tables:
                print(f"\n📅 Month-specific tables found:")
                for table, count in month_tables:
                    print(f"   - {table}: {count:,} records")
        else:
            print("\n⚠️  No tables contain data")
            
        return len(tables_with_data) > 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
        
    finally:
        if 'connector' in locals() and hasattr(connector, 'close'):
            connector.close()

if __name__ == "__main__":
    print("🔍 Checking all existing tables in database...")
    print("📖 READ-ONLY ACCESS - No data modification")
    print("=" * 60)
    
    success = check_all_tables()
    
    if success:
        print("\n✅ Found existing data in database tables")
    else:
        print("\n❌ No data found in database tables")