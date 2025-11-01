#!/usr/bin/env python3
"""
Dynamic Formula Engine untuk Real Database Processing
Menggantikan static data dengan real Firebird database queries
"""

import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

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

class DynamicFormulaEngine:
    """
    Enhanced formula engine dengan dynamic database queries
    """

    def __init__(self, formula_path: str, db_connector=None):
        """
        Inisialisasi dynamic formula engine

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

        self._load_formula()
        # Don't use hardcoded queries - use only from JSON file
        self._setup_queries_from_json()

    def _load_formula(self):
        """Load formula JSON file"""
        try:
            if not os.path.exists(self.formula_path):
                raise FileNotFoundError(f"Formula file not found: {self.formula_path}")

            with open(self.formula_path, 'r', encoding='utf-8') as f:
                self.formula_data = json.load(f)

            self.logger.info(f"Formula loaded: {self.formula_path}")

            # Extract basic structure
            if 'queries' in self.formula_data:
                self.queries = self.formula_data['queries']
            if 'variables' in self.formula_data:
                self.variables = self.formula_data['variables']
            if 'repeating_sections' in self.formula_data:
                self.repeating_sections = self.formula_data['repeating_sections']

        except Exception as e:
            self.logger.error(f"Error loading formula: {e}")
            raise

    def _setup_queries_from_json(self):
        """Setup queries from loaded JSON formula data"""
        # Use queries from JSON file instead of hardcoded queries
        if self.formula_data and 'queries' in self.formula_data:
            self.dynamic_queries = self.formula_data['queries']
            self.logger.info(f"Loaded {len(self.dynamic_queries)} queries from JSON file")
        else:
            self.logger.warning("No queries found in JSON file, using empty queries")
            self.dynamic_queries = {}

    def _process_json_variables(self, variable_definitions: Dict, query_results: Dict[str, List[Dict]], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process variable definitions from JSON file"""
        variables = {}

        for section_name, section_vars in variable_definitions.items():
            if isinstance(section_vars, dict):
                for var_name, var_def in section_vars.items():
                    if isinstance(var_def, dict):
                        # Process variable definition
                        var_type = var_def.get('type', 'static')

                        if var_type == 'static':
                            variables[var_name] = var_def.get('value', '')
                        elif var_type == 'parameter':
                            param_name = var_def.get('value', var_name)
                            variables[var_name] = parameters.get(param_name, '')
                        elif var_type == 'dynamic':
                            if var_def.get('value') == 'current_date':
                                variables[var_name] = datetime.now().strftime('%d %B %Y')
                            elif var_def.get('value') == 'current_time':
                                variables[var_name] = datetime.now().strftime('%H:%M:%S')
                        elif var_type == 'query_result':
                            query_name = var_def.get('query')
                            field_name = var_def.get('field')
                            if query_name in query_results and query_results[query_name]:
                                result = query_results[query_name][0]
                                variables[var_name] = result.get(field_name, '')
                        elif var_type == 'formatting':
                            template = var_def.get('template', '')
                            for param_name in var_def.get('parameters', []):
                                template = template.replace(f'{{{param_name}}}', str(parameters.get(param_name, '')))
                            variables[var_name] = template
                    else:
                        # Direct value
                        variables[var_name] = var_def

        return variables

    def execute_query(self, query_name: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        """
        Execute a specific query with parameters

        Args:
            query_name: Name of the query to execute
            parameters: Dictionary with parameters (start_date, end_date, month, etc.)

        Returns:
            List of dictionaries with query results
        """
        if not self.db_connector:
            self.logger.error("No database connector available")
            return []

        # Get query definition
        query_def = self.dynamic_queries.get(query_name)
        if not query_def:
            self.logger.error(f"Query not found: {query_name}")
            return []

        # Handle different query types
        query_type = query_def.get('type', 'sql')

        if query_type == 'calculation':
            # For calculation queries, execute the SQL directly
            sql = query_def.get('calculation', '')
        else:
            # For SQL queries, get the SQL
            sql = query_def.get('sql', '')

        if not sql:
            self.logger.error(f"No SQL found for query: {query_name}")
            return []

        # Substitute parameters
        if parameters:
            sql = self._substitute_parameters(sql, parameters)

        self.logger.info(f"Executing query: {query_name}")
        self.logger.debug(f"SQL: {sql}")

        try:
            # Execute query
            result = self.db_connector.execute_query(sql)

            if result and len(result) > 0:
                # Convert to list of dictionaries
                if isinstance(result[0], dict):
                    query_results = result
                else:
                    # Convert tuple results to dictionaries
                    headers = self.db_connector.get_column_names()
                    query_results = []
                    for row in result:
                        if headers and len(headers) == len(row):
                            query_results.append(dict(zip(headers, row)))
                        else:
                            # Create generic column names
                            query_results.append({
                                f'COL_{i+1}': val for i, val in enumerate(row)
                            })

                self.logger.info(f"Query {query_name} returned {len(query_results)} rows")
                return query_results
            else:
                self.logger.warning(f"Query {query_name} returned no results")
                return []

        except Exception as e:
            self.logger.error(f"Error executing query {query_name}: {e}")
            return []

    def _substitute_parameters(self, sql: str, parameters: Dict[str, Any]) -> str:
        """Substitute parameters in SQL query"""
        # Handle month parameter
        if 'month' in parameters:
            month_num = parameters['month']
            if isinstance(month_num, str):
                # Handle month range like "01,02,03"
                months = month_num.split(',')
                if len(months) == 1:
                    sql = sql.replace('{month}', f"{months[0].zfill(2)}")
                else:
                    # Multiple months - create UNION ALL
                    month_tables = [f"{m.strip().zfill(2)}" for m in months]
                    # For simplicity, use the first month for now
                    sql = sql.replace('{month}', month_tables[0])
            else:
                sql = sql.replace('{month}', f"{int(month_num):02d}")

        # Substitute other parameters
        for param, value in parameters.items():
            if param != 'month':
                placeholder = f'{{{param}}}'
                if isinstance(value, (date, datetime)):
                    value = value.strftime('%Y-%m-%d')
                    sql = sql.replace(placeholder, f"'{value}'")
                elif isinstance(value, str):
                    # Check if the value is already quoted in the SQL
                    if placeholder + "'" in sql or "'" + placeholder in sql:
                        # Value is already quoted, just replace the placeholder
                        sql = sql.replace(placeholder, value)
                    else:
                        # Add quotes for string values
                        sql = sql.replace(placeholder, f"'{value}'")
                else:
                    sql = sql.replace(placeholder, str(value))

        return sql

    def execute_all_queries(self, parameters: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Execute all dynamic queries

        Args:
            parameters: Dictionary with query parameters

        Returns:
            Dictionary with all query results
        """
        results = {}

        for query_name in self.dynamic_queries.keys():
            self.logger.info(f"Executing {query_name}...")
            query_results = self.execute_query(query_name, parameters)
            results[query_name] = query_results

        return results

    def process_variables(self, query_results: Dict[str, List[Dict]],
                         parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process variables from query results and JSON definitions

        Args:
            query_results: Results from executed queries
            parameters: Original parameters

        Returns:
            Dictionary with processed variables
        """
        variables = {}

        # First, load variables from JSON definitions
        if self.formula_data and 'variables' in self.formula_data:
            variables.update(self._process_json_variables(self.formula_data['variables'], query_results, parameters))

        # Fallback: Process estate info if not in JSON
        if 'estate_info' in query_results and query_results['estate_info']:
            estate_data = query_results['estate_info'][0]
            if 'estate_name' not in variables:
                variables['estate_name'] = estate_data.get('ESTATE_NAME', parameters.get('estate_name', 'Unknown Estate'))
            if 'estate_code' not in variables:
                variables['estate_code'] = estate_data.get('ESTATE_CODE', parameters.get('estate_code', 'Unknown'))

        # Fallback: Basic report info if not in JSON
        if 'report_title' not in variables:
            variables['report_title'] = parameters.get('report_title', 'LAPORAN ANALISIS FRESH FRUIT BUNCH (FFB)')
        if 'report_period' not in variables:
            variables['report_period'] = f"{parameters.get('start_date', 'Unknown')} - {parameters.get('end_date', 'Unknown')}"
        if 'generated_date' not in variables:
            variables['generated_date'] = datetime.now().strftime('%d %B %Y')
        if 'generated_time' not in variables:
            variables['generated_time'] = datetime.now().strftime('%H:%M:%S')

        # Calculate dashboard summaries
        daily_data = query_results.get('daily_performance', [])
        if daily_data:
            total_transactions = sum(row.get('JUMLAH_TRANSAKSI', 0) for row in daily_data)
            total_ripe = sum(row.get('RIPE_BUNCHES', 0) for row in daily_data)
            total_unripe = sum(row.get('UNRIPE_BUNCHES', 0) for row in daily_data)

            variables.update({
                'total_transactions': total_transactions,
                'total_ripe_bunches': total_ripe,
                'total_unripe_bunches': total_unripe,
                'avg_ripe_per_transaction': round(total_ripe / total_transactions, 2) if total_transactions > 0 else 0,
                'daily_average_transactions': round(total_transactions / len(daily_data), 2) if daily_data else 0,
                'daily_average_ripe': round(total_ripe / len(daily_data), 2) if daily_data else 0
            })
        else:
            # Default values when no data
            variables.update({
                'total_transactions': 0,
                'total_ripe_bunches': 0,
                'total_unripe_bunches': 0,
                'avg_ripe_per_transaction': 0,
                'daily_average_transactions': 0,
                'daily_average_ripe': 0
            })

        # Calculate quality percentage
        total_ripe = variables.get('total_ripe_bunches', 0)
        total_black = sum(row.get('BLACK_BUNCHES', 0) for row in daily_data)
        total_rotten = sum(row.get('ROTTEN_BUNCHES', 0) for row in daily_data)
        total_defect = total_black + total_rotten

        quality_percentage = (total_defect / total_ripe * 100) if total_ripe > 0 else 0
        variables.update({
            'quality_percentage': round(quality_percentage, 2)
        })

        # Process verification rate
        if 'verification_rate' in query_results and query_results['verification_rate']:
            verification_data = query_results['verification_rate'][0]
            variables.update({
                'verification_rate': verification_data.get('verification_rate', 0)
            })
        else:
            variables.update({'verification_rate': 0})

        # Find peak and low performance days
        if daily_data:
            peak_day = max(daily_data, key=lambda x: x.get('JUMLAH_TRANSAKSI', 0))
            low_day = min(daily_data, key=lambda x: x.get('JUMLAH_TRANSAKSI', 0))

            variables.update({
                'peak_performance_day': peak_day.get('TRANSDATE', 'Unknown'),
                'low_performance_day': low_day.get('TRANSDATE', 'Unknown')
            })
        else:
            variables.update({
                'peak_performance_day': 'No Data',
                'low_performance_day': 'No Data'
            })

        return variables

    def get_repeating_data(self, query_results: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        Get data for repeating sections

        Args:
            query_results: Results from executed queries

        Returns:
            Dictionary with repeating section data
        """
        repeating_data = {}

        # Map repeating sections to query results
        section_mapping = {
            'Harian': 'daily_performance',
            'Karyawan': 'employee_performance',
            'Field': 'field_performance',
            'Kualitas': 'quality_analysis'
        }

        for sheet_name, query_name in section_mapping.items():
            if query_name in query_results:
                repeating_data[sheet_name] = query_results[query_name]

        return repeating_data

    def validate_data_completeness(self, query_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Validate that all required data is available

        Args:
            query_results: Results from executed queries

        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'is_complete': True,
            'missing_queries': [],
            'empty_queries': [],
            'data_counts': {}
        }

        for query_name in self.dynamic_queries.keys():
            if query_name not in query_results:
                validation_results['missing_queries'].append(query_name)
                validation_results['is_complete'] = False
            else:
                data_count = len(query_results[query_name])
                validation_results['data_counts'][query_name] = data_count

                if data_count == 0:
                    validation_results['empty_queries'].append(query_name)
                    # Don't mark as incomplete if some queries legitimately return no data

        return validation_results


def main():
    """Test function"""
    formula_path = "laporan_ffb_analysis_formula.json"

    if not os.path.exists(formula_path):
        print(f"Formula file not found: {formula_path}")
        return

    # Create engine without database connector for testing
    engine = DynamicFormulaEngine(formula_path)

    print("Dynamic Formula Engine initialized")
    print(f"Available queries: {list(engine.dynamic_queries.keys())}")


if __name__ == "__main__":
    main()