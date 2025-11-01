#!/usr/bin/env python3
"""
Simple Database Schema Debug Script using direct ISQL calls
"""

import os
import subprocess
import json
from datetime import datetime

class SimpleDatabaseDebugger:
    def __init__(self):
        self.db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
        self.isql_path = r"C:\Program Files (x86)\Firebird\Firebird_1_5\bin\isql.exe"
        self.debug_results = []

    def execute_isql(self, sql, description):
        """Execute ISQL command and return results"""
        print(f"\nDEBUG: {description}")
        print(f"SQL: {sql}")

        try:
            # Create temporary SQL file
            temp_sql = "temp_query.sql"
            with open(temp_sql, 'w', encoding='utf-8') as f:
                f.write(f"CONNECT '{self.db_path}';\n")
                f.write(f"{sql};\n")
                f.write("EXIT;\n")

            # Execute ISQL
            result = subprocess.run(
                [self.isql_path, '-i', temp_sql],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            # Clean up temp file
            if os.path.exists(temp_sql):
                os.remove(temp_sql)

            if result.returncode == 0:
                output = result.stdout
                print("SUCCESS: Query executed successfully")
                if output.strip():
                    lines = output.strip().split('\n')
                    for line in lines[:10]:  # Show first 10 lines
                        print(f"   {line}")
                    if len(lines) > 10:
                        print(f"   ... and {len(lines) - 10} more lines")

                self.debug_results.append({
                    'description': description,
                    'sql': sql,
                    'success': True,
                    'output': output,
                    'error': None
                })
                return output
            else:
                error = result.stderr
                print(f"ERROR: Query failed: {error}")
                self.debug_results.append({
                    'description': description,
                    'sql': sql,
                    'success': False,
                    'output': None,
                    'error': error
                })
                return None

        except Exception as e:
            print(f"ERROR: Execution error: {e}")
            self.debug_results.append({
                'description': description,
                'sql': sql,
                'success': False,
                'output': None,
                'error': str(e)
            })
            return None

    def debug_employee_schema(self):
        """Debug employee-related queries"""
        print("\n" + "="*60)
        print("DEBUGGING EMPLOYEE SCHEMA")
        print("="*60)

        # Check if EMPLOYEE table exists
        self.execute_isql(
            "SELECT * FROM EMPLOYEE ROWS 5",
            "Check EMPLOYEE table structure"
        )

        # Check if EMP table exists (backup)
        self.execute_isql(
            "SELECT * FROM EMP ROWS 5",
            "Check EMP table structure (backup)"
        )

        # Get all employee-related tables
        self.execute_isql(
            "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%EMP%'",
            "Find all employee-related tables"
        )

        # Check SCANUSERID values in transactions
        self.execute_isql(
            "SELECT DISTINCT SCANUSERID FROM FFBSCANNERDATA02 WHERE SCANUSERID IS NOT NULL ROWS 10",
            "Check SCANUSERID values in FFB data"
        )

        # Test join with EMPLOYEE
        self.execute_isql(
            "SELECT COUNT(*) AS join_count FROM FFBSCANNERDATA02 a LEFT JOIN EMPLOYEE e ON a.SCANUSERID = e.EMPID WHERE a.TRANSDATE >= '2025-02-01' AND a.TRANSDATE <= '2025-02-28'",
            "Test join with EMPLOYEE table"
        )

        # Test join with EMP
        self.execute_isql(
            "SELECT COUNT(*) AS join_count FROM FFBSCANNERDATA02 a LEFT JOIN EMP e ON a.SCANUSERID = e.ID WHERE a.TRANSDATE >= '2025-02-01' AND a.TRANSDATE <= '2025-02-28'",
            "Test join with EMP table"
        )

    def debug_division_schema(self):
        """Debug division-related queries"""
        print("\n" + "="*60)
        print("DEBUGGING DIVISION SCHEMA")
        print("="*60)

        # Check CRDIVISION table
        self.execute_isql(
            "SELECT * FROM CRDIVISION ROWS 5",
            "Check CRDIVISION table structure"
        )

        # Check OCFIELD table (backup)
        self.execute_isql(
            "SELECT * FROM OCFIELD ROWS 5",
            "Check OCFIELD table structure (backup)"
        )

        # Find all field/division related tables
        self.execute_isql(
            "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$RELATION_NAME LIKE '%DIV%' OR RDB$RELATION_NAME LIKE '%FIELD%'",
            "Find all division/field-related tables"
        )

        # Check DIVID values in transactions
        self.execute_isql(
            "SELECT DISTINCT DIVID FROM FFBSCANNERDATA02 WHERE DIVID IS NOT NULL ROWS 10",
            "Check DIVID values in FFB data"
        )

        # Test join with CRDIVISION
        self.execute_isql(
            "SELECT COUNT(*) AS join_count FROM FFBSCANNERDATA02 a LEFT JOIN CRDIVISION c ON a.DIVID = c.ID WHERE a.DIVID IS NOT NULL",
            "Test join with CRDIVISION table"
        )

    def debug_quality_query(self):
        """Debug quality analysis query"""
        print("\n" + "="*60)
        print("DEBUGGING QUALITY ANALYSIS")
        print("="*60)

        # Test basic quality data
        self.execute_isql(
            "SELECT TRANSDATE, SUM(RIPEBCH) AS ripe, SUM(BLACKBCH) AS black, SUM(ROTTENBCH) AS rotten FROM FFBSCANNERDATA02 WHERE TRANSDATE >= '2025-02-01' AND TRANSDATE <= '2025-02-28' AND RIPEBCH > 0 GROUP BY TRANSDATE ORDER BY TRANSDATE ROWS 5",
            "Test basic quality data aggregation"
        )

        # Test calculation
        self.execute_isql(
            "SELECT TRANSDATE, SUM(RIPEBCH) AS ripe, SUM(BLACKBCH) AS black, SUM(ROTTENBCH) AS rotten, CAST(((SUM(BLACKBCH) + SUM(ROTTENBCH)) * 100.0 / NULLIF(SUM(RIPEBCH), 0)) AS NUMERIC(10,2)) AS defect_pct FROM FFBSCANNERDATA02 WHERE TRANSDATE >= '2025-02-01' AND TRANSDATE <= '2025-02-28' AND RIPEBCH > 0 GROUP BY TRANSDATE ORDER BY TRANSDATE ROWS 5",
            "Test defect percentage calculation"
        )

        # Check for NULL values
        self.execute_isql(
            "SELECT COUNT(*) AS total_rows, COUNT(CASE WHEN RIPEBCH IS NULL OR RIPEBCH = 0 THEN 1 END) AS problematic_rows FROM FFBSCANNERDATA02 WHERE TRANSDATE >= '2025-02-01' AND TRANSDATE <= '2025-02-28'",
            "Check for NULL or zero RIPEBCH values"
        )

    def debug_recordtag_analysis(self):
        """Debug RECORDTAG analysis for employee roles"""
        print("\n" + "="*60)
        print("DEBUGGING RECORDTAG ANALYSIS")
        print("="*60)

        # Check RECORDTAG values
        self.execute_isql(
            "SELECT RECORDTAG, COUNT(*) AS row_count FROM FFBSCANNERDATA02 WHERE TRANSDATE >= '2025-02-01' AND TRANSDATE <= '2025-02-28' GROUP BY RECORDTAG ORDER BY row_count DESC",
            "Check all RECORDTAG values"
        )

        # Check specific employee role queries
        self.execute_isql(
            "SELECT RECORDTAG, COUNT(*) AS row_count, SUM(RIPEBCH) AS total_ripe FROM FFBSCANNERDATA02 WHERE TRANSDATE >= '2025-02-01' AND TRANSDATE <= '2025-02-28' AND RECORDTAG IN ('PM', 'P1', 'P5') GROUP BY RECORDTAG",
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

            for result in self.debug_results:
                f.write(f"\n{result['description']}:\n")
                f.write(f"SQL: {result['sql']}\n")
                f.write(f"Success: {result['success']}\n")
                if result['output']:
                    f.write(f"Output:\n{result['output']}\n")
                if result['error']:
                    f.write(f"Error: {result['error']}\n")
                f.write("-" * 40 + "\n")

        print(f"\nDebug results saved to {debug_file}")

        # Also save as JSON
        json_file = 'test/schema_debug_results.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.debug_results, f, indent=2, ensure_ascii=False)
        print(f"Debug results also saved to {json_file}")

    def run_full_debug(self):
        """Run complete schema debugging"""
        print("PGE 2B DATABASE SCHEMA DEBUGGER")
        print("=" * 50)

        # Check if ISQL exists
        if not os.path.exists(self.isql_path):
            print(f"ERROR: ISQL not found at: {self.isql_path}")
            return False

        # Check if database exists
        if not os.path.exists(self.db_path):
            print(f"ERROR: Database not found at: {self.db_path}")
            return False

        print(f"Database: {self.db_path}")
        print(f"ISQL: {self.isql_path}")

        self.debug_employee_schema()
        self.debug_division_schema()
        self.debug_quality_query()
        self.debug_recordtag_analysis()

        self.save_debug_results()

        print("\n" + "="*60)
        print("DEBUG COMPLETE")
        print("="*60)
        print("\n📋 ANALYSIS SUMMARY:")
        print("1. Check if EMPLOYEE or EMP table exists and has correct structure")
        print("2. Check if CRDIVISION or OCFIELD table exists and has correct structure")
        print("3. Verify field names in employee and division tables")
        print("4. Fix quality analysis query based on actual data structure")

        return True

def main():
    debugger = SimpleDatabaseDebugger()
    success = debugger.run_full_debug()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())