#!/usr/bin/env python3
"""
Analyze FFB Tables Structure
Examines the structure and sample data from FFBLOADINGCROP tables
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def main():
    connector = FirebirdConnectorEnhanced()
    
    print('=' * 80)
    print('FFB TABLES STRUCTURE ANALYSIS')
    print('=' * 80)
    
    # Test FFBLOADINGCROP01 as representative
    table_name = 'FFBLOADINGCROP01'
    
    try:
        # Get sample data to understand structure
        sample_query = f"SELECT FIRST 3 * FROM {table_name}"
        result = connector.execute_query(sample_query)
        
        if result and result[0]['rows']:
            sample_data = result[0]['rows']
            
            print(f'Table: {table_name}')
            print(f'Sample records: {len(sample_data)}')
            print()
            
            # Show all columns and sample values
            if sample_data:
                columns = list(sample_data[0].keys())
                print(f'Total columns: {len(columns)}')
                print()
                
                for i, col in enumerate(columns, 1):
                    values = [str(row.get(col, 'NULL'))[:30] for row in sample_data]
                    print(f'{i:2d}. {col:<25} | {" | ".join(values)}')
                
                print('\n' + '=' * 80)
                print('COLUMN ANALYSIS')
                print('=' * 80)
                
                # Identify key columns
                date_columns = []
                id_columns = []
                quantity_columns = []
                employee_columns = []
                field_columns = []
                
                for col in columns:
                    col_upper = col.upper()
                    if any(d in col_upper for d in ['DATE', 'TIME']):
                        date_columns.append(col)
                    elif 'ID' in col_upper or col_upper.endswith('NO'):
                        id_columns.append(col)
                    elif any(q in col_upper for q in ['BUNCH', 'QTY', 'WEIGHT', 'COUNT']):
                        quantity_columns.append(col)
                    elif any(e in col_upper for e in ['EMP', 'USER', 'OPERATOR']):
                        employee_columns.append(col)
                    elif any(f in col_upper for f in ['FIELD', 'BLOCK', 'AREA']):
                        field_columns.append(col)
                
                print(f'Date/Time columns: {date_columns}')
                print(f'ID columns: {id_columns}')
                print(f'Quantity columns: {quantity_columns}')
                print(f'Employee columns: {employee_columns}')
                print(f'Field columns: {field_columns}')
                
                # Check date range
                if date_columns:
                    date_col = date_columns[0]
                    print(f'\nDate range analysis using {date_col}:')
                    
                    date_range_query = f"""
                    SELECT 
                        MIN({date_col}) as MIN_DATE,
                        MAX({date_col}) as MAX_DATE,
                        COUNT(*) as TOTAL_RECORDS
                    FROM {table_name}
                    WHERE {date_col} IS NOT NULL
                    """
                    
                    date_result = connector.execute_query(date_range_query)
                    if date_result and date_result[0]['rows']:
                        date_info = date_result[0]['rows'][0]
                        print(f"  Min Date: {date_info.get('MIN_DATE', 'N/A')}")
                        print(f"  Max Date: {date_info.get('MAX_DATE', 'N/A')}")
                        print(f"  Total Records: {date_info.get('TOTAL_RECORDS', 'N/A')}")
                        
                        # Check recent data (last 30 days)
                        recent_query = f"""
                        SELECT COUNT(*) as RECENT_COUNT
                        FROM {table_name}
                        WHERE {date_col} >= CURRENT_DATE - 30
                        """
                        
                        recent_result = connector.execute_query(recent_query)
                        if recent_result and recent_result[0]['rows']:
                            recent_count = recent_result[0]['rows'][0]['RECENT_COUNT']
                            print(f"  Recent records (last 30 days): {recent_count}")
                
                # Test other FFBLOADINGCROP tables
                print(f'\n' + '=' * 80)
                print('OTHER FFB TABLES SUMMARY')
                print('=' * 80)
                
                for i in range(2, 13):  # FFBLOADINGCROP02 to FFBLOADINGCROP12
                    table = f'FFBLOADINGCROP{i:02d}'
                    try:
                        count_query = f"SELECT COUNT(*) FROM {table}"
                        count_result = connector.execute_query(count_query)
                        if count_result and count_result[0]['rows']:
                            count = count_result[0]['rows'][0]['COUNT']
                            print(f'{table}: {count} records')
                    except Exception as e:
                        print(f'{table}: ERROR - {str(e)[:40]}...')
                
        else:
            print(f'No data found in {table_name}')
            
    except Exception as e:
        print(f'Error analyzing {table_name}: {e}')
        
    # Also check if there are any employee-related tables
    print(f'\n' + '=' * 80)
    print('EMPLOYEE TABLES CHECK')
    print('=' * 80)
    
    employee_tables = ['EMPLOYEE', 'EMPLOYEES', 'EMP', 'EMPMASTER', 'CREMPLOYEEMASTER']
    for table in employee_tables:
        try:
            count_query = f"SELECT COUNT(*) FROM {table}"
            count_result = connector.execute_query(count_query)
            if count_result and count_result[0]['rows']:
                count = count_result[0]['rows'][0]['COUNT']
                print(f'{table}: {count} records')
                
                if int(count) > 0:
                    # Get sample structure
                    sample_query = f"SELECT FIRST 1 * FROM {table}"
                    sample_result = connector.execute_query(sample_query)
                    if sample_result and sample_result[0]['rows']:
                        columns = list(sample_result[0]['rows'][0].keys())
                        print(f'  Columns: {columns[:10]}{"..." if len(columns) > 10 else ""}')
        except Exception as e:
            print(f'{table}: Not found or error')

if __name__ == '__main__':
    main()