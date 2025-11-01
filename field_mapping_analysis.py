#!/usr/bin/env python3
"""
Field Mapping Analysis for FFB Performance Report
Based on actual database structure analysis
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector import FirebirdConnector

def analyze_field_mapping():
    """Analyze and create field mapping for Excel template"""
    
    print("FFB Performance Report - Field Mapping Analysis")
    print("=" * 60)
    
    # Database structure analysis results
    ffb_fields = [
        'ID', 'SCANUSERID', 'OCID', 'WORKERID', 'CARRIERID', 'FIELDID', 'TASKNO', 
        'RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 'LONGSTALKBCH', 'RATDMGBCH', 
        'LOOSEFRUIT', 'TRANSNO', 'TRANSDATE', 'TRANSTIME', 'UPLOADDATETIME', 
        'RECORDTAG', 'TRANSSTATUS', 'TRANSTYPE', 'LASTUSER', 'LASTUPDATED', 
        'UNDERRIPEBCH', 'OVERRIPEBCH', 'ABNORMALBCH', 'LOOSEFRUIT2'
    ]
    
    worker_fields = [
        'ID', 'EMPID', 'RESIDENT', 'RESQTRNO', 'NONRESADDRESS1', 'NONRESADDRESS2', 
        'NONRESADDRESS3', 'NONRESPOSTCODE', 'NONRESCITYID', 'NONRESSTATEID', 
        'NONRESCOUNTRYID', 'NONRESTEL', 'PERMANENTRES', 'FORWORKER', 'FWPERMITNO', 
        'FWPERMITDATEISSUE', 'FWPASSPORTNO', 'FWADDRESS1', 'FWADDRESS2', 'FWADDRESS3', 
        'FWORGCOUNTRYID', 'JOBSTATUSID', 'LABOURCDID', 'LABOURCATID', 'QTRSTATUSID', 
        'RATETYPEID', 'MANDORE', 'FIELDDIVID', 'LASTUSER', 'LASTUPDATED', 'TEAMSIZE', 
        'PAYSTATION', 'MANDORESTARTDATE', 'GANGNOSTARTDATE', 'GANGNOID', 'CHILD18BELOW', 
        'CHILD18ABOVE', 'HANDICAP', 'HANDICAPIPT', 'SHIFTNO'
    ]
    
    # Excel template requirements
    excel_template = {
        'ESTATE': 'Estate/Kebun name',
        'DIVISI': 'Division name', 
        'KARYAWAN': 'Employee name',
        'ROLE': 'Employee role (KERANI/MANDOR/ASISTEN)',
        'JUMLAH TRANSAKSI': 'Total transaction count',
        'PERSENTASE TERVERIFIKASI': 'Verification percentage',
        'KETERANGAN PERBEDAAN': 'Difference description',
        'PERIODE LAPORAN': 'Report period'
    }
    
    print("\nFIELD MAPPING ANALYSIS")
    print("=" * 40)
    
    # Create comprehensive mapping
    field_mapping = {}
    
    print("\n1. ESTATE (Estate/Kebun)")
    print("   - Source: Need to identify from lookup tables or configuration")
    print("   - Possible approach: Use OCID from FFBSCANNERDATA10 to lookup estate name")
    field_mapping['ESTATE'] = {
        'source': 'LOOKUP_TABLE or CONFIGURATION',
        'field': 'OCID',
        'table': 'FFBSCANNERDATA10',
        'note': 'Need to find estate master table or use OCID mapping'
    }
    
    print("\n2. DIVISI (Division)")
    print("   - Source: FIELDDIVID from WORKERINFO")
    print("   - Join: WORKERINFO.EMPID = FFBSCANNERDATA10.WORKERID")
    field_mapping['DIVISI'] = {
        'source': 'FIELDDIVID',
        'table': 'WORKERINFO',
        'join_field': 'EMPID',
        'note': 'May need division master table for division names'
    }
    
    print("\n3. KARYAWAN (Employee Name)")
    print("   - Source: Need employee master table")
    print("   - Join: Employee.ID = FFBSCANNERDATA10.WORKERID")
    field_mapping['KARYAWAN'] = {
        'source': 'EMPLOYEE_MASTER_TABLE',
        'field': 'NAME_FIELD',
        'join_field': 'ID',
        'note': 'Need to find employee master table with names'
    }
    
    print("\n4. ROLE (Employee Role)")
    print("   - Source: LABOURCATID or JOBSTATUSID from WORKERINFO")
    print("   - May need lookup table for role descriptions")
    field_mapping['ROLE'] = {
        'source': 'LABOURCATID',
        'table': 'WORKERINFO',
        'join_field': 'EMPID',
        'note': 'Need labour category master for role names (KERANI/MANDOR/ASISTEN)'
    }
    
    print("\n5. JUMLAH TRANSAKSI (Transaction Count)")
    print("   - Source: COUNT(*) from FFBSCANNERDATA10")
    print("   - Group by: WORKERID, TRANSDATE")
    field_mapping['JUMLAH_TRANSAKSI'] = {
        'source': 'COUNT(*)',
        'table': 'FFBSCANNERDATA10',
        'group_by': ['WORKERID', 'TRANSDATE'],
        'note': 'Calculated field'
    }
    
    print("\n6. PERSENTASE TERVERIFIKASI (Verification Percentage)")
    print("   - Source: TRANSSTATUS from FFBSCANNERDATA10")
    print("   - Logic: Count verified vs total transactions")
    field_mapping['PERSENTASE_TERVERIFIKASI'] = {
        'source': 'TRANSSTATUS',
        'table': 'FFBSCANNERDATA10',
        'calculation': 'COUNT(verified) / COUNT(total) * 100',
        'note': 'Need to identify verified status codes'
    }
    
    print("\n7. KETERANGAN PERBEDAAN (Difference Description)")
    print("   - Source: Calculated based on verification percentage")
    print("   - Logic: Categorize based on percentage thresholds")
    field_mapping['KETERANGAN_PERBEDAAN'] = {
        'source': 'CALCULATED',
        'logic': 'IF percentage >= 95% THEN "Sesuai" ELSE "Ada perbedaan"',
        'note': 'Business logic based on verification percentage'
    }
    
    print("\n8. PERIODE LAPORAN (Report Period)")
    print("   - Source: TRANSDATE from FFBSCANNERDATA10")
    print("   - Format: Extract month/year from transaction dates")
    field_mapping['PERIODE_LAPORAN'] = {
        'source': 'TRANSDATE',
        'table': 'FFBSCANNERDATA10',
        'format': 'YYYY-MM or date range',
        'note': 'Extract from transaction date range'
    }
    
    return field_mapping

def generate_sql_queries(field_mapping):
    """Generate SQL queries for data extraction"""
    
    print("\n" + "=" * 60)
    print("RECOMMENDED SQL QUERIES")
    print("=" * 60)
    
    # Main data extraction query
    main_query = """
