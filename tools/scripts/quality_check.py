#!/usr/bin/env python3
"""
Comprehensive Quality Check Script for TurboShells
Runs all quality checks and generates a detailed report.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_section(title: str):
    """Print a formatted section"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")

def check_python_syntax() -> Dict[str, Any]:
    """Check Python syntax across all Python files"""
    print_section("Python Syntax Check")
    
    python_files = list(project_root.rglob("*.py"))
    # Exclude virtual environments and cache directories
    python_files = [f for f in python_files if not any(skip in str(f) for skip in [
        '.venv', 'venv', '__pycache__', '.git', 'node_modules'
    ])]
    
    syntax_errors = []
    syntax_warnings = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for null bytes
            if '\x00' in content:
                syntax_errors.append(f"Null bytes found in {file_path}")
                continue
            
            # Compile to check syntax
            compile(content, str(file_path), 'exec')
            
        except SyntaxError as e:
            syntax_errors.append(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            syntax_warnings.append(f"Could not check {file_path}: {e}")
    
    print(f"✅ Checked {len(python_files)} Python files")
    print(f"❌ Syntax errors: {len(syntax_errors)}")
    print(f"⚠️  Warnings: {len(syntax_warnings)}")
    
    if syntax_errors:
        print("\nSyntax Errors:")
        for error in syntax_errors:
            print(f"  - {error}")
    
    return {
        'total_files': len(python_files),
        'syntax_errors': syntax_errors,
        'warnings': syntax_warnings,
        'passed': len(syntax_errors) == 0
    }

def check_import_structure() -> Dict[str, Any]:
    """Check import structure and dependencies"""
    print_section("Import Structure Check")
    
    try:
        # Try importing main modules
        import_results = {}
        
        modules_to_check = [
            'main',
            'settings', 
            'core.game.entities',
            'core.graphics_manager',
            'core.audio_manager',
            'managers.race_manager',
            'managers.roster_manager',
            'core.systems.state_handler'
        ]
        
        for module in modules_to_check:
            try:
                __import__(module)
                import_results[module] = "✅ Success"
            except ImportError as e:
                import_results[module] = f"❌ Failed: {e}"
            except Exception as e:
                import_results[module] = f"⚠️  Warning: {e}"
        
        print("Import Results:")
        for module, result in import_results.items():
            print(f"  {module}: {result}")
        
        failed_imports = [m for m, r in import_results.items() if "❌" in r]
        
        return {
            'modules_checked': len(modules_to_check),
            'failed_imports': failed_imports,
            'passed': len(failed_imports) == 0
        }
        
    except Exception as e:
        print(f"❌ Import check failed: {e}")
        return {
            'modules_checked': 0,
            'failed_imports': [str(e)],
            'passed': False
        }

def check_code_style() -> Dict[str, Any]:
    """Check code style and formatting"""
    print_section("Code Style Check")
    
    try:
        # Try to run flake8 if available
        result = subprocess.run([
            sys.executable, '-m', 'flake8',
            '--max-line-length=120',
            '--ignore=E302,E701',
            'src/'
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ Code style check passed")
            return {'passed': True, 'issues': []}
        else:
            issues = result.stdout.strip().split('\n') if result.stdout.strip() else []
            print(f"⚠️  Code style issues found: {len(issues)}")
            for issue in issues[:10]:  # Show first 10 issues
                print(f"  - {issue}")
            if len(issues) > 10:
                print(f"  ... and {len(issues) - 10} more")
            
            return {'passed': False, 'issues': issues}
            
    except FileNotFoundError:
        print("ℹ️  flake8 not available, skipping style check")
        return {'passed': True, 'issues': [], 'skipped': True}
    except Exception as e:
        print(f"❌ Style check failed: {e}")
        return {'passed': False, 'issues': [str(e)]}

def run_tests() -> Dict[str, Any]:
    """Run the test suite"""
    print_section("Test Suite")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/', '-v', '--tb=short', '--maxfail=5'
        ], capture_output=True, text=True, cwd=project_root, timeout=120)
        
        print("Test Output:")
        print(result.stdout)
        
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        passed = result.returncode == 0
        print(f"{'✅' if passed else '❌'} Tests {'passed' if passed else 'failed'}")
        
        return {
            'passed': passed,
            'return_code': result.returncode,
            'output': result.stdout,
            'errors': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out")
        return {'passed': False, 'timeout': True}
    except FileNotFoundError:
        print("ℹ️  pytest not available, skipping tests")
        return {'passed': True, 'skipped': True}
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return {'passed': False, 'error': str(e)}

def check_file_structure() -> Dict[str, Any]:
    """Check project file structure"""
    print_section("File Structure Check")
    
    required_dirs = [
        'src/',
        'src/core/',
        'src/managers/',
        'tools/',
        'tools/scripts/',
        'assets/',
        'docs/',
        'tests/'
    ]
    
    required_files = [
        'run_game.py',
        'src/main.py',
        'src/settings.py',
        'README.md',
        'docs/TODO.md'
    ]
    
    missing_dirs = []
    missing_files = []
    
    for dir_path in required_dirs:
        if not (project_root / dir_path).exists():
            missing_dirs.append(dir_path)
    
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    print(f"✅ Required directories: {len(required_dirs) - len(missing_dirs)}/{len(required_dirs)}")
    print(f"✅ Required files: {len(required_files) - len(missing_files)}/{len(required_files)}")
    
    if missing_dirs:
        print("❌ Missing directories:")
        for d in missing_dirs:
            print(f"  - {d}")
    
    if missing_files:
        print("❌ Missing files:")
        for f in missing_files:
            print(f"  - {f}")
    
    return {
        'passed': len(missing_dirs) == 0 and len(missing_files) == 0,
        'missing_dirs': missing_dirs,
        'missing_files': missing_files
    }

def generate_quality_report(results: Dict[str, Any]) -> str:
    """Generate a quality report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'project_root': str(project_root),
        'results': results,
        'overall_passed': all(
            result.get('passed', False) and not result.get('skipped', False)
            for result in results.values()
        )
    }
    
    return json.dumps(report, indent=2)

def main():
    print_header("TurboShells Quality Check")
    print(f"Project: {project_root}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all checks
    results = {
        'syntax': check_python_syntax(),
        'imports': check_import_structure(),
        'style': check_code_style(),
        'tests': run_tests(),
        'structure': check_file_structure()
    }
    
    # Generate summary
    print_header("Quality Check Summary")
    
    passed_checks = 0
    total_checks = 0
    
    for check_name, result in results.items():
        total_checks += 1
        if result.get('passed', False):
            passed_checks += 1
            status = "✅ PASS"
        elif result.get('skipped', False):
            status = "⏭️  SKIP"
        else:
            status = "❌ FAIL"
        
        print(f"{check_name.title():12}: {status}")
    
    print(f"\nOverall: {passed_checks}/{total_checks} checks passed")
    
    # Save report
    report = generate_quality_report(results)
    report_file = project_root / 'logs' / f'quality_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    report_file.parent.mkdir(exist_ok=True)
    report_file.write_text(report)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if results['syntax']['passed'] and results['imports']['passed']:
        print("\n✅ Core quality checks passed!")
        sys.exit(0)
    else:
        print("\n❌ Critical quality checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
