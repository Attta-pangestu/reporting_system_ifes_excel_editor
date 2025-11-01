"""
Enhanced Firebird Connector Module
Modul koneksi database Firebird yang robust dengan default database PGE 2B
Didesain untuk digunakan oleh berbagai modul lain dengan mudah
"""

import os
import sys
import subprocess
import tempfile
import json
import re
import pandas as pd
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

class FirebirdConnectorEnhanced:
    """
    Enhanced Firebird Database Connector
    Modul koneksi database Firebird yang robust dengan default database PGE 2B
    """

    # Default configuration
    DEFAULT_DATABASE = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
    DEFAULT_USERNAME = 'SYSDBA'
    DEFAULT_PASSWORD = 'masterkey'

    # Known ISQL paths (prioritize Firebird 1.5 installation)
    ISQL_PATHS = [
        r'C:\Program Files (x86)\Firebird\Firebird_1_5\bin\isql.exe',
        r'C:\Program Files (x86)\Firebird-1.5.6.5026-0_win32_Manual\bin\isql.exe',
        r'C:\Program Files (x86)\Firebird\bin\isql.exe',
        r'C:\Program Files\Firebird\Firebird_2_5\bin\isql.exe',
        r'C:\Program Files\Firebird\Firebird_3_0\bin\isql.exe',
        r'C:\Program Files\Firebird\bin\isql.exe',
        r'C:\Firebird\Firebird_2_5\bin\isql.exe',
        r'C:\Firebird\Firebird_3_0\bin\isql.exe'
    ]

    # Firebird server installation paths
    FIREBIRD_PATHS = [
        r'C:\Program Files (x86)\Firebird\Firebird_1_5',
        r'C:\Program Files\Firebird\Firebird_2_5',
        r'C:\Program Files\Firebird\Firebird_3_0',
        r'C:\Firebird\Firebird_2_5',
        r'C:\Firebird\Firebird_3_0'
    ]

    def __init__(self,
                 db_path: str = None,
                 username: str = None,
                 password: str = None,
                 isql_path: str = None,
                 use_localhost: bool = True,
                 charset: str = 'UTF8',
                 role: str = None,
                 timeout: int = 300):
        """
        Inisialisasi Firebird Connector Enhanced

        Args:
            db_path: Path ke database file (default: PGE 2B)
            username: Username database (default: sysdba)
            password: Password database (default: masterkey)
            isql_path: Path ke ISQL executable (auto-detect jika None)
            use_localhost: Gunakan localhost connection (default: True)
            charset: Character set (default: UTF8)
            role: Database role (optional)
            timeout: Query timeout dalam detik (default: 300)
        """
        self.db_path = db_path or self.DEFAULT_DATABASE
        self.username = username or self.DEFAULT_USERNAME
        self.password = password or self.DEFAULT_PASSWORD
        self.use_localhost = use_localhost
        self.charset = charset
        self.role = role
        self.timeout = timeout

        # Status tracking
        self.is_connected = False
        self.connection_info = {}
        self.last_error = None

        # Initialize ISQL path
        self.isql_path = isql_path or self._detect_isql()

        # Validate setup
        self._validate_setup()

        logger.info(f"Firebird connector initialized - Database: {self.db_path}")
        logger.info(f"ISQL Path: {self.isql_path}")
        logger.info(f"Connection mode: {'localhost' if self.use_localhost else 'direct'}")

    def _detect_isql(self) -> str:
        """Auto-detect ISQL path"""
        logger.info("Detecting ISQL path...")

        for path in self.ISQL_PATHS:
            if os.path.exists(path):
                if self._test_isql(path):
                    logger.info(f"Found working ISQL at: {path}")
                    return path
                else:
                    logger.warning(f"ISQL found but test failed: {path}")

        raise FileNotFoundError("ISQL not found. Please install Firebird client tools.")

    def _test_isql(self, isql_path: str) -> bool:
        """Test if ISQL is working"""
        try:
            # Simple test command
            result = subprocess.run(
                [isql_path, "-h"],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Return True if executable exists (regardless of exit code)
            return True
        except Exception as e:
            logger.debug(f"ISQL test error: {e}")
            return False

    def _validate_setup(self):
        """Validate setup parameters"""
        if not os.path.exists(self.isql_path):
            raise FileNotFoundError(f"ISQL tidak ditemukan: {self.isql_path}")

        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database tidak ditemukan: {self.db_path}")

    def test_connection(self) -> bool:
        """
        Test koneksi ke database

        Returns:
            True jika koneksi berhasil, False jika gagal
        """
        try:
            logger.info(f"Testing connection to: {self.db_path}")

            test_query = "SELECT 'Connection Test' as TEST FROM RDB$DATABASE"
            result = self.execute_query(test_query)

            if result and len(result) > 0:
                self.is_connected = True
                self.connection_info = {
                    'database': self.db_path,
                    'username': self.username,
                    'tested_at': datetime.now().isoformat(),
                    'status': 'Connected'
                }
                logger.info("Connection test successful")
                return True
            else:
                self.last_error = "No result from connection test"
                logger.error("Connection test failed - No result")
                return False

        except Exception as e:
            self.is_connected = False
            self.last_error = str(e)
            logger.error(f"Connection test failed: {e}")
            return False

    def execute_query(self,
                     query: str,
                     parameters: Dict[str, Any] = None,
                     return_format: str = 'dict') -> Union[List[Dict], pd.DataFrame, None]:
        """
        Execute SQL query dengan parameter substitution

        Args:
            query: SQL query string
            parameters: Parameter untuk substitution
            return_format: 'dict', 'dataframe', atau 'raw'

        Returns:
            Query result sesuai format yang diminta
        """
        try:
            # Parameter substitution
            if parameters:
                query = self._substitute_parameters(query, parameters)

            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as sql_file:
                sql_file.write(query + ";\nEXIT;\n")
                sql_file_path = sql_file.name

            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as output_file:
                output_path = output_file.name

            try:
                # Build command
                cmd = self._build_command(sql_file_path, output_path)

                # Execute query
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    timeout=self.timeout
                )

                # Parse output
                data = self._parse_output(output_path, return_format)

                logger.debug(f"Query executed successfully: {len(data)} rows returned")
                return data

            finally:
                # Cleanup temporary files
                self._cleanup_files([sql_file_path, output_path])

        except subprocess.TimeoutExpired:
            error_msg = f"Query timeout after {self.timeout} seconds"
            logger.error(error_msg)
            self.last_error = error_msg
            raise Exception(error_msg)

        except Exception as e:
            error_msg = f"Query execution failed: {e}"
            logger.error(error_msg)
            self.last_error = error_msg
            raise Exception(error_msg)

    def _substitute_parameters(self, query: str, parameters: Dict[str, Any]) -> str:
        """Substitute parameters dalam query"""
        for key, value in parameters.items():
            placeholder = f"{{{key}}}"

            # Handle different data types
            if isinstance(value, str):
                # Escape single quotes for SQL
                escaped_value = value.replace("'", "''")
                query = query.replace(placeholder, f"'{escaped_value}'")
            elif isinstance(value, (datetime, date)):
                # Format dates
                if isinstance(value, datetime):
                    formatted_date = value.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    formatted_date = value.strftime('%Y-%m-%d')
                query = query.replace(placeholder, f"'{formatted_date}'")
            elif isinstance(value, (int, float)):
                query = query.replace(placeholder, str(value))
            elif value is None:
                query = query.replace(placeholder, "NULL")
            else:
                query = query.replace(placeholder, str(value))

        return query

    def _build_command(self, sql_path: str, output_path: str) -> List[str]:
        """Build ISQL command using working format from original connector"""
        conn_str = self._build_connection_string()

        # Use working format: -u username -p password connection_string
        # NOTE: Firebird 1.5 doesn't support -ch charset parameter
        cmd = [
            self.isql_path,
            '-u', self.username,
            '-p', self.password,
            conn_str,
            '-i', sql_path,
            '-o', output_path
        ]

        # Add optional parameters (only if supported by Firebird 1.5)
        if self.role:
            cmd.extend(['-r', self.role])

        return cmd

    def _build_connection_string(self) -> str:
        """Build connection string - use localhost format for working connection"""
        # Always use localhost format as it works with this database
        return f"localhost:{self.db_path}"

    def _parse_output(self, output_path: str, return_format: str) -> Union[List[Dict], pd.DataFrame, None]:
        """Parse ISQL output file using working method from original connector"""
        try:
            with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Use working parsing method from original connector
            result_data = self._parse_isql_output(content, True)

            # Return in requested format
            if return_format == 'dataframe':
                if result_data and result_data[0].get('rows'):
                    return pd.DataFrame(result_data[0]['rows'])
                else:
                    return pd.DataFrame()
            elif return_format == 'dict':
                return result_data
            else:
                return result_data

        except Exception as e:
            logger.error(f"Error parsing output: {e}")
            return []

    def _parse_isql_output(self, output_text, as_dict=True):
        """Parse ISQL output using working method from original connector"""
        lines = output_text.strip().split('\n')
        if not lines:
            return []

        result_data = []
        headers = None
        header_positions = []
        data_lines = []

        # Look for separator line with =====
        has_separator_line = False
        possible_header_line = None

        for i, line in enumerate(lines):
            line = line.rstrip()

            # Skip empty lines and SQL prompts
            if not line or line.startswith('SQL>') or "rows affected" in line.lower():
                continue

            # Look for separator line
            if ('=' * 3) in line:
                if i > 0 and not has_separator_line:
                    possible_header_line = lines[i-1].rstrip()
                    has_separator_line = True
                    # Get column positions from separator
                    header_positions = self._get_column_positions(line)
                continue

            # Collect data rows after header/separator
            if has_separator_line and possible_header_line:
                if line.strip():  # Skip empty lines
                    data_lines.append(line)

        # Process collected data if we have a header
        if has_separator_line and possible_header_line and header_positions:
            # Parse headers
            headers = []
            for start, end in header_positions:
                if start < len(possible_header_line):
                    if end <= len(possible_header_line):
                        header = possible_header_line[start:end].strip()
                    else:
                        header = possible_header_line[start:].strip()
                    headers.append(header)

            # Parse data rows
            rows = []
            for line in data_lines:
                if not line.strip():
                    continue

                row = {}
                for i, (start, end) in enumerate(header_positions):
                    if i >= len(headers):
                        continue
                    col_name = headers[i]
                    if start < len(line):
                        if end <= len(line):
                            value = line[start:end].strip()
                        else:
                            value = line[start:].strip()
                    else:
                        value = ""
                    row[col_name] = value

                # Only add rows that actually have data
                if any(v.strip() for v in row.values()):
                    rows.append(row)

            # Create result set
            result = {"headers": headers, "rows": rows}
            result_data.append(result)

        return result_data

    def _get_column_positions(self, separator_line):
        """Get column positions from separator line"""
        if not separator_line:
            return []

        positions = []
        in_column = False
        start = None

        for i, char in enumerate(separator_line):
            is_separator = char in '=-'

            if is_separator and not in_column:
                start = i
                in_column = True
            elif not is_separator and in_column:
                positions.append((start, i))
                in_column = False
                start = None

        # If the line ends with a separator character
        if in_column and start is not None:
            positions.append((start, len(separator_line)))

        # Special handling: if no positions found, try alternate approach
        if not positions:
            words = []
            word_start = None

            for i, char in enumerate(separator_line):
                if char.strip():
                    if word_start is None:
                        word_start = i
                elif word_start is not None:
                    words.append((word_start, i))
                    word_start = None

            if word_start is not None:
                words.append((word_start, len(separator_line)))

            if words:
                positions = words

        return positions

    def _convert_value(self, value: str) -> Any:
        """Convert string value ke appropriate data type"""
        if value is None or value == '' or value.upper() == 'NULL':
            return None

        # Try integer conversion
        try:
            if '.' not in value:
                return int(value)
        except ValueError:
            pass

        # Try float conversion
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _cleanup_files(self, file_paths: List[str]):
        """Cleanup temporary files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.debug(f"Error cleaning up file {file_path}: {e}")

    # Convenience methods untuk penggunaan yang lebih mudah

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get information tentang table structure

        Args:
            table_name: Nama table

        Returns:
            Dictionary dengan informasi table
        """
        query = f"""
        SELECT
            r.RDB$FIELD_NAME as FIELD_NAME,
            r.RDB$FIELD_TYPE as FIELD_TYPE,
            r.RDB$FIELD_LENGTH as FIELD_LENGTH,
            r.RDB$NULL_FLAG as NULL_FLAG,
            r.RDB$DEFAULT_SOURCE as DEFAULT_VALUE
        FROM RDB$RELATION_FIELDS r
        WHERE r.RDB$RELATION_NAME = '{table_name.upper()}'
        ORDER BY r.RDB$FIELD_POSITION
        """

        try:
            result = self.execute_query(query)
            return {
                'table_name': table_name,
                'columns': result,
                'column_count': len(result) if result else 0
            }
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return {'error': str(e)}

    def get_table_list(self) -> List[str]:
        """
        Get list semua tables dalam database

        Returns:
            List nama tables
        """
        query = """
        SELECT RDB$RELATION_NAME
        FROM RDB$RELATIONS
        WHERE RDB$SYSTEM_FLAG = 0
        ORDER BY RDB$RELATION_NAME
        """

        try:
            result = self.execute_query(query)
            if result and len(result) > 0 and result[0].get('rows'):
                # Extract table names from result
                tables = []
                for row in result[0]['rows']:
                    table_name = row.get('RDB$RELATION_NAME', '').strip()
                    if table_name:
                        tables.append(table_name)
                return tables
            return []
        except Exception as e:
            logger.error(f"Error getting table list: {e}")
            return []

    def check_table_exists(self, table_name: str) -> bool:
        """
        Check apakah table exists

        Args:
            table_name: Nama table

        Returns:
            True jika table exists
        """
        tables = self.get_table_list()
        return table_name.upper() in [t.upper() for t in tables]

    def get_row_count(self, table_name: str, where_clause: str = None) -> int:
        """
        Get jumlah rows dalam table

        Args:
            table_name: Nama table
            where_clause: Optional WHERE clause

        Returns:
            Jumlah rows
        """
        query = f"SELECT COUNT(*) as ROW_COUNT FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"

        try:
            result = self.execute_query(query)
            if result and len(result) > 0:
                return int(result[0]['ROW_COUNT'])
            return 0
        except Exception as e:
            logger.error(f"Error getting row count for {table_name}: {e}")
            return 0

    def get_sample_data(self, table_name: str, limit: int = 10) -> List[Dict]:
        """
        Get sample data dari table

        Args:
            table_name: Nama table
            limit: Jumlah maksimal rows

        Returns:
            List data rows
        """
        query = f"SELECT FIRST {limit} * FROM {table_name}"

        try:
            return self.execute_query(query) or []
        except Exception as e:
            logger.error(f"Error getting sample data for {table_name}: {e}")
            return []

    def execute_batch_queries(self, queries: List[str], parameters: Dict[str, Any] = None) -> List[Dict]:
        """
        Execute multiple queries dalam batch

        Args:
            queries: List SQL queries
            parameters: Parameters untuk substitution

        Returns:
            List results
        """
        results = []

        for i, query in enumerate(queries):
            try:
                result = self.execute_query(query, parameters)
                results.append({
                    'query_index': i,
                    'query': query,
                    'success': True,
                    'data': result
                })
                logger.debug(f"Batch query {i+1} successful")
            except Exception as e:
                results.append({
                    'query_index': i,
                    'query': query,
                    'success': False,
                    'error': str(e)
                })
                logger.error(f"Batch query {i+1} failed: {e}")

        return results

    # Static methods untuk kemudahan penggunaan

    @staticmethod
    def create_default_connector() -> 'FirebirdConnectorEnhanced':
        """
        Create connector dengan default database PGE 2B

        Returns:
            FirebirdConnectorEnhanced instance
        """
        return FirebirdConnectorEnhanced()

    @staticmethod
    def create_custom_connector(db_path: str, **kwargs) -> 'FirebirdConnectorEnhanced':
        """
        Create connector dengan custom database

        Args:
            db_path: Path ke database file
            **kwargs: Additional parameters

        Returns:
            FirebirdConnectorEnhanced instance
        """
        return FirebirdConnectorEnhanced(db_path=db_path, **kwargs)

    # Utility methods

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get informasi koneksi

        Returns:
            Dictionary dengan informasi koneksi
        """
        return {
            'database_path': self.db_path,
            'username': self.username,
            'is_connected': self.is_connected,
            'isql_path': self.isql_path,
            'connection_mode': 'localhost' if self.use_localhost else 'direct',
            'charset': self.charset,
            'connection_info': self.connection_info,
            'last_error': self.last_error
        }

    def get_database_size(self) -> Dict[str, Any]:
        """
        Get informasi ukuran database

        Returns:
            Dictionary dengan informasi ukuran
        """
        try:
            if os.path.exists(self.db_path):
                size_bytes = os.path.getsize(self.db_path)
                return {
                    'size_bytes': size_bytes,
                    'size_mb': round(size_bytes / (1024 * 1024), 2),
                    'size_gb': round(size_bytes / (1024 * 1024 * 1024), 2),
                    'file_exists': True
                }
            else:
                return {'file_exists': False, 'error': 'Database file not found'}
        except Exception as e:
            return {'error': str(e)}

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        # Nothing to cleanup for now
        pass

    def detect_firebird_installation(self) -> Dict[str, Any]:
        """
        Detect Firebird installation

        Returns:
            Dictionary dengan informasi installation
        """
        installation_info = {
            'found': False,
            'paths': [],
            'version': 'Unknown',
            'isql_found': False,
            'isql_path': None
        }

        for path in self.FIREBIRD_PATHS:
            if os.path.exists(path):
                installation_info['found'] = True
                installation_info['paths'].append(path)

                # Try to determine version from path
                if '1_5' in path:
                    installation_info['version'] = '1.5'
                elif '2_5' in path:
                    installation_info['version'] = '2.5'
                elif '3_0' in path:
                    installation_info['version'] = '3.0'
                break

        # Check ISQL availability
        if os.path.exists(self.isql_path):
            installation_info['isql_found'] = True
            installation_info['isql_path'] = self.isql_path

        return installation_info

    def start_firebird_server(self) -> bool:
        """
        Start Firebird server (if not already running)

        Returns:
            True jika berhasil
        """
        try:
            # Check if server is already running
            if self.check_server_running():
                logger.info("Firebird server is already running")
                return True

            # Look for fbguard.exe
            fbguard_paths = []
            for fb_path in self.FIREBIRD_PATHS:
                if os.path.exists(fb_path):
                    fbguard_path = os.path.join(fb_path, 'bin', 'fbguard.exe')
                    if os.path.exists(fbguard_path):
                        fbguard_paths.append(fbguard_path)

            if not fbguard_paths:
                logger.error("fbguard.exe not found")
                return False

            fbguard_path = fbguard_paths[0]  # Use first found

            logger.info(f"Starting Firebird server from: {fbguard_path}")

            # Start fbguard
            import subprocess
            import psutil

            # Kill any existing Firebird processes
            self._kill_firebird_processes()

            # Start new process
            fbguard_dir = os.path.dirname(fbguard_path)
            process = subprocess.Popen(
                [fbguard_path],
                cwd=fbguard_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                close_fds=True
            )

            # Wait for startup
            import time
            time.sleep(5)

            # Check if server started successfully
            if self.check_server_running():
                logger.info("Firebird server started successfully")
                return True
            else:
                logger.error("Firebird server failed to start")
                return False

        except Exception as e:
            logger.error(f"Error starting Firebird server: {e}")
            return False

    def _kill_firebird_processes(self):
        """Kill existing Firebird processes"""
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info()['name'].lower()
                    if 'fbguard' in proc_name or 'fbserver' in proc_name:
                        proc.terminate()
                        logger.info(f"Terminated existing Firebird process: {proc_name}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.debug(f"Error killing Firebird processes: {e}")

    def check_server_running(self) -> bool:
        """
        Check if Firebird server is running

        Returns:
            True jika server berjalan
        """
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info()['name'].lower()
                    if 'fbguard' in proc_name or 'fbserver' in proc_name:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception:
            return False

    def ensure_server_running(self) -> bool:
        """
        Ensure Firebird server is running, start if necessary

        Returns:
            True jika server berjalan
        """
        if not self.check_server_running():
            logger.info("Firebird server not running, attempting to start...")
            return self.start_firebird_server()
        else:
            logger.info("Firebird server is already running")
            return True

    def __repr__(self):
        """String representation"""
        return f"FirebirdConnectorEnhanced(db='{self.db_path}', connected={self.is_connected})"


# Convenience functions untuk kemudahan penggunaan

def connect_to_pge2b(**kwargs) -> FirebirdConnectorEnhanced:
    """
    Quick connect ke PGE 2B database

    Args:
        **kwargs: Additional parameters

    Returns:
        FirebirdConnectorEnhanced instance
    """
    return FirebirdConnectorEnhanced.create_default_connector(**kwargs)

def test_pge2b_connection() -> bool:
    """
    Test koneksi ke PGE 2B database

    Returns:
        True jika koneksi berhasil
    """
    try:
        with connect_to_pge2b() as conn:
            return conn.test_connection()
    except Exception as e:
        logger.error(f"PGE 2B connection test failed: {e}")
        return False

def get_pge2b_tables() -> List[str]:
    """
    Get list tables dari PGE 2B database

    Returns:
        List nama tables
    """
    try:
        with connect_to_pge2b() as conn:
            return conn.get_table_list()
    except Exception as e:
        logger.error(f"Error getting PGE 2B tables: {e}")
        return []

def execute_pge2b_query(query: str, parameters: Dict[str, Any] = None) -> List[Dict]:
    """
    Execute query di PGE 2B database

    Args:
        query: SQL query
        parameters: Query parameters

    Returns:
        Query results
    """
    try:
        with connect_to_pge2b() as conn:
            return conn.execute_query(query, parameters)
    except Exception as e:
        logger.error(f"Error executing PGE 2B query: {e}")
        return []


# Main untuk testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Firebird Enhanced Connector Test")
    print("=" * 40)

    # Test connection
    try:
        connector = FirebirdConnectorEnhanced.create_default_connector()

        print(f"Database: {connector.db_path}")
        print(f"ISQL: {connector.isql_path}")

        # Test connection
        if connector.test_connection():
            print("✓ Connection successful!")

            # Get tables
            tables = connector.get_table_list()
            print(f"Found {len(tables)} tables")

            # Look for FFB tables
            ffb_tables = [t for t in tables if 'FFB' in t.upper() or 'SCANNER' in t.upper()]
            if ffb_tables:
                print(f"FFB/Scanner tables: {ffb_tables}")

                # Get sample data
                sample_data = connector.get_sample_data(ffb_tables[0], limit=5)
                print(f"Sample data from {ffb_tables[0]}:")
                for i, row in enumerate(sample_data[:3]):
                    print(f"  Row {i+1}: {list(row.keys())[:3]}...")
            else:
                print("No FFB/Scanner tables found")

        else:
            print("✗ Connection failed")
            print(f"Error: {connector.last_error}")

    except Exception as e:
        print(f"Error: {e}")

    print("\nTest completed!")