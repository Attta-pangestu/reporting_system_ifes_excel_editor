#!/usr/bin/env python3
"""
Template-Based Report Generator System
Main GUI Application

Sistem generator report berbasis template dengan antarmuka GUI yang memungkinkan:
- Pemilihan database target
- Tes koneksi database
- Seleksi template report
- Generate report berdasarkan template

Author: AI Assistant
Date: 2025-10-31
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import sys
from pathlib import Path
import threading
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from template_manager import TemplateManager
from report_processor import ReportProcessor
from database_connector import DatabaseConnector
from config_manager import ConfigManager
from validator import TemplateValidator

class TemplateReportGeneratorApp:
    def __init__(self, root):
        """Initialize the main application"""
        self.root = root
        self.root.title("Template-Based Report Generator System")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Initialize components
        self.template_manager = TemplateManager()
        self.report_processor = ReportProcessor()
        self.db_connector = None
        self.config_manager = ConfigManager()
        self.validator = TemplateValidator()
        
        # Variables
        self.selected_db_path = tk.StringVar()
        self.connection_status = tk.StringVar(value="Tidak Terhubung")
        self.selected_template = tk.StringVar()
        
        # Setup GUI
        self.setup_gui()
        self.refresh_templates()
        
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Template-Based Report Generator", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Database Selection Section
        self.setup_database_section(main_frame, row=1)
        
        # Template Selection Section
        self.setup_template_section(main_frame, row=2)
        
        # Report Generation Section
        self.setup_generation_section(main_frame, row=3)
        
        # Status and Log Section
        self.setup_status_section(main_frame, row=4)
        
    def setup_database_section(self, parent, row):
        """Setup database selection and connection section"""
        # Database frame
        db_frame = ttk.LabelFrame(parent, text="1. Konfigurasi Database", padding="10")
        db_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        db_frame.columnconfigure(1, weight=1)
        
        # Database path selection
        ttk.Label(db_frame, text="Path Database:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        db_entry = ttk.Entry(db_frame, textvariable=self.selected_db_path, width=50)
        db_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(db_frame, text="Browse", command=self.browse_database)
        browse_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Connection test
        ttk.Label(db_frame, text="Status Koneksi:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        status_label = ttk.Label(db_frame, textvariable=self.connection_status, 
                                foreground="red", font=('Arial', 9, 'bold'))
        status_label.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        test_btn = ttk.Button(db_frame, text="Test Koneksi", command=self.test_connection)
        test_btn.grid(row=1, column=2, pady=(10, 0))
        
    def setup_template_section(self, parent, row):
        """Setup template selection section"""
        # Template frame
        template_frame = ttk.LabelFrame(parent, text="2. Pilih Template Report", padding="10")
        template_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        template_frame.columnconfigure(1, weight=1)
        
        # Template selection
        ttk.Label(template_frame, text="Template Tersedia:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.template_combo = ttk.Combobox(template_frame, textvariable=self.selected_template, 
                                          state="readonly", width=40)
        self.template_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        refresh_btn = ttk.Button(template_frame, text="Refresh", command=self.refresh_templates)
        refresh_btn.grid(row=0, column=2)
        
        validate_btn = ttk.Button(template_frame, text="Validate", command=self.validate_template)
        validate_btn.grid(row=0, column=3, padx=(5, 0))
        
        # Template info
        self.template_info = tk.Text(template_frame, height=4, width=60, wrap=tk.WORD)
        self.template_info.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Scrollbar for template info
        info_scrollbar = ttk.Scrollbar(template_frame, orient="vertical", command=self.template_info.yview)
        info_scrollbar.grid(row=1, column=3, sticky=(tk.N, tk.S), pady=(10, 0))
        self.template_info.configure(yscrollcommand=info_scrollbar.set)
        
        # Bind template selection event
        self.template_combo.bind('<<ComboboxSelected>>', self.on_template_selected)
        
    def setup_generation_section(self, parent, row):
        """Setup report generation section"""
        # Generation frame
        gen_frame = ttk.LabelFrame(parent, text="3. Generate Report", padding="10")
        gen_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        gen_frame.columnconfigure(0, weight=1)
        
        # Generation options
        options_frame = ttk.Frame(gen_frame)
        options_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        ttk.Label(options_frame, text="Output Folder:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.output_path = tk.StringVar(value=os.getcwd())
        output_entry = ttk.Entry(options_frame, textvariable=self.output_path, width=40)
        output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        output_browse_btn = ttk.Button(options_frame, text="Browse", command=self.browse_output_folder)
        output_browse_btn.grid(row=0, column=2)
        
        # Generate button
        self.generate_btn = ttk.Button(gen_frame, text="Generate Report", 
                                      command=self.generate_report, style="Accent.TButton")
        self.generate_btn.grid(row=1, column=0, pady=(10, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(gen_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def setup_status_section(self, parent, row):
        """Setup status and log section"""
        # Status frame
        status_frame = ttk.LabelFrame(parent, text="Status dan Log", padding="10")
        status_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # Log text area
        self.log_text = tk.Text(status_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for log
        log_scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Clear log button
        clear_btn = ttk.Button(status_frame, text="Clear Log", command=self.clear_log)
        clear_btn.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
    def browse_database(self):
        """Browse for database file"""
        file_path = filedialog.askopenfilename(
            title="Pilih File Database",
            filetypes=[("Firebird Database", "*.fdb"), ("All Files", "*.*")]
        )
        if file_path:
            self.selected_db_path.set(file_path)
            self.log_message(f"Database dipilih: {file_path}")
            
    def browse_output_folder(self):
        """Browse for output folder"""
        folder_path = filedialog.askdirectory(title="Pilih Folder Output")
        if folder_path:
            self.output_path.set(folder_path)
            self.log_message(f"Output folder: {folder_path}")
            
    def test_connection(self):
        """Test database connection"""
        if not self.selected_db_path.get():
            messagebox.showwarning("Peringatan", "Silakan pilih file database terlebih dahulu!")
            return
            
        try:
            self.log_message("Menguji koneksi database...")
            self.db_connector = DatabaseConnector(self.selected_db_path.get())
            
            if self.db_connector.test_connection():
                self.connection_status.set("Terhubung")
                self.log_message("✓ Koneksi database berhasil!")
                # Update status label color
                for child in self.root.winfo_children():
                    self.update_status_color(child, "green")
            else:
                self.connection_status.set("Gagal Terhubung")
                self.log_message("✗ Koneksi database gagal!")
                self.update_status_color(self.root, "red")
                
        except Exception as e:
            self.connection_status.set("Error")
            self.log_message(f"✗ Error koneksi: {str(e)}")
            self.update_status_color(self.root, "red")
            
    def update_status_color(self, widget, color):
        """Update status label color recursively"""
        try:
            if hasattr(widget, 'cget') and widget.cget('textvariable') == str(self.connection_status):
                widget.configure(foreground=color)
        except:
            pass
        
        for child in widget.winfo_children():
            self.update_status_color(child, color)
            
    def refresh_templates(self):
        """Refresh available templates"""
        try:
            templates = self.template_manager.get_available_templates()
            template_names = [t['name'] for t in templates]
            
            self.template_combo['values'] = template_names
            
            if template_names:
                self.template_combo.set(template_names[0])
                self.on_template_selected(None)
                
            self.log_message(f"Template dimuat: {len(template_names)} template tersedia")
            
        except Exception as e:
            self.log_message(f"Error memuat template: {str(e)}")
            
    def on_template_selected(self, event):
        """Handle template selection"""
        template_name = self.selected_template.get()
        if not template_name:
            return
            
        try:
            template_info = self.template_manager.get_template_info(template_name)
            
            # Display template information
            self.template_info.delete(1.0, tk.END)
            info_text = f"Template: {template_info['name']}\n"
            info_text += f"Deskripsi: {template_info.get('description', 'Tidak ada deskripsi')}\n"
            info_text += f"File Excel: {template_info['excel_file']}\n"
            info_text += f"File JSON: {template_info['json_file']}\n"
            info_text += f"Queries: {len(template_info.get('queries', []))} query\n"
            info_text += f"Transformations: {len(template_info.get('transformations', []))} transformasi"
            
            self.template_info.insert(1.0, info_text)
            
        except Exception as e:
            self.log_message(f"Error memuat info template: {str(e)}")
            
    def generate_report(self):
        """Generate report based on selected template"""
        # Validation
        if not self.selected_db_path.get():
            messagebox.showwarning("Peringatan", "Silakan pilih database terlebih dahulu!")
            return
            
        if not self.selected_template.get():
            messagebox.showwarning("Peringatan", "Silakan pilih template terlebih dahulu!")
            return
            
        if self.connection_status.get() != "Terhubung":
            messagebox.showwarning("Peringatan", "Pastikan koneksi database berhasil!")
            return
            
        # Start generation in separate thread
        self.generate_btn.configure(state="disabled")
        self.progress.start()
        
        thread = threading.Thread(target=self._generate_report_thread)
        thread.daemon = True
        thread.start()
        
    def _generate_report_thread(self):
        """Generate report in separate thread"""
        try:
            self.log_message("Memulai proses generate report...")
            
            # Get template info
            template_info = self.template_manager.get_template_info(self.selected_template.get())
            
            # Process report
            output_file = self.report_processor.generate_report(
                template_info=template_info,
                db_connector=self.db_connector,
                output_path=self.output_path.get()
            )
            
            # Update UI in main thread
            self.root.after(0, self._generation_complete, output_file)
            
        except Exception as e:
            self.root.after(0, self._generation_error, str(e))
            
    def _generation_complete(self, output_file):
        """Handle successful report generation"""
        self.progress.stop()
        self.generate_btn.configure(state="normal")
        
        self.log_message(f"✓ Report berhasil dibuat: {output_file}")
        
        # Ask to open file
        if messagebox.askyesno("Sukses", f"Report berhasil dibuat!\n\n{output_file}\n\nBuka file sekarang?"):
            try:
                os.startfile(output_file)
            except Exception as e:
                self.log_message(f"Error membuka file: {str(e)}")
                
    def _generation_error(self, error_msg):
        """Handle report generation error"""
        self.progress.stop()
        self.generate_btn.configure(state="normal")
        
        self.log_message(f"✗ Error generate report: {error_msg}")
        messagebox.showerror("Error", f"Gagal membuat report:\n\n{error_msg}")
        
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
    def clear_log(self):
        """Clear log text"""
        self.log_text.delete(1.0, tk.END)
        
    def validate_template(self):
        """Validate selected template"""
        try:
            template_name = self.selected_template.get()
            if not template_name:
                messagebox.showwarning("Peringatan", "Silakan pilih template untuk divalidasi")
                return
                
            self.log_message(f"Memvalidasi template: {template_name}")
            
            # Load template
            template_info = self.template_manager.get_template_info(template_name)
            if not template_info:
                messagebox.showerror("Error", f"Gagal memuat template: {template_name}")
                return
                
            # Perform validation
            validation_results = self.validator.validate_template(template_info, self.db_connector)
            
            # Generate validation report
            report = self.validator.generate_validation_report(validation_results)
            
            # Show validation results in a new window
            self.show_validation_results(template_name, report, validation_results)
            
        except Exception as e:
            self.log_message(f"Error validasi template: {str(e)}")
            messagebox.showerror("Error", f"Validasi template gagal: {str(e)}")
            
    def show_validation_results(self, template_name: str, report: str, results: dict):
        """Show validation results in a new window"""
        try:
            # Create validation results window
            validation_window = tk.Toplevel(self.root)
            validation_window.title(f"Hasil Validasi Template - {template_name}")
            validation_window.geometry("800x600")
            
            # Create main frame with scrollbar
            main_frame = ttk.Frame(validation_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Status frame
            status_frame = ttk.Frame(main_frame)
            status_frame.pack(fill=tk.X, pady=(0, 10))
            
            error_count = len(results.get("errors", []))
            warning_count = len(results.get("warnings", []))
            
            if error_count == 0:
                status_label = ttk.Label(status_frame, text="✓ VALIDASI BERHASIL", 
                                       foreground="green", font=("Arial", 12, "bold"))
            else:
                status_label = ttk.Label(status_frame, text="✗ VALIDASI GAGAL", 
                                       foreground="red", font=("Arial", 12, "bold"))
            status_label.pack(side=tk.LEFT)
            
            # Summary
            summary_text = f"Error: {error_count}, Warning: {warning_count}"
            summary_label = ttk.Label(status_frame, text=summary_text)
            summary_label.pack(side=tk.RIGHT)
            
            # Report text area
            text_frame = ttk.Frame(main_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Insert report
            text_widget.insert(tk.END, report)
            text_widget.config(state=tk.DISABLED)
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(buttons_frame, text="Tutup", 
                      command=validation_window.destroy).pack(side=tk.RIGHT, padx=5)
            
            if error_count == 0:
                ttk.Button(buttons_frame, text="Generate Report", 
                          command=lambda: self.generate_report_from_validation(template_name, validation_window)).pack(side=tk.RIGHT, padx=5)
                          
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menampilkan hasil validasi: {str(e)}")
            
    def generate_report_from_validation(self, template_name: str, validation_window):
        """Generate report after successful validation"""
        try:
            validation_window.destroy()
            # Set the template selection
            self.selected_template.set(template_name)
            self.on_template_selected(None)
            # Trigger report generation
            self.generate_report()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal generate report: {str(e)}")

def main():
    """Main function"""
    root = tk.Tk()
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')
    
    app = TemplateReportGeneratorApp(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()