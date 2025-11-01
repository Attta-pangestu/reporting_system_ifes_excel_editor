#!/usr/bin/env python3
"""
Final Table Check - Versi final dengan parsing count yang benar
"""

import os
import sys
from datetime import datetime
from firebird_connector import FirebirdConnector

def extract_count_from_result(result):
    """Extract count value from FirebirdConnector result - Fixed version"""
    try:
        print(f"DEBUG: Extracting count from result: {result}")
        
        if isinstance(result, list) and result:
            # Result is a list of result sets
            first_result_set = result[0]
            if isinstance(first_result_set, dict) and 'rows' in first_result_set:
                rows = first_result_set['rows']
                if rows and isinstance(rows, list):
                    first_row = rows[0]
                    if isinstance(first_row, dict):
                        # Look for COUNT key
                        for key, value in first_row.items():
                            if 'COUNT' in key.upper():
                                count_val = int(value)
                                print(f"DEBUG: Found count {count_val} from key {key}")
                                return count_val
                    elif isinstance(first_row, (list, tuple)) and first_row:
                        count_val = int(first_row[0])
                        print(f"DEBUG: Found count {count_val} from tuple/list")
                        return count_val
        
        elif isinstance(result, dict):
            if 'rows' in result and result['rows']:
                first_row = result['rows'][0]
                if isinstance(first_row, dict):
                    for key, value in first_row.items():
                        if 'COUNT' in key.upper():
                            count_val = int(value)
                            print(f"DEBUG: Found count {count_val} from dict key {key}")
                            return count_val
                elif isinstance(first_row, (list, tuple)) and first_row:
                    count_val = int(first_row[0])
                    print(f"DEBUG: Found count {count_val} from dict tuple/list")
                    return count_val
        
        print("DEBUG: Could not extract count, returning 0")
        return 0
        
    except (ValueError, TypeError, KeyError, IndexError) as e:
        print(f"DEBUG: Exception extracting count: {e}")
        return 0

def final_table_check():
    """Cek tabel dengan parsing count yang diperbaiki"""
    
    db_path = r'D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB'
    username = 'SYSDBA'
    password = 'masterkey'
    
    print("=== FINAL TABLE CHECK ===")
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
                        
                        if sample_result:
                            # Try to determine column count
                            column_count = 0
                            sample_data = None
                            
                            if isinstance(sample_result, list) and sample_result:
                                first_result_set = sample_result[0]
                                if isinstance(first_result_set, dict) and 'rows' in first_result_set:
                                    if first_result_set['rows']:
                                        first_row = first_result_set['rows'][0]
                                        if isinstance(first_row, dict):
                                            column_count = len(first_row)
                                            sample_data = list(first_row.keys())[:5]  # First 5 column names
                                        elif isinstance(first_row, (list, tuple)):
                                            column_count = len(first_row)
                                            sample_data = first_row[:5]  # First 5 values
                            
                            print(f"  Detected {column_count} columns")
                            if sample_data:
                                print(f"  Sample: {sample_data}")
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
                print(f"Exception: {e}")
                
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
        else:
            print("No tables with data found. Checking if tables exist but are empty...")
        
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
        else:
            # Fallback to first existing FFB table
            for table_name in existing_tables:
                if 'FFBSCANNERDATA' in table_name:
                    print(f"  - FFB Data (fallback): {table_name}")
                    main_ffb_table = table_name
                    break
        
        if main_worker_table:
            print(f"  - Worker Data: {main_worker_table}")
        else:
            # Fallback to first existing worker table
            for table_name in existing_tables:
                if 'WORKER' in table_name:
                    print(f"  - Worker Data (fallback): {table_name}")
                    main_worker_table = table_name
                    break
        
        # 5. Simpan hasil
        with open('final_table_check_results.txt', 'w', encoding='utf-8') as f:
            f.write("=== FINAL TABLE CHECK RESULTS ===\\n")
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
        
        print("\\n✓ Results saved to 'final_table_check_results.txt'")
        
        return results
        
    except Exception as e:
        print(f"Error during check: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = final_table_check()
    if results:
        existing_count = sum(1 for info in results.values() if info.get('exists', False))
        data_count = sum(1 for info in results.values() if info.get('has_data', False))
        print(f"\\nCheck complete: {existing_count}/{len(results)} tables found, {data_count} with data")