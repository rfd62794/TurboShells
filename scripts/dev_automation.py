#!/usr/bin/env python3
"""
Development Automation Script for TurboShells
Automated development workflows and quality checks.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DevTask:
    """Development task data structure"""
    name: str
    description: str
    command: List[str]
    timeout: int = 300
    critical: bool = True

class DevAutomation:
    """Development automation system"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.log_file = self.project_root / "development.log"
        
    def log_message(self, message: str):
        """Log message to file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
        except Exception:
            pass  # Silently fail logging
    
    def run_command(self, command: List[str], cwd: str = None, timeout: int = 300) -> tuple:
        """Run command and return result"""
        try:
            work_dir = cwd or str(self.project_root)
            result = subprocess.run(
                command,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def setup_development_environment(self) -> bool:
        """Set up development environment"""
        print("[FIX] Setting up development environment...")
        
        tasks = [
            DevTask(
                name="Create scripts directory",
                description="Ensure scripts directory exists",
                command=["mkdir", "-p", "scripts"],
                critical=True
            ),
            DevTask(
                name="Create logs directory",
                description="Ensure logs directory exists",
                command=["mkdir", "-p", "logs"],
                critical=True
            ),
            DevTask(
                name="Install Python dependencies",
                description="Install required Python packages",
                command=[sys.executable, "-m", "pip", "install", "pytest", "coverage"],
                critical=False
            ),
            DevTask(
                name="Set up git hooks",
                description="Install git hooks for quality checks",
                command=[sys.executable, "scripts/git_hooks.py", "--install"],
                critical=False
            )
        ]
        
        success_count = 0
        
        for task in tasks:
            print(f"  [INFO] {task.description}")
            self.log_message(f"Starting task: {task.name}")
            
            task_success, stdout, stderr = self.run_command(task.command)
            
            if task_success:
                print(f"    [PASS] {task.name} completed")
                self.log_message(f"Task completed: {task.name}")
                success_count += 1
            else:
                if task.critical:
                    print(f"    [FAIL] {task.name} failed (critical)")
                    self.log_message(f"Critical task failed: {task.name} - {stderr}")
                    return False
                else:
                    print(f"    [WARN]  {task.name} failed (non-critical)")
                    self.log_message(f"Non-critical task failed: {task.name} - {stderr}")
        
        print(f"\n[PASS] Development environment setup complete ({success_count}/{len(tasks)} tasks)")
        return True
    
    def run_daily_quality_check(self) -> bool:
        """Run daily quality checks"""
        print("[CHECK] Running daily quality checks...")
        self.log_message("Starting daily quality check")
        
        tasks = [
            DevTask(
                name="Full test suite",
                description="Run comprehensive test suite",
                command=[sys.executable, "tests/comprehensive_test_runner.py"],
                timeout=600
            ),
            DevTask(
                name="Code style check",
                description="Check code style and formatting",
                command=[sys.executable, "scripts/local_ci.py"],
                timeout=300
            ),
            DevTask(
                name="Performance benchmarks",
                description="Run performance benchmarks",
                command=[sys.executable, "tests/performance_test_suite.py"],
                timeout=300
            )
        ]
        
        results = {}
        
        for task in tasks:
            print(f"  [TEST] {task.description}")
            self.log_message(f"Running: {task.name}")
            
            task_success, stdout, stderr = self.run_command(task.command, timeout=task.timeout)
            
            results[task.name] = {
                "success": task_success,
                "execution_time": time.time(),  # Simplified - would track actual time
                "output": stdout[:500] if stdout else stderr[:500]  # Truncate output
            }
            
            if task_success:
                print(f"    [PASS] {task.name} passed")
                self.log_message(f"Task passed: {task.name}")
            else:
                print(f"    [FAIL] {task.name} failed")
                self.log_message(f"Task failed: {task.name}")
        
        # Save results
        results_file = self.project_root / "daily_quality_report.json"
        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"[DOC] Quality report saved to {results_file}")
        except Exception as e:
            print(f"[WARN]  Could not save quality report: {e}")
        
        # Overall success
        all_passed = all(result["success"] for result in results.values())
        
        if all_passed:
            print("\n[SUCCESS] All daily quality checks passed!")
            self.log_message("Daily quality check: ALL PASSED")
        else:
            failed_count = sum(1 for result in results.values() if not result["success"])
            print(f"\n[WARN]  {failed_count}/{len(tasks)} quality checks failed")
            self.log_message(f"Daily quality check: {failed_count} FAILED")
        
        return all_passed
    
    def run_pre_commit_workflow(self) -> bool:
        """Run pre-commit development workflow"""
        print("🔒 Running pre-commit workflow...")
        self.log_message("Starting pre-commit workflow")
        
        # Quick checks before commit
        tasks = [
            DevTask(
                name="Syntax check",
                description="Check Python syntax",
                command=[sys.executable, "-m", "py_compile", "main.py"],
                timeout=60
            ),
            DevTask(
                name="Quick tests",
                description="Run quick test suite",
                command=[sys.executable, "tests/comprehensive_test_runner.py", "--quick"],
                timeout=120
            ),
            DevTask(
                name="Import check",
                description="Check import structure",
                command=[sys.executable, "-c", "import core.entities; import managers.roster_manager"],
                timeout=30
            )
        ]
        
        for task in tasks:
            print(f"  [CHECK] {task.description}")
            
            task_success, stdout, stderr = self.run_command(task.command, timeout=task.timeout)
            
            if task_success:
                print(f"    [PASS] {task.name}")
            else:
                print(f"    [FAIL] {task.name}")
                print(f"       {stderr}")
                self.log_message(f"Pre-commit check failed: {task.name}")
                return False
        
        print("[PASS] Pre-commit workflow passed!")
        self.log_message("Pre-commit workflow: PASSED")
        return True
    
    def run_release_preparation(self) -> bool:
        """Run release preparation workflow"""
        print("[START] Running release preparation...")
        self.log_message("Starting release preparation")
        
        tasks = [
            DevTask(
                name="Full test suite",
                description="Run complete test suite",
                command=[sys.executable, "tests/comprehensive_test_runner.py"],
                timeout=600
            ),
            DevTask(
                name="Performance tests",
                description="Run performance benchmarks",
                command=[sys.executable, "tests/performance_test_suite.py"],
                timeout=300
            ),
            DevTask(
                name="Documentation check",
                description="Check documentation coverage",
                command=[sys.executable, "scripts/local_ci.py"],
                timeout=120
            )
        ]
        
        results = {}
        
        for task in tasks:
            print(f"  [TEST] {task.description}")
            self.log_message(f"Running release check: {task.name}")
            
            task_success, stdout, stderr = self.run_command(task.command, timeout=task.timeout)
            
            results[task.name] = task_success
            
            if task_success:
                print(f"    [PASS] {task.name}")
            else:
                print(f"    [FAIL] {task.name}")
                self.log_message(f"Release check failed: {task.name}")
                return False
        
        # Generate release report
        release_report = {
            "timestamp": datetime.now().isoformat(),
            "checks_passed": len([r for r in results.values() if r]),
            "total_checks": len(results),
            "ready_for_release": all(results.values())
        }
        
        report_file = self.project_root / "release_report.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(release_report, f, indent=2)
            print(f"[DOC] Release report saved to {report_file}")
        except Exception as e:
            print(f"[WARN]  Could not save release report: {e}")
        
        print("[PASS] Release preparation complete!")
        self.log_message("Release preparation: PASSED")
        return True
    
    def generate_development_report(self) -> Dict[str, Any]:
        """Generate development status report"""
        print("[REPORT] Generating development report...")
        
        # Check recent log entries
        recent_entries = []
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                    recent_entries = lines[-10:]  # Last 10 entries
        except Exception:
            pass
        
        # Check test results
        test_results = {}
        test_files = [
            "tests/comprehensive_report.json",
            "tests/benchmark_results.json",
            "ci_report.json"
        ]
        
        for test_file in test_files:
            file_path = self.project_root / test_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        test_results[test_file] = json.load(f)
                except Exception:
                    test_results[test_file] = {"error": "Could not read file"}
        
        # Check code metrics
        python_files = list(self.project_root.rglob("*.py"))
        total_lines = 0
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except Exception:
                pass
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_stats": {
                "python_files": len(python_files),
                "total_lines_of_code": total_lines,
                "test_files": len([f for f in python_files if "test" in f.name])
            },
            "recent_activity": recent_entries,
            "test_results": test_results,
            "development_status": "Active"
        }
        
        # Save report
        report_file = self.project_root / "development_report.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"[DOC] Development report saved to {report_file}")
        except Exception as e:
            print(f"[WARN]  Could not save development report: {e}")
        
        return report
    
    def create_development_shortcuts(self) -> bool:
        """Create development shortcut scripts"""
        print("[LINK] Creating development shortcuts...")
        
        shortcuts = {
            "test": [sys.executable, "tests/comprehensive_test_runner.py", "--quick"],
            "full-test": [sys.executable, "tests/comprehensive_test_runner.py"],
            "ci": [sys.executable, "scripts/local_ci.py"],
            "pre-commit": [sys.executable, "scripts/local_ci.py", "--pre-commit"],
            "perf": [sys.executable, "tests/performance_test_suite.py"]
        }
        
        # Create batch files for Windows
        for shortcut_name, command in shortcuts.items():
            batch_content = f"""@echo off
