#!/usr/bin/env python3
"""
Windows-Compatible Commit Message Hook for TurboShells
Validates commit message format and content.
"""

import sys
import re

def print_status(status, message):
    """Print colored status message"""
    colors = {
        'PASS': '\033[0;32m',
        'FAIL': '\033[0;31m', 
        'WARN': '\033[1;33m',
        'INFO': '\033[0;34m',
        'NC': '\033[0m'
    }
    color = colors.get(status, colors['NC'])
    print(f"{color}[{status}] {message}{colors['NC']}")

def main():
    if len(sys.argv) < 2:
        print("Usage: commit-msg-hook <commit_msg_file>")
        sys.exit(1)
    
    msg_file = sys.argv[1]
    
    try:
        with open(msg_file, 'r', encoding='utf-8') as f:
            commit_msg = f.read().strip()
    except Exception as e:
        print(f"Error reading commit message: {e}")
        sys.exit(1)
    
    # Check for minimum length
    if len(commit_msg) < 10:
        print_status("FAIL", "Commit message too short (minimum 10 characters)")
        print("Please provide a more descriptive commit message")
        sys.exit(1)
    
    # Check for common patterns
    conventional_pattern = r'^(fix|feat|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?: .+'
    
    if re.match(conventional_pattern, commit_msg):
        print_status("PASS", "Conventional commit format")
        
        # Additional checks for specific types
        if commit_msg.startswith("feat("):
            print_status("INFO", "Feature detected - ensure tests are included")
        elif commit_msg.startswith("fix("):
            print_status("INFO", "Bug fix detected - ensure issue is referenced")
        elif commit_msg.startswith("perf("):
            print_status("INFO", "Performance change detected - benchmarks updated")
        
        sys.exit(0)
    else:
        print_status("WARN", "Consider using conventional commit format:")
        print("   type(scope): description")
        print("   Types: fix, feat, docs, style, refactor, test, chore, perf, ci, build, revert")
        print("   Example: fix(ui): resolve button click detection issue")
        print("")
        print("Current message will be accepted, but consider improving format")
        sys.exit(0)

if __name__ == "__main__":
    main()
