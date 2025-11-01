#!/usr/bin/env python3
"""
Simple Debug Data Structure Script
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
        
        # Check October 2025 data
        result = connector.execute_query("""
            SELECT COUNT(*) 
            FROM FFBSCANNERDATA10 
            WHERE TRANSDATE >= '2025-10-01' AND TRANSDATE <= '2025-10-31'
        """)
        oct_records = result[0][0] if result else 0
        print(f"   Records in October 2025: {oct_records}")
        
        # Sample data with specific fields
        result = connector.execute_query("SELECT FIRST 3 FIELDID, TRANSDATE, SCANUSERID FROM FFBSCANNERDATA10")
        if result:
            print(f"   Sample records:")
            for i, record in enumerate(result):
                print(f"     Record {i+1}: FIELDID={record[0]}, TRANSDATE={record[1]}, SCANUSERID={record[2]}")
        
    except Exception as e:
        print(f"   Error checking FFBSCANNERDATA10: {e}")
    
    # Check OCFIELD table
    print(f"\n2. Checking OCFIELD table:")
    print("-" * 40)
    
    try:
        # Count total records
        result = connector.execute_query("SELECT COUNT(*) FROM OCFIELD")
        total_records = result[0][0] if result else 0
        print(f"   Total records in OCFIELD: {total_records}")
        
        # Sample data
        result = connector.execute_query("SELECT FIRST 5 ID, FIELDNAME, DIVID FROM OCFIELD")
        if result:
            print(f"   Sample records:")
            for i, record in enumerate(result):
                print(f"     Record {i+1}: ID={record[0]}, FIELDNAME={record[1]}, DIVID={record[2]}")
        
    except Exception as e:
        print(f"   Error checking OCFIELD: {e}")
    
    # Test JOIN relationships
    print(f"\n3. Testing JOIN relationships:")
    print("-" * 40)
    
    # Test FFBSCANNERDATA10 to OCFIELD join
    try:
        result = connector.execute_query("""
            SELECT COUNT(*) 
            FROM FFBSCANNERDATA10 a 
            INNER JOIN OCFIELD b ON a.FIELDID = b.ID 
            WHERE a.TRANSDATE >= '2025-10-01' AND a.TRANSDATE <= '2025-10-31'
        """)
        matched = result[0][0] if result else 0
        print(f"   FFBSCANNERDATA10 ↔ OCFIELD matches (Oct 2025): {matched}")
        
    except Exception as e:
        print(f"   Error testing FFBSCANNERDATA10 ↔ OCFIELD join: {e}")
    
    # Check specific FIELDID values
    print(f"\n4. Checking FIELDID relationships:")
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
        scanner_fieldids = [r[0] for r in result] if result else []
        print(f"   FIELDID values in FFBSCANNERDATA10 (Oct 2025): {scanner_fieldids[:10]}")
        
        # Get unique ID values from OCFIELD
        result = connector.execute_query("SELECT DISTINCT ID FROM OCFIELD WHERE ID IS NOT NULL ORDER BY ID")
        ocfield_ids = [r[0] for r in result] if result else []
        print(f"   ID values in OCFIELD: {ocfield_ids[:10]}")
        
        # Check overlap
        if scanner_fieldids and ocfield_ids:
            overlap = set(scanner_fieldids) & set(ocfield_ids)
            print(f"   Overlapping values: {len(overlap)} out of {len(scanner_fieldids)} scanner FIELDIDs")
            if overlap:
                print(f"   Sample overlaps: {list(overlap)[:5]}")
        
    except Exception as e:
        print(f"   Error checking FIELDID relationships: {e}")
    
    # Test the actual raw_ffb_data query
    print(f"\n5. Testing raw_ffb_data query:")
    print("-" * 40)
    
    try:
        query = """
            SELECT 
                a.TRANSDATE,
                a.FIELDID,
                b.FIELDNAME,
                a.SCANUSERID,
                a.RIPE,
                a.UNRIPE,
                a.BLACK,
                a.ROTTEN,
                a.RATDAMAGE
            FROM FFBSCANNERDATA10 a
            LEFT JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '2025-10-01' AND a.TRANSDATE <= '2025-10-31'
            ORDER BY a.TRANSDATE DESC
        """
        
        result = connector.execute_query(query)
        print(f"   Raw FFB data query returned: {len(result) if result else 0} rows")
        
        if result:
            print(f"   Sample records:")
            for i, record in enumerate(result[:3]):
                print(f"     Record {i+1}: DATE={record[0]}, FIELDID={record[1]}, FIELDNAME={record[2]}, USER={record[3]}")
        
    except Exception as e:
        print(f"   Error testing raw_ffb_data query: {e}")
    
    print(f"\n" + "=" * 50)
    print("Debug completed. Check the results above to identify issues.")

def main():
    """Main function"""
    debug_data_structure()

if __name__ == "__main__":
    main()