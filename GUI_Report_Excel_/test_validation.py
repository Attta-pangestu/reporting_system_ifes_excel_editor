#!/usr/bin/env python3
"""Test script to validate template structure"""

from template_manager import TemplateManager
from validator import TemplateValidator
from database_connector import DatabaseConnector
import json

def test_template_validation():
    """Test template validation"""
    print("Testing template validation...")
    
    # Initialize components
    tm = TemplateManager()
    validator = TemplateValidator()
    
    # Load the raw JSON template instead of using TemplateManager's transformed version
    import json
    json_path = "templates/laporan_kinerja_template.json"
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            template_info = json.load(f)
        
        print('Template loaded successfully from JSON')
        print(f'Template keys: {list(template_info.keys())}')
        print(f'Has template_info: {"template_info" in template_info}')
        print(f'Has queries: {"queries" in template_info}')
        print(f'Has mappings: {"mappings" in template_info}')
        
        # Add excel_path for validation
        template_info['excel_path'] = 'templates/laporan_kinerja_template.xlsx'
        
        # Test validation with real database connection
        try:
            db_connector = DatabaseConnector(
                r'D:\Gawean Rebinmas\Monitoring Database\Ifes Auto report\excel_method\referensi\IFES.FDB', 
                'SYSDBA', 
                'masterkey'
            )
            results = validator.validate_template(template_info, db_connector)
            print('\nValidation Results:')
            print(f'Errors: {len(results["errors"])}')
            print(f'Warnings: {len(results["warnings"])}')
            print(f'Info: {len(results["info"])}')
            
            if results['errors']:
                print('\nERRORS:')
                for i, error in enumerate(results['errors'], 1):
                    print(f'  {i}. {error}')
                    
            if results['warnings']:
                print('\nWARNINGS:')
                for i, warning in enumerate(results['warnings'], 1):
                    print(f'  {i}. {warning}')
                    
            if results['info']:
                print('\nINFO:')
                for i, info in enumerate(results['info'], 1):
                    print(f'  {i}. {info}')
                    
        except Exception as e:
            print(f'Validation error: {e}')
            import traceback
            traceback.print_exc()
            
    except FileNotFoundError:
        print(f'Template file {json_path} not found')
    except json.JSONDecodeError as e:
        print(f'Error parsing JSON: {e}')
    except Exception as e:
        print(f'Error loading template: {e}')

if __name__ == "__main__":
    test_template_validation()