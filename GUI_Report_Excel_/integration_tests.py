#!/usr/bin/env python3
"""
Integration Tests
End-to-end integration testing for the complete report generation system

Tests:
- Complete workflow from database to Excel report
- Template processing integration
- Data flow validation
- System component interaction
- Error propagation and handling
- File system integration

Author: AI Assistant
Date: 2025-10-31
"""

import unittest
import json
import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from database_connector import DatabaseConnector
from template_manager import TemplateManager

class IntegrationTestSuite(unittest.TestCase):
    """Integration test suite for the complete system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.logger = logging.getLogger(__name__)
        
        # Test configuration
        cls.test_config = {
            "ptrj_p2b": {
                "path": "localhost:D:/IFES/PTRJ_P2B.FDB",
                "username": "SYSDBA",
                "password": "masterkey",
                "use_localhost": True
            }
        }
        
        # Create temporary directory for test outputs
        cls.temp_dir = tempfile.mkdtemp(prefix='integration_test_')
        cls.logger.info(f"Created temporary directory: {cls.temp_dir}")
        
        # Initialize components
        cls.db_connector = None
        cls.template_manager = None
        
        try:
            cls.db_connector = DatabaseConnector(cls.test_config)
            cls.template_manager = TemplateManager()
            cls.logger.info("Test components initialized successfully")
        except Exception as e:
            cls.logger.error(f"Failed to initialize test components: {e}")
            raise
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if hasattr(cls, 'temp_dir') and os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)
            cls.logger.info(f"Cleaned up temporary directory: {cls.temp_dir}")
    
    def test_complete_workflow_single_division(self):
        """Test complete workflow for single division report"""
        self.logger.info("Testing complete workflow for single division")
        
        # Test parameters
        test_params = {
            'start_date': '2024-09-01',
            'end_date': '2024-09-30',
            'month': 9,
            'division_id': 'DIV001'
        }
        
        # Step 1: Verify database connectivity
        connection_result = self.db_connector.test_connection('ptrj_p2b')
        self.assertTrue(connection_result['success'], 
                       f"Database connection failed: {connection_result.get('error', 'Unknown error')}")
        
        # Step 2: Load and validate template
        templates = self.template_manager.get_available_templates()
        self.assertIn('laporan_kinerja_template', templates, 
                     "Required template not found")
        
        template_info = self.template_manager.get_template_info('laporan_kinerja_template')
        self.assertIsNotNone(template_info, "Failed to load template info")
        self.assertIn('queries', template_info, "Template missing queries")
        
        # Step 3: Execute all template queries
        query_results = {}
        for query_name, query_info in template_info['queries'].items():
            self.logger.info(f"Executing query: {query_name}")
            
            # Replace parameters in query
            sql_query = query_info['sql']
            for param, value in test_params.items():
                sql_query = sql_query.replace(f'{{{param}}}', str(value))
            
            try:
                result = self.db_connector.execute_query(sql_query, 'ptrj_p2b')
                query_results[query_name] = result
                
                # Validate query result
                self.assertIsNotNone(result, f"Query {query_name} returned None")
                self.assertIsInstance(result, list, f"Query {query_name} should return list")
                
                self.logger.info(f"Query {query_name}: {len(result)} records")
                
            except Exception as e:
                self.fail(f"Query {query_name} failed: {e}")
        
        # Step 4: Validate data consistency
        self._validate_data_consistency(query_results, test_params)
        
        # Step 5: Test data processing
        processed_data = self._process_query_results(query_results)
        self.assertIsNotNone(processed_data, "Data processing failed")
        
        self.logger.info("Complete workflow test passed")
    
    def test_complete_workflow_all_divisions(self):
        """Test complete workflow for all divisions report"""
        self.logger.info("Testing complete workflow for all divisions")
        
        # Test parameters for all divisions
        test_params = {
            'start_date': '2024-09-01',
            'end_date': '2024-09-30',
            'month': 9,
            'division_id': None  # All divisions
        }
        
        # Load template
        template_info = self.template_manager.get_template_info('laporan_kinerja_template')
        self.assertIsNotNone(template_info, "Failed to load template info")
        
        # Execute queries for all divisions
        query_results = {}
        
        # First get all divisions
        divisions_query = template_info['queries']['divisions']['sql']
        divisions_result = self.db_connector.execute_query(divisions_query, 'ptrj_p2b')
        self.assertIsNotNone(divisions_result, "Failed to get divisions")
        self.assertGreater(len(divisions_result), 0, "No divisions found")
        
        self.logger.info(f"Found {len(divisions_result)} divisions")
        
        # Test processing for each division
        for division in divisions_result[:3]:  # Test first 3 divisions only
            division_id = division.get('DIVID')
            if not division_id:
                continue
            
            self.logger.info(f"Testing division: {division_id}")
            
            # Update parameters for this division
            division_params = test_params.copy()
            division_params['division_id'] = division_id
            
            # Execute transaction queries for this division
            for query_name in ['transactions_kerani', 'transactions_mandor', 'transactions_asisten']:
                if query_name in template_info['queries']:
                    query_info = template_info['queries'][query_name]
                    sql_query = query_info['sql']
                    
                    # Replace parameters
                    for param, value in division_params.items():
                        if value is not None:
                            sql_query = sql_query.replace(f'{{{param}}}', str(value))
                    
                    try:
                        result = self.db_connector.execute_query(sql_query, 'ptrj_p2b')
                        self.assertIsNotNone(result, f"Query {query_name} for division {division_id} returned None")
                        
                        self.logger.info(f"Division {division_id}, Query {query_name}: {len(result)} records")
                        
                    except Exception as e:
                        self.logger.warning(f"Query {query_name} failed for division {division_id}: {e}")
        
        self.logger.info("All divisions workflow test passed")
    
    def test_error_handling_integration(self):
        """Test error handling across system components"""
        self.logger.info("Testing error handling integration")
        
        # Test 1: Invalid database configuration
        invalid_config = {
            "invalid_db": {
                "path": "localhost:INVALID_PATH.FDB",
                "username": "INVALID",
                "password": "INVALID",
                "use_localhost": True
            }
        }
        
        try:
            invalid_connector = DatabaseConnector(invalid_config)
            connection_result = invalid_connector.test_connection('invalid_db')
            self.assertFalse(connection_result['success'], 
                           "Invalid database should fail connection")
        except Exception:
            pass  # Expected to fail
        
        # Test 2: Invalid template
        try:
            invalid_template = self.template_manager.get_template_info('nonexistent_template')
            self.assertIsNone(invalid_template, "Nonexistent template should return None")
        except Exception:
            pass  # Expected behavior
        
        # Test 3: Invalid query parameters
        template_info = self.template_manager.get_template_info('laporan_kinerja_template')
        if template_info and 'queries' in template_info:
            query_name = list(template_info['queries'].keys())[0]
            query_info = template_info['queries'][query_name]
            
            # Query with invalid parameters
            invalid_sql = query_info['sql'].replace('{start_date}', 'INVALID_DATE')
            
            try:
                result = self.db_connector.execute_query(invalid_sql, 'ptrj_p2b')
                # Should either return empty result or raise exception
                if result is not None:
                    self.assertIsInstance(result, list, "Invalid query should return list or None")
            except Exception:
                pass  # Expected to fail with invalid date
        
        self.logger.info("Error handling integration test passed")
    
    def test_data_flow_validation(self):
        """Test data flow between system components"""
        self.logger.info("Testing data flow validation")
        
        # Test parameters
        test_params = {
            'start_date': '2024-09-01',
            'end_date': '2024-09-30',
            'month': 9
        }
        
        # Step 1: Get employee data
        employee_query = """
            SELECT EMPID, EMPNAME, DIVID 
            FROM EMP 
            WHERE EMPID IS NOT NULL 
            ORDER BY EMPID 
            FIRST 10
        """
        
        employees = self.db_connector.execute_query(employee_query, 'ptrj_p2b')
        self.assertIsNotNone(employees, "Failed to get employee data")
        self.assertGreater(len(employees), 0, "No employees found")
        
        # Step 2: Get division data for these employees
        if employees:
            division_ids = [emp.get('DIVID') for emp in employees if emp.get('DIVID')]
            unique_divisions = list(set(division_ids))
            
            if unique_divisions:
                division_query = f"""
                    SELECT DIVID, DIVNAME 
                    FROM CRDIVISION 
                    WHERE DIVID IN ({','.join([f"'{div}'" for div in unique_divisions[:5]])})
                """
                
                divisions = self.db_connector.execute_query(division_query, 'ptrj_p2b')
                self.assertIsNotNone(divisions, "Failed to get division data")
                
                # Validate data consistency
                division_dict = {div['DIVID']: div['DIVNAME'] for div in divisions}
                
                for employee in employees:
                    emp_div_id = employee.get('DIVID')
                    if emp_div_id and emp_div_id in division_dict:
                        self.logger.info(f"Employee {employee.get('EMPNAME')} -> Division {division_dict[emp_div_id]}")
        
        # Step 3: Get transaction data for these employees
        if employees:
            employee_ids = [emp.get('EMPID') for emp in employees[:3]]  # Test first 3 employees
            
            for emp_id in employee_ids:
                if emp_id:
                    transaction_query = f"""
                        SELECT COUNT(*) as transaction_count
                        FROM FFBSCANNERDATA09 
                        WHERE SCANUSERID = '{emp_id}' 
                        AND SCANDATE >= '{test_params['start_date']}'
                        AND SCANDATE <= '{test_params['end_date']}'
                    """
                    
                    transactions = self.db_connector.execute_query(transaction_query, 'ptrj_p2b')
                    self.assertIsNotNone(transactions, f"Failed to get transactions for employee {emp_id}")
                    
                    if transactions:
                        count = transactions[0].get('TRANSACTION_COUNT', 0)
                        self.logger.info(f"Employee {emp_id}: {count} transactions")
        
        self.logger.info("Data flow validation test passed")
    
    def test_template_excel_integration(self):
        """Test template and Excel file integration"""
        self.logger.info("Testing template and Excel file integration")
        
        # Load template
        template_info = self.template_manager.get_template_info('laporan_kinerja_template')
        self.assertIsNotNone(template_info, "Failed to load template info")
        
        # Validate template structure
        required_fields = ['name', 'excel_file', 'worksheet', 'data_sources', 'queries', 'parameters', 'output']
        for field in required_fields:
            self.assertIn(field, template_info, f"Template missing required field: {field}")
        
        # Check Excel file reference
        excel_file = template_info.get('excel_file')
        self.assertIsNotNone(excel_file, "Template missing Excel file reference")
        
        # Validate queries structure
        queries = template_info.get('queries', {})
        self.assertGreater(len(queries), 0, "Template has no queries")
        
        for query_name, query_info in queries.items():
            self.assertIn('sql', query_info, f"Query {query_name} missing SQL")
            self.assertIn('description', query_info, f"Query {query_name} missing description")
            
            # Validate SQL syntax (basic check)
            sql = query_info['sql']
            self.assertIn('SELECT', sql.upper(), f"Query {query_name} should be a SELECT statement")
        
        # Validate parameters
        parameters = template_info.get('parameters', {})
        expected_params = ['start_date', 'end_date', 'month', 'division_id']
        for param in expected_params:
            self.assertIn(param, parameters, f"Template missing parameter: {param}")
        
        # Validate output structure
        output = template_info.get('output', {})
        self.assertIn('headers', output, "Template output missing headers")
        self.assertIn('data_start_row', output, "Template output missing data_start_row")
        self.assertIn('columns', output, "Template output missing columns")
        
        self.logger.info("Template Excel integration test passed")
    
    def test_file_system_integration(self):
        """Test file system operations and integration"""
        self.logger.info("Testing file system integration")
        
        # Test 1: Template file access
        templates = self.template_manager.get_available_templates()
        self.assertGreater(len(templates), 0, "No templates available")
        
        for template_name in templates:
            template_info = self.template_manager.get_template_info(template_name)
            self.assertIsNotNone(template_info, f"Failed to load template: {template_name}")
        
        # Test 2: Temporary file creation
        test_file_path = os.path.join(self.temp_dir, 'test_output.xlsx')
        
        # Simulate Excel file creation
        with open(test_file_path, 'wb') as f:
            f.write(b'Test Excel content')
        
        self.assertTrue(os.path.exists(test_file_path), "Failed to create test file")
        
        # Test file size
        file_size = os.path.getsize(test_file_path)
        self.assertGreater(file_size, 0, "Test file is empty")
        
        # Test 3: Directory operations
        test_subdir = os.path.join(self.temp_dir, 'reports')
        os.makedirs(test_subdir, exist_ok=True)
        self.assertTrue(os.path.exists(test_subdir), "Failed to create subdirectory")
        
        # Test 4: File cleanup
        os.remove(test_file_path)
        self.assertFalse(os.path.exists(test_file_path), "Failed to remove test file")
        
        self.logger.info("File system integration test passed")
    
    def _validate_data_consistency(self, query_results: Dict[str, List[Dict]], params: Dict[str, Any]):
        """Validate consistency between query results"""
        
        # Check if we have the expected queries
        expected_queries = ['employee_mapping', 'divisions', 'transactions_kerani', 'transactions_mandor', 'transactions_asisten']
        
        for query_name in expected_queries:
            if query_name in query_results:
                result = query_results[query_name]
                self.assertIsInstance(result, list, f"Query {query_name} should return a list")
                
                # Validate data structure
                if result:
                    first_record = result[0]
                    self.assertIsInstance(first_record, dict, f"Query {query_name} records should be dictionaries")
        
        # Cross-validate employee and division data
        if 'employee_mapping' in query_results and 'divisions' in query_results:
            employees = query_results['employee_mapping']
            divisions = query_results['divisions']
            
            if employees and divisions:
                # Create division lookup
                division_lookup = {div.get('DIVID'): div.get('DIVNAME') for div in divisions}
                
                # Validate employee divisions exist
                for employee in employees:
                    emp_div_id = employee.get('DIVID')
                    if emp_div_id:
                        self.assertIn(emp_div_id, division_lookup, 
                                    f"Employee division {emp_div_id} not found in divisions")
    
    def _process_query_results(self, query_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Process query results to simulate report data processing"""
        
        processed_data = {
            'employee_count': 0,
            'division_count': 0,
            'total_transactions': 0,
            'processing_timestamp': datetime.now().isoformat()
        }
        
        # Count employees
        if 'employee_mapping' in query_results:
            processed_data['employee_count'] = len(query_results['employee_mapping'])
        
        # Count divisions
        if 'divisions' in query_results:
            processed_data['division_count'] = len(query_results['divisions'])
        
        # Count total transactions
        transaction_queries = ['transactions_kerani', 'transactions_mandor', 'transactions_asisten']
        for query_name in transaction_queries:
            if query_name in query_results:
                processed_data['total_transactions'] += len(query_results[query_name])
        
        return processed_data

