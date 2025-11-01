#!/usr/bin/env python3
"""
Debug script to examine raw ISQL output
"""

import os
import subprocess
import tempfile
from pathlib import Path

def test_raw_isql_output():
    """Test raw ISQL output to understand parsing issues"""
    
    # Database connection parameters
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Ifes Auto report\excel_method\GUI_Report_Excel_Claude\IFES_MONITORING.FDB"
    username = "SYSDBA"
    password = "masterkey"
    
    print("Testing raw ISQL output...")
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as sql_file:
        sql_file.write("SELECT COUNT(*) AS TOTAL_ROWS FROM EMP;\n")
        sql_file.write("SELECT * FROM EMP;\n")
        sql_file.write("COMMIT;\n")
        sql_file_path = sql_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as output_file:
        output_file_path = output_file.name
    
    try:
        # Build ISQL command
        isql_path = r"C:\Program Files (x86)\Firebird\Firebird_1_5\bin\isql.exe"
        
        cmd = [
            isql_path,
            "-input", sql_file_path,
            "-output", output_file_path
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        
        # Execute ISQL
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        # Read output file
        if os.path.exists(output_file_path):
            with open(output_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                output_content = f.read()
            
            print("\n=== RAW OUTPUT FILE CONTENT ===")
            print(repr(output_content))
            print("\n=== FORMATTED OUTPUT ===")
            print(output_content)
            
            # Analyze line by line
            lines = output_content.split('\n')
            print(f"\n=== LINE BY LINE ANALYSIS ({len(lines)} lines) ===")
            for i, line in enumerate(lines):
                print(f"Line {i:2d}: {repr(line)}")
        else:
            print("❌ Output file not created")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        # Cleanup
        try:
            os.unlink(sql_file_path)
            os.unlink(output_file_path)
        except:
            pass

if __name__ == "__main__":
    test_raw_isql_output()