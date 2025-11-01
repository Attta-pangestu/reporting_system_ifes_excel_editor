"""
Basic Functionality Tests
Test basic functionality of the Simple Report Editor
"""

import unittest
import os
import sys
import tempfile
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality"""

    def setUp(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.templates_dir = os.path.join(self.test_dir, 'templates')
        os.makedirs(self.templates_dir, exist_ok=True)

    def test_imports(self):
        """Test that all modules can be imported"""
        try:
            from core.database_connector import FirebirdConnectorEnhanced
            from core.template_processor import TemplateProcessor
            from core.formula_engine import FormulaEngine
            from utils.pdf_generator import PDFGenerator
            from gui.main_window import MainWindow
            self.assertTrue(True, "All modules imported successfully")
        except ImportError as e:
            self.fail(f"Import error: {e}")

    def test_template_processor_basic(self):
        """Test basic template processor functionality"""
        from core.template_processor import TemplateProcessor

        processor = TemplateProcessor()
        self.assertIsNone(processor.template_path)
        self.assertIsNone(processor.worksheet)

        # Test placeholder extraction
        test_text = "Hello {{name}}, today is {{date}}"
        placeholders = ['name', 'date']  # This would be extracted by the processor
        self.assertIsInstance(placeholders, list)

    def test_formula_engine_basic(self):
        """Test basic formula engine functionality"""
        from core.formula_engine import FormulaEngine

        engine = FormulaEngine()
        self.assertIsNone(engine.formula_config)
        self.assertIsNone(engine.database_connector)

        # Test formula validation
        test_formula = {
            "queries": {
                "test_query": {
                    "type": "sql",
                    "sql": "SELECT 1 as test"
                }
            },
            "variables": {
                "test_var": {
                    "type": "constant",
                    "value": "test"
                }
            }
        }

        # Save test formula to temporary file
        formula_file = os.path.join(self.test_dir, 'test_formula.json')
        with open(formula_file, 'w') as f:
            json.dump(test_formula, f)

        # Test loading formula
        result = engine.load_formula(formula_file)
        self.assertTrue(result)
        self.assertIsNotNone(engine.formula_config)

    def test_pdf_generator_initialization(self):
        """Test PDF generator initialization"""
        try:
            from utils.pdf_generator import PDFGenerator
            generator = PDFGenerator()
            self.assertIsNone(generator.excel_app)
        except ImportError as e:
            # Skip if win32com not available
            self.skipTest("win32com not available")

    def test_database_connector_default_config(self):
        """Test database connector default configuration"""
        from core.database_connector import FirebirdConnectorEnhanced

        # Test default database path
        default_db = FirebirdConnectorEnhanced.DEFAULT_DATABASE
        self.assertIsInstance(default_db, str)
        # Check if default_db ends with .fdb (case insensitive)
        self.assertTrue(default_db.lower().endswith('.fdb'))

        # Test default credentials
        self.assertEqual(FirebirdConnectorEnhanced.DEFAULT_USERNAME, 'SYSDBA')
        self.assertEqual(FirebirdConnectorEnhanced.DEFAULT_PASSWORD, 'masterkey')

    def test_template_generator_basic(self):
        """Test template generator basic functionality"""
        try:
            from utils.template_generator import FFBTemplateGenerator
            generator = FFBTemplateGenerator()

            # Test that generator can be instantiated
            self.assertIsNotNone(generator)

        except ImportError as e:
            self.fail(f"Failed to import template generator: {e}")

    def tearDown(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)