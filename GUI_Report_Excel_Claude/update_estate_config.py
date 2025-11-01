#!/usr/bin/env python3
"""
Update Estate Configuration dengan auto-detection
Mencari database files dan update estate_config.json
"""

import os
import json
from pathlib import Path
import logging

def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def scan_database_directories(base_path):
    """Scan untuk database directories"""
    logger = logging.getLogger(__name__)
    found_databases = {}

    if not os.path.exists(base_path):
        logger.error(f"Base path tidak ditemukan: {base_path}")
        return found_databases

    logger.info(f"Scanning database directory: {base_path}")

    # Expected estate mappings
    estate_mappings = {
        'PGE 1A': ['PTRJ_P1A.FDB'],
        'PGE 1B': ['PTRJ_P1B.FDB'],
        'PGE 2A': ['IFESS_PGE_2A'],
        'PGE 2B': ['IFESS_2B'],
        'IJL': ['IFESS_IJL'],
        'DME': ['IFESS_DME'],
        'Are B2': ['IFESS_ARE_B2'],
        'Are B1': ['IFESS_ARE_B1'],
        'Are A': ['IFESS_ARE_A'],
        'Are C': ['IFESS_ARE_C']
    }

    # Scan all subdirectories
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)

        if os.path.isdir(item_path):
            # Check for .FDB files in directory
            fdb_files = [f for f in os.listdir(item_path) if f.endswith('.FDB')]

            if fdb_files:
                logger.info(f"Found database directory: {item} with files: {fdb_files}")

                # Try to match with estate
                for estate_name, patterns in estate_mappings.items():
                    for pattern in patterns:
                        if pattern in item or any(pattern in fdb for fdb in fdb_files):
                            if fdb_files:
                                # Use first .FDB file found
                                fdb_path = os.path.join(item_path, fdb_files[0])
                                found_databases[estate_name] = fdb_path
                                logger.info(f"Mapped {estate_name} -> {fdb_path}")
                                break
                    else:
                        continue
                    break

        elif item.endswith('.FDB') and os.path.isfile(item):
            # Check for root level .FDB files
            for estate_name, patterns in estate_mappings.items():
                for pattern in patterns:
                    if pattern in item:
                        found_databases[estate_name] = os.path.join(base_path, item)
                        logger.info(f"Mapped {estate_name} -> {os.path.join(base_path, item)}")
                        break
                else:
                    continue
                break

    return found_databases

def update_estate_config(base_path, config_file='estate_config.json'):
    """Update estate configuration file"""
    logger = logging.getLogger(__name__)

    # Scan for databases
    found_databases = scan_database_directories(base_path)

    if not found_databases:
        logger.error("No databases found!")
        return False

    # Load existing config if exists
    existing_config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
            logger.info(f"Loaded existing config with {len(existing_config)} estates")
        except Exception as e:
            logger.warning(f"Error loading existing config: {e}")

    # Merge with found databases
    updated_config = {**existing_config, **found_databases}

    # Write updated config
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(updated_config, f, indent=2, ensure_ascii=False)

        logger.info(f"Updated estate config with {len(updated_config)} estates:")
        for estate, path in updated_config.items():
            exists = os.path.exists(path)
            status = "✓" if exists else "✗"
            logger.info(f"  {status} {estate}: {path}")

        return True

    except Exception as e:
        logger.error(f"Error writing config file: {e}")
        return False

def create_manual_config():
    """Create manual configuration if auto-detection fails"""
    logger = logging.getLogger(__name__)

    # Manual configuration based on found directories
    manual_config = {
        "PGE 1A": r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\PTRJ_P1A.FDB",
        "PGE 2B": r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB",
        "PGE 2A": r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_PGE_2A_24-10-2025",
        "IJL": r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_IJL_24-10-2025",
        "Are B2": r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_ARE_B2_24-10-2025",
        "Are B1": r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_ARE_B1_24-10-2025",
        "Are A": r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_ARE_A_24-10-2025",
        "Are C": r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_ARE_C_24-10-2025"
    }

    # Check for missing .FDB files in directories
    for estate, path in list(manual_config.items()):
        if os.path.isdir(path):
            # Look for .FDB files in directory
            fdb_files = [f for f in os.listdir(path) if f.endswith('.FDB')]
            if fdb_files:
                manual_config[estate] = os.path.join(path, fdb_files[0])
                logger.info(f"Updated {estate} path to: {manual_config[estate]}")
            else:
                logger.warning(f"No .FDB files found in {path}")
                del manual_config[estate]
        elif not os.path.exists(path):
            logger.warning(f"Database not found: {path}")
            del manual_config[estate]

    # Write manual config
    try:
        with open('estate_config.json', 'w', encoding='utf-8') as f:
            json.dump(manual_config, f, indent=2, ensure_ascii=False)

        logger.info(f"Created manual config with {len(manual_config)} estates:")
        for estate, path in manual_config.items():
            logger.info(f"  ✓ {estate}: {path}")

        return True

    except Exception as e:
        logger.error(f"Error creating manual config: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("Estate Configuration Updater")
    print("=" * 60)

    setup_logging()
    logger = logging.getLogger(__name__)

    # Try auto-detection first
    base_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess"

    logger.info("Attempting auto-detection of database paths...")
    success = update_estate_config(base_path)

    if not success:
        logger.warning("Auto-detection failed, creating manual configuration...")
        success = create_manual_config()

    if success:
        print("\n✅ Estate configuration updated successfully!")
        print("You can now run the GUI application.")
    else:
        print("\n❌ Failed to update estate configuration.")
        print("Please check database paths manually.")

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()