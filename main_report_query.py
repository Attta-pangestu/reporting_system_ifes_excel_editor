#!/usr/bin/env python3
"""
Main Report Query for FFB Performance Report
Generates the Laporan Kinerja Kerani, Mandor, dan Asisten based on database analysis
"""

import sys
import os
from datetime import datetime, timedelta
from firebird_connector import FirebirdConnector

class FFBReportGenerator:
    def __init__(self, db_path, username='SYSDBA', password='masterkey'):
        """Initialize the FFB Report Generator"""
        self.connector = FirebirdConnector(db_path, username, password)
        self.results = {}
        
    def get_report_data(self, start_date=None, end_date=None, estate_filter=None):
        """
        Generate comprehensive FFB performance report data
        
        Args:
            start_date: Start date for report (YYYY-MM-DD format)
            end_date: End date for report (YYYY-MM-DD format) 
            estate_filter: Optional estate/division filter
        """
        
        # Set default date range if not provided (last 30 days)
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
        print(f"Generating FFB Performance Report for period: {start_date} to {end_date}")
        
        # Main query - get transaction data with worker and division info
        main_query = f"""
        SELECT FIRST 100
            d.DIVCODE,
            d.DIVNAME,
            e.EMPCODE,
            e.NAME,
            'KERANI' as MANDORE,
            'N/A' as LABOUR_NAME,
            COUNT(*) as JUMLAH_TRANSAKSI
        FROM FFBSCANNERDATA10 f
        LEFT JOIN WORKERINFO w ON f.WORKERID = w.EMPID
        LEFT JOIN EMP e ON w.EMPID = e.ID
        LEFT JOIN CRDIVISION d ON w.FIELDDIVID = d.ID
        WHERE f.TRANSDATE >= CURRENT_DATE - 30
        GROUP BY d.DIVCODE, d.DIVNAME, e.EMPCODE, e.NAME
        ORDER BY d.DIVCODE, e.EMPCODE
        """
        
        print("Executing main report query...")
        main_results = self.connector.execute_query(main_query)
        
        if main_results and len(main_results) > 0 and 'rows' in main_results[0]:
            self.results['main_data'] = main_results[0]['rows']
            print(f"✓ Retrieved {len(self.results['main_data'])} main data records")
        else:
            print("⚠ No main data found")
            self.results['main_data'] = []
        
        # Get summary by estate
        summary_query = f"""
        SELECT 
            d.DIVCODE,
            d.DIVNAME,
            COUNT(DISTINCT f.WORKERID) as TOTAL_WORKERS,
            COUNT(*) as TOTAL_TRANSAKSI
        FROM FFBSCANNERDATA10 f
        LEFT JOIN WORKERINFO w ON f.WORKERID = w.EMPID
        LEFT JOIN CRDIVISION d ON w.FIELDDIVID = d.ID
        WHERE f.TRANSDATE >= CURRENT_DATE - 30
        """
        
        if estate_filter:
            summary_query += f" AND d.DIVCODE = '{estate_filter}'"
            
        summary_query += """
        GROUP BY d.DIVCODE, d.DIVNAME
        ORDER BY d.DIVCODE
        """
        
        print("Executing summary query...")
        summary_results = self.connector.execute_query(summary_query)
        
        if summary_results and len(summary_results) > 0 and 'rows' in summary_results[0]:
            self.results['summary_data'] = summary_results[0]['rows']
            print(f"✓ Retrieved {len(self.results['summary_data'])} summary records")
        else:
            print("⚠ No summary data found")
            self.results['summary_data'] = []
        
        # Transaction status breakdown
        status_query = f"""
        SELECT 
            f.TRANSSTATUS,
            COUNT(*) as COUNT_STATUS
        FROM FFBSCANNERDATA10 f
        WHERE f.TRANSDATE >= CURRENT_DATE - 30
        GROUP BY f.TRANSSTATUS
        ORDER BY f.TRANSSTATUS
        """
        
        print("Executing transaction status query...")
        status_results = self.connector.execute_query(status_query)
        
        if status_results and len(status_results) > 0 and 'rows' in status_results[0]:
            self.results['status_breakdown'] = status_results[0]['rows']
            print(f"✓ Retrieved {len(self.results['status_breakdown'])} status records")
        else:
            print("⚠ No status data found")
            self.results['status_breakdown'] = []
        
        # Get date range info (use broader range to ensure data)
        date_range_query = f"""
        SELECT 
            MIN(f.TRANSDATE) as START_DATE,
            MAX(f.TRANSDATE) as END_DATE,
            COUNT(DISTINCT f.TRANSDATE) as UNIQUE_DAYS
        FROM FFBSCANNERDATA10 f
        WHERE f.TRANSDATE >= CURRENT_DATE - 30
        """
        
        print("Executing date range query...")
        date_results = self.connector.execute_query(date_range_query)
        
        if date_results and len(date_results) > 0 and 'rows' in date_results[0]:
            date_info = date_results[0]['rows'][0] if date_results[0]['rows'] else {}
            self.results['date_range'] = {
                'start_date': date_info.get('START_DATE', 'N/A'),
                'end_date': date_info.get('END_DATE', 'N/A'),
                'unique_days': date_info.get('UNIQUE_DAYS', 'N/A')
            }
            print("✓ Retrieved date range info")
        else:
            print("⚠ No date range data found")
            self.results['date_range'] = {
                'start_date': 'N/A',
                'end_date': 'N/A', 
                'unique_days': 'N/A'
            }
        
        return self.results
    
    def save_results_to_file(self, filename=None):
        """Save query results to text file for analysis"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'ffb_report_results_{timestamp}.txt'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("FFB PERFORMANCE REPORT RESULTS\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Date range information
            if 'date_range' in self.results:
                date_info = self.results['date_range']
                f.write("DATE RANGE INFORMATION:\n")
                f.write("-" * 30 + "\n")
                f.write(f"Start Date: {date_info.get('start_date', 'N/A')}\n")
                f.write(f"End Date: {date_info.get('end_date', 'N/A')}\n")
                f.write(f"Unique Days: {date_info.get('unique_days', 'N/A')}\n\n")
            
            # Summary data
            if 'summary_data' in self.results and self.results['summary_data']:
                f.write("SUMMARY BY ESTATE:\n")
                f.write("-" * 30 + "\n")
                for row in self.results['summary_data']:
                    f.write(f"Estate: {row.get('DIVCODE', 'N/A')} - {row.get('DIVNAME', 'N/A')}\n")
                    f.write(f"  Total Workers: {row.get('TOTAL_WORKERS', 0)}\n")
                    f.write(f"  Total Transactions: {row.get('TOTAL_TRANSAKSI', 0)}\n\n")
            
            # Transaction status breakdown
            if 'status_breakdown' in self.results and self.results['status_breakdown']:
                f.write("TRANSACTION STATUS BREAKDOWN:\n")
                f.write("-" * 30 + "\n")
                for row in self.results['status_breakdown']:
                    f.write(f"Status {row.get('TRANSSTATUS', 'N/A')}: {row.get('COUNT_STATUS', 0)}\n")
                f.write("\n")
            
            # Main data (first 20 records for preview)
            if 'main_data' in self.results and self.results['main_data']:
                f.write("MAIN DATA (First 20 records):\n")
                f.write("-" * 30 + "\n")
                headers = ['DIVCODE', 'DIVNAME', 'EMPCODE', 'NAME', 'MANDORE', 
                          'LABOUR_NAME', 'JUMLAH_TRANSAKSI']
                f.write(" | ".join(headers) + "\n")
                f.write("-" * 120 + "\n")
                
                for i, row in enumerate(self.results['main_data'][:20]):
                    values = [
                        row.get('DIVCODE', 'N/A'),
                        row.get('DIVNAME', 'N/A'),
                        row.get('EMPCODE', 'N/A'),
                        row.get('NAME', 'N/A'),
                        row.get('MANDORE', 'N/A'),
                        row.get('LABOUR_NAME', 'N/A'),
                        str(row.get('JUMLAH_TRANSAKSI', 0))
                    ]
                    f.write(" | ".join(values) + "\n")
                
                if len(self.results['main_data']) > 20:
                    f.write(f"\n... and {len(self.results['main_data']) - 20} more records\n")
        
        print(f"✓ Results saved to: {filename}")
        return filename

def main():
    """Main function to test the report generator"""
    
    # Database configuration
    db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        # Initialize report generator
        print("Initializing FFB Report Generator...")
        generator = FFBReportGenerator(db_path)
        
        # Generate report for last 30 days to ensure we capture data
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        print(f"Generating report for period: {start_date} to {end_date}")
        
        # Get report data
        results = generator.get_report_data(start_date, end_date)
        
        # Save results
        output_file = generator.save_results_to_file()
        
        print("\n" + "="*60)
        print("REPORT GENERATION COMPLETED")
        print("="*60)
        print(f"Results saved to: {output_file}")
        
        # Print summary
        if 'summary_data' in results and results['summary_data']:
            print(f"\nFound {len(results['summary_data'])} estates")
            print(f"Main data records: {len(results.get('main_data', []))}")
            print(f"Status categories: {len(results.get('status_breakdown', []))}")
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()