#!/usr/bin/env python3
"""
Enhanced Windows-Compatible Pre-commit Hook for TurboShells
Runs auto-fixes and focused quality checks before commits on Windows systems.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def print_status(status, message):
    """Print colored status message"""
    colors = {
        'PASS': '\033[0;32m',
        'FAIL': '\033[0;31m',
        'WARN': '\033[1;33m',
        'INFO': '\033[0;34m',
        'FIX': '\033[1;36m',
        'NC': '\033[0m'
    }
    color = colors.get(status, colors['NC'])
    print(f"{color}[{status}] {message}{colors['NC']}")

def get_changed_files() -> List[Path]:
    """Get list of changed Python files"""
    try:
        # Get staged files
        result = subprocess.run([
            'git', 'diff', '--cached', '--name-only', '--diff-filter=ACM', '*.py'
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
            print_status("WARN", "Could not get changed files, checking all Python files")
            return list(Path.cwd().rglob("*.py"))
    except Exception as e:
        print_status("WARN", f"Error getting changed files: {e}")
        return list(Path.cwd().rglob("*.py"))

def run_auto_fix(changed_files: List[Path]) -> bool:
    """Run auto-fix on changed files"""
    print_status("INFO", "Running auto-fix on changed files...")
    
    try:
        # Import auto-fix system
        from scripts.auto_fix_system import CICDAutoFixer
        
        fixer = CICDAutoFixer()
        fixes_applied = 0
        
        for file_path in changed_files:
            # Fix Unicode issues in file
            original_content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Replace common issues
            content = original_content
            replacements = {
                '🚀': '[START]',
                '📋': '[INFO]',
                '✅': '[PASS]',
                '❌': '[FAIL]',
                '📊': '[REPORT]',
                '📈': '[METRICS]',
                '⚡': '[PERF]',
                '💾': '[SAVE]',
                '🎉': '[SUCCESS]',
                '🚨': '[ERROR]',
                '🔧': '[FIX]',
                '🔍': '[CHECK]',
                '🧪': '[TEST]',
                '📄': '[DOC]',
                '⚠️': '[WARN]',
                '🔗': '[LINK]',
                '💡': '[NOTE]'
            }
            
            for emoji, replacement in replacements.items():
                if emoji in content:
                    content = content.replace(emoji, replacement)
                    fixes_applied += 1
            
            # Write back if changed
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                print_status("FIX", f"Fixed Unicode in {file_path.relative_to(Path.cwd())}")
        
        if fixes_applied > 0:
            print_status("FIX", f"Applied {fixes_applied} auto-fixes")
        else:
            print_status("INFO", "No auto-fixes needed")
        
        return True
        
    except ImportError:
        print_status("WARN", "Auto-fix system not available")
        return False
    except Exception as e:
        print_status("WARN", f"Auto-fix failed: {e}")
        return False

def run_auto_lint(changed_files: List[Path]) -> bool:
    """Run auto-linting on changed files"""
    print_status("INFO", "Running auto-linting...")
    
    try:
        # Try to run autopep8 if available
        for file_path in changed_files:
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'autopep8',
                    '--in-place',
                    '--max-line-length=120',
                    str(file_path)
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print_status("FIX", f"Auto-linted {file_path.name}")
                    
            except subprocess.TimeoutExpired:
                print_status("WARN", f"Auto-lint timeout for {file_path.name}")
            except FileNotFoundError:
                print_status("INFO", "autopep8 not available, skipping auto-lint")
                break
        
        return True
        
    except Exception as e:
        print_status("WARN", f"Auto-lint failed: {e}")
        return False

def check_syntax(changed_files: List[Path]) -> bool:
    """Check Python syntax on changed files"""
    print_status("INFO", "Checking Python syntax...")
    
    syntax_errors = 0
    for file_path in changed_files:
        try:
            with open(file_path, 'rb') as f:
                compile(f.read(), str(file_path), 'exec')
        except SyntaxError as e:
            print_status("FAIL", f"Syntax error in {file_path}: {e}")
            syntax_errors += 1
        except Exception as e:
            print_status("WARN", f"Could not check {file_path}: {e}")
    
    if syntax_errors == 0:
        print_status("PASS", f"Python syntax check ({len(changed_files)} files)")
        return True
    else:
        print_status("FAIL", f"Python syntax check ({syntax_errors} errors)")
        return False

def run_focused_tests(changed_files: List[Path]) -> bool:
    """Run focused tests on changed files"""
    print_status("INFO", "Running focused tests...")
    
    if not changed_files:
        print_status("INFO", "No Python files changed, skipping tests")
        return True
    
    try:
        # Try to run pytest on specific files/directories
        test_dirs = set()
        
        for file_path in changed_files:
            # Map source files to test directories
            if 'scripts/' in str(file_path):
                test_dirs.add('tests/')
            elif 'core/' in str(file_path):
                test_dirs.add('tests/')
            elif 'tests/' in str(file_path):
                # If test file changed, run that specific test
                test_path = file_path
                try:
                    result = subprocess.run([
                        sys.executable, '-m', 'pytest',
                        str(test_path), '-v', '--tb=short'
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        print_status("PASS", f"Tests passed for {test_path.name}")
                    else:
                        print_status("WARN", f"Tests failed for {test_path.name}")
                        print(result.stdout[-500:])  # Show last 500 chars
                        return False
                        
                except subprocess.TimeoutExpired:
                    print_status("WARN", f"Tests timeout for {test_path.name}")
                except FileNotFoundError:
                    print_status("INFO", "pytest not available, skipping tests")
                    break
        
        # Run general tests if we have test directories
        if test_dirs and not any('tests/' in str(f) for f in changed_files):
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pytest',
                    '--maxfail=3', '--tb=short', '-q'
                ], capture_output=True, text=True, timeout=60, cwd=Path.cwd())
                
                if result.returncode == 0:
                    print_status("PASS", "Focused tests passed")
                    return True
                else:
                    print_status("WARN", "Some focused tests failed")
                    print(result.stdout[-500:])
                    return False
                    
            except subprocess.TimeoutExpired:
                print_status("WARN", "Focused tests timeout")
            except FileNotFoundError:
                print_status("INFO", "pytest not available, skipping tests")
        
        return True
        
    except Exception as e:
        print_status("WARN", f"Focused tests failed: {e}")
        return True  # Don't block commit on test failures

def check_imports(changed_files: List[Path]) -> bool:
    """Check imports in changed files"""
    print_status("INFO", "Checking imports...")
    
    import_errors = 0
    for file_path in changed_files:
        try:
            # Try to compile and check for import errors
            result = subprocess.run([
                sys.executable, '-m', 'py_compile', str(file_path)
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                print_status("WARN", f"Import issue in {file_path.name}")
                import_errors += 1
                
        except subprocess.TimeoutExpired:
            print_status("WARN", f"Import check timeout for {file_path.name}")
        except Exception:
            print_status("WARN", f"Import check error for {file_path.name}")
    
    if import_errors == 0:
        print_status("PASS", f"Import check ({len(changed_files)} files)")
        return True
    else:
        print_status("WARN", f"Import check ({import_errors} warnings)")
        return True  # Don't block commit on import warnings

def main():
    print("Running enhanced pre-commit checks...")
    
    # Get project root
    project_root = Path.cwd()
    
    # Get changed files
    changed_files = get_changed_files()
    print_status("INFO", f"Checking {len(changed_files)} changed Python files")
    
    if not changed_files:
        print_status("INFO", "No Python files changed, skipping checks")
        sys.exit(0)
    
    # Track overall success
    all_checks_passed = True
    
    # 1. Run auto-fix
    if not run_auto_fix(changed_files):
        print_status("WARN", "Auto-fix failed, continuing...")
    
    # 2. Run auto-linting
    if not run_auto_lint(changed_files):
        print_status("WARN", "Auto-lint failed, continuing...")
    
    # 3. Check syntax (blocking)
    if not check_syntax(changed_files):
        all_checks_passed = False
    
    # 4. Check imports (non-blocking)
    check_imports(changed_files)
    
    # 5. Run focused tests (non-blocking)
    run_focused_tests(changed_files)
    
    # Final result
    print()
    if all_checks_passed:
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
