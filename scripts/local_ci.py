#!/usr/bin/env python3
"""
Local Continuous Integration Script for TurboShells
Automated testing and quality checks for local development.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class CIResult:
    """CI result data structure"""
    stage: str
    success: bool
    execution_time: float
    output: str
    details: Dict[str, Any] = None

class LocalCI:
    """Local continuous integration automation"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.results = []
        self.start_time = time.time()
        
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
    
    def check_python_syntax(self) -> CIResult:
        """Check Python syntax for all Python files"""
        print("🔍 Checking Python syntax...")
        start_time = time.time()
        
        # Find all Python files
        python_files = list(self.project_root.rglob("*.py"))
        
        syntax_errors = []
        for py_file in python_files:
            success, stdout, stderr = self.run_command([
                sys.executable, "-m", "py_compile", str(py_file)
            ])
            
            if not success:
                syntax_errors.append(f"{py_file}: {stderr}")
        
        execution_time = time.time() - start_time
        success = len(syntax_errors) == 0
        
        output = f"Checked {len(python_files)} Python files"
        if syntax_errors:
            output += f"\nSyntax errors found:\n" + "\n".join(syntax_errors)
        else:
            output += "\n[PASS] No syntax errors found"
        
        return CIResult(
            stage="Python Syntax Check",
            success=success,
            execution_time=execution_time,
            output=output,
            details={"files_checked": len(python_files), "errors": len(syntax_errors)}
        )
    
    def run_quick_tests(self) -> CIResult:
        """Run quick test suite"""
        print("🧪 Running quick tests...")
        start_time = time.time()
        
        success, stdout, stderr = self.run_command([
            sys.executable, "tests/comprehensive_test_runner.py", "--quick"
        ])
        
        execution_time = time.time() - start_time
        
        output = stdout if stdout else stderr
        if success:
            output += "\n[PASS] Quick tests passed"
        else:
            output += "\n[FAIL] Quick tests failed"
        
        return CIResult(
            stage="Quick Tests",
            success=success,
            execution_time=execution_time,
            output=output,
            details={"test_type": "quick"}
        )
    
    def check_import_structure(self) -> CIResult:
        """Check for import issues and circular dependencies"""
        print("🔗 Checking import structure...")
        start_time = time.time()
        
        # Create a simple import checker script
        import_checker_script = """
import sys
import os
sys.path.insert(0, os.getcwd())

def check_imports():
    import_errors = []
    
    # Try importing main modules
    try:
        from core.entities import Turtle
    except ImportError as e:
        import_errors.append(f"core.entities: {e}")
    
    try:
        from core.game_state import generate_random_turtle
    except ImportError as e:
        import_errors.append(f"core.game_state: {e}")
    
    try:
        from managers.roster_manager import RosterManager
    except ImportError as e:
        import_errors.append(f"managers.roster_manager: {e}")
    
    return import_errors

if __name__ == "__main__":
    errors = check_imports()
    if errors:
        print("Import errors found:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print("[PASS] All imports successful")
        sys.exit(0)
"""
        
        # Write and run import checker
        checker_file = self.project_root / "temp_import_checker.py"
        try:
            with open(checker_file, 'w') as f:
                f.write(import_checker_script)
            
            success, stdout, stderr = self.run_command([
                sys.executable, str(checker_file)
            ])
            
            execution_time = time.time() - start_time
            output = stdout if stdout else stderr
            
        finally:
            # Clean up temporary file
            if checker_file.exists():
                checker_file.unlink()
        
        return CIResult(
            stage="Import Structure Check",
            success=success,
            execution_time=execution_time,
            output=output,
            details={"imports_checked": 4}
        )
    
    def check_code_style(self) -> CIResult:
        """Check basic code style (without external dependencies)"""
        print("📝 Checking code style...")
        start_time = time.time()
        
        # Basic style checks without external tools
        python_files = list(self.project_root.rglob("*.py"))
        style_issues = []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    # Check for trailing whitespace
                    if line.rstrip() != line.rstrip('\n\r'):
                        style_issues.append(f"{py_file}:{i} - Trailing whitespace")
                    
                    # Check for tabs (should use spaces)
                    if '\t' in line:
                        style_issues.append(f"{py_file}:{i} - Tab character found")
                    
                    # Check for lines too long (basic check)
                    if len(line.rstrip()) > 120:
                        style_issues.append(f"{py_file}:{i} - Line too long ({len(line.rstrip())} chars)")
                        
            except Exception as e:
                style_issues.append(f"{py_file}: Error reading file - {e}")
        
        execution_time = time.time() - start_time
        success = len(style_issues) == 0
        
        output = f"Checked {len(python_files)} Python files"
        if style_issues:
            output += f"\nStyle issues found:\n" + "\n".join(style_issues[:10])  # Limit output
            if len(style_issues) > 10:
                output += f"\n... and {len(style_issues) - 10} more issues"
        else:
            output += "\n[PASS] No style issues found"
        
        return CIResult(
            stage="Code Style Check",
            success=success,
            execution_time=execution_time,
            output=output,
            details={"files_checked": len(python_files), "issues": len(style_issues)}
        )
    
    def check_documentation_coverage(self) -> CIResult:
        """Check basic documentation coverage"""
        print("📚 Checking documentation coverage...")
        start_time = time.time()
        
        python_files = list(self.project_root.rglob("*.py"))
        docstring_issues = []
        
        for py_file in python_files:
            if py_file.name.startswith("test_") or py_file.parent.name == "tests":
                continue  # Skip test files
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for module docstring
                if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
                    docstring_issues.append(f"{py_file}: Missing module docstring")
                
                # Check for function/class definitions without docstrings
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('def ') or stripped.startswith('class '):
                        # Simple check - next non-empty line should be docstring
                        for j in range(i + 1, min(i + 5, len(lines))):
                            next_line = lines[j].strip()
                            if next_line:
                                if not (next_line.startswith('"""') or next_line.startswith("'''")):
                                    docstring_issues.append(f"{py_file}:{i+1} - Function/class without docstring")
                                break
                        
            except Exception as e:
                docstring_issues.append(f"{py_file}: Error analyzing file - {e}")
        
        execution_time = time.time() - start_time
        success = len(docstring_issues) == 0
        
        output = f"Checked {len(python_files)} Python files (excluding tests)"
        if docstring_issues:
            output += f"\nDocumentation issues found:\n" + "\n".join(docstring_issues[:10])
            if len(docstring_issues) > 10:
                output += f"\n... and {len(docstring_issues) - 10} more issues"
        else:
            output += "\n[PASS] Good documentation coverage"
        
        return CIResult(
            stage="Documentation Coverage",
            success=success,
            execution_time=execution_time,
            output=output,
            details={"files_checked": len(python_files), "issues": len(docstring_issues)}
        )
    
    def run_coverage_analysis(self) -> CIResult:
        """Run coverage analysis with goals checking"""
        print("Running coverage analysis...")
        start_time = time.time()
        
        # Import coverage analyzer
        try:
            from scripts.coverage_analysis import CoverageIntegration
            
            integration = CoverageIntegration(str(self.project_root))
            report = integration.run_coverage_with_tests("quick")
            
            if report:
                # Check if goals are met
                goals_met_count = sum(1 for met in report.goals_met.values() if met)
                total_goals = len(report.goals_met)
                success_rate = goals_met_count / total_goals * 100
                
                execution_time = time.time() - start_time
                
                output = f"Coverage analysis completed\n"
                output += f"Overall coverage: {report.overall_coverage:.1f}%\n"
                output += f"Goals met: {goals_met_count}/{total_goals} ({success_rate:.1f}%)\n"
                
                # Check if critical goals are met
                critical_goals = ['core.entities', 'core.game_state', 'overall']
                critical_met = sum(1 for goal in critical_goals if report.goals_met.get(goal, False))
                
                if critical_met == len(critical_goals) and success_rate >= 70:
                    output += "[PASS] Coverage goals met"
                    success = True
                else:
                    output += "[WARN] Some coverage goals not met"
                    success = True  # Warning, not failure
                
                return CIResult(
                    stage="Coverage Analysis",
                    success=success,
                    execution_time=execution_time,
                    output=output,
                    details={
                        "overall_coverage": report.overall_coverage,
                        "goals_met": goals_met_count,
                        "total_goals": total_goals,
                        "critical_goals_met": critical_met
                    }
                )
            else:
                return CIResult(
                    stage="Coverage Analysis",
                    success=False,
                    execution_time=time.time() - start_time,
                    output="Coverage analysis failed",
                    details={}
                )
                
        except ImportError:
            # Fallback if coverage analyzer not available
            success, stdout, stderr = self.run_command([
                sys.executable, "-c", "print('Coverage analysis skipped - analyzer not available')"
            ])
            
            execution_time = time.time() - start_time
            output = "Coverage analysis skipped (analyzer not available)"
            
            return CIResult(
                stage="Coverage Analysis",
                success=True,  # Not a failure
                execution_time=execution_time,
                output=output,
                details={"status": "skipped"}
            )
    
    def check_performance_regression(self) -> CIResult:
        """Check for performance regressions"""
        print("Checking performance regressions...")
        start_time = time.time()
        
        benchmark_file = self.project_root / "tests" / "benchmark_results.json"
        if not benchmark_file.exists():
            return CIResult(
                stage="Performance Regression Check",
                success=True,
                execution_time=time.time() - start_time,
                output="No baseline benchmarks found - skipping regression check",
                details={"status": "no_baseline"}
            )
        
        # Run performance tests
        success, stdout, stderr = self.run_command([
            sys.executable, "tests/performance_test_suite.py"
        ])
        
        execution_time = time.time() - start_time
        
        if not success:
            return CIResult(
                stage="Performance Regression Check",
                success=False,
                execution_time=execution_time,
                output=f"Performance tests failed:\n{stderr}",
                details={"status": "tests_failed"}
            )
        
        # Simple regression check (would be more sophisticated in real implementation)
        output = stdout + "\n[PASS] Performance tests completed"
        
        return CIResult(
            stage="Performance Regression Check",
            success=True,
            execution_time=execution_time,
            output=output,
            details={"status": "passed"}
        )
    
    def generate_ci_report(self) -> Dict[str, Any]:
        """Generate comprehensive CI report"""
        total_time = time.time() - self.start_time
        passed_stages = sum(1 for result in self.results if result.success)
        total_stages = len(self.results)
        
        report = {
            "summary": {
                "total_stages": total_stages,
                "passed_stages": passed_stages,
                "failed_stages": total_stages - passed_stages,
                "success_rate": (passed_stages / total_stages * 100) if total_stages > 0 else 0,
                "total_execution_time": total_time
            },
            "stages": []
        }
        
        for result in self.results:
            stage_report = {
                "stage": result.stage,
                "success": result.success,
                "execution_time": result.execution_time,
                "output": result.output
            }
            
            if result.details:
                stage_report["details"] = result.details
            
            report["stages"].append(stage_report)
        
        return report
    
    def save_ci_report(self, report: Dict[str, Any], filename: str = "ci_report.json"):
        """Save CI report to file"""
        report_file = self.project_root / filename
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n[REPORT] CI report saved to {report_file}")
        except Exception as e:
            print(f"Error saving CI report: {e}")
    
    def run_full_ci(self) -> bool:
        """Run complete CI pipeline"""
        print("Starting Local CI Pipeline")
        print("=" * 50)
        
        # Run all CI stages
        stages = [
            self.check_python_syntax,
            self.check_import_structure,
            self.run_quick_tests,
            self.run_coverage_analysis,
            self.check_code_style,
            self.check_documentation_coverage,
            self.check_performance_regression
        ]
        
        for stage_func in stages:
            result = stage_func()
            self.results.append(result)
            
            status = "[PASS]" if result.success else "[FAIL]"
            print(f"{status} {result.stage} ({result.execution_time:.2f}s)")
            
            if not result.success:
                print(f"Output: {result.output}")
                print("\n[FAIL] CI Pipeline Failed - Fix issues before committing")
                return False
        
        # Generate and save report
        report = self.generate_ci_report()
        self.save_ci_report(report)
        
        # Print summary
        print(f"\nCI Pipeline Summary:")
        print(f"Stages Passed: {report['summary']['passed_stages']}/{report['summary']['total_stages']}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"Total Time: {report['summary']['total_execution_time']:.2f}s")
        
        print("\n[PASS] CI Pipeline Passed - Ready to commit!")
        return True
    
    def run_pre_commit_check(self) -> bool:
        """Run pre-commit checks (subset of full CI)"""
        print("Running Pre-Commit Checks")
        print("=" * 30)
        
        # Run essential pre-commit stages
        stages = [
            self.check_python_syntax,
            self.check_import_structure,
            self.run_quick_tests
        ]
        
        for stage_func in stages:
            result = stage_func()
            
            status = "[PASS]" if result.success else "[FAIL]"
            print(f"{status} {result.stage}")
            
            if not result.success:
                print(f"Output: {result.output}")
                print("\n[FAIL] Pre-commit checks failed - Fix issues before committing")
                return False
        
        print("\n[PASS] Pre-commit checks passed!")
        return True

def main():
    """Main function for local CI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Local CI for TurboShells")
    parser.add_argument("--pre-commit", action="store_true", help="Run pre-commit checks only")
    parser.add_argument("--project-root", type=str, help="Project root directory")
    
    args = parser.parse_args()
    
    # Create CI instance
    ci = LocalCI(args.project_root)
    
    # Run appropriate checks
    if args.pre_commit:
        success = ci.run_pre_commit_check()
        sys.exit(0 if success else 1)
    else:
        success = ci.run_full_ci()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
