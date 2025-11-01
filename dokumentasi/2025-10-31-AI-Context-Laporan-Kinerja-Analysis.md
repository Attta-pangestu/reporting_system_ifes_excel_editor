---
tags: [AI-Context, Recall, Laporan-Kinerja, Excel-Template, FFB-Scanner]
created: 2025-10-31
project: "Monitoring Database Ifes Auto Report"
topic: "Laporan Kinerja Kerani, Mandor, dan Asisten Multi-Estate"
---

# AI Context: Analisis Laporan Kinerja Kerani, Mandor, dan Asisten Multi-Estate

## Ringkasan Proyek
Analisis sistem laporan kinerja karyawan (Kerani, Mandor, Asisten) berdasarkan transaksi FFB Scanner dari multiple estate. Sistem ini menghasilkan laporan PDF dengan analisis real-time terhadap akurasi input data transaksi.

## Struktur Codebase
- **File Utama**: `referensi/gui_multi_estate_ffb_analysis.py`
- **Database Connector**: `firebird_connector.py`
- **Template Generator**: `excel_template_generator.py`
- **Formula Definition**: `laporan_kinerja_formula.json`

## Arsitektur Sistem

### Komponen Utama
1. **GUI Application** (`gui_multi_estate_ffb_analysis.py`)
   - Multi-estate analysis interface
   - Configurable database paths
   - Date range selection
   - Progress tracking
   - PDF report generation

2. **Database Layer** (`firebird_connector.py`)
   - Firebird database connection
   - Query execution with isql
   - Data parsing to pandas DataFrame
   - Connection testing

3. **Report Generation**
   - PDF landscape format
   - Professional styling
   - Multi-estate aggregation
   - Performance metrics calculation

## Data Flow

### Source Data
- **Primary Tables**: `FFBSCANNERDATA[MM]` (Jan-Dec)
- **Reference Tables**: `EMP`, `OCFIELD`, `CRDIVISION`
- **Transaction Fields**: RIPEBCH, UNRIPEBCH, BLACKBCH, ROTTENBCH, LONGSTALKBCH, RATDMGBCH, LOOSEFRUIT

### Key Variables
```python
# Employee mapping
employee_mapping = {
    "ID": "NAME"  # dari tabel EMP
}

# Division mapping
divisions = {
    "DIVID": "DIVNAME"  # dari OCFIELD + CRDIVISION
}

# Transaction analysis
transaction_data = {
    "SCANUSERID": "employee_id",
    "RECORDTAG": "PM|P1|P5",  # Kerani|Mandor|Asisten
    "TRANSNO": "transaction_number",
    "TRANSSTATUS": "status_code"
}
```

## Logika Perhitungan

### 1. Transaksi Kerani
- **Total**: `COUNT(*) WHERE RECORDTAG = 'PM'`
- **Verified**: Transaksi dengan duplikat TRANSNO
- **Differences**: Perbedaan field antara kerani dan mandor/asisten

### 2. Transaksi Mandor
- **Total**: `COUNT(*) WHERE RECORDTAG = 'P1'`
- **Percentage**: `(mandor_total / kerani_total) * 100`

### 3. Transaksi Asisten
- **Total**: `COUNT(*) WHERE RECORDTAG = 'P5'`
- **Percentage**: `(asisten_total / kerani_total) * 100`

### 4. Verification Rate
- **Formula**: `(verified_transactions / total_transactions) * 100`
- **Scope**: Per karyawan, per divisi, dan grand total

### 5. Field Differences
```python
fields_to_compare = [
    'RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH',
    'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT'
]

# Count as 1 transaction difference if ANY field differs
has_difference = any(kerani_val != other_val for field in fields_to_compare)
```

## Filter Khusus

### Status 704 Filter (Mei 2025)
- **Trigger**: Bulan Mei dalam rentang tanggal
- **Logic**: Gunakan `TRANSSTATUS = '704'` untuk Mandor/Asisten saat menghitung perbedaan
- **Purpose**: Meningkatkan akurasi analisis perbedaan

## Output Formats

### 1. PDF Report (Original System)
- Landscape A4 format
- Professional corporate styling
- Multi-estate aggregation
- Color-coded rows
- Detailed explanations

