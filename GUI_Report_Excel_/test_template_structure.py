#!/usr/bin/env python3
"""Test script to validate template structure without database dependency"""

from template_manager import TemplateManager
from validator import TemplateValidator
import json

def test_template_structure():
    """Test template structure validation"""
    print("Testing template structure validation...")
    
    # Initialize components
    tm = TemplateManager()
    validator = TemplateValidator()
    
    # Load the raw JSON template
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
        
        # Test validation without database connection (structure only)
        results = validator.validate_template(template_info, db_connector=None)
        
        print('\nValidation Results:')
        print(f'Errors: {len(results["errors"])}')
        print(f'Warnings: {len(results["warnings"])}')
        print(f'Info: {len(results["info"])}')
        
        if results["errors"]:
            print('\nERRORS:')
            for i, error in enumerate(results["errors"], 1):
                print(f'  {i}. {error}')
                
        if results["warnings"]:
            print('\nWARNINGS:')
            for i, warning in enumerate(results["warnings"], 1):
                print(f'  {i}. {warning}')
                
        if results["info"]:
            print('\nINFO:')
            for i, info in enumerate(results["info"], 1):
                print(f'  {i}. {info}')
        
        # Generate validation report
        report = validator.generate_validation_report(results)
        print('\n' + '='*60)
        print('DETAILED VALIDATION REPORT')
        print('='*60)
        print(report)
        
        return len(results["errors"]) == 0
        
    except FileNotFoundError:
        print(f'Template file {json_path} not found')
        return False
    except json.JSONDecodeError as e:
        print(f'Error parsing JSON: {e}')
        return False
    except Exception as e:
        print(f'Error loading template: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_template_structure()
    print(f'\nTemplate structure validation: {"PASSED" if success else "FAILED"}')