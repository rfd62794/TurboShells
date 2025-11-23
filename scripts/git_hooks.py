#!/usr/bin/env python3
"""
Pre-commit hooks setup for TurboShells
Automated quality checks before commits.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

def create_pre_commit_hook():
    """Create pre-commit hook script"""
    hook_content = """#!/bin/bash
# TurboShells Pre-commit Hook
# Runs automated quality checks before allowing commits

echo "🔒 Running pre-commit checks..."

# Get project root
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

# Run local CI pre-commit checks
python scripts/local_ci.py --pre-commit

# Check the result
if [ $? -eq 0 ]; then
    echo "[PASS] Pre-commit checks passed"
    exit 0
else
    echo "[FAIL] Pre-commit checks failed"
    echo "Fix the issues above before committing"
    exit 1
fi
"""
    
    return hook_content

def create_pre_push_hook():
    """Create pre-push hook script"""
    hook_content = """#!/bin/bash
# TurboShells Pre-push Hook
# Runs full test suite before pushing to remote

echo "[START] Running pre-push checks..."

# Get project root
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

# Run full CI pipeline
python scripts/local_ci.py

# Check the result
if [ $? -eq 0 ]; then
    echo "[PASS] Pre-push checks passed"
    exit 0
else
    echo "[FAIL] Pre-push checks failed"
    echo "Fix the issues before pushing"
    exit 1
fi
"""
    
    return hook_content

def create_commit_msg_hook():
    """Create commit message hook script"""
    hook_content = """#!/bin/bash
# TurboShells Commit Message Hook
# Validates commit message format

# Get commit message
MSG_FILE=$1
COMMIT_MSG=$(cat "$MSG_FILE")

# Check for minimum length
if [ ${#COMMIT_MSG} -lt 10 ]; then
    echo "[FAIL] Commit message too short (minimum 10 characters)"
    exit 1
fi

# Check for common patterns
if [[ "$COMMIT_MSG" =~ ^(fix|feat|docs|style|refactor|test|chore)(\\(.+\\))?: .+ ]]; then
    echo "[PASS] Commit message format is good"
    exit 0
else
    echo "[WARN]  Consider using conventional commit format:"
    echo "   type(scope): description"
    echo "   Types: fix, feat, docs, style, refactor, test, chore"
    echo "   Example: fix(ui): resolve button click detection issue"
    echo ""
    echo "Current message will be accepted, but consider improving format"
    exit 0
fi
"""
    
    return hook_content

def setup_git_hooks(project_root: str = None):
    """Set up git hooks"""
    project_path = Path(project_root) if project_root else Path.cwd()
    git_hooks_dir = project_path / ".git" / "hooks"
    
    if not git_hooks_dir.exists():
        print("[FAIL] Not a git repository")
        return False
    
    # Create hooks
    hooks = {
        "pre-commit": create_pre_commit_hook(),
        "pre-push": create_pre_push_hook(),
        "commit-msg": create_commit_msg_hook()
    }
    
    success = True
    
    for hook_name, hook_content in hooks.items():
        hook_file = git_hooks_dir / hook_name
        
        try:
            with open(hook_file, 'w') as f:
                f.write(hook_content)
            
            # Make executable
            os.chmod(hook_file, 0o755)
            print(f"[PASS] Created {hook_name} hook")
            
        except Exception as e:
            print(f"[FAIL] Failed to create {hook_name} hook: {e}")
            success = False
    
    return success

def create_hook_installer():
    """Create hook installer script"""
    installer_content = """#!/usr/bin/env python3
\"\"\"
Git Hooks Installer for TurboShells
Installs pre-commit, pre-push, and commit-msg hooks.
\"\"\"

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.git_hooks import setup_git_hooks

def main():
    print("[FIX] Installing TurboShells Git Hooks...")
    
    success = setup_git_hooks()
    
    if success:
        print("[PASS] Git hooks installed successfully!")
        print("\\nHooks installed:")
        print("  🔒 pre-commit: Runs quick quality checks before commits")
        print("  [START] pre-push: Runs full test suite before pushes")
        print("  📝 commit-msg: Validates commit message format")
        print("\\nTo bypass hooks (not recommended):")
        print("  git commit --no-verify")
        print("  git push --no-verify")
    else:
        print("[FAIL] Failed to install git hooks")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
    
    return installer_content

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Git hooks setup for TurboShells")
    parser.add_argument("--install", action="store_true", help="Install git hooks")
    parser.add_argument("--project-root", type=str, help="Project root directory")
    
    args = parser.parse_args()
    
    if args.install:
        success = setup_git_hooks(args.project_root)
        if success:
            print("[PASS] Git hooks installed successfully!")
        else:
            print("[FAIL] Failed to install git hooks")
            sys.exit(1)
    else:
        print("Use --install to install git hooks")
        print("Or run: python scripts/git_hooks.py --install")

if __name__ == "__main__":
    main()
