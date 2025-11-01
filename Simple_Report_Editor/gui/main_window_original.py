"""
Main Window GUI
Jendela utama aplikasi Simple Report Editor
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import logging
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
    """Jendela utama aplikasi"""

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
        """Create parameters section"""
        param_frame = ttk.LabelFrame(self.main_frame, text="Report Parameters", padding="10")
        param_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        param_frame.columnconfigure(1, weight=1)
        param_frame.columnconfigure(3, weight=1)
        param_frame.columnconfigure(5, weight=1)

        # Date range
        ttk.Label(param_frame, text="Start Date:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.start_date_var = tk.StringVar()
        start_date_entry = ttk.Entry(param_frame, textvariable=self.start_date_var, width=15)
        start_date_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))

        ttk.Label(param_frame, text="End Date:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.end_date_var = tk.StringVar()
        end_date_entry = ttk.Entry(param_frame, textvariable=self.end_date_var, width=15)
        end_date_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))

        # Field ID
        ttk.Label(param_frame, text="Field ID:").grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        self.field_id_var = tk.StringVar()
        field_id_entry = ttk.Entry(param_frame, textvariable=self.field_id_var, width=15)
        field_id_entry.grid(row=0, column=5, sticky=tk.W, padx=(0, 20))

        # Worker ID
        ttk.Label(param_frame, text="Worker ID:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.worker_id_var = tk.StringVar()
        worker_id_entry = ttk.Entry(param_frame, textvariable=self.worker_id_var, width=15)
        worker_id_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=(10, 0))

        # Record Tag
        ttk.Label(param_frame, text="Record Tag:").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.record_tag_var = tk.StringVar()
        record_tag_entry = ttk.Entry(param_frame, textvariable=self.record_tag_var, width=15)
        record_tag_entry.grid(row=1, column=3, sticky=tk.W, padx=(0, 20), pady=(10, 0))

        # Output path
        ttk.Label(param_frame, text="Output Directory:").grid(row=1, column=4, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        output_entry = ttk.Entry(param_frame, textvariable=self.output_path, width=30)
        output_entry.grid(row=1, column=5, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(param_frame, text="Browse", command=self._browse_output_dir).grid(row=1, column=6, pady=(10, 0))

        # Set default output directory
        self.output_path.set(os.getcwd())

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

        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return False

        return True

    def _get_parameters(self) -> Dict[str, Any]:
        """Get parameters dari form"""
        return {
            'start_date': self.start_date_var.get() or None,
            'end_date': self.end_date_var.get() or None,
            'field_id': self.field_id_var.get() or None,
            'worker_id': self.worker_id_var.get() or None,
            'record_tag': self.record_tag_var.get() or None,
            'output_path': self.output_path.get()
        }

    def run(self):
        """Jalankan aplikasi"""
        self._log_message("Simple Report Editor started")
        self.root.mainloop()

def main():
    """Main function"""
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main()