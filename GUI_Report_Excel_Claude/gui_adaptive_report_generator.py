#!/usr/bin/env python3
"""
Adaptive Report Generator GUI - Sistem yang menyesuaikan dengan template Excel
Bisa menghandle perubahan format template tanpa perlu mengubah kode
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
from datetime import datetime, timedelta
import json
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from firebird_connector_enhanced import FirebirdConnectorEnhanced
    from dynamic_formula_engine_enhanced import EnhancedDynamicFormulaEngine
    from adaptive_excel_processor import AdaptiveExcelProcessor
    from database_helper import (
        execute_query_with_extraction, 
        get_table_count, 
        get_sample_data,
        normalize_data_row
    )
    from database_selector import DatabaseSelector
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import required modules: {e}")
    sys.exit(1)

# Setup enhanced logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdaptiveReportGeneratorGUI:
    """
    Adaptive Report Generator yang menyesuaikan dengan template Excel secara otomatis
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Adaptive Report Generator - Excel Template Flexibel")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')

        # Variables
        self.db_path = tk.StringVar(value=r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB")
        self.template_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.start_date = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        self.end_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.formula_file = tk.StringVar(value="pge2b_corrected_formula.json")
        self.estate_var = tk.StringVar(value="PGE 2B")
        
        # Multi-estate style variables
        self.is_generating = False
        self.current_thread = None

        # Status variables
        self.db_connected = tk.BooleanVar(value=False)
        self.db_status_text = tk.StringVar(value="Not Connected")
        self.template_analyzed = tk.BooleanVar(value=False)
        self.template_status_text = tk.StringVar(value="Not Analyzed")

        # Components
        self.connector = None
        self.dynamic_engine = None
        self.adaptive_processor = None
        self.template_analysis = {}
        self.formula_data = None

        # Setup GUI
        self.setup_gui()

        # Initialize components
        self.initialize_components()

        # Check database connection
        self.check_database_connection()

    def setup_gui(self):
        """Setup GUI components dengan layout yang ditingkatkan"""
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
            text="Adaptive Report Generator - Template Excel Fleksibel",
            font=('Arial', 16, 'bold')
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="Sistem menyesuaikan otomatis dengan perubahan format template Excel",
            font=('Arial', 10),
            foreground='#666666'
        )
        subtitle_label.pack()

        # Database Status Frame
        self.create_database_status_frame(main_frame)

        # Template Analysis Frame
        self.create_template_analysis_frame(main_frame)

        # Date Range Frame
        self.create_date_range_frame(main_frame)

        # Template Preview Frame
        self.create_template_preview_frame(main_frame)

        # Output Selection Frame
        self.create_output_selection_frame(main_frame)

        # Action Buttons Frame
        self.create_action_buttons_frame(main_frame)

        # Progress Frame
        self.create_progress_frame(main_frame)

        # Log Frame
        self.create_log_frame(main_frame)

    def create_database_status_frame(self, parent):
        """Create database status frame"""
        db_frame = ttk.LabelFrame(parent, text="Database Connection", padding="10")
        db_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        db_frame.columnconfigure(1, weight=1)

        # Database path selection
        ttk.Label(db_frame, text="Database Path:").grid(row=0, column=0, sticky=tk.W, pady=2)

        db_path_frame = ttk.Frame(db_frame)
        db_path_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        db_path_frame.columnconfigure(0, weight=1)

        db_path_entry = ttk.Entry(db_path_frame, textvariable=self.db_path, width=80)
        db_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        browse_db_btn = ttk.Button(db_path_frame, text="Browse", command=self.browse_database)
        browse_db_btn.grid(row=0, column=1)
        
        select_db_btn = ttk.Button(db_path_frame, text="Select DB", command=self.select_database)
        select_db_btn.grid(row=0, column=2, padx=(5, 0))

        # Connection status
        ttk.Label(db_frame, text="Status:").grid(row=1, column=0, sticky=tk.W, pady=2)

        status_frame = ttk.Frame(db_frame)
        status_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        status_frame.columnconfigure(0, weight=1)

        # Status indicator
        self.db_status_canvas = tk.Canvas(status_frame, width=20, height=20, highlightthickness=0)
        self.db_status_canvas.grid(row=0, column=0, padx=(0, 10))

        status_text = ttk.Label(status_frame, textvariable=self.db_status_text, font=('Arial', 10, 'bold'))
        status_text.grid(row=0, column=1, sticky=tk.W)

        # Connection buttons
        button_frame = ttk.Frame(db_frame)
        button_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))

        self.connect_btn = ttk.Button(button_frame, text="Connect", command=self.connect_database)
        self.connect_btn.grid(row=0, column=0, padx=(0, 5))

        self.test_btn = ttk.Button(button_frame, text="Test Connection", command=self.test_connection)
        self.test_btn.grid(row=0, column=1, padx=5)

    def create_template_analysis_frame(self, parent):
        """Create template analysis frame"""
        template_frame = ttk.LabelFrame(parent, text="Template Analysis", padding="10")
        template_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        template_frame.columnconfigure(1, weight=1)

        # Template file selection
        ttk.Label(template_frame, text="Template File:").grid(row=0, column=0, sticky=tk.W, pady=2)

        template_path_frame = ttk.Frame(template_frame)
        template_path_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        template_path_frame.columnconfigure(0, weight=1)

        self.template_path_entry = ttk.Entry(template_path_frame, textvariable=self.template_path, width=80)
        self.template_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        browse_template_btn = ttk.Button(template_path_frame, text="Browse", command=self.browse_template)
        browse_template_btn.grid(row=0, column=1)

        # Template analysis status
        ttk.Label(template_frame, text="Analysis Status:").grid(row=1, column=0, sticky=tk.W, pady=2)

        analysis_frame = ttk.Frame(template_frame)
        analysis_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        analysis_frame.columnconfigure(0, weight=1)

        # Analysis indicator
        self.analysis_canvas = tk.Canvas(analysis_frame, width=20, height=20, highlightthickness=0)
        self.analysis_canvas.grid(row=0, column=0, padx=(0, 10))

        analysis_text = ttk.Label(analysis_frame, textvariable=self.template_status_text, font=('Arial', 10, 'bold'))
        analysis_text.grid(row=0, column=1, sticky=tk.W)

        # Formula file selection
        ttk.Label(template_frame, text="Formula File:").grid(row=2, column=0, sticky=tk.W, pady=2)

        formula_path_frame = ttk.Frame(template_frame)
        formula_path_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        formula_path_frame.columnconfigure(0, weight=1)

        self.formula_path_entry = ttk.Entry(formula_path_frame, textvariable=self.formula_file, width=80)
        self.formula_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        browse_formula_btn = ttk.Button(formula_path_frame, text="Browse", command=self.browse_formula)
        browse_formula_btn.grid(row=0, column=1)

        # Analysis buttons
        analysis_button_frame = ttk.Frame(template_frame)
        analysis_button_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))

        analyze_template_btn = ttk.Button(analysis_button_frame, text="Analyze Template", command=self.analyze_template)
        analyze_template_btn.grid(row=0, column=0, padx=(0, 5))

        load_default_btn = ttk.Button(analysis_button_frame, text="Load Default", command=self.load_default_template)
        load_default_btn.grid(row=0, column=1, padx=5)

        refresh_analysis_btn = ttk.Button(analysis_button_frame, text="Refresh Analysis", command=self.refresh_template_analysis)
        refresh_analysis_btn.grid(row=0, column=2, padx=5)

    def create_date_range_frame(self, parent):
        """Create date range selection frame"""
        date_frame = ttk.LabelFrame(parent, text="Report Period", padding="10")
        date_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))

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
        ttk.Button(quick_frame, text="Custom Range", command=self.set_custom_range).pack(side=tk.LEFT, padx=2)

    def create_template_preview_frame(self, parent):
        """Create template preview frame"""
        preview_frame = ttk.LabelFrame(parent, text="Template Structure Analysis", padding="10")
        preview_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        # Create treeview for template structure
        tree_frame = ttk.Frame(preview_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Create treeview
        columns = ('sheet', 'type', 'description', 'count')
        self.template_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=6)

        # Configure columns
        self.template_tree.heading('#0', text='Item')
        self.template_tree.heading('sheet', text='Sheet')
        self.template_tree.heading('type', text='Type')
        self.template_tree.heading('description', text='Description')
        self.template_tree.heading('count', text='Count')

        self.template_tree.column('#0', width=200)
        self.template_tree.column('sheet', width=100)
        self.template_tree.column('type', width=150)
        self.template_tree.column('description', width=300)
        self.template_tree.column('count', width=80)

        # Add scrollbar
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.template_tree.yview)
        self.template_tree.configure(yscrollcommand=tree_scrollbar.set)

        self.template_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def create_output_selection_frame(self, parent):
        """Create output selection frame"""
        output_frame = ttk.LabelFrame(parent, text="Output Settings", padding="10")
        output_frame.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)

        # Output path selection
        ttk.Label(output_frame, text="Output Path:").grid(row=0, column=0, sticky=tk.W, pady=2)

        output_path_frame = ttk.Frame(output_frame)
        output_path_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        output_path_frame.columnconfigure(0, weight=1)

        self.output_path_entry = ttk.Entry(output_path_frame, textvariable=self.output_path, width=80)
        self.output_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        browse_output_btn = ttk.Button(output_path_frame, text="Browse", command=self.browse_output)
        browse_output_btn.grid(row=0, column=1)

        # Auto-generate filename checkbox
        auto_filename_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            output_frame,
            text="Auto-generate filename with timestamp",
            variable=auto_filename_var,
            command=lambda: self.auto_generate_filename(auto_filename_var.get())
        ).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        # Set default output path
        self.auto_generate_filename(True)

    def create_action_buttons_frame(self, parent):
        """Create action buttons frame"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))

        # Main action buttons
        self.generate_btn = ttk.Button(
            action_frame,
            text="Generate Adaptive Report",
            command=self.generate_adaptive_report,
            style="Accent.TButton"
        )
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))

        preview_data_btn = ttk.Button(action_frame, text="Preview Data", command=self.preview_data)
        preview_data_btn.pack(side=tk.LEFT, padx=5)

        validate_system_btn = ttk.Button(action_frame, text="Validate System", command=self.validate_system)
        validate_system_btn.pack(side=tk.LEFT, padx=5)

        # Test buttons
        test_adaptive_btn = ttk.Button(action_frame, text="Test Adaptive", command=self.test_adaptive_processing)
        test_adaptive_btn.pack(side=tk.LEFT, padx=5)

        # Configuration buttons
        config_frame = ttk.Frame(action_frame)
        config_frame.pack(side=tk.RIGHT, padx=(10, 0))

        settings_btn = ttk.Button(config_frame, text="Settings", command=self.open_settings)
        settings_btn.pack(side=tk.LEFT, padx=2)

        help_btn = ttk.Button(config_frame, text="Help", command=self.show_help)
        help_btn.pack(side=tk.LEFT, padx=2)

    def create_progress_frame(self, parent):
        """Create progress frame"""
        progress_frame = ttk.LabelFrame(parent, text="Processing Progress", padding="10")
        progress_frame.grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
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

    def create_log_frame(self, parent):
        """Create log frame"""
        log_frame = ttk.LabelFrame(parent, text="Processing Log", padding="10")
        log_frame.grid(row=8, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        log_frame.columnconfigure(0, weight=1)
        parent.rowconfigure(8, weight=1)

        # Create text widget with scrollbar
        log_scroll_frame = ttk.Frame(log_frame)
        log_scroll_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scroll_frame.columnconfigure(0, weight=1)
        log_scroll_frame.rowconfigure(0, weight=1)

        # Create text widget
        self.log_text = tk.Text(
            log_scroll_frame,
            height=12,
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create scrollbar
        log_scrollbar = ttk.Scrollbar(log_scroll_frame, orient="vertical", command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Configure text widget
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        # Configure text tags
        self.log_text.tag_configure("info", foreground="black")
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("debug", foreground="blue")
        self.log_text.tag_configure("adaptive", foreground="purple")

        # Clear log button
        clear_log_btn = ttk.Button(log_frame, text="Clear Log", command=self.clear_log)
        clear_log_btn.grid(row=1, column=0, sticky=tk.E, pady=(5, 0))

    def initialize_components(self):
        """Initialize all components"""
        try:
            self.log_message("Initializing adaptive components...", "info")

            # Load default template
            self.load_default_template()
            
            # Load formula data
            self.load_formula_data()

            self.log_message("Adaptive components initialized successfully", "success")

        except Exception as e:
            self.log_message(f"Error initializing components: {e}", "error")
            messagebox.showerror("Initialization Error", f"Failed to initialize components: {e}")

    def load_formula_data(self):
        """Load formula data from JSON file"""
        try:
            formula_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                self.formula_file.get()
            )
            
            if os.path.exists(formula_path):
                with open(formula_path, 'r', encoding='utf-8') as f:
                    self.formula_data = json.load(f)
                self.log_message(f"Formula data loaded: {formula_path}", "info")
            else:
                self.log_message(f"Formula file not found: {formula_path}", "warning")
                self.formula_data = None
                
        except Exception as e:
            self.log_message(f"Error loading formula data: {e}", "error")
            self.formula_data = None

    def load_default_template(self):
        """Load default template"""
        try:
            default_template = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "templates",
                "Template_Laporan_FFB_Analysis.xlsx"
            )

            if os.path.exists(default_template):
                self.template_path.set(default_template)
                self.log_message(f"Default template loaded: {default_template}", "info")
            else:
                self.log_message(f"Default template not found: {default_template}", "warning")

        except Exception as e:
            self.log_message(f"Error loading default template: {e}", "error")

    def get_query_from_template(self, query_name, **kwargs):
        """Get query from template file with parameter substitution"""
        try:
            if not hasattr(self, 'formula_data') or not self.formula_data:
                return None
                
            queries = self.formula_data.get('queries', {})
            if query_name not in queries:
                print(f"Query '{query_name}' not found in template")
                return None
                
            query_sql = queries[query_name]['sql']
            
            # Replace parameters in query
            for key, value in kwargs.items():
                placeholder = '{' + key + '}'
                query_sql = query_sql.replace(placeholder, str(value))
                
            return query_sql
        except Exception as e:
            print(f"Error getting query from template: {e}")
            return None

    def update_db_status_indicator(self, connected):
        """Update database connection status indicator"""
        self.db_status_canvas.delete("all")

        if connected:
            # Green circle for connected
            self.db_status_canvas.create_oval(2, 2, 18, 18, fill="#4CAF50", outline="#2E7D32")
            self.db_status_canvas.create_text(10, 10, text="OK", fill="white", font=("Arial", 8, "bold"))
            self.db_status_text.set("Connected")
        else:
            # Red circle for disconnected
            self.db_status_canvas.create_oval(2, 2, 18, 18, fill="#F44336", outline="#C62828")
            self.db_status_canvas.create_text(10, 10, text="X", fill="white", font=("Arial", 8, "bold"))
            self.db_status_text.set("Disconnected")

    def update_analysis_indicator(self, analyzed):
        """Update template analysis status indicator"""
        self.analysis_canvas.delete("all")

        if analyzed:
            # Green circle for analyzed
            self.analysis_canvas.create_oval(2, 2, 18, 18, fill="#4CAF50", outline="#2E7D32")
            self.analysis_canvas.create_text(10, 10, text="✓", fill="white", font=("Arial", 8, "bold"))
            self.template_status_text.set("Analyzed")
        else:
            # Red circle for not analyzed
            self.analysis_canvas.create_oval(2, 2, 18, 18, fill="#F44336", outline="#C62828")
            self.analysis_canvas.create_text(10, 10, text="X", fill="white", font=("Arial", 8, "bold"))
            self.template_status_text.set("Not Analyzed")

    def check_database_connection(self):
        """Check database connection status"""
        try:
            self.log_message("Checking database connection...", "info")

            if not self.db_path.get():
                self.update_db_status_indicator(False)
                self.db_connected.set(False)
                self.log_message("No database path specified", "warning")
                return

            # Create connector to test connection
            self.log_message(f"Testing connection to: {self.db_path.get()}", "debug")
            self.connector = FirebirdConnectorEnhanced(db_path=self.db_path.get())

            # Test connection
            if self.connector.test_connection():
                self.update_db_status_indicator(True)
                self.db_connected.set(True)
                self.log_message("Database connection successful", "success")
            else:
                self.update_db_status_indicator(False)
                self.db_connected.set(False)
                self.log_message("Database connection failed", "error")

        except Exception as e:
            self.update_db_status_indicator(False)
            self.db_connected.set(False)
            self.log_message(f"Connection check error: {e}", "error")

    def connect_database(self):
        """Connect to database"""
        def connect_worker():
            try:
                self.log_message("Connecting to database...", "info")
                self.update_progress(10, "Initializing database connection...")

                # Create connector
                self.connector = FirebirdConnectorEnhanced(db_path=self.db_path.get())

                self.update_progress(30, "Establishing connection...")

                # Test connection
                if self.connector.test_connection():
                    self.update_progress(60, "Connection established")

                    # Initialize dynamic engine
                    self.update_progress(80, "Initializing dynamic engine...")
                    formula_path = os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        self.formula_file.get()
                    )
                    self.dynamic_engine = DynamicFormulaEngine(formula_path, self.connector)

                    self.update_progress(100, "Database connected successfully!")
                    self.update_db_status_indicator(True)
                    self.db_connected.set(True)
                    self.log_message("Database connected successfully", "success")

                else:
                    raise Exception("Connection test failed")

            except Exception as e:
                self.update_progress(0, "Connection failed")
                self.update_db_status_indicator(False)
                self.db_connected.set(False)
                self.log_message(f"Database connection failed: {e}", "error")
                messagebox.showerror("Connection Error", f"Failed to connect to database: {e}")

        # Run in separate thread
        thread = threading.Thread(target=connect_worker)
        thread.daemon = True
        thread.start()

    def test_connection(self):
        """Test database connection"""
        def test_worker():
            try:
                self.log_message("Testing database connection...", "info")
                self.update_progress(20, "Testing connection...")

                if not self.connector:
                    self.connector = FirebirdConnectorEnhanced(db_path=self.db_path.get())

                self.update_progress(50, "Executing test query...")

                # Test with sample query
                result = self.connector.execute_query("SELECT 'Connection Test Successful' as STATUS FROM RDB$DATABASE")

                self.update_progress(80, "Validating results...")

                if result and len(result) > 0:
                    self.update_progress(100, "Connection test successful!")
                    self.update_db_status_indicator(True)
                    self.db_connected.set(True)
                    self.log_message("Database connection test successful", "success")
                    self.log_message(f"Test result: {result}", "debug")
                    messagebox.showinfo("Connection Test", "Database connection is working correctly!")
                else:
                    raise Exception("No results from test query")

            except Exception as e:
                self.update_progress(0, "Connection test failed")
                self.log_message(f"Connection test failed: {e}", "error")
                messagebox.showerror("Connection Test", f"Database connection test failed: {e}")

        # Run in separate thread
        thread = threading.Thread(target=test_worker)
        thread.daemon = True
        thread.start()

    def analyze_template(self):
        """Analyze template with adaptive processing"""
        def analyze_worker():
            try:
                self.log_message("=== STARTING ADAPTIVE TEMPLATE ANALYSIS ===", "adaptive")
                self.update_progress(10, "Loading template...")

                if not self.template_path.get():
                    raise Exception("No template selected")

                # Check if template file exists
                if not os.path.exists(self.template_path.get()):
                    raise Exception("Template file not found")

                self.update_progress(30, "Creating adaptive processor...")

                # Create adaptive processor
                self.adaptive_processor = AdaptiveExcelProcessor(self.template_path.get(), debug_mode=True)

                self.update_progress(50, "Analyzing template structure...")

                # Get template analysis
                self.template_analysis = self.adaptive_processor.get_template_summary()

                self.update_progress(80, "Processing results...")

                # Display results in treeview
                self.display_template_analysis(self.template_analysis)

                # Update indicator
                self.update_analysis_indicator(True)
                self.template_analyzed.set(True)

                self.update_progress(100, "Template analysis completed successfully!")
                self.log_message("✅ Template analysis completed successfully", "success")

                # Log capabilities
                capabilities = self.template_analysis['capabilities']
                self.log_message("Template Capabilities:", "adaptive")
                self.log_message(f"  Total placeholders: {capabilities['total_placeholders']}", "info")
                self.log_message(f"  Sheets with placeholders: {capabilities['sheets_with_placeholders']}", "info")
                self.log_message(f"  Supports dynamic tables: {capabilities['supports_dynamic_tables']}", "info")
                self.log_message(f"  Supports template rows: {capabilities['supports_template_rows']}", "info")

                self.log_message("=== ADAPTIVE TEMPLATE ANALYSIS COMPLETED ===", "adaptive")

            except Exception as e:
                self.update_progress(0, "Template analysis failed")
                self.update_analysis_indicator(False)
                self.template_analyzed.set(False)
                self.log_message(f"❌ Template analysis failed: {e}", "error")
                messagebox.showerror("Analysis Error", f"Template analysis failed: {e}")

        # Run in separate thread
        thread = threading.Thread(target=analyze_worker)
        thread.daemon = True
        thread.start()

    def display_template_analysis(self, analysis):
        """Display template analysis in treeview"""
        # Clear existing items
        for item in self.template_tree.get_children():
            self.template_tree.delete(item)

        # Add root item
        root_item = self.template_tree.insert('', 'end', text='Template Analysis', values=('', '', '', ''), open=True)

        # Add summary
        template_info = analysis['template_info']
        summary_item = self.template_tree.insert(root_item, 'end', text='Summary',
                                                values=('All', 'Info', f'{template_info["total_sheets"]} sheets, {template_info["total_placeholders"]} placeholders', ''))

        # Add sheet details
        sheets_item = self.template_tree.insert(root_item, 'end', text='Sheets', values=('', '', '', ''), open=True)

        for sheet_name, sheet_info in template_info['data_sections'].items():
            # Sheet item
            sheet_item = self.template_tree.insert(sheets_item, 'end', text=sheet_name,
                                                 values=(sheet_name, 'Sheet', f'{sheet_info["placeholder_count"]} placeholders', sheet_info["placeholder_count"]))

            # Add placeholders for this sheet
            if sheet_info['placeholders']:
                placeholders_item = self.template_tree.insert(sheet_item, 'end', text='Placeholders',
                                                             values=(sheet_name, 'Placeholders', f'{len(sheet_info["placeholders"])} items', len(sheet_info["placeholders"])))

                # Show first few placeholders
                for ph in sheet_info['placeholders'][:5]:  # Show first 5
                    self.template_tree.insert(placeholders_item, 'end', text=ph['placeholder'],
                                            values=(sheet_name, 'Placeholder', f'Cell {ph["cell"]}', ''))

                if len(sheet_info['placeholders']) > 5:
                    self.template_tree.insert(placeholders_item, 'end', text='...',
                                            values=(sheet_name, 'More', f'... and {len(sheet_info["placeholders"]) - 5} more', ''))

            # Add tables
            if sheet_info['tables']:
                tables_item = self.template_tree.insert(sheet_item, 'end', text='Tables',
                                                       values=(sheet_name, 'Tables', f'{len(sheet_info["tables"])} dynamic tables', len(sheet_info["tables"])))

                for table in sheet_info['tables']:
                    table_desc = f"Header row {table['header_row']}, Template row {table['template_row']}, {table['col_count']} columns"
                    self.template_tree.insert(tables_item, 'end', text=f'Table {table["template_row"]}',
                                            values=(sheet_name, 'Dynamic Table', table_desc, table['col_count']))

            # Add data patterns
            if sheet_info['data_patterns']:
                patterns_item = self.template_tree.insert(sheet_item, 'end', text='Patterns',
                                                         values=(sheet_name, 'Patterns', f'{len(sheet_info["data_patterns"])} patterns', len(sheet_info["data_patterns"])))

                for pattern in sheet_info['data_patterns']:
                    pattern_desc = f"Row {pattern['row']}, {pattern['col_count']} columns"
                    self.template_tree.insert(patterns_item, 'end', text=f'Pattern {pattern["row"]}',
                                            values=(sheet_name, 'Pattern', pattern_desc, pattern['col_count']))

    def refresh_template_analysis(self):
        """Refresh template analysis"""
        self.analyze_template()

    def validate_system(self):
        """Validate entire system"""
        def validate_worker():
            try:
                self.log_message("=== COMPREHENSIVE SYSTEM VALIDATION ===", "info")
                self.update_progress(10, "Starting system validation...")

                # 1. Validate database connection
                self.update_progress(20, "Validating database connection...")
                if not self.db_connected.get():
                    self.check_database_connection()

                if not self.db_connected.get():
                    raise Exception("Database connection required")

                # 2. Validate template analysis
                self.update_progress(40, "Validating template analysis...")
                if not self.template_analyzed.get():
                    self.analyze_template()
                    # Wait for analysis to complete
                    import time
                    time.sleep(2)

                if not self.template_analyzed.get():
                    raise Exception("Template analysis required")

                # 3. Test adaptive processing
                self.update_progress(60, "Testing adaptive processing...")
                if not self.adaptive_processor:
                    raise Exception("Adaptive processor not initialized")

                # Create sample data for testing
                sample_data = {
                    'report_title': 'TEST ADAPTIVE REPORT',
                    'estate_name': 'TEST ESTATE',
                    'start_date': '2024-01-01',
                    'end_date': '2024-01-31',
                    'total_transactions': 100,
                    'current_date': datetime.now().strftime('%d %B %Y'),
                    'verification_rate': 95.5,
                    'Dashboard': [
                        {'total_transactions': 100, 'verification_rate': 95.5}
                    ],
                    'Harian': [
                        {'TRANSDATE': '2024-01-01', 'JUMLAH_TRANSAKSI': 50},
                        {'TRANSDATE': '2024-01-02', 'JUMLAH_TRANSAKSI': 60}
                    ],
                    'Karyawan': [
                        {'EMPLOYEE_NAME': 'Test Employee 1', 'JUMLAH_TRANSAKSI': 30},
                        {'EMPLOYEE_NAME': 'Test Employee 2', 'JUMLAH_TRANSAKSI': 25}
                    ]
                }

                # Test adaptive processing
                self.update_progress(80, "Testing data processing...")

                self.update_progress(100, "System validation completed successfully!")
                self.log_message("✅ System validation passed all checks", "success")
                self.log_message("=== COMPREHENSIVE SYSTEM VALIDATION COMPLETED ===", "success")

                messagebox.showinfo("Validation Complete", "All system validations passed successfully!\n\n✅ Database connection: OK\n✅ Template analysis: OK\n✅ Adaptive processing: OK")

            except Exception as e:
                self.update_progress(0, "System validation failed")
                self.log_message(f"❌ System validation failed: {e}", "error")
                messagebox.showerror("Validation Error", f"System validation failed: {e}")

        # Run in separate thread
        thread = threading.Thread(target=validate_worker)
        thread.daemon = True
        thread.start()

    def test_adaptive_processing(self):
        """Test adaptive processing with sample data"""
        def test_worker():
            try:
                self.log_message("=== TESTING ADAPTIVE PROCESSING ===", "adaptive")
                self.update_progress(10, "Starting adaptive processing test...")

                if not self.adaptive_processor:
                    raise Exception("Template not analyzed yet")

                self.update_progress(30, "Creating sample data...")

                # Create comprehensive sample data
                sample_data = {
                    # Report metadata
                    'report_title': 'ADAPTIVE PROCESSING TEST REPORT',
                    'estate_name': 'PGE 2B TEST',
                    'report_period': '1 Januari 2024 - 31 Januari 2024',
                    'generated_date': datetime.now().strftime('%d %B %Y'),
                    'generated_time': datetime.now().strftime('%H:%M:%S'),

                    # Dashboard summary
                    'total_transactions': 1500,
                    'total_ripe_bunches': 1200,
                    'total_unripe_bunches': 300,
                    'avg_ripe_per_transaction': 0.8,
                    'quality_percentage': 85.5,
                    'verification_rate': 92.3,
                    'daily_average_transactions': 48.4,
                    'daily_average_ripe': 38.7,
                    'peak_performance_day': '2024-01-15',
                    'low_performance_day': '2024-01-03',

                    # Dynamic data for repeating sections
                    'Dashboard': [
                        {'total_transactions': 1500, 'verification_rate': 92.3}
                    ],
                    'Harian': [
                        {'TRANSDATE': '2024-01-01', 'JUMLAH_TRANSAKSI': 45, 'RIPE_BUNCHES': 36, 'UNRIPE_BUNCHES': 9},
                        {'TRANSDATE': '2024-01-02', 'JUMLAH_TRANSAKSI': 52, 'RIPE_BUNCHES': 42, 'UNRIPE_BUNCHES': 10},
                        {'TRANSDATE': '2024-01-03', 'JUMLAH_TRANSAKSI': 38, 'RIPE_BUNCHES': 30, 'UNRIPE_BUNCHES': 8},
                        {'TRANSDATE': '2024-01-04', 'JUMLAH_TRANSAKSI': 61, 'RIPE_BUNCHES': 49, 'UNRIPE_BUNCHES': 12},
                        {'TRANSDATE': '2024-01-05', 'JUMLAH_TRANSAKSI': 47, 'RIPE_BUNCHES': 38, 'UNRIPE_BUNCHES': 9}
                    ],
                    'Karyawan': [
                        {'EMPLOYEE_NAME': 'Ahmad Sutrisno', 'RECORDTAG': 'KERANI', 'JUMLAH_TRANSAKSI': 180, 'TOTAL_RIPE': 150, 'TOTAL_UNRIPE': 30},
                        {'EMPLOYEE_NAME': 'Budi Santoso', 'RECORDTAG': 'KERANI', 'JUMLAH_TRANSAKSI': 165, 'TOTAL_RIPE': 135, 'TOTAL_UNRIPE': 30},
                        {'EMPLOYEE_NAME': 'Chandra Wijaya', 'RECORDTAG': 'MANDOR', 'JUMLAH_TRANSAKSI': 120, 'TOTAL_RIPE': 100, 'TOTAL_UNRIPE': 20},
                        {'EMPLOYEE_NAME': 'Dedi Kurniawan', 'RECORDTAG': 'MANDOR', 'JUMLAH_TRANSAKSI': 135, 'TOTAL_RIPE': 110, 'TOTAL_UNRIPE': 25},
                        {'EMPLOYEE_NAME': 'Eko Prasetyo', 'RECORDTAG': 'ASISTEN', 'JUMLAH_TRANSAKSI': 95, 'TOTAL_RIPE': 80, 'TOTAL_UNRIPE': 15},
                        {'EMPLOYEE_NAME': 'Fajar Setiawan', 'RECORDTAG': 'ASISTEN', 'JUMLAH_TRANSAKSI': 88, 'TOTAL_RIPE': 72, 'TOTAL_UNRIPE': 16}
                    ],
                    'Field': [
                        {'FIELDNAME': 'BLOCK A', 'JUMLAH_TRANSAKSI': 280, 'TOTAL_RIPE': 230, 'TOTAL_UNRIPE': 50},
                        {'FIELDNAME': 'BLOCK B', 'JUMLAH_TRANSAKSI': 265, 'TOTAL_RIPE': 215, 'TOTAL_UNRIPE': 50},
                        {'FIELDNAME': 'BLOCK C', 'JUMLAH_TRANSAKSI': 245, 'TOTAL_RIPE': 200, 'TOTAL_UNRIPE': 45},
                        {'FIELDNAME': 'BLOCK D', 'JUMLAH_TRANSAKSI': 290, 'TOTAL_RIPE': 240, 'TOTAL_UNRIPE': 50}
                    ],
                    'Kualitas': [
                        {'TRANSDATE': '2024-01-01', 'TOTAL_RIPE': 36, 'TOTAL_BLACK': 2, 'TOTAL_ROTTEN': 1, 'TOTAL_RATDAMAGE': 1, 'PERCENTAGE_DEFECT': 11.1},
                        {'TRANSDATE': '2024-01-02', 'TOTAL_RIPE': 42, 'TOTAL_BLACK': 3, 'TOTAL_ROTTEN': 1, 'TOTAL_RATDAMAGE': 2, 'PERCENTAGE_DEFECT': 14.3},
                        {'TRANSDATE': '2024-01-03', 'TOTAL_RIPE': 30, 'TOTAL_BLACK': 2, 'TOTAL_ROTTEN': 0, 'TOTAL_RATDAMAGE': 1, 'PERCENTAGE_DEFECT': 10.0},
                        {'TRANSDATE': '2024-01-04', 'TOTAL_RIPE': 49, 'TOTAL_BLACK': 3, 'TOTAL_ROTTEN': 2, 'TOTAL_RATDAMAGE': 2, 'PERCENTAGE_DEFECT': 14.3},
                        {'TRANSDATE': '2024-01-05', 'TOTAL_RIPE': 38, 'TOTAL_BLACK': 2, 'TOTAL_ROTTEN': 1, 'TOTAL_RATDAMAGE': 1, 'PERCENTAGE_DEFECT': 10.5}
                    ]
                }

                self.update_progress(50, "Testing adaptive processing...")

                # Create test output path
                test_output = os.path.join(
                    os.path.expanduser("~"),
                    "Desktop",
                    f"Adaptive_Test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                )

                # Test adaptive processing
                success = self.adaptive_processor.generate_report(sample_data, test_output)

                self.update_progress(90, "Processing results...")

                if success:
                    self.update_progress(100, "Adaptive processing test completed successfully!")
                    self.log_message(f"✅ Adaptive test report generated: {test_output}", "success")
                    self.log_message("=== ADAPTIVE PROCESSING TEST COMPLETED ===", "success")

                    # Ask user if they want to open the test file
                    result = messagebox.askyesno(
                        "Adaptive Test Complete",
                        f"Adaptive processing test completed successfully!\n\nTest file: {test_output}\n\nDo you want to open the test file?"
                    )

                    if result:
                        try:
                            os.startfile(test_output)
                            self.log_message(f"Opened test file: {test_output}", "info")
                        except Exception as e:
                            self.log_message(f"Error opening test file: {e}", "error")
                else:
                    raise Exception("Adaptive processing test failed")

            except Exception as e:
                self.update_progress(0, "Adaptive processing test failed")
                self.log_message(f"❌ Adaptive processing test failed: {e}", "error")
                messagebox.showerror("Test Error", f"Adaptive processing test failed: {e}")

        # Run in separate thread
        thread = threading.Thread(target=test_worker)
        thread.daemon = True
        thread.start()

    def generate_adaptive_report(self):
        """Generate report with adaptive processing and FFB analysis"""
        # Check prerequisites
        if not self.db_connected.get():
            messagebox.showerror("Not Connected", "Please connect to database first")
            return

        if not self.template_analyzed.get():
            messagebox.showerror("Template Not Analyzed", "Please analyze template first")
            return

        if not self.output_path.get():
            messagebox.showerror("Output Error", "Please specify output path")
            return

        def generate_worker():
            try:
                self.log_message("=== STARTING FFB ANALYSIS REPORT GENERATION ===", "adaptive")
                self.update_progress(5, "Initializing FFB analysis report generation...")

                # Disable generate button
                self.generate_btn.config(state="disabled")
                self.is_generating = True

                # Parse dates
                try:
                    start_date = datetime.strptime(self.start_date.get(), "%Y-%m-%d")
                    end_date = datetime.strptime(self.end_date.get(), "%Y-%m-%d")
                except ValueError as e:
                    raise ValueError(f"Invalid date format: {e}")

                self.update_progress(10, "Connecting to database...")

                # Get database connection - use the connector directly for queries
                if not self.connector:
                    raise Exception("Database connector not initialized")
                
                # For Firebird, we don't need a persistent connection object
                # The connector handles connections internally

                self.update_progress(15, "Loading employee mapping...")

                # Get employee mapping
                employee_map = self.get_employee_mapping()
                if not employee_map:
                    self.log_message("Warning: No employee mapping found", "warning")

                self.update_progress(25, "Discovering divisions...")

                # Get divisions
                divisions = self.get_divisions(self.start_date.get(), self.end_date.get())
                if not divisions:
                    raise Exception("No divisions found for the specified date range")

                self.log_message(f"Found {len(divisions)} divisions to analyze", "info")

                self.update_progress(35, "Analyzing FFB data by division...")

                # Analyze each division
                all_division_data = {}
                progress_step = 40 / len(divisions) if divisions else 0

                for i, (division_id, division_name) in enumerate(divisions):
                    self.update_progress(35 + (i * progress_step), f"Analyzing division {division_id}: {division_name}...")
                    
                    division_data = self.analyze_division(
                        division_id, division_name, 
                        self.start_date.get(), self.end_date.get(), employee_map
                    )
                    
                    if division_data:
                        all_division_data[division_id] = {
                            'name': division_name,
                            'data': division_data
                        }

                self.update_progress(75, "Preparing report data structure...")

                # Prepare comprehensive data for report
                report_data = self.prepare_ffb_report_data(all_division_data, employee_map)

                self.update_progress(80, "Executing additional queries...")

                # Execute additional queries using dynamic engine
                parameters = {
                    'start_date': self.start_date.get(),
                    'end_date': self.end_date.get(),
                    'month': f"{start_date.month:02d}"
                }

                query_results = self.dynamic_engine.execute_all_queries(parameters)
                variables = self.dynamic_engine.process_variables(query_results, parameters)

                # Combine FFB analysis data with dynamic variables
                adaptive_data = {
                    **variables,
                    **report_data
                }

                self.update_progress(90, "Generating Excel report...")

                # Generate report using adaptive processor
                success = self.adaptive_processor.generate_report(adaptive_data, self.output_path.get())

                self.update_progress(95, "Finalizing report...")

                if success:
                    self.update_progress(100, "FFB analysis report generated successfully!")
                    self.log_message(f"✅ FFB Analysis Excel report generated: {self.output_path.get()}", "success")
                    self.log_message("=== FFB ANALYSIS REPORT GENERATION COMPLETED ===", "success")

                    # Ask user if they want to open the file
                    result = messagebox.askyesno(
                        "Report Generated",
                        f"FFB Analysis Excel report generated successfully!\n\nOutput: {self.output_path.get()}\n\nDo you want to open the report?"
                    )

                    if result:
                        self.open_output_file()
                else:
                    raise Exception("FFB analysis report generation failed")

            except Exception as e:
                self.update_progress(0, "FFB analysis report generation failed")
                self.log_message(f"❌ FFB analysis report generation failed: {e}", "error")
                messagebox.showerror("Generation Error", f"Failed to generate FFB analysis report: {e}")

            finally:
                # Re-enable generate button
                self.generate_btn.config(state="normal")
                self.is_generating = False

        # Start generation in separate thread
        self.current_thread = threading.Thread(target=generate_worker, daemon=True)
        self.current_thread.start()

    def prepare_ffb_report_data(self, all_division_data, employee_map):
        """Prepare comprehensive FFB report data structure"""
        try:
            # Initialize report data structure
            report_data = {
                'divisions': [],
                'all_transactions': [],
                'summary_by_division': [],
                'employee_summary': {},
                'daily_summary': {},
                'total_summary': {
                    'total_divisions': len(all_division_data),
                    'total_transactions': 0,
                    'total_bunches': 0,
                    'total_loosefruit': 0,
                    'total_weight': 0
                }
            }

            # Process each division
            for division_id, division_info in all_division_data.items():
                division_name = division_info['name']
                division_data = division_info['data']
                
                # Add division info
                report_data['divisions'].append({
                    'division_id': division_id,
                    'division_name': division_name,
                    'transaction_count': division_data['summary']['total_transactions'],
                    'total_bunches': division_data['summary']['total_bunches'],
                    'total_loosefruit': division_data['summary']['total_loosefruit'],
                    'total_weight': division_data['summary']['total_weight']
                })

                # Add all transactions
                for transaction in division_data['transactions']:
                    transaction['division_name'] = division_name
                    report_data['all_transactions'].append(transaction)

                # Update totals
                report_data['total_summary']['total_transactions'] += division_data['summary']['total_transactions']
                report_data['total_summary']['total_bunches'] += division_data['summary']['total_bunches']
                report_data['total_summary']['total_loosefruit'] += division_data['summary']['total_loosefruit']
                report_data['total_summary']['total_weight'] += division_data['summary']['total_weight']

                # Process employee summary
                for transaction in division_data['transactions']:
                    for role in ['kerani', 'mandor', 'asisten']:
                        emp_id = transaction.get(f'{role}_id')
                        emp_name = transaction.get(f'{role}_name')
                        
                        if emp_id and emp_name:
                            if emp_id not in report_data['employee_summary']:
                                report_data['employee_summary'][emp_id] = {
                                    'name': emp_name,
                                    'role': role,
                                    'divisions': set(),
                                    'transaction_count': 0,
                                    'total_bunches': 0,
                                    'total_loosefruit': 0,
                                    'total_weight': 0
                                }
                            
                            emp_summary = report_data['employee_summary'][emp_id]
                            emp_summary['divisions'].add(division_name)
                            emp_summary['transaction_count'] += 1
                            emp_summary['total_bunches'] += transaction['bunches']
                            emp_summary['total_loosefruit'] += transaction['loosefruit']
                            emp_summary['total_weight'] += transaction['totalweight']

                # Process daily summary
                for transaction in division_data['transactions']:
                    trans_date = transaction['transdate']
                    if isinstance(trans_date, str):
                        date_key = trans_date
                    else:
                        date_key = trans_date.strftime('%Y-%m-%d') if trans_date else 'Unknown'
                    
                    if date_key not in report_data['daily_summary']:
                        report_data['daily_summary'][date_key] = {
                            'date': date_key,
                            'transaction_count': 0,
                            'total_bunches': 0,
                            'total_loosefruit': 0,
                            'total_weight': 0,
                            'divisions': set()
                        }
                    
                    daily = report_data['daily_summary'][date_key]
                    daily['transaction_count'] += 1
                    daily['total_bunches'] += transaction['bunches']
                    daily['total_loosefruit'] += transaction['loosefruit']
                    daily['total_weight'] += transaction['totalweight']
                    daily['divisions'].add(division_name)

            # Convert sets to lists for JSON serialization
            for emp_id, emp_data in report_data['employee_summary'].items():
                emp_data['divisions'] = list(emp_data['divisions'])

            for date_key, daily_data in report_data['daily_summary'].items():
                daily_data['divisions'] = list(daily_data['divisions'])

            # Convert daily summary to list
            report_data['daily_summary_list'] = list(report_data['daily_summary'].values())
            report_data['employee_summary_list'] = list(report_data['employee_summary'].values())

            self.log_message(f"Prepared report data: {len(report_data['divisions'])} divisions, {len(report_data['all_transactions'])} transactions", "info")
            
            return report_data

        except Exception as e:
            self.log_message(f"Error preparing FFB report data: {e}", "error")
            return {}

    def preview_data(self):
        """Preview data from database with complete ETL process logging"""
        if not self.db_connected.get():
            messagebox.showerror("Not Connected", "Please connect to database first")
            return

        def preview_worker():
            try:
                etl_stats = {
                    'extract': {'start_time': datetime.now(), 'queries': 0, 'rows_extracted': 0, 'success': True},
                    'transform': {'start_time': None, 'variables_processed': 0, 'calculations': 0, 'success': True},
                    'load': {'start_time': None, 'data_types': 0, 'rows_processed': 0, 'success': True}
                }

                # Initialize safe default values
                extract_duration = 0
                transform_duration = 0
                load_duration = 0
                total_duration = 0

                self.log_message("=== ETL PROCESS STARTED ===", "info")
                self.update_progress(5, "Starting ETL Process...")

                # ==================== EXTRACT PHASE ====================
                self.log_message("EXTRACT PHASE: Starting data extraction...", "info")
                etl_stats['extract']['start_time'] = datetime.now()
                self.update_progress(15, "Extract: Connecting to database...")

                # Load corrected formula data
                if not self.formula_data:
                    self.load_formula_data()

                if not self.dynamic_engine:
                    formula_path = os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        self.formula_file.get()
                    )
                    self.dynamic_engine = EnhancedDynamicFormulaEngine(formula_path, self.connector)
                    self.log_message(f"SUCCESS: Enhanced formula engine loaded: {self.formula_file.get()}", "success")

                self.update_progress(25, "Extract: Preparing query parameters...")

                # Prepare parameters
                try:
                    estate_name = getattr(self, 'estate_var', None).get() if hasattr(self, 'estate_var') else "PGE 2B"
                except:
                    estate_name = "PGE 2B"

                parameters = {
                    'start_date': self.start_date.get(),
                    'end_date': self.end_date.get(),
                    'month': f"{datetime.strptime(self.start_date.get(), '%Y-%m-%d').month:02d}",
                    'estate_name': estate_name,
                    'estate_code': estate_name.replace(' ', '_')
                }

                self.log_message(f"PARAMETERS: {len(parameters)} parameters prepared", "info")
                for param, value in parameters.items():
                    self.log_message(f"   - {param}: {value}", "info")

                self.update_progress(40, "Extract: Executing database queries...")
                self.log_message("EXECUTING database queries...", "info")

                # Execute queries with detailed logging
                extract_start = datetime.now()
                
                # Get FFB Scanner data using corrected table names
                ffb_data = self.get_ffb_scanner_preview_data(parameters['start_date'], parameters['end_date'])
                
                # Execute other queries
                query_results = self.dynamic_engine.execute_all_queries(parameters)
                query_results['ffb_scanner_data'] = ffb_data
                
                extract_end = datetime.now()
                extract_duration = (extract_end - extract_start).total_seconds() if extract_start else 0

                # Calculate extraction statistics
                etl_stats['extract']['queries'] = len(query_results)
                etl_stats['extract']['rows_extracted'] = sum(len(results) if results else 0 for results in query_results.values())

                self.log_message(f"SUCCESS: EXTRACT COMPLETED: {etl_stats['extract']['queries']} queries in {extract_duration:.2f}s", "success")
                self.log_message(f"RESULTS: Extraction Results: {etl_stats['extract']['rows_extracted']} total rows extracted", "info")

                for query_name, results in query_results.items():
                    row_count = len(results) if results else 0
                    status = "SUCCESS" if row_count > 0 else "WARNING"
                    self.log_message(f"   {status}: {query_name}: {row_count} rows", "info")

                # ==================== TRANSFORM PHASE ====================
                try:
                    self.log_message("TRANSFORM PHASE: Starting data transformation...", "info")
                    etl_stats['transform']['start_time'] = datetime.now()
                    self.update_progress(60, "Transform: Processing variables and calculations...")

                    # Process variables
                    transform_start = datetime.now()
                    variables = self.dynamic_engine.process_variables(query_results, parameters)
                    etl_stats['transform']['variables_processed'] = len(variables)

                    # Get repeating data
                    repeating_data = self.dynamic_engine.get_repeating_data(query_results)
                    etl_stats['transform']['calculations'] = len(repeating_data)
                    transform_end = datetime.now()
                    transform_duration = (transform_end - transform_start).total_seconds() if transform_start else 0

                    self.log_message(f"SUCCESS: TRANSFORM COMPLETED: {transform_duration:.2f}s", "success")
                except Exception as transform_error:
                    self.log_message(f"ERROR: Transform phase failed: {transform_error}", "error")
                    variables = {}
                    repeating_data = {}
                    etl_stats['transform']['success'] = False
                    transform_duration = 0
                self.log_message(f"RESULTS: Transformation Results:", "info")
                self.log_message(f"   - Variables processed: {etl_stats['transform']['variables_processed']}", "info")
                self.log_message(f"   - Data calculations: {etl_stats['transform']['calculations']}", "info")

                # ==================== LOAD PHASE ====================
                try:
                    self.log_message("LOAD PHASE: Preparing data for display...", "info")
                    etl_stats['load']['start_time'] = datetime.now()
                    self.update_progress(80, "Load: Preparing preview display...")

                    # Calculate load statistics
                    etl_stats['load']['data_types'] = len(repeating_data)
                    etl_stats['load']['rows_processed'] = sum(len(data_list) if data_list else 0 for data_list in repeating_data.values())

                    load_end = datetime.now()
                    load_duration = (load_end - etl_stats['load']['start_time']).total_seconds() if etl_stats['load']['start_time'] else 0

                    # Calculate total duration safely
                    if etl_stats['extract']['start_time']:
                        total_duration = (load_end - etl_stats['extract']['start_time']).total_seconds()
                    else:
                        total_duration = 0

                    self.log_message(f"SUCCESS: LOAD COMPLETED: {load_duration:.2f}s", "success")
                except Exception as load_error:
                    self.log_message(f"ERROR: Load phase failed: {load_error}", "error")
                    etl_stats['load']['success'] = False
                    load_duration = 0
                    total_duration = 0
                self.log_message(f"RESULTS: Load Results: {etl_stats['load']['data_types']} data types, {etl_stats['load']['rows_processed']} rows processed", "info")

                # ==================== COMPREHENSIVE PREVIEW ====================
                self.update_progress(90, "Generating comprehensive preview...")

                preview_text = "ETL PROCESS REPORT\n"
                preview_text += "=" * 80 + "\n\n"

                # ETL Summary
                preview_text += "ETL EXECUTION SUMMARY:\n"
                preview_text += "-" * 40 + "\n"
                preview_text += f"Total Duration: {total_duration:.3f} seconds\n"

                # Safe percentage calculations
                extract_pct = (extract_duration/total_duration*100) if total_duration > 0 else 0
                transform_pct = (transform_duration/total_duration*100) if total_duration > 0 else 0
                load_pct = (load_duration/total_duration*100) if total_duration > 0 else 0

                preview_text += f"Extract Phase: {extract_duration:.3f}s ({extract_pct:.1f}%)\n"
                preview_text += f"Transform Phase: {transform_duration:.3f}s ({transform_pct:.1f}%)\n"
                preview_text += f"Load Phase: {load_duration:.3f}s ({load_pct:.1f}%)\n\n"

                # Extract Details
                preview_text += "EXTRACT PHASE DETAILS:\n"
                preview_text += "-" * 40 + "\n"
                preview_text += f"Database: {self.db_path.get()}\n"
                preview_text += f"Date Range: {parameters['start_date']} to {parameters['end_date']}\n"
                preview_text += f"Queries Executed: {etl_stats['extract']['queries']}\n"
                preview_text += f"Rows Extracted: {etl_stats['extract']['rows_extracted']:,}\n"
                extract_rate = (etl_stats['extract']['rows_extracted']/extract_duration) if extract_duration > 0 else 0
                preview_text += f"Extract Rate: {extract_rate:,.0f} rows/second\n\n"

                preview_text += "Query Breakdown:\n"
                for query_name, results in query_results.items():
                    row_count = len(results) if results else 0
                    status = "SUCCESS" if row_count > 0 else "WARNING"
                    preview_text += f"   {status}: {query_name}: {row_count:,} rows\n"
                preview_text += "\n"

                # Transform Details
                preview_text += "TRANSFORM PHASE DETAILS:\n"
                preview_text += "-" * 40 + "\n"
                preview_text += f"Variables Processed: {etl_stats['transform']['variables_processed']}\n"
                preview_text += f"Calculations Performed: {etl_stats['transform']['calculations']}\n"
                transform_rate = (etl_stats['transform']['variables_processed']/transform_duration) if transform_duration > 0 else 0
                preview_text += f"Transform Rate: {transform_rate:,.0f} variables/second\n\n"

                preview_text += "Processed Variables:\n"
                for var_name, var_value in variables.items():
                    preview_text += f"   - {var_name}: {var_value}\n"
                preview_text += "\n"

                # Load Details
                preview_text += "LOAD PHASE DETAILS:\n"
                preview_text += "-" * 40 + "\n"
                preview_text += f"Data Types Loaded: {etl_stats['load']['data_types']}\n"
                preview_text += f"Rows Processed: {etl_stats['load']['rows_processed']:,}\n"
                load_rate = (etl_stats['load']['rows_processed']/load_duration) if load_duration > 0 else 0
                preview_text += f"Load Rate: {load_rate:,.0f} rows/second\n\n"

                preview_text += "Data Types Breakdown:\n"
                for data_type, data_list in repeating_data.items():
                    row_count = len(data_list) if data_list else 0
                    status = "SUCCESS" if row_count > 0 else "WARNING"
                    preview_text += f"   {status}: {data_type.upper()}: {row_count:,} rows\n"
                preview_text += "\n"

                # Sample Data
                preview_text += "SAMPLE DATA (First 3 rows per type):\n"
                preview_text += "-" * 50 + "\n"

                # Add FFB Scanner Data section first
                if 'ffb_scanner_data' in query_results and query_results['ffb_scanner_data']:
                    ffb_data = query_results['ffb_scanner_data']
                    preview_text += f"\nFFB SCANNER DATA ({len(ffb_data):,} rows total):\n"
                    preview_text += "Using corrected FFBSCANNERDATA tables (not FFBLOADINGCROP)\n"
                    for i, row in enumerate(ffb_data[:3]):
                        preview_text += f"   Row {i+1}:\n"
                        for key, value in row.items():
                            preview_text += f"      {key}: {value}\n"
                    if len(ffb_data) > 3:
                        preview_text += f"   ... and {len(ffb_data) - 3:,} more rows\n"
                else:
                    preview_text += f"\nFFB SCANNER DATA: No data available\n"

                for data_type, data_list in repeating_data.items():
                    if data_list:
                        preview_text += f"\n{data_type.upper()} ({len(data_list):,} rows total):\n"
                        for i, row in enumerate(data_list[:3]):
                            preview_text += f"   Row {i+1}: {row}\n"
                        if len(data_list) > 3:
                            preview_text += f"   ... and {len(data_list) - 3:,} more rows\n"
                    else:
                        preview_text += f"\n{data_type.upper()}: No data available\n"

                preview_text += "\n" + "=" * 80 + "\n"
                preview_text += f"PERFORMANCE METRICS:\n"
                overall_throughput = (etl_stats['extract']['rows_extracted']/total_duration) if total_duration > 0 else 0
                data_quality_pct = (etl_stats['load']['rows_processed']/etl_stats['extract']['rows_extracted']*100) if etl_stats['extract']['rows_extracted'] > 0 else 0

                preview_text += f"   - Overall Throughput: {overall_throughput:,.0f} rows/second\n"
                preview_text += f"   - Success Rate: 100% ({etl_stats['extract']['queries']}/{etl_stats['extract']['queries']} queries)\n"
                preview_text += f"   - Data Quality: {data_quality_pct:.1f}% data retained\n"

                self.update_progress(100, "ETL Process Completed Successfully")
                self.log_message("=== ETL PROCESS COMPLETED SUCCESSFULLY ===", "success")
                self.log_message(f"FINAL SUMMARY: {etl_stats['extract']['rows_extracted']:,} rows extracted, {etl_stats['load']['rows_processed']:,} rows loaded in {total_duration:.3f}s", "success")

                # Save ETL report to file
                self.save_etl_report_to_file(preview_text, etl_stats, parameters, query_results)

                # Show comprehensive preview dialog
                self.show_preview_dialog("ETL Process Report - Data Preview", preview_text)

            except Exception as e:
                self.update_progress(0, "ETL Process Failed")
                self.log_message(f"=== ETL PROCESS FAILED: {e} ===", "error")
                messagebox.showerror("ETL Process Error", f"Failed to complete ETL process: {e}")

        # Run in separate thread
        thread = threading.Thread(target=preview_worker)
        thread.daemon = True
        thread.start()

    def browse_database(self):
        """Browse for database file"""
        filename = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("Firebird Database", "*.fdb"), ("All Files", "*.*")]
        )
        if filename:
            self.db_path.set(filename)
            self.check_database_connection()

    def select_database(self):
        """Select from available production databases"""
        try:
            selector = DatabaseSelector()
            selected_db = selector.select_database()
            if selected_db:
                self.db_path.set(selected_db)
                self.check_database_connection()
                self.log_message(f"Selected database: {os.path.basename(selected_db)}")
        except Exception as e:
            messagebox.showerror("Database Selection Error", f"Failed to select database: {e}")
            self.log_message(f"Database selection error: {e}", "error")

    def browse_template(self):
        """Browse for template file"""
        filename = filedialog.askopenfilename(
            title="Select Template File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")],
            initialdir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        )
        if filename:
            self.template_path.set(filename)
            self.template_analyzed.set(False)
            self.update_analysis_indicator(False)

    def browse_formula(self):
        """Browse for formula file"""
        filename = filedialog.askopenfilename(
            title="Select Formula File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialdir=os.path.dirname(os.path.abspath(__file__))
        )
        if filename:
            # Get relative path
            rel_path = os.path.relpath(filename, os.path.dirname(os.path.abspath(__file__)))
            self.formula_file.set(rel_path)
            # Reset dynamic engine to force reload with new formula
            self.dynamic_engine = None
            self.log_message(f"Formula file changed to: {rel_path}", "info")

    def browse_output(self):
        """Browse for output file"""
        filename = filedialog.asksaveasfilename(
            title="Save Report As",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
            initialfile=f"Adaptive_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        if filename:
            self.output_path.set(filename)

    def auto_generate_filename(self, enabled):
        """Auto-generate filename with timestamp"""
        if enabled:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"Adaptive_Report_{timestamp}.xlsx"
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            self.output_path.set(os.path.join(desktop_path, filename))

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
            # Find last day of previous month
            next_month = now.replace(month=now.month, day=1)
            end_date = next_month - timedelta(days=1)

        self.start_date.set(start_date.strftime("%Y-%m-%d"))
        self.end_date.set(end_date.strftime("%Y-%m-%d"))

    def set_custom_range(self):
        """Set custom date range"""
        # Create simple dialog for custom date input
        dialog = tk.Toplevel(self.root)
        dialog.title("Custom Date Range")
        dialog.geometry("400x200")
        dialog.configure(bg='#f0f0f0')

        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()

        # Date inputs
        ttk.Label(dialog, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=20, pady=20, sticky=tk.W)
        start_entry = ttk.Entry(dialog, width=20)
        start_entry.grid(row=0, column=1, padx=20, pady=20)
        start_entry.insert(0, self.start_date.get())

        ttk.Label(dialog, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)
        end_entry = ttk.Entry(dialog, width=20)
        end_entry.grid(row=1, column=1, padx=20, pady=10)
        end_entry.insert(0, self.end_date.get())

        def apply_custom_range():
            try:
                # Validate dates
                start_str = start_entry.get().strip()
                end_str = end_entry.get().strip()

                start_date = datetime.strptime(start_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_str, "%Y-%m-%d")

                if start_date > end_date:
                    messagebox.showerror("Invalid Range", "Start date cannot be after end date")
                    return

                self.start_date.set(start_str)
                self.end_date.set(end_str)
                dialog.destroy()

            except ValueError:
                messagebox.showerror("Invalid Format", "Please use YYYY-MM-DD format")

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Apply", command=apply_custom_range).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def update_progress(self, value, message=""):
        """Update progress bar and label"""
        self.progress_var.set(value)
        if message:
            self.progress_label.config(text=message)
        self.status_label.config(text=f"Status: {message}")
        self.root.update_idletasks()

    def log_message(self, message, level="info"):
        """Add message to log with formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_entry, level)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """Clear log text"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log cleared", "info")

    def show_preview_dialog(self, title, content):
        """Show preview dialog with text content"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("900x700")
        dialog.configure(bg='#f0f0f0')

        # Create text widget with scrollbar
        text_frame = ttk.Frame(dialog, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)

        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Insert content
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)

        # Close button
        close_btn = ttk.Button(dialog, text="Close", command=dialog.destroy)
        close_btn.pack(pady=10)

        # Export button
        export_btn = ttk.Button(dialog, text="Export Report", command=lambda: self.export_etl_report(content))
        export_btn.pack(pady=5)

    def save_etl_report_to_file(self, preview_text, etl_stats, parameters, query_results):
        """Save ETL report to file"""
        try:
            # Create reports directory if it doesn't exist
            reports_dir = "etl_reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{reports_dir}/ETL_Report_{parameters.get('estate_name', 'Unknown')}_{timestamp}.txt"

            # Save detailed report
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(preview_text)
                f.write("\n\n" + "=" * 80 + "\n")
                f.write("🔍 DETAILED QUERY RESULTS\n")
                f.write("=" * 80 + "\n\n")

                for query_name, results in query_results.items():
                    f.write(f"\n{query_name.upper()}:\n")
                    f.write("-" * 40 + "\n")
                    if results and len(results) > 0:
                        f.write(f"Total Rows: {len(results)}\n\n")
                        for i, row in enumerate(results[:10]):  # Show first 10 rows
                            f.write(f"Row {i+1}: {row}\n")
                        if len(results) > 10:
                            f.write(f"... and {len(results) - 10} more rows\n")
                    else:
                        f.write("No data returned\n")

            self.log_message(f"REPORT: ETL report saved to: {filename}", "success")

            # Also save as JSON for machine reading
            json_filename = filename.replace('.txt', '.json')
            etl_data = {
                'timestamp': datetime.now().isoformat(),
                'parameters': parameters,
                'etl_stats': etl_stats,
                'query_results': {k: v for k, v in query_results.items()},
                'summary': {
                    'total_queries': etl_stats['extract']['queries'],
                    'total_rows_extracted': etl_stats['extract']['rows_extracted'],
                    'total_rows_processed': etl_stats['load']['rows_processed'],
                    'extract_duration': (etl_stats['transform']['start_time'] - etl_stats['extract']['start_time']).total_seconds() if etl_stats['transform']['start_time'] else 0,
                    'transform_duration': 0,
                    'load_duration': 0,
                    'total_duration': 0
                }
            }

            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(etl_data, f, indent=2, ensure_ascii=False, default=str)

            self.log_message(f"REPORT: ETL JSON report saved to: {json_filename}", "success")

        except Exception as e:
            self.log_message(f"ERROR: Failed to save ETL report: {e}", "error")

    def export_etl_report(self, content):
        """Export ETL report to user-selected location"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")],
                title="Save ETL Report"
            )

            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Export Successful", f"ETL report saved to:\n{filename}")
                self.log_message(f"REPORT: ETL report exported by user: {filename}", "success")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export ETL report: {e}")
            self.log_message(f"ERROR: Failed to export ETL report: {e}", "error")

    def open_settings(self):
        """Open settings dialog"""
        messagebox.showinfo("Settings", "Settings functionality not implemented yet")

    def show_help(self):
        """Show help dialog"""
        help_text = """
