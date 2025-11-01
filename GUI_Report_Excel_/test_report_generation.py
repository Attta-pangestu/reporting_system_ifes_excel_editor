#!/usr/bin/env python3
"""Test script to verify end-to-end report generation"""

import json
import os
from datetime import datetime
from report_processor import ReportProcessor
from template_manager import TemplateManager

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
    
    # Transaction data (FFBSCANNERDATA10)
    transaction_data = [
        {
            'TANGGAL': '2024-10-01',
            'NOKENDARAAN': 'B1234AB',
            'SUPIR': 'John Doe',
            'KERANI': 'Jane Smith',
            'MANDOR': 'Bob Johnson',
            'ASISTEN': 'Alice Brown',
            'BLOK': 'A01',
            'BERAT': 1500.5,
            'POTONGAN': 50.0,
            'NETTO': 1450.5,
            'HARGA': 1200.0,
            'TOTAL': 1740600.0
        },
        {
            'TANGGAL': '2024-10-02',
            'NOKENDARAAN': 'B5678CD',
            'SUPIR': 'Mike Wilson',
            'KERANI': 'Sarah Davis',
            'MANDOR': 'Tom Anderson',
            'ASISTEN': 'Lisa Garcia',
            'BLOK': 'B02',
            'BERAT': 1800.0,
            'POTONGAN': 75.0,
            'NETTO': 1725.0,
            'HARGA': 1200.0,
            'TOTAL': 2070000.0
        },
        {
            'TANGGAL': '2024-10-03',
            'NOKENDARAAN': 'B9012EF',
            'SUPIR': 'David Lee',
            'KERANI': 'Emma Martinez',
            'MANDOR': 'Chris Taylor',
            'ASISTEN': 'Amy White',
            'BLOK': 'C03',
            'BERAT': 1650.0,
            'POTONGAN': 60.0,
            'NETTO': 1590.0,
            'HARGA': 1200.0,
            'TOTAL': 1908000.0
        }
    ]
    
    # Kerani performance data
    kerani_data = [
        {'KERANI': 'Jane Smith', 'TOTAL_TRANSAKSI': 15, 'TOTAL_BERAT': 22500.0, 'TOTAL_NILAI': 27000000.0},
        {'KERANI': 'Sarah Davis', 'TOTAL_TRANSAKSI': 12, 'TOTAL_BERAT': 18000.0, 'TOTAL_NILAI': 21600000.0},
        {'KERANI': 'Emma Martinez', 'TOTAL_TRANSAKSI': 10, 'TOTAL_BERAT': 15000.0, 'TOTAL_NILAI': 18000000.0}
    ]
    
    # Mandor performance data
    mandor_data = [
        {'MANDOR': 'Bob Johnson', 'TOTAL_TRANSAKSI': 20, 'TOTAL_BERAT': 30000.0, 'TOTAL_NILAI': 36000000.0},
        {'MANDOR': 'Tom Anderson', 'TOTAL_TRANSAKSI': 18, 'TOTAL_BERAT': 27000.0, 'TOTAL_NILAI': 32400000.0},
        {'MANDOR': 'Chris Taylor', 'TOTAL_TRANSAKSI': 15, 'TOTAL_BERAT': 22500.0, 'TOTAL_NILAI': 27000000.0}
    ]
    
    # Asisten performance data
    asisten_data = [
        {'ASISTEN': 'Alice Brown', 'TOTAL_TRANSAKSI': 25, 'TOTAL_BERAT': 37500.0, 'TOTAL_NILAI': 45000000.0},
        {'ASISTEN': 'Lisa Garcia', 'TOTAL_TRANSAKSI': 22, 'TOTAL_BERAT': 33000.0, 'TOTAL_NILAI': 39600000.0},
        {'ASISTEN': 'Amy White', 'TOTAL_TRANSAKSI': 18, 'TOTAL_BERAT': 27000.0, 'TOTAL_NILAI': 32400000.0}
    ]
    
    return {
        'transaction_data': transaction_data,
        'kerani_data': kerani_data,
        'mandor_data': mandor_data,
        'asisten_data': asisten_data
    }

def test_report_generation():
    """Test end-to-end report generation with dummy data"""
    print("Testing end-to-end report generation...")
    
    # Create template manager
    template_manager = TemplateManager()
    
    # Get template info
    template_info = template_manager.get_template_info('laporan_kinerja_template')
    
    if not template_info:
        print("❌ Failed to load template!")
        return False
    
    print("✓ Template loaded successfully")
    print(f"  Template name: {template_info.get('name', 'Unknown')}")
    print(f"  Excel file: {template_info.get('excel_file', 'Unknown')}")
    print(f"  Number of queries: {len(template_info.get('queries', []))}")
    
    # Create dummy data
    dummy_data = create_dummy_data()
    print("✓ Dummy data created")
    
    # Create mock database connector
    mock_db = MockDatabaseConnector(dummy_data)
    print("✓ Mock database connector created")
    
    # Create report processor
    try:
        report_processor = ReportProcessor()
        print("✓ Report processor created")
    except Exception as e:
        print(f"❌ Failed to create report processor: {e}")
        return False
    
    # Generate report with dummy data
    try:
        print("\nGenerating report with dummy data...")
        
        # Create output directory if it doesn't exist
        output_dir = "test_outputs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate report
        result_path = report_processor.generate_report(
            template_info=template_info,
            db_connector=mock_db,
            output_path=output_dir
        )
        
        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✓ Report generated successfully: {result_path}")
            print(f"  File size: {file_size} bytes")
            print(f"  Full path: {os.path.abspath(result_path)}")
            return True
        else:
            print("❌ Report file not found after generation")
            return False
            
    except Exception as e:
        print(f"❌ Error during report generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_data_mapping():
    """Test that template data mapping works correctly"""
    print("\n" + "="*50)
    print("Testing template data mapping...")
    
    # Load template
    template_manager = TemplateManager()
    template_info = template_manager.get_template_info('laporan_kinerja_template')
    
    if not template_info:
        print("❌ Failed to load template!")
        return False
    
    # Check mappings
    mappings = template_info.get('mappings', {})
    print(f"✓ Template has {len(mappings)} mappings")
    
    # Show sample mappings
    for i, (key, mapping) in enumerate(list(mappings.items())[:5]):
        print(f"  Mapping {i+1}: {key} -> {mapping}")
    
    # Create dummy data
    dummy_data = create_dummy_data()
    
    # Test data structure matches expected queries
    queries = template_info.get('queries', [])
    for query in queries:
        query_name = query.get('name', 'Unknown')
        data_key = query_name.lower().replace(' ', '_')
        
        if data_key in dummy_data:
            data_rows = dummy_data[data_key]
            print(f"✓ Data for '{query_name}': {len(data_rows)} rows")
            if data_rows:
                print(f"  Sample keys: {list(data_rows[0].keys())}")
        else:
            print(f"⚠ No dummy data for query: {query_name}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("REPORT GENERATION TEST")
    print("=" * 60)
    
    success1 = test_template_data_mapping()
    success2 = test_report_generation()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    print("=" * 60)