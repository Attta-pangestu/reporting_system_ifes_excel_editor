# Template Laporan Kinerja Kerani, Mandor, dan Asisten Multi-Estate

## Struktur Template Excel:
- File: `Laporan_Kinerja_Kerani_Mandor_Asisten_Template.xlsx`
- Worksheet: `Laporan Kinerja`

## Layout Excel:

### Header (A1:H1)
- A1: ESTATE
- B1: DIVISI
- C1: KARYAWAN
- D1: ROLE
- E1: JUMLAH TRANSAKSI
- F1: PERSENTASE TERVERIFIKASI
- G1: KETERANGAN PERBEDAAN
- H1: PERIODE LAPORAN

### Data Rows (A2:H100)
- Format data sama dengan report PDF
- Baris SUMMARY untuk setiap divisi
- Baris detail per karyawan (KERANI, MANDOR, ASISTEN)
- Baris GRAND TOTAL di akhir

### Style Formatting:
- Header row: Background biru tua, text putih, bold
- SUMMARY rows: Background biru, text putih, bold
- KERANI rows: Background merah muda
- MANDOR rows: Background hijau muda
- ASISTEN rows: Background biru muda
- Alternating row colors untuk readability

## Variabel yang Diperlukan:
1. **Database Configuration**: Path ke database setiap estate
2. **Date Range**: Start date dan end date
3. **Employee Mapping**: ID ke nama karyawan
4. **Transaction Data**: Data dari tabel FFBSCANNERDATA[MM]
5. **Division Data**: Mapping ID ke nama divisi
6. **Performance Metrics**: Jumlah transaksi, verifikasi, perbedaan