"""
Simple verification script to check if sample data exists
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def verify_data():
    """Verify if sample data exists in the database"""
    print("=== Verifying Sample Data ===")
    
    try:
        # Initialize connector
        connector = FirebirdConnectorEnhanced()
        print("✅ Connection successful")
        
        # Check specific tables that should have data
        tables_to_check = [
            "EMP",
            "FFBLOADINGCROP01", 
            "FFBLOADINGCROP02",
            "FFBLOADINGCROP03"
        ]
        
        for table in tables_to_check:
            try:
                # Count records
                count_query = f"SELECT COUNT(*) FROM {table}"
                result = connector.execute_query(count_query)
                count = result[0][0] if result else 0
                
                print(f"📊 {table}: {count} records")
                
                # Show sample records if any exist
                if count > 0:
                    sample_query = f"SELECT FIRST 3 * FROM {table}"
                    sample_result = connector.execute_query(sample_query)
                    print(f"   Sample data: {sample_result}")
                    
            except Exception as e:
                print(f"❌ Error checking {table}: {e}")
        
        # Test a simple query
        print("\n--- Testing Simple Queries ---")
        try:
            emp_query = "SELECT ID, NAME FROM EMP"
            emp_result = connector.execute_query(emp_query)
            print(f"Employee query result: {emp_result}")
        except Exception as e:
            print(f"❌ Employee query error: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    finally:
        if 'connector' in locals():
            try:
                connector.close()
            except:
                pass

if __name__ == "__main__":
    verify_data()