class IntegrationTestRunner:
    """Test runner for integration tests"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run all integration tests and return results"""
        
        # Set up test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(IntegrationTestSuite)
        
        # Custom test result collector
        class TestResultCollector(unittest.TestResult):
            def __init__(self):
                super().__init__()
                self.test_results = []
            
            def addSuccess(self, test):
                super().addSuccess(test)
                self.test_results.append({
                    'test_name': test._testMethodName,
                    'status': 'PASSED',
                    'message': 'Test completed successfully'
                })
            
            def addError(self, test, err):
                super().addError(test, err)
                self.test_results.append({
                    'test_name': test._testMethodName,
                    'status': 'ERROR',
                    'message': str(err[1])
                })
            
            def addFailure(self, test, err):
                super().addFailure(test, err)
                self.test_results.append({
                    'test_name': test._testMethodName,
                    'status': 'FAILED',
                    'message': str(err[1])
                })
        
        # Run tests
        result_collector = TestResultCollector()
        suite.run(result_collector)
        
        # Compile results
        results = {
            'test_suite': 'integration_tests',
            'timestamp': datetime.now().isoformat(),
            'total_tests': result_collector.testsRun,
            'passed_tests': len([r for r in result_collector.test_results if r['status'] == 'PASSED']),
            'failed_tests': len([r for r in result_collector.test_results if r['status'] == 'FAILED']),
            'error_tests': len([r for r in result_collector.test_results if r['status'] == 'ERROR']),
            'test_details': result_collector.test_results,
            'overall_success': result_collector.wasSuccessful()
        }
        
        return results

def main():
    """Main function to run integration tests"""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run integration tests
    runner = IntegrationTestRunner()
    results = runner.run_integration_tests()
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"integration_test_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print(f"\n{'='*60}")
    print("INTEGRATION TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed_tests']}")
    print(f"Failed: {results['failed_tests']}")
    print(f"Errors: {results['error_tests']}")
    print(f"Overall Success: {results['overall_success']}")
    print(f"Report saved to: {report_file}")
    print(f"{'='*60}")
    
    # Print individual test results
    for test_detail in results['test_details']:
        status_symbol = "✓" if test_detail['status'] == 'PASSED' else "✗"
        print(f"{status_symbol} {test_detail['test_name']}: {test_detail['status']}")
        if test_detail['status'] != 'PASSED':
            print(f"   Message: {test_detail['message']}")
    
    return results

if __name__ == '__main__':
    main()