Adaptive Report Generator Help

ADAPTIVE FEATURES:
- Automatic template analysis and structure detection
- Support for multiple placeholder formats: {{variable}}, {$variable$}, {variable}, [variable]
- Dynamic table detection and expansion
- Template row pattern recognition
- Formatting preservation from template
- Flexible data mapping with intelligent lookup

TEMPLATE FLEXIBILITY:
- System analyzes template structure automatically
- Detects repeating sections and tables
- Preserves all Excel formatting (fonts, colors, borders)
- Handles any template layout without code changes
- Supports multiple sheets with different structures

DATABASE PROCESSING:
- Real Firebird database connectivity
- Dynamic SQL query execution
- Real-time data aggregation
- Multi-table data processing
- Automatic date range handling

PLACEHOLDER PROCESSING:
- Multiple placeholder format support
- Case-insensitive variable matching
- Partial string matching for flexibility
- Nested data structure support
- Default values for common placeholders

VALIDATION SYSTEM:
- Comprehensive template validation
- Database connection testing
- Data completeness checking
- Adaptive processing testing
- Error reporting with details

USAGE STEPS:
1. Connect to Firebird database
2. Select and analyze Excel template
3. Validate system components
4. Generate adaptive report

TEMPLATE REQUIREMENTS:
- Excel file (.xlsx or .xls)
- Placeholders in any supported format
- Optional: Repeating rows for data tables
- Optional: Header rows for table structure

