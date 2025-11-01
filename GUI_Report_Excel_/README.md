# Template-Based Report Generator System

A comprehensive GUI application for generating Excel reports from Firebird databases using customizable templates.

## 🚀 Features

- **Template-Based Architecture**: Create reusable report templates with Excel + JSON configuration
- **GUI Interface**: User-friendly interface for database selection, template management, and report generation
- **Database Integration**: Native Firebird database connectivity with fallback to ISQL
- **Template Validation**: Comprehensive validation system for template consistency
- **Professional Formatting**: Auto-formatting, styling, and data transformation capabilities
- **Modular Design**: Extensible architecture for adding new report types

## 📁 Project Structure

```
GUI_Report_Excel_/
├── main_app.py              # Main GUI application
├── template_manager.py      # Template loading and management
├── database_connector.py    # Firebird database connectivity
├── report_processor.py      # Report generation engine
├── validator.py             # Template validation system
├── config_manager.py        # Configuration management
├── test_system.py          # System testing script
├── templates/              # Template storage directory
│   ├── sample_template.json    # JSON configuration
│   └── sample_template.xlsx    # Excel template
├── outputs/                # Generated reports directory
└── README.md              # This documentation
```

## 🛠️ Installation & Setup

### Prerequisites

1. **Python 3.8+** with required packages:
   ```bash
   pip install tkinter openpyxl fdb pathlib logging threading
   ```

2. **Firebird Database** with client libraries installed
   - Download from: https://firebirdsql.org/en/downloads/
   - Ensure `fbclient.dll` is in system PATH

### Quick Start

1. **Clone/Download** the project files
2. **Run the application**:
   ```bash
   python main_app.py
   ```
3. **Configure database** connection in the GUI
4. **Select template** and generate reports

## 📋 Usage Guide

### 1. Database Configuration

1. Click **"Browse Database"** to select your Firebird database file (.fdb)
2. Click **"Test Connection"** to verify connectivity
3. Status indicator shows connection state (🟢 Connected / 🔴 Failed)

### 2. Template Management

1. **Available Templates** are automatically detected from `templates/` directory
2. **Select Template** from dropdown menu
3. **Validate Template** to check consistency and compatibility
4. **View validation results** in popup window

### 3. Report Generation

1. **Select Output Folder** for generated reports
2. **Configure Parameters** (date ranges, filters, etc.)
3. **Click "Generate Report"** to start processing
4. **Monitor Progress** in the log area
5. **Open Generated Report** automatically when complete

## 🎯 Template Creation

### Template Structure

Each template consists of two files:

1. **Excel Template** (`template_name.xlsx`):
   - Contains layout, formatting, and placeholders
   - Uses `{{placeholder}}` syntax for dynamic content
   - Supports multiple worksheets

2. **JSON Configuration** (`template_name.json`):
   - Defines database queries and data mappings
   - Specifies transformations and formatting rules
   - Contains validation requirements

### Sample Template Configuration

```json
{
  "template_info": {
    "name": "sample_template",
    "description": "Sample FFB Performance Report",
    "version": "1.0",
    "author": "System Administrator"
  },
  "database_requirements": {
    "required_tables": ["TRANSAKSI_FFB", "MASTER_ESTATE"],
    "required_columns": ["TGL_TRANSAKSI", "KODE_ESTATE", "BERAT_FFB"]
  },
  "queries": [
    {
      "name": "date_range",
      "description": "Get report date range",
      "sql": "SELECT MIN(TGL_TRANSAKSI) as start_date, MAX(TGL_TRANSAKSI) as end_date FROM TRANSAKSI_FFB",
      "type": "single_row"
    }
  ],
  "mappings": {
    "{{REPORT_TITLE}}": "FFB Performance Report",
    "{{START_DATE}}": "query:date_range:start_date",
    "{{END_DATE}}": "query:date_range:end_date"
  },
  "transformations": [
    {
      "type": "date_format",
      "format": "DD/MM/YYYY",
      "columns": ["TGL_TRANSAKSI"]
    }
  ]
}
```

