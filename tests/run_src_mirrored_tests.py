#!/usr/bin/env python3
"""
SRC-MIRRORED test runner for TurboShells test suite
Runs tests organized to mirror the src directory structure.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_test_suite(test_path, suite_name, coverage=True):
    """Run a specific test suite"""
    print(f"\n{'='*60}")
    print(f"RUNNING {suite_name.upper()} TESTS")
    print(f"{'='*60}")
    
    cmd = [sys.executable, "-m", "pytest", str(test_path), "-v"]
    
    if coverage and "core" in str(test_path):
        cmd.extend(["--cov=src", "--cov-report=term-missing"])
    
    start_time = time.time()
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent, capture_output=True, text=True)
    duration = time.time() - start_time
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    # Parse results
    lines = result.stdout.split('\n')
    for line in lines:
        if "passed" in line and ("failed" in line or "error" in line):
            print(f"\n📊 {suite_name.upper()} Results: {line.strip()}")
            break
        elif "passed" in line and "failed" not in line and "error" not in line:
            print(f"\n📊 {suite_name.upper()} Results: {line.strip()}")
            break
    
    print(f"⏱️  Duration: {duration:.2f}s")
    return result.returncode == 0


def main():
    """Main test runner"""
    print("🚀 TURBOSHELLS SRC-MIRRORED TEST RUNNER")
    print("=" * 60)
    
    test_dir = Path(__file__).parent
    project_root = test_dir.parent
    
    # Define test suites mirroring src structure
    test_suites = [
        (test_dir / "src/core/game", "Core Game"),
        (test_dir / "src/genetics", "Genetics"),
        (test_dir / "src/core", "Core Data & Error Handling"),
        (test_dir / "integration", "Integration Tests"),
        (test_dir / "performance", "Performance Tests"),
    ]
    
    results = {}
    total_start_time = time.time()
    
    # Run each test suite
    for test_path, suite_name in test_suites:
        if test_path.exists():
            success = run_test_suite(test_path, suite_name)
            results[suite_name] = success
        else:
            print(f"\n⚠️  {suite_name} directory not found: {test_path}")
            results[suite_name] = None
    
    total_duration = time.time() - total_start_time
    
    # Summary
    print(f"\n{'='*60}")
    print("📈 TEST SUITE SUMMARY")
    print(f"{'='*60}")
    
    for suite_name, success in results.items():
        if success is True:
            status = "✅ PASSED"
        elif success is False:
            status = "❌ FAILED"
        else:
            status = "⚠️  NOT FOUND"
        print(f"{suite_name:<30}: {status}")
    
    print(f"\n⏱️  Total Duration: {total_duration:.2f}s")
    
    # Overall result
    failed_suites = [name for name, success in results.items() if success is False]
    if failed_suites:
        print(f"\n❌ Failed test suites: {', '.join(failed_suites)}")
        return 1
    else:
        print(f"\n✅ All test suites passed!")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
