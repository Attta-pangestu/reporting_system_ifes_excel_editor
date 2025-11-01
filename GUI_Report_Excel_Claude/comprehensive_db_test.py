#!/usr/bin/env python3
"""
Comprehensive Database Test - Test all databases with different authentication
READ-ONLY ACCESS - No data modification
"""

import os
import glob
import datetime
from pathlib import Path
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def find_all_databases():
    """Find all database files"""
    base_dir = r"D:\Gawean Rebinmas\Monitoring Database"
    
    print(f"🔍 Searching for all database files in: {base_dir}")
    
    # Find all .fdb files
    fdb_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith('.fdb'):
                full_path = os.path.join(root, file)
                fdb_files.append(full_path)
    
    # Get info for all files
    all_databases = []
    for file_path in fdb_files:
        try:
            size = os.path.getsize(file_path)
            mtime = os.path.getmtime(file_path)
            mod_date = datetime.datetime.fromtimestamp(mtime)
            
            all_databases.append({
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
    all_databases.sort(key=lambda x: x['modified'], reverse=True)
    
    return all_databases

def test_database_with_auth(db_path, username='SYSDBA', password='masterkey'):
    """Test a specific database with given credentials"""
    try:
        # Create connector with this database and credentials
        connector = FirebirdConnectorEnhanced(
            db_path=db_path,
            username=username,
            password=password
        )
        
        # Test connection
        if not connector.test_connection():
            return None
        
        # Get all tables
        tables = connector.get_table_list()
        
        # Look for FFB-related tables
        ffb_tables = []
        for table in tables:
            table_upper = table.upper()
            if any(keyword in table_upper for keyword in ['FFB', 'SCANNER', 'LOADING', 'CROP']):
                ffb_tables.append(table)
        
        # Check for data in FFB tables
        ffb_data = {}
        total_records = 0
        
        for table in ffb_tables:
            try:
                count = connector.get_row_count(table)
                if count > 0:
                    ffb_data[table] = count
                    total_records += count
            except:
                continue
        
        # Get sample from any table with data
        sample_data = None
        sample_table = None
        for table, count in ffb_data.items():
            if count > 0:
                try:
                    sample = connector.get_sample_data(table, limit=1)
                    if sample and len(sample) > 0:
                        sample_data = sample[0]
                        sample_table = table
                        break
                except:
                    continue
        
        return {
            'total_tables': len(tables),
            'ffb_tables': ffb_tables,
            'total_records': total_records,
            'tables_with_data': ffb_data,
            'sample_data': sample_data,
            'sample_table': sample_table,
            'connection_success': True,
            'auth_used': f"{username}/{password}"
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'connection_success': False,
            'auth_used': f"{username}/{password}"
        }

def main():
    """Main function to test all databases"""
    print("🗄️  Comprehensive Database Tester for FFB Data")
    print("📖 READ-ONLY ACCESS - No data modification")
    print("=" * 60)
    
    # Find all databases
    databases = find_all_databases()
    
    if not databases:
        print("❌ No database files found")
        return
    
    print(f"📊 Found {len(databases)} database files to test")
    
    # Different authentication combinations to try
    auth_combinations = [
        ('SYSDBA', 'masterkey'),
        ('sysdba', 'masterkey'),
        ('SYSDBA', ''),
        ('admin', 'admin'),
        ('admin', 'password'),
        ('user', 'user'),
    ]
    
    print("=" * 60)
    
    databases_with_ffb = []
    
    for i, db in enumerate(databases):
        print(f"\n🔍 Testing {i+1}/{len(databases)}: {db['name']}")
        print(f"   📁 Path: {db['relative_path']}")
        print(f"   📊 Size: {db['size_mb']:.1f} MB")
        print(f"   📅 Modified: {db['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Try different authentication methods
        result = None
        for username, password in auth_combinations:
            try:
                result = test_database_with_auth(db['path'], username, password)
                if result and result.get('connection_success'):
                    print(f"   ✅ Connected with {username}/{password}")
                    break
            except:
                continue
        
        if result and result.get('connection_success'):
            print(f"   📋 Total tables: {result['total_tables']}")
            
            if result['ffb_tables']:
                print(f"   🎯 FFB-related tables: {len(result['ffb_tables'])}")
                
                # Show first few table names
                table_names = result['ffb_tables'][:5]
                if len(result['ffb_tables']) > 5:
                    table_names.append(f"... and {len(result['ffb_tables'])-5} more")
                print(f"   📝 Tables: {', '.join(table_names)}")
                
                if result['total_records'] > 0:
                    print(f"   📈 Total FFB records: {result['total_records']:,}")
                    
                    # Show tables with data
                    tables_info = []
                    for table, count in result['tables_with_data'].items():
                        tables_info.append(f"{table}({count:,})")
                    
                    print(f"   💾 Data in: {', '.join(tables_info[:3])}")
                    if len(tables_info) > 3:
                        print(f"        ... and {len(tables_info)-3} more tables")
                    
                    # Check for FFBSCANNERDATA04
                    scanner04_tables = [t for t in result['tables_with_data'].keys() 
                                      if 'FFBSCANNERDATA04' in t.upper()]
                    if scanner04_tables:
                        for table in scanner04_tables:
                            count = result['tables_with_data'][table]
                            print(f"   🎯 {table}: {count:,} records ⭐")
                    
                    # Show sample data
                    if result['sample_data'] and result['sample_table']:
                        sample = result['sample_data']
                        if isinstance(sample, dict):
                            fields = list(sample.keys())[:8]  # Show first 8 fields
                            print(f"   📄 Sample from {result['sample_table']}: {', '.join(fields)}")
                    
                    databases_with_ffb.append((db, result))
                else:
                    print(f"   ❌ FFB tables exist but no data")
            else:
                print(f"   ❌ No FFB-related tables")
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'All authentication methods failed'
            print(f"   ❌ Connection failed: {error_msg}")
    
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
            print(f"   🔐 Auth: {result['auth_used']}")
            
            # Highlight FFBSCANNERDATA04
            scanner04_tables = [t for t in result['tables_with_data'].keys() 
                              if 'FFBSCANNERDATA04' in t.upper()]
            if scanner04_tables:
                for table in scanner04_tables:
                    count = result['tables_with_data'][table]
                    print(f"   🎯 {table}: {count:,} records")
        
        # Recommend the best database
        best_db, best_result = databases_with_ffb[0]
        print(f"\n🏆 RECOMMENDED DATABASE:")
        print(f"   📁 {best_db['name']}")
        print(f"   📂 Full path: {best_db['path']}")
        print(f"   📈 {best_result['total_records']:,} FFB records")
        print(f"   🔐 Authentication: {best_result['auth_used']}")
        
        scanner04_tables = [t for t in best_result['tables_with_data'].keys() 
                          if 'FFBSCANNERDATA04' in t.upper()]
        if scanner04_tables:
            for table in scanner04_tables:
                count = best_result['tables_with_data'][table]
                print(f"   🎯 {table}: {count:,} records ✅")
        
        print(f"\n💡 To use this database, update firebird_connector_enhanced.py:")
        print(f"   Change db_path to: r\"{best_db['path']}\"")
        if best_result['auth_used'] != 'SYSDBA/masterkey':
            username, password = best_result['auth_used'].split('/')
            print(f"   Change username to: '{username}'")
            print(f"   Change password to: '{password}'")
        
    else:
        print("\n❌ No databases found with FFB data")
        print("   This might indicate:")
        print("   - Different table naming convention")
        print("   - Data stored in different format")
        print("   - Authentication issues")
        print("   - Database corruption or access restrictions")

if __name__ == "__main__":
    main()