"""
Data Preview Window
Jendela untuk preview data dari query
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DataPreviewWindow:
    """Jendela preview data"""

    def __init__(self, parent, database_connector, formula_engine, parameters: Dict[str, Any]):
        """
        Inisialisasi Data Preview Window

        Args:
            parent: Parent window
            database_connector: Database connector instance
            formula_engine: Formula engine instance
            parameters: Query parameters
        """
        self.parent = parent
        self.database_connector = database_connector
        self.formula_engine = formula_engine
        self.parameters = parameters

        self.window = None
        self.tree = None
        self.data = {}

    def show(self):
        """Tampilkan jendela preview"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Data Preview")
        self.window.geometry("1000x600")
        self.window.transient(self.parent)
        self.window.grab_set()

        self._setup_ui()
        self._load_data()

        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

    def _setup_ui(self):
        """Setup UI components"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Data Preview", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # Query selector
        query_frame = ttk.Frame(main_frame)
        query_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        query_frame.columnconfigure(1, weight=1)

        ttk.Label(query_frame, text="Query:").grid(row=0, column=0, padx=(0, 10))
        self.query_var = tk.StringVar()
        self.query_combo = ttk.Combobox(query_frame, textvariable=self.query_var, state="readonly")
        self.query_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.query_combo.bind("<<ComboboxSelected>>", self._on_query_selected)

        ttk.Button(query_frame, text="Refresh", command=self._refresh_data).grid(row=0, column=2)

        # Data display
        data_frame = ttk.LabelFrame(main_frame, text="Data Results", padding="5")
        data_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)

        # Treeview with scrollbar
        tree_frame = ttk.Frame(data_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame)
        tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)

        self.tree.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Status bar
        self.status_label = ttk.Label(data_frame, text="Loading...")
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Button(button_frame, text="Export to CSV", command=self._export_csv).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=self.window.destroy).grid(row=0, column=1)

    def _load_data(self):
        """Load data dari database"""
        try:
            # Set database connector to formula engine
            self.formula_engine.database_connector = self.database_connector

            # Execute queries
            self.data = self.formula_engine.execute_queries(self.parameters)

            # Populate query combo
            query_names = list(self.data.keys())
            self.query_combo['values'] = query_names

            if query_names:
                self.query_combo.set(query_names[0])
                self._display_query_data(query_names[0])

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            messagebox.showerror("Error", f"Error loading data: {e}")
            self.status_label.config(text=f"Error: {e}")

    def _on_query_selected(self, event):
        """Handle query selection"""
        query_name = self.query_var.get()
        if query_name:
            self._display_query_data(query_name)

    def _display_query_data(self, query_name: str):
        """Display data dari query tertentu"""
        try:
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)

            query_result = self.data.get(query_name)

            if not query_result:
                self.status_label.config(text=f"No data for query: {query_name}")
                return

            # Handle different result formats
            if isinstance(query_result, list) and len(query_result) > 0:
                if isinstance(query_result[0], dict):
                    # List of dictionaries
                    self._display_dict_data(query_result)
                else:
                    # Simple list
                    self._display_list_data(query_result)
            elif isinstance(query_result, dict):
                if 'rows' in query_result and 'headers' in query_result:
                    # Result with headers and rows
                    self._display_table_data(query_result['headers'], query_result['rows'])
                else:
                    # Single dictionary
                    self._display_single_dict(query_result)
            else:
                self.status_label.config(text=f"No displayable data for query: {query_name}")

        except Exception as e:
            logger.error(f"Error displaying data: {e}")
            self.status_label.config(text=f"Error displaying data: {e}")

    def _display_dict_data(self, data: List[Dict]):
        """Display list of dictionaries"""
        if not data:
            return

        # Get all unique keys from all dictionaries
        columns = set()
        for item in data:
            columns.update(item.keys())
        columns = sorted(list(columns))

        # Configure treeview
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'

        # Setup columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50)

        # Add data
        for item in data:
            values = [item.get(col, '') for col in columns]
            self.tree.insert('', tk.END, values=values)

        # Update status
        self.status_label.config(text=f"{len(data)} records, {len(columns)} columns")

    def _display_table_data(self, headers: List[str], rows: List[Dict]):
        """Display tabular data with headers"""
        if not headers or not rows:
            return

        # Configure treeview
        self.tree['columns'] = headers
        self.tree['show'] = 'headings'

        # Setup columns
        for header in headers:
            self.tree.heading(header, text=header)
            self.tree.column(header, width=100, minwidth=50)

        # Add data
        for row in rows:
            values = [row.get(header, '') for header in headers]
            self.tree.insert('', tk.END, values=values)

        # Update status
        self.status_label.config(text=f"{len(rows)} records, {len(headers)} columns")

    def _display_list_data(self, data: List):
        """Display simple list data"""
        # Configure treeview
        self.tree['columns'] = ['Value']
        self.tree['show'] = 'headings'

        # Setup column
        self.tree.heading('Value', text='Value')
        self.tree.column('Value', width=300)

        # Add data
        for item in data:
            self.tree.insert('', tk.END, values=[str(item)])

        # Update status
        self.status_label.config(text=f"{len(data)} items")

    def _display_single_dict(self, data: Dict):
        """Display single dictionary as key-value pairs"""
        # Configure treeview
        self.tree['columns'] = ['Key', 'Value']
        self.tree['show'] = 'headings'

        # Setup columns
        self.tree.heading('Key', text='Key')
        self.tree.heading('Value', text='Value')
        self.tree.column('Key', width=150)
        self.tree.column('Value', width=300)

        # Add data
        for key, value in data.items():
            self.tree.insert('', tk.END, values=[key, str(value)])

        # Update status
        self.status_label.config(text=f"{len(data)} key-value pairs")

    def _refresh_data(self):
        """Refresh data dari database"""
        try:
            self.status_label.config(text="Refreshing data...")
            self.window.update()

            # Set database connector to formula engine
            self.formula_engine.database_connector = self.database_connector

            # Reload data
            self.data = self.formula_engine.execute_queries(self.parameters)

            # Refresh current query display
            current_query = self.query_var.get()
            if current_query:
                self._display_query_data(current_query)

            self.status_label.config(text="Data refreshed")

        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            messagebox.showerror("Error", f"Error refreshing data: {e}")
            self.status_label.config(text=f"Error refreshing data: {e}")

    def _export_csv(self):
        """Export current data ke CSV"""
        try:
            current_query = self.query_var.get()
            if not current_query:
                messagebox.showwarning("Warning", "No query selected")
                return

            query_result = self.data.get(current_query)
            if not query_result:
                messagebox.showwarning("Warning", "No data to export")
                return

            # Convert to DataFrame
            if isinstance(query_result, list) and query_result and isinstance(query_result[0], dict):
                df = pd.DataFrame(query_result)
            elif isinstance(query_result, dict) and 'rows' in query_result:
                df = pd.DataFrame(query_result['rows'])
            else:
                messagebox.showwarning("Warning", "Data format not supported for CSV export")
                return

            # Ask for save location
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                initialfile=f"{current_query}_data.csv"
            )

            if filename:
                df.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Data exported to:\n{filename}")

        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            messagebox.showerror("Error", f"Error exporting CSV: {e}")