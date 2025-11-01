# AI Context - FFB Scanner Data 04 Template Analysis

**Date**: 2025-11-01
**Topic**: Excel Template Structure Analysis
**Tags**: #AI-Context #Recall #Excel-Template #FFB-Scanner

## Template Overview

File: `D:\Gawean Rebinmas\Monitoring Database\Ifes Auto report\excel_method\Simple_Report_Editor\templates\FFB_ScannerData04_Template_20251101_114530.xlsx`

## Template Structure Analysis

### 1. Sheet Information
- **Sheet Name**: FFB Scanner Data 04
- **Dimensions**: 32 rows × 27 columns
- **Purpose**: Laporan transaksi FFB dari tabel FFBSCANNERDATA{MM}

### 2. Layout Structure

#### Header Section (Rows 1-9)
- **Row 1**: Judul "LAPORAN FFB SCANNER DATA 04" (merged cells A1:V1)
- **Row 3-8**: Informasi laporan dengan placeholders:
  - B3: `{{estate_name}}`
  - B4: `{{report_period}}`
  - B5: `{{report_date}}`
  - B6: `{{database_name}}`
  - B7: `{{generated_by}}`
  - B8: `{{generation_time}}`

#### Data Section (Rows 10-21)
- **Row 10**: "DATA TRANSAKSI FFB" (merged cells A10:V10)
- **Row 11**: Table headers (21 columns)
- **Row 12**: Template row dengan placeholders data (repeating section)
- **Rows 13-21**: Empty space untuk dynamic data expansion

#### Summary Section (Rows 22-29)
Summary placeholders:
- B22: `{{summary.total_records}}`
- F22: `{{summary.total_ripe_bunch}}`
- B23: `{{summary.total_unripe_bunch}}`
- F23: `{{summary.total_black_bunch}}`
- B24: `{{summary.total_rotten_bunch}}`
- F24: `{{summary.total_long_stalk_bunch}}`
- B25: `{{summary.total_rat_damage_bunch}}`
- F25: `{{summary.total_loose_fruit}}`
- B26: `{{summary.total_loose_fruit_2}}`
- F26: `{{summary.total_underripe_bunch}}`
- B27: `{{summary.total_overripe_bunch}}`
- F27: `{{summary.total_abnormal_bunch}}`
- B28: `{{summary.date_range}}`
- F28: `{{summary.unique_workers}}`
- B29: `{{summary.unique_fields}}`

#### Footer Section (Rows 30-32)
- Row 20: Merged cells A20:V20 (separator)
- Row 32: Merged cells A32:V32 (footer)

### 3. Data Fields Available

#### Table Headers (Row 11)
1. ID (Column A)
2. Scan User ID (Column B)
3. OCID (Column C)
4. Worker ID (Column D)
5. Carrier ID (Column E)
6. Field ID (Column F)
7. Task No (Column G)
8. Ripe Bunch (Column H)
9. Unripe Bunch (Column I)
10. Black Bunch (Column J)
11. Rotten Bunch (Column K)
12. Long Stalk Bunch (Column L)
13. Rat Damage Bunch (Column M)
14. Loose Fruit (Column N)
15. Trans No (Column O)
16. Trans Date (Column P)
17. Trans Time (Column Q)
18. Upload DateTime (Column R)
19. Record Tag (Column S)
20. Trans Status (Column T)
21. Trans Type (Column U)
22. Last User (Column V)

#### Template Row Placeholders (Row 12)
Format: `{{data_records.0.field_name}}`
- A12: ID
- B12: SCANUSERID
- C12: OCID
- D12: WORKERID
- E12: CARRIERID
- F12: FIELDID
- G12: TASKNO
- H12: RIPEBCH
- I12: UNRIPEBCH
- J12: BLACKBCH
- K12: ROTTENBCH
- L12: LONGSTALKBCH
- M12: RATDMGBCH
- N12: LOOSEFRUIT
- O12: TRANSNO
- P12: TRANSDATE
- Q12: TRANSTIME
- R12: UPLOADDATETIME
- S12: RECORDTAG
- T12: TRANSSTATUS
- U12: TRANSTYPE
- V12: LASTUSER

### 4. Repeating Section Configuration

According to formula JSON configuration:
- **Sheet Name**: "FFB Scanner Data 04"
- **Data Source**: "main_data"
- **Start Row**: 12
- **End Row**: null (dynamic)
- **Auto Expand**: true
- **Preserve Formatting**: true
- **Columns**: A through AA (21 columns + additional fields)

### 5. Formula Configuration

Main queries defined in `ffb_scannerdata04_formula.json`:

#### Main Data Query
- **Table**: `{table_name}` (dynamic FFBSCANNERDATA{MM})
- **Filter**: TRANSDATE BETWEEN {start_date} AND {end_date}
- **Order**: TRANSDATE, TRANSTIME, ID
- **Fields**: 22 fields including metrics and timestamps

#### Summary Stats Query
Calculates:
- Total records
- Sum of all bunch types (ripe, unripe, black, rotten, etc.)
- Date range (min/max)
- Unique workers count
- Unique fields count

### 6. Output Settings

#### PDF Settings
- Orientation: Landscape
- Paper Size: A4
- Margins: 1cm all sides
- Auto-fit: enabled
- Headers/footers: enabled

#### Excel Settings
- Auto filter: enabled
- Freeze panes: A12
- Zoom level: 85%

## Key Technical Notes

1. **Template Uses**: `{{variable_name}}` placeholder format
2. **Data Section**: Row 12 acts as template for repeating data rows
3. **Dynamic Expansion**: System automatically inserts new rows below row 12
4. **Merged Cells**: Used for titles and separators
5. **Formula Integration**: JSON file defines SQL queries and variable mappings
6. **Multiple Data Sources**: Main data, summary stats, field info, worker info
7. **Date Filtering**: Based on TRANSDATE field
8. **Data Validation**: Required fields, numeric fields, date fields defined

## Related Files

- [[FFB Scanner Data 04 Formula JSON]] - `ffb_scannerdata04_formula.json`
- [[Report Generator System]] - Main system architecture
- [[Firebird Database Schema]] - Database structure reference

## Context Links

This template is part of the PT. Rebinmas Jaya Excel Report Generator System for FFB (Fresh Fruit Bunch) transaction reporting across multiple plantation estates.