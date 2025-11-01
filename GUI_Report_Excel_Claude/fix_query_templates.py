#!/usr/bin/env python3
"""
Script to fix query templates by removing OCFIELD joins that are causing 0 results.
This will update pge2b_corrected_formula.json to work without field name mapping.
"""

import json
import re
from pathlib import Path

def fix_query_templates():
    """Fix all queries in the template file to remove OCFIELD joins."""
    
    template_file = Path("pge2b_corrected_formula.json")
    
    if not template_file.exists():
        print(f"Template file {template_file} not found!")
        return False
    
    # Load the current template
    with open(template_file, 'r', encoding='utf-8') as f:
        template_data = json.load(f)
    
    print("Original queries with OCFIELD joins:")
    
    # Fix each query
    queries_fixed = 0
    for query_name, query_info in template_data.get('queries', {}).items():
        if 'sql' in query_info:
            original_sql = query_info['sql']
            
            # Check if this query has OCFIELD joins
            if 'OCFIELD' in original_sql:
                print(f"\n--- Fixing query: {query_name} ---")
                print(f"Original: {original_sql[:100]}...")
                
                # Remove OCFIELD joins and related WHERE clauses
                fixed_sql = fix_sql_query(original_sql)
                
                query_info['sql'] = fixed_sql
                queries_fixed += 1
                
                print(f"Fixed: {fixed_sql[:100]}...")
    
    # Update data sources to remove OCFIELD reference
    if 'data_sources' in template_data:
        if 'field_data' in template_data['data_sources']:
            del template_data['data_sources']['field_data']
    
    # Update template info
    template_data['template_info']['version'] = "5.0"
    template_data['template_info']['last_modified'] = "2025-11-01"
    template_data['template_info']['correction_notes'] = "Removed OCFIELD joins to fix 0 results issue. Using FIELDID directly."
    
    # Save the fixed template
    backup_file = template_file.with_suffix('.json.backup')
    template_file.rename(backup_file)
    print(f"\nBackup created: {backup_file}")
    
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nFixed {queries_fixed} queries and saved to {template_file}")
    return True

def fix_sql_query(sql):
    """Fix a single SQL query by removing OCFIELD joins."""
    
    # Remove JOIN OCFIELD clauses
    sql = re.sub(r'\s+JOIN\s+OCFIELD\s+\w+\s+ON\s+[^WHERE\s]+', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\s+LEFT\s+JOIN\s+OCFIELD\s+\w+\s+ON\s+[^WHERE\s]+', '', sql, flags=re.IGNORECASE)
    
    # Remove WHERE clauses that reference OCFIELD aliases (b.DIVID, etc.)
    sql = re.sub(r'\s+WHERE\s+b\.DIVID\s*=\s*[^AND\s]+\s+AND', ' WHERE', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\s+AND\s+b\.DIVID\s*[^AND\s]+', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\s+WHERE\s+b\.DIVID\s*[^AND\s]+', '', sql, flags=re.IGNORECASE)
    
    # Remove references to OCFIELD alias fields in SELECT and GROUP BY
    sql = re.sub(r',\s*b\.DIVID', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r',\s*c\.DIVNAME', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'b\.DIVID,\s*', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'c\.DIVNAME,\s*', '', sql, flags=re.IGNORECASE)
    
    # Remove GROUP BY clauses that reference removed fields
    sql = re.sub(r',\s*b\.DIVID,\s*c\.DIVNAME', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'GROUP\s+BY\s+a\.FIELDID,\s*b\.DIVID,\s*c\.DIVNAME', 'GROUP BY a.FIELDID', sql, flags=re.IGNORECASE)
    
    # Clean up any double spaces
    sql = re.sub(r'\s+', ' ', sql)
    sql = sql.strip()
    
    return sql

if __name__ == "__main__":
    print("Fixing query templates to remove OCFIELD joins...")
    success = fix_query_templates()
    if success:
        print("Query templates fixed successfully!")
    else:
        print("Failed to fix query templates!")