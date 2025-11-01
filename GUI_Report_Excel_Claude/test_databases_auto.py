#!/usr/bin/env python3
"""
Automated Database Tester - Test all large databases for FFB data
READ-ONLY ACCESS - No data modification
"""

import os
import glob
import datetime
from pathlib import Path
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def find_large_databases():
    """Find all large database files"""
    base_dir = r"D:\Gawean Rebinmas\Monitoring Database"
    
    print(f"🔍 Searching for large database files in: {base_dir}")
    
    # Find all .fdb files
    fdb_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith('.fdb'):
                full_path = os.path.join(root, file)
                fdb_files.append(full_path)
    
    # Filter by size and get info
    large_databases = []
    for file_path in fdb_files:
        try:
            size = os.path.getsize(file_path)
            
            # Only include files larger than 100MB (very likely to have data)
            if size > 100 * 1024 * 1024:
                mtime = os.path.getmtime(file_path)
                mod_date = datetime.datetime.fromtimestamp(mtime)
                
                large_databases.append({
                    'path': file_path,
                    'size': size,
                    'size_mb': size / (1024 * 1024),
                    'modified': mod_date,
                    'name': os.path.basename(file_path),
                    'relative_path': os.path.relpath(file_path, base_dir)
                })
        except:
            continue
    
    # Sort by modification date (newest first)
    large_databases.sort(key=lambda x: x['modified'], reverse=True)
    
    return large_databases

def test_database_for_ffb(db_path):
    """Test a specific database for FFB data"""
    try:
        # Create connector with this database
        connector = FirebirdConnectorEnhanced()
        original_path = connector.db_path
        connector.db_path = db_path
        
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
        if 'FFBSCANNERDATA04' in ffb_data:
            try:
                sample = connector.get_sample_data('FFBSCANNERDATA04', limit=1)
                if sample and len(sample) > 0:
                    sample_data = sample[0]
            except:
                pass
        
        # Restore original path
        connector.db_path = original_path
        
        return {
            'total_records': total_records,
            'tables_with_data': ffb_data,
            'sample_data': sample_data,
            'connection_success': True
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'connection_success': False
        }

def main():
    """Main function to test all databases"""
    print("🗄️  Automated Database Tester for FFB Data")
    print("📖 READ-ONLY ACCESS - No data modification")
    print("=" * 60)
    
    # Find large databases
    databases = find_large_databases()
    
    if not databases:
        print("❌ No large database files found")
        return
    
    print(f"📊 Found {len(databases)} large database files to test")
    print("=" * 60)
    
    databases_with_ffb = []
    
    for i, db in enumerate(databases):
        print(f"\n🔍 Testing {i+1}/{len(databases)}: {db['name']}")
        print(f"   📁 Path: {db['relative_path']}")
        print(f"   📊 Size: {db['size_mb']:.1f} MB")
        print(f"   📅 Modified: {db['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test the database
        result = test_database_for_ffb(db['path'])
        
        if result and result.get('connection_success'):
            if result['total_records'] > 0:
                print(f"   ✅ Contains {result['total_records']:,} FFB records")
                
                # Show tables with data
                tables_info = []
                for table, count in result['tables_with_data'].items():
                    tables_info.append(f"{table}({count:,})")
                
                print(f"   📋 Tables: {', '.join(tables_info)}")
                
                # Check for FFBSCANNERDATA04
                if 'FFBSCANNERDATA04' in result['tables_with_data']:
                    count = result['tables_with_data']['FFBSCANNERDATA04']
                    print(f"   🎯 FFBSCANNERDATA04: {count:,} records ⭐")
                    
                    # Show sample data
                    if result['sample_data']:
                        sample = result['sample_data']
                        if isinstance(sample, dict):
                            print(f"   📄 Sample fields: {', '.join(list(sample.keys())[:6])}")
                
                databases_with_ffb.append((db, result))
            else:
                print(f"   ❌ No FFB data")
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'Connection failed'
            print(f"   ❌ Error: {error_msg}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📈 SUMMARY: {len(databases_with_ffb)} databases contain FFB data")
    
    if databases_with_ffb:
        print("\n🎯 Databases with FFB data (sorted by record count):")
        
        # Sort by total records
        databases_with_ffb.sort(key=lambda x: x[1]['total_records'], reverse=True)
        
        for db, result in databases_with_ffb:
            print(f"\n📊 {db['name']}")
            print(f"   📁 {db['relative_path']}")
            print(f"   📈 {result['total_records']:,} total FFB records")
            print(f"   📊 {db['size_mb']:.1f} MB")
            
            # Highlight FFBSCANNERDATA04
            if 'FFBSCANNERDATA04' in result['tables_with_data']:
                count = result['tables_with_data']['FFBSCANNERDATA04']
                print(f"   🎯 FFBSCANNERDATA04: {count:,} records")
        
        # Recommend the best database
        best_db, best_result = databases_with_ffb[0]
        print(f"\n🏆 RECOMMENDED DATABASE:")
        print(f"   📁 {best_db['name']}")
        print(f"   📂 Full path: {best_db['path']}")
        print(f"   📈 {best_result['total_records']:,} FFB records")
        
        if 'FFBSCANNERDATA04' in best_result['tables_with_data']:
            count = best_result['tables_with_data']['FFBSCANNERDATA04']
            print(f"   🎯 FFBSCANNERDATA04: {count:,} records ✅")
        
        print(f"\n💡 To use this database, update firebird_connector_enhanced.py:")
        print(f"   Change db_path to: r\"{best_db['path']}\"")
        
    else:
        print("\n❌ No databases found with FFB data")
        print("   This might indicate:")
        print("   - Different table naming convention")
        print("   - Data in different database format")
        print("   - Need to check smaller database files")

if __name__ == "__main__":
    main()