### Creating New Templates

1. **Create Excel Template**:
   ```python
   python create_sample_template.py
   ```

2. **Customize Layout**:
   - Add headers, tables, charts
   - Use `{{placeholder}}` for dynamic content
   - Apply desired formatting

3. **Configure JSON**:
   - Define database queries
   - Map placeholders to data
   - Set transformation rules

4. **Validate Template**:
   ```python
   python test_system.py
   ```

## 🔧 Configuration

### Application Settings (`app_config.json`)

```json
{
  "application": {
    "name": "Template Report Generator",
    "version": "1.0.0",
    "debug_mode": false
  },
  "paths": {
    "templates_dir": "./templates",
    "output_dir": "./outputs",
    "logs_dir": "./logs"
  },
  "ui": {
    "window_width": 800,
    "window_height": 600,
    "theme": "default"
  }
}
```

### Database Settings (`database_config.json`)

```json
{
  "databases": {
    "main_db": {
      "name": "Main Database",
      "path": "path/to/database.fdb",
      "description": "Primary production database"
    }
  },
  "connection_settings": {
    "charset": "UTF8",
    "timeout": 30,
    "retry_attempts": 3
  }
}
```

## 🧪 Testing

### System Tests

Run comprehensive system tests:
```bash
python test_system.py
```

Tests include:
- ✅ File Structure Validation
- ✅ Template Manager Functionality
- ✅ Template Validator Operations
- ✅ Configuration Manager
- ✅ Database Connectivity (if available)

### Manual Testing

1. **Template Validation**:
   - Load sample template
   - Check validation results
   - Verify error reporting

2. **Report Generation**:
   - Connect to test database
   - Generate sample report
   - Verify output formatting

## 🐛 Troubleshooting

### Common Issues

1. **Firebird Client Library Not Found**:
   ```
   ERROR: The location of Firebird Client Library could not be determined
   ```
   **Solution**: Install Firebird client libraries and ensure `fbclient.dll` is in PATH

2. **Template Validation Errors**:
   ```
   ERROR: Missing required key: template_info
   ```
   **Solution**: Check JSON template structure and required fields

3. **Database Connection Failed**:
   ```
   ERROR: Failed to connect to database
   ```
   **Solution**: Verify database path, permissions, and Firebird service status

### Fallback Options

- **ISQL Mode**: Automatic fallback when native connectivity fails
- **Template Validation**: Works offline without database connection
- **Configuration Recovery**: Auto-creates default configurations

## 📊 Performance Features

- **Optimized Queries**: Efficient SQL generation and execution
- **Memory Management**: Streaming data processing for large datasets
- **Progress Tracking**: Real-time generation progress updates
- **Error Recovery**: Graceful handling of database and template errors

## 🔒 Security Considerations

- **SQL Injection Protection**: Parameterized queries and validation
- **File Path Validation**: Secure template and output file handling
- **Configuration Security**: Encrypted database credentials (future enhancement)

## 🚀 Future Enhancements

- [ ] **Multi-Database Support**: PostgreSQL, MySQL, SQL Server
- [ ] **Advanced Templates**: Charts, pivot tables, conditional formatting
- [ ] **Scheduled Reports**: Automated report generation
- [ ] **Web Interface**: Browser-based report management
- [ ] **API Integration**: REST API for external systems
- [ ] **Template Marketplace**: Shared template repository

## 📞 Support

For technical support or feature requests:
1. Check troubleshooting section above
2. Run system tests to identify issues
3. Review log files in `logs/` directory
4. Contact system administrator

## 📄 License

This project is developed for internal use. All rights reserved.

---

**Version**: 1.0.0  
**Last Updated**: October 31, 2025  
**Author**: AI Assistant  
**Status**: Production Ready ✅