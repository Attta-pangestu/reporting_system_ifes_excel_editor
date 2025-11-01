#!/usr/bin/env python3
"""
Database Selector - Choose from available database files
READ-ONLY ACCESS - No data modification
"""

import os
import glob
import datetime
from pathlib import Path
from firebird_connector_enhanced import FirebirdConnectorEnhanced

class DatabaseSelector:
    def __init__(self):
        self.base_dir = r"D:\Gawean Rebinmas\Monitoring Database"
        self.available_databases = []
        
    def find_databases(self):
        """Find all available database files"""
        print(f"🔍 Searching for database files in: {self.base_dir}")
        
        # Find all .fdb files
        fdb_files = []
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                if file.lower().endswith('.fdb'):
                    full_path = os.path.join(root, file)
                    fdb_files.append(full_path)
        
        # Filter and sort by size
        db_info = []
        for file_path in fdb_files:
            try:
                size = os.path.getsize(file_path)
                mtime = os.path.getmtime(file_path)
                mod_date = datetime.datetime.fromtimestamp(mtime)
                
                # Only include files larger than 10MB (likely to have data)
                if size > 10 * 1024 * 1024:
                    db_info.append({
                        'path': file_path,
                        'size': size,
                        'size_mb': size / (1024 * 1024),
                        'modified': mod_date,
                        'name': os.path.basename(file_path),
                        'relative_path': os.path.relpath(file_path, self.base_dir)
                    })
            except:
                continue
        
        # Sort by modification date (newest first)
        db_info.sort(key=lambda x: x['modified'], reverse=True)
        self.available_databases = db_info
        
        return db_info
    
    def display_databases(self):
        """Display available databases for selection"""
        if not self.available_databases:
            self.find_databases()
        
        print(f"\n📊 Found {len(self.available_databases)} large database files:")
        print("=" * 80)
        
        for i, db in enumerate(self.available_databases):
            print(f"{i+1:2d}. {db['name']}")
            print(f"    📁 Path: {db['relative_path']}")
            print(f"    📊 Size: {db['size_mb']:.1f} MB")
            print(f"    📅 Modified: {db['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Check if this is the current default
            current_db = r"Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
            if db['relative_path'].replace('\\', '/') == current_db.replace('\\', '/'):
                print(f"    ⭐ CURRENT DEFAULT")
            
            print()
        
        return self.available_databases
    
    def test_database(self, db_path):
        """Test a database for FFB data"""
        print(f"\n🔍 Testing database: {os.path.basename(db_path)}")
        print("=" * 60)
        
        try:
            # Create temporary connector with this database
            connector = FirebirdConnectorEnhanced()
            original_path = connector.db_path
            connector.db_path = db_path
            
            # Test connection
            if not connector.test_connection():
                print("❌ Connection failed")
                return False
            
            print("✅ Connection successful")
            
            # Get FFB tables
            tables = connector.get_table_list()
            ffb_tables = [t for t in tables if 'FFB' in t.upper() and 'SCANNER' in t.upper()]
            
            print(f"📊 Found {len(ffb_tables)} FFBSCANNERDATA tables")
            
            # Check for data in FFB tables
            tables_with_data = []
            for table in ffb_tables:
                try:
                    count = connector.get_row_count(table)
                    if count > 0:
                        tables_with_data.append((table, count))
                except:
                    continue
            
            if tables_with_data:
                print(f"🎯 {len(tables_with_data)} tables contain data:")
                total_records = 0
                
                for table, count in tables_with_data:
                    print(f"   - {table}: {count:,} records")
                    total_records += count
                
                print(f"\n📈 Total FFB records: {total_records:,}")
                
                # Check FFBSCANNERDATA04 specifically
                ffb04_found = False
                for table, count in tables_with_data:
                    if table == 'FFBSCANNERDATA04':
                        ffb04_found = True
                        print(f"🎯 FFBSCANNERDATA04: {count:,} records ✅")
                        
                        # Get sample data
                        sample = connector.get_sample_data('FFBSCANNERDATA04', limit=1)
                        if sample and len(sample) > 0:
                            record = sample[0]
                            if isinstance(record, dict):
                                print(f"📋 Sample record from FFBSCANNERDATA04:")
                                for key, value in list(record.items())[:8]:  # Show first 8 fields
                                    print(f"   {key}: {value}")
                        break
                
                if not ffb04_found:
                    print(f"⚠️  FFBSCANNERDATA04: No data")
                
                return True
            else:
                print("❌ No FFB tables contain data")
                return False
                
        except Exception as e:
            print(f"❌ Error testing database: {str(e)}")
            return False
        finally:
            if 'connector' in locals():
                connector.db_path = original_path  # Restore original path
                if hasattr(connector, 'close'):
                    connector.close()
    
    def select_database(self):
        """Interactive database selection"""
        databases = self.display_databases()
        
        if not databases:
            print("❌ No suitable databases found")
            return None
        
        while True:
            try:
                print(f"\n🎯 Select a database to test (1-{len(databases)}) or 0 to exit:")
                choice = input("Enter choice: ").strip()
                
                if choice == '0':
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(databases):
                    selected_db = databases[choice_num - 1]
                    print(f"\n✅ Selected: {selected_db['name']}")
                    
                    # Test the selected database
                    if self.test_database(selected_db['path']):
                        return selected_db
                    else:
                        print(f"\n⚠️  Database has no FFB data. Try another?")
                        continue
                else:
                    print(f"❌ Invalid choice. Please enter 1-{len(databases)} or 0")
                    
            except ValueError:
                print("❌ Invalid input. Please enter a number")
            except KeyboardInterrupt:
                print("\n\n👋 Cancelled by user")
                return None

def main():
    """Main function for interactive database selection"""
    print("🗄️  Database Selector for FFB Analysis")
    print("📖 READ-ONLY ACCESS - No data modification")
    print("=" * 60)
    
    selector = DatabaseSelector()
    
    # Show current default database status
    print("🔍 Current default database status:")
    current_connector = FirebirdConnectorEnhanced()
    print(f"   Path: {current_connector.db_path}")
    
    if current_connector.test_connection():
        tables = current_connector.get_table_list()
        ffb_tables = [t for t in tables if 'FFB' in t.upper() and 'SCANNER' in t.upper()]
        
        ffb_data_count = 0
        for table in ffb_tables:
            try:
                count = current_connector.get_row_count(table)
                ffb_data_count += count
            except:
                continue
        
        if ffb_data_count > 0:
            print(f"   Status: ✅ Contains {ffb_data_count:,} FFB records")
        else:
            print(f"   Status: ❌ No FFB data (empty database)")
    else:
        print(f"   Status: ❌ Connection failed")
    
    current_connector.close()
    
    # Interactive selection
    selected = selector.select_database()
    
    if selected:
        print(f"\n🎉 Successfully selected database with FFB data!")
        print(f"📁 Path: {selected['path']}")
        print(f"📊 Size: {selected['size_mb']:.1f} MB")
        print(f"\n💡 To use this database, update the connector configuration:")
        print(f"   db_path = r\"{selected['path']}\"")
    else:
        print(f"\n👋 No database selected")

if __name__ == "__main__":
    main()