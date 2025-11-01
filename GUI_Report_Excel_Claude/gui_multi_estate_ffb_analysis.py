#!/usr/bin/env python3
"""
GUI Multi-Estate FFB Analysis Report Generator
Aplikasi GUI untuk generating laporan FFB Analysis multi-estate
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import threading
import json
import os
from datetime import datetime, date
from pathlib import Path
import logging

from excel_report_generator import ExcelReportGenerator

class MultiEstateFFBAnalysisGUI:
    """
    GUI Application untuk Multi-Estate FFB Analysis Report Generator
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Estate FFB Analysis Report Generator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        # Initialize report generator
        self.report_generator = None

        # Setup logging
        self.setup_logging()

        # Setup GUI
        self.setup_gui()

        # Initialize components
        self.initialize_components()

        # Status variables
        self.is_generating = False
        self.current_thread = None

    def setup_logging(self):
        """Setup logging untuk GUI"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('gui_ffb_analysis.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_gui(self):
        """Setup GUI components"""
        # Create main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)

        # Title
        title_frame = ttk.Frame(main_container)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E))

        title_label = ttk.Label(
            title_frame,
            text="Multi-Estate FFB Analysis Report Generator",
            font=('Arial', 16, 'bold')
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="Generate laporan analisis FFB dari database Firebird",
            font=('Arial', 10)
        )
        subtitle_label.pack()

        # Configuration Section
        config_frame = ttk.LabelFrame(main_container, text="Konfigurasi Template", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E))
        config_frame.columnconfigure(1, weight=1)

        # Template File
        ttk.Label(config_frame, text="File Template:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.template_path_var = tk.StringVar(value="Template_Laporan_FFB_Analysis.xlsx")
        template_entry = ttk.Entry(config_frame, textvariable=self.template_path_var, width=60)
        template_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        ttk.Button(config_frame, text="Browse", command=self.browse_template).grid(row=0, column=2, pady=5)

        # Formula File
        ttk.Label(config_frame, text="File Formula:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.formula_path_var = tk.StringVar(value="laporan_ffb_analysis_formula.json")
        formula_entry = ttk.Entry(config_frame, textvariable=self.formula_path_var, width=60)
        formula_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        ttk.Button(config_frame, text="Browse", command=self.browse_formula).grid(row=1, column=2, pady=5)

        # Estate Configuration File
        ttk.Label(config_frame, text="Config Estate:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.estate_config_var = tk.StringVar(value="estate_config.json")
        config_entry = ttk.Entry(config_frame, textvariable=self.estate_config_var, width=60)
        config_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        ttk.Button(config_frame, text="Browse", command=self.browse_estate_config).grid(row=2, column=2, pady=5)

        # Report Parameters Section
        params_frame = ttk.LabelFrame(main_container, text="Parameter Laporan", padding="10")
        params_frame.grid(row=2, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E))
        params_frame.columnconfigure(1, weight=1)

        # Date Range
        ttk.Label(params_frame, text="Periode Laporan:").grid(row=0, column=0, sticky=tk.W, pady=5)

        date_frame = ttk.Frame(params_frame)
        date_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)

        ttk.Label(date_frame, text="Dari:").pack(side=tk.LEFT, padx=(0, 5))
        self.start_date_var = None
        self.start_date_entry = DateEntry(
            date_frame,
            width=15,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            locale='id_ID'
        )
        self.start_date_entry.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(date_frame, text="Sampai:").pack(side=tk.LEFT, padx=(0, 5))
        self.end_date_entry = DateEntry(
            date_frame,
            width=15,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            locale='id_ID'
        )
        self.end_date_entry.pack(side=tk.LEFT)

        # Output Directory
        ttk.Label(params_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar(value="reports")
        output_frame = ttk.Frame(params_frame)
        output_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        output_frame.columnconfigure(0, weight=1)

        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=50)
        output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).grid(row=0, column=1, padx=(10, 0))

        # Estate Selection Section
        estate_frame = ttk.LabelFrame(main_container, text="Pilih Estate", padding="10")
        estate_frame.grid(row=3, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.rowconfigure(3, weight=1)

        # Estate selection with checkboxes
        estate_scroll_frame = ttk.Frame(estate_frame)
        estate_scroll_frame.pack(fill=tk.BOTH, expand=True)

        # Create scrollable frame
        canvas = tk.Canvas(estate_scroll_frame, height=200)
        scrollbar = ttk.Scrollbar(estate_scroll_frame, orient="vertical", command=canvas.yview)
        self.estate_check_frame = ttk.Frame(canvas)

        self.estate_check_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.estate_check_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Control Buttons
        self.estate_vars = {}
        self.estate_checkboxes = {}

        # Select All / None buttons
        estate_button_frame = ttk.Frame(estate_frame)
        estate_button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(estate_button_frame, text="Select All", command=self.select_all_estates).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(estate_button_frame, text="Select None", command=self.select_no_estates).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(estate_button_frame, text="Test Connections", command=self.test_connections).pack(side=tk.LEFT, padx=(0, 10))

        # Action Buttons Section
        action_frame = ttk.Frame(main_container)
        action_frame.grid(row=4, column=0, columnspan=3, pady=(0, 20))

        self.generate_button = ttk.Button(
            action_frame,
            text="Generate Laporan",
            command=self.generate_report,
            style="Accent.TButton"
        )
        self.generate_button.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(action_frame, text="Preview Data", command=self.preview_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Open Reports", command=self.open_reports_folder).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=(0, 10))

        # Progress Section
        progress_frame = ttk.LabelFrame(main_container, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky=tk.W)

        # Log Section
        log_frame = ttk.LabelFrame(main_container, text="Log Messages", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.rowconfigure(6, weight=1)
        log_frame.columnconfigure(0, weight=1)

        # Create text widget with scrollbar
        log_scroll_frame = ttk.Frame(log_frame)
        log_scroll_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_scroll_frame, height=10, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_scroll_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")

        # Configure text tags
        self.log_text.tag_configure("info", foreground="black")
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("error", foreground="red")

    def initialize_components(self):
        """Initialize report generator dan load estates"""
        try:
            self.update_status("Initializing components...")
            self.report_generator = ExcelReportGenerator(
                template_path=self.template_path_var.get(),
                formula_path=self.formula_path_var.get(),
                estate_config_path=self.estate_config_var.get()
            )

            # Load estates
            self.load_estates()
            self.update_status("Ready")
            self.log_message("System initialized successfully", "success")

        except Exception as e:
            self.update_status(f"Initialization failed: {e}")
            self.log_message(f"Error initializing system: {e}", "error")
            messagebox.showerror("Initialization Error", f"Failed to initialize system: {e}")

    def load_estates(self):
        """Load estate checkboxes"""
        # Clear existing checkboxes
        for checkbox in self.estate_checkboxes.values():
            checkbox.destroy()
        self.estate_vars.clear()
        self.estate_checkboxes.clear()

        # Get available estates
        estates = self.report_generator.get_available_estates()

        if not estates:
            self.log_message("No estates found in configuration", "warning")
            return

        # Create checkboxes
        for i, estate in enumerate(estates):
            var = tk.BooleanVar()
            self.estate_vars[estate] = var

            checkbox = ttk.Checkbutton(
                self.estate_check_frame,
                text=estate,
                variable=var
            )
            checkbox.grid(row=i, column=0, sticky=tk.W, pady=2, padx=5)
            self.estate_checkboxes[estate] = checkbox

        self.log_message(f"Loaded {len(estates)} estates", "info")

    def browse_template(self):
        """Browse untuk template file"""
        filename = filedialog.askopenfilename(
            title="Pilih File Template Excel",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.template_path_var.set(filename)

    def browse_formula(self):
        """Browse untuk formula file"""
        filename = filedialog.askopenfilename(
            title="Pilih File Formula",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.formula_path_var.set(filename)

    def browse_estate_config(self):
        """Browse untuk estate config file"""
        filename = filedialog.askopenfilename(
            title="Pilih File Konfigurasi Estate",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.estate_config_var.set(filename)

    def browse_output_dir(self):
        """Browse untuk output directory"""
        directory = filedialog.askdirectory(title="Pilih Output Directory")
        if directory:
            self.output_dir_var.set(directory)

    def select_all_estates(self):
        """Select all estates"""
        for var in self.estate_vars.values():
            var.set(True)

    def select_no_estates(self):
        """Deselect all estates"""
        for var in self.estate_vars.values():
            var.set(False)

    def get_selected_estates(self):
        """Get list of selected estates"""
        return [estate for estate, var in self.estate_vars.items() if var.get()]

    def test_connections(self):
        """Test database connections untuk selected estates"""
        selected_estates = self.get_selected_estates()
        if not selected_estates:
            messagebox.showwarning("No Selection", "Please select at least one estate")
            return

        self.update_status("Testing database connections...")
        self.log_message(f"Testing connections for {len(selected_estates)} estates...", "info")

        results = {}
        for estate in selected_estates:
            self.log_message(f"Testing connection to {estate}...", "info")
            try:
                is_connected = self.report_generator.test_database_connection(estate)
                results[estate] = is_connected
                status = "Success" if is_connected else "Failed"
                self.log_message(f"Connection to {estate}: {status}", "success" if is_connected else "error")
            except Exception as e:
                results[estate] = False
                self.log_message(f"Connection to {estate} failed: {e}", "error")

        # Show summary
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)

        message = f"Connection Test Results:\n\n"
        message += f"Successful: {success_count}/{total_count}\n\n"
        message += "Details:\n"
        for estate, success in results.items():
            status = "✓" if success else "✗"
            message += f"{status} {estate}\n"

        messagebox.showinfo("Connection Test Results", message)
        self.update_status("Ready")

    def generate_report(self):
        """Generate laporan"""
        if self.is_generating:
            messagebox.showwarning("In Progress", "Report generation is already in progress")
            return

        # Validate inputs
        selected_estates = self.get_selected_estates()
        if not selected_estates:
            messagebox.showwarning("No Selection", "Please select at least one estate")
            return

        # Get dates
        start_date = self.start_date_entry.get_date().strftime('%Y-%m-%d')
        end_date = self.end_date_entry.get_date().strftime('%Y-%m-%d')

        # Validate date range
        if start_date > end_date:
            messagebox.showerror("Invalid Date Range", "Start date cannot be after end date")
            return

        # Get output directory
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showwarning("Missing Output", "Please specify output directory")
            return

        # Start generation in separate thread
        self.current_thread = threading.Thread(
            target=self._generate_report_thread,
            args=(start_date, end_date, selected_estates, output_dir)
        )
        self.current_thread.start()

    def _generate_report_thread(self, start_date, end_date, selected_estates, output_dir):
        """Thread untuk report generation"""
        try:
            self.is_generating = True
            self.generate_button.config(state='disabled')
            self.update_status("Generating reports...")
            self.log_message(f"Starting report generation for {len(selected_estates)} estates", "info")
            self.log_message(f"Period: {start_date} to {end_date}", "info")
            self.log_message(f"Output: {output_dir}", "info")

            # Initialize report generator with current paths
            self.report_generator = ExcelReportGenerator(
                template_path=self.template_path_var.get(),
                formula_path=self.formula_path_var.get(),
                estate_config_path=self.estate_config_var.get()
            )

            # Generate reports
            success, results = self.report_generator.generate_report(
                start_date=start_date,
                end_date=end_date,
                selected_estates=selected_estates,
                output_dir=output_dir
            )

            # Update UI in main thread
            self.root.after(0, self._report_generation_complete, success, results)

        except Exception as e:
            self.root.after(0, self._report_generation_error, str(e))

    def _report_generation_complete(self, success, results):
        """Handle report generation completion"""
        self.is_generating = False
        self.generate_button.config(state='normal')
        self.progress_var.set(100)

        if success:
            self.update_status("Report generation completed successfully")
            self.log_message("Report generation completed successfully", "success")

            # Show results
            message = "Reports generated successfully!\n\n"
            message += f"Generated {len(results)} report(s):\n\n"
            for result in results:
                message += f"• {os.path.basename(result)}\n"

            messagebox.showinfo("Success", message)

            # Ask to open reports folder
            if messagebox.askyesno("Open Reports", "Would you like to open the reports folder?"):
                self.open_reports_folder()
        else:
            self.update_status("Report generation failed")
            self.log_message("Report generation failed", "error")

            error_message = "Report generation failed with errors:\n\n"
            for error in results:
                error_message += f"• {error}\n"

            messagebox.showerror("Error", error_message)

    def _report_generation_error(self, error_message):
        """Handle report generation error"""
        self.is_generating = False
        self.generate_button.config(state='normal')
        self.update_status(f"Error: {error_message}")
        self.log_message(f"Report generation error: {error_message}", "error")
        messagebox.showerror("Error", f"Report generation failed: {error_message}")

    def preview_data(self):
        """Preview data untuk selected estate"""
        selected_estates = self.get_selected_estates()
        if len(selected_estates) != 1:
            messagebox.showwarning("Select One Estate", "Please select exactly one estate for preview")
            return

        estate = selected_estates[0]
        start_date = self.start_date_entry.get_date().strftime('%Y-%m-%d')
        end_date = self.end_date_entry.get_date().strftime('%Y-%m-%d')

        self.update_status("Previewing data...")
        self.log_message(f"Previewing data for {estate}", "info")

        try:
            # Initialize report generator if needed
            if not self.report_generator:
                self.report_generator = ExcelReportGenerator(
                    template_path=self.template_path_var.get(),
                    formula_path=self.formula_path_var.get(),
                    estate_config_path=self.estate_config_var.get()
                )

            preview = self.report_generator.preview_data(estate, start_date, end_date)

            if 'error' in preview:
                messagebox.showerror("Preview Error", preview['error'])
            else:
                self.log_message("Data preview completed successfully", "success")
                messagebox.showinfo("Preview Result", f"Connection: {'Success' if preview['connection_test'] else 'Failed'}\nSample records: {len(preview['sample_data']['daily_performance'])}")

        except Exception as e:
            messagebox.showerror("Preview Error", f"Error previewing data: {e}")
            self.log_message(f"Preview error: {e}", "error")

        self.update_status("Ready")

    def open_reports_folder(self):
        """Open reports folder"""
        output_dir = self.output_dir_var.get()
        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            messagebox.showwarning("Folder Not Found", f"Reports folder not found: {output_dir}")

    def update_status(self, message):
        """Update status label"""
        self.status_var.set(message)
        self.root.update_idletasks()

    def log_message(self, message, level="info"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_entry, level)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

        # Also log to file
        if level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)
        else:
            self.logger.info(message)

def main():
    """Main function untuk run GUI"""
    root = tk.Tk()
    app = MultiEstateFFBAnalysisGUI(root)

    # Handle window closing
    def on_closing():
        if app.is_generating:
            if messagebox.askokcancel("Quit", "Report generation is in progress. Are you sure you want to quit?"):
                root.destroy()
        else:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Run GUI
    root.mainloop()

if __name__ == "__main__":
    main()