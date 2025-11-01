"""
Excel Report Generator Utama
Menggabungkan semua komponen untuk menghasilkan laporan Excel dari template
"""

import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from firebird_connector_enhanced import FirebirdConnectorEnhanced as FirebirdConnector
from template_processor import TemplateProcessor
from formula_engine import FormulaEngine

class ExcelReportGenerator:
    """
    Main report generator yang mengoordinasikan seluruh proses pembuatan laporan
    """

    def __init__(self, template_path: str = None, formula_path: str = None, estate_config_path: str = None):
        """
        Inisialisasi report generator

        Args:
            template_path: Path ke template Excel (default: Template_Laporan_FFB_Analysis.xlsx)
            formula_path: Path ke formula file (default: laporan_ffb_analysis_formula.json)
            estate_config_path: Path ke estate config (default: estate_config.json)
        """
        # Set default paths
        self.template_path = template_path or "Template_Laporan_FFB_Analysis.xlsx"
        self.formula_path = formula_path or "laporan_ffb_analysis_formula.json"
        self.estate_config_path = estate_config_path or "estate_config.json"

        # Setup logging
        self._setup_logging()

        # Initialize components
        self.template_processor = None
        self.formula_engine = None
        self.db_connector = None

        # Load estate configuration
        self.estate_config = self._load_estate_config()

        self.logger.info("Excel Report Generator initialized")

    def _setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler('report_generator.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_estate_config(self) -> Dict[str, str]:
        """Load estate configuration dari file JSON"""
        try:
            if os.path.exists(self.estate_config_path):
                with open(self.estate_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info(f"Loaded {len(config)} estates from config")
                return config
            else:
                # Create default config if not exists
                default_config = self._create_default_estate_config()
                with open(self.estate_config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                self.logger.info("Created default estate config file")
                return default_config
        except Exception as e:
            self.logger.error(f"Error loading estate config: {e}")
            return {}

    def _create_default_estate_config(self) -> Dict[str, str]:
        """Create default estate configuration"""
        return {
            "PGE 1A": "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB",
            "PGE 1B": "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1B\\PTRJ_P1B.FDB",
            "PGE 2A": "C:\\Users\\nbgmf\\Downloads\\IFESS_PGE_2A_19-06-2025",
            "PGE 2B": "C:\\Users\\nbgmf\\Downloads\\IFESS_2B_19-06-2025\\PTRJ_P2B.FDB",
            "IJL": "C:\\Users\\nbgmf\\Downloads\\IFESS_IJL_19-06-2025\\PTRJ_IJL_IMPIANJAYALESTARI.FDB",
            "DME": "C:\\Users\\nbgmf\\Downloads\\IFESS_DME_19-06-2025\\PTRJ_DME.FDB",
            "Are B2": "C:\\Users\\nbgmf\\Downloads\\IFESS_ARE_B2_19-06-2025\\PTRJ_AB2.FDB",
            "Are B1": "C:\\Users\\nbgmf\\Downloads\\IFESS_ARE_B1_19-06-2025\\PTRJ_AB1.FDB",
            "Are A": "C:\\Users\\nbgmf\\Downloads\\IFESS_ARE_A_19-06-2025\\PTRJ_ARA.FDB",
            "Are C": "C:\\Users\\nbgmf\\Downloads\\IFESS_ARE_C_19-06-2025\\PTRJ_ARC.FDB"
        }

    def generate_report(self,
                       start_date: str,
                       end_date: str,
                       selected_estates: List[str],
                       output_dir: str = "reports") -> Tuple[bool, List[str]]:
        """
        Generate laporan untuk multiple estates

        Args:
            start_date: Tanggal mulai (YYYY-MM-DD atau DD/MM/YYYY)
            end_date: Tanggal akhir (YYYY-MM-DD atau DD/MM/YYYY)
            selected_estates: List estate yang akan diproses
            output_dir: Directory untuk output files

        Returns:
            Tuple (success, list of output files)
        """
        try:
            # Validate inputs
            validation_result = self._validate_inputs(start_date, end_date, selected_estates)
            if not validation_result[0]:
                return False, validation_result[1]

            # Normalize date format
            start_date = self._normalize_date(start_date)
            end_date = self._normalize_date(end_date)

            # Create output directory
            os.makedirs(output_dir, exist_ok=True)

            # Initialize template processor
            self._initialize_components()

            output_files = []
            errors = []

            # Generate report untuk setiap estate
            for estate_name in selected_estates:
                try:
                    self.logger.info(f"Generating report for estate: {estate_name}")

                    # Get estate database path
                    db_path = self.estate_config.get(estate_name)
                    if not db_path or not os.path.exists(db_path):
                        error_msg = f"Database path not found for estate {estate_name}: {db_path}"
                        self.logger.error(error_msg)
                        errors.append(error_msg)
                        continue

                    # Generate single estate report
                    output_file = self._generate_single_estate_report(
                        estate_name, db_path, start_date, end_date, output_dir
                    )

                    if output_file:
                        output_files.append(output_file)
                        self.logger.info(f"Report generated successfully: {output_file}")
                    else:
                        error_msg = f"Failed to generate report for estate {estate_name}"
                        errors.append(error_msg)

                except Exception as e:
                    error_msg = f"Error generating report for estate {estate_name}: {e}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)

            # Generate consolidated report if multiple estates
            if len(selected_estates) > 1 and len(output_files) > 0:
                try:
                    consolidated_file = self._generate_consolidated_report(
                        selected_estates, start_date, end_date, output_dir
                    )
                    if consolidated_file:
                        output_files.append(consolidated_file)
                except Exception as e:
                    error_msg = f"Error generating consolidated report: {e}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)

            success = len(output_files) > 0
            return success, output_files if success else errors

        except Exception as e:
            self.logger.error(f"Error in generate_report: {e}")
            return False, [str(e)]

    def _validate_inputs(self, start_date: str, end_date: str, selected_estates: List[str]) -> Tuple[bool, List[str]]:
        """Validate input parameters"""
        errors = []

        # Validate date format
        try:
            self._normalize_date(start_date)
            self._normalize_date(end_date)
        except ValueError as e:
            errors.append(f"Invalid date format: {e}")

        # Validate estate selection
        if not selected_estates:
            errors.append("No estates selected")
        else:
            for estate in selected_estates:
                if estate not in self.estate_config:
                    errors.append(f"Estate {estate} not found in configuration")

        # Validate required files
        if not os.path.exists(self.template_path):
            errors.append(f"Template file not found: {self.template_path}")

        if not os.path.exists(self.formula_path):
            errors.append(f"Formula file not found: {self.formula_path}")

        return len(errors) == 0, errors

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string ke YYYY-MM-DD format"""
        if not date_str:
            raise ValueError("Date cannot be empty")

        # Try different date formats
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']

        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue

        raise ValueError(f"Unrecognized date format: {date_str}")

    def _initialize_components(self):
        """Initialize semua komponen"""
        try:
            # Initialize template processor
            self.template_processor = TemplateProcessor(self.template_path, self.formula_path)

            # Formula engine akan diinitialize per estate karena database connection berbeda
            self.logger.info("Components initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            raise

    def _generate_single_estate_report(self,
                                     estate_name: str,
                                     db_path: str,
                                     start_date: str,
                                     end_date: str,
                                     output_dir: str) -> Optional[str]:
        """Generate report untuk single estate"""
        try:
            # Initialize database connection
            self.db_connector = FirebirdConnector(db_path=db_path)

            # Test connection
            if not self.db_connector.test_connection():
                self.logger.error(f"Failed to connect to database: {db_path}")
                return None

            # Initialize formula engine
            self.formula_engine = FormulaEngine(self.formula_path, self.db_connector)

            # Prepare parameters
            parameters = {
                'start_date': start_date,
                'end_date': end_date,
                'estate_name': estate_name,
                'estate_code': estate_name.replace(' ', '_')
            }

            # Execute all queries
            self.logger.info(f"Executing queries for estate {estate_name}")
            query_results = self.formula_engine.execute_all_queries(parameters)

            # Process variables
            self.logger.info("Processing variables")
            variables = self.formula_engine.process_variables(query_results, parameters)

            # Calculate derived metrics
            derived_metrics = self.formula_engine.calculate_derived_metrics({
                **parameters,
                **query_results,
                **variables
            })

            # Merge all data
            all_data = {
                **parameters,
                **variables,
                **derived_metrics,
                **query_results
            }

            # Validate data
            validation = self.formula_engine.validate_data(all_data)
            if not validation['is_valid']:
                self.logger.warning(f"Data validation failed: {validation['errors']}")

            # Create new template instance
            template_instance = self.template_processor.create_copy()

            # Process placeholders
            self.logger.info("Processing template placeholders")
            for sheet_name in template_instance.workbook.sheetnames:
                template_instance.process_sheet_placeholders(sheet_name, all_data)

            # Process repeating sections
            self.logger.info("Processing repeating sections")
            repeating_sections = self.formula_engine.formulas.get('repeating_sections', {})
            for section_name, section_config in repeating_sections.items():
                sheet_name = section_config.get('sheet_name')
                if sheet_name:
                    data = self.formula_engine.process_repeating_section_data(section_name, query_results)
                    if data:
                        template_instance.process_repeating_section(sheet_name, data)

            # Generate output filename
            output_filename = f"Laporan_FFB_Analysis_{estate_name.replace(' ', '_')}_{start_date}_{end_date}.xlsx"
            output_path = os.path.join(output_dir, output_filename)

            # Save report
            template_instance.save_processed_template(output_path)

            self.logger.info(f"Report saved: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Error generating report for estate {estate_name}: {e}")
            return None

    def _generate_consolidated_report(self,
                                    selected_estates: List[str],
                                    start_date: str,
                                    end_date: str,
                                    output_dir: str) -> Optional[str]:
        """Generate consolidated report untuk multiple estates"""
        try:
            # Create consolidated template
            template_instance = self.template_processor.create_copy()

            # Prepare consolidated data
            consolidated_data = {
                'start_date': start_date,
                'end_date': end_date,
                'report_title': f'LAPORAN ANALISIS FFB - KONSOLIDASI {len(selected_estates)} ESTATES',
                'report_period': f'Periode: {start_date} s/d {end_date}',
                'generated_date': datetime.now().strftime('%d %B %Y'),
                'generated_time': datetime.now().strftime('%H:%M:%S')
            }

            # Process dashboard sheet with consolidated info
            dashboard_sheet = template_instance.workbook['Dashboard']
            dashboard_sheet['A1'] = consolidated_data['report_title']
            dashboard_sheet['A2'] = consolidated_data['report_period']
            dashboard_sheet['A3'] = f"Estates: {', '.join(selected_estates)}"

            # Create summary sheet for all estates
            summary_sheet = template_instance.workbook.create_sheet("Konsolidasi")

            # Add headers
            headers = ['Estate', 'Total Transaksi', 'Total Ripe', 'Total Unripe', 'Quality %', 'Verification %']
            for i, header in enumerate(headers, 1):
                cell = summary_sheet.cell(row=1, column=i, value=header)
                cell.font = cell.font.copy(bold=True)

            # Add estate data (simplified for demo)
            for i, estate in enumerate(selected_estates, 2):
                summary_sheet.cell(row=i, column=1, value=estate)
                summary_sheet.cell(row=i, column=2, value=0)  # Placeholder
                summary_sheet.cell(row=i, column=3, value=0)  # Placeholder
                summary_sheet.cell(row=i, column=4, value=0)  # Placeholder
                summary_sheet.cell(row=i, column=5, value=0)  # Placeholder
                summary_sheet.cell(row=i, column=6, value=0)  # Placeholder

            # Save consolidated report
            output_filename = f"Laporan_FFB_Analysis_Konsolidasi_{start_date}_{end_date}.xlsx"
            output_path = os.path.join(output_dir, output_filename)

            template_instance.save_processed_template(output_path)

            self.logger.info(f"Consolidated report saved: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Error generating consolidated report: {e}")
            return None

    def get_available_estates(self) -> List[str]:
        """Get list of available estates from configuration"""
        return list(self.estate_config.keys())

    def get_template_info(self) -> Dict[str, Any]:
        """Get template information"""
        try:
            if os.path.exists(self.template_path):
                template_processor = TemplateProcessor(self.template_path, self.formula_path)
                return template_processor.get_template_info()
            else:
                return {'error': 'Template file not found'}
        except Exception as e:
            return {'error': str(e)}

    def test_database_connection(self, estate_name: str) -> bool:
        """Test database connection untuk estate tertentu"""
        try:
            if estate_name not in self.estate_config:
                return False

            db_path = self.estate_config[estate_name]
            if not os.path.exists(db_path):
                return False

            connector = FirebirdConnector(db_path=db_path)
            return connector.test_connection()
        except Exception as e:
            self.logger.error(f"Error testing connection for {estate_name}: {e}")
            return False

    def preview_data(self,
                    estate_name: str,
                    start_date: str,
                    end_date: str,
                    limit: int = 10) -> Dict[str, Any]:
        """Preview data untuk estate tertentu"""
        try:
            if estate_name not in self.estate_config:
                return {'error': f'Estate {estate_name} not found in configuration'}

            db_path = self.estate_config[estate_name]
            if not os.path.exists(db_path):
                return {'error': f'Database file not found: {db_path}'}

            # Initialize connection
            self.db_connector = FirebirdConnector(db_path=db_path)
            self.formula_engine = FormulaEngine(self.formula_path, self.db_connector)

            # Prepare parameters
            parameters = {
                'start_date': self._normalize_date(start_date),
                'end_date': self._normalize_date(end_date),
                'estate_name': estate_name
            }

            # Execute limited queries for preview
            daily_performance_query = self.formula_engine.formulas['queries']['daily_performance']['sql']
            daily_performance_query += f" FETCH FIRST {limit} ROWS ONLY"

            preview_data = {
                'connection_test': self.db_connector.test_connection(),
                'sample_data': {
                    'daily_performance': self.db_connector.execute_query(daily_performance_query, parameters, 'dict')
                }
            }

            return preview_data

        except Exception as e:
            self.logger.error(f"Error in preview_data: {e}")
            return {'error': str(e)}

def main():
    """Main function untuk testing"""
    generator = ExcelReportGenerator()

    # Test dengan sample data
    estates = generator.get_available_estates()
    print(f"Available estates: {estates}")

    if estates:
        # Generate sample report
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        selected_estates = [estates[0]]  # Test dengan 1 estate

        success, results = generator.generate_report(start_date, end_date, selected_estates)

        if success:
            print(f"Report generated successfully: {results}")
        else:
            print(f"Report generation failed: {results}")

if __name__ == "__main__":
    main()