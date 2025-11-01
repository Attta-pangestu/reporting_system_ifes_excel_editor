#!/usr/bin/env python3
"""
Simple Report Editor - Main Application
FFB Report Generator with Template Engine and PDF Export

Usage:
    python main_app.py
"""

import sys
import os
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_report_editor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function"""
    try:
        logger.info("Starting Simple Report Editor...")

        # Import GUI components
        try:
            from gui.main_window import MainWindow
        except ImportError as e:
            logger.error(f"Error importing GUI components: {e}")
            logger.error("Please ensure all required modules are installed:")
            logger.error("pip install -r requirements.txt")
            return

        # Create and run main application
        app = MainWindow()
        app.run()

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        import tkinter as tk
        from tkinter import messagebox

        # Show error message if possible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Fatal Error", f"Application failed to start:\n{e}")
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    main()