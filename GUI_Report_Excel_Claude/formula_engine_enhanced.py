"""
Enhanced Formula Engine untuk Data Processing
Menangani eksekusi formula, query database, dan data transformation dengan debug logging yang lebih baik
"""

import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date, timedelta
import re
import logging
from firebird_connector_enhanced import FirebirdConnectorEnhanced as FirebirdConnector

class FormulaEngineEnhanced:
    """
    Enhanced formula engine dengan debug logging dan perbaikan processing
    """

    def __init__(self, formula_path: str, db_connector: FirebirdConnector):
        """
        Inisialisasi formula engine

        Args:
            formula_path: Path ke file formula definition JSON
            db_connector: Instance FirebirdConnector
        """
        self.formula_path = formula_path
        self.db_connector = db_connector
        self.formulas = {}
        self.data_cache = {}
        self.variables_cache = {}

        # Setup enhanced logging
        self._setup_enhanced_logging()

        # Load formulas
        self._load_formulas()

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

    def _load_formulas(self):
        """Load formula definitions dari file JSON dengan debug"""
        try:
            self.logger.info(f"Loading formulas from: {self.formula_path}")
            with open(self.formula_path, 'r', encoding='utf-8') as f:
                self.formulas = json.load(f)

            queries_count = len(self.formulas.get('queries', {}))
            variables_count = sum(len(vars) for vars in self.formulas.get('variables', {}).values())

            self.logger.info(f"Formulas loaded successfully: {queries_count} queries, {variables_count} variables")

            # Debug: Log semua query names
            queries = self.formulas.get('queries', {})
            for query_name in queries.keys():
                self.logger.debug(f"Found query: {query_name}")

        except Exception as e:
            self.logger.error(f"Error loading formulas: {e}")
            raise

    def execute_all_queries(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute semua queries dengan debug logging dan parameter substitution

        Args:
            parameters: Parameter untuk query (start_date, end_date, estate, dll)

        Returns:
            Dictionary berisi hasil semua query
        """
        results = {}
        queries = self.formulas.get('queries', {})

        self.logger.info(f"=== EXECUTING ALL QUERIES ===")
        self.logger.info(f"Parameters: {parameters}")
        self.logger.info(f"Found {len(queries)} queries to execute")

        for query_name, query_config in queries.items():
            try:
                self.logger.info(f"--- Executing query: {query_name} ---")
                result = self.execute_query(query_name, parameters)
                results[query_name] = result

                # Log result summary
                if result:
                    if isinstance(result, list) and len(result) > 0:
                        if isinstance(result[0], dict) and 'rows' in result[0]:
                            rows_count = len(result[0]['rows'])
                            self.logger.info(f"Query {query_name} executed successfully: {rows_count} rows")
                        else:
                            self.logger.info(f"Query {query_name} executed successfully: {len(result)} items")
                    elif isinstance(result, pd.DataFrame):
                        self.logger.info(f"Query {query_name} executed successfully: {len(result)} rows")
                    else:
                        self.logger.info(f"Query {query_name} executed successfully: {type(result)}")
                else:
                    self.logger.warning(f"Query {query_name} returned no results")

            except Exception as e:
                self.logger.error(f"Error executing query {query_name}: {e}", exc_info=True)
                results[query_name] = None

        self.logger.info(f"=== QUERY EXECUTION COMPLETED ===")
        return results

    def execute_query(self, query_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute single query dengan parameter substitution yang benar

        Args:
            query_name: Nama query
            parameters: Parameter untuk query

        Returns:
            Query result
        """
        queries = self.formulas.get('queries', {})
        if query_name not in queries:
            raise ValueError(f"Query {query_name} not found in formulas")

        query_config = queries[query_name]
        sql = query_config.get('sql', '')

        self.logger.debug(f"Original SQL for {query_name}: {sql}")

        # Handle month substitution for FFBSCANNERDATA tables
        if 'FFBSCANNERDATA{month}' in sql:
            sql = self._substitute_month(sql, parameters.get('start_date'))
            self.logger.debug(f"After month substitution: {sql}")

        # Parameter substitution - FIXED: Replace {start_date} and {end_date}
        sql = self._substitute_parameters(sql, parameters)
        self.logger.debug(f"After parameter substitution: {sql}")

        # Execute query
        return_format = query_config.get('return_format', 'dataframe')
        self.logger.debug(f"Executing {query_name} with return format: {return_format}")

        result = self.db_connector.execute_query(sql, parameters, return_format)

        # Debug log result structure
        self._debug_log_result(query_name, result)

        return result

    def _substitute_parameters(self, sql: str, parameters: Dict[str, Any]) -> str:
        """Substitute parameters dalam SQL query dengan proper quoting"""
        try:
            # Handle date parameters with proper quoting
            for param_name, param_value in parameters.items():
                placeholder = f"{{{param_name}}}"
                if placeholder in sql:
                    if param_name in ['start_date', 'end_date']:
                        # Format date for SQL (YYYY-MM-DD)
                        if isinstance(param_value, str):
                            # Try to normalize date format
                            try:
                                date_obj = datetime.strptime(param_value, '%Y-%m-%d')
                                formatted_date = f"'{date_obj.strftime('%Y-%m-%d')}'"
                            except:
                                formatted_date = f"'{param_value}'"
                        elif isinstance(param_value, (datetime, date)):
                            formatted_date = f"'{param_value.strftime('%Y-%m-%d')}'"
                        else:
                            formatted_date = f"'{str(param_value)}'"

                        sql = sql.replace(placeholder, formatted_date)
                        self.logger.debug(f"Replaced {placeholder} with {formatted_date}")
                    else:
                        # Replace other parameters as-is
                        sql = sql.replace(placeholder, str(param_value))
                        self.logger.debug(f"Replaced {placeholder} with {str(param_value)}")

            return sql
        except Exception as e:
            self.logger.error(f"Error substituting parameters: {e}")
            return sql

    def _debug_log_result(self, query_name: str, result: Any):
        """Debug log hasil query"""
        try:
            if result is None:
                self.logger.debug(f"Query {query_name} result: None")
            elif isinstance(result, pd.DataFrame):
                self.logger.debug(f"Query {query_name} result: DataFrame with {len(result)} rows, columns: {list(result.columns)}")
                if not result.empty:
                    self.logger.debug(f"Sample data from {query_name}: {result.head(2).to_dict('records')}")
            elif isinstance(result, list):
                self.logger.debug(f"Query {query_name} result: List with {len(result)} items")
                if len(result) > 0:
                    if isinstance(result[0], dict):
                        if 'rows' in result[0]:
                            self.logger.debug(f"Enhanced connector format - rows: {len(result[0]['rows'])}")
                            if len(result[0]['rows']) > 0:
                                self.logger.debug(f"Sample row: {result[0]['rows'][0]}")
                        else:
                            self.logger.debug(f"First item: {result[0]}")
                    else:
                        self.logger.debug(f"First item type: {type(result[0])}, value: {result[0]}")
            else:
                self.logger.debug(f"Query {query_name} result: {type(result)} - {result}")
        except Exception as e:
            self.logger.error(f"Error in debug logging result for {query_name}: {e}")

    def _substitute_month(self, sql: str, start_date: Union[str, datetime, date]) -> str:
        """Substitute {month} dalam SQL query"""
        try:
            if isinstance(start_date, str):
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                except:
                    start_date = datetime.strptime(start_date, '%d/%m/%Y')

            month = start_date.month
            if month < 10:
                month_str = f'0{month}'
            else:
                month_str = str(month)

            result = sql.replace('{month}', month_str)
            self.logger.debug(f"Month substitution: {month} -> {month_str}")
            return result
        except Exception as e:
            self.logger.error(f"Error in month substitution: {e}")
            return sql

    def process_variables(self, query_results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process semua variables dengan debug logging

        Args:
            query_results: Hasil query dari database
            parameters: Parameter input

        Returns:
            Dictionary berisi semua processed variables
        """
        variables = {}
        variable_configs = self.formulas.get('variables', {})

        self.logger.info(f"=== PROCESSING VARIABLES ===")
        self.logger.info(f"Found {len(variable_configs)} variable categories")

        for category, category_vars in variable_configs.items():
            self.logger.info(f"Processing category: {category} with {len(category_vars)} variables")

            for var_name, var_config in category_vars.items():
                try:
                    self.logger.debug(f"Processing variable: {category}.{var_name}")
                    value = self._process_variable(var_name, var_config, query_results, parameters)
                    variables[var_name] = value
                    self.logger.debug(f"Variable {var_name} = {value} (type: {type(value)})")
                except Exception as e:
                    self.logger.error(f"Error processing variable {var_name}: {e}", exc_info=True)
                    default_value = var_config.get('default', None)
                    variables[var_name] = default_value
                    self.logger.warning(f"Using default value for {var_name}: {default_value}")

        self.logger.info(f"=== VARIABLE PROCESSING COMPLETED ===")
        self.logger.info(f"Total variables processed: {len(variables)}")

        # Log all variables for debugging
        for var_name, value in variables.items():
            self.logger.debug(f"FINAL VARIABLE {var_name}: {value}")

        return variables

    def _process_variable(self, var_name: str, var_config: Dict, query_results: Dict[str, Any], parameters: Dict[str, Any]) -> Any:
        """Process single variable dengan enhanced logic"""
        var_type = var_config.get('type', 'static')

        self.logger.debug(f"Processing variable {var_name} with type: {var_type}")

        if var_type == 'static':
            value = var_config.get('value')
            self.logger.debug(f"Static value for {var_name}: {value}")
            return value

        elif var_type == 'dynamic':
            value_source = var_config.get('value')
            if value_source == 'current_date':
                format_str = var_config.get('format', '%d %B %Y')
                value = datetime.now().strftime(format_str)
                self.logger.debug(f"Dynamic date for {var_name}: {value}")
                return value
            elif value_source == 'current_time':
                format_str = var_config.get('format', '%H:%M:%S')
                value = datetime.now().strftime(format_str)
                self.logger.debug(f"Dynamic time for {var_name}: {value}")
                return value

        elif var_type == 'formatting':
            template = var_config.get('template', '')
            param_names = var_config.get('parameters', [])
            format_params = {}

            self.logger.debug(f"Formatting template: {template}, params: {param_names}")

            for param in param_names:
                if param in parameters:
                    format_params[param] = parameters[param]
                    self.logger.debug(f"Template param {param}: {parameters[param]}")

            value = template.format(**format_params)
            self.logger.debug(f"Formatted value for {var_name}: {value}")
            return value

        elif var_type == 'query_result':
            query_name = var_config.get('query')
            field = var_config.get('field')
            extract_single = var_config.get('extract_single', False)

            self.logger.debug(f"Query result variable {var_name}: query={query_name}, field={field}, extract_single={extract_single}")

            if query_name in query_results and query_results[query_name] is not None:
                data = query_results[query_name]

                self.logger.debug(f"Query {query_name} data type: {type(data)}")

                if extract_single:
                    # Extract single scalar value
                    if isinstance(data, list) and len(data) > 0:
                        # Handle enhanced connector format: {'headers': [...], 'rows': [...]}
                        if isinstance(data[0], dict) and 'rows' in data[0]:
                            rows = data[0]['rows']
                            if len(rows) > 0 and field in rows[0]:
                                value = rows[0][field]
                                self.logger.debug(f"Extracted single value from enhanced format: {value}")
                                return value
                    elif isinstance(data, pd.DataFrame) and not data.empty:
                        if field in data.columns:
                            value = data[field].iloc[0]
                            self.logger.debug(f"Extracted single value from DataFrame: {value}")
                            return value
                    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                        value = data[0].get(field)
                        self.logger.debug(f"Extracted single value from list of dicts: {value}")
                        return value
                else:
                    # Return full data structure or first matching field
                    if isinstance(data, pd.DataFrame) and not data.empty:
                        if field in data.columns:
                            value = data[field].iloc[0] if len(data) == 1 else data[field].tolist()
                            self.logger.debug(f"Field value from DataFrame: {value}")
                            return value
                    elif isinstance(data, list) and len(data) > 0:
                        # Handle enhanced connector format
                        if isinstance(data[0], dict) and 'rows' in data[0]:
                            rows = data[0]['rows']
                            if len(rows) > 0:
                                if field:
                                    # Return all values for the field
                                    values = [row.get(field) for row in rows if field in row]
                                    value = values[0] if len(values) == 1 else values
                                    self.logger.debug(f"Field values from enhanced format: {value}")
                                    return value
                                else:
                                    value = rows
                                    self.logger.debug(f"All rows from enhanced format: {len(rows)} items")
                                    return value
                        elif isinstance(data[0], dict):
                            value = data[0].get(field) if field else data
                            self.logger.debug(f"Value from list of dicts: {value}")
                            return value

            self.logger.warning(f"Query {query_name} not found or field {field} not available")
            return var_config.get('default', None)

        elif var_type == 'calculation':
            expression = var_config.get('expression', '')
            self.logger.debug(f"Calculating expression for {var_name}: {expression}")
            value = self._evaluate_expression(expression, query_results, parameters)
            self.logger.debug(f"Calculated value for {var_name}: {value}")
            return value

        elif var_type == 'query_aggregation':
            query_name = var_config.get('query')
            field = var_config.get('field')
            aggregation = var_config.get('aggregation', 'sum')

            self.logger.debug(f"Query aggregation {var_name}: query={query_name}, field={field}, agg={aggregation}")

            if query_name in query_results and query_results[query_name] is not None:
                data = query_results[query_name]
                if isinstance(data, pd.DataFrame) and not data.empty and field in data.columns:
                    if aggregation == 'sum':
                        value = data[field].sum()
                    elif aggregation == 'avg':
                        value = data[field].mean()
                    elif aggregation == 'max':
                        value = data[field].max()
                    elif aggregation == 'min':
                        value = data[field].min()
                    elif aggregation == 'count':
                        value = data[field].count()
                    else:
                        value = 0

                    self.logger.debug(f"Aggregated value for {var_name}: {value}")
                    return value

            return var_config.get('default', None)

        self.logger.debug(f"Unknown variable type {var_type} for {var_name}, using default")
        return var_config.get('default', None)

    def _evaluate_expression(self, expression: str, query_results: Dict[str, Any], parameters: Dict[str, Any]) -> Any:
        """Evaluate mathematical expression dengan enhanced variable substitution"""
        try:
            processed_expr = expression
            self.logger.debug(f"Evaluating expression: {expression}")

            # Replace variables in expression
            # Handle query result variables
            for var_name in re.findall(r'\{(\w+)\}', expression):
                value = 0

                # Check if it's in parameters first
                if var_name in parameters:
                    value = parameters[var_name]
                    self.logger.debug(f"Parameter {var_name}: {value}")
                # Check if it's in query_results
                elif var_name in query_results:
                    data = query_results[var_name]
                    if isinstance(data, (int, float)):
                        value = data
                    elif isinstance(data, pd.DataFrame) and not data.empty:
                        # If it's a single row dataframe, get first value
                        if len(data) == 1 and len(data.columns) == 1:
                            value = data.iloc[0, 0]
                        else:
                            # Try to sum numeric columns
                            numeric_sum = 0
                            for col in data.select_dtypes(include=['number']).columns:
                                numeric_sum += data[col].sum()
                            value = numeric_sum
                    elif isinstance(data, list) and len(data) > 0:
                        if isinstance(data[0], dict) and 'rows' in data[0]:
                            # Handle enhanced connector format
                            rows = data[0]['rows']
                            # Sum numeric values from all rows
                            for row in rows:
                                for val in row.values():
                                    if isinstance(val, (int, float)):
                                        value += val
                        else:
                            # Handle list of dicts or simple values
                            for item in data:
                                if isinstance(item, dict):
                                    for val in item.values():
                                        if isinstance(val, (int, float)):
                                            value += val
                                elif isinstance(item, (int, float)):
                                    value += item

                    self.logger.debug(f"Query result {var_name}: {value}")
                else:
                    self.logger.debug(f"Variable {var_name} not found, using 0")

                # Replace in expression
                processed_expr = processed_expr.replace(f'{{{var_name}}}', str(value))

            self.logger.debug(f"Processed expression: {processed_expr}")

            # Evaluate expression safely
            processed_expr = processed_expr.replace('^', '**')
            result = eval(processed_expr, {"__builtins__": {}}, {})

            self.logger.debug(f"Expression result: {result}")
            return result

        except Exception as e:
            self.logger.error(f"Error evaluating expression '{expression}': {e}")
            self.logger.error(f"Processed expression: {processed_expr}")
            return 0

    def get_formula_info(self) -> Dict[str, Any]:
        """Get information tentang loaded formulas"""
        return {
            'formula_path': self.formula_path,
            'queries_count': len(self.formulas.get('queries', {})),
            'variables_count': sum(len(vars) for vars in self.formulas.get('variables', {}).values()),
            'repeating_sections_count': len(self.formulas.get('repeating_sections', {})),
            'cache_size': len(self.data_cache)
        }