-- Main FFB Performance Report Query
SELECT 
    f.OCID as estate_code,
    w.FIELDDIVID as division_id,
    f.WORKERID as worker_id,
    w.LABOURCATID as role_id,
    w.JOBSTATUSID as job_status_id,
    f.TRANSDATE as transaction_date,
    COUNT(*) as total_transactions,
    COUNT(CASE WHEN f.TRANSSTATUS = '704' THEN 1 END) as verified_transactions,
    CAST(COUNT(CASE WHEN f.TRANSSTATUS = '704' THEN 1 END) * 100.0 / COUNT(*) AS DECIMAL(5,2)) as verification_percentage
FROM FFBSCANNERDATA10 f
LEFT JOIN WORKERINFO w ON w.EMPID = f.WORKERID
WHERE f.TRANSDATE BETWEEN ? AND ?  -- Date range parameters
GROUP BY f.OCID, w.FIELDDIVID, f.WORKERID, w.LABOURCATID, w.JOBSTATUSID, f.TRANSDATE
ORDER BY f.OCID, w.FIELDDIVID, f.WORKERID, f.TRANSDATE
"""
    
    print("1. MAIN DATA EXTRACTION QUERY:")
    print(main_query)
    
    # Lookup queries
    lookup_queries = {
        'estate_lookup': """
-- Estate/OCID Lookup (need to find estate master table)
SELECT DISTINCT OCID FROM FFBSCANNERDATA10 ORDER BY OCID
""",
        'division_lookup': """
-- Division Lookup (need to find division master table)
SELECT DISTINCT FIELDDIVID FROM WORKERINFO WHERE FIELDDIVID IS NOT NULL ORDER BY FIELDDIVID
""",
        'role_lookup': """
-- Role/Labour Category Lookup (need to find labour category master table)
SELECT DISTINCT LABOURCATID FROM WORKERINFO WHERE LABOURCATID IS NOT NULL ORDER BY LABOURCATID
""",
        'status_lookup': """
