#!/usr/bin/env python3
"""
Database Debug Script
Investigates database structure and data availability
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced
import json
from datetime import datetime

def main():
    # Initialize connector
    db_path = r'D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB'
    connector = FirebirdConnectorEnhanced(db_path)
    
    print('=' * 60)
    print('DATABASE INVESTIGATION REPORT')
    print('=' * 60)
    print(f'Database: {db_path}')
    print(f'Investigation Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    # 1. Basic connection test
    print('1. CONNECTION TEST')
    print('-' * 30)
    try:
        test_result = connector.execute_query("SELECT 1 FROM RDB$DATABASE")
        print(f'✓ Connection successful: {test_result}')
    except Exception as e:
        print(f'✗ Connection failed: {e}')
        return
    
    # 2. List all user tables
    print('\n2. USER TABLES')
    print('-' * 30)
    try:
        tables_query = """
        SELECT RDB$RELATION_NAME 
        FROM RDB$RELATIONS 
        WHERE RDB$SYSTEM_FLAG = 0 
        AND RDB$RELATION_TYPE = 0
        ORDER BY RDB$RELATION_NAME
        """
        tables = connector.execute_query(tables_query)
        print(f'Found {len(tables)} user tables:')
        
        table_names = []
        for table in tables:
            table_name = table[0].strip() if table[0] else 'NULL'
            table_names.append(table_name)
            print(f'  - {table_name}')
            
    except Exception as e:
        print(f'Error listing tables: {e}')
        table_names = []
    
    # 3. Check specific tables we need
    print('\n3. TARGET TABLES CHECK')
    print('-' * 30)
    
    target_tables = [
        'FFBSCANNERDATA10',
        'FFBSCANNERDATA', 
        'EMPLOYEE',
        'FFB_DATA',
        'SCANNER_DATA',
        'TRANSACTION_DATA'
    ]
    
    existing_tables = {}
    for table in target_tables:
        try:
            count_query = f"SELECT COUNT(*) FROM {table}"
            result = connector.execute_query(count_query)
            count = result[0][0] if result else 0
            existing_tables[table] = count
            print(f'  ✓ {table}: {count} records')
        except Exception as e:
            print(f'  ✗ {table}: {str(e)[:60]}...')
    
    # 4. Check date ranges in existing tables
    print('\n4. DATE RANGE ANALYSIS')
    print('-' * 30)
    
    for table_name, count in existing_tables.items():
        if count > 0:
            print(f'\nAnalyzing {table_name}:')
            
            # Get table structure first
            try:
                structure_query = f"""
                SELECT RDB$FIELD_NAME 
                FROM RDB$RELATION_FIELDS 
                WHERE RDB$RELATION_NAME = '{table_name}'
                ORDER BY RDB$FIELD_POSITION
                """
                fields = connector.execute_query(structure_query)
                field_names = [f[0].strip() for f in fields]
                print(f'  Fields: {", ".join(field_names[:10])}{"..." if len(field_names) > 10 else ""}')
                
                # Look for date fields
                date_fields = [f for f in field_names if any(keyword in f.upper() for keyword in ['DATE', 'TIME', 'CREATED', 'UPDATED'])]
                if date_fields:
                    print(f'  Date fields found: {", ".join(date_fields)}')
                    
                    # Check date range for first date field
                    date_field = date_fields[0]
                    try:
                        date_range_query = f"""
                        SELECT MIN({date_field}), MAX({date_field}), COUNT(*)
                        FROM {table_name}
                        WHERE {date_field} IS NOT NULL
                        """
                        date_result = connector.execute_query(date_range_query)
                        if date_result and date_result[0][0]:
                            min_date, max_date, date_count = date_result[0]
                            print(f'  Date range ({date_field}): {min_date} to {max_date} ({date_count} records)')
                        else:
                            print(f'  No valid dates in {date_field}')
                    except Exception as e:
                        print(f'  Date range check failed: {str(e)[:50]}...')
                else:
                    print('  No date fields found')
                    
                # Sample data
                try:
                    sample_query = f"SELECT FIRST 2 * FROM {table_name}"
                    sample_data = connector.execute_query(sample_query)
                    print(f'  Sample data ({len(sample_data)} rows):')
                    for i, row in enumerate(sample_data):
                        # Show first 5 columns only
                        row_preview = [str(val)[:20] + '...' if len(str(val)) > 20 else str(val) for val in row[:5]]
                        print(f'    Row {i+1}: {row_preview}')
                except Exception as e:
                    print(f'  Sample data failed: {str(e)[:50]}...')
                    
            except Exception as e:
                print(f'  Structure analysis failed: {str(e)[:50]}...')
    
    # 5. Test our current queries
    print('\n5. CURRENT QUERY TESTING')
    print('-' * 30)
    
    # Load current formula file
    try:
        with open('pge2b_corrected_formula.json', 'r') as f:
            formulas = json.load(f)
        
        print('Testing queries from formula file:')
        
        # Test a few key queries
        test_queries = ['raw_ffb_data', 'employee_mapping', 'daily_performance']
        
        for query_name in test_queries:
            if query_name in formulas.get('queries', {}):
                query = formulas['queries'][query_name]
                print(f'\nTesting {query_name}:')
                print(f'Query: {query[:100]}...')
                
                try:
                    # Replace date placeholders for testing
                    test_query = query.replace('{start_date}', '2025-10-01').replace('{end_date}', '2025-11-01')
                    result = connector.execute_query(test_query)
                    print(f'  ✓ Result: {len(result)} rows')
                    if result:
                        print(f'  Sample: {result[0][:3]}...')
                except Exception as e:
                    print(f'  ✗ Error: {str(e)[:60]}...')
    
    except Exception as e:
        print(f'Formula file test failed: {e}')
    
    print('\n' + '=' * 60)
    print('INVESTIGATION COMPLETE')
    print('=' * 60)

if __name__ == '__main__':
    main()