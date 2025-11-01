# Enhanced Firebird Connector Documentation

## Overview

Enhanced Firebird Connector adalah modul koneksi database Firebird yang robust dengan default database PGE 2B. Modul ini dirancang untuk mudah digunakan oleh berbagai modul lain dengan fitur-fitur lengkap.

## Features

### 🔧 **Core Features**
- **Auto-detection ISQL path** - Mencari ISQL secara otomatis
- **Default database PGE 2B** - Tidak perlu setup path manual
- **Multiple return formats** - Support dict, DataFrame, raw output
- **Parameter substitution** - Safe parameter binding dengan `{{variable}}` syntax
- **Error handling** - Comprehensive error handling dan logging
- **Timeout management** - Konfigurasi timeout untuk query

### 🎯 **Advanced Features**
- **Connection pooling ready** - Support untuk future enhancements
- **Query batch execution** - Execute multiple queries sekaligus
- **Context manager support** - Dapat digunakan dengan `with` statement
- **Table inspection** - Get table info, column details, row counts
- **Data type conversion** - Otomatis konversi tipe data
- **Comprehensive logging** - Debugging friendly dengan detailed logs

## Installation & Setup

### Dependencies
```python
# Required (built-in Python)
import os
import sys
import subprocess
import tempfile
import json
import re
import pandas as pd  # pip install pandas
```

### Basic Setup
```python
from firebird_connector_enhanced import FirebirdConnectorEnhanced

# Create dengan default PGE 2B database
connector = FirebirdConnectorEnhanced.create_default_connector()
```

## Usage Examples

### 1. **Quick Start - Default Connection**

```python
from firebird_connector_enhanced import connect_to_pge2b

# Simple connection dengan default database
with connect_to_pge2b() as conn:
    if conn.test_connection():
        tables = conn.get_table_list()
        print(f"Found {len(tables)} tables")
```

### 2. **Custom Database Connection**

```python
from firebird_connector_enhanced import FirebirdConnectorEnhanced

# Custom database path
connector = FirebirdConnectorEnhanced(
    db_path=r"D:\Custom\Path\database.fdb",
    username="myuser",
    password="mypass"
)

# Test connection
if connector.test_connection():
    print("Connected successfully!")
```

### 3. **Basic Query Execution**

```python
# Simple query
data = connector.execute_query("SELECT * FROM TABLE_NAME")

# Return as DataFrame
df = connector.execute_query("SELECT * FROM TABLE_NAME", return_format='dataframe')

# Query with parameters
query = "SELECT * FROM TRANSACTIONS WHERE DATE >= '{start_date}'"
params = {'start_date': '2025-10-01'}
data = connector.execute_query(query, params)
```

### 4. **Convenience Functions**

```python
from firebird_connector_enhanced import (
    execute_pge2b_query,
    get_pge2b_tables,
    test_pge2b_connection
)

# Quick query execution
data = execute_pge2b_query("SELECT COUNT(*) FROM FFB_TABLE")

# Get table list
tables = get_pge2b_tables()

# Test connection
if test_pge2b_connection():
    print("PGE 2B is accessible")
```

### 5. **Table Operations**

```python
# Check if table exists
if connector.check_table_exists('FFB_TABLE'):
    print("Table exists")

# Get table information
table_info = connector.get_table_info('FFB_TABLE')
print(f"Columns: {table_info['column_count']}")

# Get row count
row_count = connector.get_row_count('FFB_TABLE', "STATUS = 'ACTIVE'")
print(f"Active rows: {row_count}")

# Get sample data
sample_data = connector.get_sample_data('FFB_TABLE', limit=10)
```

### 6. **Batch Query Execution**

```python
queries = [
    "SELECT COUNT(*) FROM TABLE1",
    "SELECT COUNT(*) FROM TABLE2",
    "SELECT MAX(DATE) FROM TABLE3"
]

results = connector.execute_batch_queries(queries)

for result in results:
    if result['success']:
        print(f"Query {result['query_index']}: Success")
    else:
        print(f"Query {result['query_index']}: Failed - {result['error']}")
```

### 7. **Error Handling & Information**

