#!/usr/bin/env python3
"""
Quick test runner for the system
"""

import subprocess
import sys
import os

def main():
    """Run system tests"""
    print("Running System Tests...")
    print("=" * 40)

    try:
        # Run test_system.py
        result = subprocess.run([sys.executable, 'test_system.py'],
                              capture_output=True, text=True, encoding='utf-8')

        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)

        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed with exit code: {result.returncode}")

        return result.returncode

    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    input("Press Enter to exit...")
    sys.exit(exit_code)