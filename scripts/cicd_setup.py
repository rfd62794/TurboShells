#!/usr/bin/env python3
"""
CI/CD Infrastructure Setup Script for TurboShells
Sets up complete local continuous integration and development automation.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any

class CICDSetup:
    """CI/CD infrastructure setup"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.scripts_dir = self.project_root / "scripts"
        self.logs_dir = self.project_root / "logs"
        
    def create_directories(self):
        """Create necessary directories"""
        directories = [
            self.scripts_dir,
            self.logs_dir,
            self.project_root / "tests" / "reports",
            self.project_root / "docs" / "reports"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
    
    def create_requirements_file(self):
        """Create requirements.txt for development dependencies"""
        requirements = """# TurboShells Development Requirements

# Testing Framework
pytest>=7.0.0
coverage>=6.0.0
pytest-cov>=3.0.0

# Code Quality
flake8>=4.0.0
black>=22.0.0
isort>=5.0.0

# Performance Monitoring
psutil>=5.8.0
memory-profiler>=0.60.0

# Development Tools
pre-commit>=2.20.0
"""
        
        requirements_file = self.project_root / "requirements-dev.txt"
        
        try:
            with open(requirements_file, 'w') as f:
                f.write(requirements)
            print(f"✅ Created requirements file: {requirements_file}")
        except Exception as e:
            print(f"❌ Could not create requirements file: {e}")
    
    def create_makefile(self):
        """Create Makefile for common development tasks"""
        makefile_content = """# TurboShells Development Makefile

.PHONY: help test test-quick test-full ci ci-quick setup dev-report clean install-hooks

# Default target
help:
	@echo "TurboShells Development Commands:"
	@echo "  setup          - Set up development environment"
	@echo "  test-quick     - Run quick tests"
	@echo "  test-full      - Run full test suite"
	@echo "  ci-quick       - Run quick CI checks"
	@echo "  ci             - Run full CI pipeline"
	@echo "  dev-report     - Generate development report"
	@echo "  install-hooks  - Install git hooks"
	@echo "  clean          - Clean temporary files"

# Setup development environment
setup:
	python scripts/dev_automation.py --setup
	python scripts/dev_automation.py --shortcuts
	@echo "✅ Development environment setup complete"

# Install git hooks
install-hooks:
	python scripts/git_hooks.py --install
	@echo "✅ Git hooks installed"

# Quick tests
test-quick:
	python tests/comprehensive_test_runner.py --quick

# Full test suite
test-full:
	python tests/comprehensive_test_runner.py

# Quick CI checks
ci-quick:
	python scripts/local_ci.py --pre-commit

# Full CI pipeline
ci:
	python scripts/local_ci.py

# Development report
dev-report:
	python scripts/dev_automation.py --report

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type f -name "ci_report.json" -delete
	find . -type f -name "development_report.json" -delete
	find . -type f -name "daily_quality_report.json" -delete
	find . -type f -name "release_report.json" -delete
	@echo "✅ Cleaned temporary files"

# Install development dependencies
install:
	pip install -r requirements-dev.txt
	@echo "✅ Development dependencies installed"
"""
        
        makefile_path = self.project_root / "Makefile"
        
        try:
            with open(makefile_path, 'w') as f:
                f.write(makefile_content)
            print(f"✅ Created Makefile: {makefile_path}")
        except Exception as e:
            print(f"❌ Could not create Makefile: {e}")
    
    def create_vscode_tasks(self):
        """Create VS Code tasks for development"""
        vscode_dir = self.project_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        tasks_json = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Run Quick Tests",
                    "type": "shell",
                    "command": "python",
                    "args": ["tests/comprehensive_test_runner.py", "--quick"],
                    "group": {
                        "kind": "test",
                        "isDefault": True
                    },
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "problemMatcher": []
                },
                {
                    "label": "Run Full Test Suite",
                    "type": "shell",
                    "command": "python",
                    "args": ["tests/comprehensive_test_runner.py"],
                    "group": "test",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "problemMatcher": []
                },
                {
                    "label": "Run CI Checks",
                    "type": "shell",
                    "command": "python",
                    "args": ["scripts/local_ci.py"],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "problemMatcher": []
                },
                {
                    "label": "Generate Development Report",
                    "type": "shell",
                    "command": "python",
                    "args": ["scripts/dev_automation.py", "--report"],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "problemMatcher": []
                }
            ]
        }
        
        tasks_file = vscode_dir / "tasks.json"
        
        try:
            with open(tasks_file, 'w') as f:
                json.dump(tasks_json, f, indent=2)
            print(f"✅ Created VS Code tasks: {tasks_file}")
        except Exception as e:
            print(f"❌ Could not create VS Code tasks: {e}")
    
    def create_launch_json(self):
        """Create VS Code launch configuration"""
        vscode_dir = self.project_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        launch_json = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Debug TurboShells",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/main.py",
                    "console": "integratedTerminal",
                    "cwd": "${workspaceFolder}",
                    "env": {
                        "PYTHONPATH": "${workspaceFolder}"
                    }
                },
                {
                    "name": "Debug Test Runner",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/tests/comprehensive_test_runner.py",
                    "args": ["--quick"],
                    "console": "integratedTerminal",
                    "cwd": "${workspaceFolder}",
                    "env": {
                        "PYTHONPATH": "${workspaceFolder}"
                    }
                }
            ]
        }
        
        launch_file = vscode_dir / "launch.json"
        
        try:
            with open(launch_file, 'w') as f:
                json.dump(launch_json, f, indent=2)
            print(f"✅ Created VS Code launch config: {launch_file}")
        except Exception as e:
            print(f"❌ Could not create VS Code launch config: {e}")
    
    def create_settings_json(self):
        """Create VS Code settings"""
        vscode_dir = self.project_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        settings_json = {
            "python.defaultInterpreterPath": "./venv/bin/python",
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": False,
            "python.linting.flake8Enabled": True,
            "python.formatting.provider": "black",
            "python.sortImports.args": ["--profile", "black"],
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": True
            },
            "files.exclude": {
                "**/__pycache__": true,
                "**/*.pyc": true,
                ".pytest_cache": true,
                "htmlcov": true,
                ".coverage": true
            },
            "files.watcherExclude": {
                "**/__pycache__/**": True,
                "**/tests/reports/**": True,
                "**/logs/**": True
            }
        }
        
        settings_file = vscode_dir / "settings.json"
        
        try:
            with open(settings_file, 'w') as f:
                json.dump(settings_json, f, indent=2)
            print(f"✅ Created VS Code settings: {settings_file}")
        except Exception as e:
            print(f"❌ Could not create VS Code settings: {e}")
    
    def create_development_readme(self):
        """Create development README"""
        readme_content = """# TurboShells Development Guide

This document provides information for developers working on TurboShells.

## 🚀 Quick Start

### Setup Development Environment
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Set up development environment
python scripts/dev_automation.py --setup

# Install git hooks
python scripts/git_hooks.py --install

# Create development shortcuts
python scripts/dev_automation.py --shortcuts
```

### Using Make Commands
```bash
# Run quick tests
make test-quick

# Run full test suite
make test-full

# Run CI checks
make ci

# Generate development report
make dev-report

# Clean temporary files
make clean
```

## 🧪 Testing

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: System interaction testing
- **UI Tests**: User interface testing
- **Performance Tests**: Benchmark and regression testing

### Running Tests
```bash
# Quick tests (for development)
python tests/comprehensive_test_runner.py --quick

# Full test suite (for releases)
python tests/comprehensive_test_runner.py

# Specific test suite
python tests/comprehensive_test_runner.py --suite unit_tests
```

### Test Coverage Goals
- Core Game Logic: 95%+
- Manager Classes: 90%+
- UI Components: 85%+
- Integration Points: 90%+

## 🔒 Quality Gates

### Pre-commit Checks
- Python syntax validation
- Import structure check
- Quick test suite

### Pre-push Checks
- Full CI pipeline
- Performance benchmarks
- Code quality checks

### Release Preparation
- Complete test suite
- Performance validation
- Documentation coverage

## 📊 Development Automation

### Daily Quality Checks
```bash
python scripts/dev_automation.py --daily-check
```

### Development Report
```bash
python scripts/dev_automation.py --report
```

### Release Preparation
```bash
python scripts/dev_automation.py --release
```

## 🔧 Development Tools

### VS Code Integration
- Tasks for running tests and CI
- Debug configurations
- Code formatting with Black
- Import sorting with isort

### Git Hooks
- Pre-commit: Quick quality checks
- Pre-push: Full test suite
- Commit-msg: Message format validation

### Performance Monitoring
- Benchmark tracking
- Regression detection
- Memory usage monitoring

## 📁 Project Structure

```
TurboShells/
├── main.py                    # Main game entry point
├── core/                      # Core game logic
├── managers/                  # Game state managers
├── ui/                        # User interface
├── tests/                     # Test suite
│   ├── unit_test_framework.py
│   ├── integration_test_suite.py
│   ├── ui_testing_framework.py
│   ├── performance_test_suite.py
│   └── comprehensive_test_runner.py
├── scripts/                   # Development automation
│   ├── local_ci.py
│   ├── git_hooks.py
│   └── dev_automation.py
├── docs/                      # Documentation
├── logs/                      # Development logs
└── requirements-dev.txt       # Development dependencies
```

## 🎯 Best Practices

### Code Quality
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Document public APIs
- Use type hints where appropriate

### Testing
- Write tests for new features
- Maintain high coverage
- Test edge cases and error conditions
- Use mock data for consistency

### Performance
- Monitor performance metrics
- Avoid regressions
- Profile critical paths
- Optimize memory usage

### Documentation
- Update README for new features
- Document API changes
- Maintain changelog
- Provide examples

## 🐛 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure project root is in Python path
2. **Test Failures**: Check mock data generation
3. **Performance Issues**: Close other applications
4. **Git Hooks**: Reinstall if not working

### Getting Help
- Check development logs in `development.log`
- Review CI reports in `ci_report.json`
- Examine test results in `tests/reports/`
- Check performance benchmarks in `benchmark_results.json`

## 📞 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Run quality checks
5. Submit pull request

### Pull Request Requirements
- All tests must pass
- Coverage targets met
- Performance benchmarks met
- Documentation updated
- Code style compliant

---

Happy developing! 🎮
"""
        
        readme_file = self.project_root / "DEVELOPMENT.md"
        
        try:
            with open(readme_file, 'w') as f:
                f.write(readme_content)
            print(f"✅ Created development README: {readme_file}")
        except Exception as e:
            print(f"❌ Could not create development README: {e}")
    
    def setup_complete_infrastructure(self):
        """Set up complete CI/CD infrastructure"""
        print("🚀 Setting up TurboShells CI/CD Infrastructure")
        print("=" * 50)
        
        # Create directories
        print("\n📁 Creating directories...")
        self.create_directories()
        
        # Create requirements file
        print("\n📦 Creating requirements file...")
        self.create_requirements_file()
        
        # Create Makefile
        print("\n🔧 Creating Makefile...")
        self.create_makefile()
        
        # Create VS Code configuration
        print("\n💻 Creating VS Code configuration...")
        self.create_vscode_tasks()
        self.create_launch_json()
        self.create_settings_json()
        
        # Create development documentation
        print("\n📚 Creating development documentation...")
        self.create_development_readme()
        
        print("\n✅ CI/CD infrastructure setup complete!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements-dev.txt")
        print("2. Set up environment: python scripts/dev_automation.py --setup")
        print("3. Install git hooks: python scripts/git_hooks.py --install")
        print("4. Run tests: python tests/comprehensive_test_runner.py --quick")
        print("5. Check documentation: DEVELOPMENT.md")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CI/CD infrastructure setup for TurboShells")
    parser.add_argument("--project-root", type=str, help="Project root directory")
    
    args = parser.parse_args()
    
    # Create setup instance
    setup = CICDSetup(args.project_root)
    
    # Run setup
    setup.setup_complete_infrastructure()

if __name__ == "__main__":
    main()
