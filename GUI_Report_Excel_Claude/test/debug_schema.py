#!/usr/bin/env python3
"""
Database Schema Debug Script
Investigates database structure to fix problematic queries
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from firebird_connector_enhanced import FirebirdConnectorEnhanced
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

class DatabaseSchemaDebugger:
    def __init__(self):
        self.db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
        self.connector = None
        self.debug_results = {}

    def connect(self):
        """Connect to database"""
        try:
            self.connector = FirebirdConnectorEnhanced(self.db_path)
            if self.connector.test_connection():
                print("✅ Database connection successful")
                return True
            else:
                print("❌ Database connection failed")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def execute_query(self, sql, description):
        """Execute query and return results"""
        print(f"\n🔍 {description}")
        print(f"SQL: {sql}")

        try:
            result = self.connector.execute_query(sql)
            if result and len(result) > 0:
                print(f"✅ Found {len(result)} rows")
                for i, row in enumerate(result[:3]):  # Show first 3 rows
                    print(f"   Row {i+1}: {row}")
                if len(result) > 3:
                    print(f"   ... and {len(result) - 3} more rows")
                return result
            else:
                print("❌ No results found")
                return []
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return []

    def debug_employee_schema(self):
        """Debug employee-related queries"""
        print("\n" + "="*60)
        print("DEBUGGING EMPLOYEE SCHEMA")
        print("="*60)

        # Check if EMPLOYEE table exists
        self.execute_query(
            "SELECT * FROM EMPLOYEE LIMIT 5",
            "Check EMPLOYEE table structure"
        )

        # Check if EMP table exists (backup)
        self.execute_query(
            "SELECT * FROM EMP LIMIT 5",
            "Check EMP table structure (backup)"
        )

        # Get all employee-related tables
        self.execute_query(
            "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%EMP%'",
            "Find all employee-related tables"
        )

        # Check SCANUSERID values in transactions
        self.execute_query(
            "SELECT DISTINCT SCANUSERID FROM FFBSCANNERDATA02 WHERE SCANUSERID IS NOT NULL LIMIT 10",
            "Check SCANUSERID values in FFB data"
        )

        # Try to find employee name patterns
        self.execute_query(
            "SELECT COUNT(*) as count, SCANUSERID FROM FFBSCANNERDATA02 WHERE SCANUSERID IS NOT NULL GROUP BY SCANUSERID ORDER BY count DESC LIMIT 10",
            "Most active SCANUSERID values"
        )

        # Test join with EMPLOYEE
        self.execute_query(
            "SELECT COUNT(*) as count FROM FFBSCANNERDATA02 a LEFT JOIN EMPLOYEE e ON a.SCANUSERID = e.EMPID WHERE a.TRANSDATE >= '2025-02-01' AND a.TRANSDATE <= '2025-02-28'",
            "Test join with EMPLOYEE table"
        )

        # Test join with EMP
        self.execute_query(
            "SELECT COUNT(*) as count FROM FFBSCANNERDATA02 a LEFT JOIN EMP e ON a.SCANUSERID = e.ID WHERE a.TRANSDATE >= '2025-02-01' AND a.TRANSDATE <= '2025-02-28'",
            "Test join with EMP table"
        )

    def debug_division_schema(self):
        """Debug division-related queries"""
        print("\n" + "="*60)
        print("DEBUGGING DIVISION SCHEMA")
        print("="*60)

        # Check CRDIVISION table
        self.execute_query(
            "SELECT * FROM CRDIVISION LIMIT 5",
            "Check CRDIVISION table structure"
        )

        # Check OCFIELD table (backup)
        self.execute_query(
            "SELECT * FROM OCFIELD LIMIT 5",
            "Check OCFIELD table structure (backup)"
        )

        # Find all field/division related tables
        self.execute_query(
            "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%DIV%' OR RDB$RELATION_NAME LIKE '%FIELD%'",
            "Find all division/field-related tables"
        )

        # Check DIVID values in transactions
        self.execute_query(
            "SELECT DISTINCT DIVID FROM FFBSCANNERDATA02 WHERE DIVID IS NOT NULL LIMIT 10",
            "Check DIVID values in FFB data"
        )

        # Check FIELDID values (backup)
        self.execute_query(
            "SELECT DISTINCT FIELDID FROM FFBSCANNERDATA02 WHERE FIELDID IS NOT NULL LIMIT 10",
            "Check FIELDID values in FFB data (backup)"
        )

        # Test join with CRDIVISION
        self.execute_query(
            "SELECT COUNT(*) as count FROM FFBSCANNERDATA02 a LEFT JOIN CRDIVISION c ON a.DIVID = c.ID WHERE a.DIVID IS NOT NULL",
            "Test join with CRDIVISION table"
        )

        # Test join with OCFIELD
        self.execute_query(
            "SELECT COUNT(*) as count FROM FFBSCANNERDATA02 a LEFT JOIN OCFIELD b ON a.FIELDID = b.ID WHERE a.FIELDID IS NOT NULL",
            "Test join with OCFIELD table"
        )

    def debug_quality_query(self):
        """Debug quality analysis query"""
        print("\n" + "="*60)
        print("DEBUGGING QUALITY ANALYSIS")
        print("="*60)

        # Test basic quality data
        self.execute_query(
            "SELECT TRANSDATE, SUM(RIPEBCH) as ripe, SUM(BLACKBCH) as black, SUM(ROTTENBCH) as rotten FROM FFBSCANNERDATA02 WHERE TRANSDATE >= '2025-02-01' AND TRANSDATE <= '2025-02-28' AND RIPEBCH > 0 GROUP BY TRANSDATE ORDER BY TRANSDATE LIMIT 5",
            "Test basic quality data aggregation"
        )

        # Test calculation
        self.execute_query(
            "SELECT TRANSDATE, SUM(RIPEBCH) as ripe, SUM(BLACKBCH) as black, SUM(ROTTENBCH) as rotten, ((SUM(BLACKBCH) + SUM(ROTTENBCH)) * 100.0 / NULLIF(SUM(RIPEBCH), 0)) as defect_pct FROM FFBSCANNERDATA02 WHERE TRANSDATE >= '2025-02-01' AND TRANSDATE <= '2025-02-28' AND RIPEBCH > 0 GROUP BY TRANSDATE ORDER BY TRANSDATE LIMIT 5",
            "Test defect percentage calculation"
        )

        # Check for NULL values
        self.execute_query(
            "SELECT COUNT(*) as total_rows, COUNT(CASE WHEN RIPEBCH IS NULL OR RIPEBCH = 0 THEN 1 END) as problematic_rows FROM FFBSCANNERDATA02 WHERE TRANSDATE >= '2025-02-01' AND TRANSDATE <= '2025-02-28'",
            "Check for NULL or zero RIPEBCH values"
        )

    def debug_recordtag_analysis(self):
        """Debug RECORDTAG analysis for employee roles"""
        print("\n" + "="*60)
        print("DEBUGGING RECORDTAG ANALYSIS")
        print("="*60)

        # Check RECORDTAG values
        self.execute_query(
            "SELECT DISTINCT RECORDTAG, COUNT(*) as count FROM FFBSCANNERDATA02 WHERE TRANSDATE >= '2025-02-01' AND TRANSDATE <= '2025-02-28' GROUP BY RECORDTAG ORDER BY count DESC",
            "Check all RECORDTAG values"
        )

        # Check specific employee role queries
        self.execute_query(
            "SELECT RECORDTAG, COUNT(*) as count, SUM(RIPEBCH) as total_ripe FROM FFBSCANNERDATA02 WHERE TRANSDATE >= '2025-02-01' AND TRANSDATE <= '2025-02-28' AND RECORDTAG IN ('PM', 'P1', 'P5') GROUP BY RECORDTAG",
            "Check specific employee role queries"
        )

    def save_debug_results(self):
        """Save debug results to file"""
        debug_file = 'test/schema_debug_results.txt'
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write("PGE 2B DATABASE SCHEMA DEBUG RESULTS\n")
            f.write("=" * 50 + "\n")
            f.write(f"Debug Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Database: PTRJ_P2B.FDB\n\n")

            for key, value in self.debug_results.items():
                f.write(f"{key.upper()}:\n")
                f.write(f"  {value}\n\n")

        print(f"\n📁 Debug results saved to {debug_file}")

    def run_full_debug(self):
        """Run complete schema debugging"""
        print("PGE 2B DATABASE SCHEMA DEBUGGER")
        print("=" * 50)

        if not self.connect():
            return False

        self.debug_employee_schema()
        self.debug_division_schema()
        self.debug_quality_query()
        self.debug_recordtag_analysis()

        self.save_debug_results()

        print("\n" + "="*60)
        print("DEBUG COMPLETE")
        print("="*60)
        print("📁 Results saved to test/schema_debug_results.txt")
        print("\n📋 RECOMMENDED FIXES:")
        print("1. Update employee query based on actual EMPLOYEE/EMP table structure")
        print("2. Update division query based on actual CRDIVISION/OCFIELD table structure")
        print("3. Fix quality analysis query based on data patterns found")

        return True

def main():
    debugger = DatabaseSchemaDebugger()
    success = debugger.run_full_debug()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())