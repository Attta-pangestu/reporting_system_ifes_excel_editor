"""
Formula Engine untuk sistem report generator
Menangani definisi formula dan transformasi data dari database
"""

import json
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import re
import logging
import time
import os
from firebird_connector import FirebirdConnector

# Configure logging for formula engine
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('formula_engine_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FormulaEngine:
    """
    Engine untuk memproses formula definitions dan mengambil data dari database
    """
    
    def __init__(self, formula_path: str, db_connector: FirebirdConnector):
        """
        Inisialisasi formula engine
        
        :param formula_path: Path ke file formula definition
        :param db_connector: Instance FirebirdConnector untuk akses database
        """
        logger.info("="*60)
        logger.info("INITIALIZING FORMULA ENGINE")
        logger.info("="*60)
        
        start_time = time.time()
        
        logger.info(f"Formula path: {formula_path}")
        logger.info(f"Database connector: {type(db_connector).__name__}")
        
        self.formula_path = formula_path
        self.db_connector = db_connector
        self.formulas = {}
        self.data_cache = {}
        self.query_stats = {}
        
        # Validate formula file exists
        if not os.path.exists(formula_path):
            logger.error(f"Formula file not found: {formula_path}")
            raise FileNotFoundError(f"Formula file not found: {formula_path}")
        
        file_size = os.path.getsize(formula_path)
        logger.debug(f"Formula file size: {file_size} bytes")
        
        self._load_formulas()
        
        init_time = time.time() - start_time
        logger.info(f"Formula engine initialization completed in {init_time:.3f} seconds")
        logger.info("="*60)
    
    def _load_formulas(self):
        """Load formula definitions dari file JSON"""
        logger.info("Loading formula definitions...")
        start_time = time.time()
        
        try:
            with open(self.formula_path, 'r', encoding='utf-8') as f:
                self.formulas = json.load(f)
            
            load_time = time.time() - start_time
            
            # Log detailed formula statistics
            queries_count = len(self.formulas.get('queries', {}))
            variables_count = len(self.formulas.get('variables', {}))
            repeating_sections_count = len(self.formulas.get('repeating_sections', {}))
            
            logger.info(f"Formula definitions loaded successfully in {load_time:.3f} seconds")
            logger.info(f"Loaded components:")
            logger.info(f"  - Queries: {queries_count}")
            logger.info(f"  - Variables: {variables_count}")
            logger.info(f"  - Repeating sections: {repeating_sections_count}")
            
            # Log query details
            if queries_count > 0:
                logger.debug("Query definitions:")
                for query_name, query_config in self.formulas.get('queries', {}).items():
                    query_type = query_config.get('type', 'sql')
                    logger.debug(f"  - {query_name}: type={query_type}")
            
            # Log variable details
            if variables_count > 0:
                logger.debug("Variable definitions:")
                for var_name, var_config in self.formulas.get('variables', {}).items():
                    var_type = var_config.get('type', 'unknown')
                    logger.debug(f"  - {var_name}: type={var_type}")
            
            print(f"Formula engine loaded: {queries_count} queries, {variables_count} variables")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in formula file: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading formula definitions: {str(e)}")
            raise
    
    def execute_data_queries(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Eksekusi semua query yang didefinisikan dalam formula
        
        :param parameters: Parameter untuk query (tanggal, estate, dll)
        :return: Dictionary berisi hasil semua query
        """
        logger.info("="*50)
        logger.info("EXECUTING DATA QUERIES")
        logger.info("="*50)
        
        start_time = time.time()
        
        logger.info(f"Query parameters: {parameters}")
        
        query_results = {}
        queries = self.formulas.get('queries', {})
        
        logger.info(f"Total queries to execute: {len(queries)}")
        
        successful_queries = 0
        failed_queries = 0
        
        for query_name, query_config in queries.items():
            logger.info(f"Executing query: {query_name}")
            query_start_time = time.time()
            
            try:
                result = self._execute_single_query(query_config, parameters)
                query_execution_time = time.time() - query_start_time
                
                query_results[query_name] = result
                
                # Log query statistics
                result_count = len(result) if isinstance(result, list) else 'single value'
                logger.info(f"Query '{query_name}' completed successfully:")
                logger.info(f"  - Execution time: {query_execution_time:.3f} seconds")
                logger.info(f"  - Result count: {result_count}")
                
                # Store query statistics
                self.query_stats[query_name] = {
                    'execution_time': query_execution_time,
                    'result_count': result_count,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                }
                
                successful_queries += 1
                
                # Log sample data for debugging
                if isinstance(result, list) and len(result) > 0:
                    logger.debug(f"Sample result from '{query_name}': {result[0]}")
                elif not isinstance(result, list):
                    logger.debug(f"Result from '{query_name}': {result}")
                
            except Exception as e:
                query_execution_time = time.time() - query_start_time
                
                logger.error(f"Error executing query '{query_name}': {str(e)}")
                logger.error(f"Query execution time before error: {query_execution_time:.3f} seconds")
                
                query_results[query_name] = []
                failed_queries += 1
                
                # Store error statistics
                self.query_stats[query_name] = {
                    'execution_time': query_execution_time,
                    'result_count': 0,
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        total_execution_time = time.time() - start_time
        
        logger.info("="*50)
        logger.info("QUERY EXECUTION SUMMARY")
        logger.info("="*50)
        logger.info(f"Total execution time: {total_execution_time:.3f} seconds")
        logger.info(f"Successful queries: {successful_queries}")
        logger.info(f"Failed queries: {failed_queries}")
        logger.info(f"Success rate: {(successful_queries/(successful_queries+failed_queries)*100):.1f}%" if (successful_queries+failed_queries) > 0 else "N/A")
        
        return query_results
    
    def _execute_single_query(self, query_config: Dict, parameters: Dict[str, Any]) -> Any:
        """
        Eksekusi satu query berdasarkan konfigurasi
        
        :param query_config: Konfigurasi query
        :param parameters: Parameter untuk query
        :return: Hasil query
        """
        query_type = query_config.get('type', 'sql')
        logger.debug(f"Executing single query of type: {query_type}")
        
        start_time = time.time()
        
        try:
            if query_type == 'sql':
                result = self._execute_sql_query(query_config, parameters)
            elif query_type == 'aggregation':
                result = self._execute_aggregation_query(query_config, parameters)
            elif query_type == 'calculation':
                result = self._execute_calculation_query(query_config, parameters)
            else:
                logger.error(f"Unknown query type: {query_type}")
                raise ValueError(f"Unknown query type: {query_type}")
            
            execution_time = time.time() - start_time
            logger.debug(f"Query type '{query_type}' executed in {execution_time:.3f} seconds")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error in single query execution (type: {query_type}): {str(e)}")
            logger.error(f"Execution time before error: {execution_time:.3f} seconds")
            raise
    
    def _execute_sql_query(self, query_config: Dict, parameters: Dict[str, Any]) -> List[Dict]:
        """Eksekusi SQL query"""
        logger.debug("Executing SQL query...")
        
        sql_template = query_config.get('sql', '')
        logger.debug(f"SQL template length: {len(sql_template)} characters")
        
        start_time = time.time()
        
        # Replace parameters dalam SQL
        sql_query = self._replace_parameters(sql_template, parameters)
        param_replacement_time = time.time() - start_time
        
        logger.debug(f"Parameter replacement completed in {param_replacement_time:.3f} seconds")
        logger.debug(f"Final SQL query length: {len(sql_query)} characters")
        
        # Log SQL query for debugging (truncated if too long)
        if len(sql_query) <= 500:
            logger.debug(f"SQL Query: {sql_query}")
        else:
            logger.debug(f"SQL Query (truncated): {sql_query[:500]}...")
        
        # Execute query
        db_start_time = time.time()
        result = self.db_connector.execute_query(sql_query)
        db_execution_time = time.time() - db_start_time
        
        logger.debug(f"Database execution completed in {db_execution_time:.3f} seconds")
        
        # Process result
        processing_start_time = time.time()
        
        # Convert ke pandas jika diperlukan
        if query_config.get('return_format', 'dict') == 'pandas':
            processed_result = self.db_connector.to_pandas(result)
            logger.debug(f"Result converted to pandas DataFrame")
        else:
            # Return sebagai list of dictionaries
            if result and len(result) > 0 and 'rows' in result[0]:
                processed_result = result[0]['rows']
            else:
                processed_result = []
        
        processing_time = time.time() - processing_start_time
        logger.debug(f"Result processing completed in {processing_time:.3f} seconds")
        
        # Log result statistics
        if isinstance(processed_result, list):
            logger.debug(f"SQL query returned {len(processed_result)} rows")
            if len(processed_result) > 0:
                logger.debug(f"Sample row keys: {list(processed_result[0].keys()) if processed_result[0] else 'Empty row'}")
        else:
            logger.debug(f"SQL query returned non-list result: {type(processed_result)}")
        
        return processed_result

    def _execute_aggregation_query(self, query_config: Dict, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Eksekusi aggregation query"""
        source_query = query_config.get('source_query', '')
        aggregations = query_config.get('aggregations', {})
        
        # Ambil data source
        if source_query in self.data_cache:
            source_data = self.data_cache[source_query]
        else:
            # Execute source query terlebih dahulu
            source_config = self.formulas.get('queries', {}).get(source_query, {})
            source_data = self._execute_single_query(source_config, parameters)
            self.data_cache[source_query] = source_data
        
        # Perform aggregations
        results = {}
        for agg_name, agg_config in aggregations.items():
            results[agg_name] = self._perform_aggregation(source_data, agg_config)
        
        return results
    
    def _execute_calculation_query(self, query_config: Dict, parameters: Dict[str, Any]) -> Any:
        """Eksekusi calculation query"""
        expression = query_config.get('expression', '')
        dependencies = query_config.get('dependencies', [])
        
        # Load dependencies
        dep_data = {}
        for dep in dependencies:
            if dep in self.data_cache:
                dep_data[dep] = self.data_cache[dep]
            else:
                dep_config = self.formulas.get('queries', {}).get(dep, {})
                dep_data[dep] = self._execute_single_query(dep_config, parameters)
                self.data_cache[dep] = dep_data[dep]
        
        # Execute calculation
        return self._evaluate_calculation(expression, dep_data, parameters)
    
    def _replace_parameters(self, template: str, parameters: Dict[str, Any]) -> str:
        """Replace parameter placeholders dalam template"""
        result = template
        
        for key, value in parameters.items():
            placeholder = f"{{{key}}}"
            
            # Format value berdasarkan tipe
            if isinstance(value, date):
                formatted_value = value.strftime('%Y-%m-%d')
            elif isinstance(value, datetime):
                formatted_value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, str):
                formatted_value = f"'{value}'"
            else:
                formatted_value = str(value)
            
            result = result.replace(placeholder, formatted_value)
        
        return result
    
    def _perform_aggregation(self, data: List[Dict], agg_config: Dict) -> Any:
        """Perform aggregation pada data"""
        agg_type = agg_config.get('type', 'sum')
        field = agg_config.get('field', '')
        filter_condition = agg_config.get('filter', None)
        
        # Apply filter jika ada
        if filter_condition:
            data = [row for row in data if self._evaluate_filter(row, filter_condition)]
        
        # Extract field values
        values = []
        for row in data:
            if field in row:
                try:
                    value = float(row[field]) if row[field] is not None else 0
                    values.append(value)
                except (ValueError, TypeError):
                    continue
        
        # Perform aggregation
        if agg_type == 'sum':
            return sum(values)
        elif agg_type == 'count':
            return len(values)
        elif agg_type == 'average':
            return sum(values) / len(values) if values else 0
        elif agg_type == 'max':
            return max(values) if values else 0
        elif agg_type == 'min':
            return min(values) if values else 0
        else:
            return 0
    
    def _evaluate_filter(self, row: Dict, filter_condition: Dict) -> bool:
        """Evaluasi filter condition"""
        field = filter_condition.get('field', '')
        operator = filter_condition.get('operator', '==')
        value = filter_condition.get('value', '')
        
        if field not in row:
            return False
        
        row_value = row[field]
        
        if operator == '==':
            return row_value == value
        elif operator == '!=':
            return row_value != value
        elif operator == '>':
            return float(row_value) > float(value)
        elif operator == '<':
            return float(row_value) < float(value)
        elif operator == '>=':
            return float(row_value) >= float(value)
        elif operator == '<=':
            return float(row_value) <= float(value)
        elif operator == 'contains':
            return str(value).lower() in str(row_value).lower()
        else:
            return False
    
    def _evaluate_calculation(self, expression: str, dep_data: Dict, parameters: Dict[str, Any]) -> Any:
        """Evaluasi calculation expression"""
        logger.debug("Evaluating calculation expression...")
        start_time = time.time()
        
        original_expression = expression
        logger.debug(f"Original expression: {original_expression}")
        logger.debug(f"Dependencies: {list(dep_data.keys())}")
        logger.debug(f"Parameters: {list(parameters.keys())}")
        
        try:
            # Replace dependencies dalam expression
            for dep_name, dep_value in dep_data.items():
                if isinstance(dep_value, (int, float)):
                    expression = expression.replace(f"{{{dep_name}}}", str(dep_value))
                    logger.debug(f"Replaced {{{dep_name}}} with {dep_value}")
                elif isinstance(dep_value, dict):
                    # Jika dependency adalah dict, replace dengan nilai spesifik
                    for key, value in dep_value.items():
                        placeholder = f"{{{dep_name}.{key}}}"
                        if placeholder in expression:
                            expression = expression.replace(placeholder, str(value))
                            logger.debug(f"Replaced {placeholder} with {value}")
            
            # Replace parameters
            for param_name, param_value in parameters.items():
                placeholder = f"{{{param_name}}}"
                if placeholder in expression:
                    expression = expression.replace(placeholder, str(param_value))
                    logger.debug(f"Replaced {placeholder} with {param_value}")
            
            logger.debug(f"Final expression: {expression}")
            
            # Evaluasi expression (hanya operasi matematika dasar)
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expression.replace(' ', '')):
                result = eval(expression)
                evaluation_time = time.time() - start_time
                logger.debug(f"Calculation result: {result} (evaluated in {evaluation_time:.3f} seconds)")
                return result
            else:
                logger.warning(f"Expression contains invalid characters: {expression}")
                return 0
        except Exception as e:
            evaluation_time = time.time() - start_time
            logger.error(f"Error evaluating calculation: {str(e)}")
            logger.error(f"Original expression: {original_expression}")
            logger.error(f"Final expression: {expression}")
            logger.error(f"Evaluation time before error: {evaluation_time:.3f} seconds")
            return 0
    
    def process_variables(self, query_results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Proses semua variable definitions berdasarkan hasil query
        
        :param query_results: Hasil dari execute_data_queries
        :param parameters: Parameter tambahan
        :return: Dictionary berisi nilai semua variables
        """
        logger.info("="*50)
        logger.info("PROCESSING VARIABLES")
        logger.info("="*50)
        
        start_time = time.time()
        
        variables = {}
        variable_definitions = self.formulas.get('variables', {})
        
        logger.info(f"Total variables to process: {len(variable_definitions)}")
        logger.debug(f"Query results keys: {list(query_results.keys())}")
        logger.debug(f"Parameters keys: {list(parameters.keys())}")
        
        # Gabungkan query results dan parameters sebagai context
        context = {**query_results, **parameters}
        
        successful_variables = 0
        failed_variables = 0
        
        for var_name, var_config in variable_definitions.items():
            logger.debug(f"Processing variable: {var_name}")
            var_start_time = time.time()
            
            try:
                value = self._process_single_variable(var_config, context)
                var_processing_time = time.time() - var_start_time
                
                variables[var_name] = value
                successful_variables += 1
                
                logger.info(f"Variable '{var_name}' processed successfully:")
                logger.info(f"  - Value: {value}")
                logger.info(f"  - Processing time: {var_processing_time:.3f} seconds")
                
                print(f"Variable {var_name}: {value}")
                
            except Exception as e:
                var_processing_time = time.time() - var_start_time
                failed_variables += 1
                
                default_value = var_config.get('default', '')
                variables[var_name] = default_value
                
                logger.error(f"Error processing variable '{var_name}': {str(e)}")
                logger.error(f"Using default value: {default_value}")
                logger.error(f"Processing time before error: {var_processing_time:.3f} seconds")
                
                print(f"Error processing variable {var_name}: {e}")
        
        total_processing_time = time.time() - start_time
        
        logger.info("="*50)
        logger.info("VARIABLE PROCESSING SUMMARY")
        logger.info("="*50)
        logger.info(f"Total processing time: {total_processing_time:.3f} seconds")
        logger.info(f"Successful variables: {successful_variables}")
        logger.info(f"Failed variables: {failed_variables}")
        logger.info(f"Success rate: {(successful_variables/(successful_variables+failed_variables)*100):.1f}%" if (successful_variables+failed_variables) > 0 else "N/A")
        
        return variables
    
    def _process_single_variable(self, var_config: Dict, context: Dict[str, Any]) -> Any:
        """Proses satu variable definition"""
        var_type = var_config.get('type', 'direct')
        logger.debug(f"Processing single variable of type: {var_type}")
        
        start_time = time.time()
        
        try:
            if var_type == 'direct':
                result = self._process_direct_variable(var_config, context)
            elif var_type == 'calculation':
                expression = var_config.get('expression', '')
                result = self._evaluate_variable_calculation(expression, context)
            elif var_type == 'aggregation':
                result = self._process_variable_aggregation(var_config, context)
            elif var_type == 'formatting':
                result = self._process_variable_formatting(var_config, context)
            elif var_type == 'conditional':
                result = self._process_variable_conditional(var_config, context)
            else:
                logger.warning(f"Unknown variable type: {var_type}")
                result = var_config.get('default', '')
            
            processing_time = time.time() - start_time
            logger.debug(f"Variable type '{var_type}' processed in {processing_time:.3f} seconds")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error processing variable type '{var_type}': {str(e)}")
            logger.error(f"Processing time before error: {processing_time:.3f} seconds")
            return var_config.get('default', '')
    
    def _process_direct_variable(self, var_config: Dict, context: Dict[str, Any]) -> Any:
        """Process direct variable type"""
        source = var_config.get('source', '')
        default_value = var_config.get('default', '')
        
        logger.debug(f"Processing direct variable with source: {source}")
        
        if source in context:
            result = context[source]
            logger.debug(f"Direct variable found in context: {result}")
            return result
        else:
            logger.debug(f"Direct variable not found in context, using default: {default_value}")
            return default_value
    
    def _evaluate_variable_calculation(self, expression: str, context: Dict[str, Any]) -> Any:
        """Evaluasi calculation untuk variable"""
        logger.debug("Evaluating variable calculation...")
        start_time = time.time()
        
        original_expression = expression
        logger.debug(f"Original variable expression: {original_expression}")
        
        try:
            # Replace context values dalam expression
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                if placeholder in expression:
                    if isinstance(value, (int, float)):
                        expression = expression.replace(placeholder, str(value))
                        logger.debug(f"Replaced {placeholder} with {value}")
                    elif isinstance(value, dict):
                        # Handle nested values
                        for nested_key, nested_value in value.items():
                            nested_placeholder = f"{{{key}.{nested_key}}}"
                            if nested_placeholder in expression:
                                expression = expression.replace(nested_placeholder, str(nested_value))
                                logger.debug(f"Replaced {nested_placeholder} with {nested_value}")
            
            logger.debug(f"Final variable expression: {expression}")
            
            # Evaluasi expression
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expression.replace(' ', '')):
                result = eval(expression)
                evaluation_time = time.time() - start_time
                logger.debug(f"Variable calculation result: {result} (evaluated in {evaluation_time:.3f} seconds)")
                return result
            else:
                logger.warning(f"Variable expression contains invalid characters: {expression}")
                return 0
        except Exception as e:
            evaluation_time = time.time() - start_time
            logger.error(f"Error evaluating variable calculation: {str(e)}")
            logger.error(f"Original expression: {original_expression}")
            logger.error(f"Final expression: {expression}")
            logger.error(f"Evaluation time before error: {evaluation_time:.3f} seconds")
            return 0
    
    def _process_variable_aggregation(self, var_config: Dict, context: Dict[str, Any]) -> Any:
        """Proses aggregation variable"""
        logger.debug("Processing aggregation variable...")
        start_time = time.time()
        
        source = var_config.get('source', '')
        agg_type = var_config.get('aggregation_type', 'sum')
        field = var_config.get('field', '')
        
        logger.debug(f"Aggregation config - source: {source}, type: {agg_type}, field: {field}")
        
        source_data = context.get(source, [])
        if not isinstance(source_data, list):
            logger.warning(f"Source data for aggregation is not a list: {type(source_data)}")
            return 0
        
        logger.debug(f"Source data contains {len(source_data)} records")
        
        result = self._perform_aggregation(source_data, {
            'type': agg_type,
            'field': field,
            'filter': var_config.get('filter')
        })
        
        processing_time = time.time() - start_time
        logger.debug(f"Aggregation variable processed in {processing_time:.3f} seconds, result: {result}")
        
        return result
    
    def _process_variable_formatting(self, var_config: Dict, context: Dict[str, Any]) -> str:
        """Proses formatting variable"""
        logger.debug("Processing formatting variable...")
        start_time = time.time()
        
        source = var_config.get('source', '')
        format_template = var_config.get('format', '{value}')
        format_type = var_config.get('format_type', 'string')
        
        logger.debug(f"Formatting config - source: {source}, template: {format_template}, type: {format_type}")
        
        value = context.get(source, '')
        logger.debug(f"Source value: {value} (type: {type(value)})")
        
        try:
            # Handle special formatting
            if format_type == 'date':
                if isinstance(value, (date, datetime)):
                    result = value.strftime(format_template)
                    logger.debug(f"Date formatted result: {result}")
                else:
                    result = str(value)
                    logger.debug(f"Non-date value converted to string: {result}")
            elif format_type == 'number':
                try:
                    num_value = float(value)
                    result = format_template.format(value=num_value)
                    logger.debug(f"Number formatted result: {result}")
                except Exception as e:
                    result = str(value)
                    logger.warning(f"Number formatting failed, using string: {result}, error: {str(e)}")
            else:
                result = format_template.format(value=value)
                logger.debug(f"String formatted result: {result}")
            
            processing_time = time.time() - start_time
            logger.debug(f"Formatting variable processed in {processing_time:.3f} seconds")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in formatting variable: {str(e)}")
            logger.error(f"Processing time before error: {processing_time:.3f} seconds")
            return str(value)
    
    def _process_variable_conditional(self, var_config: Dict, context: Dict[str, Any]) -> Any:
        """Proses conditional variable"""
        logger.debug("Processing conditional variable...")
        start_time = time.time()
        
        conditions = var_config.get('conditions', [])
        default_value = var_config.get('default', '')
        
        logger.debug(f"Conditional variable has {len(conditions)} conditions")
        logger.debug(f"Default value: {default_value}")
        
        for i, condition in enumerate(conditions):
            logger.debug(f"Evaluating condition {i+1}: {condition}")
            
            if self._evaluate_condition(condition, context):
                result = condition.get('value', default_value)
                processing_time = time.time() - start_time
                logger.debug(f"Condition {i+1} matched, returning: {result}")
                logger.debug(f"Conditional variable processed in {processing_time:.3f} seconds")
                return result
        
        processing_time = time.time() - start_time
        logger.debug(f"No conditions matched, returning default: {default_value}")
        logger.debug(f"Conditional variable processed in {processing_time:.3f} seconds")
        
        return default_value
    
    def _evaluate_condition(self, condition: Dict, context: Dict[str, Any]) -> bool:
        """Evaluasi condition"""
        field = condition.get('field', '')
        operator = condition.get('operator', '==')
        value = condition.get('compare_value', '')
        
        logger.debug(f"Evaluating condition: {field} {operator} {value}")
        
        context_value = context.get(field, '')
        logger.debug(f"Context value for '{field}': {context_value}")
        
        try:
            if operator == '==':
                result = context_value == value
            elif operator == '!=':
                result = context_value != value
            elif operator == '>':
                result = float(context_value) > float(value)
            elif operator == '<':
                result = float(context_value) < float(value)
            elif operator == '>=':
                result = float(context_value) >= float(value)
            elif operator == '<=':
                result = float(context_value) <= float(value)
            elif operator == 'contains':
                result = str(value).lower() in str(context_value).lower()
            else:
                logger.warning(f"Unknown operator: {operator}")
                result = False
            
            logger.debug(f"Condition evaluation result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            logger.error(f"Field: {field}, Operator: {operator}, Value: {value}, Context value: {context_value}")
            return False
    
    def get_repeating_data(self, parameters: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Ambil data untuk repeating sections
        
        :param parameters: Parameter untuk query
        :return: Dictionary berisi data untuk setiap repeating section
        """
        logger.info("="*50)
        logger.info("GETTING REPEATING DATA")
        logger.info("="*50)
        
        start_time = time.time()
        
        repeating_data = {}
        repeating_config = self.formulas.get('repeating_sections', {})
        
        logger.info(f"Total repeating sections: {len(repeating_config)}")
        logger.debug(f"Parameters: {parameters}")
        
        for sheet_name, sections in repeating_config.items():
            logger.info(f"Processing sheet: {sheet_name}")
            sheet_start_time = time.time()
            
            sheet_data = {}
            for section_name, section_config in sections.items():
                logger.debug(f"Processing section: {section_name}")
                section_start_time = time.time()
                
                data_source = section_config.get('data_source', '')
                logger.debug(f"Data source: {data_source}")
                
                # Execute query untuk data source
                if data_source in self.formulas.get('queries', {}):
                    try:
                        query_config = self.formulas['queries'][data_source]
                        section_data = self._execute_single_query(query_config, parameters)
                        sheet_data[section_name] = section_data
                        
                        section_processing_time = time.time() - section_start_time
                        data_count = len(section_data) if isinstance(section_data, list) else 'single value'
                        
                        logger.info(f"Section '{section_name}' processed successfully:")
                        logger.info(f"  - Data count: {data_count}")
                        logger.info(f"  - Processing time: {section_processing_time:.3f} seconds")
                        
                    except Exception as e:
                        section_processing_time = time.time() - section_start_time
                        logger.error(f"Error processing section '{section_name}': {str(e)}")
                        logger.error(f"Processing time before error: {section_processing_time:.3f} seconds")
                        sheet_data[section_name] = []
                else:
                    logger.warning(f"Data source '{data_source}' not found in queries")
                    sheet_data[section_name] = []
            
            if sheet_data:
                repeating_data[sheet_name] = sheet_data
                sheet_processing_time = time.time() - sheet_start_time
                logger.info(f"Sheet '{sheet_name}' completed in {sheet_processing_time:.3f} seconds")
        
        total_processing_time = time.time() - start_time
        
        logger.info("="*50)
        logger.info("REPEATING DATA SUMMARY")
        logger.info("="*50)
        logger.info(f"Total processing time: {total_processing_time:.3f} seconds")
        logger.info(f"Sheets processed: {len(repeating_data)}")
        
        for sheet_name, sheet_data in repeating_data.items():
            logger.info(f"Sheet '{sheet_name}': {len(sheet_data)} sections")
        
        return repeating_data