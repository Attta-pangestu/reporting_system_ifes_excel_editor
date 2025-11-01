#!/usr/bin/env python3
"""
Robust Database Analysis untuk Firebird
Menangani masalah parsing dengan lebih baik
"""

import os
import sys
from datetime import datetime
from firebird_connector import FirebirdConnector

def analyze_database_robust():
    """Analisis database dengan error handling yang lebih baik"""
    
    db_path = r'D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB'
    username = 'SYSDBA'
    password = 'masterkey'
    
    print("=== ROBUST DATABASE ANALYSIS ===")
    print(f"Database: {db_path}")
    print(f"Time: {datetime.now()}")
    print()
    
    try:
        connector = FirebirdConnector(db_path=db_path, username=username, password=password)
        
        # Test koneksi dulu
        print("1. Testing connection...")
        if not connector.test_connection():
            print("ERROR: Cannot connect to database!")
            return
        print("✓ Connection successful")
        print()
        
        # Query sederhana untuk mendapatkan daftar tabel
        print("2. Getting table list...")
        table_query = """
        SELECT RDB$RELATION_NAME
        FROM RDB$RELATIONS
        WHERE RDB$SYSTEM_FLAG = 0
        ORDER BY RDB$RELATION_NAME
        """
        
        tables_result = connector.execute_query(table_query, as_dict=False)
        print(f"Raw result type: {type(tables_result)}")
        print(f"Raw result length: {len(tables_result) if tables_result else 0}")
        
        if tables_result:
            # Handle different result formats
            tables = []
            
            # Try to extract table names from different possible formats
            for i, row in enumerate(tables_result):
                print(f"Row {i}: {row} (type: {type(row)})")
                
                if isinstance(row, dict):
                    # Dictionary format
                    for key, value in row.items():
                        if 'RELATION_NAME' in key.upper():
                            table_name = str(value).strip()
                            if table_name and table_name not in tables:
                                tables.append(table_name)
                elif isinstance(row, (list, tuple)):
                    # List/tuple format
                    if len(row) > 0:
                        table_name = str(row[0]).strip()
                        if table_name and table_name not in tables:
                            tables.append(table_name)
                else:
                    # String format
                    table_name = str(row).strip()
                    if table_name and table_name not in tables:
                        tables.append(table_name)
                
                # Limit output for debugging
                if i >= 10:
                    print("... (showing first 10 rows only)")
                    break
            
            print(f"\nExtracted {len(tables)} unique tables:")
            for table in tables[:20]:  # Show first 20 tables
                print(f"  - {table}")
            
            if len(tables) > 20:
                print(f"  ... and {len(tables) - 20} more tables")
            print()
            
            # Cari tabel yang relevan untuk FFB Scanner
            print("3. Identifying relevant tables...")
            ffb_tables = []
            employee_tables = []
            other_relevant = []
            
            for table in tables:
                table_lower = table.lower()
                if any(keyword in table_lower for keyword in ['ffb', 'scanner', 'scan']):
                    ffb_tables.append(table)
                elif any(keyword in table_lower for keyword in ['employee', 'karyawan', 'user', 'pekerja']):
                    employee_tables.append(table)
                elif any(keyword in table_lower for keyword in ['divisi', 'division', 'estate', 'field', 'afdeling', 'blok']):
                    other_relevant.append(table)
            
            print("FFB/Scanner related tables:")
            for table in ffb_tables:
                print(f"  - {table}")
            
            print("\nEmployee related tables:")
            for table in employee_tables:
                print(f"  - {table}")
                
            print("\nOther relevant tables:")
            for table in other_relevant:
                print(f"  - {table}")
            print()
            
            # Simpan hasil ke file
            print("4. Saving analysis results...")
            with open('database_analysis_results.txt', 'w', encoding='utf-8') as f:
                f.write("=== DATABASE ANALYSIS RESULTS ===\n")
                f.write(f"Database: {db_path}\n")
                f.write(f"Analysis Time: {datetime.now()}\n\n")
                
                f.write(f"TOTAL TABLES FOUND: {len(tables)}\n\n")
                
                f.write("ALL TABLES:\n")
                for table in tables:
                    f.write(f"  - {table}\n")
                
                f.write(f"\nFFB/SCANNER TABLES ({len(ffb_tables)}):\n")
                for table in ffb_tables:
                    f.write(f"  - {table}\n")
                
                f.write(f"\nEMPLOYEE TABLES ({len(employee_tables)}):\n")
                for table in employee_tables:
                    f.write(f"  - {table}\n")
                
                f.write(f"\nOTHER RELEVANT TABLES ({len(other_relevant)}):\n")
                for table in other_relevant:
                    f.write(f"  - {table}\n")
            
            print("✓ Analysis results saved to 'database_analysis_results.txt'")
            
            # Coba analisis tabel yang paling mungkin mengandung data FFB
            if ffb_tables or any('ffb' in t.lower() for t in tables):
                print("\n5. Analyzing potential FFB tables...")
                potential_ffb = [t for t in tables if 'ffb' in t.lower() or 'scanner' in t.lower() or 'scan' in t.lower()]
                
                for table in potential_ffb[:3]:  # Analyze first 3 potential tables
                    try:
                        print(f"\n--- Analyzing Table: {table} ---")
                        
                        # Try to get row count
                        count_query = f"SELECT COUNT(*) FROM {table}"
                        count_result = connector.execute_query(count_query, as_dict=False)
                        if count_result:
                            print(f"Row count: {count_result[0] if count_result[0] else 'Unknown'}")
                        
                        # Try to get sample data
                        sample_query = f"SELECT FIRST 2 * FROM {table}"
                        sample_result = connector.execute_query(sample_query, as_dict=False)
                        if sample_result:
                            print(f"Sample data available: {len(sample_result)} rows")
                        
                    except Exception as e:
                        print(f"Error analyzing table {table}: {e}")
            
        else:
            print("ERROR: Could not retrieve table list")
            
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_database_robust()