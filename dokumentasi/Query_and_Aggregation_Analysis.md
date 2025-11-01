# Detail Query dan Proses Agregasi Data
## Sistem Laporan Kinerja Kerani, Mandor, dan Asisten Multi-Estate

## 1. DATABASE SCHEMA DAN STRUKTUR TABEL

### Primary Tables
```sql
-- FFBSCANNERDATA[MM] - Main transaction tables (Jan-Dec)
CREATE TABLE FFBSCANNERDATA01 (
    ID VARCHAR(50) PRIMARY KEY,
    SCANUSERID VARCHAR(50),      -- Employee ID yang melakukan scan
    OCID VARCHAR(50),            -- Operation Center ID
    WORKERID VARCHAR(50),        -- ID pekerja
    CARRIERID VARCHAR(50),       -- ID pengangkut
    FIELDID VARCHAR(50),         -- ID blok/field
    TASKNO VARCHAR(50),          -- Nomor task
    RIPEBCH DECIMAL(10,2),       -- Janjang matang
    UNRIPEBCH DECIMAL(10,2),     -- Janjang mentah
    BLACKBCH DECIMAL(10,2),      -- Janjang busuk
    ROTTENBCH DECIMAL(10,2),     -- Janjang rusak
    LONGSTALKBCH DECIMAL(10,2),  -- Janjang tangkai panjang
    RATDMGBCH DECIMAL(10,2),     -- Janjang rusak tikus
    LOOSEFRUIT DECIMAL(10,2),    -- Brondolan
    TRANSNO VARCHAR(50),         -- Nomor transaksi (UNIK KEY untuk verifikasi)
    TRANSDATE DATE,              -- Tanggal transaksi
    TRANSTIME TIME,              -- Waktu transaksi
    UPLOADDATETIME TIMESTAMP,    -- Waktu upload
    RECORDTAG VARCHAR(10),       -- TAG: PM (Kerani), P1 (Mandor), P5 (Asisten)
    TRANSSTATUS VARCHAR(10),     -- Status transaksi (704, 731, 732, etc.)
    TRANSTYPE VARCHAR(10),       -- Tipe transaksi
    LASTUSER VARCHAR(50),        -- User terakhir yang update
    LASTUPDATED TIMESTAMP,       -- Waktu terakhir update
    OVERRIPEBCH DECIMAL(10,2),   -- Janjang terlalu matang
    UNDERRIPEBCH DECIMAL(10,2),  -- Janjang kurang matang
    ABNORMALBCH DECIMAL(10,2),   -- Janjang abnormal
    LOOSEFRUIT2 DECIMAL(10,2)    -- Brondolan tipe 2
);

-- Reference Tables
CREATE TABLE EMP (
    ID VARCHAR(50) PRIMARY KEY,
    NAME VARCHAR(100)            -- Nama karyawan
);

CREATE TABLE OCFIELD (
    ID VARCHAR(50) PRIMARY KEY,
    DIVID VARCHAR(50)            -- ID divisi
);

CREATE TABLE CRDIVISION (
    ID VARCHAR(50) PRIMARY KEY,
    DIVNAME VARCHAR(100)         -- Nama divisi
);
```

## 2. QUERY DETAIL YANG DIGUNAKAN

### 2.1 Employee Mapping Query
```sql
-- Lokasi: get_employee_mapping() method
-- Purpose: Mapping ID employee ke nama lengkap
SELECT ID, NAME
FROM EMP;

-- Hasil: Dictionary format
{
    "12345": "AHMAD RIZKI",
    "67890": "BUDI SANTOSO",
    "11111": "CHANDRA KUSUMA"
}
```

### 2.2 Division Discovery Query
```sql
-- Lokasi: get_divisions() method
-- Purpose: Mendapatkan semua divisi aktif dalam periode
SELECT DISTINCT
    b.DIVID,
    c.DIVNAME
FROM FFBSCANNERDATA{MM} a
JOIN OCFIELD b ON a.FIELDID = b.ID
LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
WHERE b.DIVID IS NOT NULL
  AND c.DIVNAME IS NOT NULL;

-- {MM} diganti dengan bulan yang ada dalam rentang tanggal
-- Contoh: FFBSCANNERDATA04 untuk April, FFBSCANNERDATA05 untuk Mei

-- Hasil: Dictionary format
{
    "001": "DIVISI 1",
    "002": "DIVISI 2",
    "003": "DIVISI 3"
}
```