TROUBLESHOOTING:
- Ensure template file exists and is readable
- Check database connection before generation
- Use 'Test Adaptive' to verify processing
- Check logs for detailed error information
- Validate template structure if issues occur

ADAPTIVE ADVANTAGES:
- No code changes needed for template updates
- Automatic detection of template changes
- Flexible data mapping capabilities
- Preserves Excel formatting and layout
- Handles complex nested data structures
        """

        self.show_preview_dialog("Adaptive Report Generator Help", help_text)

    def open_output_file(self):
        """Open the generated output file"""
        try:
            if os.path.exists(self.output_path.get()):
                os.startfile(self.output_path.get())
                self.log_message(f"Opened output file: {self.output_path.get()}", "info")
            else:
                messagebox.showerror("File Not Found", f"Output file not found: {self.output_path.get()}")
        except Exception as e:
            self.log_message(f"Error opening file: {e}", "error")
            messagebox.showerror("Error", f"Failed to open file: {e}")

    def get_employee_mapping(self):
        """Get employee mapping from EMP table using template query"""
        try:
            # Try to get query from template first
            query = self.get_query_from_template('employee_mapping')
            if not query:
                # Fallback to hardcoded query if template not available
                query = """
                SELECT EMPID, EMPNAME, EMPTYPE, EMPPOSITION, DIVISIONID
                FROM EMP
                WHERE EMPSTATUS = 'A'
                ORDER BY EMPID
                """
            
            # Use helper function to extract data properly
            results = execute_query_with_extraction(self.connector, query)
            
            employee_map = {}
            for row in results:
                normalized_row = normalize_data_row(row)
                empid = normalized_row.get('EMPID')
                empname = normalized_row.get('EMPNAME')
                emptype = normalized_row.get('EMPTYPE')
                empposition = normalized_row.get('EMPPOSITION')
                divisionid = normalized_row.get('DIVISIONID')
                
                if empid:  # Only add if we have a valid employee ID
                    employee_map[empid] = {
                        'name': empname or 'Unknown',
                        'type': emptype or 'Unknown',
                        'position': empposition or 'Unknown',
                        'division': divisionid or 'Unknown'
                    }
            
            self.log_message(f"Loaded {len(employee_map)} employee records", "info")
            return employee_map
            
        except Exception as e:
            self.log_message(f"Error getting employee mapping: {e}", "error")
            return {}

    def get_ffb_scanner_preview_data(self, start_date, end_date):
        """Get FFB Scanner data preview using corrected FFBSCANNERDATA tables"""
        try:
            current_date = datetime.strptime(start_date, '%Y-%m-%d')
            table_name = f"FFBSCANNERDATA{current_date.month:02d}"
            
            # Query to get sample FFB scanner data with proper structure handling
            query = f"""
            SELECT FIRST 10
                SCANUSERID,
                WORKERID,
                CARRIERID,
                FIELDID,
                RIPEBCH,
                UNRIPEBCH,
                TRANSDATE,
                TRANSTIME,
                TRANSSTATUS
            FROM {table_name}
            WHERE TRANSDATE BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY TRANSDATE DESC, TRANSTIME DESC
            """
            
            # Use the new helper function to properly extract data
            data = execute_query_with_extraction(self.connector, query)
            
            # Normalize the data
            normalized_data = []
            for row in data:
                normalized_row = normalize_data_row(row)
                normalized_data.append(normalized_row)
            
            self.log_message(f"SUCCESS: FFB Scanner data retrieved from {table_name}: {len(normalized_data)} rows", "success")
            return normalized_data
            
        except Exception as e:
            self.log_message(f"ERROR: Failed to get FFB scanner data: {str(e)}", "error")
            return []

    def get_divisions(self, start_date, end_date):
        """Get divisions from FFBSCANNERDATA tables within date range using template query"""
        try:
            divisions = set()
            
            # Generate table names for the date range
            current_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            
            table_names = []
            while current_date <= end_date_obj:
                table_name = f"FFBSCANNERDATA{current_date.month:02d}"
                if table_name not in table_names:
                    table_names.append((table_name, current_date.month))
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            # Query each table for divisions
            for table_name, month in table_names:
                try:
                    # Try to get query from template first
                    query = self.get_query_from_template('division_list', 
                                                       month=month, 
                                                       start_date=start_date, 
                                                       end_date=end_date)
                    if not query:
                        # Fallback to hardcoded query with proper structure
                        query = f"""
                        SELECT DISTINCT 
                            f.FIELDID as DIVID,
                            o.FIELDNAME as DIVNAME
                        FROM {table_name} f
                        LEFT JOIN OCFIELD o ON f.FIELDID = o.ID
                        WHERE f.TRANSDATE BETWEEN '{start_date}' AND '{end_date}'
                        AND f.FIELDID IS NOT NULL 
                        AND o.FIELDNAME IS NOT NULL
                        ORDER BY f.FIELDID
                        """
                    
                    # Use helper function to extract data properly
                    results = execute_query_with_extraction(self.connector, query)
                    
                    for row in results:
                        normalized_row = normalize_data_row(row)
                        div_id = normalized_row.get('DIVID') or normalized_row.get('FIELDID')
                        div_name = normalized_row.get('DIVNAME') or normalized_row.get('FIELDNAME')
                        if div_id and div_name:
                            divisions.add((div_id, div_name))
                        
                except Exception as table_error:
                    self.log_message(f"Warning: Could not query table {table_name}: {table_error}", "warning")
                    continue
            
            division_list = list(divisions)
            self.log_message(f"Found {len(division_list)} divisions", "info")
            return division_list
            
        except Exception as e:
            self.log_message(f"Error getting divisions: {e}", "error")
            return []

    def analyze_division(self, division_id, division_name, start_date, end_date, employee_map):
        """Analyze FFB data for a specific division using template query"""
        try:
            # Generate table names for the date range
            current_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            
            table_names = []
            while current_date <= end_date_obj:
                table_name = f"FFBSCANNERDATA{current_date.month:02d}"
                if table_name not in table_names:
                    table_names.append((table_name, current_date.month))
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            all_data = []
            
            # Query each table
            for table_name, month in table_names:
                try:
                    # Try to get query from template first
                    query = self.get_query_from_template('division_data', 
                                                       month=month, 
                                                       div_id=division_id,
                                                       start_date=start_date, 
                                                       end_date=end_date)
                    if not query:
                        # Fallback to hardcoded query with proper FFBSCANNERDATA structure
                        query = f"""
                        SELECT f.ID, f.SCANUSERID, f.OCID, f.WORKERID, f.CARRIERID, f.FIELDID, 
                               f.TASKNO, f.RIPEBCH, f.UNRIPEBCH, f.BLACKBCH, f.ROTTENBCH, 
                               f.LONGSTALKBCH, f.RATDMGBCH, f.LOOSEFRUIT, f.TRANSNO, 
                               f.TRANSDATE, f.TRANSTIME, f.UPLOADDATETIME, f.RECORDTAG, 
                               f.TRANSSTATUS, f.TRANSTYPE, f.LASTUSER, f.LASTUPDATED, 
                               f.OVERRIPEBCH, f.UNDERRIPEBCH, f.ABNORMALBCH, f.LOOSEFRUIT2
                        FROM {table_name} f 
                        LEFT JOIN OCFIELD o ON f.FIELDID = o.ID 
                        WHERE o.DIVID = '{division_id}'
                        AND f.TRANSDATE BETWEEN '{start_date}' AND '{end_date}'
                        ORDER BY f.TRANSDATE, f.TRANSTIME
                        """
                    
                    # Use helper function to extract data properly
                    results = execute_query_with_extraction(self.connector, query)
                    
                    for row in results:
                        normalized_row = normalize_data_row(row)
                        all_data.append({
                            'table': table_name,
                            'id': normalized_row.get('ID'),
                            'scanuserid': normalized_row.get('SCANUSERID'),
                            'ocid': normalized_row.get('OCID'),
                            'workerid': normalized_row.get('WORKERID'),
                            'carrierid': normalized_row.get('CARRIERID'),
                            'fieldid': normalized_row.get('FIELDID'),
                            'taskno': normalized_row.get('TASKNO'),
                            'ripebch': normalized_row.get('RIPEBCH', 0),
                            'unripebch': normalized_row.get('UNRIPEBCH', 0),
                            'blackbch': normalized_row.get('BLACKBCH', 0),
                            'rottenbch': normalized_row.get('ROTTENBCH', 0),
                            'longstalkbch': normalized_row.get('LONGSTALKBCH', 0),
                            'ratdmgbch': normalized_row.get('RATDMGBCH', 0),
                            'loosefruit': normalized_row.get('LOOSEFRUIT', 0),
                            'transno': normalized_row.get('TRANSNO'),
                            'transdate': normalized_row.get('TRANSDATE'),
                            'transtime': normalized_row.get('TRANSTIME'),
                            'uploaddatetime': normalized_row.get('UPLOADDATETIME'),
                            'recordtag': normalized_row.get('RECORDTAG'),
                            'transstatus': normalized_row.get('TRANSSTATUS'),
                            'transtype': normalized_row.get('TRANSTYPE'),
                            'lastuser': normalized_row.get('LASTUSER'),
                            'lastupdated': normalized_row.get('LASTUPDATED'),
                            'overripebch': normalized_row.get('OVERRIPEBCH', 0),
                            'underripebch': normalized_row.get('UNDERRIPEBCH', 0),
                            'abnormalbch': normalized_row.get('ABNORMALBCH', 0),
                            'loosefruit2': normalized_row.get('LOOSEFRUIT2', 0)
                        })
                        
                except Exception as table_error:
                    self.log_message(f"Warning: Could not query table {table_name}: {table_error}", "warning")
                    continue
            
            # Process the data to calculate employee details
            processed_data = self.process_division_data(all_data, employee_map, division_id, start_date, end_date)
            
            return processed_data
            
        except Exception as e:
            self.log_message(f"Error analyzing division {division_id}: {e}", "error")
            return {}

    def process_division_data(self, raw_data, employee_map, division_id, start_date, end_date):
        """Process raw division data to calculate employee details"""
        try:
            # Group by transaction number to handle duplicates
            transactions = {}
            
            for record in raw_data:
                transno = record['transno']
                if transno not in transactions:
                    transactions[transno] = []
                transactions[transno].append(record)
            
            # Calculate employee details for each transaction
            processed_transactions = []
            
            for transno, records in transactions.items():
                # Find the main record (usually RECORDTAG = 1)
                main_record = None
                for record in records:
                    if record['recordtag'] == 1:
                        main_record = record
                        break
                
                if not main_record:
                    main_record = records[0]  # Fallback to first record
                
                # Calculate employee details
                kerani_id = None
                mandor_id = None
                asisten_id = None
                
                # Find employees based on SCANUSERID and employee hierarchy
                scanner_id = main_record['scanuserid']
                if scanner_id and scanner_id in employee_map:
                    emp_info = employee_map[scanner_id]
                    position = emp_info.get('position', '').upper()
                    
                    if 'KERANI' in position:
                        kerani_id = scanner_id
                    elif 'MANDOR' in position:
                        mandor_id = scanner_id
                    elif 'ASISTEN' in position:
                        asisten_id = scanner_id
                
                # Handle special case for TRANSSTATUS = 704 (if needed)
                apply_704_filter = False
                if main_record['transstatus'] == 704:
                    # Apply special filtering logic if needed
                    apply_704_filter = True
                
                processed_record = {
                    'transdate': main_record['transdate'],
                    'transno': transno,
                    'division_id': division_id,
                    'driverid': main_record['driverid'],
                    'vehicleid': main_record['vehicleid'],
                    'bunches': sum(r['bunches'] for r in records),
                    'loosefruit': sum(r['loosefruit'] for r in records),
                    'totalweight': sum(r['totalweight'] for r in records),
                    'kerani_id': kerani_id,
                    'mandor_id': mandor_id,
                    'asisten_id': asisten_id,
                    'kerani_name': employee_map.get(kerani_id, {}).get('name', '') if kerani_id else '',
                    'mandor_name': employee_map.get(mandor_id, {}).get('name', '') if mandor_id else '',
                    'asisten_name': employee_map.get(asisten_id, {}).get('name', '') if asisten_id else '',
                    'transstatus': main_record['transstatus'],
                    'apply_704_filter': apply_704_filter
                }
                
                processed_transactions.append(processed_record)
            
            # Calculate summary statistics
            total_bunches = sum(t['bunches'] for t in processed_transactions)
            total_loosefruit = sum(t['loosefruit'] for t in processed_transactions)
            total_weight = sum(t['totalweight'] for t in processed_transactions)
            
            result = {
                'division_id': division_id,
                'transactions': processed_transactions,
                'summary': {
                    'total_transactions': len(processed_transactions),
                    'total_bunches': total_bunches,
                    'total_loosefruit': total_loosefruit,
                    'total_weight': total_weight,
                    'date_range': f"{start_date} to {end_date}"
                }
            }
            
            self.log_message(f"Processed {len(processed_transactions)} transactions for division {division_id}", "info")
            return result
            
        except Exception as e:
            self.log_message(f"Error processing division data: {e}", "error")
            return {}


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
    app = AdaptiveReportGeneratorGUI(root)

    # Handle window closing
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start application
    root.mainloop()


if __name__ == "__main__":
    main()