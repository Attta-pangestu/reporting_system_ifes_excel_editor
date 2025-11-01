"""
Report Generator UI Dialog
Dialog untuk generate report dengan parameter
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ReportGeneratorDialog:
    """Dialog untuk generate report"""

    def __init__(self, parent, database_connector, template_processor, formula_engine, output_format: str = "excel"):
        """
        Inisialisasi Report Generator Dialog

        Args:
            parent: Parent window
            database_connector: Database connector instance
            template_processor: Template processor instance
            formula_engine: Formula engine instance
            output_format: Format output ("excel" atau "pdf")
        """
        self.parent = parent
        self.database_connector = database_connector
        self.template_processor = template_processor
        self.formula_engine = formula_engine
        self.output_format = output_format

        self.dialog = None
        self.result_path = None

    def show(self) -> Optional[str]:
        """
        Tampilkan dialog dan return result

        Returns:
            Path ke file yang di-generate atau None jika dibatalkan
        """
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Generate {'Excel' if self.output_format == 'excel' else 'PDF'} Report")
        self.dialog.geometry("600x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        self._setup_ui()
        self._set_defaults()

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.dialog.wait_window()
        return self.result_path

    def _setup_ui(self):
        """Setup UI components"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text=f"Generate {'Excel' if self.output_format == 'excel' else 'PDF'} Report",
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        # Parameters section
        param_frame = ttk.LabelFrame(main_frame, text="Report Parameters", padding="10")
        param_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        param_frame.columnconfigure(1, weight=1)
        param_frame.columnconfigure(3, weight=1)

        # Date range
        ttk.Label(param_frame, text="Start Date:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.start_date_var = tk.StringVar()
        start_date_entry = ttk.Entry(param_frame, textvariable=self.start_date_var, width=15)
        start_date_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=(0, 5))

        ttk.Label(param_frame, text="End Date:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.end_date_var = tk.StringVar()
        end_date_entry = ttk.Entry(param_frame, textvariable=self.end_date_var, width=15)
        end_date_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 10), pady=(0, 5))

        # Output settings
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="10")
        output_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        output_frame.columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="File Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.filename_var = tk.StringVar()
        filename_entry = ttk.Entry(output_frame, textvariable=self.filename_var, width=40)
        filename_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 5))

        ttk.Label(output_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.output_dir_var = tk.StringVar()
        output_dir_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=40)
        output_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self._browse_output_dir).grid(row=1, column=2, padx=(0, 0), pady=(0, 5))

        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        self.open_file_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Open file after generation", variable=self.open_file_var).grid(row=0, column=0, sticky=tk.W)

        if self.output_format == "pdf":
            self.pdf_settings_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(options_frame, text="Use PDF settings from formula", variable=self.pdf_settings_var).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.StringVar(value="Ready to generate report")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.E, tk.W), pady=(10, 0))

        ttk.Button(button_frame, text="Generate Report", command=self._generate_report).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self._cancel).grid(row=0, column=1)

    def _set_defaults(self):
        """Set default values"""
        # Set default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.output_format == "excel":
            self.filename_var.set(f"FFB_Report_{timestamp}.xlsx")
        else:
            self.filename_var.set(f"FFB_Report_{timestamp}.pdf")

        # Set default output directory
        self.output_dir_var.set(os.getcwd())

        # Set default date range (current month)
        today = datetime.now()
        first_day = today.replace(day=1)
        self.start_date_var.set(first_day.strftime("%Y-%m-%d"))
        self.end_date_var.set(today.strftime("%Y-%m-%d"))

    def _browse_output_dir(self):
        """Browse untuk output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)

    def _generate_report(self):
        """Generate report"""
        try:
            # Update UI
            self.progress_var.set("Starting report generation...")
            self.progress_bar.start(10)
            self.dialog.update()

            # Get parameters
            parameters = {
                'start_date': self.start_date_var.get() or None,
                'end_date': self.end_date_var.get() or None
            }

            # Validate filename and directory
            filename = self.filename_var.get().strip()
            output_dir = self.output_dir_var.get().strip()

            if not filename:
                messagebox.showerror("Error", "Please enter a file name")
                return

            if not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot create output directory: {e}")
                    return

            # Ensure correct extension
            if self.output_format == "excel" and not filename.lower().endswith(('.xlsx', '.xls')):
                filename += '.xlsx'
            elif self.output_format == "pdf" and not filename.lower().endswith('.pdf'):
                filename += '.pdf'

            output_path = os.path.join(output_dir, filename)

            # Check if file exists
            if os.path.exists(output_path):
                if not messagebox.askyesno("File Exists", f"File already exists:\n{output_path}\n\nOverwrite?"):
                    return

            self.progress_var.set("Executing database queries...")
            self.dialog.update()

            # Set database connector to formula engine
            self.formula_engine.database_connector = self.database_connector

            # Execute queries
            query_results = self.formula_engine.execute_queries(parameters)

            # Check if we have data
            if not any(query_results.values()):
                if not messagebox.askyesno("No Data", "No data found for the specified parameters.\n\nGenerate empty report anyway?"):
                    return

            self.progress_var.set("Processing variables...")
            self.dialog.update()

            # Process variables
            variables = self.formula_engine.process_variables(query_results, parameters)

            self.progress_var.set("Processing template...")
            self.dialog.update()

            # Create template processor copy
            template_copy = self.template_processor.create_copy()

            # Replace placeholders
            template_copy.replace_placeholders(variables)

            # Process repeating sections
            main_data = query_results.get('main_data', [])
            if main_data:
                sections = template_copy.find_repeating_sections()
                for section_name, section_config in sections.items():
                    template_copy.process_repeating_sections(main_data, section_config)

            self.progress_var.set(f"Saving {'Excel' if self.output_format == 'excel' else 'PDF'} file...")
            self.dialog.update()

            if self.output_format == "excel":
                # Save Excel file
                template_copy.save_template(output_path)
                self.result_path = output_path

            else:
                # Save temporary Excel file first
                temp_excel_path = output_path.replace('.pdf', '_temp.xlsx')
                template_copy.save_template(temp_excel_path)

                self.progress_var.set("Converting to PDF...")
                self.dialog.update()

                # Convert to PDF
                from utils.pdf_generator import PDFGenerator
                pdf_generator = PDFGenerator()

                # Get PDF settings if available
                pdf_settings = None
                if self.pdf_settings_var.get():
                    pdf_settings = self.formula_engine.get_output_settings().get('pdf_settings', {})

                # Convert to PDF
                self.result_path = pdf_generator.convert_to_pdf(temp_excel_path, output_path, pdf_settings)

                # Remove temporary Excel file
                try:
                    os.remove(temp_excel_path)
                except:
                    pass

            self.progress_var.set("Report generation completed!")
            self.progress_bar.stop()
            self.dialog.update()

            # Show success message
            messagebox.showinfo("Success", f"{'Excel' if self.output_format == 'excel' else 'PDF'} report generated successfully:\n{self.result_path}")

            # Open file if requested
            if self.open_file_var.get():
                try:
                    os.startfile(self.result_path)
                except Exception as e:
                    logger.warning(f"Cannot open file: {e}")

            # Close dialog
            self.dialog.destroy()

        except Exception as e:
            self.progress_var.set(f"Error: {e}")
            self.progress_bar.stop()
            logger.error(f"Error generating report: {e}")
            messagebox.showerror("Error", f"Error generating report:\n{e}")

    def _cancel(self):
        """Tutup dialog"""
        if self.result_path is None:
            self.dialog.destroy()