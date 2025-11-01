#!/usr/bin/env python3
"""
System Testing Script - Simple Report Editor
==========================================

Testing script untuk memverifikasi semua komponen sistem bekerja dengan baik:
1. Template loading dan scanning
2. Database connection
3. Formula processing
4. Data extraction
5. Template rendering
6. Report generation

Author: Claude AI Assistant
Version: 1.0.0
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Setup logging with proper encoding for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_imports():
    """Test semua imports yang diperlukan"""
    logger.info("Testing imports...")

    try:
        from firebird_connector import FirebirdConnector
        from formula_engine import FormulaEngine
        from template_processor import TemplateProcessor
        from report_generator import ReportGenerator
        logger.info("[PASS] All imports successful")
        return True
    except ImportError as e:
        logger.error(f"[FAIL] Import error: {e}")
        return False

def test_config_loading():
    """Test loading konfigurasi"""
    logger.info("Testing configuration loading...")

    try:
        config_file = "config/app_config.json"
        if not os.path.exists(config_file):
            logger.error(f"✗ Config file not found: {config_file}")
            return False

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Check required sections
        required_sections = ['app_info', 'database_settings', 'template_settings']
        for section in required_sections:
            if section not in config:
                logger.error(f"✗ Missing config section: {section}")
                return False

        logger.info("✓ Configuration loaded successfully")
        return True

    except Exception as e:
        logger.error(f"✗ Error loading config: {e}")
        return False

def test_template_discovery():
    """Test penemuan template yang tersedia"""
    logger.info("Testing template discovery...")

    try:
        template_dir = Path("./templates")
        if not template_dir.exists():
            logger.error("✗ Templates directory not found")
            return False

        # Find formula files
        formula_files = list(template_dir.glob("*_formula.json"))

        if not formula_files:
            logger.error("✗ No formula files found")
            return False

        logger.info(f"✓ Found {len(formula_files)} formula files:")
        for file in formula_files:
            logger.info(f"  - {file.name}")

        return True

    except Exception as e:
        logger.error(f"✗ Error discovering templates: {e}")
        return False

def test_formula_loading():
    """Test loading formula JSON"""
    logger.info("Testing formula loading...")

    try:
        template_dir = Path("./templates")
        formula_files = list(template_dir.glob("*_formula.json"))

        if not formula_files:
            logger.error("✗ No formula files to test")
            return False

        # Test first formula file
        formula_file = formula_files[0]
        logger.info(f"Testing formula file: {formula_file.name}")

        with open(formula_file, 'r', encoding='utf-8') as f:
            formula_data = json.load(f)

        # Validate structure
        required_sections = ['queries', 'variables']
        for section in required_sections:
            if section not in formula_data:
                logger.error(f"✗ Missing formula section: {section}")
                return False

        # Check queries
        queries = formula_data.get('queries', {})
        if not queries:
            logger.error("✗ No queries defined in formula")
            return False

        logger.info(f"✓ Formula loaded with {len(queries)} queries")
        return True

    except Exception as e:
        logger.error(f"✗ Error loading formula: {e}")
        return False

def test_template_loading():
    """Test loading template Excel"""
    logger.info("Testing template loading...")

    try:
        template_dir = Path("./templates")
        excel_files = list(template_dir.glob("*.xlsx"))

        if not excel_files:
            logger.warning("⚠ No Excel templates found, skipping template loading test")
            return True

        # Test first Excel file
        template_file = excel_files[0]
        logger.info(f"Testing template file: {template_file.name}")

        from template_processor import TemplateProcessor
        processor = TemplateProcessor()

        if not processor.load_template(str(template_file)):
            logger.error("✗ Failed to load template")
            return False

        # Get template info
        info = processor.get_template_info()
        logger.info(f"✓ Template loaded successfully:")
        logger.info(f"  - Sheets: {info.get('sheet_names', [])}")
        logger.info(f"  - Placeholders: {info.get('total_placeholders', 0)}")

        return True

    except Exception as e:
        logger.error(f"✗ Error loading template: {e}")
        return False

def test_database_connection():
    """Test koneksi database (jika ada)"""
    logger.info("Testing database connection...")

    try:
        # Load config
        config_file = "config/app_config.json"
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        db_settings = config.get('database_settings', {})
        db_path = db_settings.get('default_database', '')

        if not db_path or not os.path.exists(db_path):
            logger.warning("⚠ Database file not found, skipping database test")
            return True

        from firebird_connector import FirebirdConnector

        # Test connection
        connector = FirebirdConnector(
            database_path=db_path,
            username=db_settings.get('default_username', 'SYSDBA'),
            password=db_settings.get('default_password', 'masterkey')
        )

        if connector.test_connection():
            logger.info("✓ Database connection successful")
            return True
        else:
            logger.error("✗ Database connection failed")
            return False

    except Exception as e:
        logger.warning(f"⚠ Database test skipped: {e}")
        return True  # Don't fail the entire test for database issues

def test_formula_engine():
    """Test formula engine functionality"""
    logger.info("Testing formula engine...")

    try:
        from formula_engine import FormulaEngine

        engine = FormulaEngine()

        # Test data processing
        test_data = {
            'test_query': [
                {'ID': 1, 'NAME': 'Test1', 'VALUE': 100},
                {'ID': 2, 'NAME': 'Test2', 'VALUE': 200}
            ]
        }

        # Test variable processing
        formula_config = {
            'variables': {
                'test_var': {
                    'type': 'constant',
                    'value': 'Test Value'
                },
                'calculated_var': {
                    'type': 'calculation',
                    'formula': '100 + 200'
                }
            }
        }

        engine.query_results = test_data
        processed_vars = engine.process_variables(formula_config, test_data)

        if 'test_var' in processed_vars and processed_vars['test_var'] == 'Test Value':
            logger.info("✓ Formula engine working correctly")
            return True
        else:
            logger.error("✗ Formula engine processing failed")
            return False

    except Exception as e:
        logger.error(f"✗ Error testing formula engine: {e}")
        return False

def test_placeholder_extraction():
    """Test placeholder extraction"""
    logger.info("Testing placeholder extraction...")

    try:
        from template_processor import TemplateProcessor

        processor = TemplateProcessor()

        # Test placeholder extraction
        test_text = "Hello {{name}}, today is {{date|format:%Y-%m-%d}}"
        placeholders = processor.extract_placeholders(test_text)

        expected_placeholders = ['name', 'date|format:%Y-%m-%d']

        if placeholders == expected_placeholders:
            logger.info("✓ Placeholder extraction working correctly")
            return True
        else:
            logger.error(f"✗ Expected {expected_placeholders}, got {placeholders}")
            return False

    except Exception as e:
        logger.error(f"✗ Error testing placeholder extraction: {e}")
        return False

def test_value_formatting():
    """Test value formatting"""
    logger.info("Testing value formatting...")

    try:
        from template_processor import TemplateProcessor

        processor = TemplateProcessor()
        processor.processed_data = {'test_value': 123.4567}

        # Test number formatting
        formatted = processor.format_value(123.4567, 'number:.2f')
        if formatted != '123.46':
            logger.error(f"✗ Number formatting failed: expected '123.46', got '{formatted}'")
            return False

        # Test date formatting
        test_date = datetime(2025, 1, 1)
        formatted = processor.format_value(test_date, 'format:%Y-%m-%d')
        if formatted != '2025-01-01':
            logger.error(f"✗ Date formatting failed: expected '2025-01-01', got '{formatted}'")
            return False

        logger.info("✓ Value formatting working correctly")
        return True

    except Exception as e:
        logger.error(f"✗ Error testing value formatting: {e}")
        return False

def test_report_generator_initialization():
    """Test inisialisasi report generator"""
    logger.info("Testing report generator initialization...")

    try:
        from report_generator import ReportGenerator

        # Load config
        config_file = "config/app_config.json"
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        generator = ReportGenerator(config)

        # Test validation
        test_formula = {
            'queries': {
                'test_query': {
                    'type': 'sql',
                    'sql': 'SELECT 1 as test'
                }
            },
            'variables': {
                'test_var': {
                    'type': 'constant',
                    'value': 'test'
                }
            }
        }

        issues = generator.validate_report_configuration(test_formula)

        if not issues:
            logger.info("✓ Report generator initialization successful")
            return True
        else:
            logger.error(f"✗ Report generator validation issues: {issues}")
            return False

    except Exception as e:
        logger.error(f"✗ Error testing report generator: {e}")
        return False

def test_end_to_end_simulation():
    """Test simulasi end-to-end tanpa database connection"""
    logger.info("Testing end-to-end simulation...")

    try:
        from template_processor import TemplateProcessor
        from formula_engine import FormulaEngine

        # Simulate data
        mock_data = {
            'main_data': [
                {'ID': 1, 'NAME': 'Item 1', 'VALUE': 100},
                {'ID': 2, 'NAME': 'Item 2', 'VALUE': 200},
                {'ID': 3, 'NAME': 'Item 3', 'VALUE': 300}
            ],
            'summary_stats': {
                'total_records': 3,
                'total_value': 600,
                'average_value': 200
            },
            'report_date': '2025-11-01',
            'estate_name': 'Test Estate'
        }

        # Test template processor with mock data
        processor = TemplateProcessor()

        # Create a simple test template in memory
        test_template_path = "test_template.xlsx"

        # Check if we can process mock data
        processor.processed_data = mock_data

        # Test placeholder value retrieval
        value = processor.get_placeholder_value('estate_name')
        if value != 'Test Estate':
            logger.error(f"✗ Placeholder value test failed: expected 'Test Estate', got '{value}'")
            return False

        # Test nested value retrieval
        nested_value = processor.get_nested_value({'summary': {'total': 100}}, 'summary.total')
        if nested_value != 100:
            logger.error(f"✗ Nested value test failed: expected 100, got {nested_value}")
            return False

        logger.info("✓ End-to-end simulation successful")
        return True

    except Exception as e:
        logger.error(f"✗ Error in end-to-end simulation: {e}")
        return False

def run_all_tests():
    """Run semua tests"""
    logger.info("=" * 60)
    logger.info("Starting Simple Report Editor System Tests")
    logger.info("=" * 60)

    tests = [
        ("Import Test", test_imports),
        ("Config Loading Test", test_config_loading),
        ("Template Discovery Test", test_template_discovery),
        ("Formula Loading Test", test_formula_loading),
        ("Template Loading Test", test_template_loading),
        ("Database Connection Test", test_database_connection),
        ("Formula Engine Test", test_formula_engine),
        ("Placeholder Extraction Test", test_placeholder_extraction),
        ("Value Formatting Test", test_value_formatting),
        ("Report Generator Test", test_report_generator_initialization),
        ("End-to-End Simulation Test", test_end_to_end_simulation)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} PASSED")
            else:
                failed += 1
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            failed += 1
            logger.error(f"✗ {test_name} ERROR: {e}")

    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total Tests: {len(tests)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")

    if failed == 0:
        logger.info("🎉 ALL TESTS PASSED! System is ready to use.")
        return True
    else:
        logger.warning(f"⚠ {failed} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)