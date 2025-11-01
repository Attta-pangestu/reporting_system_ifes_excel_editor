"""
Enhanced Sample Data Insertion Script with Transaction Commits
Inserts sample data into EMP and FFBLOADINGCROP tables with proper transaction handling
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced
from datetime import datetime, timedelta
import sys

def insert_sample_data_with_commit():
    """Insert sample data with proper transaction commits"""
    print("=== Enhanced Sample Data Insertion ===")
    
    try:
        # Initialize connector
        connector = FirebirdConnectorEnhanced()
        print("✅ Connection successful")
        
        # First, clear existing data (if any)
        print("\n--- Clearing existing data ---")
        clear_queries = [
            "DELETE FROM FFBLOADINGCROP01",
            "DELETE FROM FFBLOADINGCROP02", 
            "DELETE FROM FFBLOADINGCROP03",
            "DELETE FROM EMP"
        ]
        
        for query in clear_queries:
            try:
                connector.execute_query(query)
                print(f"✅ Cleared table: {query.split()[-1]}")
            except Exception as e:
                print(f"⚠️ Could not clear {query.split()[-1]}: {e}")
        
        # Commit the deletions
        commit_result = connector.execute_query("COMMIT")
        print("✅ Deletion committed")
        
        # Insert Employee Data
        print("\n--- Inserting Employee Data ---")
        employees = [
            ("EMP001", "John Doe", "KERANI", "SCANNER", "A01", "A"),
            ("EMP002", "Jane Smith", "MANDOR", "SUPERVISOR", "A02", "A"),
            ("EMP003", "Bob Wilson", "ASISTEN", "MANAGER", "B01", "A"),
            ("EMP004", "Alice Brown", "KERANI", "SCANNER", "B02", "A"),
            ("EMP005", "Charlie Davis", "MANDOR", "SUPERVISOR", "C01", "A")
        ]
        
        for emp_id, emp_name, emp_type, emp_position, division_id, emp_status in employees:
            query = f"""
            INSERT INTO EMP (EMPID, EMPNAME, EMPTYPE, EMPPOSITION, DIVISIONID, EMPSTATUS)
            VALUES ('{emp_id}', '{emp_name}', '{emp_type}', '{emp_position}', '{division_id}', '{emp_status}')
            """
            try:
                connector.execute_query(query)
                print(f"✅ Inserted employee: {emp_id} - {emp_name}")
            except Exception as e:
                print(f"❌ Failed to insert employee {emp_id}: {e}")
        
        # Commit employee data
        connector.execute_query("COMMIT")
        print("✅ Employee data committed")
        
        # Insert FFB Loading Data
        print("\n--- Inserting FFB Loading Data ---")
        
        # Define divisions
        divisions = [
            ("A01", "Division A1"),
            ("A02", "Division A2"), 
            ("B01", "Division B1"),
            ("B02", "Division B2"),
            ("C01", "Division C1")
        ]
        
        # Insert data for each table and month
        tables = ["FFBLOADINGCROP01", "FFBLOADINGCROP02", "FFBLOADINGCROP03"]
        start_date = datetime(2024, 1, 1)
        
        record_id = 1
        
        for table_name in tables:
            print(f"\nInserting data into {table_name}...")
            
            # Insert 10 days of data for each division
            current_date = start_date
            for day in range(10):
                for division_id, division_name in divisions:
                    emp_id = f"EMP00{(day % 5) + 1}"  # Rotate through employees
                    
                    # Create a simple insert with minimal required fields
                    query = f"""
                    INSERT INTO {table_name} 
                    (TRANSDATE, DIVISIONID, DIVISIONNAME, EMPID, EMPNAME, EMPTYPE, EMPPOSITION, FFBWEIGHT, FFBPRICE, FFBVALUE)
                    VALUES 
                    ('{current_date.strftime('%Y-%m-%d')}', '{division_id}', '{division_name}', '{emp_id}', 
                     'Employee {emp_id}', 'KERANI', 'SCANNER', {100 + (day * 10)}, 1500, {(100 + (day * 10)) * 1500})
                    """
                    
                    try:
                        connector.execute_query(query)
                        record_id += 1
                    except Exception as e:
                        print(f"⚠️ Error inserting record for {current_date.strftime('%Y-%m-%d')}, {division_id}: {e}")
                
                current_date += timedelta(days=1)
            
            # Commit after each table
            connector.execute_query("COMMIT")
            print(f"✅ {table_name} data committed")
        
        # Final verification
        print("\n--- Final Verification ---")
        
        # Check EMP table
        emp_count_result = connector.execute_query("SELECT COUNT(*) as COUNT FROM EMP")
        if emp_count_result:
            emp_count = emp_count_result[0]['COUNT']
            print(f"✅ EMP table: {emp_count} records")
        
        # Check FFB tables
        for table_name in tables:
            count_result = connector.execute_query(f"SELECT COUNT(*) as COUNT FROM {table_name}")
            if count_result:
                count = count_result[0]['COUNT']
                print(f"✅ {table_name}: {count} records")
        
        print("\n=== Enhanced Sample Data Insertion Complete ===")
        return True
        
    except Exception as e:
        print(f"❌ Error during data insertion: {e}")
        return False

if __name__ == "__main__":
    success = insert_sample_data_with_commit()
    if success:
        print("\n✅ Enhanced sample data insertion completed successfully!")
        print("Data has been properly committed to the database.")
        print("You can now test the GUI with actual data.")
    else:
        print("\n❌ Enhanced sample data insertion failed.")
        print("Please check the database connection and table structure.")