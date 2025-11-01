# User Guide - Simple Report Editor

## Overview

Simple Report Editor adalah aplikasi berbasis GUI untuk menghasilkan laporan dari database Firebird menggunakan template Excel dan formula JSON. Aplikasi ini dirancang khusus untuk laporan FFB (Fresh Fruit Bunch) namun dapat digunakan untuk berbagai jenis laporan lainnya.

## Fitur Utama

- **Template Engine**: Gunakan file Excel sebagai template dengan placeholder variables
- **Database Connector**: Koneksi ke database Firebird (.fdb)
- **Formula Processing**: Definisikan query SQL dan perhitungan dalam file JSON
- **Preview Data**: Pratinjau data sebelum generate laporan
- **Multiple Output**: Generate laporan dalam format Excel dan PDF
- **User-Friendly GUI**: Interface yang mudah digunakan

## Persyaratan Sistem

### Software Requirements
- Python 3.7 atau lebih tinggi
- Windows OS (karena ketergantungan pada Excel COM object)
- Microsoft Excel (untuk PDF export)

### Python Dependencies
Install dependencies dengan command:
```bash
pip install -r requirements.txt
```

Dependencies yang dibutuhkan:
- `openpyxl` - Manipulasi file Excel
- `tkinter` - GUI framework (built-in dengan Python)
- `pandas` - Processing data
- `reportlab` - PDF generation
- `tkcalendar` - Date picker widgets
- `Pillow` - Image processing
- `psutil` - System utilities
- `pywin32` - Windows COM interface (untuk PDF export)

## Instalasi

