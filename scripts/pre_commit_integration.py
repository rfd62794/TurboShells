#!/usr/bin/env python3
"""
Pre-commit Integration Script for TurboShells
Installs and configures pre-commit hooks with full test suite integration.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any

class PreCommitIntegrator:
    """Pre-commit hooks integration and management"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.git_hooks_dir = self.project_root / ".git" / "hooks"
        
    def is_git_repository(self) -> bool:
        """Check if current directory is a git repository"""
        return (self.project_root / ".git").exists()
    
    def install_pre_commit_config(self):
        """Create .pre-commit-config.yaml for pre-commit framework"""
        config_content = """# TurboShells Pre-commit Configuration
repos:
  - repo: local
    hooks:
      # Python syntax check
      - id: python-syntax
        name: Python Syntax Check
        entry: python -m py_compile
        language: system
        files: ^.*\\.py$
        
      # Import structure check
      - id: import-check
        name: Import Structure Check
        entry: python scripts/local_ci.py --pre-commit
        language: system
        pass_filenames: false
        always_run: true
        
      # Quick test suite
      - id: quick-tests
        name: Quick Test Suite
        entry: python tests/comprehensive_test_runner.py --quick
        language: system
        pass_filenames: false
        always_run: true
        
      # Code style check
      - id: code-style
        name: Code Style Check
        entry: python scripts/local_ci.py
        language: system
        pass_filenames: false
        always_run: true
        
      # Documentation check
      - id: docs-check
        name: Documentation Coverage
        entry: python scripts/local_ci.py
        language: system
        pass_filenames: false
        always_run: true

  # Built-in hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: check-added-large-files
      - id: debug-statements

  # Python hooks
  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/isort
    rev: 5.11.4
    hooks:
      - id: isort
        args: ["--profile", "black"]
        
  - repo: https://github.com/pycqa/flake8
    rev: 5.0.4
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]
"""
        
        config_file = self.project_root / ".pre-commit-config.yaml"
        
        try:
            with open(config_file, 'w') as f:
                f.write(config_content)
            print(f"✅ Created pre-commit config: {config_file}")
            return True
        except Exception as e:
            print(f"❌ Could not create pre-commit config: {e}")
            return False
    
    def create_enhanced_git_hooks(self):
        """Create enhanced git hooks with full test suite integration"""
        if not self.is_git_repository():
            print("❌ Not a git repository")
            return False
        
        hooks = {
            "pre-commit": self.create_enhanced_pre_commit_hook(),
            "pre-push": self.create_enhanced_pre_push_hook(),
            "commit-msg": self.create_enhanced_commit_msg_hook(),
            "post-checkout": self.create_post_checkout_hook(),
            "post-merge": self.create_post_merge_hook()
        }
        
        success = True
        
        for hook_name, hook_content in hooks.items():
            hook_file = self.git_hooks_dir / hook_name
            
            try:
                with open(hook_file, 'w') as f:
                    f.write(hook_content)
                
                # Make executable
                os.chmod(hook_file, 0o755)
                print(f"✅ Created {hook_name} hook")
                
            except Exception as e:
                print(f"❌ Failed to create {hook_name} hook: {e}")
                success = False
        
        return success
    
    def create_enhanced_pre_commit_hook(self):
        """Create enhanced pre-commit hook"""
        return """#!/bin/bash
# TurboShells Enhanced Pre-commit Hook
# Comprehensive quality checks before commits

echo "🔒 Running enhanced pre-commit checks..."

# Get project root
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}❌ $message${NC}"
    else
        echo -e "${YELLOW}⚠️  $message${NC}"
    fi
}

# Track overall success
OVERALL_SUCCESS=0

# 1. Python syntax check
echo "🔍 Checking Python syntax..."
python_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\\.py$' || true)
if [ -n "$python_files" ]; then
    syntax_errors=0
    for file in $python_files; do
        if ! python -m py_compile "$file" 2>/dev/null; then
            print_status "FAIL" "Syntax error in $file"
            syntax_errors=$((syntax_errors + 1))
        fi
    done
    
    if [ $syntax_errors -eq 0 ]; then
        print_status "PASS" "Python syntax check"
    else
        print_status "FAIL" "Python syntax check ($syntax_errors errors)"
        OVERALL_SUCCESS=1
    fi
else
    print_status "PASS" "Python syntax check (no Python files)"
fi

# 2. Import structure check
echo "🔗 Checking import structure..."
if python scripts/local_ci.py --pre-commit > /dev/null 2>&1; then
    print_status "PASS" "Import structure check"
else
    print_status "FAIL" "Import structure check"
    OVERALL_SUCCESS=1
fi

# 3. Quick test suite
echo "🧪 Running quick test suite..."
if python tests/comprehensive_test_runner.py --quick > /dev/null 2>&1; then
    print_status "PASS" "Quick test suite"
else
    print_status "FAIL" "Quick test suite"
    OVERALL_SUCCESS=1
fi

# 4. Code style check
echo "📝 Checking code style..."
if python scripts/local_ci.py > /dev/null 2>&1; then
    print_status "PASS" "Code style check"
else
    print_status "WARN" "Code style issues found (not blocking)"
fi

# 5. Documentation check
echo "📚 Checking documentation coverage..."
if python scripts/local_ci.py > /dev/null 2>&1; then
    print_status "PASS" "Documentation coverage"
else
    print_status "WARN" "Documentation issues found (not blocking)"
fi

# Final result
echo ""
if [ $OVERALL_SUCCESS -eq 0 ]; then
    print_status "PASS" "All pre-commit checks passed"
    echo "🎉 Ready to commit!"
    exit 0
else
    print_status "FAIL" "Pre-commit checks failed"
    echo "🔧 Fix the issues above before committing"
    echo "💡 To bypass: git commit --no-verify"
    exit 1
fi
"""
    
    def create_enhanced_pre_push_hook(self):
        """Create enhanced pre-push hook"""
        return """#!/bin/bash
# TurboShells Enhanced Pre-push Hook
# Full test suite and quality checks before pushes

echo "🚀 Running enhanced pre-push checks..."

# Get project root
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

print_status() {
    local status=$1
    local message=$2
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}❌ $message${NC}"
    else
        echo -e "${YELLOW}⚠️  $message${NC}"
    fi
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Track overall success
OVERALL_SUCCESS=0

print_info "Running comprehensive pre-push validation..."

# 1. Full test suite
echo "🧪 Running full test suite..."
if python tests/comprehensive_test_runner.py; then
    print_status "PASS" "Full test suite"
else
    print_status "FAIL" "Full test suite"
    OVERALL_SUCCESS=1
fi

# 2. Performance benchmarks
echo "⚡ Running performance benchmarks..."
if python tests/performance_test_suite.py > /dev/null 2>&1; then
    print_status "PASS" "Performance benchmarks"
else
    print_status "WARN" "Performance benchmarks failed (not blocking)"
fi

# 3. Complete CI pipeline
echo "🔧 Running complete CI pipeline..."
if python scripts/local_ci.py; then
    print_status "PASS" "Complete CI pipeline"
else
    print_status "FAIL" "Complete CI pipeline"
    OVERALL_SUCCESS=1
fi

# 4. Development report generation
echo "📊 Generating development report..."
if python scripts/dev_automation.py --report > /dev/null 2>&1; then
    print_status "PASS" "Development report generated"
else
    print_status "WARN" "Development report failed (not blocking)"
fi

# Final result
echo ""
if [ $OVERALL_SUCCESS -eq 0 ]; then
    print_status "PASS" "All pre-push checks passed"
    echo "🎉 Ready to push!"
    exit 0
else
    print_status "FAIL" "Pre-push checks failed"
    echo "🔧 Fix the issues above before pushing"
    echo "💡 To bypass: git push --no-verify"
    exit 1
fi
"""
    
    def create_enhanced_commit_msg_hook(self):
        """Create enhanced commit message hook"""
        return """#!/bin/bash
# TurboShells Enhanced Commit Message Hook
# Validates commit message format and content

MSG_FILE=$1
COMMIT_MSG=$(cat "$MSG_FILE")

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

print_status() {
    local status=$1
    local message=$2
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}❌ $message${NC}"
    else
        echo -e "${YELLOW}⚠️  $message${NC}"
    fi
}

# Check for minimum length
if [ ${#COMMIT_MSG} -lt 10 ]; then
    print_status "FAIL" "Commit message too short (minimum 10 characters)"
    echo "💡 Please provide a more descriptive commit message"
    exit 1
fi

# Check for common patterns
if [[ "$COMMIT_MSG" =~ ^(fix|feat|docs|style|refactor|test|chore|perf|ci|build|revert)(\\(.+\\))?: .+ ]]; then
    print_status "PASS" "Conventional commit format"
    
    # Additional checks for specific types
    if [[ "$COMMIT_MSG" =~ ^feat\\(.+\\): ]]; then
        print_status "INFO" "Feature detected - ensure tests are included"
    elif [[ "$COMMIT_MSG" =~ ^fix\\(.+\\): ]]; then
        print_status "INFO" "Bug fix detected - ensure issue is referenced"
    elif [[ "$COMMIT_MSG" =~ ^perf\\(.+\\): ]]; then
        print_status "INFO" "Performance change detected - benchmarks updated"
    fi
    
    exit 0
else
    print_status "WARN" "Consider using conventional commit format:"
    echo "   type(scope): description"
    echo "   Types: fix, feat, docs, style, refactor, test, chore, perf, ci, build, revert"
    echo "   Example: fix(ui): resolve button click detection issue"
    echo ""
    echo "Current message will be accepted, but consider improving format"
    exit 0
fi
"""
    
    def create_post_checkout_hook(self):
        """Create post-checkout hook"""
        return """#!/bin/bash
# TurboShells Post-checkout Hook
# Runs setup after checkout

# Get project root
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

# Only run on branch checkout
if [ "$3" = "1" ]; then
    echo "🔄 Post-checkout: Running setup..."
    
    # Update dependencies if needed
    if [ -f "requirements-dev.txt" ]; then
        echo "📦 Checking dependencies..."
        pip install -r requirements-dev.txt > /dev/null 2>&1 || true
    fi
    
    # Run quick validation
    echo "🧪 Quick validation..."
    python scripts/local_ci.py --pre-commit > /dev/null 2>&1 || true
    
    echo "✅ Post-checkout complete"
fi
"""
    
    def create_post_merge_hook(self):
        """Create post-merge hook"""
        return """#!/bin/bash
# TurboShells Post-merge Hook
# Runs validation after merge

# Get project root
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

echo "🔄 Post-merge: Running validation..."

# Run quick tests to ensure merge didn't break anything
echo "🧪 Quick validation..."
python tests/comprehensive_test_runner.py --quick || true

echo "✅ Post-merge complete"
"""
    
    def install_pre_commit_framework(self):
        """Install pre-commit framework if not available"""
        try:
            # Check if pre-commit is available
            result = subprocess.run(
                ["pre-commit", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Pre-commit framework already available")
                return True
        except FileNotFoundError:
            pass
        
        # Install pre-commit
        print("📦 Installing pre-commit framework...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pre-commit"], check=True)
            print("✅ Pre-commit framework installed")
            return True
        except subprocess.CalledProcessError:
            print("⚠️  Could not install pre-commit framework")
            return False
    
    def setup_complete_integration(self):
        """Set up complete pre-commit integration"""
        print("🔧 Setting up complete pre-commit integration...")
        print("=" * 50)
        
        if not self.is_git_repository():
            print("❌ Not a git repository - cannot install hooks")
            return False
        
        # Create pre-commit config
        print("\n📝 Creating pre-commit configuration...")
        config_success = self.install_pre_commit_config()
        
        # Install pre-commit framework
        print("\n📦 Installing pre-commit framework...")
        framework_success = self.install_pre_commit_framework()
        
        # Create enhanced git hooks
        print("\n🔗 Creating enhanced git hooks...")
        hooks_success = self.create_enhanced_git_hooks()
        
        # Install pre-commit hooks if framework is available
        if framework_success and config_success:
            print("\n⚙️  Installing pre-commit hooks...")
            try:
                subprocess.run(["pre-commit", "install"], check=True, cwd=self.project_root)
                print("✅ Pre-commit hooks installed")
            except subprocess.CalledProcessError:
                print("⚠️  Could not install pre-commit hooks")
        
        # Summary
        print("\n📊 Integration Summary:")
        print(f"  Pre-commit config: {'✅' if config_success else '❌'}")
        print(f"  Pre-commit framework: {'✅' if framework_success else '❌'}")
        print(f"  Enhanced git hooks: {'✅' if hooks_success else '❌'}")
        
        overall_success = config_success and hooks_success
        
        if overall_success:
            print("\n🎉 Pre-commit integration complete!")
            print("\nFeatures enabled:")
            print("  🔒 Pre-commit: Syntax, imports, quick tests, style checks")
            print("  🚀 Pre-push: Full test suite, performance benchmarks")
            print("  📝 Commit-msg: Format validation")
            print("  🔄 Post-checkout: Environment setup")
            print("  🔄 Post-merge: Validation after merge")
            print("\nUsage:")
            print("  git commit                    # Runs pre-commit checks")
            print("  git push                      # Runs pre-push checks")
            print("  pre-commit run --all-files    # Run all checks manually")
            print("  pre-commit install            # Reinstall hooks")
        else:
            print("\n❌ Pre-commit integration incomplete")
        
        return overall_success

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pre-commit integration for TurboShells")
    parser.add_argument("--project-root", type=str, help="Project root directory")
    parser.add_argument("--config-only", action="store_true", help="Only create config file")
    parser.add_argument("--hooks-only", action="store_true", help="Only create git hooks")
    
    args = parser.parse_args()
    
    # Create integrator instance
    integrator = PreCommitIntegrator(args.project_root)
    
    # Run requested action
    if args.config_only:
        success = integrator.install_pre_commit_config()
        sys.exit(0 if success else 1)
    elif args.hooks_only:
        success = integrator.create_enhanced_git_hooks()
        sys.exit(0 if success else 1)
    else:
        success = integrator.setup_complete_integration()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
