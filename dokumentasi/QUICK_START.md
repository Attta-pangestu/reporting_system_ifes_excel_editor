# Quick Start Guide - Excel Report Generator

## 🚀 Getting Started in 5 Minutes

### Step 1: Prerequisites
- Python 3.7+ installed
- Firebird database with ISQL client
- Required Python package: `pip install openpyxl`

### Step 2: Configuration
1. Edit `config.json` with your estate database paths:
```json
{
  "estates": {
    "YourEstate": {
      "name": "Your Estate Name",
      "db_path": "C:/path/to/your/database.fdb"
    }
  }
}
```

### Step 3: Run the Application
```bash
python gui_excel_report_generator.py
```

### Step 4: Generate Your First Report
1. **Select Template**: Choose `sample_template.xlsx` (or your custom template)
2. **Select Formula**: Choose `sample_formula.json` (or your custom formulas)
3. **Set Date Range**: Pick start and end dates
4. **Choose Estates**: Select one or more estates
5. **Output Directory**: Choose where to save reports
6. **Generate**: Click "Generate Report" button

## 📋 Sample Files Included

- `sample_template.xlsx` - Ready-to-use Excel template
- `sample_formula.json` - Sample formula definitions
- `config.json` - Estate configuration template

## 🔧 Customization

### Create Custom Template
```bash
python create_sample_template.py
```

### Modify Formula File
Edit `sample_formula.json` to add your SQL queries and variables.

## ✅ Test the System
```bash
python test_system.py
```

## 🆘 Need Help?
- Check `README.md` for detailed documentation
- Review log files for error details
- Ensure database connectivity with ISQL

## 📊 Expected Output
- Excel files with populated data
- Formatted reports with charts and summaries
- Multi-sheet reports (Summary + Detail)

---
**That's it!** You should now have working Excel reports generated from your Firebird database.