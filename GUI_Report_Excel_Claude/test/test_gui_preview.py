#!/usr/bin/env python3
"""
Test GUI with Comprehensive Data Preview
"""

import os
import sys
import subprocess
from datetime import datetime

def setup_console_output():
    """Setup console output untuk Windows compatibility"""
    import sys
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('cp850')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('cp850')(sys.stderr.buffer, 'strict')

def print_section(title):
    """Print section header"""
    print("="*60)
    print(f"GUI PREVIEW TEST: {title}")
    print("="*60)

def test_gui_with_preview():
    """Test GUI dengan comprehensive preview"""
    print_section("TESTING GUI WITH COMPREHENSIVE PREVIEW")

    gui_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gui_with_preview.py")

    if not os.path.exists(gui_file):
        print(f"ERROR: GUI file not found: {gui_file}")
        return False

    print(f"Starting GUI with comprehensive preview...")
    print(f"GUI file: {gui_file}")

    try:
        # Run the GUI
        subprocess.run([sys.executable, gui_file], check=True)
        return True

    except Exception as e:
        print(f"ERROR running GUI: {e}")
        return False

def main():
    """Main function"""
    # Setup console
    setup_console_output()

    print("Enhanced Report Generator with Data Preview - Test")
    print("="*60)

    print("\nThis GUI provides:")
    print("1. Comprehensive data preview before report generation")
    print("2. Query results analysis with detailed information")
    print("3. Variable processing tracing and source identification")
    print("4. Template placeholder compatibility checking")
    print("5. Debug logging with detailed step-by-step information")
    print("6. Export preview data to CSV")
    print("7. Real-time query execution monitoring")
    print("8. Enhanced error tracking and recommendations")

    print_section("FEATURES OVERVIEW")

    print("\nCONFIGURATION TAB:")
    print("- Database connection status with visual indicators")
    print("- Template selection with automatic validation")
    print("- Date range selection with quick options")
    print("- Output path configuration")

    print("\nDATA PREVIEW TAB:")
    print("- Load comprehensive preview button")
    print("- Query results treeview with status, rows, and sample data")
    print("- Processed variables treeview with categories and sources")
    print("- Query detail viewer with SQL and result information")
    print("- Variable tracer with processing information")
    print("- Export preview to CSV functionality")
    print("- Real-time loading status")

    print("\nDEBUG LOG TAB:")
    print("- Complete debug logging with color-coded messages")
    print("- Error filtering capabilities")
    print("- Save debug log to file")
    print("- Clear log functionality")

    print_section("USAGE INSTRUCTIONS")

    print("\n1. CONNECT TO DATABASE:")
    print("   - Enter database path or use Browse button")
    print("   - Click 'Connect' to establish connection")
    print("   - Verify connection status indicator (green = connected)")

    print("\n2. SELECT TEMPLATE:")
    print("   - Choose Excel template from available list")
    print("   - Ensure template is compatible with formula JSON")

    print("\n3. SET DATE RANGE:")
    print("   - Choose start and end dates")
    print("   - Use quick range buttons for convenience")

    print("\n4. LOAD DATA PREVIEW:")
    print("   - Click 'Load Data Preview' button")
    print("   - Monitor progress in debug log tab")
    print("   - Review query results in Data Preview tab")
    print("   - Check processed variables and their sources")
    print("   - Analyze template compatibility")

    print("\n5. GENERATE REPORT:")
    print("   - Click 'Generate Report' when preview is satisfactory")
    print("   - Monitor generation progress")
    print("   - Report will be saved to specified output path")

    print_section("PREVIEW FEATURES DETAIL")

    print("\nQUERY RESULTS ANALYSIS:")
    print("• Status: SUCCESS/FAILED/EMPTY")
    print("• Rows: Number of rows returned")
    print("• Sample Data: Preview of first row")
    print("• Execution Time: Query performance metrics")
    print("• SQL Viewer: View actual SQL queries")
    print("• Detail Viewer: Full result analysis")

    print("\nVARIABLE PROCESSING:")
    print("• Categories: Report Info, Estate Summary, Repeating Section Data")
    print("• Value: Processed variable value")
    print("• Type: Data type (string, integer, etc.)")
    print("• Source: Query Result, Static, Calculated")
    print("• Status: Available/Missing")
    print("• Trace: Variable processing history")

    print("\nTEMPLATE COMPATIBILITY:")
    print("• Total Placeholders: Number of placeholders in template")
    print("• Resolved: Successfully filled placeholders")
    print("• Unresolved: Missing variables")
    print("• Success Rate: Percentage completion")
    print("• Missing Variables: List of unresolved placeholders")

    print("\nDEBUG LOGGING:")
    print("• Real-time logging of all operations")
    print("• Color-coded messages (info, success, warning, error)")
    print("• Detailed step-by-step process tracking")
    print("• Error stack traces for debugging")
    print("• Performance timing information")

    print_section("TROUBLESHOOTING GUIDE")

    print("\nIF PREVIEW LOADS WITH ERRORS:")
    print("1. Check debug log tab for detailed error messages")
    print("2. Verify database connection status")
    print("3. Ensure template file exists and is valid")
    print("4. Check formula JSON file exists")
    print("5. Verify date range has valid data")

    print("\nIF PLACEHOLDERS UNRESOLVED:")
    print("1. Review 'Missing Variables' section in preview summary")
    print("2. Check if variable names match template")
    print("3. Verify query execution returned data")
    print("4. Ensure variable processing completed successfully")

    print("\nIF QUERIES FAIL:")
    print("1. Check SQL syntax in query details viewer")
    print("2. Verify table names exist in database")
    print("3. Check parameter substitution in SQL")
    print("4. Ensure database connection is stable")

    print_section("ADVANCED FEATURES")

    print("\nEXPORT TO CSV:")
    print("• Export all query results to separate CSV files")
    print("• Export variables to variables.csv")
    print("• Useful for external analysis")

    print("\nQUERY OPTIMIZATION:")
    print("• Monitor execution times in query results")
    print("• Identify slow queries for optimization")
    print("• Review SQL for performance improvements")

    print("\nVARIABLE ANALYSIS:")
    print("• Trace variable processing steps")
    print("• Identify variable dependencies")
    print("• Understand data transformation process")

    # Ask user if they want to start GUI
    print("\n" + "="*60)
    response = input("Do you want to start the GUI now? (y/n): ").lower().strip()

    if response in ['y', 'yes', '']:
        return test_gui_with_preview()
    else:
        print("\nGUI not started. To run later, execute:")
        print(f"python {gui_file}")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)