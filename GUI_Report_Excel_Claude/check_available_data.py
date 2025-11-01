#!/usr/bin/env python3
"""
Check Available Data Script
Find out what data is actually in the database
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def check_available_data():
    """Check what data is available in the database"""
    
    print("Checking Available Data")
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
    print(f"\n1. FFBSCANNERDATA10 table analysis:")
    print("-" * 40)
    
    try:
        # Count total records
        result = connector.execute_query("SELECT COUNT(*) FROM FFBSCANNERDATA10")
        total_records = result[0][0] if result else 0
        print(f"   Total records: {total_records}")
        
        if total_records > 0:
            # Check date range
            result = connector.execute_query("""
                SELECT MIN(TRANSDATE), MAX(TRANSDATE) 
                FROM FFBSCANNERDATA10 
                WHERE TRANSDATE IS NOT NULL
            """)
            if result and result[0][0]:
                print(f"   Date range: {result[0][0]} to {result[0][1]}")
            
            # Check available months/years
            result = connector.execute_query("""
                SELECT EXTRACT(YEAR FROM TRANSDATE) as YEAR, 
                       EXTRACT(MONTH FROM TRANSDATE) as MONTH, 
                       COUNT(*) as RECORDS
                FROM FFBSCANNERDATA10 
                WHERE TRANSDATE IS NOT NULL
                GROUP BY EXTRACT(YEAR FROM TRANSDATE), EXTRACT(MONTH FROM TRANSDATE)
                ORDER BY YEAR DESC, MONTH DESC
            """)
            if result:
                print(f"   Available data by month:")
                for record in result[:10]:  # Show first 10 months
                    year, month, count = record[0], record[1], record[2]
                    print(f"     {int(year)}-{int(month):02d}: {count} records")
            
            # Sample recent data
            result = connector.execute_query("""
                SELECT FIRST 5 TRANSDATE, FIELDID, SCANUSERID, RIPE, UNRIPE 
                FROM FFBSCANNERDATA10 
                WHERE TRANSDATE IS NOT NULL 
                ORDER BY TRANSDATE DESC
            """)
            if result:
                print(f"   Recent records:")
                for i, record in enumerate(result):
                    print(f"     {i+1}: {record[0]}, FIELD={record[1]}, USER={record[2]}, RIPE={record[3]}, UNRIPE={record[4]}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check OCFIELD table
    print(f"\n2. OCFIELD table analysis:")
    print("-" * 40)
    
    try:
        result = connector.execute_query("SELECT COUNT(*) FROM OCFIELD")
        total_records = result[0][0] if result else 0
        print(f"   Total records: {total_records}")
        
        if total_records > 0:
            result = connector.execute_query("SELECT FIRST 5 ID, FIELDNAME, DIVID FROM OCFIELD")
            if result:
                print(f"   Sample records:")
                for i, record in enumerate(result):
                    print(f"     {i+1}: ID={record[0]}, NAME={record[1]}, DIVID={record[2]}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check CRDIVISION table
    print(f"\n3. CRDIVISION table analysis:")
    print("-" * 40)
    
    try:
        result = connector.execute_query("SELECT COUNT(*) FROM CRDIVISION")
        total_records = result[0][0] if result else 0
        print(f"   Total records: {total_records}")
        
        if total_records > 0:
            result = connector.execute_query("SELECT FIRST 5 ID, DIVNAME FROM CRDIVISION")
            if result:
                print(f"   Sample records:")
                for i, record in enumerate(result):
                    print(f"     {i+1}: ID={record[0]}, NAME={record[1]}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check EMP table
    print(f"\n4. EMP table analysis:")
    print("-" * 40)
    
    try:
        result = connector.execute_query("SELECT COUNT(*) FROM EMP")
        total_records = result[0][0] if result else 0
        print(f"   Total records: {total_records}")
        
        if total_records > 0:
            result = connector.execute_query('SELECT FIRST 3 "ID EMPCODE", "ID NAME" FROM EMP')
            if result:
                print(f"   Sample records:")
                for i, record in enumerate(result):
                    print(f"     {i+1}: CODE={record[0]}, NAME={record[1]}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Suggest correct date range
    print(f"\n5. Recommendations:")
    print("-" * 40)
    
    try:
        result = connector.execute_query("""
            SELECT MIN(TRANSDATE), MAX(TRANSDATE) 
            FROM FFBSCANNERDATA10 
            WHERE TRANSDATE IS NOT NULL
        """)
        if result and result[0][0]:
            min_date, max_date = result[0][0], result[0][1]
            print(f"   ✓ Use date range: {min_date} to {max_date}")
            
            # Get the most recent month with data
            result = connector.execute_query("""
                SELECT EXTRACT(YEAR FROM TRANSDATE) as YEAR, 
                       EXTRACT(MONTH FROM TRANSDATE) as MONTH, 
                       COUNT(*) as RECORDS
                FROM FFBSCANNERDATA10 
                WHERE TRANSDATE IS NOT NULL
                GROUP BY EXTRACT(YEAR FROM TRANSDATE), EXTRACT(MONTH FROM TRANSDATE)
                ORDER BY YEAR DESC, MONTH DESC
                ROWS 1
            """)
            if result:
                year, month, count = result[0][0], result[0][1], result[0][2]
                print(f"   ✓ Most recent month: {int(year)}-{int(month):02d} ({count} records)")
                print(f"   ✓ Suggested test range: {int(year)}-{int(month):02d}-01 to {int(year)}-{int(month):02d}-31")
        else:
            print(f"   ✗ No data found in FFBSCANNERDATA10")
    
    except Exception as e:
        print(f"   Error getting recommendations: {e}")
    
    print(f"\n" + "=" * 50)
    print("Data check completed.")

def main():
    """Main function"""
    check_available_data()

if __name__ == "__main__":
    main()