#!/usr/bin/env python3
"""
Streamlined Pre-push Hook for TurboShells
Runs minimal checks before push to avoid blocking workflow.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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

def get_changed_files() -> List[Path]:
    """Get list of changed Python files in current commit"""
    try:
        # Get files that are being pushed
        result = subprocess.run([
            'git', 'diff', '--name-only', 'HEAD~1', 'HEAD', '*.py'
        ], capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            files = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    file_path = Path(line.strip())
                    if file_path.exists() and file_path.suffix == '.py':
                        files.append(file_path)
            return files
        else:
            return []
    except Exception:
        return []

def check_syntax(changed_files: List[Path]) -> bool:
    """Quick syntax check on changed files"""
    if not changed_files:
        return True
        
    syntax_errors = 0
    for file_path in changed_files:
        try:
            with open(file_path, 'rb') as f:
                compile(f.read(), str(file_path), 'exec')
        except SyntaxError:
            print_status("FAIL", f"Syntax error in {file_path.name}")
            syntax_errors += 1
        except Exception:
            pass  # Ignore other errors during push
    
    if syntax_errors == 0:
        print_status("PASS", f"Syntax check ({len(changed_files)} files)")
        return True
    else:
        print_status("FAIL", f"Syntax check ({syntax_errors} errors)")
        return False

def main():
    print("Running streamlined pre-push checks...")
    
    # Get changed files
    changed_files = get_changed_files()
    
    if not changed_files:
        print_status("INFO", "No Python files in this push")
        sys.exit(0)
    
    print_status("INFO", f"Checking {len(changed_files)} Python files")
    
    # Only run syntax check - skip comprehensive tests for speed
    if check_syntax(changed_files):
        print_status("PASS", "Pre-push checks passed")
        sys.exit(0)
    else:
        print_status("FAIL", "Pre-push checks failed")
        print("Fix syntax errors before pushing")
        print("To bypass: git push --no-verify")
        sys.exit(1)

if __name__ == "__main__":
    main()
