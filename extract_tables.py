#!/usr/bin/env python3
"""
Extract Tables dari output ISQL
Berdasarkan output yang terlihat di log sebelumnya
"""

import re
from datetime import datetime

def extract_tables_from_logs():
    """Extract table names dari log output yang sudah terlihat"""
    
    # Dari log output, kita bisa melihat ada banyak tabel FFB
    # Mari kita buat daftar berdasarkan pattern yang terlihat
    
    print("=== EXTRACTING TABLES FROM PREVIOUS LOGS ===")
    print(f"Time: {datetime.now()}")
    print()
    
    # Tabel-tabel yang terlihat di log output
    observed_tables = [
        'FFBSCANNERDATA01', 'FFBSCANNERDATA02', 'FFBSCANNERDATA03', 'FFBSCANNERDATA04',
        'FFBSCANNERDATA05', 'FFBSCANNERDATA06', 'FFBSCANNERDATA07', 'FFBSCANNERDATA08',
        'FFBSCANNERDATA09', 'FFBSCANNERDATA10', 'FFBSCANNERDATA11', 'FFBSCANNERDATA12',
        'VWFFBSCANNERDATA', 'VWFFBSCANNERDATA01', 'VWFFBSCANNERDATA02', 'VWFFBSCANNERDATA03',
        'VWFFBSCANNERDATA04', 'VWFFBSCANNERDATA05', 'VWFFBSCANNERDATA06', 'VWFFBSCANNERDATA07',
        'VWFFBSCANNERDATA08', 'VWFFBSCANNERDATA09', 'VWFFBSCANNERDATA10', 'VWFFBSCANNERDATA11',
        'VWFFBSCANNERDATA12', 'VWFFBLOADINGCROP', 'VWFFBLOADINGCROP01', 'VWFFBLOADINGCROP02',
        'VWFFBLOADINGCROP03', 'VWFFBLOADINGCROP04', 'VWFFBLOADINGCROP05', 'VWFFBLOADINGCROP06',
        'VWFFBLOADINGCROP07', 'VWFFBLOADINGCROP08', 'VWFFBLOADINGCROP09', 'VWFFBLOADINGCROP10',
        'VWFFBLOADINGCROP11', 'WORKERINFO', 'WORKERWDRS', 'WORKSTATUSVIEW'
    ]
    
    # Kategorisasi tabel
    ffb_scanner_tables = []
    ffb_loading_tables = []
    worker_tables = []
    view_tables = []
    
    for table in observed_tables:
        if 'FFBSCANNERDATA' in table:
            ffb_scanner_tables.append(table)
        elif 'FFBLOADINGCROP' in table:
            ffb_loading_tables.append(table)
        elif 'WORKER' in table:
            worker_tables.append(table)
        elif table.startswith('VW'):
            view_tables.append(table)
    
    print("=== CATEGORIZED TABLES ===")
    print(f"\nFFB Scanner Data Tables ({len(ffb_scanner_tables)}):")
    for table in sorted(ffb_scanner_tables):
        print(f"  - {table}")
    
    print(f"\nFFB Loading Crop Tables ({len(ffb_loading_tables)}):")
    for table in sorted(ffb_loading_tables):
        print(f"  - {table}")
    
    print(f"\nWorker/Employee Tables ({len(worker_tables)}):")
    for table in sorted(worker_tables):
        print(f"  - {table}")
    
    print(f"\nView Tables ({len(view_tables)}):")
    for table in sorted(view_tables):
        if table not in ffb_scanner_tables and table not in ffb_loading_tables:
            print(f"  - {table}")
    
    # Identifikasi tabel yang paling relevan untuk laporan kinerja
    print("\n=== MOST RELEVANT TABLES FOR PERFORMANCE REPORT ===")
    
    # Tabel utama untuk data scanner FFB (berdasarkan bulan)
    current_month_tables = [t for t in ffb_scanner_tables if t.endswith(('10', '11', '12'))]  # Oct, Nov, Dec
    print(f"\nCurrent Period FFB Scanner Tables:")
    for table in current_month_tables:
        print(f"  - {table}")
    
    # Tabel worker untuk mapping karyawan
    print(f"\nWorker Information Tables:")
    for table in worker_tables:
        print(f"  - {table}")
    
    # Simpan hasil analisis
    print(f"\n=== SAVING RESULTS ===")
    with open('extracted_tables_analysis.txt', 'w', encoding='utf-8') as f:
        f.write("=== EXTRACTED TABLES ANALYSIS ===\n")
        f.write(f"Analysis Time: {datetime.now()}\n\n")
        
        f.write("FFB SCANNER DATA TABLES:\n")
        for table in sorted(ffb_scanner_tables):
            f.write(f"  - {table}\n")
        
        f.write(f"\nFFB LOADING CROP TABLES:\n")
        for table in sorted(ffb_loading_tables):
            f.write(f"  - {table}\n")
        
        f.write(f"\nWORKER TABLES:\n")
        for table in sorted(worker_tables):
            f.write(f"  - {table}\n")
        
        f.write(f"\nRECOMMENDED TABLES FOR PERFORMANCE REPORT:\n")
        f.write(f"1. Main FFB Scanner Data: FFBSCANNERDATA10 (October 2025)\n")
        f.write(f"2. Worker Information: WORKERINFO\n")
        f.write(f"3. Worker Status: WORKSTATUSVIEW\n")
        f.write(f"4. Alternative View: VWFFBSCANNERDATA10\n")
    
    print("✓ Results saved to 'extracted_tables_analysis.txt'")
    
    return {
        'ffb_scanner': ffb_scanner_tables,
        'ffb_loading': ffb_loading_tables,
        'worker': worker_tables,
        'recommended': ['FFBSCANNERDATA10', 'WORKERINFO', 'WORKSTATUSVIEW']
    }

if __name__ == "__main__":
    result = extract_tables_from_logs()
    print(f"\n=== SUMMARY ===")
    print(f"Total FFB Scanner tables: {len(result['ffb_scanner'])}")
    print(f"Total Worker tables: {len(result['worker'])}")
    print(f"Recommended tables: {result['recommended']}")