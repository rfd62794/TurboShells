#!/usr/bin/env python3
"""
Windows Git Hook Runner
Handles Windows Python path issues for Git hooks.
Version 1.1 - Enhanced error handling.
"""

import sys
import os
from pathlib import Path

def main():
    # Get the hook script path from command line arguments
    if len(sys.argv) < 2:
        print("Usage: git_hook_runner.py <hook_script_path> [args...]")
        sys.exit(1)
    
    hook_script = sys.argv[1]
    hook_args = sys.argv[2:]
    
    # Use current Python executable to avoid Windows path issues
    python_exe = sys.executable
    
    # Build the command
    cmd = [python_exe, hook_script] + hook_args
    
    # Execute the hook script
    import subprocess
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running hook: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
