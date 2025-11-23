#!/usr/bin/env python3
"""
Windows-Compatible Pre-commit Hook for TurboShells
Runs quality checks before commits on Windows systems.
"""

import os
import sys
import subprocess
from pathlib import Path


def print_status(status, message):
    """Print colored status message"""
    colors = {
        'PASS': '\033[0;32m',
        'FAIL': '\033[0;31m',
        'WARN': '\033[1;33m',
        'INFO': '\033[0;34m',
        'NC': '\033[0m'
    }
    color = colors.get(status, colors['NC'])
    print(f"{color}[{status}] {message}{colors['NC']}")


def main():
    print("Running Windows-compatible pre-commit checks...")

    # Get project root
    project_root = Path.cwd()

    # Track overall success
    overall_success = 0

    # 1. Python syntax check
    print("Checking Python syntax...")
    python_files = []
    for file in project_root.rglob("*.py"):
        if file.is_file():
            python_files.append(file)

    syntax_errors = 0
    for file in python_files:
        try:
            with open(file, 'rb') as f:
                compile(f.read(), str(file), 'exec')
        except SyntaxError:
            print_status("FAIL", f"Syntax error in {file}")
            syntax_errors += 1

    if syntax_errors == 0:
        print_status("PASS", "Python syntax check")
    else:
        print_status("FAIL", f"Python syntax check ({syntax_errors} errors)")
        overall_success = 1

    # 2. Quick validation
    print("Running quick validation...")
    try:
        # Simple import test for key modules
        test_modules = [
            "scripts.local_ci",
            "tests.comprehensive_test_runner"
        ]

        import_errors = 0
        for module in test_modules:
            try:
                result = subprocess.run([
                    sys.executable, "-c", f"import {module.replace('.', '/')}"
                ], capture_output=True, text=True, cwd=project_root, timeout=10)

                if result.returncode != 0:
                    print_status("WARN", f"Import test failed for {module}")
                    import_errors += 1
            except subprocess.TimeoutExpired:
                print_status("WARN", f"Import test timed out for {module}")
                import_errors += 1
            except Exception:
                print_status("WARN", f"Import test error for {module}")
                import_errors += 1

        if import_errors == 0:
            print_status("PASS", "Quick validation")
        else:
            print_status("WARN", f"Quick validation ({import_errors} warnings)")

    except Exception:
        print_status("WARN", "Quick validation failed (not blocking)")

    # Final result
    print()
    if overall_success == 0:
        print_status("PASS", "Pre-commit checks passed")
        print("Ready to commit!")
        sys.exit(0)
    else:
        print_status("FAIL", "Pre-commit checks failed")
        print("Fix the issues above before committing")
        print("To bypass: git commit --no-verify")
        sys.exit(1)


if __name__ == "__main__":
    main()