```python
# Get connection information
info = connector.get_connection_info()
print(f"Database: {info['database_path']}")
print(f"Connected: {info['is_connected']}")
print(f"Last Error: {info['last_error']}")

# Get database size
db_info = connector.get_database_size()
print(f"Database size: {db_info['size_mb']} MB")

# Using context manager
with FirebirdConnectorEnhanced.create_default_connector() as conn:
    try:
        data = conn.execute_query("SELECT * FROM TABLE_NAME")
        print(f"Retrieved {len(data)} rows")
    except Exception as e:
        print(f"Query failed: {e}")
```

## Configuration

### Default Settings
```python
DEFAULT_DATABASE = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
DEFAULT_USERNAME = 'sysdba'
DEFAULT_PASSWORD = 'masterkey'
DEFAULT_CHARSET = 'UTF8'
DEFAULT_TIMEOUT = 300  # seconds
```

### Custom Configuration
```python
connector = FirebirdConnectorEnhanced(
    db_path=r"Custom\Path\database.fdb",
    username="myuser",
    password="mypass",
    isql_path=r"Custom\ISQL\isql.exe",  # Override auto-detection
    use_localhost=True,                   # Connection mode
    charset="WIN1252",                    # Character set
    role="MY_ROLE",                       # Database role
    timeout=600                           # Query timeout
)
```

## Parameter Substitution

### Syntax
Gunakan `{{variable_name}}` syntax dalam query:

```python
query = """
SELECT * FROM TRANSACTIONS
WHERE DATE BETWEEN '{start_date}' AND '{end_date}'
  AND STATUS = '{status}'
"""

params = {
    'start_date': '2025-10-01',
    'end_date': '2025-10-31',
    'status': 'ACTIVE'
}

data = connector.execute_query(query, params)
```

### Supported Data Types
- **String**: Automatically escaped and quoted
- **Integer/Float**: Direct substitution
- **Date/DateTime**: Formatted as SQL datetime
- **None**: Converted to NULL
- **Boolean**: Converted to 1/0

## Return Formats

### 1. **Dictionary Format (Default)**
```python
data = connector.execute_query("SELECT * FROM TABLE")
# Returns: List[Dict] - [{'COL1': 'value1', 'COL2': 'value2'}, ...]
```

### 2. **DataFrame Format**
```python
df = connector.execute_query("SELECT * FROM TABLE", return_format='dataframe')
# Returns: pandas.DataFrame
```

### 3. **Raw Format**
```python
data = connector.execute_query("SELECT * FROM TABLE", return_format='raw')
# Returns: Raw parsed data structure
```

## Error Handling

### Common Errors & Solutions

#### 1. **ISQL Not Found**
```python
try:
    connector = FirebirdConnectorEnhanced()
except FileNotFoundError as e:
    print(f"ISQL not found: {e}")
    # Install Firebird client tools
```

#### 2. **Database Connection Failed**
```python
connector = FirebirdConnectorEnhanced()
if not connector.test_connection():
    info = connector.get_connection_info()
    print(f"Connection failed: {info['last_error']}")
    # Check database path and Firebird server status
```

#### 3. **Query Timeout**
```python
# Increase timeout for long queries
connector = FirebirdConnectorEnhanced(timeout=600)  # 10 minutes
```

#### 4. **Invalid Query**
```python
try:
    data = connector.execute_query("INVALID QUERY")
except Exception as e:
    print(f"Query error: {e}")
    # Check SQL syntax and table names
```

## Logging

### Enable Logging
```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logs will appear from 'firebird_connector_enhanced' logger
```

### Log Levels
- **INFO**: Connection info, ISQL detection
- **DEBUG**: Query execution details
- **ERROR**: Connection failures, query errors
- **WARNING**: Non-critical issues

## Best Practices

### 1. **Use Context Managers**
```python
# Good
with connect_to_pge2b() as conn:
    data = conn.execute_query("SELECT * FROM TABLE")

# Avoid (manual cleanup not guaranteed)
conn = connect_to_pge2b()
data = conn.execute_query("SELECT * FROM TABLE")
```

