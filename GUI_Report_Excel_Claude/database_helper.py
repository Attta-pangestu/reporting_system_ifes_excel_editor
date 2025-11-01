#!/usr/bin/env python3
"""
Database Helper Module
Handles the special headers/rows structure format used by the Firebird database
"""

def extract_structured_data(query_result):
    """
    Extract data from the special headers/rows format
    
    Args:
        query_result: Result from database query in format [{'headers': [...], 'rows': [...]}]
    
    Returns:
        List of dictionaries with proper column names
    """
    if not query_result or len(query_result) == 0:
        return []
    
    extracted_data = []
    
    for result_item in query_result:
        if not isinstance(result_item, dict):
            continue
            
        headers = result_item.get('headers', [])
        rows = result_item.get('rows', [])
        
        if not headers or not rows:
            continue
        
        # Process each row
        for row in rows:
            if isinstance(row, dict):
                # Row is already a dictionary, use it directly
                extracted_data.append(row)
            elif isinstance(row, (list, tuple)):
                # Row is a list/tuple, zip with headers
                if len(row) >= len(headers):
                    row_dict = dict(zip(headers, row))
                    extracted_data.append(row_dict)
    
    return extracted_data

def execute_query_with_extraction(connector, query, params=None):
    """
    Execute query and automatically extract structured data
    
    Args:
        connector: Database connector instance
        query: SQL query string
        params: Query parameters (optional)
    
    Returns:
        List of dictionaries with extracted data
    """
    try:
        if params:
            raw_result = connector.execute_query(query, params)
        else:
            raw_result = connector.execute_query(query)
        
        return extract_structured_data(raw_result)
    except Exception as e:
        print(f"Query execution failed: {e}")
        return []

def get_table_count(connector, table_name):
    """
    Get count of records in a table
    
    Args:
        connector: Database connector instance
        table_name: Name of the table
    
    Returns:
        Integer count of records
    """
    try:
        query = f"SELECT COUNT(*) as TOTAL FROM {table_name}"
        result = execute_query_with_extraction(connector, query)
        if result and len(result) > 0:
            return int(result[0].get('TOTAL', 0))
        return 0
    except Exception as e:
        print(f"Count query failed for {table_name}: {e}")
        return 0

def get_date_range_for_table(connector, table_name, date_column='TRANSDATE'):
    """
    Get date range for a table
    
    Args:
        connector: Database connector instance
        table_name: Name of the table
        date_column: Name of the date column
    
    Returns:
        Tuple of (min_date, max_date) or (None, None) if no data
    """
    try:
        query = f"""
        SELECT 
            MIN({date_column}) as MIN_DATE,
            MAX({date_column}) as MAX_DATE
        FROM {table_name}
        WHERE {date_column} IS NOT NULL
        """
        result = execute_query_with_extraction(connector, query)
        if result and len(result) > 0:
            min_date = result[0].get('MIN_DATE')
            max_date = result[0].get('MAX_DATE')
            return (min_date, max_date)
        return (None, None)
    except Exception as e:
        print(f"Date range query failed for {table_name}: {e}")
        return (None, None)

def clean_column_name(column_name):
    """
    Clean column names that might have formatting issues
    
    Args:
        column_name: Original column name
    
    Returns:
        Cleaned column name
    """
    if not column_name:
        return column_name
    
    # Remove extra spaces and clean up
    cleaned = str(column_name).strip()
    
    # Handle common patterns in the headers
    if 'SCANUSE' in cleaned:
        return 'SCANUSERID'
    elif 'WORKE' in cleaned:
        return 'WORKERID'
    elif 'CARRIE' in cleaned:
        return 'CARRIERID'
    elif 'FIEL' in cleaned:
        return 'FIELDID'
    elif 'TRANSDA' in cleaned:
        return 'TRANSDATE'
    elif 'TRANS' in cleaned and 'IME' in cleaned:
        return 'TRANSTIME'
    elif 'RIPE' in cleaned and 'CH' in cleaned:
        return 'RIPEBCH'
    elif 'UNRIPE' in cleaned:
        return 'UNRIPEBCH'
    
    return cleaned

def normalize_data_row(row_dict):
    """
    Normalize a data row by cleaning column names and values
    
    Args:
        row_dict: Dictionary representing a data row
    
    Returns:
        Normalized dictionary
    """
    if not isinstance(row_dict, dict):
        return row_dict
    
    normalized = {}
    for key, value in row_dict.items():
        clean_key = clean_column_name(key)
        
        # Clean up common value issues
        if value == '<null>' or value == 'N/A':
            value = None
        elif isinstance(value, str) and value.strip() == '':
            value = None
        
        normalized[clean_key] = value
    
    return normalized

def get_sample_data(connector, table_name, limit=10, date_filter=None):
    """
    Get sample data from a table with proper extraction
    
    Args:
        connector: Database connector instance
        table_name: Name of the table
        limit: Number of records to retrieve
        date_filter: Optional date filter tuple (start_date, end_date)
    
    Returns:
        List of normalized dictionaries
    """
    try:
        query = f"SELECT FIRST {limit} * FROM {table_name}"
        
        if date_filter and len(date_filter) == 2:
            start_date, end_date = date_filter
            if start_date and end_date:
                query += f" WHERE TRANSDATE BETWEEN '{start_date}' AND '{end_date}'"
        
        result = execute_query_with_extraction(connector, query)
        
        # Normalize the data
        normalized_result = []
        for row in result:
            normalized_row = normalize_data_row(row)
            normalized_result.append(normalized_row)
        
        return normalized_result
    except Exception as e:
        print(f"Sample data query failed for {table_name}: {e}")
        return []