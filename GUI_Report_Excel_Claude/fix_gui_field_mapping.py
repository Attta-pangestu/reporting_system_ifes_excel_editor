#!/usr/bin/env python3
"""
Script to fix GUI field mapping issues by updating methods to work without field name joins
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_gui_field_mapping():
    """Fix GUI methods to work without field name mapping"""
    
    gui_file = "gui_adaptive_report_generator.py"
    
    print("=== Fixing GUI Field Mapping ===")
    
    # Read the current GUI file
    with open(gui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Update get_ffb_scanner_preview_data to not use field name join
    old_preview_method = '''    def get_ffb_scanner_preview_data(self, month):
        """Get preview data for FFB scanner for a specific month"""
        try:
            table_name = f"FFBSCANNERDATA{month:02d}"
            
            # Try to get query from template first
            query = self.query_manager.get_query('ffb_scanner_preview')
            
            if query:
                # Replace placeholder with actual table name
                query = query.replace('{table_name}', table_name)
            else:
                # Fallback query without field name join
                query = f"""
                SELECT f.SCANUSERID, f.WORKERID, f.FIELDID, f.TRANSDATE
                FROM {table_name} f
                WHERE f.TRANSDATE >= '2020-01-01'
                ORDER BY f.SCANUSERID
                LIMIT 10
                """
            
            results = execute_query_with_extraction(self.db_connector, query)
            
            # Normalize the data
            normalized_results = []
            for row in results:
                normalized_row = normalize_data_row(row)
                normalized_results.append(normalized_row)
            
            return normalized_results
            
        except Exception as e:
            print(f"Error getting FFB scanner preview data: {e}")
            return []'''
    
    new_preview_method = '''    def get_ffb_scanner_preview_data(self, month):
        """Get preview data for FFB scanner for a specific month"""
        try:
            table_name = f"FFBSCANNERDATA{month:02d}"
            
            # Simple query without field name join - show FIELDID directly
            query = f"""
            SELECT f.SCANUSERID, f.WORKERID, f.FIELDID, f.TRANSDATE, f.RIPE, f.RIPEBCH
            FROM {table_name} f
            WHERE f.TRANSDATE >= '2020-01-01'
            ORDER BY f.SCANUSERID
            LIMIT 10
            """
            
            results = execute_query_with_extraction(self.db_connector, query)
            
            # Normalize the data and add field name as FIELDID for now
            normalized_results = []
            for row in results:
                normalized_row = normalize_data_row(row)
                # Add a field name that shows the FIELDID value
                normalized_row['FIELDNAME'] = f"Field_{normalized_row.get('FIELDID', 'Unknown')}"
                normalized_results.append(normalized_row)
            
            return normalized_results
            
        except Exception as e:
            print(f"Error getting FFB scanner preview data: {e}")
            return []'''
    
    # Fix 2: Update get_divisions to work without field name join
    old_divisions_method = '''    def get_divisions(self, start_date, end_date):
        """Get list of divisions for the date range"""
        try:
            divisions = {}
            
            # Get months in the date range
            months = self.get_months_in_range(start_date, end_date)
            
            for month in months:
                table_name = f"FFBSCANNERDATA{month:02d}"
                
                # Try to get query from template first
                query = self.query_manager.get_query('divisions_list')
                
                if query:
                    # Replace placeholder with actual table name
                    query = query.replace('{table_name}', table_name)
                else:
                    # Fallback query - get FIELDID as DIVID and create name
                    query = f"""
                    SELECT DISTINCT f.FIELDID as DIVID, f.FIELDID as DIVNAME
                    FROM {table_name} f
                    WHERE f.TRANSDATE BETWEEN '{start_date}' AND '{end_date}'
                    """
                
                results = execute_query_with_extraction(self.db_connector, query)
                
                for row in results:
                    normalized_row = normalize_data_row(row)
                    divid = normalized_row.get('DIVID')
                    divname = normalized_row.get('DIVNAME', f'Field_{divid}')
                    
                    if divid and divid not in divisions:
                        divisions[divid] = divname
            
            return divisions
            
        except Exception as e:
            print(f"Error getting divisions: {e}")
            return {}'''
    
    new_divisions_method = '''    def get_divisions(self, start_date, end_date):
        """Get list of divisions for the date range"""
        try:
            divisions = {}
            
            # Get months in the date range
            months = self.get_months_in_range(start_date, end_date)
            
            for month in months:
                table_name = f"FFBSCANNERDATA{month:02d}"
                
                # Simple query to get unique FIELDID values
                query = f"""
                SELECT DISTINCT f.FIELDID
                FROM {table_name} f
                WHERE f.TRANSDATE BETWEEN '{start_date}' AND '{end_date}'
                AND f.FIELDID IS NOT NULL
                """
                
                results = execute_query_with_extraction(self.db_connector, query)
                
                for row in results:
                    normalized_row = normalize_data_row(row)
                    fieldid = normalized_row.get('FIELDID')
                    
                    if fieldid and fieldid not in divisions:
                        # Create a readable name from FIELDID
                        divisions[fieldid] = f'Field_{fieldid}'
            
            return divisions
            
        except Exception as e:
            print(f"Error getting divisions: {e}")
            return {}'''
    
    # Fix 3: Update analyze_division to work without field name join
    old_analyze_method = '''    def analyze_division(self, division_id, start_date, end_date):
        """Analyze FFB data for a specific division"""
        try:
            results = []
            
            # Get months in the date range
            months = self.get_months_in_range(start_date, end_date)
            
            for month in months:
                table_name = f"FFBSCANNERDATA{month:02d}"
                
                # Try to get query from template first
                query = self.query_manager.get_query('division_analysis')
                
                if query:
                    # Replace placeholders
                    query = query.replace('{table_name}', table_name)
                    query = query.replace('{division_id}', str(division_id))
                    query = query.replace('{start_date}', start_date)
                    query = query.replace('{end_date}', end_date)
                else:
                    # Fallback query without field name join
                    query = f"""
                    SELECT f.SCANUSERID, f.WORKERID, f.FIELDID, f.TRANSDATE, 
                           f.RIPE, f.RIPEBCH, f."CH     BLACK", f."CH    ROTTEN",
                           f."CH LONGSTALK", f."CH    RATDMG", f."CH   LOOSEFR"
                    FROM {table_name} f
                    WHERE f.FIELDID = {division_id}
                    AND f.TRANSDATE BETWEEN '{start_date}' AND '{end_date}'
                    """
                
                month_results = execute_query_with_extraction(self.db_connector, query)
                
                for row in month_results:
                    normalized_row = normalize_data_row(row)
                    # Add field name
                    normalized_row['FIELDNAME'] = f'Field_{division_id}'
                    results.append(normalized_row)
            
            return results
            
        except Exception as e:
            print(f"Error analyzing division: {e}")
            return []'''
    
    new_analyze_method = '''    def analyze_division(self, division_id, start_date, end_date):
        """Analyze FFB data for a specific division"""
        try:
            results = []
            
            # Get months in the date range
            months = self.get_months_in_range(start_date, end_date)
            
            for month in months:
                table_name = f"FFBSCANNERDATA{month:02d}"
                
                # Simple query without field name join
                query = f"""
                SELECT f.SCANUSERID, f.WORKERID, f.FIELDID, f.TRANSDATE, 
                       f.RIPE, f.RIPEBCH, f."CH     BLACK", f."CH    ROTTEN",
                       f."CH LONGSTALK", f."CH    RATDMG", f."CH   LOOSEFR"
                FROM {table_name} f
                WHERE f.FIELDID = {division_id}
                AND f.TRANSDATE BETWEEN '{start_date}' AND '{end_date}'
                """
                
                month_results = execute_query_with_extraction(self.db_connector, query)
                
                for row in month_results:
                    normalized_row = normalize_data_row(row)
                    # Add field name based on FIELDID
                    normalized_row['FIELDNAME'] = f'Field_{division_id}'
                    results.append(normalized_row)
            
            return results
            
        except Exception as e:
            print(f"Error analyzing division: {e}")
            return []'''
    
    # Apply the fixes
    content = content.replace(old_preview_method, new_preview_method)
    content = content.replace(old_divisions_method, new_divisions_method)
    content = content.replace(old_analyze_method, new_analyze_method)
    
    # Write the updated content back
    with open(gui_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Updated get_ffb_scanner_preview_data method")
    print("✓ Updated get_divisions method")
    print("✓ Updated analyze_division method")
    print("✓ All methods now work without field name joins")
    print("\n=== GUI Field Mapping Fixed ===")

if __name__ == "__main__":
    fix_gui_field_mapping()