### 2. **Handle Connection Failures**
```python
def safe_query(query, params=None):
    try:
        with connect_to_pge2b() as conn:
            if conn.test_connection():
                return conn.execute_query(query, params)
            else:
                raise Exception("Database connection failed")
    except Exception as e:
        print(f"Query failed: {e}")
        return None
```

### 3. **Use Parameter Substitution**
```python
# Good (SQL injection safe)
query = "SELECT * FROM TABLE WHERE NAME = '{name}'"
params = {'name': "O'Reilly"}  # Automatically escaped
data = conn.execute_query(query, params)

# Bad (SQL injection vulnerable)
query = f"SELECT * FROM TABLE WHERE NAME = 'O'Reilly'"
data = conn.execute_query(query)  # Will fail
```

### 4. **Choose Appropriate Return Format**
```python
# For data analysis
df = conn.execute_query("SELECT * FROM LARGE_TABLE", return_format='dataframe')

# For simple lookups
data = conn.execute_query("SELECT STATUS FROM CONFIG WHERE ID = 1")
if data:
    status = data[0]['STATUS']
```

## Integration with Other Modules

### Import in Other Modules
```python
# In your module
from firebird_connector_enhanced import (
    FirebirdConnectorEnhanced,
    connect_to_pge2b,
    execute_pge2b_query
)

def get_ffb_data(start_date, end_date):
    """Get FFB data for report"""
    query = """
    SELECT DATE, COUNT(*) as TRANSACTIONS, SUM(WEIGHT) as TOTAL_WEIGHT
    FROM FFB_TRANSACTIONS
    WHERE DATE BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY DATE
    ORDER BY DATE
    """

    return execute_pge2b_query(query, {
        'start_date': start_date,
        'end_date': end_date
    })
```

### Dependency Injection
```python
class ReportGenerator:
    def __init__(self, db_connector=None):
        self.db = db_connector or FirebirdConnectorEnhanced.create_default_connector()

    def generate_report(self):
        data = self.db.execute_query("SELECT * FROM REPORT_DATA")
        # Process data
        return data
```

## Performance Tips

### 1. **Use LIMIT for Large Tables**
```python
# Good - Limit results
sample_data = connector.get_sample_data('LARGE_TABLE', limit=100)

# Bad - May return millions of rows
all_data = connector.execute_query("SELECT * FROM LARGE_TABLE")
```

### 2. **Optimize Query Structure**
```python
# Good - Indexed columns first
query = "SELECT * FROM TABLE WHERE DATE_INDEXED >= '{date}'"

# Bad - Non-indexed columns first
query = "SELECT * FROM TABLE WHERE DESCRIPTION LIKE '%text%'"
```

### 3. **Use Appropriate Timeouts**
```python
# Quick queries
quick_conn = FirebirdConnectorEnhanced(timeout=30)

# Long-running reports
report_conn = FirebirdConnectorEnhanced(timeout=1800)  # 30 minutes
```

## Troubleshooting

### Common Issues

#### 1. **"Database unavailable" Error**
- Check Firebird server is running
- Verify database file exists and is not corrupted
- Check file permissions

#### 2. **"ISQL not found" Error**
- Install Firebird client tools
- Check ISQL path in system PATH
- Specify custom ISQL path manually

#### 3. **"No result" from Queries**
- Check SQL syntax
- Verify table and column names
- Check for proper COMMIT in procedures

#### 4. **Encoding Issues**
- Use appropriate charset (UTF8, WIN1252, etc.)
- Check database character set
- Handle special characters properly

### Debug Mode
```python
import logging
logging.getLogger('firebird_connector_enhanced').setLevel(logging.DEBUG)

# Now detailed debug information will be logged
connector = FirebirdConnectorEnhanced()
```

## Version History

- **v1.0** - Initial release with basic functionality
- **v1.1** - Added convenience functions and error handling
- **v1.2** - Enhanced parameter substitution and logging
- **v1.3** - Added DataFrame support and batch queries

## Support

For issues or questions:
1. Check troubleshooting section above
2. Enable debug logging for detailed information
3. Verify database connection and Firebird server status
4. Check this documentation for usage examples

---

*This connector is designed specifically for PGE 2B database but can be easily configured for other Firebird databases.*