echo Running {shortcut_name}...
{" ".join(command)}
pause
"""
            batch_file = self.project_root / f"{shortcut_name}.bat"
            
            try:
                with open(batch_file, 'w') as f:
                    f.write(batch_content)
                print(f"  [PASS] Created {shortcut_name}.bat")
            except Exception as e:
                print(f"  [FAIL] Could not create {shortcut_name}.bat: {e}")
        
        return True

def main():
    """Main function for development automation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Development automation for TurboShells")
    parser.add_argument("--setup", action="store_true", help="Set up development environment")
    parser.add_argument("--daily-check", action="store_true", help="Run daily quality checks")
    parser.add_argument("--pre-commit", action="store_true", help="Run pre-commit workflow")
    parser.add_argument("--release", action="store_true", help="Run release preparation")
    parser.add_argument("--report", action="store_true", help="Generate development report")
    parser.add_argument("--shortcuts", action="store_true", help="Create development shortcuts")
    parser.add_argument("--project-root", type=str, help="Project root directory")
    
    args = parser.parse_args()
    
    # Create automation instance
    automation = DevAutomation(args.project_root)
    
    # Run requested action
    if args.setup:
        success = automation.setup_development_environment()
        sys.exit(0 if success else 1)
    
    elif args.daily_check:
        success = automation.run_daily_quality_check()
        sys.exit(0 if success else 1)
    
    elif args.pre_commit:
        success = automation.run_pre_commit_workflow()
        sys.exit(0 if success else 1)
    
    elif args.release:
        success = automation.run_release_preparation()
        sys.exit(0 if success else 1)
    
    elif args.report:
        report = automation.generate_development_report()
        print(f"[REPORT] Development report generated")
        sys.exit(0)
    
    elif args.shortcuts:
        success = automation.create_development_shortcuts()
        sys.exit(0 if success else 1)
    
    else:
        print("Development automation for TurboShells")
        print("Available actions:")
        print("  --setup        Set up development environment")
        print("  --daily-check  Run daily quality checks")
        print("  --pre-commit   Run pre-commit workflow")
        print("  --release      Run release preparation")
        print("  --report       Generate development report")
        print("  --shortcuts    Create development shortcuts")

if __name__ == "__main__":
    main()
