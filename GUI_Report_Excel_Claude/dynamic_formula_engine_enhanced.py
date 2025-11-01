#!/usr/bin/env python3
"""
Enhanced Dynamic Formula Engine untuk Raw Data Processing
Mendukung algoritma pemrosesan data berdasarkan referensi gui_multi_estate_ffb_analysis_extraction.json
"""

import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict

# Import Firebird connector
try:
    from firebird_connector_enhanced import FirebirdConnectorEnhanced
except ImportError:
    # Fallback to standard connector
    try:
        from firebird_connector import FirebirdConnector
        FirebirdConnectorEnhanced = FirebirdConnector
    except ImportError:
        print("Warning: No Firebird connector available")
        FirebirdConnectorEnhanced = None

class EnhancedDynamicFormulaEngine:
    """
    Enhanced formula engine dengan raw data processing dan algoritma yang diperbaiki
    """

    def __init__(self, formula_path: str, db_connector=None):
        """
        Inisialisasi enhanced dynamic formula engine

        Args:
            formula_path: Path ke formula JSON file
            db_connector: Firebird database connector instance
        """
        self.formula_path = formula_path
        self.db_connector = db_connector
        self.logger = logging.getLogger(__name__)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Load formula definitions
        self.formula_data = None
        self.queries = {}
        self.variables = {}
        self.repeating_sections = {}
        self.processing_logic = {}
        
        # Data storage for processing
        self.employee_mapping = {}
        self.raw_ffb_data = []
        self.filtered_data = []
        self.processed_data = {}

        self._load_formula()
        self._setup_queries_from_json()

    def _load_formula(self):
        """Load formula JSON file"""
        try:
            if not os.path.exists(self.formula_path):
                raise FileNotFoundError(f"Formula file not found: {self.formula_path}")

            with open(self.formula_path, 'r', encoding='utf-8') as f:
                self.formula_data = json.load(f)

            self.logger.info(f"Enhanced formula loaded: {self.formula_path}")

            # Extract structure
            if 'queries' in self.formula_data:
                self.queries = self.formula_data['queries']
            if 'variables' in self.formula_data:
                self.variables = self.formula_data['variables']
            if 'repeating_sections' in self.formula_data:
                self.repeating_sections = self.formula_data['repeating_sections']
            if 'processing_logic' in self.formula_data:
                self.processing_logic = self.formula_data['processing_logic']

        except Exception as e:
            self.logger.error(f"Error loading formula: {e}")
            raise

    def _setup_queries_from_json(self):
        """Setup queries from loaded JSON formula data"""
        if self.formula_data and 'queries' in self.formula_data:
            self.dynamic_queries = self.formula_data['queries']
            self.logger.info(f"Loaded {len(self.dynamic_queries)} queries from JSON file")
        else:
            self.logger.warning("No queries found in JSON file, using empty queries")
            self.dynamic_queries = {}

    def execute_query(self, query_name: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        """
        Execute a single query with enhanced error handling and parameter substitution
        """
        if parameters is None:
            parameters = {}

        try:
            if query_name not in self.dynamic_queries:
                self.logger.error(f"Query '{query_name}' not found in formula file")
                return []

            query_def = self.dynamic_queries[query_name]
            
            if 'sql' not in query_def:
                self.logger.error(f"No SQL found for query '{query_name}'")
                return []

            # Substitute parameters in SQL
            sql = self._substitute_parameters(query_def['sql'], parameters)
            self.logger.info(f"Executing query '{query_name}': {sql}")

            if not self.db_connector:
                self.logger.error("No database connector available")
                return []

            # Execute query
            results = self.db_connector.execute_query(sql)
            
            if not results:
                self.logger.warning(f"Query '{query_name}' returned no results")
                return []

            # Convert to list of dictionaries
            if isinstance(results, list) and len(results) > 0:
                if isinstance(results[0], dict):
                    self.logger.info(f"Query '{query_name}' returned {len(results)} rows")
                    return results
                else:
                    # Convert tuple results to dictionaries
                    columns = self.db_connector.get_column_names()
                    dict_results = []
                    for row in results:
                        if isinstance(row, (list, tuple)):
                            dict_results.append(dict(zip(columns, row)))
                        else:
                            dict_results.append({'result': row})
                    self.logger.info(f"Query '{query_name}' converted {len(dict_results)} rows to dictionaries")
                    return dict_results
            
            return []

        except Exception as e:
            self.logger.error(f"Error executing query '{query_name}': {e}")
            return []

    def _substitute_parameters(self, sql: str, parameters: Dict[str, Any]) -> str:
        """Enhanced parameter substitution with better formatting"""
        try:
            # Handle month parameter with zero-padding
            if 'month' in parameters:
                month_val = parameters['month']
                if isinstance(month_val, str):
                    try:
                        month_int = int(month_val)
                        parameters['month:02d'] = f"{month_int:02d}"
                    except ValueError:
                        parameters['month:02d'] = month_val
                elif isinstance(month_val, int):
                    parameters['month:02d'] = f"{month_val:02d}"

            # Standard parameter substitution
            for key, value in parameters.items():
                placeholder = '{' + key + '}'
                if placeholder in sql:
                    if isinstance(value, str):
                        sql = sql.replace(placeholder, value)
                    else:
                        sql = sql.replace(placeholder, str(value))

            return sql

        except Exception as e:
            self.logger.error(f"Error substituting parameters: {e}")
            return sql

    def execute_all_queries(self, parameters: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Execute all queries and perform raw data processing
        """
        results = {}
        
        try:
            # Step 1: Execute employee mapping query first
            if 'employee_mapping' in self.dynamic_queries:
                self.logger.info("Step 1: Creating employee mapping...")
                employee_data = self.execute_query('employee_mapping', parameters)
                results['employee_mapping'] = employee_data
                
                # Create mapping dictionary
                self.employee_mapping = {}
                for emp in employee_data:
                    empid = emp.get('EMPID')
                    empname = emp.get('EMPNAME', 'Unknown')
                    if empid:
                        self.employee_mapping[empid] = empname
                
                self.logger.info(f"Created employee mapping with {len(self.employee_mapping)} entries")

            # Step 2: Execute raw FFB data query
            if 'raw_ffb_data' in self.dynamic_queries:
                self.logger.info("Step 2: Extracting raw FFB data...")
                self.raw_ffb_data = self.execute_query('raw_ffb_data', parameters)
                results['raw_ffb_data'] = self.raw_ffb_data
                self.logger.info(f"Extracted {len(self.raw_ffb_data)} raw FFB records")

            # Step 3: Filter data by date range
            self.logger.info("Step 3: Filtering data by date range...")
            self.filtered_data = self._filter_by_date_range(
                self.raw_ffb_data, 
                parameters.get('start_date'), 
                parameters.get('end_date')
            )
            self.logger.info(f"Filtered to {len(self.filtered_data)} records within date range")

            # Step 4: Process data for different views
            self.logger.info("Step 4: Processing data for different views...")
            self.processed_data = self._process_filtered_data(self.filtered_data)

            # Step 5: Execute other queries
            for query_name in self.dynamic_queries:
                if query_name not in ['employee_mapping', 'raw_ffb_data']:
                    self.logger.info(f"Step 5: Executing query '{query_name}'...")
                    results[query_name] = self.execute_query(query_name, parameters)

            # Add processed data to results
            results.update(self.processed_data)

        except Exception as e:
            self.logger.error(f"Error executing queries: {e}")

        return results

    def _filter_by_date_range(self, data: List[Dict], start_date: str, end_date: str) -> List[Dict]:
        """Filter data by date range at application level"""
        if not data or not start_date or not end_date:
            return data

        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            filtered = []
            for record in data:
                trans_date = record.get('TRANSDATE')
                if trans_date:
                    if isinstance(trans_date, str):
                        try:
                            trans_dt = datetime.strptime(trans_date, '%Y-%m-%d').date()
                        except ValueError:
                            try:
                                trans_dt = datetime.strptime(trans_date, '%d/%m/%Y').date()
                            except ValueError:
                                continue
                    elif isinstance(trans_date, date):
                        trans_dt = trans_date
                    else:
                        continue
                    
                    if start_dt <= trans_dt <= end_dt:
                        filtered.append(record)
            
            return filtered

        except Exception as e:
            self.logger.error(f"Error filtering by date range: {e}")
            return data

    def _process_filtered_data(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        """Process filtered data into different views"""
        processed = {}
        
        try:
            # Daily performance data
            daily_data = self._group_by_date(data)
            processed['daily_performance'] = daily_data
            processed['processed_daily_data'] = daily_data

            # Employee performance data
            employee_data = self._group_by_employee(data)
            processed['employee_performance'] = employee_data
            processed['processed_employee_data'] = employee_data

            # Field performance data
            field_data = self._group_by_field(data)
            processed['field_performance'] = field_data
            processed['processed_field_data'] = field_data

            # Verification analysis
            verification_data = self._calculate_verification_rate(data)
            processed['verification_data'] = verification_data

        except Exception as e:
            self.logger.error(f"Error processing filtered data: {e}")

        return processed

    def _group_by_date(self, data: List[Dict]) -> List[Dict]:
        """Group data by transaction date"""
        daily_totals = defaultdict(lambda: {
            'TRANSDATE': '',
            'JUMLAH_TRANSAKSI': 0,
            'RIPE_BUNCHES': 0,
            'UNRIPE_BUNCHES': 0,
            'BLACK_BUNCHES': 0,
            'ROTTEN_BUNCHES': 0,
            'RAT_DAMAGE_BUNCHES': 0
        })

        for record in data:
            trans_date = record.get('TRANSDATE', '')
            if trans_date:
                daily_totals[trans_date]['TRANSDATE'] = trans_date
                daily_totals[trans_date]['JUMLAH_TRANSAKSI'] += 1
                daily_totals[trans_date]['RIPE_BUNCHES'] += record.get('RIPEBCH', 0)
                daily_totals[trans_date]['UNRIPE_BUNCHES'] += record.get('UNRIPEBCH', 0)
                daily_totals[trans_date]['BLACK_BUNCHES'] += record.get('BLACKBCH', 0)
                daily_totals[trans_date]['ROTTEN_BUNCHES'] += record.get('ROTTENBCH', 0)
                daily_totals[trans_date]['RAT_DAMAGE_BUNCHES'] += record.get('RATDMGBCH', 0)

        return list(daily_totals.values())

    def _group_by_employee(self, data: List[Dict]) -> List[Dict]:
        """Group data by employee and role"""
        employee_totals = defaultdict(lambda: {
            'EMPLOYEE_NAME': '',
            'RECORDTAG': '',
            'JUMLAH_TRANSAKSI': 0,
            'TOTAL_RIPE': 0,
            'TOTAL_UNRIPE': 0,
            'VERIFICATION_RATE': 0
        })

        for record in data:
            empid = record.get('SCANUSERID', '')
            recordtag = record.get('RECORDTAG', '')
            
            if empid and recordtag:
                key = f"{empid}_{recordtag}"
                employee_name = self.employee_mapping.get(empid, f"EMP_{empid}")
                
                employee_totals[key]['EMPLOYEE_NAME'] = employee_name
                employee_totals[key]['RECORDTAG'] = recordtag
                employee_totals[key]['JUMLAH_TRANSAKSI'] += 1
                employee_totals[key]['TOTAL_RIPE'] += record.get('RIPEBCH', 0)
                employee_totals[key]['TOTAL_UNRIPE'] += record.get('UNRIPEBCH', 0)

        # Calculate verification rates
        for emp_data in employee_totals.values():
            if emp_data['RECORDTAG'] != 'PM':
                emp_data['VERIFICATION_RATE'] = 100  # Non-PM records are considered verified
            else:
                emp_data['VERIFICATION_RATE'] = 0   # PM records need verification

        return list(employee_totals.values())

    def _group_by_field(self, data: List[Dict]) -> List[Dict]:
        """Group data by field/division"""
        field_totals = defaultdict(lambda: {
            'FIELDNAME': '',
            'JUMLAH_TRANSAKSI': 0,
            'TOTAL_RIPE': 0,
            'TOTAL_UNRIPE': 0
        })

        for record in data:
            divid = record.get('DIVID', '')
            fieldname = record.get('FIELDNAME', divid or 'Unknown Field')
            
            if divid:
                field_totals[divid]['FIELDNAME'] = fieldname
                field_totals[divid]['JUMLAH_TRANSAKSI'] += 1
                field_totals[divid]['TOTAL_RIPE'] += record.get('RIPEBCH', 0)
                field_totals[divid]['TOTAL_UNRIPE'] += record.get('UNRIPEBCH', 0)

        return list(field_totals.values())

    def _calculate_verification_rate(self, data: List[Dict]) -> List[Dict]:
        """Calculate verification rate based on PM vs non-PM records"""
        total_transactions = len(data)
        pm_transactions = len([r for r in data if r.get('RECORDTAG') == 'PM'])
        verified_transactions = total_transactions - pm_transactions
        
        verification_rate = (verified_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        return [{
            'total_transactions': total_transactions,
            'pm_transactions': pm_transactions,
            'verified_transactions': verified_transactions,
            'verification_rate': round(verification_rate, 2)
        }]

    def process_variables(self, query_results: Dict[str, List[Dict]], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced variable processing with raw data calculations
        """
        variables = {}

        try:
            # Process JSON variable definitions first
            if self.formula_data and 'variables' in self.formula_data:
                variables.update(self._process_json_variables(self.formula_data['variables'], query_results, parameters))

            # Calculate variables from processed data
            variables.update(self._calculate_summary_variables(query_results))

            # Add basic report info
            variables.update({
                'report_title': parameters.get('report_title', 'LAPORAN ANALISIS FRESH FRUIT BUNCH (FFB) - PGE 2B'),
                'estate_name': parameters.get('estate_name', 'PGE 2B'),
                'estate_code': parameters.get('estate_code', 'PGE_2B'),
                'report_period': f"{parameters.get('start_date', 'Unknown')} - {parameters.get('end_date', 'Unknown')}",
                'generated_date': datetime.now().strftime('%d %B %Y'),
                'generated_time': datetime.now().strftime('%H:%M:%S')
            })

        except Exception as e:
            self.logger.error(f"Error processing variables: {e}")

        return variables

    def _calculate_summary_variables(self, query_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Calculate summary variables from processed data"""
        variables = {}

        try:
            # Get data from filtered results
            filtered_data = self.filtered_data
            
            if filtered_data:
                # Calculate totals
                total_transactions = len(filtered_data)
                total_ripe = sum(record.get('RIPEBCH', 0) for record in filtered_data)
                total_unripe = sum(record.get('UNRIPEBCH', 0) for record in filtered_data)
                total_black = sum(record.get('BLACKBCH', 0) for record in filtered_data)
                total_rotten = sum(record.get('ROTTENBCH', 0) for record in filtered_data)
                total_ratdamage = sum(record.get('RATDMGBCH', 0) for record in filtered_data)
                
                # Calculate verification metrics
                verified_transactions = len([r for r in filtered_data if r.get('RECORDTAG') != 'PM'])
                
                # Calculate daily averages
                daily_data = query_results.get('daily_performance', [])
                num_days = len(daily_data) if daily_data else 1
                
                # Calculate performance metrics
                peak_day = 'Unknown'
                low_day = 'Unknown'
                if daily_data:
                    peak_record = max(daily_data, key=lambda x: x.get('JUMLAH_TRANSAKSI', 0))
                    low_record = min(daily_data, key=lambda x: x.get('JUMLAH_TRANSAKSI', 0))
                    peak_day = peak_record.get('TRANSDATE', 'Unknown')
                    low_day = low_record.get('TRANSDATE', 'Unknown')

                variables.update({
                    'total_transactions': total_transactions,
                    'total_ripe_bunches': total_ripe,
                    'total_unripe_bunches': total_unripe,
                    'total_black': total_black,
                    'total_rotten': total_rotten,
                    'total_ratdamage': total_ratdamage,
                    'verified_transactions': verified_transactions,
                    'avg_ripe_per_transaction': round(total_ripe / total_transactions, 2) if total_transactions > 0 else 0,
                    'daily_average_transactions': round(total_transactions / num_days, 2),
                    'daily_average_ripe': round(total_ripe / num_days, 2),
                    'quality_percentage': round((total_black + total_rotten + total_ratdamage) / total_ripe * 100, 2) if total_ripe > 0 else 0,
                    'verification_rate': round(verified_transactions / total_transactions * 100, 2) if total_transactions > 0 else 0,
                    'peak_performance_day': peak_day,
                    'low_performance_day': low_day
                })
            else:
                # Default values when no data
                variables.update({
                    'total_transactions': 0,
                    'total_ripe_bunches': 0,
                    'total_unripe_bunches': 0,
                    'total_black': 0,
                    'total_rotten': 0,
                    'total_ratdamage': 0,
                    'verified_transactions': 0,
                    'avg_ripe_per_transaction': 0,
                    'daily_average_transactions': 0.0,
                    'daily_average_ripe': 0.0,
                    'quality_percentage': 0,
                    'verification_rate': 0,
                    'peak_performance_day': 'No Data',
                    'low_performance_day': 'No Data'
                })

        except Exception as e:
            self.logger.error(f"Error calculating summary variables: {e}")

        return variables

    def _process_json_variables(self, variable_definitions: Dict, query_results: Dict[str, List[Dict]], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process variable definitions from JSON file"""
        variables = {}

        try:
            for section_name, section_vars in variable_definitions.items():
                if isinstance(section_vars, dict):
                    for var_name, var_def in section_vars.items():
                        if isinstance(var_def, dict):
                            var_type = var_def.get('type', 'static')
                            
                            if var_type == 'static':
                                variables[var_name] = var_def.get('value', '')
                            elif var_type == 'parameter':
                                param_name = var_def.get('value', var_name)
                                variables[var_name] = parameters.get(param_name, '')
                            elif var_type == 'dynamic':
                                if var_def.get('value') == 'current_date':
                                    fmt = var_def.get('format', '%Y-%m-%d')
                                    variables[var_name] = datetime.now().strftime(fmt)
                                elif var_def.get('value') == 'current_time':
                                    fmt = var_def.get('format', '%H:%M:%S')
                                    variables[var_name] = datetime.now().strftime(fmt)
                            elif var_type == 'formatting':
                                template = var_def.get('template', '')
                                template_params = var_def.get('parameters', [])
                                format_values = {p: parameters.get(p, '') for p in template_params}
                                variables[var_name] = template.format(**format_values)

        except Exception as e:
            self.logger.error(f"Error processing JSON variables: {e}")

        return variables

    def get_repeating_data(self, query_results: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Get data for repeating sections"""
        repeating_data = {}
        
        for section_name, section_def in self.repeating_sections.items():
            data_source = section_def.get('data_source', section_name.lower())
            if data_source in query_results:
                repeating_data[section_name] = query_results[data_source]
            else:
                self.logger.warning(f"Data source '{data_source}' not found for section '{section_name}'")
                repeating_data[section_name] = []

        return repeating_data

    def validate_data_completeness(self, query_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Enhanced data validation"""
        validation = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'data_summary': {}
        }

        try:
            # Check if we have raw data
            if not self.raw_ffb_data:
                validation['errors'].append("No raw FFB data found")
                validation['is_valid'] = False
            else:
                validation['data_summary']['raw_records'] = len(self.raw_ffb_data)

            # Check if we have filtered data
            if not self.filtered_data:
                validation['warnings'].append("No data found in specified date range")
            else:
                validation['data_summary']['filtered_records'] = len(self.filtered_data)

            # Check employee mapping
            if not self.employee_mapping:
                validation['warnings'].append("No employee mapping available")
            else:
                validation['data_summary']['mapped_employees'] = len(self.employee_mapping)

            # Check processed data
            for key, data in self.processed_data.items():
                if not data:
                    validation['warnings'].append(f"No data for {key}")
                else:
                    validation['data_summary'][key] = len(data)

        except Exception as e:
            validation['errors'].append(f"Validation error: {e}")
            validation['is_valid'] = False

        return validation


def main():
    """Test function"""
    print("Enhanced Dynamic Formula Engine")
    print("Supports raw data processing and corrected algorithms")


if __name__ == "__main__":
    main()