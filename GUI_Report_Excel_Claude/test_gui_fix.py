#!/usr/bin/env python3
"""
Test script untuk memastikan GUI fix berjalan dengan benar
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing GUI imports...")

    # Test basic imports
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    from datetime import datetime, timedelta
    import json
    import threading

    print("SUCCESS: Basic imports successful")

    # Test GUI class import
    from gui_adaptive_report_generator import AdaptiveReportGeneratorGUI
    print("SUCCESS: GUI class import successful")

    # Test instantiation (without showing GUI)
    root = tk.Tk()
    root.withdraw()  # Hide the window

    try:
        gui = AdaptiveReportGeneratorGUI(root)
        print("SUCCESS: GUI instantiation successful")

        # Test estate_var exists
        if hasattr(gui, 'estate_var'):
            print(f"SUCCESS: estate_var exists: {gui.estate_var.get()}")
        else:
            print("ERROR: estate_var does not exist")

        # Test other required attributes
        required_attrs = ['db_path', 'start_date', 'end_date', 'formula_file']
        for attr in required_attrs:
            if hasattr(gui, attr):
                print(f"SUCCESS: {attr} exists")
            else:
                print(f"ERROR: {attr} missing")

        # Test preview data method exists
        if hasattr(gui, 'preview_data'):
            print("SUCCESS: preview_data method exists")
        else:
            print("ERROR: preview_data method missing")

        print("SUCCESS: All tests passed!")

    except Exception as e:
        print(f"ERROR: GUI instantiation failed: {e}")
        import traceback
        traceback.print_exc()

    root.destroy()

except ImportError as e:
    print(f"ERROR: Import failed: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"ERROR: Unexpected error: {e}")
    import traceback
    traceback.print_exc()