"""
Verify Data Insertion Script
Checks if the sample data was actually committed to the database
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced
import sys

def verify_data():
    """Verify that data was actually inserted and committed"""
    print("=== Verifying Data Insertion ===")
    
    try:
        # Initialize connector
        connector = FirebirdConnectorEnhanced()
        print("✅ Connection successful")
        
        # Check EMP table
        print("\n--- Checking EMP Table ---")
        emp_query = "SELECT COUNT(*) as count FROM EMP"
        emp_result = connector.execute_query(emp_query)
        if emp_result and len(emp_result) > 0:
            emp_count = emp_result[0].get('COUNT', 0)
            print(f"EMP table has {emp_count} rows")
            
            if emp_count > 0:
                # Get sample records
                sample_query = "SELECT FIRST 3 EMPID, EMPNAME, EMPSTATUS FROM EMP"
                sample_result = connector.execute_query(sample_query)
                print("Sample EMP records:")
                for row in sample_result:
                    print(f"  - {row.get('EMPID')}: {row.get('EMPNAME')} ({row.get('EMPSTATUS')})")
        else:
            print("❌ No data in EMP table")
        
        # Check FFBLOADINGCROP tables
        for table_num in ['01', '02', '03']:
            table_name = f"FFBLOADINGCROP{table_num}"
            print(f"\n--- Checking {table_name} Table ---")
            
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_result = connector.execute_query(count_query)
            
            if count_result and len(count_result) > 0:
                count = count_result[0].get('COUNT', 0)
                print(f"{table_name} has {count} rows")
                
                if count > 0:
                    # Get sample records
                    sample_query = f"SELECT FIRST 2 TRANSDATE, DIVISIONID, EMPID, FFBWEIGHT FROM {table_name}"
                    sample_result = connector.execute_query(sample_query)
                    print(f"Sample {table_name} records:")
                    for row in sample_result:
                        print(f"  - {row.get('TRANSDATE')}: Div {row.get('DIVISIONID')}, Emp {row.get('EMPID')}, Weight {row.get('FFBWEIGHT')}")
            else:
                print(f"❌ No data in {table_name}")
        
        # Test the actual GUI queries
        print("\n--- Testing GUI Query Patterns ---")
        
        # Test employee mapping query
        emp_mapping_query = """
        SELECT DISTINCT EMPID, EMPNAME, EMPTYPE, EMPPOSITION, DIVISIONID 
        FROM EMP 
        WHERE EMPSTATUS = 'A' 
        ORDER BY EMPID
        """
        emp_mapping_result = connector.execute_query(emp_mapping_query)
        print(f"Employee mapping query returned {len(emp_mapping_result) if emp_mapping_result else 0} rows")
        
        # Test divisions query for January 2024
        divisions_query = """
        SELECT DISTINCT DIVISIONID, DIVISIONNAME 
        FROM FFBLOADINGCROP01 
        WHERE TRANSDATE BETWEEN '2024-01-01' AND '2024-12-31' 
        AND DIVISIONID IS NOT NULL 
        AND DIVISIONNAME IS NOT NULL 
        ORDER BY DIVISIONID
        """
        divisions_result = connector.execute_query(divisions_query)
        print(f"Divisions query returned {len(divisions_result) if divisions_result else 0} rows")
        
        if divisions_result:
            print("Available divisions:")
            for row in divisions_result:
                print(f"  - {row.get('DIVISIONID')}: {row.get('DIVISIONNAME')}")
        
        print("\n=== Verification Complete ===")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
    
    return True

if __name__ == "__main__":
    verify_data()