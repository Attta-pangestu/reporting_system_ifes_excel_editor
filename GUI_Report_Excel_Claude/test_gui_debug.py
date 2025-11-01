#!/usr/bin/env python3
"""
Debug script to test GUI initialization and catch errors
"""

import sys
import traceback

try:
    print("Starting GUI debug test...")
    
    # Test imports
    print("Testing imports...")
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    print("Tkinter imports OK")
    
    import threading
    import os
    from datetime import datetime, timedelta
    import json
    import logging
    print("Standard library imports OK")
    
    # Add current directory to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from firebird_connector_enhanced import FirebirdConnectorEnhanced
    print("FirebirdConnectorEnhanced import OK")
    
    from dynamic_formula_engine_enhanced import EnhancedDynamicFormulaEngine
    print("EnhancedDynamicFormulaEngine import OK")
    
    from adaptive_excel_processor import AdaptiveExcelProcessor
    print("AdaptiveExcelProcessor import OK")
    
    print("All imports successful!")
    
    # Test GUI initialization
    print("Testing GUI initialization...")
    root = tk.Tk()
    root.withdraw()  # Hide the window for testing
    
    # Import and test the GUI class
    from gui_adaptive_report_generator import AdaptiveReportGeneratorGUI
    print("GUI class import OK")
    
    # Try to create the GUI instance
    app = AdaptiveReportGeneratorGUI(root)
    print("GUI instance created successfully!")
    
    root.destroy()
    print("GUI test completed successfully!")
    
except Exception as e:
    print(f"Error occurred: {e}")
    print("Full traceback:")
    traceback.print_exc()
    sys.exit(1)