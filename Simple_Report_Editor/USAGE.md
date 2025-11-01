# Simple Report Editor - Usage Guide

## Overview

Simple Report Editor adalah aplikasi berbasis GUI untuk menghasilkan laporan FFB (Fresh Fruit Bunch) dari template yang sudah didefinisikan. Aplikasi ini memproses data dari database Firebird dan menghasilkan laporan Excel/PDF yang terstruktur.

## Features

- **Template-based Report Generation**: Gunakan template Excel dengan placeholder `{{variable}}`
- **Data Preview**: Preview data sebelum generate laporan
- **Multi-format Output**: Generate laporan dalam format Excel dan PDF
- **Firebird Database Integration**: Koneksi otomatis ke database Firebird
- **Flexible Parameters**: Konfigurasi tanggal dan parameter lainnya
- **Progress Tracking**: Monitor proses generation dengan progress bar

## Requirements

- Python 3.7+
- Firebird Database dengan ISQL client
- Libraries:
  - `openpyxl` - Excel file manipulation
  - `tkinter` - GUI framework (built-in)
  - `pandas` - Data processing (optional)

## Installation

1. Pastikan Python 3.7+ sudah terinstall
2. Install Firebird Database dengan ISQL client
3. Install required libraries:
   ```bash
   pip install openpyxl pandas
   ```

## Quick Start

1. Buka command prompt dan navigasi ke directory `Simple_Report_Editor`
2. Jalankan aplikasi:
   ```bash
   python simple_report_editor.py
   ```
3. Pilih template dari dropdown
4. Konfigurasi parameter (tanggal, database)
5. Klik "Preview Data" untuk melihat data
6. Klik "Generate Report" untuk generate laporan

## Template System

### Template Excel Structure
Template Excel menggunakan placeholder dengan format `{{variable_name}}`:

```
LAPORAN FFB SCANNER DATA 04
Estate: {{estate_name}}
Period: {{report_period}}
Date: {{report_date}}

DATA TRANSAKSI FFB
{{data_records}}  <-- Repeating section untuk data tabel

SUMMARY:
Total Records: {{summary.total_records}}
Total Bunch: {{summary.total_ripe_bunch}}
```

### Formula JSON Configuration
Setiap template memiliki file JSON konfigurasi:

```json
{
  "template_info": {
    "name": "FFB Scanner Data Report",
    "description": "Laporan transaksi FFB"
  },
  "queries": {
    "main_data": {
      "sql": "SELECT * FROM {table_name} WHERE TRANSDATE BETWEEN {start_date} AND {end_date}",
      "return_format": "dict"
    }
  },
  "variables": {
    "estate_name": {
      "type": "constant",
      "value": "PGE 2B"
    },
    "report_date": {
      "type": "formatting",
      "source": "TODAY()",
      "format": "dd MMMM yyyy"
    }
  },
  "repeating_sections": {
    "Sheet1": {
      "data_section": {
        "data_source": "main_data",
        "start_row": 12,
        "columns": {"A": "ID", "B": "SCANUSERID", "C": "WORKERID"}
      }
    }
  }
}
```

## Configuration

### Database Configuration
Edit `config/app_config.json` untuk mengatur database:

```json
{
  "database_settings": {
    "default_database": "D:\\Path\\To\\Your\\Database.FDB",
    "default_username": "SYSDBA",
    "default_password": "masterkey"
  }
}
```

### Template Directory
Template files ditempatkan di `templates/`:
- `{name}_formula.json` - File konfigurasi formula
- `{name}_template.xlsx` - File Excel template

## Usage Workflow

1. **Template Selection**
   - Pilih template dari dropdown
   - Informasi template akan ditampilkan

2. **Parameter Configuration**
   - Set start date dan end date
   - Konfigurasi database connection
   - Template-specific parameters

3. **Data Preview**
   - Klik "Preview Data" untuk ekstrak data
   - Review summary statistics
   - Check sample data rows

4. **Report Generation**
   - Klik "Generate Report**
   - Pilih output format (Excel/PDF)
   - Tunggu proses selesai
   - Report akan disimpan di `reports/` folder

## File Structure

```
Simple_Report_Editor/
├── simple_report_editor.py          # Main GUI application
├── formula_engine.py                # Formula processing engine
├── template_processor.py            # Excel template processor
├── report_generator.py              # Report orchestrator
├── firebird_connector.py            # Database connector
├── config/
│   └── app_config.json              # Application configuration
├── templates/
│   ├── ffb_scannerdata04_formula.json
│   ├── ffb_scannerdata_dynamic_formula.json
│   └── FFB_ScannerData04_Template_20251101_114530.xlsx
├── reports/                         # Generated reports output
└── USAGE.md                         # This file
```

## Troubleshooting

### Common Issues

1. **ISQL Not Found**
   - Pastikan Firebird terinstall dengan ISQL
   - Cek path ISQL di standard location:
     - `C:\Program Files\Firebird\Firebird_2_5\bin\isql.exe`
     - `C:\Program Files\Firebird\Firebird_3_0\bin\isql.exe`

2. **Database Connection Failed**
   - Verify database path
   - Check username dan password
   - Ensure database file accessible

3. **Template Loading Error**
   - Check Excel file format (.xlsx)
   - Verify JSON syntax in formula file
   - Ensure template file exists

4. **No Data in Preview**
   - Check date parameters
   - Verify SQL queries in formula
   - Ensure data exists in database

### Error Handling

- Error messages ditampilkan di GUI
- Detailed logging di `simple_report_editor.log`
- Check log file untuk troubleshooting detail

## Testing

Run test script untuk verify system:

```bash
# Minimal test
python minimal_test.py

# Basic functionality test
python simple_test.py

# Comprehensive test (requires database)
python test_system.py
```

## Advanced Features

### Custom Variables
Support untuk berbagai tipe variables:

```json
{
  "variables": {
    "constant_var": {
      "type": "constant",
      "value": "Fixed Value"
    },
    "calculated_var": {
      "type": "calculation",
      "formula": "summary.total_records * 100"
    },
    "formatted_date": {
      "type": "formatting",
      "source": "TODAY()",
      "format": "dd MMMM yyyy"
    },
    "conditional_var": {
      "type": "conditional",
      "condition": "summary.total_records > 1000",
      "true_value": "High Volume",
      "false_value": "Low Volume"
    }
  }
}
```

### Complex Queries
Support untuk multiple queries dan joins:

```json
{
  "queries": {
    "main_data": {
      "sql": "SELECT a.*, e.EMPNAME FROM {table_name} a LEFT JOIN EMP e ON a.WORKERID = e.EMPID WHERE a.TRANSDATE BETWEEN {start_date} AND {end_date}"
    },
    "summary_stats": {
      "sql": "SELECT COUNT(*) as total, SUM(RIPEBCH) as total_ripe FROM {table_name} WHERE TRANSDATE BETWEEN {start_date} AND {end_date}"
    }
  }
}
```

## Support

For issues and questions:
1. Check this guide for common solutions
2. Review log files for detailed error messages
3. Verify database connectivity and file permissions
4. Ensure all dependencies are properly installed

## License

This project is proprietary software for PT. Rebinmas Jaya internal use.