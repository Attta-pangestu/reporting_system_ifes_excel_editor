# Technical Specifications - Excel Report Generator

## System Requirements

### Software Requirements
- **Python**: 3.7 or higher
- **Operating System**: Windows (tested), Linux/macOS (compatible)
- **Database**: Firebird 1.5+ with ISQL client
- **Excel**: Microsoft Excel 2007+ format support (.xlsx)

### Python Dependencies
```
openpyxl>=3.0.0    # Excel file manipulation
tkinter            # GUI framework (built-in)
```

## Architecture Overview

### Component Interaction Flow
```
GUI Application
    ↓
ReportGenerator
    ↓
┌─────────────────┬─────────────────┐
│ TemplateProcessor │  FormulaEngine   │
│                 │        ↓        │
│                 │ FirebirdConnector│
└─────────────────┴─────────────────┘
    ↓
Excel Output File
```

## Class Specifications

### TemplateProcessor
```python
class TemplateProcessor:
    def __init__(self, template_path: str, formula_path: str)
    def get_placeholder_info(self) -> dict
    def populate_data(self, data: dict) -> None
    def save_report(self, output_path: str) -> str
```

**Responsibilities:**
- Load Excel templates using openpyxl
- Identify placeholders in format `{{variable_name}}`
- Apply data to template cells
- Handle formatting and styling
- Save final Excel files

### FormulaEngine
```python
class FormulaEngine:
    def __init__(self, formula_path: str, db_connector: FirebirdConnector)
    def execute_queries(self, variables: dict) -> dict
    def get_query_data(self, query_name: str, variables: dict) -> list
```

**Responsibilities:**
- Parse JSON formula definitions
- Execute SQL queries via FirebirdConnector
- Process query results
- Handle variable substitution
- Manage repeating sections

### ReportGenerator
```python
class ReportGenerator:
    def __init__(self, template_path: str, formula_path: str, db_config: dict)
    def generate_report(self, output_path: str, variables: dict) -> str
```

**Responsibilities:**
- Orchestrate report generation process
- Coordinate between TemplateProcessor and FormulaEngine
- Handle error management and logging
- Provide unified interface for report creation

### FirebirdConnector
```python
class FirebirdConnector:
    def __init__(self, db_path: str, host: str = "localhost", 
                 user: str = "SYSDBA", password: str = "masterkey")
    def execute_query(self, query: str) -> list
    def test_connection(self) -> bool
```

**Responsibilities:**
- Manage Firebird database connections
- Execute SQL queries via ISQL subprocess
- Parse ISQL output into structured data
- Handle database errors and timeouts

## Data Formats

### Formula Definition JSON Schema
```json
{
  "queries": {
    "string": "string (SQL query)"
  },
  "variables": {
    "string": "any (variable value)"
  },
  "repeating_sections": {
    "string": {
      "query": "string (query name)",
      "start_row": "integer",
      "columns": ["string (column letters)"],
      "sheet": "string (sheet name, optional)"
    }
  },
  "formatting": {
    "styles": {
      "string": {
        "bold": "boolean",
        "bg_color": "string (hex color)",
        "number_format": "string (Excel format)"
      }
    }
  }
}
```

### Configuration JSON Schema
```json
{
  "estates": {
    "string (estate_id)": {
      "name": "string (display name)",
      "db_path": "string (database file path)"
    }
  }
}
```

## Database Integration

### ISQL Command Format
```bash
isql -user {user} -password {password} {host}:{db_path} -q -o {output_file}
```

### Query Result Parsing
- Tab-separated values from ISQL output
- Header row identification
- Data type inference
- NULL value handling
- Error message extraction

## Template Processing

### Placeholder Syntax
- Format: `{{variable_name}}`
- Case-sensitive matching
- Support for nested objects: `{{object.property}}`
- Array indexing: `{{array[0]}}`

### Repeating Sections
- Dynamic row insertion
- Column mapping from JSON definition
- Automatic formatting application
- Row numbering and calculations

### Formatting Rules
- Style inheritance from template
- JSON-defined style overrides
- Number format preservation
- Cell merging and borders

## Error Handling

### Exception Hierarchy
```
ReportGeneratorError (base)
├── TemplateError
│   ├── TemplateNotFoundError
│   ├── TemplateFormatError
│   └── PlaceholderError
├── DatabaseError
│   ├── ConnectionError
│   ├── QueryError
│   └── ISQLError
└── FormulaError
    ├── FormulaParseError
    └── VariableError
```

### Logging Configuration
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('report_generator.log'),
        logging.StreamHandler()
    ]
)
```

## Performance Specifications

### Memory Usage
- Template loading: ~5-10MB per template
- Query results: Variable based on data size
- Peak usage: ~50MB for typical reports

### Processing Time
- Template loading: <1 second
- Query execution: 1-30 seconds (database dependent)
- Report generation: 2-10 seconds
- Total time: 5-45 seconds typical

### Scalability Limits
- Maximum rows per sheet: 1,048,576 (Excel limit)
- Maximum columns per sheet: 16,384 (Excel limit)
- Recommended query result size: <100,000 rows
- Concurrent report generation: Not supported

## Security Considerations

### Database Security
- Credentials stored in configuration files
- No SQL injection protection (trusted queries only)
- ISQL subprocess execution with full privileges
- Database file access requires appropriate permissions

### File System Security
- Template files require read access
- Output directory requires write access
- Temporary files created during processing
- No encryption of sensitive data

## Testing Framework

### Test Categories
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **System Tests**: End-to-end functionality
4. **Performance Tests**: Load and stress testing

### Test Data Requirements
- Sample Firebird database with test data
- Various Excel template formats
- Edge case formula definitions
- Invalid input scenarios

## Deployment Considerations

### Installation Requirements
1. Python environment setup
2. Firebird client installation
3. Database connectivity verification
4. File system permissions configuration

### Configuration Management
- Environment-specific config files
- Database connection parameters
- Template and formula file locations
- Output directory permissions

### Monitoring and Maintenance
- Log file rotation and archival
- Database connection health checks
- Template file integrity verification
- Performance metric collection

## API Extensions

### Future Enhancement Points
- REST API wrapper for web integration
- Batch processing capabilities
- Template validation utilities
- Custom formatting functions
- Additional database connectors
- Cloud storage integration

### Plugin Architecture
- Custom data source plugins
- Template processor extensions
- Formatting rule plugins
- Export format plugins