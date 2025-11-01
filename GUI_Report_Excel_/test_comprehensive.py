#!/usr/bin/env python3
"""
Comprehensive test for the Excel report generation system.
Tests both real database connection and dummy data fallback.
"""

import os
import sys
from datetime import datetime
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from database_connector import DatabaseConnector
from template_manager import TemplateManager
from report_processor import ReportProcessor

class MockDatabaseConnector:
    """Mock database connector that returns dummy data"""
    
    def __init__(self, dummy_data):
        self.dummy_data = dummy_data
    
    def execute_query(self, query, as_dict=True):
        """Mock query execution that returns dummy data based on query content"""
        query_lower = query.lower()
        
        # Determine which data to return based on query content
        if 'kerani' in query_lower and 'group by' in query_lower:
            return self.dummy_data['kerani_data']
        elif 'mandor' in query_lower and 'group by' in query_lower:
            return self.dummy_data['mandor_data']
        elif 'asisten' in query_lower and 'group by' in query_lower:
            return self.dummy_data['asisten_data']
        elif 'ffbscannerdata10' in query_lower:
            return self.dummy_data['transaction_data']
        else:
            # Default to transaction data
            return self.dummy_data['transaction_data']

def create_dummy_data():
    """Create dummy data that matches the expected structure"""
    return {
        'transaction_data': [
            {'TANGGAL': '2024-10-01', 'KERANI': 'John Doe', 'MANDOR': 'Jane Smith', 'ASISTEN': 'Bob Wilson', 'BERAT': 1500.5, 'NILAI': 750000},
            {'TANGGAL': '2024-10-02', 'KERANI': 'Alice Brown', 'MANDOR': 'Charlie Davis', 'ASISTEN': 'Diana Lee', 'BERAT': 2200.0, 'NILAI': 1100000},
            {'TANGGAL': '2024-10-03', 'KERANI': 'Eve Johnson', 'MANDOR': 'Frank Miller', 'ASISTEN': 'Grace Taylor', 'BERAT': 1800.75, 'NILAI': 900000}
        ],
        'kerani_data': [
            {'KERANI': 'John Doe', 'TOTAL_TRANSAKSI': 15, 'TOTAL_BERAT': 22500.5, 'TOTAL_NILAI': 11250000},
            {'KERANI': 'Alice Brown', 'TOTAL_TRANSAKSI': 12, 'TOTAL_BERAT': 18000.0, 'TOTAL_NILAI': 9000000},
            {'KERANI': 'Eve Johnson', 'TOTAL_TRANSAKSI': 18, 'TOTAL_BERAT': 27000.75, 'TOTAL_NILAI': 13500000}
        ],
        'mandor_data': [
            {'MANDOR': 'Jane Smith', 'TOTAL_TRANSAKSI': 20, 'TOTAL_BERAT': 30000.0, 'TOTAL_NILAI': 15000000},
            {'MANDOR': 'Charlie Davis', 'TOTAL_TRANSAKSI': 16, 'TOTAL_BERAT': 24000.5, 'TOTAL_NILAI': 12000000},
            {'MANDOR': 'Frank Miller', 'TOTAL_TRANSAKSI': 22, 'TOTAL_BERAT': 33000.25, 'TOTAL_NILAI': 16500000}
        ],
        'asisten_data': [
            {'ASISTEN': 'Bob Wilson', 'TOTAL_TRANSAKSI': 25, 'TOTAL_BERAT': 37500.0, 'TOTAL_NILAI': 18750000},
            {'ASISTEN': 'Diana Lee', 'TOTAL_TRANSAKSI': 20, 'TOTAL_BERAT': 30000.5, 'TOTAL_NILAI': 15000000},
            {'ASISTEN': 'Grace Taylor', 'TOTAL_TRANSAKSI': 28, 'TOTAL_BERAT': 42000.75, 'TOTAL_NILAI': 21000000}
        ]
    }

