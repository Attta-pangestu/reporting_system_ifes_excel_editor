#!/usr/bin/env python3
"""
Debug Analyzer untuk Excel Report Generator
Menganalisis setiap komponen secara mendalam untuk menemukan akar masalah rendering placeholder
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from firebird_connector_enhanced import FirebirdConnectorEnhanced
    from template_processor_enhanced import TemplateProcessorEnhanced
    from formula_engine_enhanced import FormulaEngineEnhanced
    from excel_report_generator_enhanced import ExcelReportGeneratorEnhanced
except ImportError as e:
    print(f"ERROR: Failed to import modules: {e}")
    sys.exit(1)

class DebugAnalyzer:
    """
    Comprehensive debugging tool untuk menganalisis seluruh proses report generation
    """

    def __init__(self):
        self.setup_debug_logging()
        self.results = {}
        self.errors = []

    def setup_debug_logging(self):
        """Setup detailed debug logging ke console dan file"""
        # Create logger
        self.logger = logging.getLogger("DebugAnalyzer")
        self.logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Console handler dengan detailed formatting
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Detailed formatter
        formatter = logging.Formatter(
            '\n%(asctime)s - %(name)s - %(levelname)s - LINE:%(lineno)d - %(funcName)s\n%(message)s\n',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler untuk complete log
        log_file = os.path.join(os.path.dirname(__file__), "debug_complete.log")
        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.info("="*80)
        self.logger.info("DEBUG ANALYZER STARTED - COMPREHENSIVE ANALYSIS MODE")
        self.logger.info("="*80)

    def print_section_header(self, title: str):
        """Print section header yang jelas"""
        border = "="*60
        print(f"\n{border}")
        print(f"🔍 {title}")
        print(f"{border}")
        self.logger.info(f"SECTION: {title}")

    def print_subsection(self, title: str):
        """Print subsection header"""
        print(f"\n📋 {title}")
        print("-" * 40)
        self.logger.info(f"SUBSECTION: {title}")

    def analyze_file_structure(self):
        """Analisis struktur file dan path"""
        self.print_section_header("FILE STRUCTURE ANALYSIS")

        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Check critical files
        critical_files = {
            "Formula JSON": "laporan_ffb_analysis_formula.json",
            "Firebird Connector": "firebird_connector_enhanced.py",
            "Template Processor": "template_processor_enhanced.py",
            "Formula Engine": "formula_engine_enhanced.py",
            "Excel Generator": "excel_report_generator_enhanced.py"
        }

        for name, filename in critical_files.items():
            filepath = os.path.join(base_path, filename)
            exists = os.path.exists(filepath)
            size = os.path.getsize(filepath) if exists else 0
            status = "✅ EXISTS" if exists else "❌ MISSING"

            print(f"{status} {name}: {filename} ({size:,} bytes)")
            self.logger.info(f"File check - {name}: {filename} - Exists: {exists}, Size: {size}")

            if not exists:
                self.errors.append(f"Critical file missing: {filename}")

        # Check templates folder
        templates_dir = os.path.join(base_path, "templates")
        if os.path.exists(templates_dir):
            template_files = [f for f in os.listdir(templates_dir) if f.endswith(('.xlsx', '.xls'))]
            print(f"\n📁 Templates folder: {len(template_files)} Excel files found")
            for template in template_files:
                print(f"   - {template}")
            self.logger.info(f"Templates found: {template_files}")
        else:
            print(f"\n❌ Templates folder not found: {templates_dir}")
            self.errors.append("Templates folder not found")

    def analyze_formula_json(self):
        """Analisis mendalam formula JSON structure"""
        self.print_section_header("FORMULA JSON ANALYSIS")

        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        formula_path = os.path.join(base_path, "laporan_ffb_analysis_formula.json")

        if not os.path.exists(formula_path):
            print("❌ Formula JSON file not found!")
            self.errors.append("Formula JSON file not found")
            return

        try:
            with open(formula_path, 'r', encoding='utf-8') as f:
                formulas = json.load(f)

            print("✅ Formula JSON loaded successfully")
            self.logger.info("Formula JSON structure analysis started")

            # Analyze queries section
            self.print_subsection("QUERIES ANALYSIS")
            queries = formulas.get('queries', {})
            print(f"Total queries defined: {len(queries)}")

            for query_name, query_config in queries.items():
                print(f"\n🔹 Query: {query_name}")
                sql = query_config.get('sql', '')
                return_format = query_config.get('return_format', 'unknown')

                # Check for parameters
                has_start_date = '{start_date}' in sql
                has_end_date = '{end_date}' in sql
                has_month = '{month}' in sql

                print(f"   SQL Length: {len(sql)} chars")
                print(f"   Return Format: {return_format}")
                print(f"   Uses start_date: {'✅' if has_start_date else '❌'}")
                print(f"   Uses end_date: {'✅' if has_end_date else '❌'}")
                print(f"   Uses month: {'✅' if has_month else '❌'}")

                # Show first 100 chars of SQL
                sql_preview = sql[:100] + "..." if len(sql) > 100 else sql
                print(f"   SQL Preview: {sql_preview}")

                self.logger.info(f"Query {query_name}: {len(sql)} chars, format: {return_format}")
                self.logger.debug(f"SQL for {query_name}: {sql}")

            # Analyze variables section
            self.print_subsection("VARIABLES ANALYSIS")
            variables = formulas.get('variables', {})
            total_vars = sum(len(category_vars) for category_vars in variables.values())
            print(f"Total variable categories: {len(variables)}")
            print(f"Total variables: {total_vars}")

            for category_name, category_vars in variables.items():
                print(f"\n📁 Category: {category_name} ({len(category_vars)} variables)")

                for var_name, var_config in category_vars.items():
                    var_type = var_config.get('type', 'unknown')
                    query = var_config.get('query', '')
                    field = var_config.get('field', '')

                    print(f"   • {var_name}: {var_type}")
                    if query:
                        print(f"     → Query: {query}")
                    if field:
                        print(f"     → Field: {field}")

                    self.logger.debug(f"Variable {category_name}.{var_name}: type={var_type}, query={query}, field={field}")

            # Analyze repeating sections
            self.print_subsection("REPEATING SECTIONS ANALYSIS")
            repeating = formulas.get('repeating_sections', {})
            print(f"Total repeating sections: {len(repeating)}")

            for section_name, section_config in repeating.items():
                sheet_name = section_config.get('sheet_name', 'unknown')
                data_source = section_config.get('data_source', 'unknown')
                columns = section_config.get('columns', {})

                print(f"\n📊 Section: {section_name}")
                print(f"   Target Sheet: {sheet_name}")
                print(f"   Data Source: {data_source}")
                print(f"   Columns: {len(columns)} defined")

                self.logger.info(f"Repeating section {section_name}: sheet={sheet_name}, source={data_source}")

            self.results['formula_analysis'] = {
                'queries_count': len(queries),
                'variables_count': total_vars,
                'repeating_sections_count': len(repeating),
                'valid': True
            }

        except Exception as e:
            print(f"❌ Error analyzing formula JSON: {e}")
            traceback.print_exc()
            self.logger.error(f"Formula JSON analysis failed: {e}")
            self.errors.append(f"Formula JSON analysis error: {e}")

    def test_database_connection(self):
        """Test database connection dan basic queries"""
        self.print_section_header("DATABASE CONNECTION TEST")

        db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"

        print(f"Testing connection to: {db_path}")

        if not os.path.exists(db_path):
            print("❌ Database file not found!")
            self.errors.append("Database file not found")
            return

        try:
            print("🔄 Creating Firebird connector...")
            connector = FirebirdConnectorEnhanced(db_path=db_path)

            print("🔄 Testing connection...")
            if connector.test_connection():
                print("✅ Database connection successful!")
                self.logger.info("Database connection test: SUCCESS")

                # Test basic query
                print("\n🔄 Testing basic query...")
                test_query = "SELECT 'CONNECTION_TEST' as STATUS, CURRENT_TIMESTAMP as TEST_TIME FROM RDB$DATABASE"
                result = connector.execute_query(test_query)

                print(f"✅ Basic query successful!")
                print(f"   Result type: {type(result)}")
                if result and len(result) > 0:
                    if isinstance(result[0], dict):
                        print(f"   First result: {result[0]}")
                    elif isinstance(result[0], dict) and 'rows' in result[0]:
                        print(f"   Rows returned: {len(result[0]['rows'])}")
                        if result[0]['rows']:
                            print(f"   First row: {result[0]['rows'][0]}")

                # Test FFB table exists
                print("\n🔄 Testing FFB table access...")
                ffb_query = "SELECT FIRST 1 * FROM FFBSCANNERDATA01 WHERE ROWNUM <= 1"
                try:
                    ffb_result = connector.execute_query(ffb_query)
                    print("✅ FFB table accessible!")
                    if ffb_result and len(ffb_result) > 0:
                        if isinstance(ffb_result[0], dict) and 'rows' in ffb_result[0]:
                            headers = ffb_result[0].get('headers', [])
                            print(f"   Table columns: {len(headers)}")
                            print(f"   Sample columns: {headers[:5]}")
                except Exception as e:
                    print(f"⚠️  FFB table access issue: {e}")
                    self.logger.warning(f"FFB table access issue: {e}")

                self.results['database_test'] = {
                    'connection': True,
                    'basic_query': True,
                    'ffb_table': True
                }

            else:
                print("❌ Database connection failed!")
                self.errors.append("Database connection failed")
                self.results['database_test'] = {'connection': False}

        except Exception as e:
            print(f"❌ Database test error: {e}")
            traceback.print_exc()
            self.logger.error(f"Database test failed: {e}")
            self.errors.append(f"Database test error: {e}")

    def test_query_execution(self):
        """Test eksekusi semua queries dari formula JSON"""
        self.print_section_header("QUERY EXECUTION TEST")

        db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
        formula_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "laporan_ffb_analysis_formula.json")

        if not os.path.exists(formula_path):
            print("❌ Formula JSON not found!")
            return

        try:
            # Load formulas
            with open(formula_path, 'r', encoding='utf-8') as f:
                formulas = json.load(f)

            # Create connector and formula engine
            connector = FirebirdConnectorEnhanced(db_path=db_path)
            formula_engine = FormulaEngineEnhanced(formula_path, connector)

            # Prepare test parameters
            test_params = {
                'start_date': '2024-10-01',
                'end_date': '2024-10-31',
                'estate_name': 'PGE 2B',
                'estate_code': 'PGE_2B'
            }

            print(f"Test Parameters: {test_params}")

            # Execute all queries
            self.print_subsection("EXECUTING ALL QUERIES")
            query_results = {}

            for query_name, query_config in formulas.get('queries', {}).items():
                print(f"\n🔄 Executing query: {query_name}")

                try:
                    original_sql = query_config.get('sql', '')
                    print(f"   Original SQL: {original_sql[:100]}...")

                    result = formula_engine.execute_query(query_name, test_params)
                    query_results[query_name] = result

                    # Analyze result
                    if result is None:
                        print("❌ Query returned None")
                        self.errors.append(f"Query {query_name} returned None")
                    elif isinstance(result, list):
                        if len(result) == 0:
                            print("⚠️  Query returned empty list")
                        else:
                            print(f"✅ Query returned list with {len(result)} items")
                            if isinstance(result[0], dict):
                                if 'rows' in result[0]:
                                    rows = result[0]['rows']
                                    headers = result[0].get('headers', [])
                                    print(f"   Headers: {headers}")
                                    print(f"   Rows: {len(rows)}")
                                    if rows:
                                        print(f"   Sample row: {rows[0]}")
                                else:
                                    print(f"   First item: {result[0]}")
                    elif isinstance(result, dict):
                        print(f"✅ Query returned dict: {list(result.keys())}")
                    else:
                        print(f"✅ Query returned {type(result)}: {result}")

                    self.logger.info(f"Query {query_name} executed successfully: {type(result)}")

                except Exception as e:
                    print(f"❌ Query {query_name} failed: {e}")
                    traceback.print_exc()
                    self.logger.error(f"Query {query_name} failed: {e}")
                    self.errors.append(f"Query {query_name} execution error: {e}")
                    query_results[query_name] = None

            self.results['query_execution'] = query_results

            # Test variable processing
            self.print_subsection("VARIABLE PROCESSING TEST")
            try:
                variables = formula_engine.process_variables(query_results, test_params)
                print(f"\n✅ Variable processing successful!")
                print(f"Total variables processed: {len(variables)}")

                for var_name, value in list(variables.items())[:10]:  # Show first 10
                    print(f"   {var_name}: {value} (type: {type(value).__name__})")

                self.logger.info(f"Variable processing successful: {len(variables)} variables")
                self.results['variable_processing'] = variables

            except Exception as e:
                print(f"❌ Variable processing failed: {e}")
                traceback.print_exc()
                self.logger.error(f"Variable processing failed: {e}")
                self.errors.append(f"Variable processing error: {e}")

        except Exception as e:
            print(f"❌ Query execution test failed: {e}")
            traceback.print_exc()
            self.logger.error(f"Query execution test failed: {e}")
            self.errors.append(f"Query execution test error: {e}")

    def test_template_loading(self):
        """Test loading template dan placeholder detection"""
        self.print_section_header("TEMPLATE LOADING TEST")

        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        templates_dir = os.path.join(base_path, "templates")
        formula_path = os.path.join(base_path, "laporan_ffb_analysis_formula.json")

        if not os.path.exists(templates_dir):
            print("❌ Templates directory not found!")
            self.errors.append("Templates directory not found")
            return

        # Find Excel templates
        template_files = [f for f in os.listdir(templates_dir) if f.endswith(('.xlsx', '.xls'))]

        if not template_files:
            print("❌ No Excel template files found!")
            self.errors.append("No Excel template files found")
            return

        print(f"Found {len(template_files)} template files:")
        for template in template_files:
            print(f"   - {template}")

        # Test first template
        template_file = template_files[0]
        template_path = os.path.join(templates_dir, template_file)

        print(f"\n🔄 Testing template: {template_file}")

        try:
            # Load template
            processor = TemplateProcessorEnhanced(template_path, formula_path)

            print("✅ Template loaded successfully!")

            # Get template info
            info = processor.get_template_info()
            print(f"   Sheets: {info.get('sheets', [])}")
            print(f"   Total placeholders: {info.get('total_placeholders', 0)}")
            print(f"   Repeating sections: {info.get('repeating_sections', [])}")

            # Analyze placeholders per sheet
            placeholders = processor.get_placeholders()
            print(f"\n📋 Placeholder Analysis:")

            for sheet_name, sheet_placeholders in placeholders.items():
                print(f"\n   Sheet '{sheet_name}': {len(sheet_placeholders)} placeholders")

                for i, ph in enumerate(sheet_placeholders[:5]):  # Show first 5
                    print(f"      {i+1}. {ph['placeholder']} at {ph['cell']}")
                    print(f"         Full text: {ph['original_value']}")

                if len(sheet_placeholders) > 5:
                    print(f"      ... and {len(sheet_placeholders) - 5} more")

            self.results['template_analysis'] = {
                'template_file': template_file,
                'sheets': info.get('sheets', []),
                'total_placeholders': info.get('total_placeholders', 0),
                'placeholders': placeholders
            }

        except Exception as e:
            print(f"❌ Template loading failed: {e}")
            traceback.print_exc()
            self.logger.error(f"Template loading failed: {e}")
            self.errors.append(f"Template loading error: {e}")

    def test_end_to_end_rendering(self):
        """Test rendering end-to-end dengan data aktual"""
        self.print_section_header("END-TO-END RENDERING TEST")

        try:
            # Setup paths
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            templates_dir = os.path.join(base_path, "templates")
            formula_path = os.path.join(base_path, "laporan_ffb_analysis_formula.json")
            db_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"

            # Find template
            template_files = [f for f in os.listdir(templates_dir) if f.endswith(('.xlsx', '.xls'))]
            if not template_files:
                print("❌ No templates found for E2E test!")
                return

            template_path = os.path.join(templates_dir, template_files[0])
            print(f"Using template: {template_files[0]}")

            # Initialize components
            print("\n🔄 Initializing components...")
            connector = FirebirdConnectorEnhanced(db_path=db_path)
            formula_engine = FormulaEngineEnhanced(formula_path, connector)
            template_processor = TemplateProcessorEnhanced(template_path, formula_path)

            # Prepare parameters
            test_params = {
                'start_date': '2024-10-01',
                'end_date': '2024-10-31',
                'estate_name': 'PGE 2B TEST',
                'estate_code': 'PGE_2B_TEST'
            }

            print(f"Test parameters: {test_params}")

            # Execute queries
            print("\n🔄 Executing queries...")
            query_results = formula_engine.execute_all_queries(test_params)

            successful_queries = sum(1 for r in query_results.values() if r is not None)
            print(f"Queries executed: {successful_queries}/{len(query_results)} successful")

            # Process variables
            print("\n🔄 Processing variables...")
            variables = formula_engine.process_variables(query_results, test_params)
            print(f"Variables processed: {len(variables)}")

            # Prepare complete data
            all_data = {
                **test_params,
                **variables,
                **query_results
            }

            print(f"Complete data keys: {list(all_data.keys())}")

            # Test placeholder substitution
            print("\n🔄 Testing placeholder substitution...")
            placeholders = template_processor.get_placeholders()

            substitution_results = {}

            for sheet_name, sheet_placeholders in placeholders.items():
                print(f"\n   Sheet '{sheet_name}': {len(sheet_placeholders)} placeholders")

                sheet_results = []
                for ph in sheet_placeholders:
                    placeholder = ph['placeholder']
                    cell_coord = ph['cell']

                    # Try to get value
                    try:
                        value = template_processor._get_placeholder_value(placeholder, all_data)

                        if value is not None:
                            print(f"      ✅ {placeholder} at {cell_coord} = {value}")
                            sheet_results.append({
                                'placeholder': placeholder,
                                'cell': cell_coord,
                                'value': value,
                                'success': True
                            })
                        else:
                            print(f"      ❌ {placeholder} at {cell_coord} = NO VALUE FOUND")
                            sheet_results.append({
                                'placeholder': placeholder,
                                'cell': cell_coord,
                                'value': None,
                                'success': False
                            })
                            self.errors.append(f"Placeholder {placeholder} not found in data")

                    except Exception as e:
                        print(f"      ❌ {placeholder} at {cell_coord} = ERROR: {e}")
                        sheet_results.append({
                            'placeholder': placeholder,
                            'cell': cell_coord,
                            'value': f"ERROR: {e}",
                            'success': False
                        })
                        self.errors.append(f"Placeholder {placeholder} error: {e}")

                substitution_results[sheet_name] = sheet_results

                # Summary per sheet
                successful = sum(1 for r in sheet_results if r['success'])
                total = len(sheet_results)
                print(f"   Summary: {successful}/{total} placeholders resolved ({successful/total*100:.1f}%)")

            self.results['e2e_rendering'] = {
                'template': template_files[0],
                'queries_successful': successful_queries,
                'variables_processed': len(variables),
                'substitution_results': substitution_results
            }

            # Test actual template processing
            print("\n🔄 Testing actual template processing...")
            try:
                # Create copy
                template_instance = template_processor.create_copy()

                # Process each sheet
                processed_sheets = 0
                for sheet_name in template_instance.workbook.sheetnames:
                    try:
                        success = template_instance.process_sheet_placeholders(sheet_name, all_data)
                        if success:
                            processed_sheets += 1
                            print(f"   ✅ Sheet '{sheet_name}' processed")
                        else:
                            print(f"   ❌ Sheet '{sheet_name}' processing failed")
                    except Exception as e:
                        print(f"   ❌ Sheet '{sheet_name}' error: {e}")
                        self.errors.append(f"Sheet {sheet_name} processing error: {e}")

                print(f"\n   Sheets processed: {processed_sheets}/{len(template_instance.workbook.sheetnames)}")

                # Save test output
                output_path = os.path.join(os.path.dirname(__file__), "test_output.xlsx")
                template_instance.save_processed_template(output_path)
                print(f"   ✅ Test output saved: {output_path}")

                self.results['e2e_rendering']['actual_processing'] = {
                    'sheets_processed': processed_sheets,
                    'total_sheets': len(template_instance.workbook.sheetnames),
                    'output_file': output_path
                }

            except Exception as e:
                print(f"   ❌ Actual template processing failed: {e}")
                traceback.print_exc()
                self.errors.append(f"Actual template processing error: {e}")

        except Exception as e:
            print(f"❌ End-to-end test failed: {e}")
            traceback.print_exc()
            self.logger.error(f"End-to-end test failed: {e}")
            self.errors.append(f"End-to-end test error: {e}")

    def generate_diagnostic_report(self):
        """Generate comprehensive diagnostic report"""
        self.print_section_header("COMPREHENSIVE DIAGNOSTIC REPORT")

        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"   Total errors found: {len(self.errors)}")
        print(f"   Tests completed: {len(self.results)}")

        if self.errors:
            print(f"\n❌ ERRORS IDENTIFIED:")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")

        print(f"\n✅ RESULTS SUMMARY:")
        for test_name, result in self.results.items():
            if isinstance(result, dict):
                status = "✅ PASSED" if not any('error' in str(k).lower() or 'failed' in str(k).lower() for k in result.keys()) else "⚠️  ISSUES"
                print(f"   {test_name}: {status}")

        # Root cause analysis
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")

        if self.errors:
            error_categories = {}
            for error in self.errors:
                if 'connection' in error.lower():
                    error_categories['Database Connection'] = error_categories.get('Database Connection', 0) + 1
                elif 'template' in error.lower():
                    error_categories['Template Issues'] = error_categories.get('Template Issues', 0) + 1
                elif 'query' in error.lower():
                    error_categories['Query Execution'] = error_categories.get('Query Execution', 0) + 1
                elif 'variable' in error.lower():
                    error_categories['Variable Processing'] = error_categories.get('Variable Processing', 0) + 1
                else:
                    error_categories['Other'] = error_categories.get('Other', 0) + 1

            for category, count in error_categories.items():
                print(f"   • {category}: {count} issues")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if 'Database Connection' in [e for e in self.errors if 'connection' in e.lower()]:
            print("   • Check database file path and permissions")
            print("   • Ensure Firebird server is running")
            print("   • Verify ISQL client is available")

        if 'Template Issues' in [e for e in self.errors if 'template' in e.lower()]:
            print("   • Verify template file exists and is readable")
            print("   • Check template for proper {{variable}} placeholder format")
            print("   • Ensure template sheets are not corrupted")

        if 'Query Execution' in [e for e in self.errors if 'query' in e.lower()]:
            print("   • Review SQL query syntax in formula JSON")
            print("   • Check table and column names in database")
            print("   • Verify parameter substitution in queries")

        if 'Variable Processing' in [e for e in self.errors if 'variable' in e.lower()]:
            print("   • Check variable mapping in formula JSON")
            print("   • Verify query result field names match variable definitions")
            print("   • Ensure proper data type handling")

        # Save detailed report
        report_path = os.path.join(os.path.dirname(__file__), "diagnostic_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'errors': self.errors,
                'results': self.results,
                'summary': {
                    'total_errors': len(self.errors),
                    'tests_completed': len(self.results),
                    'status': 'FAILED' if self.errors else 'PASSED'
                }
            }, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Detailed report saved: {report_path}")

        return len(self.errors) == 0

    def run_complete_analysis(self):
        """Run semua analisis secara komprehensif"""
        try:
            print("🚀 STARTING COMPREHENSIVE DEBUG ANALYSIS")
            print("="*80)

            # Run all tests
            self.analyze_file_structure()
            self.analyze_formula_json()
            self.test_database_connection()
            self.test_query_execution()
            self.test_template_loading()
            self.test_end_to_end_rendering()

            # Generate final report
            success = self.generate_diagnostic_report()

            if success:
                print("\n🎉 ALL TESTS PASSED! System should be working correctly.")
            else:
                print(f"\n⚠️  FOUND {len(self.errors)} ISSUES that need to be addressed.")

            return success

        except Exception as e:
            print(f"\n💥 CRITICAL ERROR during analysis: {e}")
            traceback.print_exc()
            return False

def main():
    """Main function untuk menjalankan debug analyzer"""
    print("Excel Report Generator - Debug Analyzer")
    print("="*80)

    analyzer = DebugAnalyzer()
    success = analyzer.run_complete_analysis()

    if not success:
        print(f"\n❌ Analysis completed with issues found.")
        print("Check diagnostic_report.json for detailed information.")
        sys.exit(1)
    else:
        print(f"\n✅ All tests passed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()