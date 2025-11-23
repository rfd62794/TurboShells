#!/usr/bin/env python3
"""
Windows-Compatible Pre-commit Hook for TurboShells
Runs enhanced quality checks with auto-fixes before commits on Windows systems.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    try:
        # Import and run enhanced pre-commit
        from scripts.enhanced_pre_commit import main as enhanced_main
        enhanced_main()
    except ImportError:
        # Fallback to basic checks if enhanced version not available
        print("Running basic pre-commit checks...")
        
        # Get changed files
        try:
            result = subprocess.run([
                'git', 'diff', '--cached', '--name-only', '*.py'
            ], capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                changed_files = [
                    Path(f.strip()) for f in result.stdout.strip().split('\n') 
                    if f.strip() and Path(f.strip()).exists()
                ]
            else:
                changed_files = list(Path.cwd().rglob("*.py"))
        except:
            changed_files = list(Path.cwd().rglob("*.py"))
        
        # Basic syntax check
        syntax_errors = 0
        for file_path in changed_files:
            if file_path.suffix == '.py':
                try:
                    with open(file_path, 'rb') as f:
                        compile(f.read(), str(file_path), 'exec')
                except SyntaxError:
                    print(f"[FAIL] Syntax error in {file_path}")
                    syntax_errors += 1
        
        if syntax_errors == 0:
            print("[PASS] Pre-commit checks passed")
            sys.exit(0)
        else:
            print(f"[FAIL] Pre-commit checks failed ({syntax_errors} errors)")
            sys.exit(1)

if __name__ == "__main__":
    main()
