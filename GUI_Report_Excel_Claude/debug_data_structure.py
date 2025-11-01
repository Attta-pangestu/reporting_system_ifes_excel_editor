#!/usr/bin/env python3
"""
Debug Data Structure Script
Investigate why some queries are still returning 0 rows
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def debug_data_structure():
    """Debug the data structure to understand the issues"""
    
    print("Debugging Data Structure")
    print("=" * 50)
    
    # Initialize database connection
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    
    try:
        connector = FirebirdConnectorEnhanced(db_path)
        print(f"✓ Connected to database: {db_path}")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    
    # Check FFBSCANNERDATA10 table
    print(f"\n1. Checking FFBSCANNERDATA10 table:")
    print("-" * 40)
    
    try:
        # Count total records
        result = connector.execute_query("SELECT COUNT(*) FROM FFBSCANNERDATA10")
        total_records = result[0][0] if result else 0
        print(f"   Total records in FFBSCANNERDATA10: {total_records}")
        
        # Check date range
        result = connector.execute_query("""
            SELECT MIN(TRANSDATE), MAX(TRANSDATE) 
            FROM FFBSCANNERDATA10 
            WHERE TRANSDATE IS NOT NULL
        """)
        if result and result[0][0]:
            print(f"   Date range: {result[0][0]} to {result[0][1]}")
        else:
            print(f"   No valid dates found")
        
        # Check October 2025 data
        result = connector.execute_query("""
            SELECT COUNT(*) 
            FROM FFBSCANNERDATA10 
            WHERE TRANSDATE >= '2025-10-01' AND TRANSDATE <= '2025-10-31'
        """)
        oct_records = result[0][0] if result else 0
        print(f"   Records in October 2025: {oct_records}")
        
        # Sample data
        result = connector.execute_query("SELECT FIRST 3 * FROM FFBSCANNERDATA10")
        if result:
            print(f"   Sample record fields: {list(result[0].keys()) if hasattr(result[0], 'keys') else 'Raw tuple data'}")
            print(f"   Sample records: {result[:3]}")
        
    except Exception as e:
        print(f"   Error checking FFBSCANNERDATA10: {e}")
    
    # Check OCFIELD table
    print(f"\n2. Checking OCFIELD table:")
    print("-" * 40)
    
    try:
        # Count total records
        result = connector.execute_query("SELECT COUNT(*) as TOTAL_RECORDS FROM OCFIELD")
        total_records = result[0]['TOTAL_RECORDS'] if result else 0
        print(f"   Total records in OCFIELD: {total_records}")
        
        # Sample data
        result = connector.execute_query("SELECT FIRST 5 * FROM OCFIELD")
        if result:
            print(f"   Sample record fields: {list(result[0].keys())}")
            for i, record in enumerate(result[:3]):
                print(f"   Sample {i+1}: ID={record.get('ID')}, FIELDNAME={record.get('FIELDNAME')}, DIVID={record.get('DIVID')}")
        
    except Exception as e:
        print(f"   Error checking OCFIELD: {e}")
    
    # Check CRDIVISION table
    print(f"\n3. Checking CRDIVISION table:")
    print("-" * 40)
    
    try:
        # Count total records
        result = connector.execute_query("SELECT COUNT(*) as TOTAL_RECORDS FROM CRDIVISION")
        total_records = result[0]['TOTAL_RECORDS'] if result else 0
        print(f"   Total records in CRDIVISION: {total_records}")
        
        # Sample data
        result = connector.execute_query("SELECT FIRST 5 * FROM CRDIVISION")
        if result:
            print(f"   Sample record fields: {list(result[0].keys())}")
            for i, record in enumerate(result[:3]):
                print(f"   Sample {i+1}: ID={record.get('ID')}, DIVNAME={record.get('DIVNAME')}")
        
    except Exception as e:
        print(f"   Error checking CRDIVISION: {e}")
    
    # Check EMP table
    print(f"\n4. Checking EMP table:")
    print("-" * 40)
    
    try:
        # Count total records
        result = connector.execute_query("SELECT COUNT(*) as TOTAL_RECORDS FROM EMP")
        total_records = result[0]['TOTAL_RECORDS'] if result else 0
        print(f"   Total records in EMP: {total_records}")
        
        # Sample data
        result = connector.execute_query('SELECT FIRST 3 "ID EMPCODE", "ID NAME" FROM EMP WHERE "ID EMPCODE" IS NOT NULL')
        if result:
            for i, record in enumerate(result[:3]):
                print(f"   Sample {i+1}: EMPCODE={record.get('ID EMPCODE')}, NAME={record.get('ID NAME')}")
        
    except Exception as e:
        print(f"   Error checking EMP: {e}")
    
    # Test JOIN relationships
    print(f"\n5. Testing JOIN relationships:")
    print("-" * 40)
    
    # Test FFBSCANNERDATA10 to OCFIELD join
    try:
        result = connector.execute_query("""
            SELECT COUNT(*) as MATCHED_RECORDS 
            FROM FFBSCANNERDATA10 a 
            INNER JOIN OCFIELD b ON a.FIELDID = b.ID 
            WHERE a.TRANSDATE >= '2025-10-01' AND a.TRANSDATE <= '2025-10-31'
        """)
        matched = result[0]['MATCHED_RECORDS'] if result else 0
        print(f"   FFBSCANNERDATA10 ↔ OCFIELD matches (Oct 2025): {matched}")
        
    except Exception as e:
        print(f"   Error testing FFBSCANNERDATA10 ↔ OCFIELD join: {e}")
    
    # Test OCFIELD to CRDIVISION join
    try:
        result = connector.execute_query("""
            SELECT COUNT(*) as MATCHED_RECORDS 
            FROM OCFIELD b 
            INNER JOIN CRDIVISION c ON b.DIVID = c.ID
        """)
        matched = result[0]['MATCHED_RECORDS'] if result else 0
        print(f"   OCFIELD ↔ CRDIVISION matches: {matched}")
        
    except Exception as e:
        print(f"   Error testing OCFIELD ↔ CRDIVISION join: {e}")
    
    # Test full chain join
    try:
        result = connector.execute_query("""
            SELECT COUNT(*) as MATCHED_RECORDS 
            FROM FFBSCANNERDATA10 a 
            INNER JOIN OCFIELD b ON a.FIELDID = b.ID 
            INNER JOIN CRDIVISION c ON b.DIVID = c.ID 
            WHERE a.TRANSDATE >= '2025-10-01' AND a.TRANSDATE <= '2025-10-31'
        """)
        matched = result[0]['MATCHED_RECORDS'] if result else 0
        print(f"   Full chain matches (Oct 2025): {matched}")
        
    except Exception as e:
        print(f"   Error testing full chain join: {e}")
    
    # Check specific FIELDID values
    print(f"\n6. Checking FIELDID relationships:")
    print("-" * 40)
    
    try:
        # Get unique FIELDID values from FFBSCANNERDATA10
        result = connector.execute_query("""
            SELECT DISTINCT FIELDID 
            FROM FFBSCANNERDATA10 
            WHERE TRANSDATE >= '2025-10-01' AND TRANSDATE <= '2025-10-31' 
            AND FIELDID IS NOT NULL 
            ORDER BY FIELDID
        """)
        scanner_fieldids = [r['FIELDID'] for r in result] if result else []
        print(f"   FIELDID values in FFBSCANNERDATA10 (Oct 2025): {scanner_fieldids[:10]}...")
        
        # Get unique ID values from OCFIELD
        result = connector.execute_query("SELECT DISTINCT ID FROM OCFIELD WHERE ID IS NOT NULL ORDER BY ID")
        ocfield_ids = [r['ID'] for r in result] if result else []
        print(f"   ID values in OCFIELD: {ocfield_ids[:10]}...")
        
        # Check overlap
        if scanner_fieldids and ocfield_ids:
            overlap = set(scanner_fieldids) & set(ocfield_ids)
            print(f"   Overlapping values: {len(overlap)} out of {len(scanner_fieldids)} scanner FIELDIDs")
            if overlap:
                print(f"   Sample overlaps: {list(overlap)[:5]}")
        
    except Exception as e:
        print(f"   Error checking FIELDID relationships: {e}")
    
    print(f"\n" + "=" * 50)
    print("Debug completed. Check the results above to identify issues.")

def main():
    """Main function"""
    debug_data_structure()

if __name__ == "__main__":
    main()