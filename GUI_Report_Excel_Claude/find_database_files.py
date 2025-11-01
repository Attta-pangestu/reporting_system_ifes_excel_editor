#!/usr/bin/env python3
"""
Find all database files and check their sizes
"""

import os
import glob
from pathlib import Path

def find_database_files():
    """Find all database files in the directory structure"""
    
    # Base directory from the connector
    base_dir = r"D:\Gawean Rebinmas\Monitoring Database"
    
    print(f"🔍 Searching for database files in: {base_dir}")
    print("=" * 60)
    
    # Common database file extensions
    db_extensions = ['*.fdb', '*.gdb', '*.db', '*.sqlite', '*.mdb']
    
    found_files = []
    
    # Search recursively
    for root, dirs, files in os.walk(base_dir):
        for ext in db_extensions:
            pattern = os.path.join(root, ext)
            matches = glob.glob(pattern)
            found_files.extend(matches)
    
    if not found_files:
        print("❌ No database files found")
        return
    
    print(f"📁 Found {len(found_files)} database files:")
    print()
    
    # Sort by size (largest first)
    file_info = []
    for file_path in found_files:
        try:
            size = os.path.getsize(file_path)
            file_info.append((file_path, size))
        except:
            file_info.append((file_path, 0))
    
    file_info.sort(key=lambda x: x[1], reverse=True)
    
    for file_path, size in file_info:
        size_mb = size / (1024 * 1024)
        rel_path = os.path.relpath(file_path, base_dir)
        
        if size > 1024 * 1024:  # > 1MB
            print(f"📊 {rel_path}")
            print(f"   Size: {size:,} bytes ({size_mb:.1f} MB)")
        else:
            print(f"📄 {rel_path}")
            print(f"   Size: {size:,} bytes ({size_mb:.3f} MB)")
        
        # Check if this is the current database
        current_db = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
        if os.path.abspath(file_path) == os.path.abspath(current_db):
            print(f"   ⭐ CURRENT DATABASE (used by connector)")
        
        print()
    
    # Highlight potentially interesting files
    large_files = [(path, size) for path, size in file_info if size > 10 * 1024 * 1024]  # > 10MB
    
    if large_files:
        print("🎯 Large database files (likely to contain data):")
        for file_path, size in large_files:
            size_mb = size / (1024 * 1024)
            rel_path = os.path.relpath(file_path, base_dir)
            print(f"   - {rel_path} ({size_mb:.1f} MB)")
    
    # Check for files with recent modification dates
    print("\n📅 Recently modified database files:")
    import datetime
    
    recent_files = []
    for file_path, size in file_info:
        try:
            mtime = os.path.getmtime(file_path)
            mod_date = datetime.datetime.fromtimestamp(mtime)
            days_ago = (datetime.datetime.now() - mod_date).days
            
            if days_ago < 30:  # Modified in last 30 days
                recent_files.append((file_path, mod_date, size))
        except:
            continue
    
    if recent_files:
        recent_files.sort(key=lambda x: x[1], reverse=True)  # Sort by date
        for file_path, mod_date, size in recent_files:
            rel_path = os.path.relpath(file_path, base_dir)
            size_mb = size / (1024 * 1024)
            print(f"   - {rel_path}")
            print(f"     Modified: {mod_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     Size: {size_mb:.1f} MB")
    else:
        print("   No recently modified database files found")

if __name__ == "__main__":
    find_database_files()