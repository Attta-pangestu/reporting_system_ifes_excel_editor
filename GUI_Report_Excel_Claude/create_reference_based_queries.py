#!/usr/bin/env python3
"""
Create Reference-Based Query Templates
Based on gui_multi_estate_ffb_analysis.py structure
"""

import json
import os
from datetime import datetime

def create_reference_based_queries():
    """Create query templates based on the reference structure"""
    
    # Based on the reference file analysis, here are the proper query structures
    queries = {
        "employee_mapping": {
            "description": "Get employee ID to name mapping from EMP table",
            "query": "SELECT ID, NAME FROM EMP",
            "parameters": [],
            "expected_columns": ["ID", "NAME"]
        },
        
        "raw_ffb_data": {
            "description": "Get raw FFB scanner data with field information",
            "query": """
            SELECT a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
                   a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
                   a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
                   a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
                   a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2,
                   b.DIVID, b.FIELDNAME
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["ID", "SCANUSERID", "FIELDID", "RIPEBCH", "UNRIPEBCH", "TRANSDATE"]
        },
        
        "division_list": {
            "description": "Get list of divisions with names",
            "query": """
            SELECT DISTINCT b.DIVID, c.DIVNAME
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
            WHERE b.DIVID IS NOT NULL AND c.DIVNAME IS NOT NULL
                AND a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["DIVID", "DIVNAME"]
        },
        
        "division_data": {
            "description": "Get division-specific FFB data",
            "query": """
            SELECT a.ID, a.SCANUSERID, a.FIELDID, a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, 
                   a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH, a.LOOSEFRUIT, a.TRANSDATE,
                   a.RECORDTAG, a.TRANSSTATUS, b.DIVID, c.DIVNAME
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
            WHERE b.DIVID = '{division_id}'
                AND a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            """,
            "parameters": ["start_date", "end_date", "month", "division_id"],
            "expected_columns": ["ID", "SCANUSERID", "FIELDID", "RIPEBCH", "TRANSDATE"]
        },
        
        "daily_summary": {
            "description": "Get daily summary of FFB transactions",
            "query": """
            SELECT a.TRANSDATE, 
                   COUNT(*) as TOTAL_TRANSACTIONS,
                   SUM(a.RIPEBCH) as TOTAL_RIPE,
                   SUM(a.UNRIPEBCH) as TOTAL_UNRIPE,
                   SUM(a.BLACKBCH) as TOTAL_BLACK,
                   SUM(a.ROTTENBCH) as TOTAL_ROTTEN,
                   SUM(a.RATDMGBCH) as TOTAL_RATDAMAGE,
                   COUNT(DISTINCT a.SCANUSERID) as UNIQUE_SCANNERS
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            GROUP BY a.TRANSDATE
            ORDER BY a.TRANSDATE
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["TRANSDATE", "TOTAL_TRANSACTIONS", "TOTAL_RIPE"]
        },
        
        "scanner_performance": {
            "description": "Get scanner performance metrics",
            "query": """
            SELECT a.SCANUSERID, 
                   COUNT(*) as TOTAL_SCANS,
                   SUM(a.RIPEBCH) as TOTAL_RIPE,
                   SUM(a.UNRIPEBCH) as TOTAL_UNRIPE,
                   AVG(a.RIPEBCH) as AVG_RIPE_PER_SCAN,
                   e.NAME as SCANNER_NAME
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN EMP e ON a.SCANUSERID = e.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            GROUP BY a.SCANUSERID, e.NAME
            ORDER BY TOTAL_SCANS DESC
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["SCANUSERID", "TOTAL_SCANS", "TOTAL_RIPE", "SCANNER_NAME"]
        },
        
        "field_performance": {
            "description": "Get field performance metrics",
            "query": """
            SELECT a.FIELDID, b.FIELDNAME, b.DIVID, c.DIVNAME,
                   COUNT(*) as TOTAL_TRANSACTIONS,
                   SUM(a.RIPEBCH) as TOTAL_RIPE,
                   SUM(a.UNRIPEBCH) as TOTAL_UNRIPE,
                   AVG(a.RIPEBCH) as AVG_RIPE_PER_TRANSACTION
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            GROUP BY a.FIELDID, b.FIELDNAME, b.DIVID, c.DIVNAME
            ORDER BY TOTAL_RIPE DESC
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["FIELDID", "FIELDNAME", "TOTAL_TRANSACTIONS", "TOTAL_RIPE"]
        },
        
        "quality_analysis": {
            "description": "Analyze fruit quality metrics",
            "query": """
            SELECT 
                SUM(a.RIPEBCH) as TOTAL_RIPE,
                SUM(a.UNRIPEBCH) as TOTAL_UNRIPE,
                SUM(a.BLACKBCH) as TOTAL_BLACK,
                SUM(a.ROTTENBCH) as TOTAL_ROTTEN,
                SUM(a.RATDMGBCH) as TOTAL_RATDAMAGE,
                SUM(a.OVERRIPEBCH) as TOTAL_OVERRIPE,
                SUM(a.UNDERRIPEBCH) as TOTAL_UNDERRIPE,
                SUM(a.ABNORMALBCH) as TOTAL_ABNORMAL,
                COUNT(*) as TOTAL_TRANSACTIONS
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["TOTAL_RIPE", "TOTAL_UNRIPE", "TOTAL_BLACK", "TOTAL_TRANSACTIONS"]
        },
        
        "duplicate_analysis": {
            "description": "Analyze duplicate transactions",
            "query": """
            SELECT a.TRANSNO, COUNT(*) as DUPLICATE_COUNT,
                   STRING_AGG(a.RECORDTAG, ',') as RECORD_TAGS
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            GROUP BY a.TRANSNO
            HAVING COUNT(*) > 1
            ORDER BY DUPLICATE_COUNT DESC
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["TRANSNO", "DUPLICATE_COUNT", "RECORD_TAGS"]
        },
        
        "kerani_mandor_analysis": {
            "description": "Analyze Kerani and Mandor performance",
            "query": """
            SELECT a.RECORDTAG, a.SCANUSERID, e.NAME,
                   COUNT(*) as TOTAL_RECORDS,
                   SUM(a.RIPEBCH) as TOTAL_RIPE,
                   AVG(a.RIPEBCH) as AVG_RIPE
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN EMP e ON a.SCANUSERID = e.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
                AND a.RECORDTAG IN ('PM', 'P1', 'P5')
            GROUP BY a.RECORDTAG, a.SCANUSERID, e.NAME
            ORDER BY a.RECORDTAG, TOTAL_RECORDS DESC
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["RECORDTAG", "SCANUSERID", "NAME", "TOTAL_RECORDS"]
        },
        
        "monthly_summary": {
            "description": "Get monthly summary statistics",
            "query": """
            SELECT 
                COUNT(*) as TOTAL_TRANSACTIONS,
                COUNT(DISTINCT a.SCANUSERID) as UNIQUE_SCANNERS,
                COUNT(DISTINCT a.FIELDID) as UNIQUE_FIELDS,
                SUM(a.RIPEBCH) as TOTAL_RIPE,
                SUM(a.UNRIPEBCH) as TOTAL_UNRIPE,
                AVG(a.RIPEBCH) as AVG_RIPE_PER_TRANSACTION,
                MIN(a.TRANSDATE) as FIRST_DATE,
                MAX(a.TRANSDATE) as LAST_DATE
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["TOTAL_TRANSACTIONS", "UNIQUE_SCANNERS", "TOTAL_RIPE"]
        },
        
        "verification_status": {
            "description": "Check verification status of transactions",
            "query": """
            SELECT a.TRANSSTATUS, COUNT(*) as STATUS_COUNT,
                   SUM(a.RIPEBCH) as TOTAL_RIPE
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            GROUP BY a.TRANSSTATUS
            ORDER BY STATUS_COUNT DESC
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["TRANSSTATUS", "STATUS_COUNT", "TOTAL_RIPE"]
        },
        
        "daily_performance": {
            "description": "Daily performance breakdown",
            "query": """
            SELECT a.TRANSDATE, a.RECORDTAG,
                   COUNT(*) as DAILY_COUNT,
                   SUM(a.RIPEBCH) as DAILY_RIPE,
                   COUNT(DISTINCT a.SCANUSERID) as DAILY_SCANNERS
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            GROUP BY a.TRANSDATE, a.RECORDTAG
            ORDER BY a.TRANSDATE, a.RECORDTAG
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["TRANSDATE", "RECORDTAG", "DAILY_COUNT", "DAILY_RIPE"]
        },
        
        "processed_daily_data": {
            "description": "Processed daily data with calculations",
            "query": """
            SELECT a.TRANSDATE,
                   SUM(a.RIPEBCH + a.UNRIPEBCH + a.BLACKBCH + a.ROTTENBCH) as TOTAL_BUNCHES,
                   SUM(a.RIPEBCH) as RIPE_BUNCHES,
                   CASE 
                       WHEN SUM(a.RIPEBCH + a.UNRIPEBCH + a.BLACKBCH + a.ROTTENBCH) > 0 
                       THEN (SUM(a.RIPEBCH) * 100.0 / SUM(a.RIPEBCH + a.UNRIPEBCH + a.BLACKBCH + a.ROTTENBCH))
                       ELSE 0 
                   END as QUALITY_PERCENTAGE
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            GROUP BY a.TRANSDATE
            ORDER BY a.TRANSDATE
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["TRANSDATE", "TOTAL_BUNCHES", "RIPE_BUNCHES", "QUALITY_PERCENTAGE"]
        },
        
        "employee_performance": {
            "description": "Employee performance metrics",
            "query": """
            SELECT a.SCANUSERID, e.NAME, a.RECORDTAG,
                   COUNT(*) as PERFORMANCE_COUNT,
                   SUM(a.RIPEBCH) as PERFORMANCE_RIPE,
                   AVG(a.RIPEBCH) as AVG_PERFORMANCE
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN EMP e ON a.SCANUSERID = e.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            GROUP BY a.SCANUSERID, e.NAME, a.RECORDTAG
            ORDER BY PERFORMANCE_COUNT DESC
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["SCANUSERID", "NAME", "RECORDTAG", "PERFORMANCE_COUNT"]
        },
        
        "processed_employee_data": {
            "description": "Processed employee data with metrics",
            "query": """
            SELECT e.ID, e.NAME,
                   COUNT(a.ID) as TOTAL_TRANSACTIONS,
                   SUM(a.RIPEBCH) as TOTAL_RIPE_PROCESSED,
                   AVG(a.RIPEBCH) as AVG_RIPE_PROCESSED
            FROM EMP e
            LEFT JOIN FFBSCANNERDATA{month:02d} a ON e.ID = a.SCANUSERID
            LEFT JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            GROUP BY e.ID, e.NAME
            HAVING COUNT(a.ID) > 0
            ORDER BY TOTAL_TRANSACTIONS DESC
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["ID", "NAME", "TOTAL_TRANSACTIONS", "TOTAL_RIPE_PROCESSED"]
        },
        
        "processed_field_data": {
            "description": "Processed field data with metrics",
            "query": """
            SELECT b.ID, b.FIELDNAME, b.DIVID, c.DIVNAME,
                   COUNT(a.ID) as FIELD_TRANSACTIONS,
                   SUM(a.RIPEBCH) as FIELD_RIPE_TOTAL,
                   AVG(a.RIPEBCH) as FIELD_AVG_RIPE
            FROM OCFIELD b
            LEFT JOIN FFBSCANNERDATA{month:02d} a ON b.ID = a.FIELDID
            LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            GROUP BY b.ID, b.FIELDNAME, b.DIVID, c.DIVNAME
            HAVING COUNT(a.ID) > 0
            ORDER BY FIELD_TRANSACTIONS DESC
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["ID", "FIELDNAME", "FIELD_TRANSACTIONS", "FIELD_RIPE_TOTAL"]
        },
        
        "verification_data": {
            "description": "Verification data analysis",
            "query": """
            SELECT a.TRANSNO, a.RECORDTAG, a.TRANSSTATUS,
                   COUNT(*) as VERIFICATION_COUNT,
                   SUM(a.RIPEBCH) as VERIFICATION_RIPE
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
                AND a.TRANSSTATUS IN ('704', '731', '732')
            GROUP BY a.TRANSNO, a.RECORDTAG, a.TRANSSTATUS
            ORDER BY VERIFICATION_COUNT DESC
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["TRANSNO", "RECORDTAG", "TRANSSTATUS", "VERIFICATION_COUNT"]
        },
        
        "ffb_scanner_data": {
            "description": "Raw FFB scanner data for analysis",
            "query": """
            SELECT a.ID, a.SCANUSERID, a.FIELDID, a.TRANSNO, a.TRANSDATE,
                   a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH,
                   a.RECORDTAG, a.TRANSSTATUS, b.FIELDNAME, c.DIVNAME
            FROM FFBSCANNERDATA{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            ORDER BY a.TRANSDATE, a.TRANSNO
            """,
            "parameters": ["start_date", "end_date", "month"],
            "expected_columns": ["ID", "SCANUSERID", "FIELDID", "TRANSDATE", "RIPEBCH"]
        }
    }
    
    return queries

def main():
    print("Creating reference-based query templates...")
    
    # Create the new queries
    queries = create_reference_based_queries()
    
    # Save to file
    output_file = "pge2b_reference_based_formula.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(queries, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created {len(queries)} reference-based queries")
    print(f"📁 Saved to: {output_file}")
    
    # Print summary
    print("\n📊 Query Summary:")
    for query_name, query_info in queries.items():
        params = len(query_info.get('parameters', []))
        print(f"  - {query_name}: {params} parameters")
    
    print(f"\n🔧 Key improvements:")
    print("  - Proper JOIN syntax: JOIN OCFIELD b ON a.FIELDID = b.ID")
    print("  - LEFT JOIN for optional tables: LEFT JOIN CRDIVISION c ON b.DIVID = c.ID")
    print("  - Consistent parameter naming and structure")
    print("  - Based on working reference from gui_multi_estate_ffb_analysis.py")

if __name__ == "__main__":
    main()