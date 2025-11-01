#!/usr/bin/env python3
"""
List Database Tables Script
Identifies all tables in the database and finds FFB-related tables
"""

from firebird_connector_enhanced import FirebirdConnectorEnhanced

def main():
    connector = FirebirdConnectorEnhanced()
    
    print('=' * 60)
    print('DATABASE TABLES ANALYSIS')
    print('=' * 60)
    
    try:
        # Get all tables
        query = "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0 ORDER BY RDB$RELATION_NAME"
        result = connector.execute_query(query)
        
        if result and len(result) > 0 and 'rows' in result[0]:
            tables = result[0]['rows']
            print(f'Found {len(tables)} tables:')
            
            # Categorize tables
            ffb_tables = []
            scanner_tables = []
            employee_tables = []
            transaction_tables = []
            other_tables = []
            
            for table in tables:
                table_name = table['RDB$RELATION_NAME'].strip()
                print(f'  - {table_name}')
                
                table_upper = table_name.upper()
                if 'FFB' in table_upper:
                    ffb_tables.append(table_name)
                elif 'SCANNER' in table_upper:
                    scanner_tables.append(table_name)
                elif 'EMPLOYEE' in table_upper or 'EMP' in table_upper:
                    employee_tables.append(table_name)
                elif 'TRANS' in table_upper or 'TXN' in table_upper:
                    transaction_tables.append(table_name)
                else:
                    other_tables.append(table_name)
            
            print(f'\n=== TABLE CATEGORIES ===')
            print(f'FFB-related tables ({len(ffb_tables)}): {ffb_tables}')
            print(f'Scanner-related tables ({len(scanner_tables)}): {scanner_tables}')
            print(f'Employee-related tables ({len(employee_tables)}): {employee_tables}')
            print(f'Transaction-related tables ({len(transaction_tables)}): {transaction_tables}')
            print(f'Other tables ({len(other_tables)}): {other_tables[:10]}{"..." if len(other_tables) > 10 else ""}')
            
            # Test data counts for relevant tables
            print(f'\n=== DATA COUNTS ===')
            test_tables = ffb_tables + scanner_tables + employee_tables + transaction_tables
            
            # If no specific tables found, test some common ones
            if not test_tables:
                common_names = ['TRANSACTION', 'DATA', 'RECORDS', 'LOG', 'MASTER', 'DETAIL']
                for name in common_names:
                    matching = [t for t in other_tables if name in t.upper()]
                    test_tables.extend(matching[:3])  # Take first 3 matches
            
            for table in test_tables[:15]:  # Test first 15 tables
                try:
                    count_query = f"SELECT COUNT(*) FROM {table}"
                    count_result = connector.execute_query(count_query)
                    
                    if count_result and count_result[0]['rows']:
                        count = count_result[0]['rows'][0]['COUNT']
                        print(f'  {table}: {count} records')
                        
                        # If table has data, show structure
                        if int(count) > 0:
                            try:
                                sample_query = f"SELECT FIRST 1 * FROM {table}"
                                sample_result = connector.execute_query(sample_query)
                                if sample_result and sample_result[0]['rows']:
                                    columns = list(sample_result[0]['rows'][0].keys())
                                    print(f'    Columns ({len(columns)}): {columns[:8]}{"..." if len(columns) > 8 else ""}')
                                    
                                    # Look for date columns
                                    date_cols = [c for c in columns if any(d in c.upper() for d in ['DATE', 'TIME', 'CREATED', 'UPDATED'])]
                                    if date_cols:
                                        print(f'    Date columns: {date_cols}')
                            except Exception as e:
                                print(f'    Structure check failed: {str(e)[:40]}...')
                        
                except Exception as e:
                    print(f'  {table}: ERROR - {str(e)[:50]}...')
            
            # Look for tables with specific patterns that might contain FFB data
            print(f'\n=== POTENTIAL FFB DATA TABLES ===')
            potential_tables = []
            
            # Look for tables that might contain scanner/transaction data
            keywords = ['SCAN', 'TRANS', 'DATA', 'RECORD', 'LOG', 'DETAIL', 'MASTER']
            for keyword in keywords:
                matching = [t for t in other_tables if keyword in t.upper()]
                potential_tables.extend(matching[:2])  # Take first 2 matches per keyword
            
            # Remove duplicates
            potential_tables = list(set(potential_tables))
            
            print(f'Testing potential tables: {potential_tables[:10]}')
            for table in potential_tables[:10]:
                try:
                    count_query = f"SELECT COUNT(*) FROM {table}"
                    count_result = connector.execute_query(count_query)
                    
                    if count_result and count_result[0]['rows']:
                        count = count_result[0]['rows'][0]['COUNT']
                        if int(count) > 0:
                            print(f'  ✓ {table}: {count} records (POTENTIAL DATA SOURCE)')
                        else:
                            print(f'  - {table}: {count} records')
                except Exception as e:
                    print(f'  ✗ {table}: {str(e)[:40]}...')
                    
        else:
            print('No tables found or parsing error')
            
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    main()