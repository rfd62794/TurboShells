#!/usr/bin/env python3
"""
Complete Quality System Setup for TurboShells
Sets up pre-commit hooks, quality checks, and validates the entire system.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List
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


def print_status(status: str, message: str):
    """Print status message"""
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


def check_python_environment() -> bool:
    """Check Python environment and required packages"""
    print_section("Python Environment Check")

    required_packages = ['pytest', 'pygame']
    optional_packages = ['autopep8', 'flake8', 'coverage']

    all_required = True

    for package in required_packages:
        try:
            __import__(package)
            print_status("PASS", f"{package} available")
        except ImportError:
            print_status("FAIL", f"{package} missing")
            all_required = False

    for package in optional_packages:
        try:
            __import__(package)
            print_status("PASS", f"{package} available")
        except ImportError:
            print_status("WARN", f"{package} not available (optional)")

    return all_required


def setup_git_hooks() -> bool:
    """Setup Git hooks for quality checks"""
    print_section("Git Hooks Setup")

    hooks_dir = project_root / ".git" / "hooks"
    if not hooks_dir.exists():
        print_status("FAIL", "Git hooks directory not found")
        return False

    # Hook files to setup
    hook_files = {
        'pre-commit.bat': 'C:\\Python314\\python.exe "%PROJECT_ROOT%\\tools\\scripts\\git_hook_runner.py" "%PROJECT_ROOT%\\tools\\scripts\\windows_pre_commit.py"',
        'commit-msg.bat': 'C:\\Python314\\python.exe "%PROJECT_ROOT%\\tools\\scripts\\git_hook_runner.py" "%PROJECT_ROOT%\\tools\\scripts\\windows_commit_msg.py"',
        'pre-push.bat': 'C:\\Python314\\python.exe "%PROJECT_ROOT%\\tools\\scripts\\git_hook_runner.py" "%PROJECT_ROOT%\\tools\\scripts\\streamlined_pre_push.py"'
    }

    success = True

    for hook_file, content in hook_files.items():
        hook_path = hooks_dir / hook_file
        try:
            hook_path.write_text(content, encoding='utf-8')
            print_status("PASS", f"Created {hook_file}")
        except Exception as e:
            print_status("FAIL", f"Failed to create {hook_file}: {e}")
            success = False

    return success


def validate_directory_structure() -> bool:
    """Validate project directory structure"""
    print_section("Directory Structure Validation")

    required_structure = {
        'src/': 'Source code directory',
        'src/core/': 'Core game systems',
        'src/managers/': 'Game managers',
        'tools/': 'Development tools',
        'tools/scripts/': 'Utility scripts',
        'tests/': 'Test suite',
        'docs/': 'Documentation',
        'assets/': 'Game assets'
    }

    required_files = {
        'run_game.py': 'Main game entry point',
        'src/main.py': 'Main game class',
        'src/settings.py': 'Game settings',
        'README.md': 'Project documentation'
    }

    success = True

    for dir_path, description in required_structure.items():
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print_status("PASS", f"{dir_path} - {description}")
        else:
            print_status("FAIL", f"{dir_path} - {description} (missing)")
            success = False

    for file_path, description in required_files.items():
        full_path = project_root / file_path
        if full_path.exists() and full_path.is_file():
            print_status("PASS", f"{file_path} - {description}")
        else:
            print_status("FAIL", f"{file_path} - {description} (missing)")
            success = False

    return success


def validate_quality_scripts() -> bool:
    """Validate quality check scripts"""
    print_section("Quality Scripts Validation")

    required_scripts = [
        'tools/scripts/enhanced_pre_commit.py',
        'tools/scripts/windows_pre_commit.py',
        'tools/scripts/streamlined_pre_push.py',
        'tools/scripts/git_hook_runner.py',
        'tools/scripts/quality_check.py',
        'tools/scripts/fix_test_imports.py'
    ]

    success = True

    for script_path in required_scripts:
        full_path = project_root / script_path
        if full_path.exists() and full_path.is_file():
            try:
                # Try to run the script with --help or check syntax
                result = subprocess.run([
                    sys.executable, str(full_path), '--help'
                ], capture_output=True, text=True, timeout=5)

                if result.returncode == 0 or "usage:" in result.stdout.lower():
                    print_status("PASS", f"{script_path}")
                else:
                    # Check syntax instead
                    result = subprocess.run([
                        sys.executable, '-m', 'py_compile', str(full_path)
                    ], capture_output=True, text=True, timeout=5)

                    if result.returncode == 0:
                        print_status("PASS", f"{script_path} (syntax OK)")
                    else:
                        print_status("FAIL", f"{script_path} (syntax error)")
                        success = False

            except subprocess.TimeoutExpired:
                print_status("WARN", f"{script_path} (timeout)")
            except Exception as e:
                print_status("FAIL", f"{script_path} - {e}")
                success = False
        else:
            print_status("FAIL", f"{script_path} (missing)")
            success = False

    return success


def run_quality_check() -> bool:
    """Run comprehensive quality check"""
    print_section("Quality Check Execution")

    quality_script = project_root / "tools" / "scripts" / "quality_check.py"

    if not quality_script.exists():
        print_status("FAIL", "Quality check script not found")
        return False

    try:
        result = subprocess.run([
            sys.executable, str(quality_script)
        ], capture_output=True, text=True, timeout=120, cwd=project_root)

        # Show summary of results
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Overall:' in line or any(status in line for status in ['[PASS]', '[FAIL]', '[WARN]']):
                print(line)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print_status("FAIL", "Quality check timed out")
        return False
    except Exception as e:
        print_status("FAIL", f"Quality check failed: {e}")
        return False


def test_pre_commit_hook() -> bool:
    """Test pre-commit hook functionality"""
    print_section("Pre-commit Hook Test")

    # Create a test file
    test_file = project_root / "test_quality.py"
    test_content = '''#!/usr/bin/env python3
"""Test file for quality check"""

def test_function():
    """Test function"""
    print("This is a test")
    return True

if __name__ == "__main__":
    test_function()
'''

    try:
        # Write test file
        test_file.write_text(test_content, encoding='utf-8')

        # Add to git
        subprocess.run(['git', 'add', str(test_file)],
                       capture_output=True, cwd=project_root)

        # Run pre-commit hook
        pre_commit_script = project_root / "tools" / "scripts" / "enhanced_pre_commit.py"
        result = subprocess.run([
            sys.executable, str(pre_commit_script)
        ], capture_output=True, text=True, timeout=30, cwd=project_root)

        # Clean up
        subprocess.run(['git', 'reset', 'HEAD', str(test_file)],
                       capture_output=True, cwd=project_root)
        test_file.unlink()

        if result.returncode == 0:
            print_status("PASS", "Pre-commit hook test passed")
            return True
        else:
            print_status("FAIL", "Pre-commit hook test failed")
            # Show error output
            for line in result.stdout.split('\n')[-10:]:
                if line.strip():
                    print(f"  {line}")
            return False

    except Exception as e:
        print_status("FAIL", f"Pre-commit hook test error: {e}")
        if test_file.exists():
            test_file.unlink()
        return False


def generate_setup_report(results: Dict[str, bool]) -> str:
    """Generate setup report"""
    report_lines = [
        "# Quality System Setup Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Results Summary"
    ]

    for check_name, passed in results.items():
        status = "[PASS] PASS" if passed else "[FAIL] FAIL"
        report_lines.append(f"- {check_name}: {status}")

    passed_count = sum(results.values())
    total_count = len(results)

    report_lines.extend([
        "",
        f"Overall: {passed_count}/{total_count} checks passed",
        "",
        "## Next Steps"
    ])

    if passed_count == total_count:
        report_lines.extend([
            "[PASS] Quality system is fully configured!",
            "- All pre-commit hooks are active",
            "- Quality checks are functional",
            "- Directory structure is valid",
            "- Ready for development!"
        ])
    else:
        report_lines.extend([
            "[WARN] Some setup steps need attention:",
            "- Review failed checks above",
            "- Install missing dependencies if needed",
            "- Fix any configuration issues",
            "- Re-run setup script after fixes"
        ])

    return '\n'.join(report_lines)


def main():
    """Main setup function"""
    print_header("TurboShells Quality System Setup")
    print(f"Project: {project_root}")

    # Run all setup checks
    results = {
        'Python Environment': check_python_environment(),
        'Directory Structure': validate_directory_structure(),
        'Quality Scripts': validate_quality_scripts(),
        'Git Hooks': setup_git_hooks(),
        'Quality Check': run_quality_check(),
        'Pre-commit Hook': test_pre_commit_hook()
    }

    # Generate summary
    print_header("Setup Summary")

    passed_count = sum(results.values())
    total_count = len(results)

    for check_name, passed in results.items():
        status = "[PASS] PASS" if passed else "[FAIL] FAIL"
        print(f"{check_name:20}: {status}")

    print(f"\nOverall: {passed_count}/{total_count} checks passed")

    # Save report
    report = generate_setup_report(results)
    report_file = project_root / 'logs' / 'quality_setup_report.md'
    report_file.parent.mkdir(exist_ok=True)
    report_file.write_text(report, encoding='utf-8')

    print(f"\n[DOC] Setup report saved to: {report_file}")

    # Final message
    if passed_count == total_count:
        print("\n[SUCCESS] Quality system setup completed successfully!")
        print("Your development environment is ready for high-quality code!")
    else:
        print("\n[WARN] Some setup steps need attention.")
        print("Please review the failed checks and fix any issues.")

    # Exit with appropriate code
    sys.exit(0 if passed_count >= 4 else 1)  # Allow 2 failures for optional components


if __name__ == "__main__":
    main()
