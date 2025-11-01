#!/usr/bin/env python3
"""
Simple Report Editor - FFB Report Generator with Template Engine
===============================================================

Aplikasi GUI untuk menghasilkan laporan FFB dari template yang sudah didefinisikan.
Mendukung preview data, placeholder mapping, dan generate report Excel/PDF.

Author: Claude AI Assistant
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
import sys
from datetime import datetime, timedelta
import threading
import logging
from pathlib import Path

# Import modules
try:
    from firebird_connector import FirebirdConnector
    from template_processor import TemplateProcessor
    from formula_engine import FormulaEngine
    from report_generator import ReportGenerator
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all required modules are in the same directory")
    sys.exit(1)

class SimpleReportEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_logging()
        self.load_config()
        self.setup_ui()
        self.init_components()

    def setup_logging(self):
        """Setup logging untuk aplikasi"""
        log_file = "simple_report_editor.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        """Load konfigurasi aplikasi"""
        try:
            config_file = "config/app_config.json"
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.logger.info("Configuration loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self.config = self.get_default_config()

    def get_default_config(self):
        """Default configuration jika file tidak ditemukan"""
        return {
            "template_settings": {
                "default_template_dir": "./templates"
            },
            "output_settings": {
                "default_output_dir": "./reports"
            },
            "database_settings": {
                "default_database": "D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\IFESS_2B_24-10-2025\\PTRJ_P2B.FDB",
                "default_username": "SYSDBA",
                "default_password": "masterkey"
            }
        }

    def setup_ui(self):
        """Setup UI utama"""
        self.root.title("Simple Report Editor - FFB Report Generator")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(1, weight=1)

        # Header
        self.create_header(main_container)

        # Content area
        content_frame = ttk.Frame(main_container)
        content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        # Left panel - Template & Parameters
        self.create_left_panel(content_frame)

        # Right panel - Preview & Results
        self.create_right_panel(content_frame)

        # Bottom panel - Status & Actions
        self.create_bottom_panel(main_container)

    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.LabelFrame(parent, text="Simple Report Editor", padding="10")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        title_label = ttk.Label(header_frame, text="FFB Report Generator with Template Engine",
                                font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, sticky="w")

        status_label = ttk.Label(header_frame, text="Ready", foreground="green")
        status_label.grid(row=0, column=1, sticky="e")

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(header_frame, textvariable=self.status_var, foreground="green")
        self.status_label.grid(row=0, column=1, sticky="e")

    def create_left_panel(self, parent):
        """Create left panel for template selection and parameters"""
        left_frame = ttk.LabelFrame(parent, text="Template & Parameters", padding="10")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_rowconfigure(3, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Template Selection
        template_frame = ttk.LabelFrame(left_frame, text="Template Selection", padding="5")
        template_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        template_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(template_frame, text="Template:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(template_frame, textvariable=self.template_var, state="readonly")
        self.template_combo.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        self.template_combo.bind('<<ComboboxSelected>>', self.on_template_selected)

        ttk.Button(template_frame, text="Refresh", command=self.refresh_templates).grid(row=0, column=2)

        # Template Info
        self.template_info = scrolledtext.ScrolledText(template_frame, height=6, wrap=tk.WORD)
        self.template_info.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(5, 0))
        self.template_info.config(state=tk.DISABLED)

        # Parameters
        param_frame = ttk.LabelFrame(left_frame, text="Parameters", padding="5")
        param_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        param_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(param_frame, text="Start Date:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.start_date_var = tk.StringVar(value=self.get_first_day_of_month())
        self.start_date_entry = ttk.Entry(param_frame, textvariable=self.start_date_var)
        self.start_date_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))

        ttk.Label(param_frame, text="End Date:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        self.end_date_var = tk.StringVar(value=self.get_last_day_of_month())
        self.end_date_entry = ttk.Entry(param_frame, textvariable=self.end_date_var)
        self.end_date_entry.grid(row=1, column=1, sticky="ew", pady=(5, 0))

        # Database Config
        db_frame = ttk.LabelFrame(left_frame, text="Database", padding="5")
        db_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        db_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(db_frame, text="Database:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.db_var = tk.StringVar(value=self.config.get('database_settings', {}).get('default_database', ''))
        self.db_entry = ttk.Entry(db_frame, textvariable=self.db_var)
        self.db_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))

        ttk.Button(db_frame, text="Browse", command=self.browse_database).grid(row=0, column=2)

        ttk.Label(db_frame, text="Username:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        self.username_var = tk.StringVar(value=self.config.get('database_settings', {}).get('default_username', 'SYSDBA'))
        self.username_entry = ttk.Entry(db_frame, textvariable=self.username_var)
        self.username_entry.grid(row=1, column=1, sticky="ew", pady=(5, 0))

        ttk.Label(db_frame, text="Password:").grid(row=2, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        self.password_var = tk.StringVar(value=self.config.get('database_settings', {}).get('default_password', 'masterkey'))
        self.password_entry = ttk.Entry(db_frame, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=2, column=1, sticky="ew", pady=(5, 0))

        # Action Buttons
        action_frame = ttk.Frame(left_frame)
        action_frame.grid(row=3, column=0, sticky="ew")

        self.preview_btn = ttk.Button(action_frame, text="Preview Data", command=self.preview_data)
        self.preview_btn.grid(row=0, column=0, padx=(0, 5), pady=5)

        self.generate_btn = ttk.Button(action_frame, text="Generate Report", command=self.generate_report)
        self.generate_btn.grid(row=1, column=0, padx=(0, 5), pady=5)

        ttk.Button(action_frame, text="Clear", command=self.clear_all).grid(row=2, column=0, padx=(0, 5), pady=5)

    def create_right_panel(self, parent):
        """Create right panel for preview and results"""
        right_frame = ttk.LabelFrame(parent, text="Preview & Results", padding="10")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Preview Controls
        preview_control_frame = ttk.Frame(right_frame)
        preview_control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.preview_limit_var = tk.StringVar(value="100")
        ttk.Label(preview_control_frame, text="Limit:").grid(row=0, column=0, padx=(0, 5))
        ttk.Entry(preview_control_frame, textvariable=self.preview_limit_var, width=10).grid(row=0, column=1, padx=(0, 10))

        self.export_preview_btn = ttk.Button(preview_control_frame, text="Export Preview", command=self.export_preview, state=tk.DISABLED)
        self.export_preview_btn.grid(row=0, column=2, padx=(0, 5))

        # Preview Area
        self.preview_text = scrolledtext.ScrolledText(right_frame, wrap=tk.NONE)
        self.preview_text.grid(row=1, column=0, sticky="nsew")

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(right_frame, variable=self.progress_var, mode='determinate')
        self.progress_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))

    def create_bottom_panel(self, parent):
        """Create bottom panel for status and actions"""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        # Status bar
        self.status_bar = ttk.Label(bottom_frame, text="Ready", relief=tk.SUNKEN)
        self.status_bar.grid(row=0, column=0, sticky="ew")

        # Quick actions
        actions_frame = ttk.Frame(bottom_frame)
        actions_frame.grid(row=0, column=1, sticky="e")

        ttk.Button(actions_frame, text="Open Reports Folder", command=self.open_reports_folder).grid(row=0, column=0, padx=(5, 0))
        ttk.Button(actions_frame, text="Settings", command=self.open_settings).grid(row=0, column=1, padx=(5, 0))
        ttk.Button(actions_frame, text="About", command=self.show_about).grid(row=0, column=2, padx=(5, 0))

    def init_components(self):
        """Initialize components"""
        self.current_template = None
        self.current_formula = None
        self.preview_data = None
        self.formula_engine = None

        # Load available templates
        self.refresh_templates()

    def get_first_day_of_month(self):
        """Get first day of current month"""
        today = datetime.now()
        return today.replace(day=1).strftime('%Y-%m-%d')

    def get_last_day_of_month(self):
        """Get last day of current month"""
        today = datetime.now()
        next_month = today.replace(day=28) + timedelta(days=4)
        return (next_month - timedelta(days=next_month.day)).strftime('%Y-%m-%d')

    def refresh_templates(self):
        """Refresh available templates"""
        try:
            template_dir = Path(self.config.get('template_settings', {}).get('default_template_dir', './templates'))
            if not template_dir.exists():
                template_dir.mkdir(parents=True, exist_ok=True)

            # Find all JSON formula files
            formula_files = list(template_dir.glob("*_formula.json"))
            template_names = [f.stem.replace('_formula', '') for f in formula_files]

            self.template_combo['values'] = template_names

            if template_names:
                self.template_combo.set(template_names[0])
                self.on_template_selected(None)

            self.logger.info(f"Found {len(template_names)} templates")
            self.update_status(f"Found {len(template_names)} templates")

        except Exception as e:
            self.logger.error(f"Error refreshing templates: {e}")
            messagebox.showerror("Error", f"Failed to refresh templates: {e}")

    def on_template_selected(self, event):
        """Handle template selection"""
        template_name = self.template_var.get()
        if not template_name:
            return

        try:
            # Load formula file
            formula_file = Path(self.config.get('template_settings', {}).get('default_template_dir', './templates')) / f"{template_name}_formula.json"

            if not formula_file.exists():
                messagebox.showerror("Error", f"Formula file not found: {formula_file}")
                return

            with open(formula_file, 'r', encoding='utf-8') as f:
                self.current_formula = json.load(f)

            # Display template info
            self.display_template_info()

            # Update parameter fields based on template
            self.update_parameter_fields()

            self.logger.info(f"Template loaded: {template_name}")
            self.update_status(f"Template loaded: {template_name}")

        except Exception as e:
            self.logger.error(f"Error loading template {template_name}: {e}")
            messagebox.showerror("Error", f"Failed to load template: {e}")

    def display_template_info(self):
        """Display template information"""
        if not self.current_formula:
            return

        info = []
        template_info = self.current_formula.get('template_info', {})

        info.append(f"Name: {template_info.get('name', 'Unknown')}")
        info.append(f"Description: {template_info.get('description', 'No description')}")
        info.append(f"Version: {template_info.get('version', '1.0')}")
        info.append(f"Author: {template_info.get('author', 'Unknown')}")
        info.append(f"Created: {template_info.get('created_date', 'Unknown')}")
        info.append(f"Database Table: {template_info.get('database_table', 'Unknown')}")
        info.append("")

        # Queries info
        queries = self.current_formula.get('queries', {})
        info.append(f"Queries: {len(queries)}")
        for query_name, query_data in queries.items():
            info.append(f"  - {query_name}: {query_data.get('description', 'No description')}")

        self.template_info.config(state=tk.NORMAL)
        self.template_info.delete(1.0, tk.END)
        self.preview_text.insert(1.0, '\n'.join(info))
        self.template_info.config(state=tk.DISABLED)

    def update_parameter_fields(self):
        """Update parameter fields based on template"""
        if not self.current_formula:
            return

        parameters = self.current_formula.get('parameters', {})

        # Update date fields if defaults are specified
        if 'start_date' in parameters:
            start_date_param = parameters['start_date']
            if start_date_param.get('default') == 'first_day_of_month':
                self.start_date_var.set(self.get_first_day_of_month())

        if 'end_date' in parameters:
            end_date_param = parameters['end_date']
            if end_date_param.get('default') == 'last_day_of_month':
                self.end_date_var.set(self.get_last_day_of_month())

    def browse_database(self):
        """Browse for database file"""
        filename = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("Firebird Database", "*.fdb"), ("All Files", "*.*")]
        )
        if filename:
            self.db_var.set(filename)

    def preview_data(self):
        """Preview data from selected template"""
        if not self.current_formula:
            messagebox.showerror("Error", "Please select a template first")
            return

        try:
            self.update_status("Connecting to database...")
            self.progress_var.set(10)

            # Get parameters
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            db_path = self.db_var.get()
            username = self.username_var.get()
            password = self.password_var.get()

            if not all([start_date, end_date, db_path, username, password]):
                messagebox.showerror("Error", "Please fill in all required parameters")
                return

            # Run preview in background thread
            threading.Thread(
                target=self._preview_data_thread,
                args=(start_date, end_date, db_path, username, password),
                daemon=True
            ).start()

        except Exception as e:
            self.logger.error(f"Error starting preview: {e}")
            messagebox.showerror("Error", f"Failed to start preview: {e}")

    def _preview_data_thread(self, start_date, end_date, db_path, username, password):
        """Background thread for data preview"""
        try:
            # Initialize formula engine
            self.formula_engine = FormulaEngine()

            # Connect to database
            self.update_status("Connecting to database...")
            self.progress_var.set(20)

            # Create database connection
            from firebird_connector import FirebirdConnector
            db_connector = FirebirdConnector(db_path, username, password)

            # Execute queries
            self.update_status("Executing queries...")
            self.progress_var.set(40)

            # Process parameters
            params = {
                'start_date': f"'{start_date}'",
                'end_date': f"'{end_date}'",
                'table_name': 'FFBSCANNERDATA04'  # Default table
            }

            results = {}
            queries = self.current_formula.get('queries', {})

            for query_name, query_data in queries.items():
                self.update_status(f"Executing query: {query_name}")
                self.progress_var.set(40 + (len(results) / len(queries)) * 40)

                sql = query_data.get('sql', '')

                # Replace placeholders in SQL
                for param_name, param_value in params.items():
                    sql = sql.replace(f'{{{param_name}}}', str(param_value))

                # Execute query
                query_result = db_connector.execute_query(sql)
                results[query_name] = query_result

            self.preview_data = results

            # Display preview
            self.root.after(0, self.display_preview)

            self.progress_var.set(100)
            self.update_status("Preview completed")

        except Exception as e:
            self.logger.error(f"Error in preview thread: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Preview failed: {e}"))
            self.root.after(0, lambda: self.update_status("Preview failed"))
            self.progress_var.set(0)

    def display_preview(self):
        """Display preview data"""
        if not self.preview_data:
            return

        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)

        preview_lines = []
        preview_lines.append("DATA PREVIEW")
        preview_lines.append("=" * 80)
        preview_lines.append("")

        # Display summary first
        if 'summary_stats' in self.preview_data:
            summary = self.preview_data['summary_stats']
            if summary and len(summary) > 0:
                preview_lines.append("SUMMARY STATISTICS")
                preview_lines.append("-" * 40)
                summary_data = summary[0]  # Assuming first row contains summary
                for key, value in summary_data.items():
                    preview_lines.append(f"{key}: {value}")
                preview_lines.append("")

        # Display main data with limit
        if 'main_data' in self.preview_data:
            main_data = self.preview_data['main_data']
            if main_data:
                preview_lines.append(f"MAIN DATA (First {len(main_data)} records)")
                preview_lines.append("-" * 40)

                if len(main_data) > 0:
                    # Headers
                    headers = list(main_data[0].keys())
                    preview_lines.append("\t".join(headers))

                    # Data rows
                    limit = int(self.preview_limit_var.get())
                    for i, row in enumerate(main_data[:limit]):
                        values = [str(row.get(header, '')) for header in headers]
                        preview_lines.append("\t".join(values))

                    if len(main_data) > limit:
                        preview_lines.append(f"... and {len(main_data) - limit} more records")

        self.preview_text.insert(1.0, '\n'.join(preview_lines))
        self.preview_text.config(state=tk.DISABLED)

        # Enable export preview button
        self.export_preview_btn.config(state=tk.NORMAL)

    def export_preview(self):
        """Export preview data to Excel"""
        if not self.preview_data:
            return

        try:
            filename = filedialog.asksaveasfilename(
                title="Export Preview",
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
            )

            if filename:
                # Export using pandas
                import pandas as pd

                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    for sheet_name, data in self.preview_data.items():
                        if data and len(data) > 0:
                            df = pd.DataFrame(data)
                            df.to_excel(writer, sheet_name=sheet_name, index=False)

                messagebox.showinfo("Success", f"Preview exported to {filename}")
                self.update_status(f"Preview exported to {os.path.basename(filename)}")

        except Exception as e:
            self.logger.error(f"Error exporting preview: {e}")
            messagebox.showerror("Error", f"Failed to export preview: {e}")

    def generate_report(self):
        """Generate full report"""
        if not self.current_formula:
            messagebox.showerror("Error", "Please select a template first")
            return

        if not self.preview_data:
            messagebox.showerror("Error", "Please preview data first")
            return

        try:
            # Check for template file
            template_info = self.current_formula.get('template_info', {})
            template_file = template_info.get('template_file', '')

            if template_file:
                template_path = Path(self.config.get('template_settings', {}).get('default_template_dir', './templates')) / template_file
            else:
                # Browse for template file
                template_path = filedialog.askopenfilename(
                    title="Select Excel Template",
                    filetypes=[("Excel Files", "*.xlsx;*.xls"), ("All Files", "*.*")]
                )

            if not template_path or not os.path.exists(template_path):
                messagebox.showerror("Error", "Template file not found")
                return

            # Run report generation in background thread
            threading.Thread(
                target=self._generate_report_thread,
                args=(str(template_path),),
                daemon=True
            ).start()

        except Exception as e:
            self.logger.error(f"Error starting report generation: {e}")
            messagebox.showerror("Error", f"Failed to start report generation: {e}")

    def _generate_report_thread(self, template_path):
        """Background thread for report generation"""
        try:
            self.update_status("Generating report...")
            self.progress_var.set(10)

            # Initialize report generator
            from report_generator import ReportGenerator
            generator = ReportGenerator()

            # Get parameters
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            db_path = self.db_var.get()
            username = self.username_var.get()
            password = self.password_var.get()

            # Process parameters
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'table_name': 'FFBSCANNERDATA04'
            }

            self.update_status("Processing template...")
            self.progress_var.set(30)

            # Generate report
            output_path = generator.generate_report(
                template_path=template_path,
                formula_data=self.current_formula,
                db_params={
                    'database_path': db_path,
                    'username': username,
                    'password': password
                },
                report_params=params
            )

            self.progress_var.set(100)
            self.update_status(f"Report generated: {os.path.basename(output_path)}")

            # Ask to open the report
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Report generated successfully!\n\nSaved as: {output_path}"))

        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Report generation failed: {e}"))
            self.root.after(0, lambda: self.update_status("Report generation failed"))
            self.progress_var.set(0)

    def clear_all(self):
        """Clear all fields and data"""
        self.template_var.set('')
        self.start_date_var.set(self.get_first_day_of_month())
        self.end_date_var.set(self.get_last_day_of_month())
        self.current_template = None
        self.current_formula = None
        self.preview_data = None

        self.template_info.config(state=tk.NORMAL)
        self.template_info.delete(1.0, tk.END)
        self.template_info.config(state=tk.DISABLED)

        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state=tk.DISABLED)

        self.export_preview_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.update_status("Cleared")

    def open_reports_folder(self):
        """Open reports folder"""
        import subprocess
        import platform

        reports_dir = Path(self.config.get('output_settings', {}).get('default_output_dir', './reports'))
        reports_dir.mkdir(parents=True, exist_ok=True)

        try:
            if platform.system() == 'Windows':
                subprocess.run(['explorer', str(reports_dir)], check=True)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(reports_dir)], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', str(reports_dir)], check=True)
        except Exception as e:
            self.logger.error(f"Error opening reports folder: {e}")

    def open_settings(self):
        """Open settings dialog"""
        # TODO: Implement settings dialog
        messagebox.showinfo("Settings", "Settings dialog not implemented yet")

    def show_about(self):
        """Show about dialog"""
        about_text = """Simple Report Editor - FFB Report Generator
Version 1.0.0

Aplikasi untuk menghasilkan laporan FFB dari template yang sudah didefinisikan.

Features:
• Template-based report generation
• Data preview functionality
• Excel and PDF export
• Firebird database integration

Author: Claude AI Assistant
Created: 2025-11-01"""

        messagebox.showinfo("About", about_text)

    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()

    def run(self):
        """Run the application"""
        self.logger.info("Starting Simple Report Editor")
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleReportEditor()
    app.run()