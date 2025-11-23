#!/usr/bin/env python3
"""
Simple test runner for TurboShells test suite
"""

import subprocess
import sys
import json
from pathlib import Path

def run_pytest(test_files=None, coverage=True, verbose=True):
    """Run pytest with given options"""
    cmd = [sys.executable, "-m", "pytest"]
    
    if test_files:
        cmd.extend(test_files)
    else:
        cmd.append("tests/")
    
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing"])
    
    if verbose:
        cmd.append("-v")
    
    # Run pytest
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
    
    return result

def main():
    """Main test runner"""
    print("=" * 60)
    print("TURBOSHELLS TEST RUNNER")
    print("=" * 60)
    
    # Run unit tests
    print("\n🧪 Running Unit Tests...")
    result = run_pytest(["tests/test_core_entities.py", "tests/test_game_systems.py"], coverage=False)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    # Parse results
    lines = result.stdout.split('\n')
    for line in lines:
        if "passed" in line and "failed" in line:
            print(f"\n📊 Results: {line.strip()}")
            break
    
    # Run with coverage if requested
    if "--coverage" in sys.argv:
        print("\n📈 Running with Coverage...")
        result = run_pytest(["tests/test_core_entities.py", "tests/test_game_systems.py"], coverage=True)
        print(result.stdout)
    
    print("\n✅ Test run completed!")

if __name__ == "__main__":
    main()
