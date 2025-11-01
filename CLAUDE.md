# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Excel Report Generator System for PT. Rebinmas Jaya that automatically generates Excel reports from Firebird database data. The system processes FFB (Fresh Fruit Bunch) transaction data and creates performance reports for clerks, foremen, and assistants across multiple plantation estates.

## Core Architecture

The system follows a modular architecture with five main components:

1. **ReportGenerator** (`report_generator.py`) - Main orchestrator that coordinates template processing, data retrieval, and Excel output generation
2. **FirebirdConnector** (`firebird_connector.py`) - Database connectivity layer using ISQL for Firebird database access
3. **TemplateProcessor** (`template_processor.py`) - Handles Excel template loading and placeholder variable processing
4. **FormulaEngine** (`formula_engine.py`) - Processes JSON-defined formulas and executes SQL queries
5. **GUI Application** (`gui_excel_report_generator.py`) - Tkinter-based user interface for report generation

## Key Files and Their Purposes

### Core System Files
- `report_generator.py` - Main entry point for programmatic report generation
- `firebird_connector.py` - Database abstraction layer for Firebird connectivity
- `template_processor.py` - Excel template processing with `{{variable}}` placeholder support
- `formula_engine.py` - JSON-based formula definition and SQL execution engine
- `gui_excel_report_generator.py` - User interface application

### Configuration and Templates
- `config.json` - Estate database configuration mapping estate names to .fdb file paths
- `laporan_kinerja_formula.json` - Comprehensive formula definitions for performance reports
- `sample_formula.json` - Basic FFB analysis formula definitions
- `Laporan_Kinerja_Kerani_Mandor_Asisten_Template.xlsx` - Excel template for performance reports

### Database Analysis Tools
- `analyze_database.py`, `simple_db_analysis.py`, `robust_db_analysis.py` - Database structure analysis
- `master_table_discovery.py` - Core table discovery for FFBSCANNERDATA tables
- `analyze_table_structure.py`, `analyze_field_structure.py` - Detailed table/column analysis
- `extract_tables.py`, `simple_table_check.py` - Table validation tools

### Testing and Generation
- `test_system.py` - Comprehensive system testing suite
- `create_sample_template.py` - Utility for creating sample Excel templates
- `excel_report_generator*.py` - Various report generation implementations

## Common Development Commands

### Running the GUI Application
```bash
python gui_excel_report_generator.py
```

### Running System Tests
```bash
python test_system.py
```

### Database Analysis
```bash
python master_table_discovery.py
python analyze_table_structure.py
```

### Creating Sample Templates
```bash
python create_sample_template.py
```

## Dependencies

### Python Packages
- `openpyxl` - Excel file manipulation (core dependency)
- `tkinter` - GUI framework (built-in with Python)
- `pandas` - Data processing and analysis
- `tkcalendar` - Date picker widgets for GUI

### External Requirements
- Firebird database server
- ISQL executable (Firebird client tool) - automatically detected in standard paths

## Database Configuration

The system connects to multiple plantation estate databases through `config.json`. Each estate has:
- Estate name as key
- Full path to .fdb database file as value

Default ISQL detection paths:
- `C:\Program Files (x86)\Firebird\Firebird_1_5\bin\isql.exe`
- `C:\Program Files\Firebird\Firebird_2_5\bin\isql.exe`
- `C:\Program Files\Firebird\Firebird_3_0\bin\isql.exe`

## Formula Definition System

The system uses JSON-based formula definitions with this structure:

```json
{
  "queries": {
    "query_name": {
      "type": "sql",
      "sql": "SELECT ... FROM ... WHERE ...",
      "return_format": "dict"
    }
  },
  "variables": {
    "variable_name": {
      "type": "direct|calculation|formatting|conditional",
      "source": "query.field or expression"
    }
  },
  "repeating_sections": {
    "sheet_name": {
      "section_name": {
        "data_source": "query_name",
        "start_row": 10,
        "columns": {...}
      }
    }
  }
}
```

## Template System

Excel templates use `{{variable_name}}` placeholder syntax. The system supports:
- Single variable replacement: `{{estate_name}}`
- Date formatting: `{{report_date|format:%d %B %Y}}`
- Calculated fields: `{{total_amount}}`
- Conditional formatting based on values

## Multi-Estate Processing

The system processes multiple estates simultaneously:
1. Loads estate configuration from `config.json`
2. Iterates through selected estates
3. Connects to each estate's Firebird database
4. Executes queries with estate-specific parameters
5. Generates consolidated or individual reports

## Error Handling and Logging

- Comprehensive error handling for database connectivity
- ISQL path validation and auto-detection
- Template file validation
- SQL query error reporting
- GUI error notifications with detailed messages

## Database Schema Focus

Primary analysis targets:
- `FFBSCANNERDATA01` through `FFBSCANNERDATA12` tables (monthly data)
- `EMP` table (employee information)
- `OCFIELD` table (field/block information)
- `CRDIVISION` table (division mappings)

Key transaction fields:
- `TRANSDATE`, `TRANSTIME` - Transaction timestamps
- `SCANUSERID`, `WORKERID` - Employee identifiers
- `FIELDID` - Location identifier
- `RIPEBCH`, `UNRIPEBCH`, `BLACKBCH` - Quality metrics
- `RECORDTAG` - Transaction type ('PM' for clerk, 'P1' for foreman, 'P5' for assistant)

## Development Notes

- All file paths use Windows format with backslashes
- Database connections use ISQL rather than direct Python DB-API
- Template processing preserves Excel formatting and styling
- The system handles both Indonesian and English field names
- Date formatting supports Indonesian locale
- Multi-threading is used in GUI for non-blocking operations