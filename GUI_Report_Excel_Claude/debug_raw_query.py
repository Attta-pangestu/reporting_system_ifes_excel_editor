#!/usr/bin/env python3
"""
Raw Query Debug Script
Debug ISQL output to understand why queries return empty results
"""

import subprocess
import tempfile
import os
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def debug_raw_query():
    # Initialize connector
    connector = FirebirdConnectorEnhanced()
    
    print('=' * 60)
    print('RAW QUERY DEBUG')
    print('=' * 60)
    print(f'Database: {connector.db_path}')
    print(f'ISQL Path: {connector.isql_path}')
    print()
    
    # Test queries
    test_queries = [
        "SELECT 1 FROM RDB$DATABASE",
        "SELECT COUNT(*) FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0",
        "SELECT FIRST 5 RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0",
        "SELECT COUNT(*) FROM FFBSCANNERDATA",
        "SELECT FIRST 3 * FROM FFBSCANNERDATA"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f'{i}. Testing Query: {query}')
        print('-' * 50)
        
        try:
            # Create temp files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as sql_file:
                sql_file.write(query + ";\nEXIT;\n")
                sql_file_path = sql_file.name
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as output_file:
                output_path = output_file.name
            
            # Build command
            cmd = [
                connector.isql_path,
                '-u', connector.username,
                '-p', connector.password,
                f"localhost:{connector.db_path}",
                '-i', sql_file_path,
                '-o', output_path
            ]
            
            print(f'Command: {" ".join(cmd)}')
            
            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )
            
            print(f'Return code: {result.returncode}')
            print(f'STDERR: {result.stderr}')
            
            # Read output file
            if os.path.exists(output_path):
                with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
                    raw_output = f.read()
                
                print('Raw Output:')
                print('```')
                print(raw_output)
                print('```')
                
                # Try parsing
                try:
                    parsed = connector._parse_isql_output(raw_output, True)
                    print(f'Parsed result: {len(parsed)} result sets')
                    for j, result_set in enumerate(parsed):
                        print(f'  Result set {j}: {len(result_set.get("rows", []))} rows')
                        if result_set.get("rows"):
                            print(f'  Sample: {result_set["rows"][0]}')
                except Exception as e:
                    print(f'Parsing error: {e}')
            else:
                print('No output file created')
            
            # Cleanup
            try:
                os.unlink(sql_file_path)
                os.unlink(output_path)
            except:
                pass
                
        except Exception as e:
            print(f'Query failed: {e}')
        
        print()

if __name__ == '__main__':
    debug_raw_query()