"""
Script to insert sample data into empty database tables for testing
"""
from firebird_connector_enhanced import FirebirdConnectorEnhanced
from datetime import datetime, timedelta
import random

def insert_sample_data():
    """Insert sample data into EMP and FFBLOADINGCROP tables"""
    print("=== Inserting Sample Data ===")
    
    # Create connector
    connector = FirebirdConnectorEnhanced.create_default_connector()
    
    if not connector.test_connection():
        print(f"❌ Connection failed: {connector.last_error}")
        return False
    
    print("✅ Connection successful")
    
    try:
        # Insert sample employee data
        print("\n--- Inserting Employee Data ---")
        emp_data = [
            ("EMP001", "John Doe", "KERANI", "SCANNER", "A01", "A"),
            ("EMP002", "Jane Smith", "MANDOR", "SUPERVISOR", "A01", "A"),
            ("EMP003", "Bob Wilson", "ASISTEN", "ASSISTANT", "A01", "A"),
            ("EMP004", "Alice Brown", "KERANI", "SCANNER", "B01", "A"),
            ("EMP005", "Charlie Davis", "MANDOR", "SUPERVISOR", "B01", "A"),
        ]
        
        for emp_id, emp_name, emp_type, emp_position, division_id, emp_status in emp_data:
            query = f"""
            INSERT INTO EMP (EMPID, EMPNAME, EMPTYPE, EMPPOSITION, DIVISIONID, EMPSTATUS)
            VALUES ('{emp_id}', '{emp_name}', '{emp_type}', '{emp_position}', '{division_id}', '{emp_status}')
            """
            try:
                connector.execute_query(query)
                print(f"✅ Inserted employee: {emp_id} - {emp_name}")
            except Exception as e:
                print(f"⚠️ Employee {emp_id} might already exist or error: {e}")
        
        # Insert sample FFB data for multiple months
        print("\n--- Inserting FFB Loading Data ---")
        
        # Generate data for January (01), February (02), March (03)
        for month in [1, 2, 3]:
            table_name = f"FFBLOADINGCROP{month:02d}"
            print(f"\nInserting data into {table_name}...")
            
            # Generate sample data for each day in the month
            start_date = datetime(2024, month, 1)
            if month == 2:
                end_date = datetime(2024, month, 28)  # February
            elif month in [1, 3]:
                end_date = datetime(2024, month, 31)  # January, March
            
            current_date = start_date
            record_id = 1
            
            while current_date <= end_date:
                # Generate 3-5 records per day
                daily_records = random.randint(3, 5)
                
                for i in range(daily_records):
                    # Random division
                    division = random.choice(['A01', 'B01'])
                    division_name = f"Division {division}"
                    
                    # Random employee based on division
                    if division == 'A01':
                        emp_id = random.choice(['EMP001', 'EMP002', 'EMP003'])
                    else:
                        emp_id = random.choice(['EMP004', 'EMP005'])
                    
                    # Random data
                    bunches = random.randint(50, 200)
                    loose_fruit = random.randint(10, 50)
                    trans_time = f"{random.randint(8, 16):02d}:{random.randint(0, 59):02d}:00"
                    
                    # Sample query - adjust field names based on actual table structure
                    query = f"""
                    INSERT INTO {table_name} 
                    (ID, TRANSDATE, TRANSTIME, DIVISIONID, DIVISIONNAME, EMPID, EMPNAME, EMPTYPE, EMPPOSITION, 
                     BUNCHES, LOOSEFRUIT, FFBWEIGHT, FFBPRICE, FFBVALUE, SCANUSERID, FIELDID, DRIVERID, DRIVERNAME, 
                     HARVESTINGDATE, VEHICLECODEID)
                    VALUES 
                    ({record_id}, '{current_date.strftime('%Y-%m-%d')}', '{trans_time}', '{division}', '{division_name}', 
                     '{emp_id}', 'Employee {emp_id}', 'KERANI', 'SCANNER', 
                     {bunches}, {loose_fruit}, {bunches * 15 + loose_fruit * 2}, 1500, {(bunches * 15 + loose_fruit * 2) * 1500}, 
                     '{emp_id}', '{division}', 'DRV001', 'Driver Name', 
                     '{current_date.strftime('%Y-%m-%d')}', 'VEH001')
                    """
                    
                    try:
                        connector.execute_query(query)
                        record_id += 1
                    except Exception as e:
                        print(f"⚠️ Error inserting record {record_id}: {e}")
                        # Try simpler insert if complex one fails
                        simple_query = f"""
                        INSERT INTO {table_name} 
                        (TRANSDATE, DIVISIONID, DIVISIONNAME, EMPID)
                        VALUES 
                        ('{current_date.strftime('%Y-%m-%d')}', '{division}', '{division_name}', '{emp_id}')
                        """
                        try:
                            connector.execute_query(simple_query)
                            print(f"✅ Inserted simple record for {current_date.strftime('%Y-%m-%d')}")
                            record_id += 1
                        except Exception as e2:
                            print(f"❌ Failed to insert even simple record: {e2}")
                
                current_date += timedelta(days=1)
            
            # Check how many records were inserted
            try:
                count_result = connector.execute_query(f"SELECT COUNT(*) as COUNT FROM {table_name}")
                if count_result:
                    count = count_result[0]['COUNT']
                    print(f"✅ {table_name}: {count} records inserted")
            except Exception as e:
                print(f"⚠️ Could not count records in {table_name}: {e}")
        
        print("\n=== Sample Data Insertion Complete ===")
        return True
        
    except Exception as e:
        print(f"❌ Error during data insertion: {e}")
        return False

if __name__ == "__main__":
    success = insert_sample_data()
    if success:
        print("\n✅ Sample data insertion completed successfully!")
        print("You can now test the GUI with actual data.")
    else:
        print("\n❌ Sample data insertion failed.")
        print("Please check the database connection and table structure.")