-- Transaction Status Lookup
SELECT DISTINCT TRANSSTATUS FROM FFBSCANNERDATA10 ORDER BY TRANSSTATUS
"""
    }
    
    print("\n2. LOOKUP QUERIES:")
    for name, query in lookup_queries.items():
        print(f"\n{name.upper()}:")
        print(query)
    
    return main_query, lookup_queries

def create_data_extraction_plan():
    """Create step-by-step data extraction plan"""
    
    print("\n" + "=" * 60)
    print("DATA EXTRACTION IMPLEMENTATION PLAN")
    print("=" * 60)
    
    steps = [
        {
            'step': 1,
            'title': 'Identify Master Tables',
            'description': 'Find estate, division, employee, and role master tables',
            'queries': [
                "SELECT * FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%ESTATE%'",
                "SELECT * FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%DIVISION%'", 
                "SELECT * FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%EMPLOYEE%'",
                "SELECT * FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%LABOUR%'"
            ]
        },
        {
            'step': 2,
            'title': 'Analyze Transaction Status Codes',
            'description': 'Understand what TRANSSTATUS values mean for verification',
            'queries': [
                "SELECT TRANSSTATUS, COUNT(*) FROM FFBSCANNERDATA10 GROUP BY TRANSSTATUS"
            ]
        },
        {
            'step': 3,
            'title': 'Test Date Range Filtering',
            'description': 'Verify date filtering works correctly',
            'queries': [
                "SELECT MIN(TRANSDATE), MAX(TRANSDATE) FROM FFBSCANNERDATA10",
                "SELECT COUNT(*) FROM FFBSCANNERDATA10 WHERE TRANSDATE >= '2024-01-01'"
            ]
        },
        {
            'step': 4,
            'title': 'Create Sample Report Query',
            'description': 'Build and test the main report query with sample data',
            'queries': [
                "-- Use the main query from above with actual date range"
            ]
        },
        {
            'step': 5,
            'title': 'Implement Excel Generation',
            'description': 'Create Python script to generate Excel report',
            'tasks': [
                'Extract data using main query',
                'Apply business logic for KETERANGAN_PERBEDAAN',
                'Format data according to Excel template',
                'Generate Excel file with proper formatting'
            ]
        }
    ]
    
    for step in steps:
        print(f"\nSTEP {step['step']}: {step['title']}")
        print(f"Description: {step['description']}")
        if 'queries' in step:
            print("Queries to run:")
            for query in step['queries']:
                print(f"  - {query}")
        if 'tasks' in step:
            print("Tasks:")
            for task in step['tasks']:
                print(f"  - {task}")
    
    return steps

def main():
    """Main analysis function"""
    
    # Analyze field mapping
    field_mapping = analyze_field_mapping()
    
    # Generate SQL queries
    main_query, lookup_queries = generate_sql_queries(field_mapping)
    
    # Create implementation plan
    steps = create_data_extraction_plan()
    
    # Save results
    results_file = "field_mapping_complete_analysis.txt"
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write("FFB Performance Report - Complete Field Mapping Analysis\n")
        f.write("=" * 60 + "\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("FIELD MAPPING:\n")
        f.write("-" * 20 + "\n")
        for field, mapping in field_mapping.items():
            f.write(f"\n{field}:\n")
            for key, value in mapping.items():
                f.write(f"  {key}: {value}\n")
        
        f.write(f"\n\nMAIN QUERY:\n")
        f.write("-" * 15 + "\n")
        f.write(main_query)
        
        f.write(f"\n\nLOOKUP QUERIES:\n")
        f.write("-" * 20 + "\n")
        for name, query in lookup_queries.items():
            f.write(f"\n{name}:\n{query}\n")
        
        f.write(f"\n\nIMPLEMENTATION STEPS:\n")
        f.write("-" * 25 + "\n")
        for step in steps:
            f.write(f"\nStep {step['step']}: {step['title']}\n")
            f.write(f"Description: {step['description']}\n")
            if 'queries' in step:
                f.write("Queries:\n")
                for query in step['queries']:
                    f.write(f"  - {query}\n")
            if 'tasks' in step:
                f.write("Tasks:\n")
                for task in step['tasks']:
                    f.write(f"  - {task}\n")
    
    print(f"\n✓ Complete analysis saved to: {results_file}")
    print("✓ Field mapping analysis completed successfully")
    
    # Next steps recommendation
    print("\n" + "=" * 60)
    print("NEXT STEPS RECOMMENDATION")
    print("=" * 60)
    print("1. Run master table discovery queries")
    print("2. Analyze transaction status codes")
    print("3. Create data extraction script")
    print("4. Implement Excel report generator")
    print("5. Test with sample data")

if __name__ == "__main__":
    main()