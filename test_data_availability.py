#!/usr/bin/env python3
"""
Test Data Availability Script
Check what data is actually available in the database
"""

import sys
import os
from firebird_connector import FirebirdConnector

def test_data_availability():
    """Test what data is available in the database"""
    
    # Database configuration
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        print("Initializing database connection...")
        connector = FirebirdConnector(db_path)
        
        # Check total records in FFBSCANNERDATA10
        print("\n1. Checking total records in FFBSCANNERDATA10...")
        total_query = "SELECT COUNT(*) as TOTAL_RECORDS FROM FFBSCANNERDATA10"
        total_result = connector.execute_query(total_query)
        if total_result:
            print(f"   Total records: {total_result[0].get('TOTAL_RECORDS', 0)}")
        
        # Check date range
        print("\n2. Checking date range...")
        date_query = """
        SELECT 
            MIN(TRANSDATE) as MIN_DATE,
            MAX(TRANSDATE) as MAX_DATE,
            COUNT(DISTINCT TRANSDATE) as UNIQUE_DAYS
        FROM FFBSCANNERDATA10
        """
        date_result = connector.execute_query(date_query)
        if date_result and date_result[0]:
            result = date_result[0]
            print(f"   Min Date: {result.get('MIN_DATE', 'N/A')}")
            print(f"   Max Date: {result.get('MAX_DATE', 'N/A')}")
            print(f"   Unique Days: {result.get('UNIQUE_DAYS', 'N/A')}")
        
        # Check recent data (last 30 days from max date)
        print("\n3. Checking recent data availability...")
        recent_query = """
        SELECT 
            TRANSDATE,
            COUNT(*) as DAILY_COUNT
        FROM FFBSCANNERDATA10
        WHERE TRANSDATE >= (SELECT MAX(TRANSDATE) - 30 FROM FFBSCANNERDATA10)
        GROUP BY TRANSDATE
        ORDER BY TRANSDATE DESC
        """
        recent_result = connector.execute_query(recent_query)
        if recent_result:
            print(f"   Found {len(recent_result)} days with data in recent period:")
            for i, row in enumerate(recent_result[:10]):  # Show first 10 days
                print(f"     {row.get('TRANSDATE', 'N/A')}: {row.get('DAILY_COUNT', 0)} transactions")
            if len(recent_result) > 10:
                print(f"     ... and {len(recent_result) - 10} more days")
        
        # Check worker data availability
        print("\n4. Checking worker data...")
        worker_query = """
        SELECT 
            COUNT(DISTINCT f.WORKERID) as UNIQUE_WORKERS,
            COUNT(DISTINCT w.EMPID) as WORKERS_WITH_INFO,
            COUNT(DISTINCT e.ID) as WORKERS_WITH_EMP_DATA
        FROM FFBSCANNERDATA10 f
        LEFT JOIN WORKERINFO w ON f.WORKERID = w.EMPID
        LEFT JOIN EMP e ON w.EMPID = e.ID
        """
        worker_result = connector.execute_query(worker_query)
        if worker_result and worker_result[0]:
            result = worker_result[0]
            print(f"   Unique Workers in transactions: {result.get('UNIQUE_WORKERS', 0)}")
            print(f"   Workers with WORKERINFO: {result.get('WORKERS_WITH_INFO', 0)}")
            print(f"   Workers with EMP data: {result.get('WORKERS_WITH_EMP_DATA', 0)}")
        
        # Check division data
        print("\n5. Checking division data...")
        division_query = """
        SELECT 
            COUNT(DISTINCT w.FIELDDIVID) as UNIQUE_DIVISIONS,
            COUNT(DISTINCT d.ID) as DIVISIONS_WITH_DATA
        FROM WORKERINFO w
        LEFT JOIN CRDIVISION d ON w.FIELDDIVID = d.ID
        WHERE w.FIELDDIVID IS NOT NULL
        """
        division_result = connector.execute_query(division_query)
        if division_result and division_result[0]:
            result = division_result[0]
            print(f"   Unique Field Divisions: {result.get('UNIQUE_DIVISIONS', 0)}")
            print(f"   Divisions with master data: {result.get('DIVISIONS_WITH_DATA', 0)}")
        
        # Sample transaction data
        print("\n6. Sample transaction data...")
        sample_query = """
        SELECT FIRST 5
            f.ID,
            f.WORKERID,
            f.TRANSDATE,
            f.TRANSSTATUS,
            w.EMPID,
            e.EMPCODE,
            e.NAME
        FROM FFBSCANNERDATA10 f
        LEFT JOIN WORKERINFO w ON f.WORKERID = w.EMPID
        LEFT JOIN EMP e ON w.EMPID = e.ID
        ORDER BY f.TRANSDATE DESC
        """
        sample_result = connector.execute_query(sample_query)
        if sample_result:
            print("   Recent transactions:")
            for row in sample_result:
                print(f"     ID: {row.get('ID', 'N/A')}, Worker: {row.get('WORKERID', 'N/A')}, "
                      f"Date: {row.get('TRANSDATE', 'N/A')}, Status: {row.get('TRANSSTATUS', 'N/A')}, "
                      f"Name: {row.get('NAME', 'N/A')}")
        
        print("\n" + "="*60)
        print("DATA AVAILABILITY CHECK COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error checking data availability: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_availability()