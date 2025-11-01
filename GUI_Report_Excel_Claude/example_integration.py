#!/usr/bin/env python3
"""
Example Integration - How to use Enhanced Firebird Connector in other modules
Contoh integrasi Enhanced Firebird Connector dengan modul lain
"""

import sys
import os
from datetime import datetime, date
from typing import List, Dict, Any
import pandas as pd

# Import enhanced connector
from firebird_connector_enhanced import (
    FirebirdConnectorEnhanced,
    connect_to_pge2b,
    execute_pge2b_query,
    get_pge2b_tables
)

class FFBDataManager:
    """
    Contoh class untuk mengelola data FFB menggunakan Enhanced Firebird Connector
    """

    def __init__(self):
        """Initialize dengan default PGE 2B connection"""
        self.connector = FirebirdConnectorEnhanced.create_default_connector()

    def get_daily_transactions(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Get daily transaction data

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of daily transaction records
        """
        query = """
        SELECT
            TRANSDATE,
            COUNT(*) as JUMLAH_TRANSAKSI,
            SUM(RIPEBCH) as TOTAL_RIPE,
            SUM(UNRIPEBCH) as TOTAL_UNRIPE,
            SUM(BLACKBCH) as TOTAL_BLACK,
            SUM(ROTTENBCH) as TOTAL_ROTTEN
        FROM FFBSCANNERDATA10
        WHERE TRANSDATE >= '{start_date}'
          AND TRANSDATE <= '{end_date}'
        GROUP BY TRANSDATE
        ORDER BY TRANSDATE
        """

        try:
            with self.connector as conn:
                return conn.execute_query(query, {
                    'start_date': start_date,
                    'end_date': end_date
                })
        except Exception as e:
            print(f"Error getting daily transactions: {e}")
            return []

    def get_employee_performance(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Get employee performance data

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List employee performance records
        """
        query = """
        SELECT
            e.NAME as EMPLOYEE_NAME,
            a.RECORDTAG,
            COUNT(*) as JUMLAH_TRANSAKSI,
            SUM(a.RIPEBCH) as TOTAL_RIPE,
            AVG(a.RIPEBCH) as AVG_RIPE
        FROM FFBSCANNERDATA10 a
        LEFT JOIN EMP e ON a.SCANUSERID = e.ID
        WHERE a.TRANSDATE >= '{start_date}'
          AND a.TRANSDATE <= '{end_date}'
        GROUP BY e.NAME, a.RECORDTAG
        ORDER BY e.NAME, a.RECORDTAG
        """

        try:
            with self.connector as conn:
                data = conn.execute_query(query, {
                    'start_date': start_date,
                    'end_date': end_date
                })

                # Process data untuk mapping role
                role_mapping = {
                    'PM': 'Kerani',
                    'P1': 'Mandor',
                    'P5': 'Asisten'
                }

                for record in data:
                    record['ROLE_NAME'] = role_mapping.get(record.get('RECORDTAG', ''), 'Unknown')

                return data
        except Exception as e:
            print(f"Error getting employee performance: {e}")
            return []

    def get_quality_metrics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get quality metrics untuk periode tertentu

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary with quality metrics
        """
        query = """
        SELECT
            SUM(RIPEBCH) as TOTAL_RIPE,
            SUM(BLACKBCH) as TOTAL_BLACK,
            SUM(ROTTENBCH) as TOTAL_ROTTEN,
            SUM(RATDMGBCH) as TOTAL_RAT_DAMAGE
        FROM FFBSCANNERDATA10
        WHERE TRANSDATE >= '{start_date}'
          AND TRANSDATE <= '{end_date}'
        """

        try:
            with self.connector as conn:
                result = conn.execute_query(query, {
                    'start_date': start_date,
                    'end_date': end_date
                })

                if result and len(result) > 0:
                    data = result[0]
                    total_ripe = int(data.get('TOTAL_RIPE', 0))
                    total_defects = (
                        int(data.get('TOTAL_BLACK', 0)) +
                        int(data.get('TOTAL_ROTTEN', 0)) +
                        int(data.get('TOTAL_RAT_DAMAGE', 0))
                    )

                    return {
                        'total_ripe': total_ripe,
                        'total_black': int(data.get('TOTAL_BLACK', 0)),
                        'total_rotten': int(data.get('TOTAL_ROTTEN', 0)),
                        'total_rat_damage': int(data.get('TOTAL_RAT_DAMAGE', 0)),
                        'total_defects': total_defects,
                        'quality_percentage': (total_defects / total_ripe * 100) if total_ripe > 0 else 0
                    }
                else:
                    return {
                        'total_ripe': 0,
                        'quality_percentage': 0,
                        'error': 'No data found'
                    }
        except Exception as e:
            return {'error': str(e)}

class ReportGenerator:
    """
    Contoh class untuk generate report menggunakan Enhanced Firebird Connector
    """

    def __init__(self, db_connector: FirebirdConnectorEnhanced = None):
        """
        Initialize dengan dependency injection

        Args:
            db_connector: Database connector instance (optional)
        """
        self.db = db_connector or FirebirdConnectorEnhanced.create_default_connector()

    def generate_summary_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate summary report

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary dengan summary data
        """
        try:
            # Get various data components
            daily_data = self.get_daily_summary(start_date, end_date)
            employee_data = self.get_employee_summary(start_date, end_date)
            quality_data = self.get_quality_summary(start_date, end_date)

            return {
                'period': f"{start_date} to {end_date}",
                'daily_summary': daily_data,
                'employee_summary': employee_data,
                'quality_summary': quality_data,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            return {'error': str(e)}

    def get_daily_summary(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get daily summary data"""
        query = """
        SELECT
            COUNT(*) as total_transactions,
            SUM(RIPEBCH) as total_ripe,
            AVG(RIPEBCH) as avg_ripe_per_transaction,
            MAX(RIPEBCH) as max_ripe,
            MIN(RIPEBCH) as min_ripe
        FROM FFBSCANNERDATA10
        WHERE TRANSDATE >= '{start_date}' AND TRANSDATE <= '{end_date}'
        """

        try:
            with self.db as conn:
                result = conn.execute_query(query, {
                    'start_date': start_date,
                    'end_date': end_date
                })

                if result:
                    return result[0]
                else:
                    return {'error': 'No daily data found'}
        except Exception as e:
            return {'error': str(e)}

    def get_employee_summary(self, start_date: str, end_date: str) -> List[Dict]:
        """Get employee summary data"""
        query = """
        SELECT
            COUNT(DISTINCT SCANUSERID) as total_karyawan,
            COUNT(*) as total_transaksi,
            SUM(RIPEBCH) as total_ripe
        FROM FFBSCANNERDATA10
        WHERE TRANSDATE >= '{start_date}' AND TRANSDATE <= '{end_date}'
        """

        try:
            with self.db as conn:
                return conn.execute_query(query, {
                    'start_date': start_date,
                    'end_date': end_date
                })
        except Exception as e:
            return [{'error': str(e)}]

    def get_quality_summary(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get quality summary"""
        query = """
        SELECT
            SUM(BLACKBCH + ROTTENBCH + RATDMGBCH) * 100.0 / NULLIF(SUM(RIPEBCH), 0) as defect_percentage,
            COUNT(*) as total_records
        FROM FFBSCANNERDATA10
        WHERE TRANSDATE >= '{start_date}' AND TRANSDATE <= '{end_date}'
        """

        try:
            with self.db as conn:
                result = conn.execute_query(query, {
                    'start_date': start_date,
                    'end_date': end_date
                })

                if result:
                    return result[0]
                else:
                    return {'defect_percentage': 0, 'total_records': 0}
        except Exception as e:
            return {'error': str(e)}

class DataAnalyzer:
    """
    Contoh class untuk analisis data menggunakan Enhanced Firebird Connector
    """

    @staticmethod
    def analyze_trends(start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Analisis trends menggunakan convenience functions

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary dengan trend analysis
        """
        try:
            # Get daily data
            query = """
            SELECT
                TRANSDATE,
                COUNT(*) as transactions,
                SUM(RIPEBCH) as ripe
            FROM FFBSCANNERDATA10
            WHERE TRANSDATE >= '{start_date}' AND TRANSDATE <= '{end_date}'
            GROUP BY TRANSDATE
            ORDER BY TRANSDATE
            """

            data = execute_pge2b_query(query, {
                'start_date': start_date,
                'end_date': end_date
            })

            if not data:
                return {'error': 'No data available for analysis'}

            # Convert to DataFrame untuk analysis
            df = pd.DataFrame(data)

            # Konversi tipe data
            df['transactions'] = pd.to_numeric(df['transactions'], errors='coerce')
            df['ripe'] = pd.to_numeric(df['ripe'], errors='coerce')

            # Calculate trends
            analysis = {
                'total_days': len(df),
                'total_transactions': df['transactions'].sum(),
                'total_ripe': df['ripe'].sum(),
                'avg_daily_transactions': df['transactions'].mean(),
                'avg_daily_ripe': df['ripe'].mean(),
                'peak_day': df.loc[df['transactions'].idxmax(), 'TRANSDATE'],
                'peak_transactions': df['transactions'].max(),
                'trend_direction': 'increasing' if df['transactions'].iloc[-1] > df['transactions'].iloc[0] else 'decreasing'
            }

            return analysis

        except Exception as e:
            return {'error': str(e)}

# Contoh penggunaan dalam script lain
def example_usage():
    """Contoh penggunaan Enhanced Firebird Connector"""
    print("=== Enhanced Firebird Connector - Example Usage ===")

    # 1. Menggunakan convenience functions
    print("\n1. Using Convenience Functions:")
    try:
        tables = get_pge2b_tables()
        print(f"   Found {len(tables)} tables in PGE 2B")
        if tables:
            print(f"   First 5 tables: {tables[:5]}")
    except Exception as e:
        print(f"   Error: {e}")

    # 2. Menggunakan FFBDataManager
    print("\n2. Using FFBDataManager:")
    try:
        manager = FFBDataManager()

        # Test koneksi
        if manager.connector.test_connection():
            print("   + Connection to PGE 2B successful")

            # Get sample data
            sample_data = manager.get_daily_transactions('2025-10-01', '2025-10-31')
            print(f"   + Retrieved {len(sample_data)} daily records")

            # Get quality metrics
            quality = manager.get_quality_metrics('2025-10-01', '2025-10-31')
            if 'error' not in quality:
                print(f"   + Quality metrics: {quality.get('quality_percentage', 0):.2f}% defect rate")
        else:
            print("   - Connection failed")
    except Exception as e:
        print(f"   Error: {e}")

    # 3. Menggunakan ReportGenerator dengan dependency injection
    print("\n3. Using ReportGenerator:")
    try:
        # Create dengan custom connector (misalnya untuk testing)
        test_connector = FirebirdConnectorEnhanced.create_default_connector()
        generator = ReportGenerator(test_connector)

        print("   + ReportGenerator initialized with dependency injection")
        print("   + Ready to generate reports with customizable connector")
    except Exception as e:
        print(f"   Error: {e}")

    # 4. Menggunakan DataAnalyzer
    print("\n4. Using DataAnalyzer:")
    try:
        analysis = DataAnalyzer.analyze_trends('2025-10-01', '2025-10-31')
        if 'error' not in analysis:
            print(f"   + Analysis completed: {analysis.get('total_days', 0)} days analyzed")
            print(f"   + Trend direction: {analysis.get('trend_direction', 'unknown')}")
        else:
            print(f"   - Analysis failed: {analysis['error']}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n=== Example Usage Completed ===")

# Contoh integrasi dengan GUI atau web framework
def web_api_example():
    """Contoh integrasi dengan web API"""
    from flask import Flask, jsonify
    app = Flask(__name__)

    @app.route('/api/ffb/daily')
    def get_daily_ffb():
        """API endpoint untuk daily FFB data"""
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date required'}), 400

        try:
            manager = FFBDataManager()
            data = manager.get_daily_transactions(start_date, end_date)
            return jsonify({'success': True, 'data': data})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app

if __name__ == "__main__":
    example_usage()

    # Uncomment untuk testing web API
    # web_app = web_api_example()
    # web_app.run(debug=True)