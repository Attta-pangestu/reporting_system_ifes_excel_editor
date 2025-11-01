#!/usr/bin/env python3
"""
Script to investigate FFBSCANNERDATA10 field structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced
from database_helper import (
    execute_query_with_extraction, 
    get_sample_data,
    normalize_data_row,
    get_table_count
)

def debug_ffb_fields():
    """Debug FFBSCANNERDATA10 field structure"""
    
    # Initialize connector
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    connector = FirebirdConnectorEnhanced(db_path)
    
    print("=== Debugging FFBSCANNERDATA10 Field Structure ===")
    
    # Test 1: Get sample data and examine all columns
    print("\n1. Sample FFBSCANNERDATA10 data:")
    try:
        sample_data = get_sample_data(connector, "FFBSCANNERDATA10", limit=3)
        print(f"   Sample records: {len(sample_data)}")
        
        if sample_data:
            # Show all columns in first record
            first_record = sample_data[0]
            print(f"   All columns in first record:")
            for key, value in first_record.items():
                print(f"     {key}: {value}")
            
            # Look for field-related columns
            field_columns = []
            for key in first_record.keys():
                if any(term in key.upper() for term in ['FIELD', 'DIV', 'AREA', 'BLOCK']):
                    field_columns.append(key)
            
            print(f"\n   Field-related columns: {field_columns}")
            
            # Show values for field-related columns in all sample records
            if field_columns:
                print(f"\n   Values for field-related columns:")
                for i, record in enumerate(sample_data):
                    print(f"   Record {i+1}:")
                    for col in field_columns:
                        print(f"     {col}: {record.get(col, 'N/A')}")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Check for non-null field values
    print("\n2. Checking for non-null field values:")
    
    field_check_queries = [
        "SELECT DISTINCT FIELDID FROM FFBSCANNERDATA10 WHERE FIELDID IS NOT NULL AND FIELDID != '' LIMIT 5",
        "SELECT DISTINCT DIVID FROM FFBSCANNERDATA10 WHERE DIVID IS NOT NULL AND DIVID != '' LIMIT 5",
        "SELECT DISTINCT AREAID FROM FFBSCANNERDATA10 WHERE AREAID IS NOT NULL AND AREAID != '' LIMIT 5",
        "SELECT DISTINCT BLOCKID FROM FFBSCANNERDATA10 WHERE BLOCKID IS NOT NULL AND BLOCKID != '' LIMIT 5"
    ]
    
    for query in field_check_queries:
        try:
            results = execute_query_with_extraction(connector, query)
            column_name = query.split('DISTINCT ')[1].split(' FROM')[0]
            values = [r[column_name] for r in results if r.get(column_name)]
            print(f"   {column_name}: {values}")
        except Exception as e:
            print(f"   {query.split('DISTINCT ')[1].split(' FROM')[0]}: Error - {e}")
    
    # Test 3: Try different JOIN approaches with CRDIVISION
    print("\n3. Testing JOIN approaches with CRDIVISION:")
    
    join_tests = [
        # Test with FIELDID
        """
        SELECT f.SCANUSERID, f.FIELDID, c.VNAME, c.LENTOCRMK
        FROM FFBSCANNERDATA10 f
        LEFT JOIN CRDIVISION c ON CAST(f.FIELDID AS INTEGER) = CAST(c."ID         O" AS INTEGER)
        WHERE f.SCANUSERID <= 3
        """,
        
        # Test with DIVID  
        """
        SELECT f.SCANUSERID, f.DIVID, c.VNAME, c.LENTOCRMK
        FROM FFBSCANNERDATA10 f
        LEFT JOIN CRDIVISION c ON CAST(f.DIVID AS INTEGER) = CAST(c."ID         O" AS INTEGER)
        WHERE f.SCANUSERID <= 3
        """,
        
        # Test with AREAID
        """
        SELECT f.SCANUSERID, f.AREAID, c.VNAME, c.LENTOCRMK
        FROM FFBSCANNERDATA10 f
        LEFT JOIN CRDIVISION c ON CAST(f.AREAID AS INTEGER) = CAST(c."ID         O" AS INTEGER)
        WHERE f.SCANUSERID <= 3
        """,
        
        # Test with BLOCKID
        """
        SELECT f.SCANUSERID, f.BLOCKID, c.VNAME, c.LENTOCRMK
        FROM FFBSCANNERDATA10 f
        LEFT JOIN CRDIVISION c ON CAST(f.BLOCKID AS INTEGER) = CAST(c."ID         O" AS INTEGER)
        WHERE f.SCANUSERID <= 3
        """
    ]
    
    for i, query in enumerate(join_tests):
        try:
            results = execute_query_with_extraction(connector, query)
            join_type = ['FIELDID', 'DIVID', 'AREAID', 'BLOCKID'][i]
            print(f"   JOIN with {join_type}: {len(results)} records")
            
            if results:
                for j, record in enumerate(results[:2]):
                    normalized = normalize_data_row(record)
                    print(f"     Record {j+1}: {normalized}")
        
        except Exception as e:
            join_type = ['FIELDID', 'DIVID', 'AREAID', 'BLOCKID'][i]
            print(f"   JOIN with {join_type}: Error - {e}")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    debug_ffb_fields()