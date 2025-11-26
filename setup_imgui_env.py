#!/usr/bin/env python3
"""
ImGui Environment Setup for TurboShells
Creates Python 3.12 virtual environment and installs ImGui dependencies
"""

import subprocess
import sys
import venv
from pathlib import Path


def create_virtual_environment():
    """Create Python 3.12 virtual environment with ImGui support"""
    print("=== TurboShells ImGui Environment Setup ===")
    print()
    
    # Check Python version
    if sys.version_info < (3, 12):
        print("WARNING: Python 3.12+ recommended for best ImGui compatibility")
        print(f"Current Python version: {sys.version}")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    # Create virtual environment
    venv_path = Path(__file__).parent / "venv"
    print(f"Creating virtual environment at: {venv_path}")
    
    try:
        venv.create(venv_path, with_pip=True, clear=True)
        print("✅ Virtual environment created successfully")
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False
    
    # Determine pip executable path
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # Upgrade pip
    print("Upgrading pip...")
    try:
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        print("✅ Pip upgraded")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to upgrade pip: {e}")
        return False
    
    # Install ImGui dependencies with precompiled wheels
    print("Installing ImGui dependencies...")
    imgui_packages = [
        "imgui[pygame]>=2.0.0",
        "PyOpenGL>=3.1.0",
        "PyOpenGL-accelerate>=3.1.0",
        "pygame-ce>=2.5"
    ]
    
    try:
        # Install with precompiled wheels only
        subprocess.run([
            str(pip_path), 
            "install", 
            "--only-binary=all",
            "--upgrade"
        ] + imgui_packages, check=True)
        print("✅ ImGui dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install ImGui dependencies: {e}")
        print("Trying without binary restriction...")
        try:
            subprocess.run([str(pip_path), "install", "--upgrade"] + imgui_packages, check=True)
            print("✅ ImGui dependencies installed (fallback)")
        except subprocess.CalledProcessError as e2:
            print(f"❌ Failed to install ImGui dependencies (fallback): {e2}")
            return False
    
    # Install remaining dependencies
    print("Installing remaining dependencies...")
    try:
        subprocess.run([
            str(pip_path), 
            "install", 
            "-r", 
            "requirements.txt"
        ], check=True)
        print("✅ All dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install remaining dependencies: {e}")
        return False
    
    # Test ImGui import
    print("Testing ImGui import...")
    try:
        result = subprocess.run([
            str(python_path), 
            "-c", 
            "import imgui; import pygame; import OpenGL.GL as gl; print('✅ ImGui import test successful')"
        ], capture_output=True, text=True, check=True)
        print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"❌ ImGui import test failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False
    
    # Setup instructions
    print()
    print("=== Setup Complete! ===")
    print()
    print("To activate the environment:")
    if sys.platform == "win32":
        print(f"   {venv_path}\\Scripts\\activate")
    else:
        print(f"   source {venv_path}/bin/activate")
    print()
    print("To run the game:")
    print("   python run_game.py")
    print()
    print("To test ImGui specifically:")
    print("   python test_imgui_integration.py")
    print()
    
    return True


if __name__ == "__main__":
    success = create_virtual_environment()
    sys.exit(0 if success else 1)