### 2.3 Main Transaction Data Query
```sql
-- Lokasi: analyze_division() method
-- Purpose: Mengambil semua data transaksi per divisi dalam periode tertentu
SELECT
    a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID,
    a.FIELDID, a.TASKNO, a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH,
    a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH, a.LOOSEFRUIT,
    a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
    a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER,
    a.LASTUPDATED, a.OVERRIPEBCH, a.UNDERRIPEBCH,
    a.ABNORMALBCH, a.LOOSEFRUIT2
FROM FFBSCANNERDATA{MM} a
JOIN OCFIELD b ON a.FIELDID = b.ID
WHERE b.DIVID = '{div_id}'
  AND a.TRANSDATE >= '{start_date}'
  AND a.TRANSDATE <= '{end_date}';

-- Parameters:
-- {MM}: Bulan tabel (01-12)
-- {div_id}: ID divisi yang dianalisis
-- {start_date}: Tanggal mulai periode
-- {end_date}: Tanggal akhir periode
```

## 3. PROSES DATA PROCESSING LANGSUNG DARI CODE

### 3.1 Data Collection Phase
```python
# Lokasi: analyze_division() method, lines 423-452
# Process: Menggabungkan data dari semua tabel bulanan
all_data_df = pd.DataFrame()

for ffb_table in month_tables:  # FFBSCANNERDATA01-12
    query = f"""
    SELECT a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID,
           a.FIELDID, a.TASKNO, a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH,
           a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH, a.LOOSEFRUIT,
           a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
           a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER,
           a.LASTUPDATED, a.OVERRIPEBCH, a.UNDERRIPEBCH,
           a.ABNORMALBCH, a.LOOSEFRUIT2
    FROM {ffb_table} a
    JOIN OCFIELD b ON a.FIELDID = b.ID
    WHERE b.DIVID = '{div_id}'
        AND a.TRANSDATE >= '{start_str}'
        AND a.TRANSDATE <= '{end_str}'
    """

    result = connector.execute_query(query)
    df_monthly = connector.to_pandas(result)
    if not df_monthly.empty:
        all_data_df = pd.concat([all_data_df, df_monthly], ignore_index=True)

# Remove duplicates
df.drop_duplicates(subset=['ID'], inplace=True)
```

### 3.2 Duplicate Detection Algorithm
```python
# Lokasi: analyze_division() method, lines 459-461
# Process: Mendeteksi transaksi yang diverifikasi (memiliki duplikat TRANSNO)
duplicated_rows = df[df.duplicated(subset=['TRANSNO'], keep=False)]
verified_transnos = set(duplicated_rows['TRANSNO'].tolist())

# Logic:
# 1. Cari baris dengan TRANSNO yang sama
# 2. Jika ada duplikat, transaksi dianggap "terverifikasi"
# 3. Semua TRANSNO duplikat dimasukkan ke verified_transnos set
```

### 3.3 Employee Data Structure Initialization
```python
# Lokasi: analyze_division() method, lines 465-476
# Process: Inisialisasi struktur data untuk setiap employee
employee_details = {}

# Inisialisasi struktur detail karyawan
all_user_ids = df['SCANUSERID'].unique()
for user_id in all_user_ids:
    user_id_str = str(user_id).strip()
    employee_details[user_id_str] = {
        'name': employee_mapping.get(user_id_str, f"EMP-{user_id_str}"),
        'kerani': 0,
        'kerani_verified': 0,     # Tambahan untuk verifikasi per kerani
        'kerani_differences': 0,  # Tambahan untuk jumlah perbedaan input
        'mandor': 0,
        'asisten': 0
    }
```

