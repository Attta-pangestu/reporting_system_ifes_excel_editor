#!/usr/bin/env python3
"""
Formula Engine - Template-based Data Processing Engine
====================================================

Menangani ekstraksi data, pemrosesan, dan perhitungan berdasarkan formula JSON.
Mendukung query SQL, variabel dinamis, dan section berulang.

Author: Claude AI Assistant
Version: 1.0.0
"""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
from pathlib import Path

class FormulaEngine:
    """
    Engine untuk memproses formula JSON dan mengeksekusi query database.

    Features:
    - SQL query execution dengan parameter dinamis
    - Variable calculation dan formatting
    - Repeating sections untuk data tables
    - Data validation dan error handling
    """

    def __init__(self, config: Dict = None):
        """
        Initialize Formula Engine

        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.db_connector = None
        self.query_results = {}
        self.processed_variables = {}

    def load_formula(self, formula_path: str) -> Dict:
        """
        Load formula dari file JSON

        Args:
            formula_path: Path ke file formula JSON

        Returns:
            Dictionary berisi data formula
        """
        try:
            with open(formula_path, 'r', encoding='utf-8') as f:
                formula_data = json.load(f)

            self.logger.info(f"Formula loaded: {formula_path}")
            return formula_data

        except Exception as e:
            self.logger.error(f"Error loading formula {formula_path}: {e}")
            raise

    def set_database_connector(self, db_connector):
        """
        Set database connector untuk query execution

        Args:
            db_connector: Database connector instance
        """
        self.db_connector = db_connector

    def execute_queries(self, formula_data: Dict, params: Dict = None) -> Dict:
        """
        Eksekusi semua queries yang didefinisikan dalam formula

        Args:
            formula_data: Formula data dictionary
            params: Parameters untuk substitution

        Returns:
            Dictionary hasil query
        """
        if not self.db_connector:
            raise ValueError("Database connector not set")

        params = params or {}
        queries = formula_data.get('queries', {})
        results = {}

        self.logger.info(f"Executing {len(queries)} queries")

        for query_name, query_config in queries.items():
            try:
                self.logger.info(f"Executing query: {query_name}")

                # Get SQL template
                sql_template = query_config.get('sql', '')

                # Substitute parameters
                sql = self._substitute_parameters(sql_template, params)

                # Execute query
                query_result = self.db_connector.execute_query(sql)

                # Process result based on return format
                return_format = query_config.get('return_format', 'dict')

                if return_format == 'dict':
                    results[query_name] = query_result
                elif return_format == 'dataframe':
                    results[query_name] = pd.DataFrame(query_result)
                elif return_format == 'single_value':
                    results[query_name] = query_result[0] if query_result else None

                self.logger.info(f"Query {query_name} completed: {len(query_result) if query_result else 0} records")

            except Exception as e:
                self.logger.error(f"Error executing query {query_name}: {e}")
                results[query_name] = None

        self.query_results = results
        return results

    def _substitute_parameters(self, template: str, params: Dict) -> str:
        """
        Substitute parameters dalam SQL template

        Args:
            template: SQL template dengan placeholders
            params: Parameter values

        Returns:
            SQL string dengan parameters yang sudah disubstitusi
        """
        result = template

        # Replace {parameter} dengan values
        for param_name, param_value in params.items():
            placeholder = f'{{{param_name}}}'
            result = result.replace(placeholder, str(param_value))

        return result

    def process_variables(self, formula_data: Dict, query_results: Dict = None) -> Dict:
        """
        Process variables berdasarkan formula definition

        Args:
            formula_data: Formula data dictionary
            query_results: Hasil query execution

        Returns:
            Dictionary processed variables
        """
        query_results = query_results or self.query_results
        variables_config = formula_data.get('variables', {})
        processed_vars = {}

        self.logger.info(f"Processing {len(variables_config)} variables")

        for var_name, var_config in variables_config.items():
            try:
                var_type = var_config.get('type', 'direct')

                if var_type == 'constant':
                    processed_vars[var_name] = var_config.get('value', '')

                elif var_type == 'direct':
                    source = var_config.get('source', '')
                    processed_vars[var_name] = self._get_direct_value(source, query_results)

                elif var_type == 'calculation':
                    processed_vars[var_name] = self._process_calculation(var_config, query_results)

                elif var_type == 'formatting':
                    processed_vars[var_name] = self._process_formatting(var_config)

                self.logger.debug(f"Variable {var_name} processed: {type(processed_vars[var_name])}")

            except Exception as e:
                self.logger.error(f"Error processing variable {var_name}: {e}")
                processed_vars[var_name] = None

        self.processed_variables = processed_vars
        return processed_vars

    def _get_direct_value(self, source: str, query_results: Dict) -> Any:
        """
        Get direct value dari query results

        Args:
            source: Source path (query.field)
            query_results: Query results dictionary

        Returns:
            Value dari source
        """
        try:
            # Parse source path (query.field or query.field[index])
            if '.' in source:
                query_name, field_path = source.split('.', 1)

                if query_name in query_results and query_results[query_name]:
                    result_data = query_results[query_name]

                    # Handle single value vs list
                    if isinstance(result_data, list) and len(result_data) > 0:
                        # If it's a list, get first item
                        if isinstance(result_data[0], dict):
                            return result_data[0].get(field_path)
                        else:
                            return result_data[0]
                    elif isinstance(result_data, dict):
                        return result_data.get(field_path)
                    else:
                        return result_data
                else:
                    return None
            else:
                # Direct query name
                return query_results.get(source)

        except Exception as e:
            self.logger.error(f"Error getting direct value from {source}: {e}")
            return None

    def _process_calculation(self, var_config: Dict, query_results: Dict) -> Any:
        """
        Process calculation variable

        Args:
            var_config: Variable configuration
            query_results: Query results

        Returns:
            Calculated value
        """
        try:
            formula = var_config.get('formula', '')
            variables = var_config.get('variables', {})

            # Get values for variables in calculation
            calc_values = {}
            for var_name, source_path in variables.items():
                calc_values[var_name] = self._get_direct_value(source_path, query_results)

            # Simple formula evaluation (extend as needed)
            if 'IF' in formula:
                return self._evaluate_conditional(formula, calc_values)
            elif '+' in formula or '-' in formula or '*' in formula or '/' in formula:
                return self._evaluate_arithmetic(formula, calc_values)
            else:
                # Simple string concatenation or function call
                return self._evaluate_expression(formula, calc_values)

        except Exception as e:
            self.logger.error(f"Error processing calculation: {e}")
            return None

    def _process_formatting(self, var_config: Dict) -> str:
        """
        Process formatting variable

        Args:
            var_config: Variable configuration

        Returns:
            Formatted string
        """
        try:
            source = var_config.get('source', '')
            format_string = var_config.get('format', '')

            if source == 'TODAY()':
                value = datetime.now()
            elif source == 'NOW()':
                value = datetime.now()
            else:
                value = source

            # Format based on format string
            if format_string:
                if format_string == 'dd MMMM yyyy':
                    return value.strftime('%d %B %Y')
                elif format_string == 'dd-MM-yyyy HH:mm:ss':
                    return value.strftime('%d-%m-%Y %H:%M:%S')
                elif format_string == 'MMMM yyyy':
                    return value.strftime('%B %Y')
                else:
                    # Try Python strftime
                    try:
                        return value.strftime(format_string)
                    except:
                        return str(value)
            else:
                return str(value)

        except Exception as e:
            self.logger.error(f"Error processing formatting: {e}")
            return str(source) if 'source' in locals() else ''

    def _evaluate_conditional(self, formula: str, values: Dict) -> Any:
        """
        Evaluate conditional formula

        Args:
            formula: Conditional formula string
            values: Variable values

        Returns:
            Evaluated result
        """
        try:
            # Simple IF evaluation: IF(condition, true_value, false_value)
            if_match = re.match(r'IF\(([^,]+),\s*([^,]+),\s*([^)]+)\)', formula, re.IGNORECASE)

            if if_match:
                condition, true_val, false_val = if_match.groups()

                # Evaluate condition
                condition_result = self._evaluate_condition(condition, values)

                if condition_result:
                    return self._evaluate_expression(true_val, values)
                else:
                    return self._evaluate_expression(false_val, values)
            else:
                return self._evaluate_expression(formula, values)

        except Exception as e:
            self.logger.error(f"Error evaluating conditional: {e}")
            return None

    def _evaluate_condition(self, condition: str, values: Dict) -> bool:
        """
        Evaluate condition string

        Args:
            condition: Condition string
            values: Variable values

        Returns:
            Boolean result
        """
        try:
            # Simple condition evaluation
            condition = condition.strip()

            # Handle ISBLANK function
            if condition.startswith('ISBLANK('):
                var_name = condition[8:-1].strip()
                return values.get(var_name) is None or values.get(var_name) == ''

            # Handle simple comparisons
            for op in ['>=', '<=', '!=', '==', '>', '<']:
                if op in condition:
                    left, right = condition.split(op, 1)
                    left_val = self._evaluate_expression(left.strip(), values)
                    right_val = self._evaluate_expression(right.strip(), values)

                    if op == '>=':
                        return left_val >= right_val
                    elif op == '<=':
                        return left_val <= right_val
                    elif op == '!=':
                        return left_val != right_val
                    elif op == '==':
                        return left_val == right_val
                    elif op == '>':
                        return left_val > right_val
                    elif op == '<':
                        return left_val < right_val

            # Default: evaluate as boolean
            result = self._evaluate_expression(condition, values)
            return bool(result)

        except Exception as e:
            self.logger.error(f"Error evaluating condition '{condition}': {e}")
            return False

    def _evaluate_arithmetic(self, formula: str, values: Dict) -> float:
        """
        Evaluate arithmetic expression

        Args:
            formula: Arithmetic formula
            values: Variable values

        Returns:
            Numeric result
        """
        try:
            # Replace variables with values
            expression = formula
            for var_name, var_value in values.items():
                if var_value is not None:
                    expression = expression.replace(var_name, str(var_value))

            # Safe evaluation
            return eval(expression, {"__builtins__": {}}, {})

        except Exception as e:
            self.logger.error(f"Error evaluating arithmetic '{formula}': {e}")
            return 0.0

    def _evaluate_expression(self, expression: str, values: Dict) -> Any:
        """
        Evaluate general expression

        Args:
            expression: Expression string
            values: Variable values

        Returns:
            Evaluated result
        """
        try:
            # Replace variables with values
            result = expression

            # Handle MONTH(), YEAR(), TODAY() functions
            result = result.replace('MONTH(TODAY())', str(datetime.now().month))
            result = result.replace('YEAR(TODAY())', str(datetime.now().year))
            result = result.replace('TODAY()', f"'{datetime.now().strftime('%Y-%m-%d')}'")

            # Replace variable references
            for var_name, var_value in values.items():
                if var_value is not None:
                    result = result.replace(var_name, str(var_value))

            # Handle string concatenation with &
            result = result.replace('&', '+')

            # Evaluate if it's an expression
            if any(op in result for op in ['+', '-', '*', '/', '(', ')']):
                return eval(result, {"__builtins__": {}}, {})
            else:
                return result

        except Exception as e:
            self.logger.error(f"Error evaluating expression '{expression}': {e}")
            return expression

    def get_repeating_sections(self, formula_data: Dict) -> Dict:
        """
        Get repeating sections configuration

        Args:
            formula_data: Formula data dictionary

        Returns:
            Dictionary repeating sections config
        """
        return formula_data.get('repeating_sections', {})

    def validate_data(self, data: List[Dict], validations: Dict) -> List[str]:
        """
        Validate data against validation rules

        Args:
            data: Data to validate
            validations: Validation rules

        Returns:
            List of validation errors
        """
        errors = []

        if not validations or not data:
            return errors

        required_fields = validations.get('required_fields', [])
        numeric_fields = validations.get('numeric_fields', [])
        date_fields = validations.get('date_fields', [])

        for i, row in enumerate(data):
            # Check required fields
            for field in required_fields:
                if field not in row or row[field] is None or row[field] == '':
                    errors.append(f"Row {i+1}: Missing required field '{field}'")

            # Check numeric fields
            for field in numeric_fields:
                if field in row and row[field] is not None:
                    try:
                        float(row[field])
                    except (ValueError, TypeError):
                        errors.append(f"Row {i+1}: Field '{field}' should be numeric")

            # Check date fields
            for field in date_fields:
                if field in row and row[field] is not None:
                    try:
                        # Try to parse as date
                        if isinstance(row[field], str):
                            datetime.strptime(row[field], '%Y-%m-%d')
                    except ValueError:
                        errors.append(f"Row {i+1}: Field '{field}' has invalid date format")

        return errors

    def get_summary_statistics(self, data: List[Dict]) -> Dict:
        """
        Generate summary statistics for data

        Args:
            data: Data to summarize

        Returns:
            Dictionary summary statistics
        """
        if not data:
            return {}

        summary = {
            'total_records': len(data),
            'numeric_summaries': {},
            'unique_counts': {}
        }

        # Get numeric fields
        if data:
            for field in data[0].keys():
                values = [row.get(field) for row in data if row.get(field) is not None]

                if values:
                    # Try to determine if field is numeric
                    try:
                        numeric_values = [float(v) for v in values]
                        if numeric_values:
                            summary['numeric_summaries'][field] = {
                                'count': len(numeric_values),
                                'sum': sum(numeric_values),
                                'average': sum(numeric_values) / len(numeric_values),
                                'min': min(numeric_values),
                                'max': max(numeric_values)
                            }
                    except (ValueError, TypeError):
                        # Not numeric, count unique values
                        summary['unique_counts'][field] = len(set(values))

        return summary

    def export_results(self, output_path: str, format_type: str = 'excel') -> bool:
        """
        Export results to file

        Args:
            output_path: Output file path
            format_type: Export format ('excel', 'json', 'csv')

        Returns:
            True if successful, False otherwise
        """
        try:
            if format_type.lower() == 'excel':
                return self._export_to_excel(output_path)
            elif format_type.lower() == 'json':
                return self._export_to_json(output_path)
            elif format_type.lower() == 'csv':
                return self._export_to_csv(output_path)
            else:
                self.logger.error(f"Unsupported export format: {format_type}")
                return False

        except Exception as e:
            self.logger.error(f"Error exporting results: {e}")
            return False

    def _export_to_excel(self, output_path: str) -> bool:
        """Export to Excel format"""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for query_name, data in self.query_results.items():
                    if data and len(data) > 0:
                        df = pd.DataFrame(data)
                        df.to_excel(writer, sheet_name=query_name[:31], index=False)

            self.logger.info(f"Results exported to Excel: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {e}")
            return False

    def _export_to_json(self, output_path: str) -> bool:
        """Export to JSON format"""
        try:
            export_data = {
                'query_results': self.query_results,
                'processed_variables': self.processed_variables,
                'export_timestamp': datetime.now().isoformat()
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)

            self.logger.info(f"Results exported to JSON: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {e}")
            return False

    def _export_to_csv(self, output_path: str) -> bool:
        """Export to CSV format (main query only)"""
        try:
            # Find main data query
            main_data = None
            for query_name, data in self.query_results.items():
                if 'main' in query_name.lower() or data is not None:
                    main_data = data
                    break

            if main_data and len(main_data) > 0:
                df = pd.DataFrame(main_data)
                df.to_csv(output_path, index=False)
                self.logger.info(f"Results exported to CSV: {output_path}")
                return True
            else:
                self.logger.error("No data to export to CSV")
                return False

        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            return False