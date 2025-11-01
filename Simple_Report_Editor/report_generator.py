#!/usr/bin/env python3
"""
Report Generator - Main Report Generation Orchestrator
=====================================================

Mengkoordinasikan keseluruhan proses pembuatan laporan dari template:
1. Load template dan formula
2. Connect ke database
3. Eksekusi query dan proses data
4. Render template dengan data
5. Export ke Excel/PDF

Author: Claude AI Assistant
Version: 1.0.0
"""

import logging
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import modules
from firebird_connector import FirebirdConnector
from formula_engine import FormulaEngine
from template_processor import TemplateProcessor

class ReportGenerator:
    """
    Main orchestrator untuk report generation.

    Features:
    - Template-based report generation
    - Multi-format output (Excel, PDF)
    - Data processing dan aggregation
    - Error handling dan logging
    - Progress tracking
    """

    def __init__(self, config: Dict = None):
        """
        Initialize Report Generator

        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

        # Initialize components
        self.db_connector = None
        self.formula_engine = FormulaEngine(config)
        self.template_processor = TemplateProcessor()

        # Status tracking
        self.current_step = ""
        self.progress_callback = None

    def set_progress_callback(self, callback):
        """
        Set progress callback function

        Args:
            callback: Function to call with progress updates
        """
        self.progress_callback = callback

    def update_progress(self, step: str, progress: float) -> None:
        """
        Update progress dengan callback

        Args:
            step: Current step description
            progress: Progress percentage (0-100)
        """
        self.current_step = step
        if self.progress_callback:
            self.progress_callback(step, progress)

        self.logger.info(f"Progress: {step} ({progress:.1f}%)")

    def generate_report(self, template_path: str, formula_data: Dict,
                       db_params: Dict, report_params: Dict,
                       output_path: str = None, output_format: str = 'excel') -> str:
        """
        Generate laporan lengkap

        Args:
            template_path: Path ke template Excel
            formula_data: Formula configuration data
            db_params: Database connection parameters
            report_params: Report-specific parameters
            output_path: Output file path (optional)
            output_format: Output format ('excel' atau 'pdf')

        Returns:
            Path ke file yang di-generate
        """
        try:
            self.update_progress("Initializing report generation", 5)

            # Step 1: Validate inputs
            self.validate_inputs(template_path, formula_data, db_params)

            # Step 2: Setup database connection
            self.setup_database_connection(db_params)
            self.update_progress("Database connected", 15)

            # Step 3: Execute queries dan process data
            processed_data = self.process_data(formula_data, report_params)
            self.update_progress("Data processing completed", 60)

            # Step 4: Process template dengan data
            self.process_template_with_data(template_path, formula_data, processed_data)
            self.update_progress("Template processing completed", 80)

            # Step 5: Generate output file
            output_file = self.generate_output_file(output_path, output_format)
            self.update_progress("Report generation completed", 100)

            self.logger.info(f"Report generated successfully: {output_file}")
            return output_file

        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            raise

    def validate_inputs(self, template_path: str, formula_data: Dict, db_params: Dict) -> None:
        """
        Validate input parameters

        Args:
            template_path: Path ke template
            formula_data: Formula configuration
            db_params: Database parameters
        """
        # Validate template file
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")

        # Validate formula data
        if not formula_data or not isinstance(formula_data, dict):
            raise ValueError("Invalid formula data")

        required_formula_keys = ['queries', 'variables']
        for key in required_formula_keys:
            if key not in formula_data:
                raise ValueError(f"Missing required key in formula data: {key}")

        # Validate database parameters
        required_db_keys = ['database_path', 'username', 'password']
        for key in required_db_keys:
            if key not in db_params:
                raise ValueError(f"Missing required database parameter: {key}")

        if not os.path.exists(db_params['database_path']):
            raise FileNotFoundError(f"Database file not found: {db_params['database_path']}")

    def setup_database_connection(self, db_params: Dict) -> None:
        """
        Setup database connection

        Args:
            db_params: Database connection parameters
        """
        try:
            self.db_connector = FirebirdConnector(
                database_path=db_params['database_path'],
                username=db_params['username'],
                password=db_params['password']
            )

            # Test connection
            if not self.db_connector.test_connection():
                raise ConnectionError("Failed to connect to database")

            # Set connector untuk formula engine
            self.formula_engine.set_database_connector(self.db_connector)

            self.logger.info("Database connection established")

        except Exception as e:
            self.logger.error(f"Error setting up database connection: {e}")
            raise

    def process_data(self, formula_data: Dict, report_params: Dict) -> Dict:
        """
        Process data: execute queries dan process variables

        Args:
            formula_data: Formula configuration
            report_params: Report parameters

        Returns:
            Dictionary processed data
        """
        try:
            # Execute queries
            self.update_progress("Executing database queries", 20)
            query_results = self.formula_engine.execute_queries(formula_data, report_params)

            # Process variables
            self.update_progress("Processing variables and calculations", 40)
            processed_variables = self.formula_engine.process_variables(formula_data, query_results)

            # Combine results
            processed_data = {**query_results, **processed_variables}

            # Validate data
            self.validate_processed_data(processed_data, formula_data)

            return processed_data

        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
            raise

    def validate_processed_data(self, data: Dict, formula_data: Dict) -> None:
        """
        Validate processed data

        Args:
            data: Processed data
            formula_data: Formula configuration
        """
        validations = formula_data.get('validations', {})

        # Validate main data if exists
        if 'main_data' in data and data['main_data']:
            validation_errors = self.formula_engine.validate_data(
                data['main_data'],
                validations
            )

            if validation_errors:
                self.logger.warning(f"Data validation warnings: {validation_errors}")

        # Check required variables
        variables = formula_data.get('variables', {})
        for var_name, var_config in variables.items():
            if var_config.get('type') == 'constant':
                continue  # Constants are always available

            if var_name not in data:
                self.logger.warning(f"Variable not found in processed data: {var_name}")

    def process_template_with_data(self, template_path: str, formula_data: Dict, data: Dict) -> None:
        """
        Process template dengan data

        Args:
            template_path: Path ke template
            formula_data: Formula configuration
            data: Processed data
        """
        try:
            # Load template
            if not self.template_processor.load_template(template_path):
                raise RuntimeError("Failed to load template")

            # Get repeating sections configuration
            repeating_sections = formula_data.get('repeating_sections', {})

            # Process template
            self.update_progress("Rendering template with data", 70)
            if not self.template_processor.process_template(data, repeating_sections):
                raise RuntimeError("Failed to process template")

            self.logger.info("Template processed successfully")

        except Exception as e:
            self.logger.error(f"Error processing template: {e}")
            raise

    def generate_output_file(self, output_path: str = None, output_format: str = 'excel') -> str:
        """
        Generate output file

        Args:
            output_path: Output file path (optional)
            output_format: Output format

        Returns:
            Path ke file output
        """
        try:
            # Generate output filename if not provided
            if not output_path:
                output_path = self.generate_output_filename(output_format)

            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # Save based on format
            if output_format.lower() == 'excel':
                if not self.template_processor.save_workbook(output_path):
                    raise RuntimeError("Failed to save Excel file")
            elif output_format.lower() == 'pdf':
                # Convert to PDF (requires additional implementation)
                pdf_path = self.convert_to_pdf(output_path)
                output_path = pdf_path
            else:
                raise ValueError(f"Unsupported output format: {output_format}")

            return output_path

        except Exception as e:
            self.logger.error(f"Error generating output file: {e}")
            raise

    def generate_output_filename(self, output_format: str) -> str:
        """
        Generate output filename dengan timestamp

        Args:
            output_format: Output format

        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_format.lower() == 'excel':
            extension = '.xlsx'
        elif output_format.lower() == 'pdf':
            extension = '.pdf'
        else:
            extension = '.xlsx'

        # Get template name atau default
        template_info = getattr(self.template_processor, 'template_info', {})
        template_name = template_info.get('name', 'Report')

        # Clean filename
        safe_name = "".join(c for c in template_name if c.isalnum() or c in (' ', '-')).rstrip()
        filename = f"{safe_name}_{timestamp}{extension}"

        # Default output directory
        output_dir = self.config.get('output_settings', {}).get('default_output_dir', './reports')
        return os.path.join(output_dir, filename)

    def convert_to_pdf(self, excel_path: str) -> str:
        """
        Convert Excel to PDF (requires additional libraries)

        Args:
            excel_path: Path ke Excel file

        Returns:
            Path ke PDF file
        """
        try:
            # This would require additional libraries like win32com on Windows
            # For now, just return the Excel path
            self.logger.warning("PDF conversion not implemented, returning Excel file")
            return excel_path

        except Exception as e:
            self.logger.error(f"Error converting to PDF: {e}")
            return excel_path

    def get_template_preview(self, template_path: str, formula_data: Dict,
                           db_params: Dict, report_params: Dict,
                           limit: int = 100) -> Dict:
        """
        Get preview data untuk template

        Args:
            template_path: Path ke template
            formula_data: Formula configuration
            db_params: Database parameters
            report_params: Report parameters
            limit: Maximum records untuk preview

        Returns:
            Preview data dictionary
        """
        try:
            # Setup database connection
            if not self.db_connector:
                self.setup_database_connection(db_params)

            # Execute queries dengan limit
            modified_formula = self.apply_preview_limit(formula_data, limit)
            processed_data = self.process_data(modified_formula, report_params)

            # Get template info
            template_info = self.get_template_information(template_path)

            return {
                'template_info': template_info,
                'data_preview': processed_data,
                'record_counts': self.get_record_counts(processed_data)
            }

        except Exception as e:
            self.logger.error(f"Error getting template preview: {e}")
            raise

    def apply_preview_limit(self, formula_data: Dict, limit: int) -> Dict:
        """
        Apply limit ke queries untuk preview

        Args:
            formula_data: Original formula data
            limit: Record limit

        Returns:
            Modified formula data
        """
        modified_formula = json.loads(json.dumps(formula_data))  # Deep copy

        queries = modified_formula.get('queries', {})

        for query_name, query_config in queries.items():
            sql = query_config.get('sql', '')

            # Add FIRST {limit} to SELECT statements
            if sql.upper().startswith('SELECT '):
                # Simple addition - might need more sophisticated SQL parsing
                if 'FIRST' not in sql.upper():
                    sql = sql.replace('SELECT', f'SELECT FIRST {limit}', 1)
                    query_config['sql'] = sql

        return modified_formula

    def get_template_information(self, template_path: str) -> Dict:
        """
        Get template information

        Args:
            template_path: Path ke template

        Returns:
            Template information dictionary
        """
        try:
            # Load template temporarily
            temp_processor = TemplateProcessor()
            if temp_processor.load_template(template_path):
                return temp_processor.get_template_info()
            else:
                return {}

        except Exception as e:
            self.logger.error(f"Error getting template information: {e}")
            return {}

    def get_record_counts(self, data: Dict) -> Dict:
        """
        Get record counts untuk setiap data source

        Args:
            data: Processed data

        Returns:
            Record counts dictionary
        """
        counts = {}

        for key, value in data.items():
            if isinstance(value, list):
                counts[key] = len(value)
            elif isinstance(value, dict):
                counts[key] = 1
            else:
                counts[key] = 1 if value is not None else 0

        return counts

    def export_raw_data(self, output_path: str, data: Dict, format_type: str = 'excel') -> bool:
        """
        Export raw data tanpa template processing

        Args:
            output_path: Output file path
            data: Data to export
            format_type: Export format

        Returns:
            True jika berhasil
        """
        try:
            # Create temporary formula engine for export
            temp_engine = FormulaEngine()
            temp_engine.query_results = {k: v for k, v in data.items() if isinstance(v, list)}
            temp_engine.processed_variables = {k: v for k, v in data.items() if not isinstance(v, list)}

            return temp_engine.export_results(output_path, format_type)

        except Exception as e:
            self.logger.error(f"Error exporting raw data: {e}")
            return False

    def validate_report_configuration(self, formula_data: Dict) -> List[str]:
        """
        Validate report configuration

        Args:
            formula_data: Formula configuration

        Returns:
            List validation issues
        """
        issues = []

        # Check required sections
        required_sections = ['queries', 'variables']
        for section in required_sections:
            if section not in formula_data:
                issues.append(f"Missing required section: {section}")

        # Check queries
        queries = formula_data.get('queries', {})
        if not queries:
            issues.append("No queries defined")
        else:
            for query_name, query_config in queries.items():
                if not query_config.get('sql'):
                    issues.append(f"Query '{query_name}' missing SQL")

        # Check variables
        variables = formula_data.get('variables', {})
        if not variables:
            issues.append("No variables defined")

        return issues

    def get_estimated_processing_time(self, formula_data: Dict, db_params: Dict) -> Dict:
        """
        Estimate processing time berdasarkan configuration

        Args:
            formula_data: Formula configuration
            db_params: Database parameters

        Returns:
            Estimation dictionary
        """
        try:
            queries = formula_data.get('queries', {})
            num_queries = len(queries)

            # Base estimation (seconds)
            base_time = 2.0
            query_time = num_queries * 1.5
            processing_time = 1.0
            template_time = 2.0

            total_estimated = base_time + query_time + processing_time + template_time

            return {
                'total_seconds': total_estimated,
                'breakdown': {
                    'initialization': base_time,
                    'queries': query_time,
                    'processing': processing_time,
                    'template': template_time
                },
                'queries_count': num_queries
            }

        except Exception as e:
            self.logger.error(f"Error estimating processing time: {e}")
            return {'total_seconds': 30.0, 'breakdown': {}, 'queries_count': 0}