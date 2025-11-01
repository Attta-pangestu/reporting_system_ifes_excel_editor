"""
Check FFBSCANNERDATA04 table existence and data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def check_ffb_scannerdata04():
    """Check FFBSCANNERDATA04 table"""
    try:
        # Connect to database
        connector = FirebirdConnectorEnhanced.create_default_connector()

        if not connector.test_connection():
            print("Failed to connect to database")
            return

        print("Database connection successful!")
        print(f"Database: {connector.db_path}")

        # Check if table exists
        print("\nChecking FFBSCANNERDATA04 table...")
        table_exists = connector.check_table_exists('FFBSCANNERDATA04')
        print(f"Table FFBSCANNERDATA04 exists: {table_exists}")

        if table_exists:
            # Get table info
            print("\nGetting table structure...")
            table_info = connector.get_table_info('FFBSCANNERDATA04')
            if 'error' not in table_info:
                print(f"Table has {table_info['column_count']} columns")
                print("\nColumns:")
                for col in table_info['columns'][:10]:  # Show first 10 columns
                    print(f"  {col.get('FIELD_NAME', 'N/A')} - Type: {col.get('FIELD_TYPE', 'N/A')}")
                if table_info['column_count'] > 10:
                    print(f"  ... and {table_info['column_count'] - 10} more columns")

            # Get row count
            print("\nGetting row count...")
            row_count = connector.get_row_count('FFBSCANNERDATA04')
            print(f"Total rows: {row_count}")

            if row_count > 0:
                # Get sample data
                print("\nGetting sample data (first 3 rows)...")
                sample_data = connector.get_sample_data('FFBSCANNERDATA04', limit=3)

                if sample_data and len(sample_data) > 0:
                    print("Sample data found:")
                    for i, row in enumerate(sample_data):
                        print(f"\nRow {i+1}:")
                        for key, value in list(row.items())[:8]:  # Show first 8 columns
                            print(f"  {key}: {value}")
                        if len(row) > 8:
                            print(f"  ... and {len(row) - 8} more columns")

                    # Check date range
                    print("\nChecking date range...")
                    date_query = """
                    SELECT
                        MIN(TRANSDATE) as MIN_DATE,
                        MAX(TRANSDATE) as MAX_DATE,
                        COUNT(*) as TOTAL_RECORDS
                    FROM FFBSCANNERDATA04
                    WHERE TRANSDATE IS NOT NULL
                    """
                    date_result = connector.execute_query(date_query)
                    if date_result and len(date_result) > 0 and date_result[0].get('rows'):
                        date_row = date_result[0]['rows'][0]
                        print(f"Date range: {date_row.get('MIN_DATE', 'N/A')} to {date_row.get('MAX_DATE', 'N/A')}")
                        print(f"Records with dates: {date_row.get('TOTAL_RECORDS', 0)}")

                else:
                    print("No sample data found or empty result")
            else:
                print("Table is empty - no data to test with")
        else:
            # Check alternative FFB tables
            print("\nFFBSCANNERDATA04 not found. Looking for alternative FFB tables...")
            tables = connector.get_table_list()
            ffb_tables = [t for t in tables if 'FFB' in t.upper() and 'SCANNER' in t.upper()]

            if ffb_tables:
                print(f"Found {len(ffb_tables)} FFB/Scanner tables:")
                for table in ffb_tables:
                    row_count = connector.get_row_count(table)
                    print(f"  {table}: {row_count} rows")

                    # Get sample from first table with data
                    if row_count > 0:
                        print(f"\nGetting sample data from {table}...")
                        sample_data = connector.get_sample_data(table, limit=2)
                        if sample_data and len(sample_data) > 0:
                            print(f"Sample from {table}:")
                            for i, row in enumerate(sample_data):
                                print(f"  Row {i+1}: {list(row.keys())[:5]}...")
                            break
            else:
                print("No FFB/Scanner tables found")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_ffb_scannerdata04()