#!/usr/bin/env python3
"""
Coverage Reporting and Analysis for TurboShells
Comprehensive code coverage analysis and reporting tools.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class CoverageMetric:
    """Coverage metric data structure"""
    module: str
    statements: int
    missing: int
    covered: int
    coverage_percent: float
    missing_lines: List[int]

@dataclass
class CoverageReport:
    """Coverage report data structure"""
    timestamp: float
    total_statements: int
    total_missing: int
    total_covered: int
    overall_coverage: float
    module_metrics: Dict[str, CoverageMetric]
    coverage_goals: Dict[str, float]
    goals_met: Dict[str, bool]

class CoverageAnalyzer:
    """Coverage analysis and reporting"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.coverage_file = self.project_root / ".coverage"
        self.coverage_json = self.project_root / "coverage.json"
        
        # Coverage goals from Phase 21
        self.coverage_goals = {
            'core.entities': 95.0,
            'core.game_state': 95.0,
            'core.race_track': 90.0,
            'core.state_handler': 90.0,
            'managers.roster_manager': 90.0,
            'managers.race_manager': 90.0,
            'managers.shop_manager': 90.0,
            'managers.breeding_manager': 90.0,
            'ui.components': 85.0,
            'ui.layouts': 85.0,
            'ui.rendering': 80.0,
            'overall': 77.0
        }
    
    def run_coverage_analysis(self, test_command: List[str] = None) -> bool:
        """Run coverage analysis"""
        print("🔍 Running coverage analysis...")
        
        # Default test command
        if test_command is None:
            test_command = [
                sys.executable, "-m", "pytest",
                "--cov=core",
                "--cov=managers", 
                "--cov=ui",
                "--cov-report=json",
                "--cov-report=term-missing",
                "tests/"
            ]
        
        try:
            # Change to project root
            result = subprocess.run(
                test_command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("✅ Coverage analysis completed")
                return True
            else:
                print(f"❌ Coverage analysis failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Coverage analysis timed out")
            return False
        except Exception as e:
            print(f"❌ Coverage analysis error: {e}")
            return False
    
    def parse_coverage_json(self) -> Optional[Dict[str, Any]]:
        """Parse coverage JSON report"""
        if not self.coverage_json.exists():
            print("❌ Coverage JSON file not found")
            return None
        
        try:
            with open(self.coverage_json, 'r') as f:
                coverage_data = json.load(f)
            return coverage_data
        except Exception as e:
            print(f"❌ Error parsing coverage JSON: {e}")
            return None
    
    def analyze_module_coverage(self, coverage_data: Dict[str, Any]) -> Dict[str, CoverageMetric]:
        """Analyze coverage for individual modules"""
        module_metrics = {}
        
        if 'files' not in coverage_data:
            return module_metrics
        
        for file_path, file_data in coverage_data['files'].items():
            # Convert file path to module name
            module_name = self.file_path_to_module(file_path)
            
            if module_name:
                statements = file_data.get('summary', {}).get('num_statements', 0)
                missing = file_data.get('summary', {}).get('missing_lines', 0)
                covered = statements - missing
                coverage_percent = (covered / statements * 100) if statements > 0 else 0
                missing_lines = file_data.get('missing_lines', [])
                
                metric = CoverageMetric(
                    module=module_name,
                    statements=statements,
                    missing=missing,
                    covered=covered,
                    coverage_percent=coverage_percent,
                    missing_lines=missing_lines
                )
                
                module_metrics[module_name] = metric
        
        return module_metrics
    
    def file_path_to_module(self, file_path: str) -> Optional[str]:
        """Convert file path to module name for goal matching"""
        try:
            # Convert absolute path to relative
            if os.path.isabs(file_path):
                file_path = str(Path(file_path).relative_to(self.project_root))
            
            # Normalize path separators
            file_path = file_path.replace('\\', '/')
            
            # Remove .py extension
            if file_path.endswith('.py'):
                file_path = file_path[:-3]
            
            # Convert to module notation
            module_name = file_path.replace('/', '.')
            
            return module_name
        except Exception:
            return None
    
    def calculate_overall_coverage(self, module_metrics: Dict[str, CoverageMetric]) -> Tuple[int, int, int, float]:
        """Calculate overall coverage statistics"""
        total_statements = sum(metric.statements for metric in module_metrics.values())
        total_missing = sum(metric.missing for metric in module_metrics.values())
        total_covered = total_statements - total_missing
        overall_coverage = (total_covered / total_statements * 100) if total_statements > 0 else 0
        
        return total_statements, total_missing, total_covered, overall_coverage
    
    def check_coverage_goals(self, module_metrics: Dict[str, CoverageMetric]) -> Dict[str, bool]:
        """Check if coverage goals are met"""
        goals_met = {}
        
        for goal_module, goal_percent in self.coverage_goals.items():
            if goal_module == 'overall':
                # Calculate overall coverage
                _, _, _, overall_coverage = self.calculate_overall_coverage(module_metrics)
                goals_met[goal_module] = overall_coverage >= goal_percent
            else:
                # Find matching module
                matching_metric = None
                for module_name, metric in module_metrics.items():
                    if goal_module in module_name or module_name.startswith(goal_module):
                        matching_metric = metric
                        break
                
                if matching_metric:
                    goals_met[goal_module] = matching_metric.coverage_percent >= goal_percent
                else:
                    goals_met[goal_module] = False  # Module not found
        
        return goals_met
    
    def generate_coverage_report(self) -> Optional[CoverageReport]:
        """Generate comprehensive coverage report"""
        print("📊 Generating coverage report...")
        
        # Run coverage analysis
        if not self.run_coverage_analysis():
            return None
        
        # Parse coverage data
        coverage_data = self.parse_coverage_json()
        if not coverage_data:
            return None
        
        # Analyze module coverage
        module_metrics = self.analyze_module_coverage(coverage_data)
        
        # Calculate overall coverage
        total_statements, total_missing, total_covered, overall_coverage = self.calculate_overall_coverage(module_metrics)
        
        # Check coverage goals
        goals_met = self.check_coverage_goals(module_metrics)
        
        # Create report
        report = CoverageReport(
            timestamp=time.time(),
            total_statements=total_statements,
            total_missing=total_missing,
            total_covered=total_covered,
            overall_coverage=overall_coverage,
            module_metrics=module_metrics,
            coverage_goals=self.coverage_goals,
            goals_met=goals_met
        )
        
        return report
    
    def print_coverage_summary(self, report: CoverageReport):
        """Print coverage summary"""
        print(f"\n📊 Coverage Report Summary")
        print("=" * 50)
        
        # Overall coverage
        print(f"Overall Coverage: {report.overall_coverage:.1f}%")
        print(f"Total Statements: {report.total_statements}")
        print(f"Covered: {report.total_covered}")
        print(f"Missing: {report.total_missing}")
        
        # Goals status
        print(f"\n🎯 Coverage Goals:")
        goals_met_count = sum(1 for met in report.goals_met.values() if met)
        total_goals = len(report.goals_met)
        
        for goal_module, goal_percent in report.coverage_goals.items():
            status = "✅" if report.goals_met[goal_module] else "❌"
            print(f"  {status} {goal_module}: {goal_percent}%")
        
        print(f"\nGoals Met: {goals_met_count}/{total_goals} ({goals_met_count/total_goals*100:.1f}%)")
        
        # Module details
        print(f"\n📋 Module Coverage Details:")
        for module_name, metric in sorted(report.module_metrics.items()):
            status = "✅" if metric.coverage_percent >= 80 else "⚠️" if metric.coverage_percent >= 60 else "❌"
            print(f"  {status} {module_name}: {metric.coverage_percent:.1f}% ({metric.covered}/{metric.statements})")
            
            # Show missing lines if significant
            if metric.missing > 0 and metric.coverage_percent < 80:
                missing_preview = metric.missing_lines[:10]
                if len(metric.missing_lines) > 10:
                    missing_preview.append(f"... +{len(metric.missing_lines)-10} more")
                print(f"      Missing lines: {missing_preview}")
    
    def save_coverage_report(self, report: CoverageReport, filename: str = "coverage_report.json"):
        """Save coverage report to file"""
        try:
            report_data = {
                "timestamp": report.timestamp,
                "summary": {
                    "total_statements": report.total_statements,
                    "total_missing": report.total_missing,
                    "total_covered": report.total_covered,
                    "overall_coverage": report.overall_coverage
                },
                "goals": {
                    "targets": report.coverage_goals,
                    "met": report.goals_met,
                    "goals_met_count": sum(1 for met in report.goals_met.values() if met),
                    "total_goals": len(report.goals_met)
                },
                "modules": {
                    module_name: {
                        "statements": metric.statements,
                        "missing": metric.missing,
                        "covered": metric.covered,
                        "coverage_percent": metric.coverage_percent,
                        "missing_lines": metric.missing_lines
                    }
                    for module_name, metric in report.module_metrics.items()
                }
            }
            
            report_file = self.project_root / filename
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"📄 Coverage report saved to {report_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving coverage report: {e}")
            return False
    
    def generate_coverage_trends(self, current_report: CoverageReport) -> Dict[str, Any]:
        """Generate coverage trends analysis"""
        trends_file = self.project_root / "coverage_trends.json"
        
        # Load historical data
        historical_data = []
        if trends_file.exists():
            try:
                with open(trends_file, 'r') as f:
                    historical_data = json.load(f)
            except Exception:
                pass
        
        # Add current report
        current_data = {
            "timestamp": current_report.timestamp,
            "overall_coverage": current_report.overall_coverage,
            "goals_met_count": sum(1 for met in current_report.goals_met.values() if met),
            "total_goals": len(current_report.goals_met)
        }
        
        historical_data.append(current_data)
        
        # Keep only last 30 reports
        if len(historical_data) > 30:
            historical_data = historical_data[-30:]
        
        # Calculate trends
        if len(historical_data) >= 2:
            recent = historical_data[-1]
            previous = historical_data[-2]
            
            coverage_trend = recent["overall_coverage"] - previous["overall_coverage"]
            goals_trend = recent["goals_met_count"] - previous["goals_met_count"]
            
            trends = {
                "coverage_trend": coverage_trend,
                "goals_trend": goals_trend,
                "trend_direction": "improving" if coverage_trend > 0 else "declining" if coverage_trend < 0 else "stable"
            }
        else:
            trends = {
                "coverage_trend": 0,
                "goals_trend": 0,
                "trend_direction": "insufficient_data"
            }
        
        # Save updated historical data
        try:
            with open(trends_file, 'w') as f:
                json.dump(historical_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save coverage trends: {e}")
        
        return trends
    
    def identify_uncovered_areas(self, report: CoverageReport) -> List[Dict[str, Any]]:
        """Identify areas that need more test coverage"""
        uncovered_areas = []
        
        for module_name, metric in report.module_metrics.items():
            if metric.coverage_percent < 80:  # Areas below 80% need attention
                area = {
                    "module": module_name,
                    "current_coverage": metric.coverage_percent,
                    "missing_lines": metric.missing,
                    "priority": "high" if metric.coverage_percent < 60 else "medium"
                }
                
                # Add goal information if applicable
                for goal_module, goal_percent in report.coverage_goals.items():
                    if goal_module in module_name or module_name.startswith(goal_module):
                        area["goal"] = goal_percent
                        area["goal_gap"] = goal_percent - metric.coverage_percent
                        break
                
                uncovered_areas.append(area)
        
        # Sort by priority and coverage gap
        uncovered_areas.sort(key=lambda x: (x["priority"] != "high", -x.get("goal_gap", 0)))
        
        return uncovered_areas
    
    def generate_recommendations(self, report: CoverageReport) -> List[str]:
        """Generate recommendations for improving coverage"""
        recommendations = []
        
        # Overall recommendations
        if report.overall_coverage < report.coverage_goals.get('overall', 77.0):
            gap = report.coverage_goals['overall'] - report.overall_coverage
            recommendations.append(f"Increase overall coverage by {gap:.1f}% to meet target")
        
        # Module-specific recommendations
        uncovered_areas = self.identify_uncovered_areas(report)
        
        for area in uncovered_areas[:5]:  # Top 5 areas
            if area["priority"] == "high":
                recommendations.append(
                    f"URGENT: Add tests for {area['module']} - only {area['current_coverage']:.1f}% covered"
                )
            else:
                recommendations.append(
                    f"Improve coverage for {area['module']} - currently {area['current_coverage']:.1f}%"
                )
        
        # General recommendations
        if len(uncovered_areas) > 10:
            recommendations.append("Consider focusing on high-impact modules first")
        
        goals_met_count = sum(1 for met in report.goals_met.values() if met)
        if goals_met_count < len(report.goals_met) * 0.8:
            recommendations.append("Review test strategy - many coverage goals not met")
        
        return recommendations

class CoverageIntegration:
    """Integration with test suite and CI/CD"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.analyzer = CoverageAnalyzer(project_root)
    
    def run_coverage_with_tests(self, test_type: str = "quick") -> Optional[CoverageReport]:
        """Run coverage analysis with specific test type"""
        test_commands = {
            "quick": [
                sys.executable, "-m", "pytest",
                "--cov=core", "--cov=managers", "--cov=ui",
                "--cov-report=json", "--cov-report=term-missing",
                "tests/unit_test_framework.py"
            ],
            "full": [
                sys.executable, "-m", "pytest",
                "--cov=core", "--cov=managers", "--cov=ui",
                "--cov-report=json", "--cov-report=term-missing",
                "tests/"
            ],
            "integration": [
                sys.executable, "-m", "pytest",
                "--cov=core", "--cov=managers", "--cov=ui",
                "--cov-report=json", "--cov-report=term-missing",
                "tests/integration_test_suite.py"
            ]
        }
        
        command = test_commands.get(test_type, test_commands["quick"])
        
        print(f"🧪 Running coverage analysis with {test_type} tests...")
        report = self.analyzer.generate_coverage_report()
        
        if report:
            self.analyzer.print_coverage_summary(report)
            self.analyzer.save_coverage_report(report)
            
            # Generate trends and recommendations
            trends = self.analyzer.generate_coverage_trends(report)
            recommendations = self.analyzer.generate_recommendations(report)
            
            print(f"\n📈 Coverage Trends: {trends['trend_direction']} ({trends['coverage_trend']:+.1f}%)")
            
            if recommendations:
                print(f"\n💡 Recommendations:")
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"  {i}. {rec}")
        
        return report
    
    def check_coverage_gates(self, report: CoverageReport) -> bool:
        """Check if coverage meets quality gates"""
        gates = {
            "overall_minimum": 70.0,  # Minimum overall coverage
            "critical_modules": 85.0,  # Critical modules minimum
            "no_regression": True  # No regression from previous run
        }
        
        # Check overall minimum
        if report.overall_coverage < gates["overall_minimum"]:
            print(f"❌ Coverage gate failed: Overall coverage {report.overall_coverage:.1f}% < {gates['overall_minimum']}%")
            return False
        
        # Check critical modules
        critical_modules = ['core.entities', 'core.game_state', 'managers.roster_manager']
        for module in critical_modules:
            if module in report.goals_met and not report.goals_met[module]:
                print(f"❌ Coverage gate failed: Critical module {module} below threshold")
                return False
        
        print("✅ All coverage gates passed")
        return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Coverage analysis for TurboShells")
    parser.add_argument("--project-root", type=str, help="Project root directory")
    parser.add_argument("--test-type", choices=["quick", "full", "integration"], default="quick", help="Type of tests to run")
    parser.add_argument("--gates-only", action="store_true", help="Only check coverage gates")
    parser.add_argument("--report-only", action="store_true", help="Only generate report without running tests")
    
    args = parser.parse_args()
    
    # Create integration instance
    integration = CoverageIntegration(args.project_root)
    
    if args.report_only:
        # Generate report from existing coverage data
        report = integration.analyzer.generate_coverage_report()
        if report:
            integration.analyzer.print_coverage_summary(report)
            integration.analyzer.save_coverage_report(report)
        sys.exit(0 if report else 1)
    
    # Run coverage with tests
    report = integration.run_coverage_with_tests(args.test_type)
    
    if not report:
        sys.exit(1)
    
    # Check gates if requested
    if args.gates_only:
        gates_passed = integration.check_coverage_gates(report)
        sys.exit(0 if gates_passed else 1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
