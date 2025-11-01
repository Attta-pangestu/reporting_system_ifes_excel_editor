#!/usr/bin/env python3
"""
Test script for database selector functionality
Tests the DatabaseSelector class and its integration with the GUI
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database_selector import DatabaseSelector
    from firebird_connector_enhanced import FirebirdConnectorEnhanced
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def test_database_selector():
    """Test the DatabaseSelector functionality"""
    print("Testing DatabaseSelector...")
    
    # Test 1: Initialize DatabaseSelector
    selector = DatabaseSelector()
    
    print(f"Base directory: {selector.base_dir}")
    print(f"DatabaseSelector initialized: {selector is not None}")
    
    # Test 2: Find databases
    try:
        databases = selector.find_databases()
        print(f"Found {len(databases)} databases:")
        for db in databases:
            print(f"  - {db['name']}: {db['path']} ({db['size_mb']:.1f} MB)")
    except Exception as e:
        print(f"Error finding databases: {e}")
        return False
    
    # Test 3: Test database connections
    try:
        print("\nTesting database connections...")
        for db in databases[:3]:  # Test first 3 databases
            result = selector.test_database(db['path'])
            status = "✓ Connected" if result else "✗ Failed"
            print(f"  - {db['name']}: {status}")
    except Exception as e:
        print(f"Error testing databases: {e}")
        return False
    
    return True

def test_gui_integration():
    """Test the GUI integration with database selector"""
    print("\nTesting GUI integration...")
    
    # Create a simple test window
    root = tk.Tk()
    root.title("Database Selector Test")
    root.geometry("400x300")
    
    # Test the database selector dialog
    def test_selector():
        try:
            selector = DatabaseSelector()
            databases = selector.find_databases()
            
            if databases:
                # Create a simple selection dialog
                selection_window = tk.Toplevel(root)
                selection_window.title("Select Database")
                selection_window.geometry("600x400")
                
                tk.Label(selection_window, text="Available Databases:", font=("Arial", 12, "bold")).pack(pady=10)
                
                # Create listbox for database selection
                listbox = tk.Listbox(selection_window, height=10)
                listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
                
                # Populate listbox
                for db in databases:
                    display_text = f"{db['name']} ({db['size_mb']:.1f} MB) - {db['modified']}"
                    listbox.insert(tk.END, display_text)
                
                # Add selection button
                def on_select():
                    selection = listbox.curselection()
                    if selection:
                        selected_db = databases[selection[0]]
                        messagebox.showinfo("Selected", f"Selected: {selected_db['name']}\nPath: {selected_db['path']}")
                        selection_window.destroy()
                
                tk.Button(selection_window, text="Select", command=on_select).pack(pady=10)
                tk.Button(selection_window, text="Cancel", command=selection_window.destroy).pack()
                
            else:
                messagebox.showwarning("No Databases", "No databases found in the specified directory.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error testing database selector: {e}")
    
    # Add test button
    tk.Button(root, text="Test Database Selector", command=test_selector, font=("Arial", 12)).pack(pady=20)
    tk.Button(root, text="Exit", command=root.destroy, font=("Arial", 12)).pack(pady=10)
    
    tk.Label(root, text="Click 'Test Database Selector' to test the functionality", 
             wraplength=350, justify=tk.CENTER).pack(pady=20)
    
    print("GUI test window created. Click the test button to verify functionality.")
    root.mainloop()

def test_database_connection():
    """Test connection to recommended databases"""
    print("\nTesting database connections...")
    
    # Read recommended database
    try:
        with open("recommended_database_for_etl.txt", "r") as f:
            content = f.read()
            print("Recommended database info:")
            print(content)
    except FileNotFoundError:
        print("Recommended database file not found")
    
    # Test connection to known good databases
    test_databases = [
        r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_ARC_24-10-2025\PTRJ_ARC.FDB",
        r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_P1A_24-10-2025\PTRJ_P1A.FDB"
    ]
    
    for db_path in test_databases:
        if os.path.exists(db_path):
            try:
                print(f"\nTesting connection to: {os.path.basename(db_path)}")
                connector = FirebirdConnectorEnhanced(db_path)
                
                # Test basic query
                result = connector.execute_query("SELECT COUNT(*) as table_count FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0")
                if result and 'rows' in result and result['rows']:
                    table_count = list(result['rows'][0].values())[0]
                    print(f"  ✓ Connection successful - {table_count} user tables found")
                else:
                    print(f"  ✗ Connection failed - no result")
                    
            except Exception as e:
                print(f"  ✗ Connection failed: {e}")
        else:
            print(f"Database not found: {db_path}")

def main():
    """Main test function"""
    print("=== Database Selector Test Suite ===\n")
    
    # Test 1: DatabaseSelector class
    if test_database_selector():
        print("✓ DatabaseSelector tests passed")
    else:
        print("✗ DatabaseSelector tests failed")
        return
    
    # Test 2: Database connections
    test_database_connection()
    
    # Test 3: GUI integration (interactive)
    print("\n=== Interactive GUI Test ===")
    test_gui_integration()

if __name__ == "__main__":
    main()