"""
TurboShells Build Venv
Creates and syncs the Python virtual environment for the FastAPI backend.
"""

import subprocess
import sys
import shutil
from pathlib import Path

# Ensure stdout uses UTF-8 on Windows for emoji support
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

REQUIRED_VERSION = "3.12"


def find_python_312():
    """Attempt to find a Python 3.12 executable."""
    # Check current interpreter
    if sys.version_info[:2] == (3, 12):
        return sys.executable

    # Check 'py' launcher on Windows
    if sys.platform == "win32" and shutil.which("py"):
        try:
            res = subprocess.run(
                ["py", "-3.12", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if res.returncode == 0:
                print("✅ Found Python 3.12 via 'py' launcher.")
                return "py -3.12"
        except Exception:
            pass

    # Check explicit binaries
    candidates = ["python3.12", "python3.12.exe", "python-3.12"]
    for cand in candidates:
        path = shutil.which(cand)
        if path:
            return path

    return None


def setup_venv():
    """Initialize and sync the virtual environment using uv or standard venv."""
    uv_executable = shutil.which("uv")

    if uv_executable:
        print("🚀 UV detected. Enforcing Python 3.12...")
        try:
            subprocess.run(["uv", "venv", "--python", REQUIRED_VERSION], check=True)
            subprocess.run(["uv", "sync"], check=True)
            print("✅ Environment synced successfully using UV with Python 3.12.")
            return
        except subprocess.CalledProcessError as e:
            print(f"⚠️ UV Sync Failed: {e}")
            print("Attempting fallback...")

    print("⚠️ UV not found or failed. Falling back to standard 'venv'...")

    python_exe = find_python_312()
    if not python_exe:
        print(f"❌ Critical Error: Python {REQUIRED_VERSION} not found on this system.")
        print("Please install Python 3.12 via python.org or standard package manager.")
        sys.exit(1)

    venv_path = Path(".venv")

    # Delete existing venv to prevent version conflicts
    if venv_path.exists():
        print(f"♻️  Removing existing {venv_path}...")
        try:
            shutil.rmtree(venv_path)
            print("✅ Existing venv removed.")
        except Exception as e:
            print(f"⚠️  Failed to remove .venv: {e}")
            print("Please manually delete the folder and try again.")
            sys.exit(1)

    # Create venv
    cmd = []
    if python_exe.startswith("py "):
        cmd = python_exe.split() + ["-m", "venv", str(venv_path)]
    else:
        cmd = [python_exe, "-m", "venv", str(venv_path)]

    print(f"Creating venv with: {cmd}")
    subprocess.run(cmd, check=True)

    # Paths
    pip_path = (
        venv_path / "Scripts" / "pip"
        if sys.platform == "win32"
        else venv_path / "bin" / "pip"
    )
    python_path = (
        venv_path / "Scripts" / "python"
        if sys.platform == "win32"
        else venv_path / "bin" / "python"
    )

    try:
        # Upgrade pip
        print("⬆️  Upgrading pip...")
        subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)

        # Install from pyproject.toml with server extras
        print("📦 Installing dependencies from pyproject.toml...")
        subprocess.run([str(pip_path), "install", "-e", ".[server]"], check=True)

        # Verify Python version
        print("🔍 Verifying Python version...")
        result = subprocess.run(
            [str(python_path), "--version"], capture_output=True, text=True
        )
        version_str = result.stdout.strip()
        if "3.12" not in version_str:
            print(f"⚠️  Warning: Expected Python 3.12, got {version_str}")
        else:
            print(f"✅ Python version verified: {version_str}")

        print("✅ Environment setup complete using standard pip.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Pip Install Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_venv()
