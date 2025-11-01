#!/usr/bin/env python3
"""
Fix Query Structure Script
Based on gui_multi_estate_ffb_analysis.py reference implementation
"""

import json
import shutil
from datetime import datetime

def create_corrected_queries():
    """Create corrected query templates based on reference implementation"""
    
    corrected_template = {
        "template_info": {
            "name": "PGE 2B FFB Analysis Report - Corrected Structure",
            "version": "6.0",
            "description": "FFB Scanner Analysis with proper query structure based on reference implementation",
            "estate": "PGE 2B",
            "created_date": "2025-11-01",
            "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "correction_notes": "Fixed corrupted SQL syntax. Based on gui_multi_estate_ffb_analysis.py structure."
        },
        "data_sources": {
            "ffb_scanner_data": "FFBSCANNERDATA{month:02d}",
            "employee_data": "EMP",
            "division_data": "CRDIVISION",
            "field_data": "OCFIELD"
        },
        "queries": {
            "employee_mapping": {
                "description": "Get employee ID to name mapping from EMP table",
                "sql": "SELECT DISTINCT \"ID EMPCODE\" as EMPID, \"ID NAME\" as EMPNAME FROM EMP WHERE \"ID EMPCODE\" IS NOT NULL AND \"ID NAME\" IS NOT NULL",
                "cache": True
            },
            "division_list": {
                "description": "Get divisions using proper JOIN with OCFIELD and CRDIVISION",
                "sql": """SELECT DISTINCT b.DIVID, c.DIVNAME 
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         WHERE b.DIVID IS NOT NULL AND c.DIVNAME IS NOT NULL 
                         ORDER BY b.DIVID""",
                "parameters": ["month"]
            },
            "raw_ffb_data": {
                "description": "Extract raw FFB scanner data with proper field structure",
                "sql": """SELECT a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, 
                                a.FIELDID, b.FIELDNAME, b.DIVID, c.DIVNAME,
                                a.TASKNO, a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, 
                                a.LONGSTALKBCH, a.RATDMGBCH, a.LOOSEFRUIT, a.TRANSNO, 
                                a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME, a.RECORDTAG, 
                                a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED, 
                                a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2 
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         ORDER BY a.TRANSDATE, a.TRANSTIME""",
                "parameters": ["start_date", "end_date", "month"]
            },
            "division_data": {
                "description": "Get data for specific division with proper JOINs",
                "sql": """SELECT a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, 
                                a.FIELDID, b.FIELDNAME, b.DIVID, c.DIVNAME,
                                a.TASKNO, a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, 
                                a.LONGSTALKBCH, a.RATDMGBCH, a.LOOSEFRUIT, a.TRANSNO, 
                                a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME, a.RECORDTAG, 
                                a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED, 
                                a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2 
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         WHERE b.DIVID = '{div_id}' 
                           AND a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         ORDER BY a.TRANSDATE, a.TRANSTIME""",
                "parameters": ["div_id", "start_date", "end_date", "month"]
            },
            "daily_summary": {
                "description": "Daily summary of FFB scanner activities",
                "sql": """SELECT a.TRANSDATE, 
                                COUNT(*) as TOTAL_TRANSACTIONS,
                                SUM(a.RIPEBCH + a.UNRIPEBCH + a.OVERRIPEBCH + a.UNDERRIPEBCH) as TOTAL_BUNCHES,
                                SUM(a.LOOSEFRUIT + a.LOOSEFRUIT2) as TOTAL_LOOSEFRUIT,
                                COUNT(DISTINCT a.SCANUSERID) as UNIQUE_SCANNERS
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         GROUP BY a.TRANSDATE 
                         ORDER BY a.TRANSDATE""",
                "parameters": ["start_date", "end_date", "month"]
            },
            "scanner_performance": {
                "description": "Performance summary by scanner user",
                "sql": """SELECT a.SCANUSERID, e.\"ID NAME\" as SCANNER_NAME,
                                COUNT(*) as TOTAL_SCANS,
                                SUM(a.RIPEBCH + a.UNRIPEBCH + a.OVERRIPEBCH + a.UNDERRIPEBCH) as TOTAL_BUNCHES,
                                SUM(a.LOOSEFRUIT + a.LOOSEFRUIT2) as TOTAL_LOOSEFRUIT
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         LEFT JOIN EMP e ON a.SCANUSERID = e.\"ID EMPCODE\"
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         GROUP BY a.SCANUSERID, e.\"ID NAME\" 
                         ORDER BY TOTAL_BUNCHES DESC""",
                "parameters": ["start_date", "end_date", "month"]
            },
            "field_performance": {
                "description": "Performance summary by field with division info",
                "sql": """SELECT a.FIELDID, b.FIELDNAME, b.DIVID, c.DIVNAME,
                                COUNT(*) as TOTAL_TRANSACTIONS,
                                SUM(a.RIPEBCH + a.UNRIPEBCH + a.OVERRIPEBCH + a.UNDERRIPEBCH) as TOTAL_BUNCHES,
                                SUM(a.LOOSEFRUIT + a.LOOSEFRUIT2) as TOTAL_LOOSEFRUIT
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         GROUP BY a.FIELDID, b.FIELDNAME, b.DIVID, c.DIVNAME 
                         ORDER BY TOTAL_BUNCHES DESC""",
                "parameters": ["start_date", "end_date", "month"]
            },
            "quality_analysis": {
                "description": "Quality analysis of FFB bunches",
                "sql": """SELECT a.TRANSDATE,
                                SUM(a.RIPEBCH) as RIPE_BUNCHES,
                                SUM(a.UNRIPEBCH) as UNRIPE_BUNCHES,
                                SUM(a.OVERRIPEBCH) as OVERRIPE_BUNCHES,
                                SUM(a.UNDERRIPEBCH) as UNDERRIPE_BUNCHES,
                                SUM(a.BLACKBCH) as BLACK_BUNCHES,
                                SUM(a.ROTTENBCH) as ROTTEN_BUNCHES,
                                SUM(a.LONGSTALKBCH) as LONGSTALK_BUNCHES,
                                SUM(a.RATDMGBCH) as RATDAMAGE_BUNCHES,
                                SUM(a.ABNORMALBCH) as ABNORMAL_BUNCHES
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         GROUP BY a.TRANSDATE 
                         ORDER BY a.TRANSDATE""",
                "parameters": ["start_date", "end_date", "month"]
            },
            "duplicate_analysis": {
                "description": "Find duplicate transactions for verification analysis",
                "sql": """SELECT a.TRANSNO, COUNT(*) as DUPLICATE_COUNT,
                                STRING_AGG(a.RECORDTAG, ',') as RECORD_TAGS
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         GROUP BY a.TRANSNO 
                         HAVING COUNT(*) > 1 
                         ORDER BY DUPLICATE_COUNT DESC""",
                "parameters": ["start_date", "end_date", "month"]
            },
            "kerani_mandor_analysis": {
                "description": "Analysis of Kerani (PM) vs Mandor/Asisten verification",
                "sql": """SELECT a.SCANUSERID, a.RECORDTAG, 
                                COUNT(*) as TRANSACTION_COUNT,
                                SUM(a.RIPEBCH + a.UNRIPEBCH + a.OVERRIPEBCH + a.UNDERRIPEBCH) as TOTAL_BUNCHES
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                           AND a.RECORDTAG IN ('PM', 'MN', 'AS') 
                         GROUP BY a.SCANUSERID, a.RECORDTAG 
                         ORDER BY a.SCANUSERID, a.RECORDTAG""",
                "parameters": ["start_date", "end_date", "month"]
            },
            "monthly_summary": {
                "description": "Monthly summary statistics",
                "sql": """SELECT EXTRACT(YEAR FROM a.TRANSDATE) as YEAR,
                                EXTRACT(MONTH FROM a.TRANSDATE) as MONTH,
                                COUNT(*) as TOTAL_TRANSACTIONS,
                                SUM(a.RIPEBCH + a.UNRIPEBCH + a.OVERRIPEBCH + a.UNDERRIPEBCH) as TOTAL_BUNCHES,
                                SUM(a.LOOSEFRUIT + a.LOOSEFRUIT2) as TOTAL_LOOSEFRUIT,
                                COUNT(DISTINCT a.SCANUSERID) as UNIQUE_SCANNERS
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         GROUP BY EXTRACT(YEAR FROM a.TRANSDATE), EXTRACT(MONTH FROM a.TRANSDATE) 
                         ORDER BY YEAR, MONTH""",
                "parameters": ["start_date", "end_date", "month"]
            },
            "verification_status": {
                "description": "Check verification status using TRANSSTATUS field",
                "sql": """SELECT a.TRANSSTATUS, COUNT(*) as STATUS_COUNT,
                                SUM(a.RIPEBCH + a.UNRIPEBCH + a.OVERRIPEBCH + a.UNDERRIPEBCH) as TOTAL_BUNCHES
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         GROUP BY a.TRANSSTATUS 
                         ORDER BY STATUS_COUNT DESC""",
                "parameters": ["start_date", "end_date", "month"]
            },
            # Additional queries for comprehensive analysis
            "daily_performance": {
                "description": "Daily performance metrics",
                "sql": """SELECT a.TRANSDATE, b.DIVID, c.DIVNAME,
                                COUNT(*) as TRANSACTIONS,
                                SUM(a.RIPEBCH + a.UNRIPEBCH + a.OVERRIPEBCH + a.UNDERRIPEBCH) as BUNCHES
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         GROUP BY a.TRANSDATE, b.DIVID, c.DIVNAME 
                         ORDER BY a.TRANSDATE, b.DIVID""",
                "parameters": ["start_date", "end_date", "month"]
            },
            "processed_daily_data": {
                "description": "Processed daily data with calculations",
                "sql": """SELECT a.TRANSDATE, 
                                COUNT(*) as TOTAL_TRANSACTIONS,
                                SUM(a.RIPEBCH) as RIPE_BUNCHES,
                                SUM(a.UNRIPEBCH + a.OVERRIPEBCH + a.UNDERRIPEBCH) as UNRIPE_BUNCHES,
                                SUM(a.BLACKBCH + a.ROTTENBCH + a.RATDMGBCH + a.ABNORMALBCH) as DEFECT_BUNCHES
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         GROUP BY a.TRANSDATE 
                         ORDER BY a.TRANSDATE""",
                "parameters": ["start_date", "end_date", "month"]
            },
            "employee_performance": {
                "description": "Employee performance analysis",
                "sql": """SELECT a.SCANUSERID, e.\"ID NAME\" as EMPLOYEE_NAME,
                                COUNT(*) as TOTAL_SCANS,
                                SUM(a.RIPEBCH + a.UNRIPEBCH + a.OVERRIPEBCH + a.UNDERRIPEBCH) as TOTAL_BUNCHES,
                                AVG(a.RIPEBCH + a.UNRIPEBCH + a.OVERRIPEBCH + a.UNDERRIPEBCH) as AVG_BUNCHES_PER_SCAN
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         LEFT JOIN EMP e ON a.SCANUSERID = e.\"ID EMPCODE\"
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         GROUP BY a.SCANUSERID, e.\"ID NAME\" 
                         ORDER BY TOTAL_BUNCHES DESC""",
                "parameters": ["start_date", "end_date", "month"]
            },
            "processed_employee_data": {
                "description": "Processed employee data with role analysis",
                "sql": """SELECT a.SCANUSERID, e.\"ID NAME\" as EMPLOYEE_NAME, a.RECORDTAG,
                                COUNT(*) as TRANSACTION_COUNT,
                                SUM(a.RIPEBCH + a.UNRIPEBCH + a.OVERRIPEBCH + a.UNDERRIPEBCH) as TOTAL_BUNCHES
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         LEFT JOIN EMP e ON a.SCANUSERID = e.\"ID EMPCODE\"
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         GROUP BY a.SCANUSERID, e.\"ID NAME\", a.RECORDTAG 
                         ORDER BY a.SCANUSERID, a.RECORDTAG""",
                "parameters": ["start_date", "end_date", "month"]
            },
            "processed_field_data": {
                "description": "Processed field data with division grouping",
                "sql": """SELECT a.FIELDID, b.FIELDNAME, b.DIVID, c.DIVNAME,
                                COUNT(*) as TOTAL_TRANSACTIONS,
                                SUM(a.RIPEBCH + a.UNRIPEBCH + a.OVERRIPEBCH + a.UNDERRIPEBCH) as TOTAL_BUNCHES,
                                SUM(a.RIPEBCH) as RIPE_BUNCHES,
                                SUM(a.UNRIPEBCH + a.OVERRIPEBCH + a.UNDERRIPEBCH) as UNRIPE_BUNCHES
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         GROUP BY a.FIELDID, b.FIELDNAME, b.DIVID, c.DIVNAME 
                         ORDER BY b.DIVID, a.FIELDID""",
                "parameters": ["start_date", "end_date", "month"]
            },
            "verification_data": {
                "description": "Verification data analysis",
                "sql": """SELECT a.RECORDTAG, a.TRANSSTATUS,
                                COUNT(*) as RECORD_COUNT,
                                SUM(a.RIPEBCH + a.UNRIPEBCH + a.OVERRIPEBCH + a.UNDERRIPEBCH) as TOTAL_BUNCHES
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         GROUP BY a.RECORDTAG, a.TRANSSTATUS 
                         ORDER BY a.RECORDTAG, a.TRANSSTATUS""",
                "parameters": ["start_date", "end_date", "month"]
            },
            "ffb_scanner_data": {
                "description": "Complete FFB scanner data for analysis",
                "sql": """SELECT a.*, b.FIELDNAME, b.DIVID, c.DIVNAME, e.\"ID NAME\" as EMPLOYEE_NAME
                         FROM FFBSCANNERDATA{month:02d} a 
                         LEFT JOIN OCFIELD b ON a.FIELDID = b.ID 
                         LEFT JOIN CRDIVISION c ON b.DIVID = c.ID 
                         LEFT JOIN EMP e ON a.SCANUSERID = e.\"ID EMPCODE\"
                         WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE <= '{end_date}' 
                         ORDER BY a.TRANSDATE, a.TRANSTIME""",
                "parameters": ["start_date", "end_date", "month"]
            }
        },
        "processing_rules": {
            "duplicate_handling": {
                "description": "Remove duplicates based on ID field",
                "method": "drop_duplicates",
                "subset": ["ID"]
            },
            "date_filtering": {
                "description": "Filter data within specified date range",
                "field": "TRANSDATE",
                "format": "YYYY-MM-DD"
            },
            "verification_logic": {
                "description": "Special logic for Estate 1A May 2025 - use TRANSSTATUS 704 filter",
                "condition": "estate == 'PGE 1A' and month == 5 and year == 2025",
                "filter": "TRANSSTATUS = '704'"
            }
        },
        "output_format": {
            "employee_details": {
                "structure": {
                    "name": "Employee name from mapping",
                    "kerani": "Count of PM records created",
                    "kerani_verified": "Count of verified PM records",
                    "kerani_differences": "Count of input differences",
                    "mandor": "Count of MN records",
                    "asisten": "Count of AS records"
                }
            },
            "division_summary": {
                "structure": {
                    "division_id": "Division ID",
                    "division_name": "Division name",
                    "total_transactions": "Total transaction count",
                    "total_bunches": "Sum of all bunch types",
                    "total_loosefruit": "Sum of loose fruit"
                }
            }
        }
    }
    
    return corrected_template

