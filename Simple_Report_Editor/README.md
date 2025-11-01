# Simple Report Editor

Aplikasi generator laporan berbasis template Excel dengan dukungan database Firebird dan export PDF.

## Fitur

- **Template Engine**: Gunakan file Excel sebagai template dengan placeholder variables
- **Database Connector**: Koneksi ke berbagai database Firebird
- **Formula Processing**: Definisikan query SQL dan perhitungan dalam file JSON
- **Preview Data**: Pratinjau data sebelum generate laporan
- **PDF Export**: Generate laporan dalam format PDF
- **GUI Interface**: Interface yang user-friendly untuk kemudahan penggunaan

## Struktur Proyek

```
Simple_Report_Editor/
├── core/                   # Core modules
│   ├── __init__.py
│   ├── database_connector.py
│   ├── template_processor.py
│   ├── formula_engine.py
│   └── report_generator.py
├── gui/                    # GUI modules
│   ├── __init__.py
│   ├── main_window.py
│   ├── database_selector.py
│   ├── template_selector.py
│   ├── data_preview.py
│   └── report_generator_ui.py
├── templates/              # Template files
│   ├── *.xlsx
│   └── *.json
├── config/                 # Configuration files
│   ├── app_config.json
│   └── database_configs.json
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── file_utils.py
│   ├── date_utils.py
│   └── pdf_generator.py
├── docs/                   # Documentation
│   ├── user_guide.md
│   ├── developer_guide.md
│   └── api_reference.md
├── tests/                  # Test modules
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_template.py
│   └── test_formula.py
├── debug/                  # Debug utilities
│   ├── database_checker.py
│   ├── template_validator.py
│   └── query_analyzer.py
├── main_app.py            # Main application entry point
└── requirements.txt        # Python dependencies
```

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python main_app.py
   ```

3. **Basic usage**:
   - Pilih database file (.fdb)
   - Pilih template Excel dan formula JSON
   - Atur parameter filter
   - Preview data
   - Generate report (Excel/PDF)

## Database Support

- Firebird Database (.fdb files)
- Default database: PGE 2B
- Support multiple database switching
- Auto-detect ISQL installation

## Template Format

Gunakan format `{{variable_name}}` di Excel template:
- `{{estate_name}}` - Nama estate
- `{{report_date}}` - Tanggal laporan
- `{{data_records.0.FIELD_NAME}}` - Data dari query
- `{{summary.total_records}}` - Ringkasan data

## Formula Configuration

Format JSON untuk mendefinisikan query dan variables:
```json
{
  "queries": {
    "main_data": {
      "type": "sql",
      "sql": "SELECT * FROM TABLE_NAME",
      "return_format": "dict"
    }
  },
  "variables": {
    "report_title": {
      "type": "constant",
      "value": "My Report"
    }
  }
}
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Database Debugging
```bash
python debug/database_checker.py
```

### Template Validation
```bash
python debug/template_validator.py
```

## Dependencies

- `openpyxl` - Excel file manipulation
- `tkinter` - GUI framework (built-in)
- `pandas` - Data processing
- `reportlab` - PDF generation
- `tkcalendar` - Date picker widgets

## Kontribusi

1. Fork proyek
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Buat Pull Request

## License

MIT License

## Support

Untuk bantuan dan pertanyaan, hubungi development team atau lihat dokumentasi di folder `docs/`.