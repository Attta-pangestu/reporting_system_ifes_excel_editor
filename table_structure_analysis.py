#!/usr/bin/env python3
"""
Table Structure Analysis for FFB Performance Report
Analyzes the structure of discovered tables to understand their fields and relationships.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector import FirebirdConnector
from datetime import datetime

def analyze_table_structures():
    """Analyze the structure of discovered tables"""
    
    # Database connection details
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    username = "SYSDBA"
    password = "masterkey"
    
    # Initialize connector
    connector = FirebirdConnector(db_path, username, password)
    
    # Tables to analyze based on discovery results
    tables_to_analyze = [
        # Division tables
        'CRDIVISION',
        'DIVISIONVIEW',
        
        # Worker/Employee tables
        'WORKERINFO',
        'EMP',
        'USERWORKER',
        
        # Labour/Job related tables
        'LABOURCATVIEW',
        'LABOURCODEVIEW',
        'JOBCODE',
        
        # Views that might contain useful data
        'JOBSTATUSVIEW',
        'DESIGVIEW',
        'GRADEVIEW',
        
        # OC (Organizational Code) related
        'OC',
        'OCFIELD'
    ]
    
    results = {}
    
    print("ANALYZING TABLE STRUCTURES")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Database: {db_path}")
    print()
    
    for table_name in tables_to_analyze:
        print(f"Analyzing table: {table_name}")
        
        # Get table structure - simplified for older Firebird
        structure_query = f"""
        SELECT 
            RDB$FIELD_NAME as FIELD_NAME
        FROM RDB$RELATION_FIELDS 
        WHERE RDB$RELATION_NAME = '{table_name}'
        ORDER BY RDB$FIELD_POSITION;
        """
        
        # Get sample data (first 3 rows)
        sample_query = f"SELECT FIRST 3 * FROM {table_name};"
        
        try:
            # Get structure
            structure_result = connector.execute_query(structure_query)
            
            # Get sample data
            sample_result = connector.execute_query(sample_query)
            
            results[table_name] = {
                'structure': structure_result,
                'sample': sample_result,
                'status': 'success'
            }
            
            print(f"  ✓ Structure: {len(structure_result[0]['rows']) if structure_result and structure_result[0]['rows'] else 0} fields")
            print(f"  ✓ Sample: {len(sample_result[0]['rows']) if sample_result and sample_result[0]['rows'] else 0} rows")
            
        except Exception as e:
            results[table_name] = {
                'error': str(e),
                'status': 'error'
            }
            print(f"  ✗ Error: {str(e)}")
        
        print()
    
    # Save results to file
    output_file = "table_structure_analysis_results.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("TABLE STRUCTURE ANALYSIS RESULTS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Database: {db_path}\n\n")
        
        for table_name, result in results.items():
            f.write(f"\n{table_name}\n")
            f.write("-" * 40 + "\n")
            
            if result['status'] == 'error':
                f.write(f"ERROR: {result['error']}\n")
                continue
            
            # Write structure
            f.write("STRUCTURE:\n")
            if result['structure'] and result['structure'][0]['rows']:
                for row in result['structure'][0]['rows']:
                    field_name = row.get('FIELD_NAME', '').strip()
                    f.write(f"  {field_name}\n")
            else:
                f.write("  No structure data available\n")
            
            f.write("\nSAMPLE DATA:\n")
            if result['sample'] and result['sample'][0]['rows']:
                # Write headers
                headers = result['sample'][0]['headers']
                f.write("  Headers: " + " | ".join(headers) + "\n")
                
                # Write sample rows
                for i, row in enumerate(result['sample'][0]['rows'][:3]):
                    values = []
                    for header in headers:
                        value = str(row.get(header, ''))
                        if len(value) > 20:
                            value = value[:17] + "..."
                        values.append(value)
                    f.write(f"  Row {i+1}: " + " | ".join(values) + "\n")
            else:
                f.write("  No sample data available\n")
            
            f.write("=" * 60 + "\n")
    
    print(f"Analysis complete! Results saved to: {output_file}")
    
    # Analyze relationships and provide recommendations
    print("\nANALYZING RELATIONSHIPS AND PROVIDING RECOMMENDATIONS...")
    
    # Check for key relationships
    relationship_queries = {
        'WORKERID_in_FFBSCANNERDATA10': "SELECT FIRST 5 DISTINCT WORKERID FROM FFBSCANNERDATA10 WHERE WORKERID IS NOT NULL ORDER BY WORKERID;",
        'EMPID_in_WORKERINFO': "SELECT FIRST 5 DISTINCT EMPID FROM WORKERINFO WHERE EMPID IS NOT NULL ORDER BY EMPID;",
        'OCID_in_FFBSCANNERDATA10': "SELECT FIRST 5 DISTINCT OCID FROM FFBSCANNERDATA10 WHERE OCID IS NOT NULL ORDER BY OCID;",
        'FIELDDIVID_in_WORKERINFO': "SELECT FIRST 5 DISTINCT FIELDDIVID FROM WORKERINFO WHERE FIELDDIVID IS NOT NULL ORDER BY FIELDDIVID;"
    }
    
    relationship_results = {}
    for rel_name, query in relationship_queries.items():
        try:
            result = connector.execute_query(query)
            relationship_results[rel_name] = result
            print(f"  ✓ {rel_name}: Found data")
        except Exception as e:
            relationship_results[rel_name] = f"Error: {str(e)}"
            print(f"  ✗ {rel_name}: {str(e)}")
    
    # Append relationship analysis to file
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write("\n\nRELATIONSHIP ANALYSIS\n")
        f.write("=" * 60 + "\n")
        
        for rel_name, result in relationship_results.items():
            f.write(f"\n{rel_name}:\n")
            if isinstance(result, str):
                f.write(f"  {result}\n")
            elif result and result[0]['rows']:
                f.write("  Sample values: ")
                values = [str(row[list(row.keys())[0]]) for row in result[0]['rows'][:5]]
                f.write(", ".join(values) + "\n")
            else:
                f.write("  No data found\n")
        
        f.write("\n\nRECOMMENDATIONS FOR REPORT QUERY:\n")
        f.write("=" * 60 + "\n")
        f.write("Based on the analysis, here are the recommended table joins:\n\n")
        
        f.write("1. MAIN DATA SOURCE:\n")
        f.write("   - FFBSCANNERDATA10: Transaction data with WORKERID, OCID, TRANSSTATUS\n\n")
        
        f.write("2. WORKER INFORMATION:\n")
        f.write("   - WORKERINFO: Links EMPID to FIELDDIVID, LABOURCDID, MANDORE status\n")
        f.write("   - EMP: Employee master data (if available)\n\n")
        
        f.write("3. DIVISION/ESTATE INFORMATION:\n")
        f.write("   - CRDIVISION or DIVISIONVIEW: Division master data\n")
        f.write("   - OC: Organizational code information\n\n")
        
        f.write("4. JOB/ROLE INFORMATION:\n")
        f.write("   - LABOURCODEVIEW: Labour code descriptions\n")
        f.write("   - JOBCODE: Job code information\n\n")
        
        f.write("5. SUGGESTED JOIN LOGIC:\n")
        f.write("   FFBSCANNERDATA10.WORKERID = WORKERINFO.EMPID\n")
        f.write("   WORKERINFO.FIELDDIVID = CRDIVISION.ID (or similar)\n")
        f.write("   WORKERINFO.LABOURCDID = LABOURCODEVIEW.ID (or similar)\n")
        f.write("   FFBSCANNERDATA10.OCID = OC.ID (or similar)\n\n")

if __name__ == "__main__":
    analyze_table_structures()