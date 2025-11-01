#!/usr/bin/env python3
"""
Create Test FFB Data
===================
This script creates sample FFB data in the current database for testing purposes.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def create_sample_ffb_data():
    """Create sample FFB data for testing"""
    print("🔧 Creating sample FFB data for testing...")
    
    try:
        # Initialize connector
        connector = FirebirdConnectorEnhanced()
        
        # Check available FFB tables
        print("📊 Checking available FFB tables...")
        tables_query = """
        SELECT RDB$RELATION_NAME 
        FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME LIKE 'FFBSCANNERDATA%' 
        AND RDB$SYSTEM_FLAG = 0
        ORDER BY RDB$RELATION_NAME
        """
        
        result = connector.execute_query(tables_query)
        if not result or len(result) == 0:
            print("❌ No result from tables query")
            return False
            
        # Handle the new result format - result is a list with dict containing headers and rows
        result_data = result[0]  # Get first (and only) result set
        if 'rows' in result_data:
            tables = [row['RDB$RELATION_NAME'].strip() for row in result_data['rows']]
        else:
            print("❌ Unexpected result format")
            return False
        print(f"📋 Found {len(tables)} FFB tables")
        
        if not tables:
            print("❌ No FFB tables found")
            return False
            
        # Use the first available table
        table_name = tables[0]
        print(f"🎯 Using table: {table_name}")
        
        # Simplified query - just get field names
        structure_query = f"SELECT RDB$FIELD_NAME FROM RDB$RELATION_FIELDS WHERE RDB$RELATION_NAME = '{table_name}'"
        
        result = connector.execute_query(structure_query)
        if not result or len(result) == 0:
            print("❌ No result from structure query")
            return False
            
        # Handle the new result format with headers and rows
        result_data = result[0]  # Get first (and only) result set
        if 'rows' in result_data:
            fields = [row['RDB$FIELD_NAME'].strip() for row in result_data['rows']]
        else:
            print("❌ Unexpected result format for structure query")
            return False
        print(f"📋 Table has {len(fields)} fields: {fields[:10]}...")  # Show first 10 fields
        
        # Create sample data
        print("🔧 Creating sample data...")
        
        # Generate dates for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        sample_records = []
        for i in range(50):  # Create 50 sample records
            # Generate random date within range
            random_days = random.randint(0, 30)
            trans_date = start_date + timedelta(days=random_days)
            
            # Sample data based on common FFB fields
            record = {
                'TRANSDATE': trans_date.strftime('%Y-%m-%d'),
                'TRANSTIME': f"{random.randint(6, 18):02d}:{random.randint(0, 59):02d}:00",
                'DIVID': f"DIV{random.randint(1, 5):02d}",
                'FIELDID': f"FIELD{random.randint(1, 20):03d}",
                'EMPID': f"EMP{random.randint(1000, 9999)}",
                'WEIGHT': round(random.uniform(500, 2000), 2),
                'BUNCHES': random.randint(50, 200),
                'LOOSE_FRUIT': round(random.uniform(10, 50), 2),
                'ROTTEN': round(random.uniform(0, 20), 2),
                'EMPTY_BUNCHES': random.randint(0, 10),
                'LONG_STALK': round(random.uniform(0, 15), 2),
                'DIRT': round(random.uniform(0, 10), 2),
                'CRDIVISION': f"CR{random.randint(1, 3):02d}",
                'CRFIELD': f"CRF{random.randint(1, 10):02d}",
                'CREMPLOYEE': f"CREMP{random.randint(100, 999)}"
            }
            sample_records.append(record)
        
        # Insert sample data
        print(f"📝 Inserting {len(sample_records)} sample records...")
        
        # Build insert query based on available fields
        available_fields = fields
        insert_fields = []
        insert_values = []
        
        for record in sample_records:
            field_list = []
            value_list = []
            
            for field_name, value in record.items():
                if field_name in available_fields:
                    field_list.append(field_name)
                    if isinstance(value, str):
                        value_list.append(f"'{value}'")
                    else:
                        value_list.append(str(value))
            
            if field_list:
                insert_query = f"""
                INSERT INTO {table_name} ({', '.join(field_list)})
                VALUES ({', '.join(value_list)})
                """
                
                result = connector.execute_query(insert_query)
                # For INSERT queries, result might be empty or contain success info
                if result is None or (isinstance(result, list) and len(result) == 0):
                    print(f"✅ Inserted record {len(insert_values) + 1}")
                elif isinstance(result, list) and len(result) > 0:
                    # Check if there's an error in the result
                    result_data = result[0]
                    if 'error' in result_data:
                        print(f"⚠️ Warning: Failed to insert record: {result_data['error']}")
                    else:
                        print(f"✅ Inserted record {len(insert_values) + 1}")
                else:
                    print(f"✅ Inserted record {len(insert_values) + 1}")
                    
                insert_values.append(record)
        
        print(f"✅ Successfully created {len(insert_values)} sample FFB records")
        print(f"📅 Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Verify data
        count_query = f"SELECT COUNT(*) FROM {table_name}"
        result = connector.execute_query(count_query)
        if result and len(result) > 0:
            result_data = result[0]
            if 'rows' in result_data:
                # The count result is a dictionary with column name as key
                count_row = result_data['rows'][0]
                total_count = list(count_row.values())[0]  # Get the first (and only) value
                print(f"📊 Total records in {table_name}: {total_count}")
            else:
                print("❌ Unexpected result format for count query")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def main():
    """Main function"""
    print("🚀 FFB Sample Data Creator")
    print("=" * 50)
    
    success = create_sample_ffb_data()
    
    if success:
        print("\n✅ Sample data creation completed successfully!")
        print("🎯 You can now test the GUI with real FFB data")
    else:
        print("\n❌ Sample data creation failed")
        print("🔧 Please check the database connection and table structure")

if __name__ == "__main__":
    main()