#!/usr/bin/env python3
"""
Enhanced pytest runner with comprehensive reporting
Provides detailed test execution, coverage analysis, and quality metrics.
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import argparse


@dataclass
class TestResult:
    """Test result data structure"""
    name: str
    status: str  # 'passed', 'failed', 'skipped', 'error'
    duration: float
    message: str = ""
    details: Dict[str, Any] = None


@dataclass
class TestSuiteResult:
    """Test suite result data structure"""
    name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    success_rate: float
    test_results: List[TestResult]


@dataclass
class CoverageReport:
    """Coverage report data structure"""
    total_lines: int
    covered_lines: int
    missing_lines: int
    coverage_percentage: float
    file_coverage: Dict[str, Dict[str, Any]]


@dataclass
class QualityMetrics:
    """Quality metrics data structure"""
    code_coverage: float
    test_success_rate: float
    performance_score: float
    maintainability_index: float
    technical_debt_ratio: float


@dataclass
class ComprehensiveReport:
    """Comprehensive test report data structure"""
    timestamp: float
    execution_time: float
    suite_results: List[TestSuiteResult]
    coverage_report: CoverageReport
    quality_metrics: QualityMetrics
    summary: Dict[str, Any]


class PytestRunner:
    """Enhanced pytest runner with comprehensive reporting"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dir = project_root / "tests"
        self.src_dir = project_root / "src"
        self.reports_dir = project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

    def run_pytest(self, 
                   test_path: Optional[str] = None,
                   markers: Optional[List[str]] = None,
                   coverage: bool = True,
                   verbose: bool = True,
                   parallel: bool = True) -> subprocess.CompletedProcess:
        """Run pytest with specified options"""
        
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test path
        if test_path:
            cmd.append(str(test_path))
        else:
            cmd.append(str(self.test_dir))
        
        # Add markers
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])
        
        # Add coverage options
        if coverage:
            cmd.extend([
                "--cov=.",
                "--cov-report=json",
                "--cov-report=html",
                "--cov-report=term-missing",
                "--cov-fail-under=70"
            ])
        
        # Add verbosity
        if verbose:
            cmd.append("-v")
        
        # Add parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Add JSON reporting
        cmd.extend(["--json-report", "--json-report-file=test_results.json"])
        
        # Set environment
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.src_dir) + os.pathsep + str(self.test_dir)
        
        # Run pytest
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            env=env
        )
        
        return result

    def parse_test_results(self, json_file: Path) -> TestSuiteResult:
        """Parse pytest JSON results"""
        if not json_file.exists():
            return TestSuiteResult(
                name="default",
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                errors=0,
                duration=0.0,
                success_rate=0.0,
                test_results=[]
            )
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        test_results = []
        total_tests = len(data.get('tests', []))
        passed = 0
        failed = 0
        skipped = 0
        errors = 0
        total_duration = 0.0
        
        for test in data.get('tests', []):
            outcome = test.get('outcome', 'unknown')
            duration = test.get('duration', 0.0)
            total_duration += duration
            
            test_result = TestResult(
                name=test.get('nodeid', ''),
                status=outcome,
                duration=duration,
                message=test.get('call', {}).get('longrepr', ''),
                details=test
            )
            test_results.append(test_result)
            
            if outcome == 'passed':
                passed += 1
            elif outcome == 'failed':
                failed += 1
            elif outcome == 'skipped':
                skipped += 1
            elif outcome == 'error':
                errors += 1
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0.0
        
        return TestSuiteResult(
            name="pytest",
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration=total_duration,
            success_rate=success_rate,
            test_results=test_results
        )

    def parse_coverage_report(self, json_file: Path) -> CoverageReport:
        """Parse coverage JSON report"""
        if not json_file.exists():
            return CoverageReport(
                total_lines=0,
                covered_lines=0,
                missing_lines=0,
                coverage_percentage=0.0,
                file_coverage={}
            )
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        totals = data.get('totals', {})
        file_coverage = data.get('files', {})
        
        total_lines = totals.get('num_statements', 0)
        covered_lines = totals.get('covered_lines', 0)
        missing_lines = total_lines - covered_lines
        coverage_percentage = totals.get('percent_covered', 0.0)
        
        return CoverageReport(
            total_lines=total_lines,
            covered_lines=covered_lines,
            missing_lines=missing_lines,
            coverage_percentage=coverage_percentage,
            file_coverage=file_coverage
        )

    def calculate_quality_metrics(self, 
                                 test_result: TestSuiteResult,
                                 coverage_report: CoverageReport) -> QualityMetrics:
        """Calculate quality metrics"""
        
        # Code coverage score (0-100)
        code_coverage = coverage_report.coverage_percentage
        
        # Test success rate (0-100)
        test_success_rate = test_result.success_rate
        
        # Performance score (based on test execution time)
        # Faster execution = higher score
        if test_result.duration <= 10:
            performance_score = 100
        elif test_result.duration <= 30:
            performance_score = 80
        elif test_result.duration <= 60:
            performance_score = 60
        else:
            performance_score = 40
        
        # Maintainability index (simplified calculation)
        # Based on coverage and test success rate
        maintainability_index = (code_coverage + test_success_rate) / 2
        
        # Technical debt ratio (inverse of quality)
        # Higher quality = lower technical debt
        technical_debt_ratio = max(0, 100 - maintainability_index)
        
        return QualityMetrics(
            code_coverage=code_coverage,
            test_success_rate=test_success_rate,
            performance_score=performance_score,
            maintainability_index=maintainability_index,
            technical_debt_ratio=technical_debt_ratio
        )

    def generate_comprehensive_report(self, 
                                      test_result: TestSuiteResult,
                                      coverage_report: CoverageReport,
                                      quality_metrics: QualityMetrics,
                                      execution_time: float) -> ComprehensiveReport:
        """Generate comprehensive test report"""
        
        # Calculate summary
        summary = {
            'overall_status': 'PASS' if test_result.failed == 0 and test_result.errors == 0 else 'FAIL',
            'critical_issues': test_result.failed + test_result.errors,
            'warnings': test_result.skipped,
            'recommendations': self._generate_recommendations(test_result, coverage_report, quality_metrics)
        }
        
        return ComprehensiveReport(
            timestamp=time.time(),
            execution_time=execution_time,
            suite_results=[test_result],
            coverage_report=coverage_report,
            quality_metrics=quality_metrics,
            summary=summary
        )

    def _generate_recommendations(self, 
                                test_result: TestSuiteResult,
                                coverage_report: CoverageReport,
                                quality_metrics: QualityMetrics) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Coverage recommendations
        if coverage_report.coverage_percentage < 80:
            recommendations.append(
                f"Increase code coverage from {coverage_report.coverage_percentage:.1f}% to 80%+ by adding more unit tests"
            )
        
        # Test success rate recommendations
        if test_result.success_rate < 95:
            recommendations.append(
                f"Fix {test_result.failed + test_result.errors} failing tests to improve success rate"
            )
        
        # Performance recommendations
        if quality_metrics.performance_score < 80:
            recommendations.append(
                "Optimize test execution time by using parallel testing and reducing test complexity"
            )
        
        # Maintainability recommendations
        if quality_metrics.maintainability_index < 80:
            recommendations.append(
                "Improve code maintainability by refactoring complex modules and improving test coverage"
            )
        
        # Technical debt recommendations
        if quality_metrics.technical_debt_ratio > 20:
            recommendations.append(
                "Address technical debt by refactoring legacy code and improving test infrastructure"
            )
        
        return recommendations

    def save_report(self, report: ComprehensiveReport, filename: str = None) -> Path:
        """Save comprehensive report to file"""
        if filename is None:
            timestamp = int(report.timestamp)
            filename = f"test_report_{timestamp}.json"
        
        report_file = self.reports_dir / filename
        
        # Convert to serializable format
        report_dict = asdict(report)
        
        with open(report_file, 'w') as f:
            json.dump(report_dict, f, indent=2, default=str)
        
        return report_file

    def print_summary(self, report: ComprehensiveReport):
        """Print test execution summary"""
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        # Summary
        print(f"Overall Status: {report.summary['overall_status']}")
        print(f"Execution Time: {report.execution_time:.2f}s")
        
        # Test Results
        if report.suite_results:
            test_result = report.suite_results[0]
            print(f"\nTEST RESULTS:")
            print(f"  Total Tests: {test_result.total_tests}")
            print(f"  Passed: {test_result.passed}")
            print(f"  Failed: {test_result.failed}")
            print(f"  Skipped: {test_result.skipped}")
            print(f"  Errors: {test_result.errors}")
            print(f"  Success Rate: {test_result.success_rate:.1f}%")
            print(f"  Duration: {test_result.duration:.2f}s")
        
        # Coverage
        print(f"\nCODE COVERAGE:")
        print(f"  Overall Coverage: {report.coverage_report.coverage_percentage:.1f}%")
        print(f"  Total Lines: {report.coverage_report.total_lines}")
        print(f"  Covered Lines: {report.coverage_report.covered_lines}")
        print(f"  Missing Lines: {report.coverage_report.missing_lines}")
        
        # Quality Metrics
        print(f"\nQUALITY METRICS:")
        print(f"  Code Coverage: {report.quality_metrics.code_coverage:.1f}/100")
        print(f"  Test Success Rate: {report.quality_metrics.test_success_rate:.1f}/100")
        print(f"  Performance Score: {report.quality_metrics.performance_score:.1f}/100")
        print(f"  Maintainability Index: {report.quality_metrics.maintainability_index:.1f}/100")
        print(f"  Technical Debt Ratio: {report.quality_metrics.technical_debt_ratio:.1f}%")
        
        # Recommendations
        if report.summary['recommendations']:
            print(f"\nRECOMMENDATIONS:")
            for i, rec in enumerate(report.summary['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("="*80)

    def run_test_suite(self, 
                      test_categories: List[str] = None,
                      coverage: bool = True,
                      verbose: bool = True) -> ComprehensiveReport:
        """Run complete test suite and generate report"""
        
        start_time = time.time()
        
        # Define test categories
        if test_categories is None:
            test_categories = ['unit', 'integration', 'performance', 'ui']
        
        # Run pytest
        pytest_result = self.run_pytest(
            coverage=coverage,
            verbose=verbose,
            parallel=True
        )
        
        # Parse results
        test_results_file = self.project_root / "test_results.json"
        test_result = self.parse_test_results(test_results_file)
        
        # Parse coverage
        coverage_file = self.project_root / "coverage.json"
        coverage_report = self.parse_coverage_report(coverage_file)
        
        # Calculate quality metrics
        quality_metrics = self.calculate_quality_metrics(test_result, coverage_report)
        
        # Generate comprehensive report
        execution_time = time.time() - start_time
        report = self.generate_comprehensive_report(
            test_result, coverage_report, quality_metrics, execution_time
        )
        
        # Save report
        self.save_report(report)
        
        # Print summary
        self.print_summary(report)
        
        return report


def main():
    """Main entry point for pytest runner"""
    parser = argparse.ArgumentParser(description="Enhanced pytest runner for TurboShells")
    parser.add_argument("--test-path", help="Specific test path to run")
    parser.add_argument("--markers", nargs="+", help="Test markers to run")
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")
    parser.add_argument("--quiet", action="store_true", help="Reduce verbosity")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel execution")
    parser.add_argument("--categories", nargs="+", 
                       choices=['unit', 'integration', 'performance', 'ui'],
                       help="Test categories to run")
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Create runner
    runner = PytestRunner(project_root)
    
    # Run tests
    try:
        report = runner.run_test_suite(
            test_categories=args.categories,
            coverage=not args.no_coverage,
            verbose=not args.quiet
        )
        
        # Exit with appropriate code
        if report.summary['overall_status'] == 'PASS':
            sys.exit(0)
        else:
            sys.exit(1)
    
    except Exception as e:
        print(f"Error running test suite: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
