"""
Formula Engine untuk Data Processing
Menangani eksekusi formula, query database, dan data transformation
"""

import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date, timedelta
import re
import logging
from firebird_connector_enhanced import FirebirdConnectorEnhanced as FirebirdConnector

class FormulaEngine:
    """
    Formula engine untuk memproses data dari database Firebird
    berdasarkan definisi formula dalam file JSON
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

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Load formulas
        self._load_formulas()

    def _load_formulas(self):
        """Load formula definitions dari file JSON"""
        try:
            with open(self.formula_path, 'r', encoding='utf-8') as f:
                self.formulas = json.load(f)

            self.logger.info(f"Formula definitions loaded: {len(self.formulas.get('queries', {}))} queries")
        except Exception as e:
            self.logger.error(f"Error loading formulas: {e}")
            raise

    def execute_all_queries(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute semua queries yang didefinisikan dalam formula

        Args:
            parameters: Parameter untuk query (start_date, end_date, estate, dll)

        Returns:
            Dictionary berisi hasil semua query
        """
        results = {}
        queries = self.formulas.get('queries', {})

        for query_name, query_config in queries.items():
            try:
                result = self.execute_query(query_name, parameters)
                results[query_name] = result
                self.logger.debug(f"Query {query_name} executed successfully")
            except Exception as e:
                self.logger.error(f"Error executing query {query_name}: {e}")
                results[query_name] = None

        return results

    def execute_query(self, query_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute single query

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

        # Handle month substitution for FFBSCANNERDATA tables
        if 'FFBSCANNERDATA{month}' in sql:
            sql = self._substitute_month(sql, parameters.get('start_date'))

        # Execute query
        return_format = query_config.get('return_format', 'dataframe')
        result = self.db_connector.execute_query(sql, parameters, return_format)

        return result

    def _substitute_month(self, sql: str, start_date: Union[str, datetime, date]) -> str:
        """Substitute {month} dalam SQL query"""
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

        return sql.replace('{month}', month_str)

    def process_variables(self, query_results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process semua variables berdasarkan query results

        Args:
            query_results: Hasil query dari database
            parameters: Parameter input

        Returns:
            Dictionary berisi semua processed variables
        """
        variables = {}
        variable_configs = self.formulas.get('variables', {})

        for category, category_vars in variable_configs.items():
            for var_name, var_config in category_vars.items():
                try:
                    value = self._process_variable(var_name, var_config, query_results, parameters)
                    variables[var_name] = value
                except Exception as e:
                    self.logger.error(f"Error processing variable {var_name}: {e}")
                    variables[var_name] = var_config.get('default', None)

        return variables

    def _process_variable(self, var_name: str, var_config: Dict, query_results: Dict[str, Any], parameters: Dict[str, Any]) -> Any:
        """Process single variable"""
        var_type = var_config.get('type', 'static')

        if var_type == 'static':
            return var_config.get('value')

        elif var_type == 'dynamic':
            value_source = var_config.get('value')
            if value_source == 'current_date':
                format_str = var_config.get('format', '%d %B %Y')
                return datetime.now().strftime(format_str)
            elif value_source == 'current_time':
                format_str = var_config.get('format', '%H:%M:%S')
                return datetime.now().strftime(format_str)

        elif var_type == 'formatting':
            template = var_config.get('template', '')
            param_names = var_config.get('parameters', [])
            format_params = {}

            for param in param_names:
                if param in parameters:
                    format_params[param] = parameters[param]

            return template.format(**format_params)

        elif var_type == 'query_result':
            query_name = var_config.get('query')
            field = var_config.get('field')
            extract_single = var_config.get('extract_single', False)

            if query_name in query_results and query_results[query_name] is not None:
                data = query_results[query_name]
                if extract_single:
                    # Extract single scalar value
                    if isinstance(data, list) and len(data) > 0:
                        # Handle enhanced connector format: {'headers': [...], 'rows': [...]}
                        if isinstance(data[0], dict) and 'rows' in data[0]:
                            rows = data[0]['rows']
                            if len(rows) > 0 and field in rows[0]:
                                return rows[0][field]
                    elif isinstance(data, pd.DataFrame) and not data.empty:
                        if field in data.columns:
                            return data[field].iloc[0]
                    return None
                else:
                    # Return full data structure (original behavior)
                    if isinstance(data, pd.DataFrame) and not data.empty:
                        return data[field].iloc[0] if field in data.columns else None
                    elif isinstance(data, list) and len(data) > 0:
                        # Handle enhanced connector format: {'headers': [...], 'rows': [...]}
                        if isinstance(data[0], dict) and 'rows' in data[0]:
                            rows = data[0]['rows']
                            if len(rows) > 0 and field in rows[0]:
                                return rows[0][field]
                    elif isinstance(data[0], dict):
                        return data[0].get(field) if field in data[0] else None

            return var_config.get('default', None)

        elif var_type == 'calculation':
            expression = var_config.get('expression', '')
            return self._evaluate_expression(expression, query_results, parameters)

        elif var_type == 'query_aggregation':
            query_name = var_config.get('query')
            field = var_config.get('field')
            aggregation = var_config.get('aggregation', 'sum')

            if query_name in query_results and query_results[query_name] is not None:
                data = query_results[query_name]
                if isinstance(data, pd.DataFrame) and not data.empty and field in data.columns:
                    if aggregation == 'sum':
                        return data[field].sum()
                    elif aggregation == 'avg':
                        return data[field].mean()
                    elif aggregation == 'max':
                        return data[field].max()
                    elif aggregation == 'min':
                        return data[field].min()
                    elif aggregation == 'count':
                        return data[field].count()

            return var_config.get('default', None)

        return var_config.get('default', None)

    def _evaluate_expression(self, expression: str, query_results: Dict[str, Any], parameters: Dict[str, Any]) -> Any:
        """Evaluate mathematical expression dengan variable substitution"""
        # Replace variables in expression
        processed_expr = expression

        # Handle common query field variables
        field_mappings = {
            'total_transactions': 'transaction_summary.TOTAL_TRANSAKSI',
            'total_ripe_bunches': 'transaction_summary.TOTAL_RIPE',
            'total_unripe_bunches': 'transaction_summary.TOTAL_UNRIPE',
            'total_black': 'transaction_summary.TOTAL_BLACK',
            'total_rotten': 'transaction_summary.TOTAL_ROTTEN',
            'total_ratdamage': 'transaction_summary.TOTAL_RATDAMAGE',
            'total_ripe': 'transaction_summary.TOTAL_RIPE',  # Alternative mapping
            'total_days': None  # Special case handled separately
        }

        # Replace query result variables and field mappings
        for var in re.findall(r'\{(\w+)\}', expression):
            var_name = var.strip()
            value = 0

            # Check if it's a field mapping
            if var_name in field_mappings and field_mappings[var_name]:
                field_path = field_mappings[var_name]
                query_name, field = field_path.split('.', 1)

                if query_name in query_results and query_results[query_name] is not None:
                    data = query_results[query_name]
                    if isinstance(data, pd.DataFrame) and not data.empty and field in data.columns:
                        value = data[field].iloc[0]
                    elif isinstance(data, list) and len(data) > 0:
                        # Handle enhanced connector format
                        if isinstance(data[0], dict) and 'rows' in data[0]:
                            rows = data[0]['rows']
                            if len(rows) > 0 and field in rows[0]:
                                value = rows[0][field]
                            else:
                                value = 0
                        elif isinstance(data[0], dict):
                            value = data[0].get(field, 0)
                        else:
                            value = 0
                    else:
                        value = 0

            # Special case for total_days - calculate from parameters
            elif var_name == 'total_days':
                if 'start_date' in parameters and 'end_date' in parameters:
                    try:
                        start_date = datetime.strptime(parameters['start_date'], '%Y-%m-%d')
                        end_date = datetime.strptime(parameters['end_date'], '%Y-%m-%d')
                        value = (end_date - start_date).days + 1
                    except:
                        value = 1
                else:
                    value = 1

            # Check if it's directly in query_results
            elif var_name in query_results and query_results[var_name] is not None:
                data = query_results[var_name]
                if isinstance(data, pd.DataFrame) and not data.empty:
                    # If it's a single row dataframe, get first value
                    if len(data) == 1 and len(data.columns) == 1:
                        value = data.iloc[0, 0]
                    else:
                        # Try to sum numeric columns
                        numeric_sum = 0
                        for col in data.select_dtypes(include=['number']).columns:
                            numeric_sum += data[col].sum()
                        value = numeric_sum
                elif isinstance(data, (int, float)):
                    value = data
                elif isinstance(data, list) and len(data) > 0:
                    # Handle list of dicts
                    if isinstance(data[0], dict):
                        # Sum numeric values from all dicts
                        for item in data:
                            for val in item.values():
                                if isinstance(val, (int, float)):
                                    value += val

            # Replace in expression
            processed_expr = processed_expr.replace(f'{{{var_name}}}', str(value))

        # Replace parameter variables
        for param, param_value in parameters.items():
            if f'{{{param}}}' in processed_expr:
                processed_expr = processed_expr.replace(f'{{{param}}}', str(param_value))

        # Evaluate expression safely
        try:
            # Replace common mathematical functions
            processed_expr = processed_expr.replace('^', '**')

            # Evaluate using eval with restricted globals
            result = eval(processed_expr, {"__builtins__": {}}, {})
            return result
        except Exception as e:
            self.logger.error(f"Error evaluating expression '{expression}': {e}")
            self.logger.error(f"Processed expression: {processed_expr}")
            return 0

    def process_repeating_section_data(self, section_name: str, query_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process data untuk repeating section

        Args:
            section_name: Nama repeating section
            query_results: Hasil query dari database

        Returns:
            List data untuk repeating section
        """
        repeating_sections = self.formulas.get('repeating_sections', {})

        if section_name not in repeating_sections:
            return []

        section_config = repeating_sections[section_name]
        data_source = section_config.get('data_source')
        group_by = section_config.get('group_by')

        if data_source not in query_results or query_results[data_source] is None:
            return []

        data = query_results[data_source]

        if isinstance(data, pd.DataFrame):
            if data.empty:
                return []

            # Convert to list of dictionaries
            result = data.to_dict('records')

            # Apply grouping if specified
            if group_by:
                result = self._apply_grouping(result, group_by, section_config)

            return result
        elif isinstance(data, list):
            return data
        else:
            return []

    def _apply_grouping(self, data: List[Dict], group_by: str, section_config: Dict) -> List[Dict]:
        """Apply grouping ke data"""
        if not group_by:
            return data

        # Group data by group_by field
        grouped_data = {}
        for item in data:
            group_value = item.get(group_by)
            if group_value not in grouped_data:
                grouped_data[group_value] = []
            grouped_data[group_value].append(item)

        # Process each group
        result = []
        for group_value, group_items in grouped_data.items():
            # Create summary row for each group
            summary_row = {}
            summary_row[group_by] = group_value

            # Calculate aggregates for numeric fields
            columns = section_config.get('columns', {})
            for col_name, col_config in columns.items():
                field = col_config.get('field')
                if field and field != group_by:
                    values = [item.get(field, 0) for item in group_items if isinstance(item.get(field), (int, float))]
                    if values:
                        summary_row[field] = sum(values)
                    else:
                        summary_row[field] = 0

            result.append(summary_row)

        return result

    def calculate_derived_metrics(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate derived metrics dari base data

        Args:
            base_data: Data dasar dari query results

        Returns:
            Derived metrics
        """
        metrics = {}

        # Calculate total days in period
        if 'start_date' in base_data and 'end_date' in base_data:
            try:
                start_date = datetime.strptime(base_data['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(base_data['end_date'], '%Y-%m-%d')
                total_days = (end_date - start_date).days + 1
                metrics['total_days'] = total_days
            except:
                metrics['total_days'] = 1

        # Calculate performance metrics
        transaction_summary = base_data.get('transaction_summary')
        if transaction_summary is not None:
            if isinstance(transaction_summary, pd.DataFrame) and not transaction_summary.empty:
                total_trans = transaction_summary['TOTAL_TRANSAKSI'].iloc[0] if 'TOTAL_TRANSAKSI' in transaction_summary.columns else 0
                total_ripe = transaction_summary['TOTAL_RIPE'].iloc[0] if 'TOTAL_RIPE' in transaction_summary.columns else 0

                if total_trans > 0:
                    metrics['avg_ripe_per_transaction'] = total_ripe / total_trans
                else:
                    metrics['avg_ripe_per_transaction'] = 0

                if metrics.get('total_days', 0) > 0:
                    metrics['daily_average_transactions'] = total_trans / metrics['total_days']
                    metrics['daily_average_ripe'] = total_ripe / metrics['total_days']
                else:
                    metrics['daily_average_transactions'] = 0
                    metrics['daily_average_ripe'] = 0

        # Calculate quality percentage
        quality_data = base_data.get('quality_analysis')
        if quality_data is not None and isinstance(quality_data, pd.DataFrame) and not quality_data.empty:
            if 'PERCENTAGE_DEFECT' in quality_data.columns:
                avg_defect = quality_data['PERCENTAGE_DEFECT'].mean()
                metrics['quality_percentage'] = avg_defect
            else:
                metrics['quality_percentage'] = 0

        return metrics

    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate processed data

        Args:
            data: Data yang akan divalidasi

        Returns:
            Validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        # Check required data
        required_queries = ['transaction_summary', 'daily_performance']
        for query in required_queries:
            if query not in data or data[query] is None:
                validation_results['errors'].append(f"Required query '{query}' not available")
                validation_results['is_valid'] = False

        # Check data completeness
        for query_name, query_data in data.items():
            if query_data is not None:
                if isinstance(query_data, pd.DataFrame):
                    if query_data.empty:
                        validation_results['warnings'].append(f"Query '{query_name}' returned no data")
                elif isinstance(query_data, list):
                    if len(query_data) == 0:
                        validation_results['warnings'].append(f"Query '{query_name}' returned empty list")

        return validation_results

    def get_estate_config(self, estate_name: str, estate_config_file: str = 'estate_config.json') -> Dict[str, Any]:
        """
        Get estate configuration dari file

        Args:
            estate_name: Nama estate
            estate_config_file: Path ke config file

        Returns:
            Estate configuration
        """
        try:
            with open(estate_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            if estate_name in config:
                return config[estate_name]
            else:
                self.logger.warning(f"Estate {estate_name} not found in config file")
                return {}

        except Exception as e:
            self.logger.error(f"Error loading estate config: {e}")
            return {}

    def clear_cache(self):
        """Clear semua cache"""
        self.data_cache.clear()
        self.variables_cache.clear()
        self.logger.info("Cache cleared")

    def get_formula_info(self) -> Dict[str, Any]:
        """Get information tentang loaded formulas"""
        return {
            'formula_path': self.formula_path,
            'queries_count': len(self.formulas.get('queries', {})),
            'variables_count': sum(len(vars) for vars in self.formulas.get('variables', {}).values()),
            'repeating_sections_count': len(self.formulas.get('repeating_sections', {})),
            'cache_size': len(self.data_cache)
        }