#!/usr/bin/env python3
"""
TurboShells Test Suite Runner
Runs all test suites and provides comprehensive reporting.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_test_file(test_file):
    """Run a single test file and return results"""
    print(f"\n{'=' * 60}")
    print(f"Running {test_file}")
    print('=' * 60)

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )

        end_time = time.time()
        duration = end_time - start_time

        # Print output
        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("STDERR:", result.stderr)

        success = result.returncode == 0

        return {
            'file': test_file.name,
            'success': success,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }

    except Exception as e:
        print(f"Error running {test_file}: {e}")
        return {
            'file': test_file.name,
            'success': False,
            'duration': 0,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }


def main():
    """Run all test suites"""
    print("TurboShells Comprehensive Test Suite")
    print("=" * 60)

    # Find all test files
    tests_dir = Path(__file__).parent
    test_files = list(tests_dir.glob("test_*.py"))

    if not test_files:
        print("No test files found!")
        return False

    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  - {test_file.name}")

    # Run all tests
    all_results = []
    total_start_time = time.time()

    for test_file in test_files:
        result = run_test_file(test_file)
        all_results.append(result)

    total_end_time = time.time()
    total_duration = total_end_time - total_start_time

    # Generate summary report
    print(f"\n{'=' * 60}")
    print("TEST SUITE SUMMARY")
    print('=' * 60)

    passed = sum(1 for r in all_results if r['success'])
    failed = len(all_results) - passed

    print(f"Total Tests: {len(all_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total Duration: {total_duration:.2f}s")

    # Individual test results
    print(f"\n{'=' * 60}")
    print("INDIVIDUAL TEST RESULTS")
    print('=' * 60)

    for result in all_results:
        status = "PASS" if result['success'] else "FAIL"
        duration = result['duration']
        print(f"{result['file']:<30} {status:<8} {duration:>6.2f}s")

        if not result['success']:
            print(f"  Error: {result['stderr'][:100]}...")

    # Performance summary
    print(f"\n{'=' * 60}")
    print("PERFORMANCE SUMMARY")
    print('=' * 60)

    for result in all_results:
        if 'performance' in result['file'].lower():
            print(f"{result['file']}: {result['duration']:.2f}s")

    # Overall success
    print(f"\n{'=' * 60}")
    if failed == 0:
        print("ALL TESTS PASSED!")
        print("TurboShells test suite is fully functional!")
        return True
    else:
        print(f"{failed} TESTS FAILED")
        print("Review the errors above and fix issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
