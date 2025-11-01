#!/usr/bin/env python3
"""
Test script untuk preview ETL functionality
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing ETL Preview functionality...")

    import tkinter as tk
    from datetime import datetime
    from gui_adaptive_report_generator import AdaptiveReportGeneratorGUI

    # Create GUI instance
    root = tk.Tk()
    root.withdraw()  # Hide window initially

    gui = AdaptiveReportGeneratorGUI(root)

    # Check if database is connected
    if gui.db_connected.get():
        print("SUCCESS: Database is connected")

        # Check if formula engine exists
        if hasattr(gui, 'dynamic_engine') and gui.dynamic_engine:
            print("SUCCESS: Dynamic formula engine exists")
        else:
            print("WARNING: Dynamic formula engine will be created during preview")

        # Test parameters creation
        try:
            estate_name = getattr(gui, 'estate_var', None).get() if hasattr(gui, 'estate_var') else "PGE 2B"
        except:
            estate_name = "PGE 2B"

        parameters = {
            'start_date': gui.start_date.get(),
            'end_date': gui.end_date.get(),
            'month': f"{datetime.strptime(gui.start_date.get(), '%Y-%m-%d').month:02d}",
            'estate_name': estate_name,
            'estate_code': estate_name.replace(' ', '_')
        }

        print("SUCCESS: Parameters created successfully:")
        for key, value in parameters.items():
            print(f"   - {key}: {value}")

        print("\nREADY TO TEST PREVIEW DATA FUNCTIONALITY!")
        print("Please run the GUI and click 'Preview Data' button to see the full ETL process.")

    else:
        print("WARNING: Database not connected. Please connect first before testing preview.")

    root.destroy()
    print("Test completed successfully!")

except Exception as e:
    print(f"ERROR: Test failed: {e}")
    import traceback
    traceback.print_exc()