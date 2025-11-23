#!/usr/bin/env python3
"""
Development environment setup script for TurboShells.
This script helps set up a clean development environment with all necessary tools.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, check=True):
    """Run a command and handle errors."""
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version < (3, 8):
        print(f"[FAIL] Python {version.major}.{version.minor} is not supported. Please use Python 3.8+")
        return False
    print(f"[PASS] Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def setup_virtual_environment():
    """Set up Python virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("[PASS] Virtual environment already exists")
        return True
    
    print("[FIX] Creating virtual environment...")
    success, stdout, stderr = run_command(f"{sys.executable} -m venv venv")
    
    if success:
        print("[PASS] Virtual environment created successfully")
        return True
    else:
        print(f"[FAIL] Failed to create virtual environment: {stderr}")
        return False


def install_dependencies():
    """Install project dependencies."""
    print("📦 Installing dependencies...")
    
    # Determine pip command based on platform
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix-like
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip first
    success, _, _ = run_command(f"{pip_cmd} install --upgrade pip")
    if not success:
        print("[WARN]  Failed to upgrade pip, continuing...")
    
    # Install requirements
    success, stdout, stderr = run_command(f"{pip_cmd} install -r requirements.txt")
    
    if success:
        print("[PASS] Dependencies installed successfully")
        return True
    else:
        print(f"[FAIL] Failed to install dependencies: {stderr}")
        return False


def install_dev_dependencies():
    """Install development dependencies."""
    print("🛠️  Installing development dependencies...")
    
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix-like
        pip_cmd = "venv/bin/pip"
    
    # Install dev dependencies
    success, stdout, stderr = run_command(f"{pip_cmd} install -e .[dev]")
    
    if success:
        print("[PASS] Development dependencies installed successfully")
        return True
    else:
        print(f"[FAIL] Failed to install development dependencies: {stderr}")
        return False


def setup_pre_commit():
    """Set up pre-commit hooks."""
    print("[LINK] Setting up pre-commit hooks...")
    
    if os.name == 'nt':  # Windows
        precommit_cmd = "venv\\Scripts\\pre-commit"
    else:  # Unix-like
        precommit_cmd = "venv/bin/pre-commit"
    
    # Install pre-commit
    success, stdout, stderr = run_command(f"{precommit_cmd} install")
    
    if success:
        print("[PASS] Pre-commit hooks installed successfully")
        return True
    else:
        print(f"[FAIL] Failed to install pre-commit hooks: {stderr}")
        return False


def run_tests():
    """Run the test suite to verify setup."""
    print("[TEST] Running tests to verify setup...")
    
    if os.name == 'nt':  # Windows
        pytest_cmd = "venv\\Scripts\\pytest"
    else:  # Unix-like
        pytest_cmd = "venv/bin/pytest"
    
    success, stdout, stderr = run_command(f"{pytest_cmd} tests/ -v")
    
    if success:
        print("[PASS] Tests passed successfully")
        return True
    else:
        print(f"[WARN]  Some tests failed: {stderr}")
        return False


def print_next_steps():
    """Print next steps for the developer."""
    print("\n[SUCCESS] Development environment setup complete!")
    print("\n[INFO] Next steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix-like
        print("   source venv/bin/activate")
    print("\n2. Run the game:")
    print("   python main.py")
    print("\n3. Run tests:")
    print("   pytest tests/")
    print("\n4. Format code:")
    print("   black .")
    print("\n5. Lint code:")
    print("   pylint .")
    print("\n6. Install pre-commit hooks (if not done automatically):")
    print("   pre-commit install")


def main():
    """Main setup function."""
    print("[START] TurboShells Development Environment Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Set up virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Install development dependencies
    if not install_dev_dependencies():
        sys.exit(1)
    
    # Set up pre-commit hooks
    if not setup_pre_commit():
        print("[WARN]  Pre-commit setup failed, but you can continue without it")
    
    # Run tests
    run_tests()
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