def test_database_connection():
    """Test real database connection"""
    print("Testing real database connection...")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        databases = config_manager.get_databases()
        
        if 'ptrj_p2b' not in databases:
            print("❌ Database 'ptrj_p2b' not found in configuration")
            return None
        
        db_config = databases['ptrj_p2b']
        print(f"✓ Database configuration loaded: {db_config['path']}")
        
        # Create database connector
        db_connector = DatabaseConnector(
            db_path=db_config['path'],
            username=db_config['username'],
            password=db_config['password']
        )
        
        # Test a simple query
        test_query = "SELECT FIRST 1 * FROM RDB$DATABASE"
        result = db_connector.execute_query(test_query)
        
        if result is not None:
            print("✓ Database connection successful!")
            return db_connector
        else:
            print("❌ Database query returned no results")
            return None
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def test_report_generation_with_real_db():
    """Test report generation with real database"""
    print("\n" + "="*60)
    print("TESTING REPORT GENERATION WITH REAL DATABASE")
    print("="*60)
    
    # Test database connection
    db_connector = test_database_connection()
    
    if not db_connector:
        print("❌ Cannot proceed with real database test - connection failed")
        return False
    
    try:
        # Load template
        template_manager = TemplateManager()
        template_info = template_manager.get_template_info('laporan_kinerja_template')
        
        if not template_info:
            print("❌ Failed to load template!")
            return False
        
        print("✓ Template loaded successfully")
        
        # Create report processor
        report_processor = ReportProcessor()
        
        # Generate report
        output_dir = "test_outputs_real_db"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print("Generating report with real database data...")
        result_path = report_processor.generate_report(
            template_info=template_info,
            db_connector=db_connector,
            output_path=output_dir
        )
        
        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✓ Report generated successfully: {result_path}")
            print(f"  File size: {file_size} bytes")
            return True
        else:
            print("❌ Report generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during real database report generation: {e}")
        traceback.print_exc()
        return False

def test_report_generation_with_dummy_data():
    """Test report generation with dummy data"""
    print("\n" + "="*60)
    print("TESTING REPORT GENERATION WITH DUMMY DATA")
    print("="*60)
    
    try:
        # Create dummy data
        dummy_data = create_dummy_data()
        print("✓ Dummy data created")
        
        # Create mock database connector
        mock_db = MockDatabaseConnector(dummy_data)
        
        # Load template
        template_manager = TemplateManager()
        template_info = template_manager.get_template_info('laporan_kinerja_template')
        
        if not template_info:
            print("❌ Failed to load template!")
            return False
        
        print("✓ Template loaded successfully")
        
        # Create report processor
        report_processor = ReportProcessor()
        
        # Generate report
        output_dir = "test_outputs_dummy"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print("Generating report with dummy data...")
        result_path = report_processor.generate_report(
            template_info=template_info,
            db_connector=mock_db,
            output_path=output_dir
        )
        
        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✓ Report generated successfully: {result_path}")
            print(f"  File size: {file_size} bytes")
            return True
        else:
            print("❌ Report generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during dummy data report generation: {e}")
        traceback.print_exc()
        return False

def main():
    """Run comprehensive tests"""
    print("COMPREHENSIVE EXCEL REPORT GENERATION TEST")
    print("="*60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test 1: Real database connection and report generation
    results['real_db'] = test_report_generation_with_real_db()
    
    # Test 2: Dummy data report generation (fallback)
    results['dummy_data'] = test_report_generation_with_dummy_data()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if results['real_db']:
        print("✅ Real database test: PASSED")
        print("   - Database connection successful")
        print("   - Report generation with real data successful")
    else:
        print("❌ Real database test: FAILED")
        print("   - Database connection or report generation failed")
    
    if results['dummy_data']:
        print("✅ Dummy data test: PASSED")
        print("   - Mock database connector working")
        print("   - Report generation with dummy data successful")
    else:
        print("❌ Dummy data test: FAILED")
        print("   - Mock database or report generation failed")
    
    # Overall result
    if results['dummy_data']:
        if results['real_db']:
            print("\n🎉 EXCELLENT: Both real database and dummy data tests passed!")
            print("   The system is fully functional with real data and has a reliable fallback.")
        else:
            print("\n⚠️  GOOD: Dummy data test passed, but real database test failed.")
            print("   The system can generate reports with dummy data as fallback.")
            print("   Check database connection settings for real data functionality.")
    else:
        print("\n❌ CRITICAL: Both tests failed!")
        print("   The report generation system needs debugging.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()