def main():
    """Main function to fix query structure"""
    print("Fixing Query Structure...")
    print("=" * 50)
    
    # Create backup of current file
    original_file = "pge2b_corrected_formula.json"
    backup_file = f"pge2b_corrected_formula_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        shutil.copy2(original_file, backup_file)
        print(f"✓ Created backup: {backup_file}")
    except Exception as e:
        print(f"⚠ Warning: Could not create backup: {e}")
    
    # Generate corrected template
    corrected_template = create_corrected_queries()
    
    # Save corrected template
    try:
        with open(original_file, 'w', encoding='utf-8') as f:
            json.dump(corrected_template, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Fixed query structure in {original_file}")
        print(f"✓ Total queries: {len(corrected_template['queries'])}")
        
        # List all queries
        print("\nCorrected Queries:")
        for i, (query_name, query_info) in enumerate(corrected_template['queries'].items(), 1):
            print(f"  {i:2d}. {query_name}: {query_info['description']}")
        
        print("\nKey Fixes Applied:")
        print("  • Restored proper JOIN syntax (LEFT JOIN ... ON ...)")
        print("  • Added OCFIELD table joins for field name mapping")
        print("  • Added CRDIVISION table joins for division info")
        print("  • Added EMP table joins for employee names")
        print("  • Fixed malformed WHERE clauses")
        print("  • Ensured proper SQL formatting")
        
    except Exception as e:
        print(f"✗ Error saving corrected template: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("Query structure fix completed successfully!")
    return True

if __name__ == "__main__":
    main()