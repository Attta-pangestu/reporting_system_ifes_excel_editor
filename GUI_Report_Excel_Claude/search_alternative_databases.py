#!/usr/bin/env python3
"""
Search for database files in alternative locations that might contain FFB data.
This script will search broader directory structures and check for backup databases.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import subprocess

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def search_database_files(root_paths):
    """Search for database files in multiple root paths"""
    database_files = []
    extensions = ['.fdb', '.gdb', '.db']
    
    for root_path in root_paths:
        if not os.path.exists(root_path):
            print(f"Path does not exist: {root_path}")
            continue
            
        print(f"\nSearching in: {root_path}")
        
        for root, dirs, files in os.walk(root_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        database_files.append({
                            'path': file_path,
                            'name': file,
                            'size_mb': size / (1024 * 1024),
                            'modified': modified,
                            'directory': root
                        })
                    except Exception as e:
                        print(f"Error accessing {file_path}: {e}")
    
    return database_files

def test_database_for_ffb_data(db_path):
    """Test a database for FFB data"""
    try:
        print(f"\nTesting database: {db_path}")
        
        # Try to connect with default credentials
        connector = FirebirdConnectorEnhanced(db_path=db_path)
        
        if not connector.test_connection():
            print(f"  ❌ Failed to connect to {db_path}")
            return False, "Connection failed"
        
        print(f"  ✅ Connected successfully")
        
        # Check for FFB tables
        ffb_tables = []
        tables = connector.get_table_list()
        
        for table in tables:
            if 'FFB' in table.upper() or 'SCANNER' in table.upper():
                ffb_tables.append(table)
        
        if not ffb_tables:
            print(f"  ❌ No FFB tables found")
            return False, "No FFB tables"
        
        print(f"  ✅ Found {len(ffb_tables)} FFB tables: {ffb_tables[:5]}...")
        
        # Check for data in FFB tables
        data_found = False
        sample_data = {}
        
        for table in ffb_tables[:3]:  # Check first 3 tables
            try:
                query = f"SELECT FIRST 5 * FROM {table}"
                result = connector.execute_query(query)
                
                if result and len(result) > 0:
                    data_found = True
                    sample_data[table] = len(result)
                    print(f"  ✅ {table}: {len(result)} records found")
                else:
                    print(f"  ❌ {table}: No data")
                    
            except Exception as e:
                print(f"  ❌ Error querying {table}: {e}")
        
        if data_found:
            return True, f"Data found in {len(sample_data)} tables: {sample_data}"
        else:
            return False, "Tables exist but no data found"
            
    except Exception as e:
        print(f"  ❌ Error testing database: {e}")
        return False, f"Error: {e}"

def main():
    """Main function to search and test databases"""
    print("🔍 Searching for database files in alternative locations...")
    
    # Define search paths
    search_paths = [
        r"D:\Gawean Rebinmas\Monitoring Database",
        r"D:\Gawean Rebinmas",
        r"C:\Program Files\Firebird",
        r"C:\Firebird",
        r"D:\Database",
        r"D:\Backup",
        r"D:\Data"
    ]
    
    # Search for database files
    database_files = search_database_files(search_paths)
    
    if not database_files:
        print("❌ No database files found in alternative locations")
        return
    
    print(f"\n📊 Found {len(database_files)} database files")
    
    # Sort by size (largest first) and modification date (newest first)
    database_files.sort(key=lambda x: (x['size_mb'], x['modified']), reverse=True)
    
    # Display found databases
    print("\n📋 Database files found:")
    for i, db in enumerate(database_files[:20]):  # Show top 20
        print(f"{i+1:2d}. {db['name']}")
        print(f"    Path: {db['path']}")
        print(f"    Size: {db['size_mb']:.1f} MB")
        print(f"    Modified: {db['modified']}")
        print(f"    Directory: {db['directory']}")
        print()
    
    # Test databases with data
    print("\n🧪 Testing databases for FFB data...")
    databases_with_data = []
    
    for db in database_files:
        # Skip very small databases (likely empty)
        if db['size_mb'] < 0.5:
            continue
            
        success, message = test_database_for_ffb_data(db['path'])
        
        if success:
            databases_with_data.append({
                'path': db['path'],
                'name': db['name'],
                'size_mb': db['size_mb'],
                'modified': db['modified'],
                'message': message
            })
    
    # Report results
    print(f"\n📈 RESULTS:")
    print(f"Total databases found: {len(database_files)}")
    print(f"Databases tested: {len([db for db in database_files if db['size_mb'] >= 0.5])}")
    print(f"Databases with FFB data: {len(databases_with_data)}")
    
    if databases_with_data:
        print(f"\n✅ DATABASES WITH FFB DATA:")
        for i, db in enumerate(databases_with_data):
            print(f"{i+1}. {db['name']}")
            print(f"   Path: {db['path']}")
            print(f"   Size: {db['size_mb']:.1f} MB")
            print(f"   Modified: {db['modified']}")
            print(f"   Data: {db['message']}")
            print()
            
        # Save results to file
        results_file = "alternative_databases_with_data.txt"
        with open(results_file, 'w') as f:
            f.write("DATABASES WITH FFB DATA FOUND:\n")
            f.write("=" * 50 + "\n\n")
            
            for i, db in enumerate(databases_with_data):
                f.write(f"{i+1}. {db['name']}\n")
                f.write(f"   Path: {db['path']}\n")
                f.write(f"   Size: {db['size_mb']:.1f} MB\n")
                f.write(f"   Modified: {db['modified']}\n")
                f.write(f"   Data: {db['message']}\n\n")
        
        print(f"📄 Results saved to: {results_file}")
        
    else:
        print(f"\n❌ No databases with FFB data found in alternative locations")
        print("   This suggests that:")
        print("   1. FFB data might be stored in a different format")
        print("   2. Data might be in a different database system")
        print("   3. Data might need to be imported/generated")
        print("   4. Different authentication credentials might be needed")

if __name__ == "__main__":
    main()