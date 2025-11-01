#!/usr/bin/env python3
"""Test script to verify database queries work with real data"""

import json
from database_connector import DatabaseConnector
from config_manager import ConfigManager

def test_database_queries():
    """Test database queries with real database connection"""
    print("Testing database queries with real data...")
    
    # Load database configuration
    config_manager = ConfigManager()
    databases = config_manager.get_databases()
    
    if 'ptrj_p2b' not in databases:
        print("Database 'ptrj_p2b' not found in configuration!")
        print(f"Available databases: {list(databases.keys())}")
        return
    
    db_config = databases['ptrj_p2b']
    print(f"Database path: {db_config['path']}")
    
    # Create database connector
    try:
        db_connector = DatabaseConnector(
            db_config['path'],
            db_config['username'],
            db_config['password']
        )
        print("Database connector created successfully")
    except Exception as e:
        print(f"Error creating database connector: {e}")
        return
    
    # Load template queries
    try:
        with open('templates/laporan_kinerja_template.json', 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        print("Template loaded successfully")
    except Exception as e:
        print(f"Error loading template: {e}")
        return
    
    # Test each query
    queries = template_data.get('queries', [])
    print(f"\nTesting {len(queries)} queries...")
    
    for i, query_config in enumerate(queries, 1):
        query_name = query_config.get('name', f'Query {i}')
        sql = query_config.get('sql', '')
        
        print(f"\n--- Testing Query {i}: {query_name} ---")
        print(f"SQL: {sql[:100]}{'...' if len(sql) > 100 else ''}")
        
        try:
            # Execute query
            result = db_connector.execute_query(sql)
            
            if result:
                print(f"✓ Query executed successfully")
                print(f"  Result type: {type(result)}")
                
                if isinstance(result, list) and result:
                    print(f"  Number of rows: {len(result)}")
                    print(f"  First row keys: {list(result[0].keys()) if isinstance(result[0], dict) else 'Not a dict'}")
                    
                    # Show sample data (first few rows)
                    sample_size = min(3, len(result))
                    print(f"  Sample data (first {sample_size} rows):")
                    for j, row in enumerate(result[:sample_size]):
                        if isinstance(row, dict):
                            # Show first few fields of each row
                            sample_fields = dict(list(row.items())[:3])
                            print(f"    Row {j+1}: {sample_fields}")
                        else:
                            print(f"    Row {j+1}: {row}")
                else:
                    print(f"  Result: {result}")
                    
        except Exception as e:
            print(f"✗ Query failed: {e}")
            
    print("\nDatabase query testing completed!")

def test_specific_table_queries():
    """Test specific table queries to understand data structure"""
    print("\n" + "="*50)
    print("Testing specific table queries...")
    
    # Load database configuration
    config_manager = ConfigManager()
    databases = config_manager.get_databases()
    
    if 'ptrj_p2b' not in databases:
        print("Database 'ptrj_p2b' not found in configuration!")
        return
    
    db_config = databases['ptrj_p2b']
    
    # Create database connector
    try:
        db_connector = DatabaseConnector(
            db_config['path'],
            db_config['username'],
            db_config['password']
        )
    except Exception as e:
        print(f"Error creating database connector: {e}")
        return
    
    # Test queries for key tables
    test_queries = [
        {
            'name': 'FFBSCANNERDATA10 Sample',
            'sql': 'SELECT FIRST 5 * FROM FFBSCANNERDATA10 WHERE TANGGAL >= \'2024-10-01\''
        },
        {
            'name': 'FFBSCANNERDATA10 Count',
            'sql': 'SELECT COUNT(*) as TOTAL_RECORDS FROM FFBSCANNERDATA10 WHERE TANGGAL >= \'2024-10-01\''
        },
        {
            'name': 'Date Range Check',
            'sql': 'SELECT MIN(TANGGAL) as MIN_DATE, MAX(TANGGAL) as MAX_DATE FROM FFBSCANNERDATA10'
        }
    ]
    
    for query_info in test_queries:
        print(f"\n--- {query_info['name']} ---")
        print(f"SQL: {query_info['sql']}")
        
        try:
            result = db_connector.execute_query(query_info['sql'])
            
            if result:
                print(f"✓ Success - {len(result)} rows returned")
                for row in result:
                    print(f"  {row}")
            else:
                print("✓ Success - No data returned")
                
        except Exception as e:
            print(f"✗ Failed: {e}")

if __name__ == "__main__":
    test_database_queries()
    test_specific_table_queries()