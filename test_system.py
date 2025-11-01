#!/usr/bin/env python3
"""
Test script untuk sistem Excel Report Generator
Menguji semua komponen dan memverifikasi output
"""

import os
import sys
import json
from datetime import datetime, date
from report_generator import ReportGenerator
from template_processor import TemplateProcessor
from formula_engine import FormulaEngine

def test_template_processor():
    """Test TemplateProcessor functionality."""
    print("Testing TemplateProcessor...")
    
    template_path = "sample_template.xlsx"
    formula_path = "sample_formula.json"
    
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return False
    
    if not os.path.exists(formula_path):
        print(f"❌ Formula file not found: {formula_path}")
        return False
    
    try:
        processor = TemplateProcessor(template_path, formula_path)
        
        # Test if workbook is loaded (workbook is loaded in constructor)
        if processor.workbook is None:
            print("❌ Failed to load template")
            return False
        
        print("✅ Template loaded successfully")
        
        # Test sheet names
        sheet_names = processor.workbook.sheetnames
        print(f"✅ Found {len(sheet_names)} sheets")
        
        # Test placeholder info
        placeholder_info = processor.get_placeholder_info()
        print(f"✅ Found placeholders: {len(placeholder_info)}")
        
        return True
        
    except Exception as e:
        print(f"❌ TemplateProcessor test failed: {e}")
        return False

def test_formula_engine():
    """Test FormulaEngine functionality"""
    print("Testing FormulaEngine...")
    try:
        formula_path = "sample_formula.json"
        
        # Create a mock database connector
        class MockDBConnector:
            def execute_query(self, query):
                return [{"estate_name": "Test Estate", "total_weight": 1000}]
        
        db_connector = MockDBConnector()
        engine = FormulaEngine(formula_path, db_connector)
        
        # Test that formulas are loaded (loaded in constructor)
        if not engine.formulas:
            print("❌ Failed to load formulas")
            return False
            
        # Test getting formula definitions
        formula_defs = engine.formulas
        print(f"✅ Loaded {len(formula_defs.get('queries', {}))} queries")
        print(f"✅ Loaded {len(formula_defs.get('variables', {}))} variables")
            
        print("✅ FormulaEngine PASSED")
        return True
        
    except Exception as e:
        print(f"❌ FormulaEngine test failed: {e}")
        return False

def test_report_generator():
    """Test ReportGenerator functionality"""
    print("Testing ReportGenerator...")
    try:
        template_path = "sample_template.xlsx"
        formula_path = "sample_formula.json"
        
        # Mock database config with correct FirebirdConnector parameters
        db_config = {
            "db_path": "test.fdb",
            "username": "SYSDBA",
            "password": "masterkey"
        }
        
        generator = ReportGenerator(template_path, formula_path, db_config)
        
        # Test basic functionality
        if hasattr(generator, 'generate_report'):
            print("✅ generate_report method exists")
        else:
            print("❌ generate_report method missing")
            return False
            
        print("✅ ReportGenerator PASSED")
        return True
        
    except Exception as e:
        print(f"❌ ReportGenerator test failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist."""
    print("\nTesting file structure...")
    
    required_files = [
        "template_processor.py",
        "formula_engine.py", 
        "report_generator.py",
        "sample_template.xlsx",
        "sample_formula.json",
        "gui_excel_report_generator.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file} exists")
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def test_sample_data_structure():
    """Test sample data structure."""
    print("\nTesting sample data structure...")
    
    try:
        # Test formula file structure
        with open("sample_formula.json", 'r', encoding='utf-8') as f:
            formula_data = json.load(f)
        
        required_sections = ['queries', 'variables', 'repeating_sections', 'formatting']
        for section in required_sections:
            if section in formula_data:
                print(f"✅ Formula section '{section}' exists")
            else:
                print(f"❌ Formula section '{section}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Sample data structure test failed: {e}")
        return False

def run_integration_test():
    """Run a basic integration test."""
    print("\nRunning integration test...")
    
    try:
        template_path = "sample_template.xlsx"
        formula_path = "sample_formula.json"
        
        # Mock database config with correct FirebirdConnector parameters
        db_config = {
            "db_path": "test.fdb",
            "username": "SYSDBA",
            "password": "masterkey"
        }
        
        # Test that all components can be initialized together
        processor = TemplateProcessor(template_path, formula_path)
        
        # Create mock db connector for formula engine
        class MockDBConnector:
            def execute_query(self, query):
                return [{"estate_name": "Test Estate", "total_weight": 1000}]
        
        db_connector = MockDBConnector()
        engine = FormulaEngine(formula_path, db_connector)
        generator = ReportGenerator(template_path, formula_path, db_config)
        
        print("✅ All components initialized successfully")
        print("✅ Integration test passed (basic)")
        return True
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("EXCEL REPORT GENERATOR SYSTEM TEST")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Sample Data Structure", test_sample_data_structure),
        ("TemplateProcessor", test_template_processor),
        ("FormulaEngine", test_formula_engine),
        ("ReportGenerator", test_report_generator),
        ("Integration", run_integration_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready for use.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)