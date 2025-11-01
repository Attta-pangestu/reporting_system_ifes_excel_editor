"""
Direct ISQL Test Script
Tests database operations using direct ISQL commands to debug transaction issues
"""

import subprocess
import tempfile
import os
from firebird_connector_enhanced import FirebirdConnectorEnhanced

def test_direct_isql():
    """Test database operations using direct ISQL commands"""
    print("=== Direct ISQL Test ===")
    
    try:
        # Get connection details from the connector
        connector = FirebirdConnectorEnhanced()
        
        # Create a comprehensive test script
        test_script = f"""
CONNECT '{connector.db_path}' USER '{connector.username}' PASSWORD '{connector.password}';

-- Show current transaction mode
SELECT 'Starting transaction test...' FROM RDB$DATABASE;

-- Check if tables exist and their current row counts
SELECT 'EMP table count:' || COUNT(*) FROM EMP;
SELECT 'FFBLOADINGCROP01 count:' || COUNT(*) FROM FFBLOADINGCROP01;

-- Insert a test record with explicit transaction control
SET AUTODDL OFF;
SET TRANSACTION;

INSERT INTO EMP (EMPID, EMPNAME, EMPTYPE, EMPPOSITION, DIVISIONID, EMPSTATUS)
VALUES ('TEST001', 'Test User', 'KERANI', 'SCANNER', 'TEST', 'A');

-- Check if the record was inserted in this transaction
SELECT 'After insert count:' || COUNT(*) FROM EMP WHERE EMPID = 'TEST001';

-- Commit the transaction
COMMIT;

-- Check if the record persists after commit
SELECT 'After commit count:' || COUNT(*) FROM EMP WHERE EMPID = 'TEST001';

-- Show all records in EMP table
SELECT EMPID, EMPNAME FROM EMP;

-- Clean up
DELETE FROM EMP WHERE EMPID = 'TEST001';
COMMIT;

SELECT 'Final EMP count:' || COUNT(*) FROM EMP;

EXIT;
"""
        
        # Write script to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as f:
            f.write(test_script)
            script_path = f.name
        
        # Execute using ISQL
        isql_path = connector._get_isql_path()
        if not isql_path:
            print("❌ Could not find ISQL executable")
            return False
        
        print(f"Using ISQL: {isql_path}")
        print(f"Database: {connector.db_path}")
        
        # Run the script
        cmd = [isql_path, '-i', script_path]
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        
        print(f"\nReturn code: {result.returncode}")
        print(f"\nSTDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"\nSTDERR:\n{result.stderr}")
        
        # Clean up
        try:
            os.unlink(script_path)
        except:
            pass
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error in direct ISQL test: {e}")
        return False

def test_connector_transaction():
    """Test the connector's transaction handling"""
    print("\n=== Connector Transaction Test ===")
    
    try:
        connector = FirebirdConnectorEnhanced()
        
        # Test 1: Simple insert and immediate check
        print("Test 1: Insert and immediate check")
        insert_query = """
        INSERT INTO EMP (EMPID, EMPNAME, EMPTYPE, EMPPOSITION, DIVISIONID, EMPSTATUS)
        VALUES ('CONN001', 'Connector Test', 'KERANI', 'SCANNER', 'TEST', 'A')
        """
        
        result = connector.execute_query(insert_query)
        print(f"Insert result: {result}")
        
        # Immediate check
        check_query = "SELECT COUNT(*) as COUNT FROM EMP WHERE EMPID = 'CONN001'"
        check_result = connector.execute_query(check_query)
        print(f"Immediate check result: {check_result}")
        
        # Test 2: Explicit commit
        print("\nTest 2: Explicit commit")
        commit_result = connector.execute_query("COMMIT")
        print(f"Commit result: {commit_result}")
        
        # Check after commit
        check_result2 = connector.execute_query(check_query)
        print(f"After commit check result: {check_result2}")
        
        # Test 3: New connection check
        print("\nTest 3: New connection check")
        connector2 = FirebirdConnectorEnhanced()
        check_result3 = connector2.execute_query(check_query)
        print(f"New connection check result: {check_result3}")
        
        # Cleanup
        cleanup_query = "DELETE FROM EMP WHERE EMPID = 'CONN001'"
        connector.execute_query(cleanup_query)
        connector.execute_query("COMMIT")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in connector transaction test: {e}")
        return False

if __name__ == "__main__":
    print("Testing database transaction handling...\n")
    
    # Test 1: Direct ISQL
    success1 = test_direct_isql()
    
    # Test 2: Connector transactions
    success2 = test_connector_transaction()
    
    if success1 and success2:
        print("\n✅ All tests completed")
    else:
        print("\n❌ Some tests failed")