1. **Download atau clone proyek**:
   ```bash
   git clone <repository-url>
   cd Simple_Report_Editor
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan aplikasi**:
   ```bash
   python main_app.py
   ```

## Panduan Penggunaan

### 1. Memulai Aplikasi

Jalankan `main_app.py` untuk memulai aplikasi. Akan muncul jendela utama dengan beberapa section:

- **Database Configuration**: Pilih dan test koneksi database
- **Template Configuration**: Pilih Excel template dan formula JSON
- **Report Parameters**: Atur parameter filter untuk query
- **Action Buttons**: Tombol untuk preview dan generate laporan

### 2. Konfigurasi Database

1. **Pilih Database File**:
   - Klik tombol "Browse" untuk memilih file database (.fdb)
   - Atau gunakan path default yang sudah disediakan

2. **Test Koneksi**:
   - Klik tombol "Test Connection" untuk memverifikasi koneksi
   - Status akan muncul sebagai "Connected" (hijau) jika berhasil

### 3. Konfigurasi Template

1. **Pilih Excel Template**:
   - Klik "Browse" untuk memilih file Excel template (.xlsx)
   - Template harus menggunakan format `{{variable_name}}` untuk placeholder

2. **Pilih Formula JSON**:
   - Klik "Browse" untuk memilih file formula JSON
   - File JSON mendefinisikan query dan variables untuk laporan

3. **Load Sample**:
   - Klik "Load Sample" untuk menggunakan template contoh

### 4. Parameter Laporan

Atur parameter untuk filter data:

- **Start Date / End Date**: Filter berdasarkan rentang tanggal
- **Field ID**: Filter berdasarkan field/lokasi
- **Worker ID**: Filter berdasarkan ID pekerja
- **Record Tag**: Filter berdasarkan tipe record (PM=PMA, P1=Mandor, P5=Asisten)
- **Output Directory**: Direktori untuk menyimpan laporan

### 5. Preview Data

1. Klik tombol "Preview Data" untuk melihat data sebelum generate laporan
2. Akan muncul jendela preview dengan:
   - Dropdown untuk memilih query yang ingin dilihat
   - Tabel data yang bisa di-scroll
   - Tombol "Export to CSV" untuk export data
   - Tombol "Refresh" untuk refresh data

### 6. Generate Laporan

#### Generate Excel Report
1. Klik tombol "Generate Excel Report"
2. Atur parameter di dialog yang muncul
3. Pilih lokasi dan nama file
4. Klik "Generate Report"
5. File Excel akan di-generate dan otomatis dibuka (jika dicentang)

#### Generate PDF Report
1. Klik tombol "Generate PDF Report"
2. Atur parameter di dialog yang muncul
3. Pilih lokasi dan nama file PDF
4. Klik "Generate Report"
5. File PDF akan di-generate dari Excel template

## Format Template

### Excel Template Format

Gunakan format `{{variable_name}}` di Excel template:

#### Contoh Placeholder:
- `{{estate_name}}` - Nama estate/perkebunan
- `{{report_date}}` - Tanggal laporan
- `{{report_period}}` - Periode laporan
- `{{database_name}}` - Nama database
- `{{generated_by}}` - User yang generate
- `{{generation_time}}` - Waktu generate

#### Data Records:
- `{{data_records.0.FIELD_NAME}}` - Data dari query (baris pertama)
- `{{data_records.1.FIELD_NAME}}` - Data dari query (baris kedua)
- Sistem akan otomatis mengisi semua rows untuk repeating sections

#### Summary Variables:
- `{{summary.total_records}}` - Total records
- `{{summary.total_ripe_bunch}}` - Total ripe bunch
- `{{summary.date_range}}` - Rentang tanggal

### Formula JSON Format

Struktur dasar file formula JSON:

```json
{
  "template_info": {
    "name": "Nama Template",
    "description": "Deskripsi template",
    "version": "1.0"
  },
  "database_config": {
    "connection_string": "path/to/database.fdb",
    "username": "SYSDBA",
    "password": "masterkey"
  },
  "parameters": {
    "start_date": {
      "type": "date",
      "description": "Tanggal mulai filter",
      "required": false
    }
  },
  "queries": {
    "main_data": {
      "type": "sql",
      "sql": "SELECT * FROM TABLE_NAME WHERE ...",
      "return_format": "dict"
    },
    "summary_stats": {
      "type": "sql",
      "sql": "SELECT COUNT(*) as total FROM TABLE_NAME",
      "return_format": "dict"
    }
  },
  "variables": {
    "report_title": {
      "type": "constant",
      "value": "Laporan Harian"
    },
    "current_date": {
      "type": "formatting",
      "source": "TODAY()",
      "format": "dd MMMM yyyy"
    }
  },
  "repeating_sections": {
    "Sheet1": {
      "data_section": {
        "data_source": "main_data",
        "start_row": 10,
        "columns": {
          "A": "FIELD1",
          "B": "FIELD2"
        }
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Pastikan file database (.fdb) ada dan accessible
   - Pastikan Firebird server berjalan
   - Cek path ISQL.exe sudah benar

2. **Template Loading Failed**:
   - Pastikan file Excel template ada dan tidak corrupt
   - Pastikan file tidak sedang dibuka di Excel
   - Cek format placeholder `{{variable_name}}` sudah benar

3. **Formula Loading Failed**:
   - Pastikan file JSON valid (bisa dicek di JSON validator)
   - Cek syntax SQL sudah benar
   - Pastikan semua required sections ada

4. **PDF Generation Failed**:
   - Pastikan Microsoft Excel terinstall
   - Pastikan file Excel tidak sedang dibuka
   - Cek permission untuk write ke output directory

5. **No Data Found**:
   - Cek parameter filter (tanggal, field ID, dll)
   - Pastikan query menghasilkan data
   - Gunakan Preview Data untuk verifikasi

### Log Files

Aplikasi membuat log file:
- `simple_report_editor.log` - Log utama aplikasi
- `ffb_scannerdata04_report.log` - Log khusus FFB report

### Debug Mode

Untuk mengaktifkan debug mode:
1. Edit file `config/app_config.json`
2. Set `"enable_debug_mode": true`
3. Restart aplikasi

## Tips and Best Practices

1. **Template Design**:
   - Gunakan formatting Excel yang konsisten
   - Pisahkan section header, data, dan summary
   - Gunakan freeze panes untuk kemudahan navigasi

2. **Query Optimization**:
   - Gunakan parameter filtering yang efisien
   - Batasi jumlah records dengan LIMIT jika perlu
   - Gunakan index pada tabel database

3. **File Management**:
   - Simpan template dan formula di folder yang terorganisir
   - Gunakan naming convention yang konsisten
   - Backup template dan formula secara rutin

4. **Performance**:
   - Untuk dataset besar, gunakan preview dengan limit
   - Generate PDF bisa memakan waktu lebih lama
   - Close aplikasi Excel lain saat generate PDF

## Support

Untuk bantuan lebih lanjut:
1. Lihat file log untuk error detail
2. Cek dokumentasi di folder `docs/`
3. Run debug tools di folder `debug/`
4. Hubungi development team

## Appendix

### Keyboard Shortcuts
- `Ctrl+O` - Open file (dalam file dialog)
- `Ctrl+S` - Save (dalam save dialog)
- `F5` - Refresh data (dalam preview window)
- `Escape` - Close dialog

### File Extensions
- `.xlsx` - Excel template files
- `.json` - Formula configuration files
- `.log` - Log files
- `.pdf` - Generated PDF reports
- `.csv` - Exported data files