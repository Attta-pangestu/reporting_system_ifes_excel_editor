#!/usr/bin/env python3
"""
Configuration Manager
Mengelola konfigurasi aplikasi dan database

Fungsi utama:
- Mengelola konfigurasi database
- Menyimpan dan memuat pengaturan aplikasi
- Validasi konfigurasi
- Manajemen path dan direktori

Author: AI Assistant
Date: 2025-10-31
"""

import json
import os
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

class ConfigManager:
    def __init__(self, config_dir: str = None):
        """Initialize Configuration Manager"""
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Set configuration directory
        if config_dir is None:
            self.config_dir = os.path.dirname(__file__)
        else:
            self.config_dir = config_dir
            
        # Configuration files
        self.app_config_file = os.path.join(self.config_dir, "app_config.json")
        self.db_config_file = os.path.join(self.config_dir, "database_config.json")
        
        # Default configurations
        self.default_app_config = {
            "application": {
                "name": "Template-Based Report Generator",
                "version": "1.0.0",
                "author": "System Administrator"
            },
            "paths": {
                "templates_dir": "templates",
                "output_dir": "output",
                "logs_dir": "logs"
            },
            "ui": {
                "window_title": "Report Generator",
                "window_size": "800x600",
                "theme": "default"
            },
            "report": {
                "default_format": "xlsx",
                "auto_open": True,
                "backup_reports": True,
                "max_backup_files": 10
            }
        }
        
        self.default_db_config = {
            "databases": {},
            "connection_settings": {
                "timeout": 30,
                "charset": "UTF8",
                "page_size": 4096
            }
        }
        
        # Load configurations
        self.app_config = self.load_app_config()
        self.db_config = self.load_db_config()
        
    def load_app_config(self) -> Dict[str, Any]:
        """Load application configuration"""
        try:
            if os.path.exists(self.app_config_file):
                with open(self.app_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Merge with defaults
                merged_config = self._merge_configs(self.default_app_config, config)
                self.logger.info("Application configuration loaded successfully")
                return merged_config
            else:
                self.logger.info("No app config file found, using defaults")
                return self.default_app_config.copy()
                
        except Exception as e:
            self.logger.error(f"Error loading app config: {str(e)}")
            return self.default_app_config.copy()
            
    def load_db_config(self) -> Dict[str, Any]:
        """Load database configuration"""
        try:
            if os.path.exists(self.db_config_file):
                with open(self.db_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Merge with defaults
                merged_config = self._merge_configs(self.default_db_config, config)
                self.logger.info("Database configuration loaded successfully")
                return merged_config
            else:
                self.logger.info("No database config file found, using defaults")
                return self.default_db_config.copy()
                
        except Exception as e:
            self.logger.error(f"Error loading database config: {str(e)}")
            return self.default_db_config.copy()
            
    def save_app_config(self) -> bool:
        """Save application configuration"""
        try:
            with open(self.app_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.app_config, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Application configuration saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving app config: {str(e)}")
            return False
            
    def save_db_config(self) -> bool:
        """Save database configuration"""
        try:
            with open(self.db_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.db_config, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Database configuration saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving database config: {str(e)}")
            return False
            
    def add_database(self, name: str, path: str, description: str = "") -> bool:
        """Add database configuration"""
        try:
            if not os.path.exists(path):
                self.logger.warning(f"Database file does not exist: {path}")
                
            self.db_config["databases"][name] = {
                "path": path,
                "description": description,
                "added_date": str(Path().cwd()),
                "last_used": None
            }
            
            return self.save_db_config()
            
        except Exception as e:
            self.logger.error(f"Error adding database: {str(e)}")
            return False
            
    def remove_database(self, name: str) -> bool:
        """Remove database configuration"""
        try:
            if name in self.db_config["databases"]:
                del self.db_config["databases"][name]
                return self.save_db_config()
            else:
                self.logger.warning(f"Database '{name}' not found in configuration")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing database: {str(e)}")
            return False
            
    def get_databases(self) -> Dict[str, Dict[str, Any]]:
        """Get all configured databases"""
        return self.db_config.get("databases", {})
        
    def get_database_path(self, name: str) -> Optional[str]:
        """Get database path by name"""
        databases = self.get_databases()
        if name in databases:
            return databases[name].get("path")
        return None
        
    def update_last_used(self, db_name: str) -> bool:
        """Update last used timestamp for database"""
        try:
            if db_name in self.db_config["databases"]:
                from datetime import datetime
                self.db_config["databases"][db_name]["last_used"] = datetime.now().isoformat()
                return self.save_db_config()
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating last used: {str(e)}")
            return False
            
    def get_templates_dir(self) -> str:
        """Get templates directory path"""
        templates_dir = self.app_config["paths"]["templates_dir"]
        if not os.path.isabs(templates_dir):
            templates_dir = os.path.join(self.config_dir, templates_dir)
        return templates_dir
        
    def get_output_dir(self) -> str:
        """Get output directory path"""
        output_dir = self.app_config["paths"]["output_dir"]
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(self.config_dir, output_dir)
        return output_dir
        
    def get_logs_dir(self) -> str:
        """Get logs directory path"""
        logs_dir = self.app_config["paths"]["logs_dir"]
        if not os.path.isabs(logs_dir):
            logs_dir = os.path.join(self.config_dir, logs_dir)
        return logs_dir
        
    def ensure_directories(self) -> bool:
        """Ensure all required directories exist"""
        try:
            directories = [
                self.get_templates_dir(),
                self.get_output_dir(),
                self.get_logs_dir()
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                self.logger.info(f"Directory ensured: {directory}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error ensuring directories: {str(e)}")
            return False
            
    def validate_config(self) -> Dict[str, List[str]]:
        """Validate configuration and return issues"""
        issues = {
            "errors": [],
            "warnings": []
        }
        
        try:
            # Validate paths
            templates_dir = self.get_templates_dir()
            if not os.path.exists(templates_dir):
                issues["warnings"].append(f"Templates directory does not exist: {templates_dir}")
                
            # Validate databases
            for db_name, db_info in self.get_databases().items():
                db_path = db_info.get("path")
                if not db_path:
                    issues["errors"].append(f"Database '{db_name}' has no path specified")
                elif not os.path.exists(db_path):
                    issues["warnings"].append(f"Database file does not exist: {db_path}")
                    
            # Validate required configuration keys
            required_keys = ["application", "paths", "ui", "report"]
            for key in required_keys:
                if key not in self.app_config:
                    issues["errors"].append(f"Missing required configuration key: {key}")
                    
        except Exception as e:
            issues["errors"].append(f"Configuration validation error: {str(e)}")
            
        return issues
        
    def get_setting(self, key_path: str, default: Any = None) -> Any:
        """Get setting value using dot notation (e.g., 'ui.window_title')"""
        try:
            keys = key_path.split('.')
            value = self.app_config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
                    
            return value
            
        except Exception as e:
            self.logger.error(f"Error getting setting '{key_path}': {str(e)}")
            return default
            
    def set_setting(self, key_path: str, value: Any) -> bool:
        """Set setting value using dot notation"""
        try:
            keys = key_path.split('.')
            config = self.app_config
            
            # Navigate to parent
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
                
            # Set value
            config[keys[-1]] = value
            
            return self.save_app_config()
            
        except Exception as e:
            self.logger.error(f"Error setting '{key_path}': {str(e)}")
            return False
            
    def _merge_configs(self, default: Dict[str, Any], 
                      user: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user configuration with defaults"""
        merged = default.copy()
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
                
        return merged
        
    def export_config(self, export_path: str) -> bool:
        """Export all configurations to a file"""
        try:
            export_data = {
                "app_config": self.app_config,
                "db_config": self.db_config,
                "export_timestamp": str(Path().cwd())
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Configuration exported to: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {str(e)}")
            return False
            
    def import_config(self, import_path: str) -> bool:
        """Import configurations from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
                
            if "app_config" in import_data:
                self.app_config = import_data["app_config"]
                self.save_app_config()
                
            if "db_config" in import_data:
                self.db_config = import_data["db_config"]
                self.save_db_config()
                
            self.logger.info(f"Configuration imported from: {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing configuration: {str(e)}")
            return False