#!/usr/bin/env python3
"""
GUI Application untuk Excel Report Generator
Menggunakan template Excel yang fleksibel untuk menghasilkan laporan dari database Firebird
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import pandas as pd
import os
from datetime import datetime, date
import threading
import json
from report_generator import ReportGenerator
from firebird_connector import FirebirdConnector

class ExcelReportGeneratorGUI:
    CONFIG_FILE = "config.json"
    
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Report Generator - Multi-Estate")
        self.root.geometry("1200x900")
        self.root.configure(bg='#f0f0f0')
        
        self.ESTATES = self.load_config()
        self.report_generator = ReportGenerator()
        
        self.setup_ui()
    
    def load_config(self):
        """Memuat konfigurasi dari file JSON."""
        default_estates = {
            "PGE 1A": r"C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB",
            "PGE 1B": r"C:\Users\nbgmf\Downloads\PTRJ_P1B\PTRJ_P1B.FDB", 
            "PGE 2A": r"C:\Users\nbgmf\Downloads\IFESS_PGE_2A_19-06-2025",
            "PGE 2B": r"C:\Users\nbgmf\Downloads\IFESS_2B_19-06-2025\PTRJ_P2B.FDB",
            "IJL": r"C:\Users\nbgmf\Downloads\IFESS_IJL_19-06-2025\PTRJ_IJL_IMPIANJAYALESTARI.FDB",
            "DME": r"C:\Users\nbgmf\Downloads\IFESS_DME_19-06-2025\PTRJ_DME.FDB",
            "Are B2": r"C:\Users\nbgmf\Downloads\IFESS_ARE_B2_19-06-2025\PTRJ_AB2.FDB",
            "Are B1": r"C:\Users\nbgmf\Downloads\IFESS_ARE_B1_19-06-2025\PTRJ_AB1.FDB",
            "Are A": r"C:\Users\nbgmf\Downloads\IFESS_ARE_A_19-06-2025\PTRJ_ARA.FDB",
            "Are C": r"C:\Users\nbgmf\Downloads\IFESS_ARE_C_19-06-2025\PTRJ_ARC.FDB"
        }
        
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('estates', default_estates)
            except Exception as e:
                messagebox.showwarning("Config Warning", f"Error loading config: {e}\nUsing default settings.")
                return default_estates
        else:
            self.save_config({'estates': default_estates})
            return default_estates
    
    def save_config(self, data_to_save=None):
        """Menyimpan konfigurasi ke file JSON."""
        if data_to_save is None:
            data_to_save = {'estates': self.ESTATES}
        
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Config Error", f"Error saving config: {e}")
    
    def setup_ui(self):
        """Setup user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Excel Report Generator", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Template and Formula Files Section
        files_frame = ttk.LabelFrame(main_frame, text="Template & Formula Files", padding="10")
        files_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        files_frame.columnconfigure(1, weight=1)
        
        # Template file
        ttk.Label(files_frame, text="Excel Template:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.template_path_var = tk.StringVar(value="sample_template.xlsx")
        template_entry = ttk.Entry(files_frame, textvariable=self.template_path_var, width=50)
        template_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(files_frame, text="Browse", 
                  command=self.browse_template_file).grid(row=0, column=2)
        
        # Formula file
        ttk.Label(files_frame, text="Formula File:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.formula_path_var = tk.StringVar(value="sample_formula.json")
        formula_entry = ttk.Entry(files_frame, textvariable=self.formula_path_var, width=50)
        formula_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(files_frame, text="Browse", 
                  command=self.browse_formula_file).grid(row=1, column=2, pady=(10, 0))
        
        # Date Selection Section
        date_frame = ttk.LabelFrame(main_frame, text="Date Range", padding="10")
        date_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.start_date = DateEntry(date_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_date.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(date_frame, text="End Date:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.end_date = DateEntry(date_frame, width=12, background='darkblue',
                                 foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.end_date.grid(row=0, column=3, padx=(0, 20))
        
        # Estate Selection Section
        estate_frame = ttk.LabelFrame(main_frame, text="Estate Selection", padding="10")
        estate_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        estate_frame.columnconfigure(0, weight=1)
        
        # Estate selection buttons
        button_frame = ttk.Frame(estate_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(button_frame, text="Select All", 
                  command=self.select_all_estates).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear Selection", 
                  command=self.clear_estate_selection).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Change DB Path", 
                  command=self.change_db_path).pack(side=tk.LEFT)
        
        # Estate tree
        tree_frame = ttk.Frame(estate_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        self.estate_tree = ttk.Treeview(tree_frame, columns=('path',), height=8)
        self.estate_tree.heading('#0', text='Estate Name')
        self.estate_tree.heading('path', text='Database Path')
        self.estate_tree.column('#0', width=150)
        self.estate_tree.column('path', width=400)
        
        # Scrollbar for tree
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.estate_tree.yview)
        self.estate_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.estate_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.populate_estate_tree()
        
        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="10")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.output_dir_var = tk.StringVar(value="output")
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=50)
        output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(output_frame, text="Browse", 
                  command=self.browse_output_dir).grid(row=0, column=2)
        
        # Control Buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=3, pady=(20, 0))
        
        self.generate_button = ttk.Button(control_frame, text="Generate Reports", 
                                         command=self.start_generation, style='Accent.TButton')
        self.generate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="Clear Results", 
                  command=self.clear_results).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="Open Output Folder", 
                  command=self.open_output_folder).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Results text area
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = tk.Text(results_frame, height=15, wrap=tk.WORD)
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure main frame row weights
        main_frame.rowconfigure(7, weight=1)
    
    def browse_template_file(self):
        """Browse for Excel template file."""
        filename = filedialog.askopenfilename(
            title="Select Excel Template",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.template_path_var.set(filename)
    
    def browse_formula_file(self):
        """Browse for formula definition file."""
        filename = filedialog.askopenfilename(
            title="Select Formula File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.formula_path_var.set(filename)
    
    def browse_output_dir(self):
        """Browse for output directory."""
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_dir_var.set(dirname)
    
    def populate_estate_tree(self):
        """Populate estate tree with current estates."""
        for item in self.estate_tree.get_children():
            self.estate_tree.delete(item)
        
        for estate_name, db_path in self.ESTATES.items():
            self.estate_tree.insert('', 'end', text=estate_name, values=(db_path,))
    
    def change_db_path(self):
        """Change database path for selected estate."""
        selected = self.estate_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an estate first.")
            return
        
        item = selected[0]
        estate_name = self.estate_tree.item(item, 'text')
        current_path = self.estate_tree.item(item, 'values')[0]
        
        new_path = filedialog.askopenfilename(
            title=f"Select database for {estate_name}",
            initialdir=os.path.dirname(current_path) if current_path else "",
            filetypes=[("Firebird Database", "*.fdb"), ("All files", "*.*")]
        )
        
        if new_path:
            self.ESTATES[estate_name] = new_path
            self.estate_tree.item(item, values=(new_path,))
            self.save_config()
    
    def select_all_estates(self):
        """Select all estates."""
        for item in self.estate_tree.get_children():
            self.estate_tree.selection_add(item)
    
    def clear_estate_selection(self):
        """Clear estate selection."""
        self.estate_tree.selection_remove(self.estate_tree.selection())
    
    def start_generation(self):
        """Start report generation in a separate thread."""
        selected_estates = self.estate_tree.selection()
        if not selected_estates:
            messagebox.showwarning("Warning", "Please select at least one estate.")
            return
        
        template_path = self.template_path_var.get()
        formula_path = self.formula_path_var.get()
        
        if not template_path or not os.path.exists(template_path):
            messagebox.showerror("Error", "Please select a valid Excel template file.")
            return
        
        if not formula_path or not os.path.exists(formula_path):
            messagebox.showerror("Error", "Please select a valid formula file.")
            return
        
        # Disable generate button
        self.generate_button.config(state='disabled')
        self.progress_var.set(0)
        
        # Start generation in separate thread
        thread = threading.Thread(target=self.run_generation, daemon=True)
        thread.start()
    
    def run_generation(self):
        """Run report generation process."""
        try:
            selected_estates = self.estate_tree.selection()
            total_estates = len(selected_estates)
            
            template_path = self.template_path_var.get()
            formula_path = self.formula_path_var.get()
            output_dir = self.output_dir_var.get()
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            self.log_message(f"Starting report generation for {total_estates} estates...")
            self.log_message(f"Date range: {start_date} to {end_date}")
            self.log_message(f"Template: {template_path}")
            self.log_message(f"Formula: {formula_path}")
            self.log_message("-" * 50)
            
            for i, item in enumerate(selected_estates):
                estate_name = self.estate_tree.item(item, 'text')
                db_path = self.estate_tree.item(item, 'values')[0]
                
                self.log_message(f"Processing {estate_name}...")
                
                try:
                    # Generate report for this estate
                    output_filename = f"{estate_name}_Report_{start_date}_{end_date}.xlsx"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    # Prepare context data for the report
                    context_data = {
                        'estate_name': estate_name,
                        'start_date': start_date,
                        'end_date': end_date,
                        'db_path': db_path
                    }
                    
                    # Generate the report
                    self.report_generator.generate_report(
                        template_path=template_path,
                        formula_path=formula_path,
                        output_path=output_path,
                        context_data=context_data
                    )
                    
                    self.log_message(f"✓ {estate_name} report generated: {output_filename}")
                    
                except Exception as e:
                    self.log_message(f"✗ Error processing {estate_name}: {str(e)}")
                
                # Update progress
                progress = ((i + 1) / total_estates) * 100
                self.progress_var.set(progress)
            
            self.log_message("-" * 50)
            self.log_message("Report generation completed!")
            
        except Exception as e:
            self.log_message(f"Error during generation: {str(e)}")
        
        finally:
            # Re-enable generate button
            self.root.after(0, lambda: self.generate_button.config(state='normal'))
    
    def log_message(self, message):
        """Log message to results text area."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        def update_text():
            self.results_text.insert(tk.END, formatted_message)
            self.results_text.see(tk.END)
        
        self.root.after(0, update_text)
    
    def clear_results(self):
        """Clear results text area."""
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set(0)
    
    def open_output_folder(self):
        """Open output folder in file explorer."""
        output_dir = self.output_dir_var.get()
        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            messagebox.showwarning("Warning", "Output directory does not exist.")

def main():
    root = tk.Tk()
    app = ExcelReportGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()