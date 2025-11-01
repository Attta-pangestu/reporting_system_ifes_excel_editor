"""
Create Reference-Based Queries for FFBLOADINGCROP Tables
This script generates queries that work with the sample data in FFBLOADINGCROP tables
"""

import json

def create_ffbloadingcrop_queries():
    """Create queries that use FFBLOADINGCROP tables instead of FFBSCANNERDATA"""
    
    queries = {
        "employee_mapping": {
            "description": "Get employee ID to name mapping",
            "parameters": [],
            "query": """
            SELECT ID, NAME
            FROM EMP
            WHERE ID IS NOT NULL AND NAME IS NOT NULL
            """
        },
        
        "raw_ffb_data": {
            "description": "Get raw FFB loading data with field information",
            "parameters": ["month", "start_date", "end_date"],
            "query": """
            SELECT a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
                   a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
                   a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
                   a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
                   a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2,
                   b.DIVID, b.FIELDNAME
            FROM FFBLOADINGCROP{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            """
        },
        
        "divisions_list": {
            "description": "Get list of divisions with data",
            "parameters": ["month", "start_date", "end_date"],
            "query": """
            SELECT DISTINCT b.DIVID, c.DIVNAME
            FROM FFBLOADINGCROP{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
            WHERE b.DIVID IS NOT NULL AND c.DIVNAME IS NOT NULL
                AND a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            """
        },
        
        "division_data": {
            "description": "Get FFB data for specific division",
            "parameters": ["month", "division_id", "start_date", "end_date"],
            "query": """
            SELECT a.ID, a.SCANUSERID, a.FIELDID, a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, 
                   a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH, a.LOOSEFRUIT, a.TRANSDATE,
                   a.RECORDTAG, a.TRANSSTATUS, b.DIVID, c.DIVNAME
            FROM FFBLOADINGCROP{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
            WHERE b.DIVID = '{division_id}'
                AND a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            """
        },
        
        "daily_summary": {
            "description": "Daily summary of FFB transactions",
            "parameters": ["month", "start_date", "end_date"],
            "query": """
            SELECT a.TRANSDATE, 
                   COUNT(*) as TOTAL_TRANSACTIONS,
                   SUM(a.RIPEBCH) as TOTAL_RIPE,
                   SUM(a.UNRIPEBCH) as TOTAL_UNRIPE,
                   SUM(a.BLACKBCH) as TOTAL_BLACK,
                   SUM(a.ROTTENBCH) as TOTAL_ROTTEN,
                   SUM(a.RATDMGBCH) as TOTAL_RATDAMAGE,
                   COUNT(DISTINCT a.SCANUSERID) as UNIQUE_SCANNERS
            FROM FFBLOADINGCROP{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            GROUP BY a.TRANSDATE
            ORDER BY a.TRANSDATE
            """
        },
        
        "scanner_performance": {
            "description": "Scanner performance analysis",
            "parameters": ["month", "start_date", "end_date"],
            "query": """
            SELECT a.SCANUSERID, 
                   COUNT(*) as TOTAL_SCANS,
                   SUM(a.RIPEBCH) as TOTAL_RIPE,
                   SUM(a.UNRIPEBCH) as TOTAL_UNRIPE,
                   AVG(a.RIPEBCH) as AVG_RIPE_PER_SCAN,
                   e.NAME as SCANNER_NAME
            FROM FFBLOADINGCROP{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN EMP e ON a.SCANUSERID = e.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            GROUP BY a.SCANUSERID, e.NAME
            ORDER BY TOTAL_SCANS DESC
            """
        },
        
        "field_analysis": {
            "description": "Field-wise analysis",
            "parameters": ["month", "start_date", "end_date"],
            "query": """
            SELECT a.FIELDID, b.FIELDNAME, b.DIVID, c.DIVNAME,
                   COUNT(*) as TOTAL_TRANSACTIONS,
                   SUM(a.RIPEBCH) as TOTAL_RIPE,
                   SUM(a.UNRIPEBCH) as TOTAL_UNRIPE,
                   AVG(a.RIPEBCH) as AVG_RIPE_PER_TRANSACTION
            FROM FFBLOADINGCROP{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            GROUP BY a.FIELDID, b.FIELDNAME, b.DIVID, c.DIVNAME
            ORDER BY TOTAL_RIPE DESC
            """
        },
        
        "quality_summary": {
            "description": "Overall quality summary",
            "parameters": ["month", "start_date", "end_date"],
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
            FROM FFBLOADINGCROP{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            """
        },
        
        "duplicate_transactions": {
            "description": "Find duplicate transactions",
            "parameters": ["month", "start_date", "end_date"],
            "query": """
            SELECT a.TRANSNO, COUNT(*) as DUPLICATE_COUNT,
                   GROUP_CONCAT(a.RECORDTAG) as RECORD_TAGS
            FROM FFBLOADINGCROP{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
            GROUP BY a.TRANSNO
            HAVING COUNT(*) > 1
            ORDER BY DUPLICATE_COUNT DESC
            """
        },
        
        "record_tag_analysis": {
            "description": "Analysis by record tag (PM, P1, P5)",
            "parameters": ["month", "start_date", "end_date"],
            "query": """
            SELECT a.RECORDTAG, a.SCANUSERID, e.NAME,
                   COUNT(*) as TOTAL_RECORDS,
                   SUM(a.RIPEBCH) as TOTAL_RIPE,
                   AVG(a.RIPEBCH) as AVG_RIPE
            FROM FFBLOADINGCROP{month:02d} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN EMP e ON a.SCANUSERID = e.ID
            WHERE a.TRANSDATE >= '{start_date}' 
                AND a.TRANSDATE <= '{end_date}'
                AND a.RECORDTAG IN ('PM', 'P1', 'P5')
            GROUP BY a.RECORDTAG, a.SCANUSERID, e.NAME
            ORDER BY a.RECORDTAG, TOTAL_RECORDS DESC
            """
        }
    }
    
    # Save to JSON file
    output_file = "pge2b_ffbloadingcrop_formula.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(queries, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Created {len(queries)} FFBLOADINGCROP-based queries")
    print(f"📁 Saved to: {output_file}")
    
    return queries

if __name__ == "__main__":
    create_ffbloadingcrop_queries()