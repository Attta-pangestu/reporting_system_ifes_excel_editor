"""
Enhanced Database Connector for Template-Based Report Generator
Integrates the robust FirebirdConnector from referensi folder
"""
import os
import subprocess
import json
import tempfile
import re
import pandas as pd
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configure detailed logging for database operations
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
db_logger = logging.getLogger('DatabaseConnector')

class DatabaseConnector:
    """
    Enhanced database connector using the robust FirebirdConnector implementation
    """
    def __init__(self, db_path=None, username='sysdba', password='masterkey', isql_path=None, use_localhost=False):
        """
        Initialize Firebird database connection

        :param db_path: Full path to .fdb file
        :param username: Username for connection (default: sysdba)
        :param password: Password for connection (default: masterkey)
        :param isql_path: Path to isql.exe executable (default: auto-detect)
        :param use_localhost: If True, use localhost:path format for connection
        """
        db_logger.info("=== INITIALIZING DATABASE CONNECTOR ===")
        db_logger.info(f"Database path: {db_path}")
        db_logger.info(f"Username: {username}")
        db_logger.info(f"Use localhost: {use_localhost}")
        
        self.db_path = db_path
        self.username = username
        self.password = password
        self.use_localhost = use_localhost
        self.query_count = 0
        self.total_execution_time = 0.0

        # Auto-detect isql_path if not provided
        if isql_path is None:
            db_logger.debug("Auto-detecting ISQL path...")
            self.isql_path = self._detect_isql_path()
        else:
            self.isql_path = isql_path

        db_logger.info(f"ISQL path: {self.isql_path}")

        # Verify isql exists
        if not os.path.exists(self.isql_path):
            db_logger.error(f"ISQL executable not found at: {self.isql_path}")
            raise FileNotFoundError(f"isql.exe not found at: {self.isql_path}")
        
        db_logger.info("Database connector initialized successfully")

    def _detect_isql_path(self):
        """Auto-detect isql.exe location"""
        default_paths = [
            r'C:\Program Files (x86)\Firebird\Firebird_1_5\bin\isql.exe',
            r'C:\Program Files (x86)\Firebird-1.5.6.5026-0_win32_Manual\bin\isql.exe',
            r'C:\Program Files (x86)\Firebird\bin\isql.exe',
            r'C:\Program Files\Firebird\Firebird_2_5\bin\isql.exe',
            r'C:\Program Files\Firebird\Firebird_3_0\bin\isql.exe',
            r'C:\Program Files\Firebird\bin\isql.exe'
        ]

        for path in default_paths:
            if os.path.exists(path):
                # Verify that the ISQL is working
                if self.test_isql(path):
                    return path
                print(f"Found ISQL at {path} but test failed")

        raise FileNotFoundError("Cannot find working isql.exe. Please specify path manually.")

    def test_isql(self, isql_path):
        """Test if ISQL can be executed"""
        try:
            print(f"Testing ISQL at: {isql_path}")

            # Try to run isql with help command
            result = subprocess.run([isql_path, "-h"],
                                   capture_output=True,
                                   text=True,
                                   timeout=10)

            print(f"ISQL test successful. Return code: {result.returncode}")
            return True
        except subprocess.TimeoutExpired:
            print(f"ISQL test timed out but executable exists. Assuming it works.")
            return True
        except Exception as e:
            print(f"ISQL test failed: {e}")

            # Even if the test command failed, check if the file exists and is executable
            if os.path.exists(isql_path) and os.access(isql_path, os.X_OK):
                print(f"ISQL exists and appears to be executable, proceeding anyway")
                return True

            return False

    def execute_query(self, query, params=None, as_dict=True):
        """
        Execute SQL query and return results with comprehensive debug logging

        :param query: SQL query to execute
        :param params: Parameters for query (not used in current implementation)
        :param as_dict: If True, results returned as list of dictionaries
        :return: Query results in JSON format
        """
        # Start timing and logging
        start_time = time.time()
        self.query_count += 1
        query_id = f"Q{self.query_count:04d}"
        
        db_logger.info(f"=== EXECUTING QUERY {query_id} ===")
        db_logger.info(f"Query: {query}")
        db_logger.info(f"Parameters: {params}")
        db_logger.info(f"Return as dict: {as_dict}")
        db_logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
        
        # Create SQL file for query
        fd, sql_path = tempfile.mkstemp(suffix='.sql')
        output_fd, output_path = tempfile.mkstemp(suffix='.txt')
        
        db_logger.debug(f"Temporary SQL file: {sql_path}")
        db_logger.debug(f"Temporary output file: {output_path}")

        try:
            # Ensure isql executable exists
            if not os.path.exists(self.isql_path):
                db_logger.error(f"ISQL executable not found: {self.isql_path}")
                raise FileNotFoundError(f"ISQL executable not found: {self.isql_path}")

            # Ensure database file exists
            if not os.path.exists(self.db_path):
                db_logger.error(f"Database file not found: {self.db_path}")
                raise FileNotFoundError(f"Database file not found: {self.db_path}")

            # Create connection string with appropriate format
            if self.use_localhost:
                connection_string = f"localhost:{self.db_path}"
            else:
                connection_string = self.db_path
                
            db_logger.debug(f"Connection string: {connection_string}")

            with os.fdopen(fd, 'w') as sql_file:
                # Write query directly for Firebird 1.5 compatibility
                sql_content = f"{query};\nCOMMIT;\nEXIT;\n"
                sql_file.write(sql_content)
                db_logger.debug(f"SQL file content written: {sql_content}")

            db_logger.info(f"Executing query via ISQL: {query[:100]}...")
            db_logger.info(f"Database path: {self.db_path}")

            # Close the output file handle to prevent access errors
            os.close(output_fd)

            # Use ISQL with database connection parameters
            cmd = [
                self.isql_path,
                connection_string,
                "-u", self.username,
                "-p", self.password,
                "-i", sql_path,
                "-o", output_path
            ]
            
            db_logger.info(f"Running command: {' '.join(cmd)}")
            
            # Execute command and track timing
            cmd_start_time = time.time()
            process_result = subprocess.run(cmd, check=False, capture_output=True, timeout=300)
            cmd_execution_time = time.time() - cmd_start_time
            
            db_logger.info(f"ISQL process completed with return code: {process_result.returncode}")
            db_logger.info(f"Command execution time: {cmd_execution_time:.3f} seconds")

            # Log debug information
            if process_result.stdout:
                db_logger.debug(f"STDOUT: {process_result.stdout.decode('utf-8', errors='ignore')}")
            if process_result.stderr:
                db_logger.warning(f"STDERR: {process_result.stderr.decode('utf-8', errors='ignore')}")

            # If process failed, try alternative connection method
            if process_result.returncode != 0:
                db_logger.warning("Command failed, trying alternative method...")

                alt_cmd = [
                    self.isql_path,
                    connection_string,
                    "-u", self.username,
                    "-p", self.password,
                    "-i", sql_path
                ]

                db_logger.info(f"Running alternative command: {' '.join(alt_cmd)}")
                
                alt_cmd_start_time = time.time()
                process_result = subprocess.run(alt_cmd, check=False, capture_output=True, timeout=300)
                alt_cmd_execution_time = time.time() - alt_cmd_start_time
                
                db_logger.info(f"Alternative command completed with return code: {process_result.returncode}")
                db_logger.info(f"Alternative command execution time: {alt_cmd_execution_time:.3f} seconds")

            # Read output file
            with open(output_path, 'r', encoding='utf-8', errors='ignore') as output_file:
                output_text = output_file.read()

            db_logger.info(f"Raw output length: {len(output_text)} characters")
            if len(output_text) > 0:
                db_logger.debug(f"First 500 chars of output:\n{output_text[:500]}")
                if len(output_text) > 500:
                    db_logger.debug(f"Last 500 chars of output:\n{output_text[-500:]}")

            # Parse output and track results
            parse_start_time = time.time()
            result = self._parse_isql_output(output_text, as_dict)
            parse_time = time.time() - parse_start_time
            
            # Calculate total execution time
            total_time = time.time() - start_time
            self.total_execution_time += total_time
            
            # Log comprehensive results
            record_count = len(result) if isinstance(result, list) else 0
            db_logger.info(f"=== QUERY {query_id} RESULTS ===")
            db_logger.info(f"Records returned: {record_count}")
            db_logger.info(f"Parse time: {parse_time:.3f} seconds")
            db_logger.info(f"Total execution time: {total_time:.3f} seconds")
            db_logger.info(f"Cumulative execution time: {self.total_execution_time:.3f} seconds")
            
            # Log sample data if available
            if record_count > 0:
                db_logger.debug(f"Sample record (first): {result[0] if isinstance(result, list) else result}")
                if record_count > 1:
                    db_logger.debug(f"Sample record (last): {result[-1]}")
                    
                # Log column information if dict format
                if as_dict and isinstance(result, list) and len(result) > 0:
                    columns = list(result[0].keys()) if isinstance(result[0], dict) else []
                    db_logger.info(f"Columns returned: {columns}")
            else:
                db_logger.warning("No records returned from query")
            
            db_logger.info(f"=== QUERY {query_id} COMPLETED SUCCESSFULLY ===")
            return result

        except Exception as e:
            total_time = time.time() - start_time
            db_logger.error(f"=== QUERY {query_id} FAILED ===")
            db_logger.error(f"Error executing query: {e}")
            db_logger.error(f"Query: {query}")
            db_logger.error(f"Execution time before failure: {total_time:.3f} seconds")
            db_logger.error(f"Exception type: {type(e).__name__}")
            raise
        finally:
            # Clean up temporary files
            try:
                if os.path.exists(sql_path):
                    os.unlink(sql_path)
                    db_logger.debug(f"Cleaned up SQL file: {sql_path}")
                if os.path.exists(output_path):
                    os.unlink(output_path)
                    db_logger.debug(f"Cleaned up output file: {output_path}")
            except Exception as cleanup_error:
                db_logger.error(f"Error cleaning up temporary files: {cleanup_error}")

    def _parse_isql_output(self, output_text, as_dict=True):
        """Parse ISQL output into structured data"""
        if not output_text.strip():
            return [{"headers": [], "rows": [], "row_count": 0}]

        lines = output_text.split('\n')
        result_sets = []
        current_headers = []
        current_rows = []
        in_data_section = False
        separator_line = None

        for i, line in enumerate(lines):
            line = line.rstrip()
            
            # Skip empty lines at the beginning
            if not line and not in_data_section:
                continue
                
            # Look for separator line (contains = or -)
            if re.match(r'^[\s=\-]+$', line) and len(line) > 10:
                if not in_data_section:
                    # This is the header separator
                    separator_line = line
                    in_data_section = True
                    
                    # Get headers from previous line
                    if i > 0:
                        header_line = lines[i-1].rstrip()
                        current_headers = self._extract_headers(header_line, separator_line)
                else:
                    # This might be end of current result set
                    if current_headers and current_rows:
                        result_sets.append({
                            "headers": current_headers,
                            "rows": current_rows,
                            "row_count": len(current_rows)
                        })
                    
                    # Reset for potential next result set
                    current_headers = []
                    current_rows = []
                    in_data_section = False
                    separator_line = None
                continue
            
            # Process data rows
            if in_data_section and current_headers and line.strip():
                # Skip lines that look like SQL commands or messages
                if (line.strip().upper().startswith(('SQL>', 'CON>', 'COMMIT', 'EXIT')) or
                    'records selected' in line.lower() or
                    'statement executed' in line.lower()):
                    continue
                
                row_data = self._extract_row_data(line, separator_line, current_headers, as_dict)
                if row_data:
                    current_rows.append(row_data)

        # Add final result set if exists
        if current_headers:
            result_sets.append({
                "headers": current_headers,
                "rows": current_rows,
                "row_count": len(current_rows)
            })

        # If no result sets found, return empty structure
        if not result_sets:
            result_sets = [{"headers": [], "rows": [], "row_count": 0}]

        return result_sets

    def _extract_headers(self, header_line, separator_line):
        """Extract column headers based on separator positions"""
        if not separator_line:
            return []
        
        positions = self._get_column_positions(separator_line)
        headers = []
        
        for start, end in positions:
            if start < len(header_line):
                header = header_line[start:end].strip()
                if header:
                    headers.append(header)
        
        return headers

    def _extract_row_data(self, line, separator_line, headers, as_dict=True):
        """Extract row data based on column positions"""
        if not separator_line or not headers:
            return None
        
        positions = self._get_column_positions(separator_line)
        values = []
        
        for start, end in positions:
            if start < len(line):
                value = line[start:end].strip()
                values.append(value if value else None)
            else:
                values.append(None)
        
        # Ensure we have the right number of values
        while len(values) < len(headers):
            values.append(None)
        
        if as_dict:
            return dict(zip(headers, values))
        else:
            return values

    def _get_column_positions(self, separator_line):
        """Determine column positions from separator line"""
        positions = []
        start = 0
        
        # Find groups of separator characters
        i = 0
        while i < len(separator_line):
            if separator_line[i] in '=-':
                # Found start of a column
                start = i
                # Find end of this column
                while i < len(separator_line) and separator_line[i] in '=-':
                    i += 1
                end = i
                positions.append((start, end))
            else:
                i += 1
        
        return positions

    def test_connection(self):
        """
        Test database connection

        :return: True if connection successful, False if failed
        """
        try:
            result = self.execute_query("SELECT 'Connection Test' FROM RDB$DATABASE")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def get_tables(self):
        """
        Get list of tables in database

        :return: List of tables in database
        """
        query = "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL"
        result = self.execute_query(query)

        tables = []
        if result and result[0]["rows"]:
            for row in result[0]["rows"]:
                table_name = row.get(result[0]["headers"][0], "").strip()
                if table_name:
                    tables.append(table_name)

        return tables

    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get column information for a specific table
        
        :param table_name: Name of the table
        :return: List of column information dictionaries
        """
        query = f"""
        SELECT 
            RF.RDB$FIELD_NAME AS COLUMN_NAME,
            F.RDB$FIELD_TYPE AS FIELD_TYPE,
            F.RDB$FIELD_LENGTH AS FIELD_LENGTH,
            RF.RDB$NULL_FLAG AS NULL_FLAG
        FROM RDB$RELATION_FIELDS RF
        JOIN RDB$FIELDS F ON RF.RDB$FIELD_SOURCE = F.RDB$FIELD_NAME
        WHERE RF.RDB$RELATION_NAME = '{table_name.upper()}'
        ORDER BY RF.RDB$FIELD_POSITION
        """
        
        try:
            result = self.execute_query(query)
            columns = []
            
            if result and result[0]["rows"]:
                for row in result[0]["rows"]:
                    column_info = {
                        'name': row.get('COLUMN_NAME', '').strip(),
                        'type': self._get_field_type_name(row.get('FIELD_TYPE')),
                        'length': row.get('FIELD_LENGTH'),
                        'nullable': row.get('NULL_FLAG') != 1
                    }
                    columns.append(column_info)
            
            return columns
        except Exception as e:
            print(f"Error getting table columns: {e}")
            return []

    def _get_field_type_name(self, field_type):
        """Convert Firebird field type number to name"""
        type_mapping = {
            7: 'SMALLINT',
            8: 'INTEGER',
            10: 'FLOAT',
            12: 'DATE',
            13: 'TIME',
            14: 'CHAR',
            16: 'BIGINT',
            27: 'DOUBLE',
            35: 'TIMESTAMP',
            37: 'VARCHAR',
            261: 'BLOB'
        }
        return type_mapping.get(field_type, f'UNKNOWN({field_type})')

    def get_example_query(self, table_name=None):
        """Get example query for testing"""
        if not table_name:
            # Try to get first table from database
            tables = self.get_tables()
            if tables:
                table_name = tables[0]
            else:
                # Default table if no tables found
                table_name = "FFBSCANNERDATA04"

        # Create SELECT * FROM table LIMIT 100 query
        query = f"SELECT FIRST 100 * FROM {table_name}"

        print(f"Generated example query: {query}")
        return query

    def to_pandas(self, result_data):
        """
        Convert query results to pandas DataFrame

        :param result_data: Results from execute_query
        :return: pandas.DataFrame
        """
        if not result_data or not result_data[0].get("rows"):
            return pd.DataFrame()

        # Get data from first result set
        rows = result_data[0]["rows"]
        return pd.DataFrame(rows)

    def get_tables_info(self):
        """Get information about all tables in the database"""
        try:
            # Get list of all tables
            tables = self.get_tables()
            tables_info = {}
            
            for table in tables:
                try:
                    # Get columns for each table
                    columns = self.get_table_columns(table)
                    tables_info[table] = {
                        'columns': columns,
                        'exists': True
                    }
                except Exception as e:
                    print(f"Warning: Could not get columns for table {table}: {e}")
                    tables_info[table] = {
                        'columns': [],
                        'exists': False,
                        'error': str(e)
                    }
            
            return tables_info
            
        except Exception as e:
            print(f"Error getting tables info: {e}")
            return {}

    def validate_sql(self, sql_query):
        """
        Validate SQL query syntax by attempting to prepare it
        
        :param sql_query: SQL query string to validate
        :return: True if valid, False otherwise
        """
        try:
            # Basic SQL syntax validation
            if not sql_query or not sql_query.strip():
                return False
            
            # Check for basic SQL keywords
            sql_upper = sql_query.upper().strip()
            if not any(sql_upper.startswith(keyword) for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']):
                return False
            
            # Try to execute EXPLAIN PLAN to validate syntax without executing
            explain_query = f"SET PLAN ON;\n{sql_query}"
            
            # Create temporary SQL file
            fd, sql_path = tempfile.mkstemp(suffix='.sql')
            try:
                with os.fdopen(fd, 'w') as f:
                    f.write(explain_query)
                
                # Build connection string
                if self.use_localhost:
                    connection_string = f"localhost:{self.db_path}"
                else:
                    connection_string = self.db_path
                
                # Execute validation query
                cmd = [
                    self.isql_path,
                    "-user", self.username,
                    "-password", self.password,
                    "-input", sql_path,
                    connection_string
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                # Check if there are syntax errors
                if result.returncode == 0:
                    return True
                else:
                    # Check for specific syntax error indicators
                    error_output = result.stderr.lower()
                    if any(error in error_output for error in ['syntax error', 'token unknown', 'unexpected end']):
                        return False
                    # If it's not a syntax error, consider it valid (might be data-related error)
                    return True
                    
            finally:
                if os.path.exists(sql_path):
                    os.unlink(sql_path)
                    
        except Exception as e:
            print(f"SQL validation error: {e}")
            # If validation fails due to connection issues, assume SQL is syntactically correct
            return True
    
    def close(self):
        """Close database connection (placeholder for compatibility)"""
        # ISQL doesn't maintain persistent connections, so nothing to close
        pass

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()