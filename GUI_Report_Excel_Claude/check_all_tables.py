#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cek semua tabel yang ada di database PGE 2B
"""

import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from firebird_connector_enhanced import FirebirdConnectorEnhanced
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def check_all_tables():
    """Cek semua tabel yang ada di database"""
    print("=" * 80)
    print("CHECK ALL TABLES - PGE 2B DATABASE")
    print("=" * 80)

    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    print(f"Database: {db_path}")
    print("-" * 80)

    try:
        connector = FirebirdConnectorEnhanced(db_path=db_path)

        if not connector.test_connection():
            raise Exception("Database connection failed")
        print("[OK] Database connection successful")

        # Get all tables
        print("\nGetting all tables...")
        tables_query = """
        SELECT RDB$RELATION_NAME, RDB$VIEW_SOURCE IS NOT NULL as IS_VIEW
        FROM RDB$RELATIONS
        WHERE RDB$RELATION_NAME NOT STARTING WITH 'RDB$'
        AND RDB$RELATION_NAME NOT STARTING WITH 'MON$'
        AND RDB$RELATION_NAME NOT STARTING WITH 'SEC$'
        ORDER BY RDB$RELATION_NAME
        """

        tables_result = connector.execute_query(tables_query)

        if tables_result:
            print(f"Found {len(tables_result)} tables/views:")

            ffb_related = []
            emp_tables = []
            other_tables = []

            for row in tables_result:
                if isinstance(row, tuple) and len(row) >= 2:
                    table_name = str(row[0]).strip()
                    is_view = bool(row[1])
                elif isinstance(row, dict):
                    table_name = row.get('RDB$RELATION_NAME', '').strip()
                    is_view = bool(row.get('IS_VIEW', False))
                else:
                    continue

                table_type = "VIEW" if is_view else "TABLE"

                # Categorize tables
                if any(keyword in table_name.upper() for keyword in ['FFB', 'SCANNER', 'TRANSACTION', 'HARVEST']):
                    ffb_related.append((table_name, table_type))
                elif any(keyword in table_name.upper() for keyword in ['EMP', 'EMPLOYEE', 'KARYAWAN']):
                    emp_tables.append((table_name, table_type))
                else:
                    other_tables.append((table_name, table_type))

            # Print FFB related tables
            if ffb_related:
                print("\n[FFB RELATED TABLES]:")
                for table_name, table_type in ffb_related:
                    print(f"   - {table_name} ({table_type})")

                    # Check row count for FFB tables
                    try:
                        count_query = f"SELECT COUNT(*) as ROW_COUNT FROM {table_name}"
                        count_result = connector.execute_query(count_query)
                        if count_result and len(count_result) > 0:
                            row = count_result[0]
                            count = row.get('ROW_COUNT', 0) if isinstance(row, dict) else (row[0] if row else 0)
                            print(f"     Rows: {count:,}")
                    except Exception as e:
                        print(f"     Error counting rows: {e}")

            # Print Employee tables
            if emp_tables:
                print("\n[EMPLOYEE TABLES]:")
                for table_name, table_type in emp_tables:
                    print(f"   - {table_name} ({table_type})")

                    # Check row count for employee tables
                    try:
                        count_query = f"SELECT COUNT(*) as ROW_COUNT FROM {table_name}"
                        count_result = connector.execute_query(count_query)
                        if count_result and len(count_result) > 0:
                            row = count_result[0]
                            count = row.get('ROW_COUNT', 0) if isinstance(row, dict) else (row[0] if row else 0)
                            print(f"     Rows: {count:,}")

                            # For EMP table, show sample data
                            if 'EMP' in table_name.upper() and count > 0:
                                try:
                                    sample_query = f"SELECT FIRST 5 * FROM {table_name}"
                                    sample_result = connector.execute_query(sample_query)
                                    if sample_result:
                                        print(f"     Sample columns: {list(sample_result[0].keys()) if isinstance(sample_result[0], dict) else 'N/A'}")
                                except Exception as e:
                                    print(f"     Error getting sample: {e}")
                    except Exception as e:
                        print(f"     Error counting rows: {e}")

            # Print other important tables
            important_others = []
            for table_name, table_type in other_tables:
                if any(keyword in table_name.upper() for keyword in ['FIELD', 'BLOCK', 'DIVISION', 'ESTATE', 'OC']):
                    important_others.append((table_name, table_type))

            if important_others:
                print("\n[OTHER IMPORTANT TABLES]:")
                for table_name, table_type in important_others:
                    print(f"   - {table_name} ({table_type})")

                    try:
                        count_query = f"SELECT COUNT(*) as ROW_COUNT FROM {table_name}"
                        count_result = connector.execute_query(count_query)
                        if count_result and len(count_result) > 0:
                            row = count_result[0]
                            count = row.get('ROW_COUNT', 0) if isinstance(row, dict) else (row[0] if row else 0)
                            print(f"     Rows: {count:,}")
                    except Exception as e:
                        print(f"     Error counting rows: {e}")

            # Print other tables (limit to first 20)
            if other_tables:
                other_filtered = [t for t in other_tables if t not in important_others]
                if other_filtered:
                    print(f"\n[OTHER TABLES] (showing first 20 of {len(other_filtered)}):")
                    for i, (table_name, table_type) in enumerate(other_filtered[:20]):
                        print(f"   - {table_name} ({table_type})")

        else:
            print("No tables found")

        print("\n" + "=" * 80)
        print("TABLE CHECK COMPLETED!")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = check_all_tables()

    if success:
        print("\n[SUCCESS] Table check completed!")
    else:
        print("\n[FAILED] Table check failed!")

if __name__ == "__main__":
    main()