### 3.4 Kerani Data Processing
```python
# Lokasi: analyze_division() method, lines 478-541
# Process: Menghitung metrik untuk Kerani (RECORDTAG = 'PM')
kerani_df = df[df['RECORDTAG'] == 'PM']
if not kerani_df.empty:
    for user_id, group in kerani_df.groupby('SCANUSERID'):
        user_id_str = str(user_id).strip()
        total_created = len(group)

        # Hitung jumlah perbedaan input untuk transaksi yang terverifikasi
        differences_count = 0
        for _, kerani_row in group.iterrows():
            if kerani_row['TRANSNO'] in verified_transnos:
                # Cari transaksi dengan TRANSNO yang sama tapi RECORDTAG berbeda
                matching_transactions = df[(df['TRANSNO'] == kerani_row['TRANSNO']) &
                                          (df['RECORDTAG'] != 'PM')]

                # FILTER KHUSUS: Untuk bulan Mei, hanya hitung perbedaan jika
                # Mandor/Asisten memiliki TRANSSTATUS = 704
                if use_status_704_filter:
                    matching_transactions = matching_transactions[
                        matching_transactions['TRANSSTATUS'] == '704']

                if not matching_transactions.empty:
                    # Prioritaskan P1 (Asisten) jika ada, jika tidak gunakan P5 (Mandor)
                    p1_records = matching_transactions[matching_transactions['RECORDTAG'] == 'P1']
                    p5_records = matching_transactions[matching_transactions['RECORDTAG'] == 'P5']

                    if not p1_records.empty:
                        other_row = p1_records.iloc[0]
                    elif not p5_records.empty:
                        other_row = p5_records.iloc[0]
                    else:
                        continue

                    # Hitung perbedaan untuk setiap field
                    fields_to_compare = [
                        'RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH',
                        'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT'
                    ]

                    # Count as 1 transaction difference if ANY field differs
                    has_difference = False
                    for field in fields_to_compare:
                        try:
                            kerani_val = float(kerani_row[field]) if kerani_row[field] else 0
                            other_val = float(other_row[field]) if other_row[field] else 0
                            if kerani_val != other_val:
                                has_difference = True
                                break  # Exit loop once we find any difference
                        except (ValueError, TypeError):
                            continue

                    # Count as 1 transaction difference if any field differs
                    if has_difference:
                        differences_count += 1

        # Hitung persentase terverifikasi
        verified_count = len(group[group['TRANSNO'].isin(verified_transnos)])
        percentage = (verified_count / total_created * 100) if total_created > 0 else 0

        if user_id_str in employee_details:
            employee_details[user_id_str]['kerani'] = total_created
            employee_details[user_id_str]['kerani_verified'] = verified_count
            employee_details[user_id_str]['kerani_differences'] = differences_count
```

### 3.5 Mandor and Asisten Data Processing
```python
# Lokasi: analyze_division() method, lines 542-558
# Process: Menghitung metrik untuk Mandor (RECORDTAG = 'P1')
mandor_df = df[df['RECORDTAG'] == 'P1']
if not mandor_df.empty:
    mandor_counts = mandor_df.groupby('SCANUSERID').size()
    for user_id, count in mandor_counts.items():
        user_id_str = str(user_id).strip()
        if user_id_str in employee_details:
            employee_details[user_id_str]['mandor'] = count

# Process: Menghitung metrik untuk Asisten (RECORDTAG = 'P5')
asisten_df = df[df['RECORDTAG'] == 'P5']
if not asisten_df.empty:
    asisten_counts = asisten_df.groupby('SCANUSERID').size()
    for user_id, count in asisten_counts.items():
        user_id_str = str(user_id).strip()
        if user_id_str in employee_details:
            employee_details[user_id_str]['asisten'] = count
```

## 4. PROSES AGREGASI DATA

### 4.1 Division Level Aggregation
```python
# Lokasi: analyze_division() method, lines 560-592
# Process: Menghitung total per divisi
kerani_total = sum(d['kerani'] for d in employee_details.values())
mandor_total = sum(d['mandor'] for d in employee_details.values())
asisten_total = sum(d['asisten'] for d in employee_details.values())

# Verifikasi keseluruhan berdasarkan logika duplikat
div_kerani_verified_total = sum(d['kerani_verified'] for d in employee_details.values())
verification_rate = (div_kerani_verified_total / kerani_total * 100) if kerani_total > 0 else 0

return {
    'estate': estate_name,
    'division': div_name,
    'kerani_total': kerani_total,
    'mandor_total': mandor_total,
    'asisten_total': asisten_total,
    'verifikasi_total': div_kerani_verified_total,
    'verification_rate': verification_rate,
    'employee_details': employee_details
}
```

