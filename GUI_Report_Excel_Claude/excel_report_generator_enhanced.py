"""
Enhanced Excel Report Generator Utama
Menggabungkan semua komponen enhanced untuk menghasilkan laporan Excel dari template dengan debug logging
"""

import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from firebird_connector_enhanced import FirebirdConnectorEnhanced as FirebirdConnector
from template_processor_enhanced import TemplateProcessorEnhanced
from formula_engine_enhanced import FormulaEngineEnhanced

class ExcelReportGeneratorEnhanced:
    """
    Enhanced report generator dengan debug logging dan perbaikan processing
    """

    def __init__(self, template_path: str = None, formula_path: str = None, estate_config_path: str = None):
        """
        Inisialisasi enhanced report generator

        Args:
            template_path: Path ke template Excel (default: Template_Laporan_FFB_Analysis.xlsx)
            formula_path: Path ke formula file (default: laporan_ffb_analysis_formula.json)
            estate_config_path: Path ke estate config (default: estate_config.json)
        """
        # Set default paths
        self.template_path = template_path or "Template_Laporan_FFB_Analysis.xlsx"
        self.formula_path = formula_path or "laporan_ffb_analysis_formula.json"
        self.estate_config_path = estate_config_path or "estate_config.json"

        # Setup enhanced logging
        self._setup_enhanced_logging()

        # Initialize components
        self.template_processor = None
        self.formula_engine = None
        self.db_connector = None

        # Load estate configuration
        self.estate_config = self._load_estate_config()

        self.logger.info("Enhanced Excel Report Generator initialized")

    def _setup_enhanced_logging(self):
        """Setup enhanced logging dengan debug detail"""
        self.logger = logging.getLogger(f"{__name__}_enhanced")
        self.logger.setLevel(logging.DEBUG)

        # Create console handler if not exists
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)

            # Create detailed formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            self.logger.propagate = False

    def _load_estate_config(self) -> Dict[str, str]:
        """Load estate configuration dari file JSON dengan debug"""
        try:
            self.logger.info(f"Loading estate config from: {self.estate_config_path}")

            if os.path.exists(self.estate_config_path):
                with open(self.estate_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info(f"Loaded {len(config)} estates from config file")
                return config
            else:
                # Create default config if not exists
                self.logger.warning("Estate config file not found, creating default")
                default_config = self._create_default_estate_config()
                with open(self.estate_config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                self.logger.info("Created default estate config file")
                return default_config

        except Exception as e:
            self.logger.error(f"Error loading estate config: {e}", exc_info=True)
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
        Generate laporan untuk multiple estates dengan enhanced debugging

        Args:
            start_date: Tanggal mulai (YYYY-MM-DD atau DD/MM/YYYY)
            end_date: Tanggal akhir (YYYY-MM-DD atau DD/MM/YYYY)
            selected_estates: List estate yang akan diproses
            output_dir: Directory untuk output files

        Returns:
            Tuple (success, list of output files)
        """
        try:
            self.logger.info("=== STARTING ENHANCED REPORT GENERATION ===")
            self.logger.info(f"Start date: {start_date}")
            self.logger.info(f"End date: {end_date}")
            self.logger.info(f"Selected estates: {selected_estates}")
            self.logger.info(f"Output directory: {output_dir}")

            # Validate inputs
            validation_result = self._validate_inputs(start_date, end_date, selected_estates)
            if not validation_result[0]:
                self.logger.error(f"Input validation failed: {validation_result[1]}")
                return False, validation_result[1]

            # Normalize date format
            start_date = self._normalize_date(start_date)
            end_date = self._normalize_date(end_date)

            self.logger.info(f"Normalized dates - Start: {start_date}, End: {end_date}")

            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            self.logger.info(f"Output directory ready: {output_dir}")

            # Initialize template processor
            self._initialize_components()

            output_files = []
            errors = []

            # Generate report untuk setiap estate
            for i, estate_name in enumerate(selected_estates, 1):
                try:
                    self.logger.info(f"=== PROCESSING ESTATE {i}/{len(selected_estates)}: {estate_name} ===")

                    # Get estate database path
                    db_path = self.estate_config.get(estate_name)
                    if not db_path:
                        error_msg = f"No database path configured for estate {estate_name}"
                        self.logger.error(error_msg)
                        errors.append(error_msg)
                        continue

                    self.logger.info(f"Estate {estate_name} database path: {db_path}")

                    # Handle directory database paths (like PGE 2A)
                    if os.path.isdir(db_path):
                        self.logger.info(f"Database path is a directory, looking for .FDB file")
                        for file in os.listdir(db_path):
                            if file.upper().endswith('.FDB'):
                                db_path = os.path.join(db_path, file)
                                self.logger.info(f"Found database file: {db_path}")
                                break
                        else:
                            error_msg = f"No .FDB file found in directory {db_path}"
                            self.logger.error(error_msg)
                            errors.append(error_msg)
                            continue

                    if not os.path.exists(db_path):
                        error_msg = f"Database file not found: {db_path}"
                        self.logger.error(error_msg)
                        errors.append(error_msg)
                        continue

                    # Generate single estate report
                    output_file = self._generate_single_estate_report(
                        estate_name, db_path, start_date, end_date, output_dir
                    )

                    if output_file:
                        output_files.append(output_file)
                        self.logger.info(f"✓ Report generated successfully: {output_file}")
                    else:
                        error_msg = f"Failed to generate report for estate {estate_name}"
                        self.logger.error(f"✗ {error_msg}")
                        errors.append(error_msg)

                except Exception as e:
                    error_msg = f"Error generating report for estate {estate_name}: {e}"
                    self.logger.error(f"✗ {error_msg}", exc_info=True)
                    errors.append(error_msg)

            # Generate consolidated report if multiple estates
            if len(selected_estates) > 1 and len(output_files) > 0:
                try:
                    self.logger.info("=== GENERATING CONSOLIDATED REPORT ===")
                    consolidated_file = self._generate_consolidated_report(
                        selected_estates, start_date, end_date, output_dir
                    )
                    if consolidated_file:
                        output_files.append(consolidated_file)
                        self.logger.info(f"✓ Consolidated report generated: {consolidated_file}")
                except Exception as e:
                    error_msg = f"Error generating consolidated report: {e}"
                    self.logger.error(f"✗ {error_msg}", exc_info=True)
                    errors.append(error_msg)

            success = len(output_files) > 0
            self.logger.info(f"=== REPORT GENERATION COMPLETED ===")
            self.logger.info(f"Success: {success}, Generated files: {len(output_files)}, Errors: {len(errors)}")

            if success:
                self.logger.info("Generated files:")
                for file in output_files:
                    self.logger.info(f"  - {file}")

            if errors:
                self.logger.warning("Errors encountered:")
                for error in errors:
                    self.logger.warning(f"  - {error}")

            return success, output_files if success else errors

        except Exception as e:
            self.logger.error(f"Fatal error in generate_report: {e}", exc_info=True)
            return False, [str(e)]

    def _validate_inputs(self, start_date: str, end_date: str, selected_estates: List[str]) -> Tuple[bool, List[str]]:
        """Validate input parameters dengan debug"""
        self.logger.debug("Validating input parameters")
        errors = []

        # Validate date format
        try:
            self._normalize_date(start_date)
            self._normalize_date(end_date)
            self.logger.debug("Date formats are valid")
        except ValueError as e:
            error = f"Invalid date format: {e}"
            self.logger.error(error)
            errors.append(error)

        # Validate estate selection
        if not selected_estates:
            error = "No estates selected"
            self.logger.error(error)
            errors.append(error)
        else:
            for estate in selected_estates:
                if estate not in self.estate_config:
                    error = f"Estate {estate} not found in configuration"
                    self.logger.error(error)
                    errors.append(error)
                else:
                    self.logger.debug(f"Estate {estate} validated successfully")

        # Validate required files
        if not os.path.exists(self.template_path):
            error = f"Template file not found: {self.template_path}"
            self.logger.error(error)
            errors.append(error)

        if not os.path.exists(self.formula_path):
            error = f"Formula file not found: {self.formula_path}"
            self.logger.error(error)
            errors.append(error)

        self.logger.debug(f"Validation completed: {len(errors)} errors found")
        return len(errors) == 0, errors

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string ke YYYY-MM-DD format dengan debug"""
        if not date_str:
            raise ValueError("Date cannot be empty")

        self.logger.debug(f"Normalizing date: {date_str}")

        # Try different date formats
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']

        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                normalized = date_obj.strftime('%Y-%m-%d')
                self.logger.debug(f"Date normalized: {date_str} -> {normalized} (format: {fmt})")
                return normalized
            except ValueError:
                continue

        raise ValueError(f"Unrecognized date format: {date_str}")

    def _initialize_components(self):
        """Initialize semua komponen enhanced dengan debug"""
        try:
            self.logger.info("Initializing enhanced components")

            # Initialize enhanced template processor
            self.logger.debug("Initializing enhanced template processor")
            self.template_processor = TemplateProcessorEnhanced(self.template_path, self.formula_path)

            # Formula engine akan diinitialize per estate karena database connection berbeda
            self.logger.info("Enhanced components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing enhanced components: {e}", exc_info=True)
            raise

    def _generate_single_estate_report(self,
                                     estate_name: str,
                                     db_path: str,
                                     start_date: str,
                                     end_date: str,
                                     output_dir: str) -> Optional[str]:
        """Generate report untuk single estate dengan enhanced debugging"""
        try:
            self.logger.info(f"=== GENERATING REPORT FOR ESTATE: {estate_name} ===")
            self.logger.info(f"Database: {db_path}")
            self.logger.info(f"Period: {start_date} to {end_date}")

            # Initialize database connection
            self.logger.debug("Initializing database connection")
            self.db_connector = FirebirdConnector(db_path=db_path)

            # Test connection
            self.logger.debug("Testing database connection")
            if not self.db_connector.test_connection():
                self.logger.error(f"Failed to connect to database: {db_path}")
                return None

            self.logger.info("Database connection established successfully")

            # Initialize enhanced formula engine
            self.logger.debug("Initializing enhanced formula engine")
            self.formula_engine = FormulaEngineEnhanced(self.formula_path, self.db_connector)

            # Prepare parameters
            parameters = {
                'start_date': start_date,
                'end_date': end_date,
                'estate_name': estate_name,
                'estate_code': estate_name.replace(' ', '_')
            }

            self.logger.info(f"Prepared parameters: {parameters}")

            # Execute all queries
            self.logger.info("Executing all database queries")
            query_results = self.formula_engine.execute_all_queries(parameters)

            # Log query results summary
            successful_queries = sum(1 for result in query_results.values() if result is not None)
            self.logger.info(f"Query execution completed: {successful_queries}/{len(query_results)} successful")

            # Process variables
            self.logger.info("Processing variables from query results")
            variables = self.formula_engine.process_variables(query_results, parameters)

            self.logger.info(f"Variable processing completed: {len(variables)} variables processed")

            # Calculate derived metrics
            self.logger.debug("Calculating derived metrics")
            derived_metrics = self._calculate_derived_metrics({
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

            self.logger.info(f"Merged data prepared: {len(all_data)} total items")

            # Create new template instance
            self.logger.debug("Creating new template instance")
            template_instance = self.template_processor.create_copy()

            # Process placeholders dengan detail logging
            self.logger.info("Processing template placeholders")
            processed_sheets = 0

            for sheet_name in template_instance.workbook.sheetnames:
                self.logger.debug(f"Processing sheet: {sheet_name}")
                success = template_instance.process_sheet_placeholders(sheet_name, all_data)
                if success:
                    processed_sheets += 1
                else:
                    self.logger.warning(f"Failed to process placeholders in sheet: {sheet_name}")

            self.logger.info(f"Placeholder processing completed: {processed_sheets}/{len(template_instance.workbook.sheetnames)} sheets processed")

            # Process repeating sections
            self.logger.info("Processing repeating sections")
            repeating_sections = self.formula_engine.formulas.get('repeating_sections', {})

            for section_name, section_config in repeating_sections.items():
                sheet_name = section_config.get('sheet_name')
                if sheet_name:
                    self.logger.debug(f"Processing repeating section '{section_name}' in sheet '{sheet_name}'")
                    try:
                        data = self.formula_engine.process_repeating_section_data(section_name, query_results)
                        if data:
                            success = template_instance.process_repeating_section(sheet_name, data)
                            if success:
                                self.logger.info(f"Repeating section '{section_name}' processed successfully: {len(data)} rows")
                            else:
                                self.logger.warning(f"Failed to process repeating section '{section_name}'")
                        else:
                            self.logger.warning(f"No data available for repeating section '{section_name}'")
                    except Exception as e:
                        self.logger.error(f"Error processing repeating section '{section_name}': {e}")

            # Generate output filename
            output_filename = f"Laporan_FFB_Analysis_{estate_name.replace(' ', '_')}_{start_date}_{end_date}.xlsx"
            output_path = os.path.join(output_dir, output_filename)

            self.logger.info(f"Saving report to: {output_path}")

            # Save report
            success = template_instance.save_processed_template(output_path)

            if success:
                self.logger.info(f"✓ Report saved successfully: {output_path}")
                return output_path
            else:
                self.logger.error(f"✗ Failed to save report: {output_path}")
                return None

        except Exception as e:
            self.logger.error(f"Error generating report for estate {estate_name}: {e}", exc_info=True)
            return None

    def _calculate_derived_metrics(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived metrics dari base data"""
        metrics = {}

        try:
            self.logger.debug("Calculating derived metrics")

            # Calculate total days in period
            if 'start_date' in base_data and 'end_date' in base_data:
                try:
                    start_date = datetime.strptime(base_data['start_date'], '%Y-%m-%d')
                    end_date = datetime.strptime(base_data['end_date'], '%Y-%m-%d')
                    total_days = (end_date - start_date).days + 1
                    metrics['total_days'] = total_days
                    self.logger.debug(f"Calculated total_days: {total_days}")
                except Exception as e:
                    self.logger.error(f"Error calculating total_days: {e}")
                    metrics['total_days'] = 1

            # Add basic metrics for template compatibility
            metrics.update({
                'current_date': datetime.now().strftime('%d %B %Y'),
                'current_time': datetime.now().strftime('%H:%M:%S'),
                'report_title': f'LAPORAN ANALISIS FFB - {base_data.get("estate_name", "Unknown")}',
                'report_period': f'Periode: {base_data.get("start_date", "")} s/d {base_data.get("end_date", "")}'
            })

            self.logger.debug(f"Derived metrics calculated: {len(metrics)} metrics")
            return metrics

        except Exception as e:
            self.logger.error(f"Error calculating derived metrics: {e}")
            return {}

    def _generate_consolidated_report(self,
                                    selected_estates: List[str],
                                    start_date: str,
                                    end_date: str,
                                    output_dir: str) -> Optional[str]:
        """Generate consolidated report untuk multiple estates"""
        try:
            self.logger.info("Generating consolidated report")

            # Create consolidated template
            template_instance = self.template_processor.create_copy()

            # Prepare consolidated data
            consolidated_data = {
                'start_date': start_date,
                'end_date': end_date,
                'report_title': f'LAPORAN ANALISIS FFB - KONSOLIDASI {len(selected_estates)} ESTATES',
                'report_period': f'Periode: {start_date} s/d {end_date}',
                'generated_date': datetime.now().strftime('%d %B %Y'),
                'generated_time': datetime.now().strftime('%H:%M:%S'),
                'estates': ', '.join(selected_estates)
            }

            # Process placeholders in dashboard sheet if exists
            if 'Dashboard' in template_instance.workbook.sheetnames:
                template_instance.process_sheet_placeholders('Dashboard', consolidated_data)

            # Save consolidated report
            output_filename = f"Laporan_FFB_Analysis_Konsolidasi_{start_date}_{end_date}.xlsx"
            output_path = os.path.join(output_dir, output_filename)

            template_instance.save_processed_template(output_path)

            self.logger.info(f"Consolidated report saved: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Error generating consolidated report: {e}", exc_info=True)
            return None

    def get_available_estates(self) -> List[str]:
        """Get list of available estates from configuration"""
        estates = list(self.estate_config.keys())
        self.logger.debug(f"Available estates: {estates}")
        return estates

    def get_template_info(self) -> Dict[str, Any]:
        """Get template information dengan debug"""
        try:
            if os.path.exists(self.template_path):
                template_processor = TemplateProcessorEnhanced(self.template_path, self.formula_path)
                info = template_processor.get_template_info()
                self.logger.debug(f"Template info retrieved: {info}")
                return info
            else:
                error = {'error': 'Template file not found'}
                self.logger.error(error['error'])
                return error

        except Exception as e:
            error = {'error': str(e)}
            self.logger.error(f"Error getting template info: {e}")
            return error

def main():
    """Main function untuk testing enhanced generator"""
    print("=== Enhanced Excel Report Generator Test ===")

    generator = ExcelReportGeneratorEnhanced()

    # Test dengan sample data
    estates = generator.get_available_estates()
    print(f"Available estates: {estates}")

    if estates:
        # Generate sample report
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        selected_estates = ["PGE 2B"]  # Test dengan 1 estate

        print(f"Generating report for {selected_estates} from {start_date} to {end_date}")

        success, results = generator.generate_report(start_date, end_date, selected_estates)

        if success:
            print(f"✓ Report generated successfully: {results}")
        else:
            print(f"✗ Report generation failed: {results}")

if __name__ == "__main__":
    main()