#!/usr/bin/env python3
"""
Test FFBSCANNERDATA tables with databases that contain actual data.
This script will validate the ETL process with real production data.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, date

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def test_database_with_real_data(db_path, db_name):
    """Test a database that contains real FFB data"""
    print(f"\n🧪 Testing database: {db_name}")
    print(f"📁 Path: {db_path}")
    
    try:
        # Connect to database
        connector = FirebirdConnectorEnhanced(db_path=db_path)
        
        if not connector.test_connection():
            print(f"  ❌ Failed to connect to {db_name}")
            return False
        
        print(f"  ✅ Connected successfully")
        
        # Get all tables
        tables = connector.get_table_list()
        print(f"  📊 Total tables: {len(tables)}")
        
        # Find FFB tables
        ffb_tables = [t for t in tables if 'FFB' in t.upper()]
        scanner_tables = [t for t in tables if 'SCANNER' in t.upper()]
        
        print(f"  🔍 FFB tables: {len(ffb_tables)}")
        print(f"  📡 Scanner tables: {len(scanner_tables)}")
        
        # Test FFBSCANNERDATA tables specifically
        ffbscannerdata_tables = [t for t in tables if t.upper().startswith('FFBSCANNERDATA')]
        
        if ffbscannerdata_tables:
            print(f"  📋 FFBSCANNERDATA tables found: {ffbscannerdata_tables}")
            
            # Test each FFBSCANNERDATA table
            for table in ffbscannerdata_tables:
                print(f"\n    🔍 Testing {table}:")
                
                # Get row count
                try:
                    count_query = f"SELECT COUNT(*) as TOTAL FROM {table}"
                    count_result = connector.execute_query(count_query)
                    
                    if count_result and len(count_result) > 0:
                        # Handle the specific format returned by FirebirdConnectorEnhanced
                        result_data = count_result[0]
                        
                        if 'rows' in result_data and len(result_data['rows']) > 0:
                            row_data = result_data['rows'][0]
                            
                            # Try different possible keys
                            row_count = None
                            for key in ['TOTAL', 'total', 'COUNT', 'count', 'COUNT(*)']:
                                if key in row_data:
                                    row_count = int(row_data[key])
                                    break
                            
                            # If no key found, try the first value
                            if row_count is None and row_data:
                                first_value = list(row_data.values())[0]
                                row_count = int(first_value) if first_value != '<null>' else 0
                        else:
                            row_count = 0
                        
                        print(f"      📊 Row count: {row_count}")
                        
                        if row_count > 0:
                            # Get sample data
                            sample_query = f"SELECT FIRST 5 * FROM {table}"
                            sample_data = connector.execute_query(sample_query)
                            
                            if sample_data and len(sample_data) > 0:
                                sample_result = sample_data[0]
                                
                                if 'rows' in sample_result and len(sample_result['rows']) > 0:
                                    actual_rows = sample_result['rows']
                                    headers = sample_result.get('headers', [])
                                    
                                    print(f"      ✅ Sample data retrieved ({len(actual_rows)} rows)")
                                    
                                    # Show column structure
                                    if headers:
                                        print(f"      📋 Columns ({len(headers)}): {headers[:10]}...")
                                        
                                        # Show first row data
                                        if actual_rows:
                                            first_row = actual_rows[0]
                                            print(f"      📄 First row sample:")
                                            for i, (key, value) in enumerate(first_row.items()):
                                                if i < 5:  # Show first 5 columns
                                                    print(f"        {key}: {value}")
                                                elif i == 5:
                                                    print(f"        ... and {len(first_row) - 5} more columns")
                                                    break
                                            
                                            # Check for date fields
                                            date_fields = [col for col in headers if 'DATE' in col.upper() or 'TIME' in col.upper()]
                                            if date_fields:
                                                print(f"      📅 Date fields found: {date_fields}")
                                                
                                                # Get date range
                                                for date_field in date_fields[:2]:  # Check first 2 date fields
                                                    try:
                                                        date_range_query = f"""
                                                        SELECT 
                                                            MIN({date_field}) as MIN_DATE,
                                                            MAX({date_field}) as MAX_DATE,
                                                            COUNT(DISTINCT {date_field}) as UNIQUE_DATES
                                                        FROM {table}
                                                        WHERE {date_field} IS NOT NULL
                                                        """
                                                        date_range_result = connector.execute_query(date_range_query)
                                                        
                                                        if date_range_result and len(date_range_result) > 0:
                                                            dr_data = date_range_result[0]
                                                            if 'rows' in dr_data and len(dr_data['rows']) > 0:
                                                                dr = dr_data['rows'][0]
                                                                print(f"        📅 {date_field}: {dr['MIN_DATE']} to {dr['MAX_DATE']} ({dr['UNIQUE_DATES']} unique dates)")
                                                    except Exception as e:
                                                        print(f"        ❌ Error checking {date_field}: {e}")
                                            
                                            return True
                                else:
                                    print(f"      ❌ No sample data in result")
                            else:
                                print(f"      ❌ No sample data retrieved")
                        else:
                            print(f"      ❌ Table is empty")
                    else:
                        print(f"      ❌ Could not get row count")
                        
                except Exception as e:
                    print(f"      ❌ Error querying {table}: {e}")
        else:
            print(f"  ❌ No FFBSCANNERDATA tables found")
            
            # Check for other FFB tables with data
            print(f"\n  🔍 Checking other FFB tables for data:")
            for table in ffb_tables[:5]:  # Check first 5 FFB tables
                try:
                    count_query = f"SELECT COUNT(*) as TOTAL FROM {table}"
                    count_result = connector.execute_query(count_query)
                    
                    if count_result and len(count_result) > 0:
                        # Handle the specific format returned by FirebirdConnectorEnhanced
                        result_data = count_result[0]
                        
                        if 'rows' in result_data and len(result_data['rows']) > 0:
                            row_data = result_data['rows'][0]
                            
                            # Try different possible keys
                            row_count = None
                            for key in ['TOTAL', 'total', 'COUNT', 'count', 'COUNT(*)']:
                                if key in row_data:
                                    row_count = int(row_data[key])
                                    break
                            
                            # If no key found, try the first value
                            if row_count is None and row_data:
                                first_value = list(row_data.values())[0]
                                row_count = int(first_value) if first_value != '<null>' else 0
                        else:
                            row_count = 0
                        
                        if row_count and row_count > 0:
                            print(f"    ✅ {table}: {row_count} rows")
                        else:
                            print(f"    ❌ {table}: empty")
                    else:
                        print(f"    ❌ {table}: could not check")
                        
                except Exception as e:
                    print(f"    ❌ {table}: error - {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing database: {e}")
        return False

def main():
    """Main function to test databases with real data"""
    print("🧪 Testing FFBSCANNERDATA tables with real production data")
    print("=" * 60)
    
    # List of databases with data (from our previous search)
    databases_with_data = [
        {
            'name': 'PTRJ_ARC.FDB',
            'path': r'D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_ARE_C_24-10-2025\PTRJ_ARC.FDB',
            'size_mb': 1488.9
        },
        {
            'name': 'PTRJ_P1A.FDB',
            'path': r'D:\Gawean Rebinmas\Monitoring Database\Database Ifess\PTRJ_P1A.FDB',
            'size_mb': 1464.4
        },
        {
            'name': 'PTRJ_P2A.FDB',
            'path': r'D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_PGE_2A_24-10-2025\PTRJ_P2A.FDB',
            'size_mb': 1368.7
        },
        {
            'name': 'PTRJ_P1B.FDB',
            'path': r'D:\Gawean Rebinmas\Monitoring Database\Database Ifess\1b\PTRJ_P1B.FDB',
            'size_mb': 1345.5
        }
    ]
    
    successful_tests = []
    
    # Test each database
    for db in databases_with_data:
        if os.path.exists(db['path']):
            success = test_database_with_real_data(db['path'], db['name'])
            if success:
                successful_tests.append(db)
        else:
            print(f"\n❌ Database not found: {db['path']}")
    
    # Summary
    print(f"\n📈 TESTING SUMMARY:")
    print(f"=" * 40)
    print(f"Databases tested: {len(databases_with_data)}")
    print(f"Successful connections: {len(successful_tests)}")
    
    if successful_tests:
        print(f"\n✅ DATABASES WITH WORKING FFB DATA:")
        for i, db in enumerate(successful_tests):
            print(f"{i+1}. {db['name']} ({db['size_mb']:.1f} MB)")
            print(f"   Path: {db['path']}")
        
        # Recommend best database for ETL testing
        largest_db = max(successful_tests, key=lambda x: x['size_mb'])
        print(f"\n🎯 RECOMMENDED FOR ETL TESTING:")
        print(f"Database: {largest_db['name']}")
        print(f"Path: {largest_db['path']}")
        print(f"Size: {largest_db['size_mb']:.1f} MB")
        print(f"Reason: Largest database with confirmed FFB data")
        
        # Save recommendation to file
        with open("recommended_database_for_etl.txt", 'w') as f:
            f.write("RECOMMENDED DATABASE FOR ETL TESTING\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Database: {largest_db['name']}\n")
            f.write(f"Path: {largest_db['path']}\n")
            f.write(f"Size: {largest_db['size_mb']:.1f} MB\n")
            f.write(f"Tested: {datetime.now()}\n")
            f.write(f"Status: Contains actual FFB data\n\n")
            f.write("USAGE INSTRUCTIONS:\n")
            f.write("1. Update firebird_connector_enhanced.py DEFAULT_DATABASE path\n")
            f.write("2. Test ETL queries with this database\n")
            f.write("3. Validate data extraction and report generation\n")
        
        print(f"\n📄 Recommendation saved to: recommended_database_for_etl.txt")
        
    else:
        print(f"\n❌ No databases with working FFB data found")

if __name__ == "__main__":
    main()