#!/usr/bin/env python3
"""
Test runner for Community Connect application.
Run this script to execute all tests.
"""

import subprocess
import sys
import os


def run_tests():
    """Run the test suite."""
    print("🧪 Running Community Connect Test Suite")
    print("=" * 50)

    # Change to the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    try:
        # Run pytest with coverage
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--color=yes"
        ], capture_output=False)

        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)

    except FileNotFoundError:
        print("❌ Error: pytest not found. Please install it with: pip install pytest")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
