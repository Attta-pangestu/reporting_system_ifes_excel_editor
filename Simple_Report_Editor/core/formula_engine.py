"""
Formula Engine Module
Memproses formula JSON untuk eksekusi query dan variable processing
"""

import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Union, Tuple
from .database_connector import FirebirdConnectorEnhanced

logger = logging.getLogger(__name__)

class FormulaEngine:
    """Engine untuk memproses formula JSON dan eksekusi query"""

    def __init__(self, database_connector: FirebirdConnectorEnhanced = None):
        """
        Inisialisasi Formula Engine

        Args:
            database_connector: Instance database connector
        """
        self.formula_config = None
        self.database_connector = database_connector
        self.variables = {}

    def load_formula(self, formula_path: str) -> bool:
        """
        Load konfigurasi formula dari JSON file

        Args:
            formula_path: Path ke file JSON formula

        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            if not os.path.exists(formula_path):
                logger.error(f"Formula file not found: {formula_path}")
                return False

            with open(formula_path, 'r', encoding='utf-8') as f:
                self.formula_config = json.load(f)

            logger.info(f"Formula loaded: {formula_path}")
            return True

        except Exception as e:
            logger.error(f"Error loading formula: {e}")
            return False

    def get_formula_info(self) -> Dict[str, Any]:
        """
        Get informasi tentang formula configuration

        Returns:
            Dictionary dengan informasi formula
        """
        if not self.formula_config:
            return {}

        queries = self.formula_config.get('queries', {})
        variables = self.formula_config.get('variables', {})

        return {
            'template_info': self.formula_config.get('template_info', {}),
            'query_count': len(queries),
            'variable_count': len(variables),
            'queries': list(queries.keys()),
            'variables': list(variables.keys()),
            'database_config': self.formula_config.get('database_config', {})
        }

    def generate_table_name(self, start_date: str) -> str:
        """
        Generate table name dari start_date (FFBSCANNERDATA{MM})

        Args:
            start_date: Tanggal mulai (YYYY-MM-DD format)

        Returns:
            Table name dalam format FFBSCANNERDATA{MM}
        """
        try:
            from datetime import datetime
            date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            month = date_obj.month

            # Format dengan 2 digit (01, 02, ..., 12)
            month_str = f"{month:02d}"
            table_name = f"FFBSCANNERDATA{month_str}"

            logger.info(f"Generated table name: {table_name} for date: {start_date}")
            return table_name

        except Exception as e:
            logger.error(f"Error generating table name from {start_date}: {e}")
            # Fallback ke default table
            return "FFBSCANNERDATA04"

    def execute_queries(self, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute semua queries dari formula configuration

        Args:
            parameters: Parameters untuk query substitution

        Returns:
            Dictionary dengan hasil query
        """
        if not self.formula_config:
            raise ValueError("Formula config not loaded")

        if not self.database_connector:
            raise ValueError("Database connector not provided")

        results = {}
        queries = self.formula_config.get('queries', {})

        # Prepare default parameters
        default_params = {
            'start_date': None,
            'end_date': None
        }

        if parameters:
            default_params.update(parameters)

        # Auto-generate table_name jika start_date ada
        if default_params.get('start_date') and not default_params.get('table_name'):
            default_params['table_name'] = self.generate_table_name(default_params['start_date'])

        for query_name, query_config in queries.items():
            try:
                logger.info(f"Executing query: {query_name}")
                sql = query_config['sql']
                return_format = query_config.get('return_format', 'dict')

                result = self.database_connector.execute_query(sql, default_params, return_format)
                results[query_name] = result

                # Log result info
                if result:
                    if isinstance(result, list):
                        logger.info(f"Query {query_name} returned {len(result)} results")
                    elif isinstance(result, dict) and 'rows' in result:
                        logger.info(f"Query {query_name} returned {len(result.get('rows', []))} rows")
                else:
                    logger.warning(f"Query {query_name} returned no results")

            except Exception as e:
                logger.error(f"Error executing query {query_name}: {e}")
                results[query_name] = None

        return results

    def process_variables(self, query_results: Dict[str, Any], parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process variables dari query results

        Args:
            query_results: Hasil dari execute_queries
            parameters: Parameters yang digunakan

        Returns:
            Dictionary dengan processed variables
        """
        if not self.formula_config:
            raise ValueError("Formula config not loaded")

        variables = {}
        variables_config = self.formula_config.get('variables', {})

        for var_name, var_config in variables_config.items():
            try:
                var_type = var_config.get('type')
                processed_value = None

                if var_type == 'constant':
                    processed_value = var_config.get('value')

                elif var_type == 'direct':
                    source = var_config.get('source')
                    if source in query_results:
                        processed_value = query_results[source]

                elif var_type == 'formatting':
                    processed_value = self._process_formatting_variable(var_config)

                elif var_type == 'calculation':
                    # Special handling for summary variables
                    if var_name == 'summary':
                        # Get summary data from query results
                        summary_data = query_results.get('summary_stats', {})
                        if summary_data and 'rows' in summary_data and summary_data['rows']:
                            first_row = summary_data['rows'][0]
                            # Convert all values to ensure they're accessible
                            processed_value = {}
                            for key, value in first_row.items():
                                processed_value[key] = value if value is not None else 0
                        else:
                            # Default empty summary if no data
                            processed_value = {
                                'total_records': 0,
                                'total_ripe_bunch': 0,
                                'total_unripe_bunch': 0,
                                'total_black_bunch': 0,
                                'total_rotten_bunch': 0,
                                'total_long_stalk_bunch': 0,
                                'total_rat_damage_bunch': 0,
                                'total_loose_fruit': 0,
                                'total_loose_fruit_2': 0,
                                'total_underripe_bunch': 0,
                                'total_overripe_bunch': 0,
                                'total_abnormal_bunch': 0,
                                'date_range': 'No data',
                                'unique_workers': 0,
                                'unique_fields': 0
                            }
                    else:
                        processed_value = self._process_calculation_variable(var_config, query_results, parameters)

                elif var_type == 'conditional':
                    processed_value = self._process_conditional_variable(var_config, query_results, parameters)

                variables[var_name] = processed_value

            except Exception as e:
                logger.warning(f"Error processing variable {var_name}: {e}")
                variables[var_name] = f"Error: {str(e)}"

        return variables

    def _process_formatting_variable(self, var_config: Dict[str, Any]) -> str:
        """Process formatting type variable"""
        source = var_config.get('source', '')
        format_str = var_config.get('format', '')

        if source == 'TODAY()':
            value = date.today()
        elif source == 'NOW()':
            value = datetime.now()
        else:
            value = source

        if format_str and value:
            # Convert Excel-style format to Python strftime
            python_format = format_str.replace('MMMM', '%B').replace('dddd', '%A') \
                                   .replace('yyyy', '%Y').replace('MM', '%m') \
                                   .replace('dd', '%d').replace('HH', '%H') \
                                   .replace('mm', '%M').replace('ss', '%S')
            return value.strftime(python_format)
        else:
            return str(value)

    def _process_calculation_variable(self, var_config: Dict[str, Any], query_results: Dict[str, Any], parameters: Dict[str, Any]) -> Any:
        """Process calculation type variable"""
        formula = var_config.get('formula', '')
        nested_vars = var_config.get('variables', {})

        if nested_vars:
            # Process nested variables
            processed_nested = {}
            for nested_name, nested_source in nested_vars.items():
                if '.' in nested_source:
                    # Handle nested references like summary_stats.total_records
                    parts = nested_source.split('.')
                    value = self._get_nested_value(query_results, parts)
                    processed_nested[nested_name] = value
                else:
                    processed_nested[nested_name] = query_results.get(nested_source)

            # Add parameters to processed_nested for formula access
            if parameters:
                for param_name, param_value in parameters.items():
                    if param_name not in processed_nested:
                        processed_nested[param_name] = param_value

            # Simple formula processing
            if 'IF(' in formula:
                return self._process_if_formula(formula, processed_nested)
            else:
                return formula

        # For simple formulas without nested vars, try direct processing
        if 'IF(' in formula:
            # Create variables dict from parameters
            variables = parameters.copy() if parameters else {}
            return self._process_if_formula(formula, variables)

        return formula

    def _process_conditional_variable(self, var_config: Dict[str, Any], query_results: Dict[str, Any], parameters: Dict[str, Any]) -> Any:
        """Process conditional type variable"""
        conditions = var_config.get('conditions', [])
        default_value = var_config.get('default', '')

        for condition in conditions:
            condition_expr = condition.get('condition', '')
            value = condition.get('value', '')

            # Simple condition evaluation
            if self._evaluate_condition(condition_expr, query_results, parameters):
                return value

        return default_value

    def _process_if_formula(self, formula: str, variables: Dict[str, Any]) -> str:
        """Process simple IF formula with MONTH() and YEAR() support"""
        try:
            # Handle IF(ISBLANK(start_date), "value1", "value2")
            if 'ISBLANK(start_date)' in formula:
                start_date = variables.get('start_date')
                if start_date and str(start_date).strip():  # Check if not None or empty
                    # Return second value
                    return self._process_formula_value(formula, variables, return_part=2)
                else:
                    # Return first value
                    return self._process_formula_value(formula, variables, return_part=1)

            # Handle other simple IF conditions
            elif 'IF(' in formula:
                # Extract condition and values
                parts = formula.split(',')
                if len(parts) >= 3:
                    condition = parts[0].replace('IF(', '').strip()
                    true_value = parts[1].strip()
                    false_value = parts[2].strip().rstrip(')')

                    # Evaluate condition (simplified)
                    if self._evaluate_simple_condition(condition, variables):
                        return self._process_formula_expression(true_value, variables)
                    else:
                        return self._process_formula_expression(false_value, variables)

        except Exception as e:
            logger.warning(f"Error processing IF formula: {e}")

        return ""

    def _process_formula_value(self, formula: str, variables: Dict[str, Any], return_part: int) -> str:
        """Extract and process specific part from IF formula"""
        try:
            parts = formula.split(',')
            if len(parts) >= return_part:
                value = parts[return_part - 1].strip()
                if return_part == 3:  # Last part - remove trailing )
                    value = value.rstrip(')')
                return self._process_formula_expression(value, variables)
        except Exception as e:
            logger.warning(f"Error processing formula value: {e}")
        return ""

    def _process_formula_expression(self, expression: str, variables: Dict[str, Any]) -> str:
        """Process formula expression with MONTH() and YEAR() support"""
        try:
            from datetime import datetime

            # Handle MONTH() function
            if 'MONTH(' in expression:
                # Extract date parameter
                if 'MONTH(TODAY())' in expression:
                    today = datetime.now()
                    month_name = today.strftime('%B')
                    expression = expression.replace('MONTH(TODAY())', month_name)
                elif 'MONTH(start_date)' in expression:
                    start_date = variables.get('start_date')
                    if start_date:
                        try:
                            date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                            month_name = date_obj.strftime('%B')
                            expression = expression.replace('MONTH(start_date)', month_name)
                        except ValueError:
                            pass

            # Handle YEAR() function
            if 'YEAR(' in expression:
                # Extract date parameter
                if 'YEAR(TODAY())' in expression:
                    today = datetime.now()
                    year_str = str(today.year)
                    expression = expression.replace('YEAR(TODAY())', year_str)
                elif 'YEAR(start_date)' in expression:
                    start_date = variables.get('start_date')
                    if start_date:
                        try:
                            date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                            year_str = str(date_obj.year)
                            expression = expression.replace('YEAR(start_date)', year_str)
                        except ValueError:
                            pass

            # Handle TODAY() function
            if 'TODAY()' in expression:
                today = datetime.now()
                today_str = today.strftime('%Y-%m-%d')
                expression = expression.replace('TODAY()', today_str)

            # Remove quotes and clean up
            expression = expression.replace('"', '').replace("'", "").strip()

            return expression

        except Exception as e:
            logger.warning(f"Error processing formula expression: {e}")
            return expression.replace('"', '').replace("'", "").strip()

    def _get_nested_value(self, data: Dict[str, Any], parts: List[str]) -> Any:
        """Get nested value from dictionary, handling query results format"""
        current = data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list) and current and part.isdigit():
                idx = int(part)
                if 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return None
            else:
                # Handle case where data is in Firebird result format
                if isinstance(current, dict) and 'rows' in current:
                    # Try to get value from first row
                    rows = current.get('rows', [])
                    if rows and len(rows) > 0:
                        first_row = rows[0]
                        if part in first_row:
                            current = first_row[part]
                        else:
                            return None
                    else:
                        return None
                else:
                    return None

        return current

    def _evaluate_condition(self, condition: str, query_results: Dict[str, Any], parameters: Dict[str, Any]) -> bool:
        """Evaluate condition expression"""
        try:
            # Simple condition evaluation
            if 'ISBLANK' in condition:
                var_name = condition.replace('ISBLANK(', '').replace(')', '').strip()
                return parameters.get(var_name) is None

            # Add more condition types as needed
            return False
        except:
            return False

    def _evaluate_simple_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """Evaluate simple condition"""
        try:
            # Very basic evaluation - can be expanded
            if '=' in condition:
                left, right = condition.split('=', 1)
                left_val = variables.get(left.strip(), '')
                right_val = right.strip().replace('"', '').replace("'", "")
                return str(left_val) == str(right_val)
        except:
            pass
        return False

    def validate_data_availability(self, query_results: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validasi ketersediaan data untuk report generation

        Args:
            query_results: Hasil dari execute_queries

        Returns:
            Tuple (is_valid, warning_messages)
        """
        if not self.formula_config:
            return False, ["Formula config not loaded"]

        warnings = []
        validations = self.formula_config.get('validations', {})
        required_data = validations.get('required_data', [])

        for validation in required_data:
            query_name = validation.get('query')
            min_records = validation.get('min_records', 1)
            error_message = validation.get('error_message', f"Query {query_name} tidak mengembalikan data")

            if query_name in query_results:
                result = query_results[query_name]

                if not result:
                    warnings.append(error_message)
                    continue

                record_count = 0
                if isinstance(result, list):
                    if result and 'rows' in result[0]:
                        record_count = len(result[0]['rows'])
                    else:
                        record_count = len(result)
                elif isinstance(result, dict) and 'rows' in result:
                    record_count = len(result['rows'])

                if record_count < min_records:
                    warnings.append(f"{error_message} (hanya {record_count} records)")
            else:
                warnings.append(f"Query {query_name} tidak dieksekusi")

        is_valid = len(warnings) == 0
        return is_valid, warnings

    def validate_formula(self) -> Tuple[bool, List[str]]:
        """
        Validasi formula configuration

        Returns:
            Tuple (is_valid, error_messages)
        """
        if not self.formula_config:
            return False, ["Formula config not loaded"]

        errors = []

        # Check required sections
        if 'queries' not in self.formula_config:
            errors.append("Missing 'queries' section")

        if 'variables' not in self.formula_config:
            errors.append("Missing 'variables' section")

        # Validate queries
        queries = self.formula_config.get('queries', {})
        for query_name, query_config in queries.items():
            if 'sql' not in query_config:
                errors.append(f"Query '{query_name}' missing SQL statement")
            if 'type' not in query_config:
                errors.append(f"Query '{query_name}' missing type")

        # Validate variables
        variables = self.formula_config.get('variables', {})
        for var_name, var_config in variables.items():
            if 'type' not in var_config:
                errors.append(f"Variable '{var_name}' missing type")

        is_valid = len(errors) == 0
        return is_valid, errors

    def get_database_config(self) -> Dict[str, Any]:
        """
        Get database configuration dari formula

        Returns:
            Database configuration dictionary
        """
        if not self.formula_config:
            return {}

        return self.formula_config.get('database_config', {})

    def get_output_settings(self) -> Dict[str, Any]:
        """
        Get output settings dari formula

        Returns:
            Output settings dictionary
        """
        if not self.formula_config:
            return {}

        return self.formula_config.get('output_settings', {})