### 4.2 Estate Level Aggregation
```python
# Lokasi: analyze_estate() method, lines 317-358
# Process: Akumulasi per karyawan dari semua divisi dalam satu estate
estate_employee_totals = {}

for div_id, div_name in divisions.items():
    result = self.analyze_division(connector, estate_name, div_id, div_name,
                                 start_date, end_date, employee_mapping,
                                 use_status_704_filter, month_tables)

    if result:
        # Akumulasi per karyawan
        for emp_id, emp_data in result['employee_details'].items():
            if emp_id not in estate_employee_totals:
                estate_employee_totals[emp_id] = {
                    'name': emp_data['name'],
                    'kerani': 0,
                    'kerani_verified': 0,
                    'kerani_differences': 0,
                    'mandor': 0,
                    'asisten': 0
                }

            estate_employee_totals[emp_id]['kerani'] += emp_data['kerani']
            estate_employee_totals[emp_id]['kerani_verified'] += emp_data['kerani_verified']
            estate_employee_totals[emp_id]['kerani_differences'] += emp_data['kerani_differences']
            estate_employee_totals[emp_id]['mandor'] += emp_data['mandor']
            estate_employee_totals[emp_id]['asisten'] += emp_data['asisten']
```

### 4.3 Grand Total Calculation
```python
# Lokasi: create_pdf_report() method, lines 821-845
# Process: Menghitung grand total dari semua estate
grand_kerani = 0
grand_mandor = 0
grand_asisten = 0
grand_kerani_verified = 0

for result in all_results:
    grand_kerani += result['kerani_total']
    grand_mandor += result['mandor_total']
    grand_asisten += result['asisten_total']
    grand_kerani_verified += result['verifikasi_total']

grand_total_kerani_only = grand_kerani
grand_total_verified_kerani = grand_kerani_verified
grand_verification_rate = (grand_total_verified_kerani / grand_total_kerani_only * 100) if grand_total_kerani_only > 0 else 0
```

## 5. SPECIAL FILTER LOGIC

### 5.1 Status 704 Filter (May 2025 Special Case)
```python
# Lokasi: analyze_estate() method, lines 310-316
# Logic: Filter khusus untuk bulan Mei 2025
month_num = start_date.month
use_status_704_filter = (start_date.month == 5 or end_date.month == 5)

# Implementation in field comparison:
if use_status_704_filter:
    # Filter hanya transaksi Mandor/Asisten dengan TRANSSTATUS 704
    matching_transactions = matching_transactions[matching_transactions['TRANSSTATUS'] == '704']
```

### 5.2 Field Comparison Logic
```python
# Lokasi: analyze_division() method, lines 512-531
# Fields yang dibandingkan untuk mendeteksi perbedaan
fields_to_compare = [
    'RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH',
    'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT'
]

# Logic: Hitung sebagai 1 transaksi berbeda jika ADA SATU PUN field yang berbeda
has_difference = False
for field in fields_to_compare:
    kerani_val = float(kerani_row[field]) if kerani_row[field] else 0
    other_val = float(other_row[field]) if other_row[field] else 0
    if kerani_val != other_val:
        has_difference = True
        break  # Exit loop once we find any difference
```

## 6. DATA FLOW SUMMARY

### Complete Data Flow:
1. **Input**: Date range + Estate selection + Database paths
2. **Query**: Extract data from FFBSCANNERDATA[MM] tables
3. **Filter**: Apply date range and division filters
4. **Deduplication**: Remove duplicate IDs
5. **Verification**: Identify verified transactions via TRANSNO duplicates
6. **Categorization**: Group by RECORDTAG (PM/P1/P5)
7. **Comparison**: Compare fields between Kerani and Mandor/Asisten
8. **Aggregation**: Calculate metrics per employee, division, estate
9. **Report**: Generate PDF with professional formatting

### Key Metrics Calculation:
- **Kerani Verification Rate** = (kerani_verified / kerani_total) × 100
- **Mandor Contribution Rate** = (mandor_total / kerani_total) × 100
- **Asisten Contribution Rate** = (asisten_total / kerani_total) × 100
- **Difference Rate** = (kerani_differences / kerani_verified) × 100

### Output Structure:
- Division Summary Rows (blue background)
- Employee Detail Rows grouped by role (color-coded)
- Grand Total Row (dark blue background)
- Explanation section with methodology