#!/usr/bin/env python3
"""
Find Databases with Data - Look for databases that contain actual FFB data
READ-ONLY ACCESS - No data modification
"""

import os
import glob
import datetime
from pathlib import Path
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def find_nearby_databases():
    """Find databases in the same directory structure as the current default"""
    current_db = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    current_dir = os.path.dirname(current_db)
    base_dir = os.path.dirname(current_dir)  # Go up one level
    
    print(f"🔍 Current database: {current_db}")
    print(f"🔍 Searching in: {base_dir}")
    
    # Find all .fdb files in the area
    fdb_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith('.fdb'):
                full_path = os.path.join(root, file)
                fdb_files.append(full_path)
    
    # Get info for all files
    databases = []
    for file_path in fdb_files:
        try:
            size = os.path.getsize(file_path)
            mtime = os.path.getmtime(file_path)
            mod_date = datetime.datetime.fromtimestamp(mtime)
            
            databases.append({
                'path': file_path,
                'size': size,
                'size_mb': size / (1024 * 1024),
                'modified': mod_date,
                'name': os.path.basename(file_path),
                'relative_path': os.path.relpath(file_path, base_dir),
                'is_current': file_path == current_db
            })
        except:
            continue
    
    # Sort by modification date (newest first)
    databases.sort(key=lambda x: x['modified'], reverse=True)
    
    return databases

def test_database_for_data(db_path):
    """Test a specific database for actual data"""
    try:
        # Create connector with this database
        connector = FirebirdConnectorEnhanced(db_path=db_path)
        
        # Test connection
        if not connector.test_connection():
            return None
        
        # Get FFB scanner tables
        tables = connector.get_table_list()
        ffb_scanner_tables = [t for t in tables if 'FFBSCANNERDATA' in t.upper()]
        
        # Check for data
        ffb_data = {}
        total_records = 0
        
        for table in ffb_scanner_tables:
            try:
                count = connector.get_row_count(table)
                if count > 0:
                    ffb_data[table] = count
                    total_records += count
            except:
                continue
        
        # Get sample from FFBSCANNERDATA04 if it has data
        sample_data = None
        columns = []
        if 'FFBSCANNERDATA04' in ffb_data:
            try:
                # Get table structure
                table_info = connector.get_table_info('FFBSCANNERDATA04')
                if table_info and 'columns' in table_info:
                    columns = [col['name'] for col in table_info['columns']]
                
                # Get sample data
                sample = connector.get_sample_data('FFBSCANNERDATA04', limit=1)
                if sample and len(sample) > 0:
                    sample_data = sample[0]
            except Exception as e:
                print(f"   Warning: Could not get sample from FFBSCANNERDATA04: {e}")
        
        return {
            'total_records': total_records,
            'tables_with_data': ffb_data,
            'sample_data': sample_data,
            'columns': columns,
            'connection_success': True
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'connection_success': False
        }

def main():
    """Main function to find databases with data"""
    print("🗄️  Find Databases with FFB Data")
    print("📖 READ-ONLY ACCESS - No data modification")
    print("=" * 60)
    
    # Find nearby databases
    databases = find_nearby_databases()
    
    if not databases:
        print("❌ No database files found")
        return
    
    print(f"📊 Found {len(databases)} database files in the area")
    print("=" * 60)
    
    databases_with_data = []
    
    for i, db in enumerate(databases):
        status_icon = "🎯" if db['is_current'] else "📁"
        current_text = " (CURRENT)" if db['is_current'] else ""
        
        print(f"\n{status_icon} Testing {i+1}/{len(databases)}: {db['name']}{current_text}")
        print(f"   📁 Path: {db['relative_path']}")
        print(f"   📊 Size: {db['size_mb']:.1f} MB")
        print(f"   📅 Modified: {db['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test the database
        result = test_database_for_data(db['path'])
        
        if result and result.get('connection_success'):
            if result['total_records'] > 0:
                print(f"   ✅ Contains {result['total_records']:,} FFB records")
                
                # Show tables with data
                tables_info = []
                for table, count in result['tables_with_data'].items():
                    tables_info.append(f"{table}({count:,})")
                
                print(f"   📋 Tables: {', '.join(tables_info[:3])}")
                if len(tables_info) > 3:
                    print(f"        ... and {len(tables_info)-3} more tables")
                
                # Check for FFBSCANNERDATA04
                if 'FFBSCANNERDATA04' in result['tables_with_data']:
                    count = result['tables_with_data']['FFBSCANNERDATA04']
                    print(f"   🎯 FFBSCANNERDATA04: {count:,} records ⭐")
                    
                    # Show columns
                    if result['columns']:
                        print(f"   📄 Columns: {', '.join(result['columns'][:6])}")
                        if len(result['columns']) > 6:
                            print(f"        ... and {len(result['columns'])-6} more columns")
                    
                    # Show sample data
                    if result['sample_data']:
                        sample = result['sample_data']
                        if isinstance(sample, dict):
                            sample_values = []
                            for key, value in list(sample.items())[:4]:
                                sample_values.append(f"{key}={value}")
                            print(f"   📊 Sample: {', '.join(sample_values)}")
                
                databases_with_data.append((db, result))
            else:
                print(f"   ❌ No FFB data (empty tables)")
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'Connection failed'
            print(f"   ❌ Error: {error_msg}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📈 SUMMARY: {len(databases_with_data)} databases contain FFB data")
    
    if databases_with_data:
        print("\n🎯 Databases with FFB data (sorted by record count):")
        
        # Sort by total records
        databases_with_data.sort(key=lambda x: x[1]['total_records'], reverse=True)
        
        for db, result in databases_with_data:
            current_text = " (CURRENT)" if db['is_current'] else ""
            print(f"\n📊 {db['name']}{current_text}")
            print(f"   📁 {db['relative_path']}")
            print(f"   📈 {result['total_records']:,} total FFB records")
            print(f"   📊 {db['size_mb']:.1f} MB")
            
            # Highlight FFBSCANNERDATA04
            if 'FFBSCANNERDATA04' in result['tables_with_data']:
                count = result['tables_with_data']['FFBSCANNERDATA04']
                print(f"   🎯 FFBSCANNERDATA04: {count:,} records")
        
        # Recommend the best database
        best_db, best_result = databases_with_data[0]
        
        if not best_db['is_current']:
            print(f"\n🏆 RECOMMENDED DATABASE (different from current):")
            print(f"   📁 {best_db['name']}")
            print(f"   📂 Full path: {best_db['path']}")
            print(f"   📈 {best_result['total_records']:,} FFB records")
            
            if 'FFBSCANNERDATA04' in best_result['tables_with_data']:
                count = best_result['tables_with_data']['FFBSCANNERDATA04']
                print(f"   🎯 FFBSCANNERDATA04: {count:,} records ✅")
            
            print(f"\n💡 To use this database, update firebird_connector_enhanced.py:")
            print(f"   Change DEFAULT_DATABASE to: r\"{best_db['path']}\"")
        else:
            print(f"\n✅ Current database already has the most data!")
        
    else:
        print("\n❌ No databases found with FFB data in this area")
        print("   Suggestions:")
        print("   - Check if data is in a different database format")
        print("   - Look for databases in other directories")
        print("   - Verify if data needs to be imported first")

if __name__ == "__main__":
    main()