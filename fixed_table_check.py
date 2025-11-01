#!/usr/bin/env python3
"""
Fixed Table Check - Perbaikan untuk menangani format hasil FirebirdConnector
"""

import os
import sys
from datetime import datetime
from firebird_connector import FirebirdConnector

def extract_count_from_result(result):
    """Extract count value from FirebirdConnector result"""
    try:
        if isinstance(result, dict):
            if 'rows' in result and result['rows']:
                first_row = result['rows'][0]
                if isinstance(first_row, dict):
                    # Look for count-like keys
                    for key, value in first_row.items():
                        if 'COUNT' in key.upper():
                            return int(value)
                elif isinstance(first_row, (list, tuple)) and first_row:
                    return int(first_row[0])
        elif isinstance(result, (list, tuple)) and result:
            first_item = result[0]
            if isinstance(first_item, dict):
                for key, value in first_item.items():
                    if 'COUNT' in key.upper():
                        return int(value)
            elif isinstance(first_item, (list, tuple)) and first_item:
                return int(first_item[0])
            else:
                return int(first_item)
        
        return 0
    except (ValueError, TypeError, KeyError, IndexError):
        return 0

def fixed_table_check():
    """Cek tabel dengan penanganan hasil yang diperbaiki"""
    
    db_path = r'D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB'
    username = 'SYSDBA'
    password = 'masterkey'
    
    print("=== FIXED TABLE CHECK ===")
    print(f"Database: {db_path}")
    print(f"Time: {datetime.now()}")
    print()
    
    # Tabel yang akan dicek
    target_tables = [
        'FFBSCANNERDATA10',  # Data scanner FFB Oktober 2025
        'FFBSCANNERDATA11',  # Data scanner FFB November 2025
        'WORKERINFO',        # Informasi karyawan
        'WORKERWDRS',        # Worker details
        'VWFFBSCANNERDATA10' # View untuk data scanner
    ]
    
    try:
        connector = FirebirdConnector(db_path=db_path, username=username, password=password)
        
        # Test koneksi
        print("1. Testing connection...")
        if not connector.test_connection():
            print("ERROR: Cannot connect to database!")
            return
        print("✓ Connection successful")
        print()
        
        results = {}
        
        for table_name in target_tables:
            print(f"--- Checking Table: {table_name} ---")
            
            try:
                # 1. Cek apakah tabel ada dengan query sederhana
                count_query = f"SELECT COUNT(*) FROM {table_name}"
                print(f"Executing: {count_query}")
                
                count_result = connector.execute_query(count_query, as_dict=False)
                print(f"Raw result type: {type(count_result)}")
                print(f"Raw result: {count_result}")
                
                record_count = extract_count_from_result(count_result)
                print(f"Extracted count: {record_count}")
                
                if record_count >= 0:  # 0 or positive means table exists
                    print(f"✓ Table exists with {record_count:,} records")
                    
                    # 2. Ambil sample data jika ada records
                    if record_count > 0:
                        print("Getting sample data...")
                        sample_query = f"SELECT FIRST 1 * FROM {table_name}"
                        sample_result = connector.execute_query(sample_query, as_dict=False)
                        
                        print(f"Sample result type: {type(sample_result)}")
                        
                        if sample_result:
                            # Try to determine column count
                            column_count = 0
                            if isinstance(sample_result, dict) and 'rows' in sample_result:
                                if sample_result['rows']:
                                    first_row = sample_result['rows'][0]
                                    if isinstance(first_row, dict):
                                        column_count = len(first_row)
                                    elif isinstance(first_row, (list, tuple)):
                                        column_count = len(first_row)
                            elif isinstance(sample_result, (list, tuple)) and sample_result:
                                first_row = sample_result[0]
                                if isinstance(first_row, dict):
                                    column_count = len(first_row)
                                elif isinstance(first_row, (list, tuple)):
                                    column_count = len(first_row)
                            
                            print(f"  Detected {column_count} columns")
                        else:
                            print("  No sample data retrieved")
                    else:
                        print("  Table is empty")
                    
                    results[table_name] = {
                        'exists': True,
                        'record_count': record_count,
                        'has_data': record_count > 0
                    }
                    
                else:
                    print(f"✗ Could not get count for table {table_name}")
                    results[table_name] = {'exists': False, 'error': 'Count query failed'}
                
            except Exception as e:
                error_msg = str(e)
                print(f"Exception details: {e}")
                print(f"Exception type: {type(e)}")
                
                if any(keyword in error_msg.lower() for keyword in ['table unknown', 'doesn\'t exist', 'not found', 'invalid']):
                    print(f"✗ Table {table_name} does not exist")
                    results[table_name] = {'exists': False, 'error': 'Table not found'}
                else:
                    print(f"✗ Error checking table {table_name}: {e}")
                    results[table_name] = {'exists': False, 'error': error_msg}
            
            print()
        
        # 3. Ringkasan hasil
        print("=== SUMMARY ===")
        existing_tables = []
        tables_with_data = []
        
        for table_name, info in results.items():
            if info.get('exists', False):
                existing_tables.append(table_name)
                if info.get('has_data', False):
                    tables_with_data.append((table_name, info['record_count']))
                    print(f"✓ {table_name}: {info['record_count']:,} records")
                else:
                    print(f"○ {table_name}: exists but empty")
            else:
                print(f"✗ {table_name}: {info.get('error', 'not found')}")
        
        print(f"\\nFound {len(existing_tables)} existing tables")
        print(f"Found {len(tables_with_data)} tables with data")
        
        # 4. Rekomendasi berdasarkan hasil
        print("\\n=== RECOMMENDATIONS ===")
        
        if tables_with_data:
            print("Available data sources for performance report:")
            for table_name, count in tables_with_data:
                if 'FFBSCANNERDATA' in table_name:
                    print(f"  - {table_name}: Main transaction data ({count:,} records)")
                elif 'WORKER' in table_name:
                    print(f"  - {table_name}: Employee information ({count:,} records)")
        
        # Tentukan tabel utama yang akan digunakan
        main_ffb_table = None
        main_worker_table = None
        
        for table_name, count in tables_with_data:
            if 'FFBSCANNERDATA' in table_name and main_ffb_table is None:
                main_ffb_table = table_name
            elif 'WORKER' in table_name and main_worker_table is None:
                main_worker_table = table_name
        
        print(f"\\nRecommended main tables:")
        if main_ffb_table:
            print(f"  - FFB Data: {main_ffb_table}")
        if main_worker_table:
            print(f"  - Worker Data: {main_worker_table}")
        
        # 5. Simpan hasil
        with open('fixed_table_check_results.txt', 'w', encoding='utf-8') as f:
            f.write("=== FIXED TABLE CHECK RESULTS ===\\n")
            f.write(f"Database: {db_path}\\n")
            f.write(f"Check Time: {datetime.now()}\\n\\n")
            
            f.write("TABLE STATUS:\\n")
            for table_name, info in results.items():
                if info.get('exists', False):
                    if info.get('has_data', False):
                        f.write(f"✓ {table_name}: {info['record_count']:,} records\\n")
                    else:
                        f.write(f"○ {table_name}: exists but empty\\n")
                else:
                    f.write(f"✗ {table_name}: {info.get('error', 'not found')}\\n")
            
            f.write(f"\\nRECOMMENDED TABLES:\\n")
            if main_ffb_table:
                f.write(f"Main FFB Data: {main_ffb_table}\\n")
            if main_worker_table:
                f.write(f"Main Worker Data: {main_worker_table}\\n")
        
        print("\\n✓ Results saved to 'fixed_table_check_results.txt'")
        
        return results
        
    except Exception as e:
        print(f"Error during check: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = fixed_table_check()
    if results:
        existing_count = sum(1 for info in results.values() if info.get('exists', False))
        print(f"\\nCheck complete: {existing_count}/{len(results)} tables found")