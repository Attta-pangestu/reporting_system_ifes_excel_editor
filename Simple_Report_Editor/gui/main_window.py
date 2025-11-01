"""
Main Window GUI (Updated with Date Pickers)
Jendela utama aplikasi Simple Report Editor dengan date picker untuk parameter tanggal
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database_connector import FirebirdConnectorEnhanced
from core.template_processor import TemplateProcessor
from core.formula_engine import FormulaEngine
from utils.pdf_generator import PDFGenerator
from gui.database_selector import DatabaseSelector
from gui.template_selector import TemplateSelector
from gui.data_preview import DataPreviewWindow
from gui.report_generator_ui import ReportGeneratorDialog

logger = logging.getLogger(__name__)

class MainWindow:
    """Jendela utama aplikasi dengan date picker"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple Report Editor - FFB Report Generator")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # Variables
        self.current_database = tk.StringVar(value=r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB")
        self.current_template = tk.StringVar()
        self.current_formula = tk.StringVar()
        self.output_path = tk.StringVar()

        # Components
        self.database_connector = None
        self.template_processor = None
        self.formula_engine = None
        self.pdf_generator = None

        # Status
        self.database_connected = tk.BooleanVar(value=False)
        self.template_loaded = tk.BooleanVar(value=False)
        self.formula_loaded = tk.BooleanVar(value=False)

        # Date picker components
        self.start_date_picker = None
        self.end_date_picker = None

        self._setup_ui()
        self._setup_logging()
        self._initialize_components()

    def _setup_ui(self):
        """Setup UI components"""
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        # Create sections
        self._create_header()
        self._create_database_section()
        self._create_template_section()
        self._create_parameters_section()
        self._create_action_buttons()
        self._create_status_section()

    def _create_header(self):
        """Create header section"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

        # Title
        title_label = ttk.Label(header_frame, text="Simple Report Editor",
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W)

        # Subtitle
        subtitle_label = ttk.Label(header_frame, text="FFB Report Generator with Template Engine",
                                  font=('Arial', 10))
        subtitle_label.grid(row=1, column=0, sticky=tk.W)

    def _create_database_section(self):
        """Create database selection section"""
        db_frame = ttk.LabelFrame(self.main_frame, text="Database Configuration", padding="10")
        db_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        db_frame.columnconfigure(1, weight=1)

        # Database path
        ttk.Label(db_frame, text="Database File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        db_entry = ttk.Entry(db_frame, textvariable=self.current_database, width=60)
        db_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Button(db_frame, text="Browse", command=self._browse_database).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(db_frame, text="Test Connection", command=self._test_database_connection).grid(row=0, column=3)

        # Connection status
        self.db_status_label = ttk.Label(db_frame, text="Not Connected", foreground="red")
        self.db_status_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))

    def _create_template_section(self):
        """Create template selection section"""
        template_frame = ttk.LabelFrame(self.main_frame, text="Template Configuration", padding="10")
        template_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        template_frame.columnconfigure(1, weight=1)
        template_frame.columnconfigure(4, weight=1)

        # Excel template
        ttk.Label(template_frame, text="Excel Template:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        template_entry = ttk.Entry(template_frame, textvariable=self.current_template, width=40)
        template_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(template_frame, text="Browse", command=self._browse_template).grid(row=0, column=2, padx=(0, 10))

        # Formula JSON
        ttk.Label(template_frame, text="Formula JSON:").grid(row=0, column=3, sticky=tk.W, padx=(20, 10))
        formula_entry = ttk.Entry(template_frame, textvariable=self.current_formula, width=40)
        formula_entry.grid(row=0, column=4, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(template_frame, text="Browse", command=self._browse_formula).grid(row=0, column=5, padx=(0, 10))

        # Template status
        self.template_status_label = ttk.Label(template_frame, text="No template loaded", foreground="red")
        self.template_status_label.grid(row=1, column=0, columnspan=6, sticky=tk.W, pady=(5, 0))

    def _create_parameters_section(self):
        """Create parameters section with date pickers"""
        param_frame = ttk.LabelFrame(self.main_frame, text="Report Parameters", padding="10")
        param_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        param_frame.columnconfigure(1, weight=1)
        param_frame.columnconfigure(3, weight=1)
        param_frame.columnconfigure(5, weight=1)

        # Date range with date pickers
        ttk.Label(param_frame, text="Start Date:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        start_date_frame = ttk.Frame(param_frame)
        start_date_frame.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))

        self.start_date_var = tk.StringVar()
        self.start_date_entry = ttk.Entry(start_date_frame, textvariable=self.start_date_var, width=15)
        self.start_date_entry.grid(row=0, column=0, padx=(0, 5))

        try:
            from tkcalendar import DateEntry
            self.start_date_picker = DateEntry(start_date_frame, textvariable=self.start_date_var,
                                             width=12, date_pattern='yyyy-mm-dd',
                                             locale='id_ID')
            self.start_date_picker.grid(row=0, column=1)
        except ImportError:
            # Fallback to simple entry if tkcalendar not available
            self.start_date_picker = None
            ttk.Button(start_date_frame, text="📅", command=lambda: self._manual_date_entry('start')).grid(row=0, column=1)

        ttk.Label(param_frame, text="End Date:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        end_date_frame = ttk.Frame(param_frame)
        end_date_frame.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))

        self.end_date_var = tk.StringVar()
        self.end_date_entry = ttk.Entry(end_date_frame, textvariable=self.end_date_var, width=15)
        self.end_date_entry.grid(row=0, column=0, padx=(0, 5))

        try:
            from tkcalendar import DateEntry
            self.end_date_picker = DateEntry(end_date_frame, textvariable=self.end_date_var,
                                           width=12, date_pattern='yyyy-mm-dd',
                                           locale='id_ID')
            self.end_date_picker.grid(row=0, column=1)
        except ImportError:
            # Fallback to simple entry if tkcalendar not available
            self.end_date_picker = None
            ttk.Button(end_date_frame, text="📅", command=lambda: self._manual_date_entry('end')).grid(row=0, column=1)

        # Quick date range buttons
        quick_frame = ttk.Frame(param_frame)
        quick_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))

        ttk.Label(quick_frame, text="Quick Range:").grid(row=0, column=0, padx=(0, 10))
        ttk.Button(quick_frame, text="Today", command=self._set_today).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(quick_frame, text="This Week", command=self._set_this_week).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(quick_frame, text="This Month", command=self._set_this_month).grid(row=0, column=3, padx=(0, 5))
        ttk.Button(quick_frame, text="Last Month", command=self._set_last_month).grid(row=0, column=4, padx=(0, 5))
        ttk.Button(quick_frame, text="This Year", command=self._set_this_year).grid(row=0, column=5, padx=(0, 5))

        # Output path
        ttk.Label(param_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        output_frame = ttk.Frame(param_frame)
        output_frame.grid(row=2, column=1, columnspan=5, sticky=(tk.W, tk.E), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)

        self.output_path = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path, width=50)
        output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(output_frame, text="Browse", command=self._browse_output_dir).grid(row=0, column=1)

        # Set default output directory
        self.output_path.set(os.getcwd())

        # Set default date range (current month)
        self._set_this_month()

    def _create_action_buttons(self):
        """Create action buttons"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Buttons
        ttk.Button(button_frame, text="Preview Data", command=self._preview_data).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Generate Excel Report", command=self._generate_excel_report).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Generate PDF Report", command=self._generate_pdf_report).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="Load Sample", command=self._load_sample_data).grid(row=0, column=3, padx=(0, 10))
        ttk.Button(button_frame, text="Create New Template", command=self._create_new_template).grid(row=0, column=4, padx=(0, 10))

    def _create_status_section(self):
        """Create status section"""
        status_frame = ttk.LabelFrame(self.main_frame, text="Status", padding="10")
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)

        # Status text
        self.status_text = tk.Text(status_frame, height=8, wrap=tk.WORD)
        status_scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)

        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        status_frame.rowconfigure(0, weight=1)

    def _setup_logging(self):
        """Setup logging ke status text"""
        class StatusTextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                # Use after to ensure thread safety
                self.text_widget.after(0, append)

        # Add handler to root logger
        handler = StatusTextHandler(self.status_text)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)

    def _initialize_components(self):
        """Initialize component instances"""
        try:
            self.pdf_generator = PDFGenerator()
            self._log_message("PDF Generator initialized")
        except Exception as e:
            self._log_message(f"Error initializing PDF Generator: {e}", level="ERROR")

    # Date picker helper methods
    def _set_today(self):
        """Set date range to today"""
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        self.start_date_var.set(date_str)
        self.end_date_var.set(date_str)
        if self.start_date_picker:
            self.start_date_picker.set_date(today)
        if self.end_date_picker:
            self.end_date_picker.set_date(today)

    def _set_this_week(self):
        """Set date range to this week"""
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        self.start_date_var.set(start_of_week.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_of_week.strftime('%Y-%m-%d'))
        if self.start_date_picker:
            self.start_date_picker.set_date(start_of_week)
        if self.end_date_picker:
            self.end_date_picker.set_date(end_of_week)

    def _set_this_month(self):
        """Set date range to this month"""
        today = datetime.now()
        start_of_month = today.replace(day=1)
        self.start_date_var.set(start_of_month.strftime('%Y-%m-%d'))
        self.end_date_var.set(today.strftime('%Y-%m-%d'))
        if self.start_date_picker:
            self.start_date_picker.set_date(start_of_month)
        if self.end_date_picker:
            self.end_date_picker.set_date(today)

    def _set_last_month(self):
        """Set date range to last month"""
        today = datetime.now()
        if today.month == 1:
            last_month = today.replace(year=today.year-1, month=12, day=1)
        else:
            last_month = today.replace(month=today.month-1, day=1)

        # Calculate last day of last month
        if last_month.month == 12:
            next_month = last_month.replace(year=last_month.year+1, month=1, day=1)
        else:
            next_month = last_month.replace(month=last_month.month+1, day=1)

        end_of_last_month = next_month - timedelta(days=1)

        self.start_date_var.set(last_month.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_of_last_month.strftime('%Y-%m-%d'))
        if self.start_date_picker:
            self.start_date_picker.set_date(last_month)
        if self.end_date_picker:
            self.end_date_picker.set_date(end_of_last_month)

    def _set_this_year(self):
        """Set date range to this year"""
        today = datetime.now()
        start_of_year = today.replace(month=1, day=1)
        self.start_date_var.set(start_of_year.strftime('%Y-%m-%d'))
        self.end_date_var.set(today.strftime('%Y-%m-%d'))
        if self.start_date_picker:
            self.start_date_picker.set_date(start_of_year)
        if self.end_date_picker:
            self.end_date_picker.set_date(today)

    def _manual_date_entry(self, date_type):
        """Manual date entry fallback"""
        from tkinter import simpledialog
        date_str = simpledialog.askstring("Enter Date", f"Enter {date_type} date (YYYY-MM-DD):")
        if date_str:
            try:
                # Validate date format
                datetime.strptime(date_str, '%Y-%m-%d')
                if date_type == 'start':
                    self.start_date_var.set(date_str)
                else:
                    self.end_date_var.set(date_str)
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format")

    # Rest of the methods from original main_window.py
    def _log_message(self, message: str, level: str = "INFO"):
        """Log message ke status dan logger"""
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)

    def _browse_database(self):
        """Browse untuk database file"""
        filename = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("Firebird Database", "*.fdb"), ("All Files", "*.*")]
        )
        if filename:
            self.current_database.set(filename)
            self._log_message(f"Database selected: {filename}")

    def _browse_template(self):
        """Browse untuk Excel template"""
        filename = filedialog.askopenfilename(
            title="Select Excel Template",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        if filename:
            self.current_template.set(filename)
            self._load_template_info(filename)

    def _browse_formula(self):
        """Browse untuk formula JSON"""
        filename = filedialog.askopenfilename(
            title="Select Formula JSON",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filename:
            self.current_formula.set(filename)
            self._load_formula_info(filename)

    def _browse_output_dir(self):
        """Browse untuk output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_path.set(directory)
            self._log_message(f"Output directory set: {directory}")

    def _load_template_info(self, template_path: str):
        """Load dan validasi template"""
        try:
            if not self.template_processor:
                self.template_processor = TemplateProcessor()

            if self.template_processor.load_template(template_path):
                info = self.template_processor.get_template_info()
                self._log_message(f"Template loaded: {info['placeholder_count']} placeholders, {info['repeating_section_count']} repeating sections")
                self.template_status_label.config(text="Template loaded", foreground="green")
                self.template_loaded.set(True)
            else:
                self.template_status_label.config(text="Failed to load template", foreground="red")
                self.template_loaded.set(False)

        except Exception as e:
            self._log_message(f"Error loading template: {e}", level="ERROR")
            self.template_status_label.config(text="Error loading template", foreground="red")
            self.template_loaded.set(False)

    def _load_formula_info(self, formula_path: str):
        """Load dan validasi formula"""
        try:
            if not self.formula_engine:
                self.formula_engine = FormulaEngine()

            if self.formula_engine.load_formula(formula_path):
                info = self.formula_engine.get_formula_info()
                self._log_message(f"Formula loaded: {info['query_count']} queries, {info['variable_count']} variables")
                self.formula_loaded.set(True)
                self._update_template_status()
            else:
                self._log_message("Failed to load formula", level="ERROR")
                self.formula_loaded.set(False)

        except Exception as e:
            self._log_message(f"Error loading formula: {e}", level="ERROR")
            self.formula_loaded.set(False)

    def _update_template_status(self):
        """Update template status based on loaded components"""
        if self.template_loaded.get() and self.formula_loaded.get():
            self.template_status_label.config(text="Template and formula loaded", foreground="green")
        elif self.template_loaded.get():
            self.template_status_label.config(text="Template loaded, formula missing", foreground="orange")
        elif self.formula_loaded.get():
            self.template_status_label.config(text="Formula loaded, template missing", foreground="orange")

    def _test_database_connection(self):
        """Test koneksi database"""
        try:
            db_path = self.current_database.get()
            if not db_path or not os.path.exists(db_path):
                messagebox.showerror("Error", "Database file not found")
                return

            self.database_connector = FirebirdConnectorEnhanced(db_path=db_path)

            if self.database_connector.test_connection():
                self.db_status_label.config(text="Connected", foreground="green")
                self.database_connected.set(True)
                self._log_message("Database connection successful")
                messagebox.showinfo("Success", "Database connection successful!")
            else:
                self.db_status_label.config(text="Connection failed", foreground="red")
                self.database_connected.set(False)
                self._log_message("Database connection failed", level="ERROR")
                messagebox.showerror("Error", "Database connection failed")

        except Exception as e:
            self.db_status_label.config(text="Connection error", foreground="red")
            self.database_connected.set(False)
            self._log_message(f"Database connection error: {e}", level="ERROR")
            messagebox.showerror("Error", f"Database connection error: {e}")

    def _preview_data(self):
        """Preview data dari query"""
        if not self._validate_prerequisites():
            return

        try:
            # Get parameters
            parameters = self._get_parameters()

            # Show preview window
            preview_window = DataPreviewWindow(
                self.root,
                self.database_connector,
                self.formula_engine,
                parameters
            )
            preview_window.show()

        except Exception as e:
            self._log_message(f"Error previewing data: {e}", level="ERROR")
            messagebox.showerror("Error", f"Error previewing data: {e}")

    def _generate_excel_report(self):
        """Generate Excel report"""
        if not self._validate_prerequisites():
            return

        try:
            # Show report generator dialog
            dialog = ReportGeneratorDialog(
                self.root,
                self.database_connector,
                self.template_processor,
                self.formula_engine,
                output_format="excel"
            )
            result = dialog.show()

            if result:
                self._log_message(f"Excel report generated: {result}")
                messagebox.showinfo("Success", f"Excel report generated:\n{result}")

        except Exception as e:
            self._log_message(f"Error generating Excel report: {e}", level="ERROR")
            messagebox.showerror("Error", f"Error generating Excel report: {e}")

    def _generate_pdf_report(self):
        """Generate PDF report"""
        if not self._validate_prerequisites():
            return

        try:
            # Show report generator dialog
            dialog = ReportGeneratorDialog(
                self.root,
                self.database_connector,
                self.template_processor,
                self.formula_engine,
                output_format="pdf"
            )
            result = dialog.show()

            if result:
                self._log_message(f"PDF report generated: {result}")
                messagebox.showinfo("Success", f"PDF report generated:\n{result}")

        except Exception as e:
            self._log_message(f"Error generating PDF report: {e}", level="ERROR")
            messagebox.showerror("Error", f"Error generating PDF report: {e}")

    def _load_sample_data(self):
        """Load sample data untuk testing"""
        try:
            # Load default sample
            template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
            sample_template = os.path.join(template_dir, 'ffb_scannerdata04_formula.json')
            sample_excel = None

            # Find Excel template
            for file in os.listdir(template_dir):
                if file.startswith('FFB_ScannerData04_Template_') and file.endswith('.xlsx'):
                    sample_excel = os.path.join(template_dir, file)
                    break

            if os.path.exists(sample_template):
                self.current_formula.set(sample_template)
                self._load_formula_info(sample_template)

            if sample_excel:
                self.current_template.set(sample_excel)
                self._load_template_info(sample_excel)

            self._log_message("Sample data loaded")

        except Exception as e:
            self._log_message(f"Error loading sample data: {e}", level="ERROR")

    def _create_new_template(self):
        """Create new template"""
        try:
            from utils.template_generator import FFBTemplateGenerator
            generator = FFBTemplateGenerator()
            template_path = generator.create_ffb_scannerdata04_template()

            self.current_template.set(template_path)
            self._load_template_info(template_path)
            self._log_message(f"New template created: {template_path}")

        except Exception as e:
            self._log_message(f"Error creating template: {e}", level="ERROR")

    def _validate_prerequisites(self) -> bool:
        """Validasi prerequisites untuk generate report"""
        errors = []

        if not self.database_connected.get():
            errors.append("Database not connected")

        if not self.template_loaded.get():
            errors.append("Template not loaded")

        if not self.formula_loaded.get():
            errors.append("Formula not loaded")

        # Validate date parameters
        start_date = self.start_date_var.get().strip()
        end_date = self.end_date_var.get().strip()

        if not start_date:
            errors.append("Start date is required")
        else:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                errors.append("Invalid start date format (use YYYY-MM-DD)")

        if not end_date:
            errors.append("End date is required")
        else:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                errors.append("Invalid end date format (use YYYY-MM-DD)")

        if start_date and end_date and start_date > end_date:
            errors.append("Start date cannot be after end date")

        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return False

        return True

    def _get_parameters(self) -> Dict[str, Any]:
        """Get parameters dari form"""
        return {
            'start_date': self.start_date_var.get().strip() or None,
            'end_date': self.end_date_var.get().strip() or None,
            'output_path': self.output_path.get()
        }

    def run(self):
        """Jalankan aplikasi"""
        self._log_message("Simple Report Editor started")
        self._log_message("Date picker functionality enabled")
        self.root.mainloop()

def main():
    """Main function"""
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main()