### 2. Excel Template (Generated)
- File: `Laporan_Kinerja_Kerani_Mandor_Asisten_Template.xlsx`
- Structure: 8 columns (ESTATE, DIVISI, KARYAWAN, ROLE, JUMLAH TRANSAKSI, PERSENTASE TERVERIFIKASI, KETERANGAN PERBEDAAN, PERIODE LAPORAN)
- Styling: Color-coded by role type
- Sample data included

### 3. JSON Formula (Generated)
- File: `laporan_kinerja_formula.json`
- Complete variable definitions
- Calculation formulas
- Data source mappings
- Validation rules

## Styling Guidelines

### Color Scheme
- **Header**: `#2C5282` (Deep blue)
- **Summary Rows**: `#4299E1` (Professional blue)
- **Kerani Rows**: `#FFF5F5` (Light red) + `#E53E3E` (Text)
- **Mandor Rows**: `#F0FFF4` (Light green) + `#38A169` (Text)
- **Asisten Rows**: `#F0F9FF` (Light blue) + `#3182CE` (Text)

### Typography
- **Headers**: Arial 10pt Bold
- **Summary**: Arial 9pt Bold
- **Data**: Arial 8pt
- **Special**: Bold for differences and percentages

## Configuration Management

### Config Structure (`config.json`)
```json
{
    "PGE 1A": "path/to/database/PTRJ_P1A.FDB",
    "PGE 1B": "path/to/database/PTRJ_P1B.FDB",
    // ... other estates
}
```

### Estate List (Default)
- PGE 1A, PGE 1B, PGE 2A, PGE 2B
- IJL, DME
- Are B2, Are B1, Are A, Are C

## Performance Metrics

### KPI Definitions
1. **Verification Rate**: % transaksi kerani yang terverifikasi
2. **Difference Rate**: % transaksi dengan perbedaan input
3. **Transaction Volume**: Jumlah transaksi per role
4. **Data Accuracy**: 100% - difference rate

### Calculation Examples
```python
# Example: Kerani Performance
kerani_verification_rate = (405 / 450) * 100 = 90.00%
difference_rate = (15 / 405) * 100 = 3.7%

# Example: Mandor Contribution
mandor_percentage = (280 / 1500) * 100 = 18.67%
```

## Implementation Notes

### Error Handling
- Database connection validation
- File path verification
- Query error recovery
- Progress tracking with try-catch

### Optimization Strategies
- Month-based table partitioning
- Bulk query processing
- Memory-efficient data handling
- Parallel estate processing

### Security Considerations
- Database credential management
- Path validation
- Input sanitization
- Access control through config

## Future Enhancements

### Potential Improvements
1. **Real-time Dashboard**: Web-based monitoring
2. **Mobile App**: Field data validation
3. **Advanced Analytics**: Trend analysis and forecasting
4. **Integration**: ERP system connectivity
5. **Automation**: Scheduled report generation

### Scalability Considerations
- Database indexing optimization
- Caching layer implementation
- Distributed processing capabilities
- Cloud migration pathway

## Dependencies

### Python Libraries
- `tkinter` - GUI framework
- `pandas` - Data manipulation
- `reportlab` - PDF generation
- `openpyxl` - Excel file handling
- `tkcalendar` - Date picker

### External Dependencies
- Firebird Database Server
- ISQL command-line tool
- Windows OS (for path handling)

## Troubleshooting Guide

### Common Issues
1. **Database Connection**: Verify ISQL path and credentials
2. **File Paths**: Use absolute paths for config
3. **Memory Usage**: Process estates sequentially
4. **Date Format**: Use consistent date formatting

### Debug Strategies
- Enable verbose logging
- Check SQL query syntax
- Validate data types
- Monitor resource usage

## Conclusion

Sistem ini menyediakan analisis komprehensif untuk kinerja karyawan berdasarkan transaksi FFB Scanner. Dengan template Excel dan formula JSON yang telah dibuat, proses reporting dapat diotomasi dan distandarkan. Sistem dirancang untuk scalable multi-estate deployment dengan maintenance yang minimal.

---

**Generated by**: Claude AI Assistant
**Date**: 2025-10-31
**Context**: Analysis of Multi-Estate FFB Scanner Performance Reporting System
**Related Files**: [[gui_multi_estate_ffb_analysis.py]], [[firebird_connector.py]], [[laporan_kinerja_formula.json]]