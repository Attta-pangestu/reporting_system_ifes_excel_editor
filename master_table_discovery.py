#!/usr/bin/env python3
"""
Master Table Discovery Script
Discovers master tables for estate, division, employee, and role data
"""

import os
import sys
from datetime import datetime
from firebird_connector import FirebirdConnector

def discover_master_tables():
    """Discover master tables for estate, division, employee, and role data"""
    
    # Database configuration
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    
    # Initialize connector
    connector = FirebirdConnector(db_path, username='SYSDBA', password='masterkey')
    
    print("=" * 60)
    print("MASTER TABLE DISCOVERY")
    print("=" * 60)
    print(f"Database: {db_path}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Queries to discover master tables
    discovery_queries = {
        "ESTATE_TABLES": "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%ESTATE%'",
        "DIVISION_TABLES": "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%DIVISION%'",
        "EMPLOYEE_TABLES": "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%EMPLOYEE%'",
        "LABOUR_TABLES": "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%LABOUR%'",
        "WORKER_TABLES": "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%WORKER%'",
        "ROLE_TABLES": "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%ROLE%'",
        "MASTER_TABLES": "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%MASTER%'",
        "ALL_TABLES": "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS ORDER BY RDB$RELATION_NAME"
    }
    
    results = {}
    
    # Execute discovery queries
    for category, query in discovery_queries.items():
        print(f"Discovering {category}...")
        result = connector.execute_query(query)
        results[category] = result
        print(f"✓ {category} discovery completed")
        print()
    
    # Analyze transaction status codes
    print("Analyzing transaction status codes...")
    trans_status_query = "SELECT TRANSSTATUS, COUNT(*) FROM FFBSCANNERDATA10 GROUP BY TRANSSTATUS ORDER BY TRANSSTATUS"
    trans_status_result = connector.execute_query(trans_status_query)
    results["TRANSACTION_STATUS"] = trans_status_result
    print("✓ Transaction status analysis completed")
    print()
    
    # Analyze date ranges
    print("Analyzing date ranges...")
    date_range_query = "SELECT MIN(TRANSDATE), MAX(TRANSDATE), COUNT(*) FROM FFBSCANNERDATA10"
    date_range_result = connector.execute_query(date_range_query)
    results["DATE_RANGE"] = date_range_result
    print("✓ Date range analysis completed")
    print()
    
    # Sample data from key tables
    print("Getting sample data from key tables...")
    sample_queries = {
        "FFBSCANNERDATA10_SAMPLE": "SELECT FIRST 5 * FROM FFBSCANNERDATA10",
        "WORKERINFO_SAMPLE": "SELECT FIRST 5 * FROM WORKERINFO"
    }
    
    for sample_name, query in sample_queries.items():
        result = connector.execute_query(query)
        results[sample_name] = result
        print(f"✓ {sample_name} completed")
    
    print()
    
    # Save results to file
    output_file = "master_table_discovery_results.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("MASTER TABLE DISCOVERY RESULTS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Database: {db_path}\n\n")
        
        for category, result in results.items():
            f.write(f"\n{category}\n")
            f.write("-" * 40 + "\n")
            f.write(str(result))
            f.write("\n" + "=" * 60 + "\n")
    
    print(f"✓ Results saved to: {output_file}")
    
    # Generate recommendations
    print("\nGENERATING RECOMMENDATIONS...")
    print("=" * 60)
    
    recommendations = []
    
    # Check if we found relevant tables
    if "ESTATE" in str(results.get("ESTATE_TABLES", "")):
        recommendations.append("✓ Estate tables found - use for ESTATE field mapping")
    else:
        recommendations.append("⚠ No estate tables found - may need to extract from transaction data")
    
    if "DIVISION" in str(results.get("DIVISION_TABLES", "")):
        recommendations.append("✓ Division tables found - use for DIVISI field mapping")
    else:
        recommendations.append("⚠ No division tables found - may need to extract from transaction data")
    
    if "WORKER" in str(results.get("WORKER_TABLES", "")) or "EMPLOYEE" in str(results.get("EMPLOYEE_TABLES", "")):
        recommendations.append("✓ Worker/Employee tables found - use for KARYAWAN field mapping")
    else:
        recommendations.append("⚠ No worker/employee tables found - use WORKERINFO table")
    
    recommendations.append("📊 Use TRANSSTATUS analysis for verification percentage calculation")
    recommendations.append("📅 Use date range analysis for PERIODE LAPORAN field")
    recommendations.append("🔍 Next step: Analyze discovered tables structure")
    
    for rec in recommendations:
        print(rec)
    
    print("\n" + "=" * 60)
    print("MASTER TABLE DISCOVERY COMPLETED")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    try:
        results = discover_master_tables()
        print("\n✅ Master table discovery completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during master table discovery: {str(e)}")
        sys.exit(1)