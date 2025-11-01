#!/usr/bin/env python3
"""
Enhanced Report Generator GUI with Comprehensive Data Preview
GUI lengkap dengan preview data sebelum rendering ke report
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from datetime import datetime, timedelta
import json
import logging
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from firebird_connector_enhanced import FirebirdConnectorEnhanced
    from template_processor_enhanced import TemplateProcessorEnhanced
    from formula_engine_enhanced import FormulaEngineEnhanced
    from excel_report_generator_enhanced import ExcelReportGeneratorEnhanced
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import required modules: {e}")
    sys.exit(1)

# Setup enhanced logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedReportGUIWithPreview:
    """
    GUI untuk Enhanced Report Generator dengan comprehensive data preview
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Report Generator with Data Preview - PGE 2B")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        # Variables
        self.db_path = tk.StringVar(value=r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB")
        self.template_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.start_date = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        self.end_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        # Status variables
        self.db_connected = tk.BooleanVar(value=False)
        self.db_status_text = tk.StringVar(value="Not Connected")
        self.template_ready = tk.BooleanVar(value=False)

        # Components and data
        self.connector = None
        self.template_processor = None
        self.report_generator = None
        self.query_results = {}
        self.variables = {}
        self.preview_data = {}

        # Setup GUI
        self.setup_gui()

        # Initialize components
        self.initialize_components()

        # Check database connection
        self.check_database_connection()

    def setup_gui(self):
        """Setup GUI components dengan preview functionality"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(3, weight=1)

        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 20))
        title_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(
            title_frame,
            text="Enhanced Report Generator with Data Preview - PGE 2B FFB Analysis",
            font=('Arial', 16, 'bold')
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="Generate Excel reports from Firebird database with comprehensive data preview",
            font=('Arial', 10)
        )
        subtitle_label.pack()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Tab 1: Configuration
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Configuration")
        self.setup_config_tab()

        # Tab 2: Data Preview
        self.preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.preview_frame, text="Data Preview")
        self.setup_preview_tab()

        # Tab 3: Debug Log
        self.debug_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.debug_frame, text="Debug Log")
        self.setup_debug_tab()

        # Action Buttons Frame
        self.create_action_buttons_frame(main_frame)

        # Progress Frame
        self.create_progress_frame(main_frame)

        # Configure row weights
        main_frame.rowconfigure(1, weight=1)

    def setup_config_tab(self):
        """Setup configuration tab"""
        # Database Status Frame
        self.create_database_status_frame(self.config_frame)

        # Template Selection Frame
        self.create_template_selection_frame(self.config_frame)

        # Date Range Frame
        self.create_date_range_frame(self.config_frame)

        # Output Selection Frame
        self.create_output_selection_frame(self.config_frame)

    def setup_preview_tab(self):
        """Setup comprehensive data preview tab"""
        # Create main preview container
        preview_container = ttk.Frame(self.preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Preview Controls Frame
        controls_frame = ttk.LabelFrame(preview_container, text="Preview Controls", padding="10")
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        # Preview buttons
        self.preview_btn = ttk.Button(
            controls_frame,
            text="Load Preview Data",
            command=self.load_comprehensive_preview,
            style="Accent.TButton"
        )
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.refresh_btn = ttk.Button(
            controls_frame,
            text="Refresh Preview",
            command=self.refresh_preview
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.export_btn = ttk.Button(
            controls_frame,
            text="Export Preview to CSV",
            command=self.export_preview_to_csv
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # Status label
        self.preview_status_label = ttk.Label(controls_frame, text="Ready to load preview")
        self.preview_status_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Create paned window for preview content
        preview_paned = ttk.PanedWindow(preview_container, orient=tk.VERTICAL)
        preview_paned.pack(fill=tk.BOTH, expand=True)

        # Top frame for query results
        query_frame = ttk.LabelFrame(preview_paned, text="Query Results", padding="10")
        preview_paned.add(query_frame, weight=1)

        # Query results treeview
        query_columns = ('Query Name', 'Status', 'Rows', 'Execution Time', 'Sample Data')
        self.query_tree = ttk.Treeview(query_frame, columns=query_columns, show='tree headings', height=8)

        # Configure columns
        self.query_tree.heading('#0', text='Query')
        self.query_tree.heading('Query Name', text='Query Name')
        self.query_tree.heading('Status', text='Status')
        self.query_tree.heading('Rows', text='Rows')
        self.query_tree.heading('Execution Time', text='Time (s)')
        self.query_tree.heading('Sample Data', text='Sample Data')

        self.query_tree.column('#0', width=200)
        self.query_tree.column('Query Name', width=150)
        self.query_tree.column('Status', width=80)
        self.query_tree.column('Rows', width=60)
        self.query_tree.column('Execution Time', width=80)
        self.query_tree.column('Sample Data', width=300)

        # Add scrollbars
        query_scroll_y = ttk.Scrollbar(query_frame, orient="vertical", command=self.query_tree.yview)
        query_scroll_x = ttk.Scrollbar(query_frame, orient="horizontal", command=self.query_tree.xview)
        self.query_tree.configure(yscrollcommand=query_scroll_y.set, xscrollcommand=query_scroll_x.set)

        # Pack treeview and scrollbars
        self.query_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        query_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        query_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        query_frame.grid_rowconfigure(0, weight=1)
        query_frame.grid_columnconfigure(0, weight=1)

        # Query detail frame
        query_detail_frame = ttk.Frame(query_frame)
        query_detail_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Label(query_detail_frame, text="Selected Query:").pack(side=tk.LEFT, padx=(0, 5))
        self.selected_query_label = ttk.Label(query_detail_frame, text="None", font=('Arial', 9, 'bold'))
        self.selected_query_label.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(query_detail_frame, text="View Details", command=self.view_query_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(query_detail_frame, text="View SQL", command=self.view_query_sql).pack(side=tk.LEFT, padx=5)

        # Bottom frame for variables
        variables_frame = ttk.LabelFrame(preview_paned, text="Processed Variables", padding="10")
        preview_paned.add(variables_frame, weight=1)

        # Variables treeview
        var_columns = ('Variable Name', 'Value', 'Type', 'Source', 'Status')
        self.var_tree = ttk.Treeview(variables_frame, columns=var_columns, show='tree headings', height=8)

        # Configure columns
        self.var_tree.heading('#0', text='Category')
        self.var_tree.heading('Variable Name', text='Variable Name')
        self.var_tree.heading('Value', text='Value')
        self.var_tree.heading('Type', text='Type')
        self.var_tree.heading('Source', text='Source')
        self.var_tree.heading('Status', text='Status')

        self.var_tree.column('#0', width=150)
        self.var_tree.column('Variable Name', width=150)
        self.var_tree.column('Value', width=250)
        self.var_tree.column('Type', width=80)
        self.var_tree.column('Source', width=120)
        self.var_tree.column('Status', width=80)

        # Add scrollbars for variables
        var_scroll_y = ttk.Scrollbar(variables_frame, orient="vertical", command=self.var_tree.yview)
        var_scroll_x = ttk.Scrollbar(variables_frame, orient="horizontal", command=self.var_tree.xview)
        self.var_tree.configure(yscrollcommand=var_scroll_y.set, xscrollcommand=var_scroll_x.set)

        # Pack variables treeview and scrollbars
        self.var_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        var_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        var_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        variables_frame.grid_rowconfigure(0, weight=1)
        variables_frame.grid_columnconfigure(0, weight=1)

        # Variable detail frame
        var_detail_frame = ttk.Frame(variables_frame)
        var_detail_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Label(var_detail_frame, text="Selected Variable:").pack(side=tk.LEFT, padx=(0, 5))
        self.selected_var_label = ttk.Label(var_detail_frame, text="None", font=('Arial', 9, 'bold'))
        self.selected_var_label.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(var_detail_frame, text="Trace Variable", command=self.trace_variable).pack(side=tk.LEFT, padx=5)

        # Bind selection events
        self.query_tree.bind('<<TreeviewSelect>>', self.on_query_select)
        self.var_tree.bind('<<TreeviewSelect>>', self.on_variable_select)

    def setup_debug_tab(self):
        """Setup debug log tab"""
        # Debug log container
        debug_container = ttk.Frame(self.debug_frame)
        debug_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Debug controls
        controls_frame = ttk.Frame(debug_container)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(controls_frame, text="Clear Log", command=self.clear_debug_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="Save Log", command=self.save_debug_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Filter Errors", command=self.filter_errors).pack(side=tk.LEFT, padx=5)

        # Debug text widget with scrollbar
        debug_frame = ttk.Frame(debug_container)
        debug_frame.pack(fill=tk.BOTH, expand=True)

        self.debug_text = scrolledtext.ScrolledText(
            debug_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            height=20
        )
        self.debug_text.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for coloring
        self.debug_text.tag_configure("info", foreground="black")
        self.debug_text.tag_configure("success", foreground="green")
        self.debug_text.tag_configure("warning", foreground="orange")
        self.debug_text.tag_configure("error", foreground="red")
        self.debug_text.tag_configure("debug", foreground="blue")

    def create_database_status_frame(self, parent):
        """Create database status frame"""
        db_frame = ttk.LabelFrame(parent, text="Database Status", padding="10")
        db_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        db_frame.columnconfigure(1, weight=1)

        # Database path selection
        ttk.Label(db_frame, text="Database Path:").grid(row=0, column=0, sticky=tk.W, pady=2)

        db_path_frame = ttk.Frame(db_frame)
        db_path_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        db_path_frame.columnconfigure(0, weight=1)

        self.db_path_entry = ttk.Entry(db_path_frame, textvariable=self.db_path, width=60)
        self.db_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        browse_db_btn = ttk.Button(db_path_frame, text="Browse", command=self.browse_database)
        browse_db_btn.grid(row=0, column=1)

        # Connection status
        ttk.Label(db_frame, text="Connection Status:").grid(row=1, column=0, sticky=tk.W, pady=2)

        status_frame = ttk.Frame(db_frame)
        status_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        status_frame.columnconfigure(0, weight=1)

        # Status indicator
        self.status_canvas = tk.Canvas(status_frame, width=20, height=20, highlightthickness=0)
        self.status_canvas.grid(row=0, column=0, padx=(0, 10))

        status_text = ttk.Label(status_frame, textvariable=self.db_status_text, font=('Arial', 10, 'bold'))
        status_text.grid(row=0, column=1, sticky=tk.W)

        # Connection buttons
        button_frame = ttk.Frame(db_frame)
        button_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))

        self.connect_btn = ttk.Button(button_frame, text="Connect", command=self.connect_database)
        self.connect_btn.grid(row=0, column=0, padx=(0, 5))

        self.test_btn = ttk.Button(button_frame, text="Test Connection", command=self.test_connection)
        self.test_btn.grid(row=0, column=1, padx=5)

    def create_template_selection_frame(self, parent):
        """Create template selection frame"""
        template_frame = ttk.LabelFrame(parent, text="Template Selection", padding="10")
        template_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        template_frame.columnconfigure(1, weight=1)

        # Template file selection
        ttk.Label(template_frame, text="Template File:").grid(row=0, column=0, sticky=tk.W, pady=2)

        template_path_frame = ttk.Frame(template_frame)
        template_path_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        template_path_frame.columnconfigure(0, weight=1)

        self.template_path_entry = ttk.Entry(template_path_frame, textvariable=self.template_path, width=60)
        self.template_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        browse_template_btn = ttk.Button(template_path_frame, text="Browse", command=self.browse_template)
        browse_template_btn.grid(row=0, column=1)

        # Available templates list
        ttk.Label(template_frame, text="Available Templates:").grid(row=1, column=0, sticky=tk.W, pady=(10, 2))

        list_frame = ttk.Frame(template_frame)
        list_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.templates_listbox = tk.Listbox(list_frame, height=6, yscrollcommand=scrollbar.set)
        self.templates_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.templates_listbox.bind('<<ListboxSelect>>', self.on_template_select)

        scrollbar.config(command=self.templates_listbox.yview)

        # Load templates button
        load_templates_btn = ttk.Button(template_frame, text="Refresh Templates", command=self.load_templates)
        load_templates_btn.grid(row=2, column=0, columnspan=3, pady=(5, 0))

    def create_date_range_frame(self, parent):
        """Create date range selection frame"""
        date_frame = ttk.LabelFrame(parent, text="Date Range", padding="10")
        date_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Start date
        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=2)
        ttk.Entry(date_frame, textvariable=self.start_date, width=15).grid(row=0, column=1, sticky=tk.W, pady=2)

        # End date
        ttk.Label(date_frame, text="End Date:").grid(row=0, column=2, sticky=tk.W, padx=(20, 10), pady=2)
        ttk.Entry(date_frame, textvariable=self.end_date, width=15).grid(row=0, column=3, sticky=tk.W, pady=2)

        # Quick date range buttons
        quick_frame = ttk.Frame(date_frame)
        quick_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Label(quick_frame, text="Quick Range:").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(quick_frame, text="Last 7 Days", command=lambda: self.set_date_range(7)).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="Last 30 Days", command=lambda: self.set_date_range(30)).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="This Month", command=self.set_this_month).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="Last Month", command=self.set_last_month).pack(side=tk.LEFT, padx=2)

    def create_output_selection_frame(self, parent):
        """Create output selection frame"""
        output_frame = ttk.LabelFrame(parent, text="Output Settings", padding="10")
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)

        # Output path selection
        ttk.Label(output_frame, text="Output Path:").grid(row=0, column=0, sticky=tk.W, pady=2)

        output_path_frame = ttk.Frame(output_frame)
        output_path_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        output_path_frame.columnconfigure(0, weight=1)

        self.output_path_entry = ttk.Entry(output_path_frame, textvariable=self.output_path, width=60)
        self.output_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        browse_output_btn = ttk.Button(output_path_frame, text="Browse", command=self.browse_output)
        browse_output_btn.grid(row=0, column=1)

        # Set default output path
        default_output = os.path.join(os.path.expanduser("~"), "Desktop", f"PGE2B_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        self.output_path.set(default_output)

    def create_action_buttons_frame(self, parent):
        """Create action buttons frame"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))

        # Main action buttons
        self.preview_btn = ttk.Button(
            action_frame,
            text="Load Data Preview",
            command=self.load_comprehensive_preview,
            style="Accent.TButton"
        )
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.generate_btn = ttk.Button(
            action_frame,
            text="Generate Report",
            command=self.generate_report,
            style="Accent.TButton"
        )
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))

        validate_btn = ttk.Button(action_frame, text="Validate Template", command=self.validate_template)
        validate_btn.pack(side=tk.LEFT, padx=5)

        # Debug buttons
        debug_btn = ttk.Button(action_frame, text="Debug Mode", command=self.run_debug_mode)
        debug_btn.pack(side=tk.LEFT, padx=5)

        # Configuration buttons
        config_frame = ttk.Frame(action_frame)
        config_frame.pack(side=tk.RIGHT, padx=(10, 0))

        help_btn = ttk.Button(config_frame, text="Help", command=self.show_help)
        help_btn.pack(side=tk.LEFT, padx=2)

    def create_progress_frame(self, parent):
        """Create progress frame"""
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # Progress label
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)

        # Status label
        self.status_label = ttk.Label(progress_frame, text="Status: Idle", font=('Arial', 9, 'italic'))
        self.status_label.grid(row=2, column=0, sticky=tk.W)

    def load_comprehensive_preview(self):
        """Load comprehensive data preview"""
        if not self.db_connected.get():
            messagebox.showerror("Not Connected", "Please connect to database first")
            return

        if not self.template_path.get():
            messagebox.showerror("No Template", "Please select a template first")
            return

        def preview_worker():
            try:
                self.log_message("=== STARTING COMPREHENSIVE DATA PREVIEW ===", "info")
                self.update_progress(5, "Initializing preview components...")

                # Initialize components if not already done
                if not self.template_processor or not self.report_generator:
                    self.initialize_preview_components()

                # Prepare parameters
                parameters = {
                    'start_date': self.start_date.get(),
                    'end_date': self.end_date.get(),
                    'estate_name': 'PGE 2B',
                    'estate_code': 'PGE_2B'
                }

                self.update_progress(10, "Executing database queries...")
                self.log_message(f"Parameters: {parameters}", "info")

                # Execute all queries with timing
                import time
                start_time = time.time()

                # Clear previous data
                self.query_results = {}
                self.variables = {}
                self.preview_data = {}

                # Clear treeviews
                for item in self.query_tree.get_children():
                    self.query_tree.delete(item)
                for item in self.var_tree.get_children():
                    self.var_tree.delete(item)

                # Execute queries
                query_results = self.formula_engine.execute_all_queries(parameters)
                execution_time = time.time() - start_time

                self.update_progress(30, "Processing query results...")
                self.log_message(f"Query execution completed in {execution_time:.2f} seconds", "info")

                # Populate query tree
                for query_name, result in query_results.items():
                    self.process_query_result(query_name, result, parameters)

                self.update_progress(50, "Processing variables...")
                self.log_message("Processing variables from query results...", "info")

                # Process variables
                variables = self.formula_engine.process_variables(query_results, parameters)
                self.variables = variables

                self.update_progress(70, "Populating variable tree...")
                self.log_message(f"Processed {len(variables)} variables", "info")

                # Populate variable tree
                self.populate_variable_tree(variables, query_results, parameters)

                # Prepare complete data
                complete_data = {
                    **parameters,
                    **variables,
                    **query_results
                }
                self.preview_data = complete_data

                self.update_progress(85, "Analyzing template compatibility...")
                self.log_message("Analyzing template placeholders...", "info")

                # Analyze template placeholders
                placeholder_analysis = self.analyze_template_placeholders(complete_data)

                self.update_progress(90, "Generating preview summary...")
                self.log_message("Generating preview summary...", "info")

                # Show preview summary
                self.show_preview_summary(parameters, query_results, variables, placeholder_analysis)

                self.update_progress(100, "Preview loaded successfully!")
                self.log_message("=== COMPREHENSIVE DATA PREVIEW COMPLETED ===", "success")

                self.preview_status_label.config(text=f"Preview loaded: {len(query_results)} queries, {len(variables)} variables")

                # Switch to preview tab
                self.notebook.select(1)

            except Exception as e:
                self.update_progress(0, "Preview failed")
                self.log_message(f"Error loading preview: {e}", "error")
                messagebox.showerror("Preview Error", f"Failed to load data preview: {e}")

        # Run in separate thread
        thread = threading.Thread(target=preview_worker)
        thread.daemon = True
        thread.start()

    def process_query_result(self, query_name, result, parameters):
        """Process and display query result in tree"""
        try:
            status = "SUCCESS"
            rows = 0
            sample_data = "No data"
            execution_time = "N/A"

            if result is None:
                status = "FAILED"
                sample_data = "None result"
            elif isinstance(result, list):
                if len(result) == 0:
                    status = "EMPTY"
                    sample_data = "Empty list"
                else:
                    rows = len(result)
                    if isinstance(result[0], dict):
                        if 'rows' in result[0]:
                            actual_rows = result[0]['rows']
                            rows = len(actual_rows)
                            headers = result[0].get('headers', [])
                            if actual_rows:
                                sample_row = actual_rows[0]
                                sample_data = f"Headers: {headers}, Sample: {sample_row}"
                            else:
                                sample_data = f"Headers: {headers}, No rows"
                        else:
                            sample_data = str(result[0])
                    else:
                        sample_data = str(result[0])
            elif isinstance(result, pd.DataFrame):
                rows = len(result)
                if not result.empty:
                    sample_data = f"Columns: {list(result.columns)}, Shape: {result.shape}"
                else:
                    sample_data = "Empty DataFrame"
            else:
                sample_data = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)

            # Add to tree
            query_item = self.query_tree.insert('', 'end', text=query_name,
                                            values=(query_name, status, rows, execution_time, sample_data))

            self.query_results[query_name] = {
                'result': result,
                'status': status,
                'rows': rows,
                'sample_data': sample_data,
                'parameters': parameters
            }

        except Exception as e:
            self.log_message(f"Error processing query result {query_name}: {e}", "error")
            self.query_tree.insert('', 'end', text=query_name,
                                  values=(query_name, "ERROR", 0, "N/A", str(e)[:100]))

    def populate_variable_tree(self, variables, query_results, parameters):
        """Populate variable tree with processed variables"""
        try:
            # Group variables by category
            categories = {}
            for var_name, value in variables.items():
                # Determine category based on variable name pattern
                if var_name in ['report_title', 'report_period', 'generated_date', 'generated_time']:
                    category = "Report Info"
                elif var_name in ['estate_name', 'total_transactions', 'total_ripe_bunches', 'total_unripe_bunches']:
                    category = "Estate Summary"
                elif var_name.startswith(('TRANSDATE', 'JUMLAH', 'EMPLOYEE', 'FIELDNAME')):
                    category = "Repeating Section Data"
                elif var_name in ['daily_average_transactions', 'peak_performance_day']:
                    category = "Performance Metrics"
                else:
                    category = "Other Variables"

                if category not in categories:
                    categories[category] = []
                categories[category].append((var_name, value))

            # Populate tree
            for category, var_list in categories.items():
                category_item = self.var_tree.insert('', 'end', text=category, open=True)

                for var_name, value in var_list:
                    value_str = str(value)
                    if len(value_str) > 200:
                        value_str = value_str[:200] + "..."

                    value_type = type(value).__name__

                    # Determine source
                    source = "Calculated"
                    if var_name in ['report_title', 'report_period']:
                        source = "Static/Formatting"
                    elif var_name in ['estate_name']:
                        source = "Query Result"
                    elif var_name.startswith(('TRANSDATE', 'JUMLAH', 'EMPLOYEE')):
                        source = "Query Data"
                    elif var_name in query_results:
                        source = "Query Result"

                    status = "Available"
                    if value is None or (isinstance(value, str) and value.startswith('{{')):
                        status = "Missing"

                    self.var_tree.insert(category_item, 'end', text=var_name,
                                       values=(var_name, value_str, value_type, source, status))

        except Exception as e:
            self.log_message(f"Error populating variable tree: {e}", "error")

    def analyze_template_placeholders(self, complete_data):
        """Analyze template placeholders against available data"""
        try:
            if not self.template_processor:
                return {"total_placeholders": 0, "resolved": 0, "unresolved": 0}

            placeholders = self.template_processor.get_placeholders()
            total_placeholders = sum(len(p) for p in placeholders.values())

            resolved = 0
            unresolved = 0
            missing_vars = []

            for sheet_name, sheet_placeholders in placeholders.items():
                for ph in sheet_placeholders:
                    placeholder = ph['placeholder']
                    value = self.template_processor._get_placeholder_value(placeholder, complete_data)

                    if value is not None:
                        resolved += 1
                    else:
                        unresolved += 1
                        if placeholder not in missing_vars:
                            missing_vars.append(placeholder)

            return {
                "total_placeholders": total_placeholders,
                "resolved": resolved,
                "unresolved": unresolved,
                "success_rate": (resolved / total_placeholders * 100) if total_placeholders > 0 else 0,
                "missing_variables": missing_vars
            }

        except Exception as e:
            self.log_message(f"Error analyzing template placeholders: {e}", "error")
            return {"total_placeholders": 0, "resolved": 0, "unresolved": 0}

    def show_preview_summary(self, parameters, query_results, variables, placeholder_analysis):
        """Show comprehensive preview summary"""
        try:
            summary_window = tk.Toplevel(self.root)
            summary_window.title("Data Preview Summary")
            summary_window.geometry("700x500")
            summary_window.configure(bg='#f0f0f0')

            # Title
            title_label = ttk.Label(summary_window, text="Data Preview Summary",
                                    font=('Arial', 16, 'bold'))
            title_label.pack(pady=10)

            # Create notebook for different summary sections
            summary_notebook = ttk.Notebook(summary_window)
            summary_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Tab 1: Overview
            overview_frame = ttk.Frame(summary_notebook)
            summary_notebook.add(overview_frame, text="Overview")

            overview_text = f"""
            PARAMETERS
            -----------
            Start Date: {parameters.get('start_date', 'N/A')}
            End Date: {parameters.get('end_date', 'N/A')}
            Estate Name: {parameters.get('estate_name', 'N/A')}

            QUERY RESULTS
            -------------
            Total Queries: {len(query_results)}
            Successful Queries: {sum(1 for r in query_results.values() if r is not None)}
            Failed Queries: {sum(1 for r in query_results.values() if r is None)}

            PROCESSED VARIABLES
            ------------------
            Total Variables: {len(variables)}
            Variable Categories: {len(set([v.split('_')[0] for v in variables.keys()]))}

            TEMPLATE ANALYSIS
            -----------------
            Total Placeholders: {placeholder_analysis.get('total_placeholders', 0)}
            Resolved: {placeholder_analysis.get('resolved', 0)}
            Unresolved: {placeholder_analysis.get('unresolved', 0)}
            Success Rate: {placeholder_analysis.get('success_rate', 0):.1f}%
            """

            overview_text_widget = tk.Text(overview_frame, wrap=tk.WORD, font=('Consolas', 10))
            overview_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            overview_text_widget.insert('1.0', overview_text)
            overview_text_widget.config(state=tk.DISABLED)

            # Tab 2: Missing Variables
            if placeholder_analysis.get('unresolved', 0) > 0:
                missing_frame = ttk.Frame(summary_notebook)
                summary_notebook.add(missing_frame, text="Missing Variables")

                missing_text = f"""
                MISSING PLACEHOLDERS
                --------------------
                The following {placeholder_analysis.get('unresolved', 0)} placeholders could not be resolved:

                """

                for var in placeholder_analysis.get('missing_variables', []):
                    missing_text += f"• {var}\n"

                missing_text_widget = tk.Text(missing_frame, wrap=tk.WORD, font=('Consolas', 10))
                missing_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                missing_text_widget.insert('1.0', missing_text)
                missing_text_widget.config(state=tk.DISABLED)

            # Tab 3: Recommendations
            recommendations_frame = ttk.Frame(summary_notebook)
            summary_notebook.add(recommendations_frame, text="Recommendations")

            recommendations = self.generate_recommendations(parameters, query_results, variables, placeholder_analysis)

            recommendations_text_widget = tk.Text(recommendations_frame, wrap=tk.WORD, font=('Consolas', 10))
            recommendations_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            recommendations_text_widget.insert('1.0', recommendations)
            recommendations_text_widget.config(state=tk.DISABLED)

            # Close button
            close_btn = ttk.Button(summary_window, text="Close", command=summary_window.destroy)
            close_btn.pack(pady=10)

        except Exception as e:
            self.log_message(f"Error showing preview summary: {e}", "error")

    def generate_recommendations(self, parameters, query_results, variables, placeholder_analysis):
        """Generate recommendations based on preview analysis"""
        recommendations = "RECOMMENDATIONS\n"
        recommendations += "=" * 50 + "\n\n"

        # Query recommendations
        successful_queries = sum(1 for r in query_results.values() if r is not None)
        if successful_queries < len(query_results):
            recommendations += "1. QUERY ISSUES\n"
            recommendations += f"   - {len(query_results) - successful_queries} queries failed\n"
            recommendations += "   - Check SQL syntax and table names\n"
            recommendations += "   - Verify parameter substitution\n\n"

        # Variable recommendations
        if placeholder_analysis.get('success_rate', 0) < 100:
            recommendations += "2. TEMPLATE COMPATIBILITY\n"
            recommendations += f"   - {placeholder_analysis.get('unresolved', 0)} placeholders unresolved\n"
            recommendations += "   - Add missing variables to formula JSON\n"
            recommendations += "   - Check variable naming conventions\n\n"

        # Data quality recommendations
        if len(variables) < 20:
            recommendations += "3. DATA ENHANCEMENT\n"
            recommendations += "   - Consider adding more calculated variables\n"
            recommendations += "   - Include quality metrics and ratios\n"
            recommendations += "   - Add trend analysis variables\n\n"

        # Performance recommendations
        recommendations += "4. OPTIMIZATION SUGGESTIONS\n"
        recommendations += "   - Use date range filtering for better performance\n"
        recommendations += "   - Consider data aggregation for large datasets\n"
        recommendations += "   - Implement caching for frequently accessed data\n\n"

        if placeholder_analysis.get('success_rate', 0) >= 95:
            recommendations += "5. READY TO GENERATE\n"
            recommendations += "   ✅ All critical data available\n"
            recommendations += "   ✅ Template compatibility high\n"
            recommendations += "   ✅ Ready to generate report\n"
        else:
            recommendations += "5. PRE-GENERATION STEPS\n"
            recommendations += "   ❌ Address missing variables first\n"
            recommendations += "   ❌ Validate template compatibility\n"
            recommendations += "   ❌ Ensure data quality before generation\n"

        return recommendations

    def on_query_select(self, event):
        """Handle query selection in tree"""
        selection = self.query_tree.selection()
        if selection:
            item = selection[0]
            query_name = self.query_tree.item(item, 'text')
            self.selected_query_label.config(text=query_name)

    def on_variable_select(self, event):
        """Handle variable selection in tree"""
        selection = self.var_tree.selection()
        if selection:
            item = selection[0]
            var_name = self.var_tree.item(item, 'text')
            self.selected_var_label.config(text=var_name)

    def view_query_details(self):
        """View detailed query information"""
        selection = self.query_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a query first")
            return

        query_name = self.query_tree.item(selection[0], 'text')
        query_data = self.query_results.get(query_name)

        if not query_data:
            messagebox.showinfo("No Data", f"No data available for query: {query_name}")
            return

        # Create detail window
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Query Details: {query_name}")
        detail_window.geometry("600x400")

        # Create text widget
        text_widget = tk.Text(detail_window, wrap=tk.WORD, font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(detail_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        # Format and display details
        details = f"""QUERY DETAILS: {query_name}
{'='*50}

Status: {query_data['status']}
Rows: {query_data['rows']}
Parameters: {query_data['parameters']}

SAMPLE DATA:
{'-'*50}
{query_data['sample_data']}

FULL RESULT:
{'-'*50}
{json.dumps(query_data['result'], indent=2, default=str)}
"""

        text_widget.insert('1.0', details)
        text_widget.config(state=tk.DISABLED)

    def view_query_sql(self):
        """View SQL query"""
        selection = self.query_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a query first")
            return

        query_name = self.query_tree.item(selection[0], 'text')

        if not hasattr(self, 'formula_engine'):
            messagebox.showinfo("Not Available", "Formula engine not initialized")
            return

        try:
            queries = self.formula_engine.formulas.get('queries', {})
            if query_name in queries:
                sql = queries[query_name].get('sql', 'No SQL available')

                # Create SQL viewer window
                sql_window = tk.Toplevel(self.root)
                sql_window.title(f"SQL Query: {query_name}")
                sql_window.geometry("700x500")

                # Create text widget
                text_widget = tk.Text(sql_window, wrap=tk.WORD, font=('Consolas', 10))
                scrollbar = ttk.Scrollbar(sql_window, orient="vertical", command=text_widget.yview)
                text_widget.configure(yscrollcommand=scrollbar.set)

                text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

                text_widget.insert('1.0', f"SQL QUERY: {query_name}\n{'='*50}\n\n{sql}")
                text_widget.config(state=tk.DISABLED)
            else:
                messagebox.showinfo("Not Found", f"Query {query_name} not found in formula")
        except Exception as e:
            messagebox.showerror("Error", f"Error viewing SQL: {e}")

    def trace_variable(self):
        """Trace variable processing"""
        selection = self.var_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a variable first")
            return

        var_name = self.var_tree.item(selection[0], 'text')

        # Create trace window
        trace_window = tk.Toplevel(self.root)
        trace_window.title(f"Variable Trace: {var_name}")
        trace_window.geometry("600x400")

        # Create text widget
        text_widget = tk.Text(trace_window, wrap=tk.WORD, font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(trace_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        # Trace information
        trace_info = f"""VARIABLE TRACE: {var_name}
{'='*50}

CURRENT VALUE: {self.variables.get(var_name, 'NOT FOUND')}
VALUE TYPE: {type(self.variables.get(var_name, 'None')).__name__}

AVAILABLE DATA KEYS:
{'-'*50}
{list(self.preview_data.keys())}

RECOMMENDATIONS:
{'-'*50}
"""

        if var_name in self.variables:
            trace_info += "✅ Variable successfully processed\n"
        else:
            trace_info += "❌ Variable not found in processed data\n"
            trace_info += "   • Check if variable is defined in formula JSON\n"
            trace_info += "   • Verify query execution results\n"
            trace_info += "   • Check variable naming convention\n"

        text_widget.insert('1.0', trace_info)
        text_widget.config(state=tk.DISABLED)

    def refresh_preview(self):
        """Refresh current preview data"""
        self.load_comprehensive_preview()

    def export_preview_to_csv(self):
        """Export preview data to CSV files"""
        if not self.preview_data:
            messagebox.showinfo("No Data", "No preview data available to export")
            return

        try:
            export_dir = filedialog.askdirectory(title="Select export directory")
            if not export_dir:
                return

            # Export query results
            for query_name, query_data in self.query_results.items():
                if query_data and query_data.get('result'):
                    try:
                        # Convert to DataFrame and save
                        result = query_data['result']
                        if isinstance(result, list) and len(result) > 0:
                            if isinstance(result[0], dict) and 'rows' in result[0]:
                                # Enhanced connector format
                                rows = result[0]['rows']
                                headers = result[0].get('headers', [])
                                df = pd.DataFrame(rows)
                                filename = os.path.join(export_dir, f"{query_name}.csv")
                                df.to_csv(filename, index=False)
                                self.log_message(f"Exported {query_name} to {filename}", "success")
                    except Exception as e:
                        self.log_message(f"Error exporting {query_name}: {e}", "error")

            # Export variables
            variables_data = []
            for var_name, value in self.variables.items():
                variables_data.append({
                    'Variable': var_name,
                    'Value': str(value),
                    'Type': type(value).__name__
                })

            if variables_data:
                df_vars = pd.DataFrame(variables_data)
                filename = os.path.join(export_dir, "variables.csv")
                df_vars.to_csv(filename, index=False)
                self.log_message(f"Exported variables to {filename}", "success")

            messagebox.showinfo("Export Complete", f"Data exported to {export_dir}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")

    def initialize_preview_components(self):
        """Initialize components for preview"""
        try:
            self.log_message("Initializing preview components...", "info")

            # Initialize enhanced components
            self.formula_engine = FormulaEngineEnhanced(self.formula_path, self.connector)
            self.template_processor = TemplateProcessorEnhanced(self.template_path, self.formula_path)

            self.log_message("Preview components initialized successfully", "success")

        except Exception as e:
            self.log_message(f"Error initializing preview components: {e}", "error")
            raise

    # [Include other existing methods from the original GUI]
    # For brevity, I'll include the essential methods needed

    def initialize_components(self):
        """Initialize components"""
        try:
            self.log_message("Initializing components...", "info")
            self.load_templates()
            self.log_message("Components initialized successfully", "success")
        except Exception as e:
            self.log_message(f"Error initializing components: {e}", "error")

    def load_templates(self):
        """Load available templates"""
        try:
            templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

            if not os.path.exists(templates_dir):
                os.makedirs(templates_dir)
                self.log_message(f"Created templates directory: {templates_dir}", "info")

            self.templates_listbox.delete(0, tk.END)

            excel_templates = []
            for file in os.listdir(templates_dir):
                if file.lower().endswith(('.xlsx', '.xls')):
                    excel_templates.append(file)

            for template in sorted(excel_templates):
                template_path = os.path.join(templates_dir, template)
                self.templates_listbox.insert(tk.END, f"{template} ({os.path.getsize(template_path):,} bytes)")

            self.log_message(f"Loaded {len(excel_templates)} Excel templates", "info")

        except Exception as e:
            self.log_message(f"Error loading templates: {e}", "error")

    def on_template_select(self, event):
        """Handle template selection"""
        try:
            selection = self.templates_listbox.curselection()
            if selection:
                selected_text = self.templates_listbox.get(selection[0])
                template_name = selected_text.split(' (')[0]

                templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
                template_path = os.path.join(templates_dir, template_name)

                self.template_path.set(template_path)
                self.template_ready.set(True)

                # Initialize formula path
                base_path = os.path.dirname(os.path.abspath(__file__))
                self.formula_path = os.path.join(base_path, "laporan_ffb_analysis_formula_enhanced.json")

                self.log_message(f"Selected template: {template_name}", "info")

        except Exception as e:
            self.log_message(f"Error selecting template: {e}", "error")

    def check_database_connection(self):
        """Check database connection status"""
        try:
            if not self.db_path.get():
                self.update_status_indicator(False)
                self.db_connected.set(False)
                return

            # Use enhanced connector
            self.connector = FirebirdConnectorEnhanced(db_path=self.db_path.get())

            if self.connector.test_connection():
                self.update_status_indicator(True)
                self.db_connected.set(True)
                self.log_message("Database connection successful", "success")
            else:
                self.update_status_indicator(False)
                self.db_connected.set(False)
                self.log_message("Database connection failed", "error")

        except Exception as e:
            self.update_status_indicator(False)
            self.db_connected.set(False)
            self.log_message(f"Connection check error: {e}", "error")

    def update_status_indicator(self, connected):
        """Update database connection status indicator"""
        self.status_canvas.delete("all")

        if connected:
            # Green circle for connected
            self.status_canvas.create_oval(2, 2, 18, 18, fill="#4CAF50", outline="#2E7D32")
            self.status_canvas.create_text(10, 10, text="OK", fill="white", font=("Arial", 8, "bold"))
            self.db_status_text.set("Connected")
        else:
            # Red circle for disconnected
            self.status_canvas.create_oval(2, 2, 18, 18, fill="#F44336", outline="#C62828")
            self.status_canvas.create_text(10, 10, text="X", fill="white", font=("Arial", 8, "bold"))
            self.db_status_text.set("Disconnected")

    def connect_database(self):
        """Connect to database"""
        def connect_worker():
            try:
                self.log_message("Connecting to database...", "info")
                self.update_progress(20, "Initializing connection...")

                if not self.template_path.get():
                    self.update_progress(0, "No template selected")
                    return

                self.connector = FirebirdConnectorEnhanced(db_path=self.db_path.get())
                self.formula_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "laporan_ffb_analysis_formula_enhanced.json")

                self.update_progress(50, "Testing connection...")

                if self.connector.test_connection():
                    self.update_progress(80, "Initializing formula engine...")
                    self.formula_engine = FormulaEngineEnhanced(self.formula_path, self.connector)

                    self.update_progress(100, "Database connected successfully!")
                    self.update_status_indicator(True)
                    self.db_connected.set(True)
                    self.log_message("Database connected successfully", "success")

                    # Enable preview button
                    self.preview_btn.config(state="normal")
                else:
                    self.update_progress(0, "Connection failed")
                    self.update_status_indicator(False)
                    self.db_connected.set(False)
                    self.log_message("Database connection failed", "error")

            except Exception as e:
                self.update_progress(0, "Connection failed")
                self.update_status_indicator(False)
                self.db_connected.set(False)
                self.log_message(f"Database connection failed: {e}", "error")

        thread = threading.Thread(target=connect_worker)
        thread.daemon = True
        thread.start()

    def test_connection(self):
        """Test database connection"""
        def test_worker():
            try:
                self.log_message("Testing database connection...", "info")
                self.update_progress(20, "Preparing test...")

                if not self.connector:
                    self.connector = FirebirdConnectorEnhanced(db_path=self.db_path.get())

                self.update_progress(50, "Executing test query...")

                test_query = "SELECT 'Connection Test Successful' as STATUS FROM RDB$DATABASE"
                result = self.connector.execute_query(test_query)

                self.update_progress(80, "Validating results...")

                if result and len(result) > 0:
                    self.update_progress(100, "Connection test successful!")
                    self.update_status_indicator(True)
                    self.db_connected.set(True)
                    self.log_message("Database connection test successful", "success")
                    messagebox.showinfo("Connection Test", "Database connection is working correctly!")
                else:
                    raise Exception("No results from test query")

            except Exception as e:
                self.update_progress(0, "Connection test failed")
                self.log_message(f"Connection test failed: {e}", "error")
                messagebox.showerror("Connection Test", f"Database connection test failed: {e}")

        thread = threading.Thread(target=test_worker)
        thread.daemon = True
        thread.start()

    def generate_report(self):
        """Generate report"""
        if not self.db_connected.get():
            messagebox.showerror("Not Connected", "Please connect to database first")
            return

        if not self.template_path.get():
            messagebox.showerror("No Template", "Please select a template first")
            return

        if not self.output_path.get():
            messagebox.showerror("Output Error", "Please specify output path")
            return

        def generate_worker():
            try:
                self.log_message("=== STARTING REPORT GENERATION ===", "info")
                self.update_progress(5, "Initializing report generation...")

                # Initialize components
                self.formula_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "laporan_ffb_analysis_formula_enhanced.json")
                self.report_generator = ExcelReportGeneratorEnhanced(
                    template_path=self.template_path.get(),
                    formula_path=self.formula_path
                )

                # Prepare parameters
                parameters = {
                    'start_date': self.start_date.get(),
                    'end_date': self.end_date.get(),
                    'selected_estates': ['PGE 2B']
                }

                self.update_progress(20, "Generating report...")
                self.log_message(f"Generating report for parameters: {parameters}", "info")

                # Generate report
                output_dir = os.path.dirname(self.output_path.get())
                success, files = self.report_generator.generate_report(
                    start_date=parameters['start_date'],
                    end_date=parameters['end_date'],
                    selected_estates=parameters['selected_estates'],
                    output_dir=output_dir
                )

                self.update_progress(90, "Finalizing report...")

                if success:
                    # Rename output file if needed
                    if files and len(files) > 0:
                        generated_file = files[0]
                        if os.path.exists(generated_file) and generated_file != self.output_path.get():
                            import shutil
                            shutil.move(generated_file, self.output_path.get())

                    self.update_progress(100, "Report generated successfully!")
                    self.log_message("=== REPORT GENERATION COMPLETED ===", "success")

                    messagebox.showinfo("Report Generated", f"Excel report generated successfully!\n\nOutput: {self.output_path.get()}\n\nDo you want to open the report?")
                else:
                    raise Exception("Report generation failed")

            except Exception as e:
                self.update_progress(0, "Report generation failed")
                self.log_message(f"Report generation failed: {e}", "error")
                messagebox.showerror("Generation Error", f"Failed to generate report: {e}")

        thread = threading.Thread(target=generate_worker)
        thread.daemon = True
        thread.start()

    def validate_template(self):
        """Validate selected template"""
        if not self.template_path.get():
            messagebox.showerror("No Template", "Please select a template first")
            return

        try:
            self.formula_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "laporan_ffb_analysis_formula_enhanced.json")
            processor = TemplateProcessorEnhanced(self.template_path.get(), self.formula_path)

            info = processor.get_template_info()
            placeholders = processor.get_placeholders()

            messagebox.showinfo("Template Validation", f"Template is valid!\n\nSheets: {info.get('sheets', [])}\nTotal placeholders: {info.get('total_placeholders', 0)}")

        except Exception as e:
            messagebox.showerror("Template Validation", f"Template validation failed: {e}")

    def run_debug_mode(self):
        """Run debug mode"""
        # Switch to debug tab
        self.notebook.select(2)
        self.log_message("=== DEBUG MODE ACTIVATED ===", "debug")

    def show_help(self):
        """Show help dialog"""
        help_text = """
        Enhanced Report Generator with Data Preview Help

        DATA PREVIEW FEATURES:
        • Load comprehensive preview before generating reports
        • View query results with detailed information
        • Analyze processed variables and their sources
        • Check template placeholder compatibility
        • Export preview data to CSV files

        USAGE:
        1. Connect to database
        2. Select template
        3. Set date range
        4. Click "Load Data Preview"
        5. Review query results and variables
        6. Generate report when ready

        TROUBLESHOOTING:
        • Check debug log for detailed error messages
        • Use Preview tab to identify missing variables
        • Verify query execution status
        • Ensure template compatibility
        """

        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("600x400")
        help_window.configure(bg='#f0f0f0')

        help_text_widget = tk.Text(help_window, wrap=tk.WORD, font=('Arial', 10))
        help_text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        help_text_widget.insert('1.0', help_text)
        help_text_widget.config(state=tk.DISABLED)

        close_btn = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_btn.pack(pady=20)

    def log_message(self, message, level="info"):
        """Log message to debug tab"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.debug_text.insert(tk.END, log_entry, level)
        self.debug_text.see(tk.END)

    def update_progress(self, value, message=""):
        """Update progress bar and label"""
        self.progress_var.set(value)
        if message:
            self.progress_label.config(text=message)
        self.status_label.config(text=f"Status: {message}")
        self.root.update_idletasks()

    def clear_debug_log(self):
        """Clear debug log"""
        self.debug_text.delete(1.0, tk.END)
        self.log_message("Debug log cleared", "info")

    def save_debug_log(self):
        """Save debug log to file"""
        try:
            log_file = filedialog.asksaveasfilename(
                title="Save Debug Log",
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("All Files", "*.*")]
            )
            if log_file:
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(self.debug_text.get('1.0', tk.END))
                self.log_message(f"Debug log saved to: {log_file}", "success")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save debug log: {e}")

    def filter_errors(self):
        """Filter debug log to show only errors"""
        content = self.debug_text.get('1.0', tk.END)
        lines = content.split('\n')
        error_lines = [line for line in lines if 'ERROR' in line or 'FAILED' in line]

        self.debug_text.delete('1.0', tk.END)
        self.debug_text.insert('1.0', '\n'.join(error_lines))

    # Date range methods
    def set_date_range(self, days):
        """Set date range for last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        self.start_date.set(start_date.strftime("%Y-%m-%d"))
        self.end_date.set(end_date.strftime("%Y-%m-%d"))

    def set_this_month(self):
        """Set date range to this month"""
        now = datetime.now()
        start_date = now.replace(day=1)
        end_date = now
        self.start_date.set(start_date.strftime("%Y-%m-%d"))
        self.end_date.set(end_date.strftime("%Y-%m-%d"))

    def set_last_month(self):
        """Set date range to last month"""
        now = datetime.now()
        if now.month == 1:
            start_date = now.replace(year=now.year-1, month=12, day=1)
            end_date = now.replace(year=now.year-1, month=12, day=31)
        else:
            start_date = now.replace(month=now.month-1, day=1)
            next_month = now.replace(month=now.month, day=1)
            end_date = next_month - timedelta(days=1)

        self.start_date.set(start_date.strftime("%Y-%m-%d"))
        self.end_date.set(end_date.strftime("%Y-%m-%d"))

    # Browse methods
    def browse_database(self):
        """Browse for database file"""
        filename = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("Firebird Database", "*.fdb"), ("All Files", "*.*")]
        )
        if filename:
            self.db_path.set(filename)
            self.check_database_connection()

    def browse_template(self):
        """Browse for template file"""
        filename = filedialog.askopenfilename(
            title="Select Template File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")],
            initialdir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        )
        if filename:
            self.template_path.set(filename)
            self.template_ready.set(True)

    def browse_output(self):
        """Browse for output file"""
        filename = filedialog.asksaveasfilename(
            title="Save Report As",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
            initialfile=f"PGE2B_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        if filename:
            self.output_path.set(filename)

def main():
    """Main function"""
    root = tk.Tk()

    # Set style
    style = ttk.Style()
    style.theme_use('clam')

    # Configure accent button style
    style.configure(
        "Accent.TButton",
        foreground="white",
        background="#007ACC",
        font=('Arial', 10, 'bold')
    )

    # Create application
    app = EnhancedReportGUIWithPreview(root)

    # Handle window closing
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start application
    root.mainloop()

if __name__ == "__main__":
    main()