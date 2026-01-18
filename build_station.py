"""
TurboShells Build Station
Unified build script that sets up the complete development environment.

Usage:
    python build_station.py

This will:
1. Check/create required directories
2. Set up Python virtual environment
3. Build the web frontend
4. Verify the installation
"""

import subprocess
import sys
import shutil
from pathlib import Path

# Ensure stdout uses UTF-8 on Windows for emoji support
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

REQUIRED_PYTHON = "3.12"


def print_step(msg):
    print(f"\n🟦 {msg}")


def print_success(msg):
    print(f"✅ {msg}")


def print_error(msg):
    print(f"❌ {msg}")


def print_warning(msg):
    print(f"⚠️  {msg}")


def ensure_directories():
    """Create required directories."""
    print_step("Verifying Directory Structure...")
    dirs = ["data", "logs", "scripts"]
    for d in dirs:
        p = Path(d)
        if not p.exists():
            p.mkdir(exist_ok=True)
            print_success(f"Created directory: {d}")
        else:
            print_success(f"Directory exists: {d}")


def check_node():
    """Check Node.js installation."""
    print_step("Checking Node.js...")
    node = shutil.which("node")
    npm = shutil.which("npm")
    
    if not node or not npm:
        print_error("Node.js not found. Please install Node.js 18+")
        print("Download from: https://nodejs.org/")
        return False
    
    result = subprocess.run(["node", "--version"], capture_output=True, text=True)
    print_success(f"Node.js version: {result.stdout.strip()}")
    return True


def setup_venv():
    """Set up Python virtual environment."""
    print_step("Setting up Python Virtual Environment...")
    
    # Import and run the venv builder
    try:
        subprocess.run([sys.executable, "build_venv.py"], check=True)
        print_success("Python environment ready.")
    except subprocess.CalledProcessError:
        print_error("Failed to set up Python environment.")
        return False
    return True


def setup_web():
    """Set up web frontend."""
    print_step("Setting up Web Frontend...")
    
    web_dir = Path.cwd() / "web"
    if not web_dir.exists():
        print_error("'web' directory not found.")
        return False
    
    # Install npm dependencies
    node_modules = web_dir / "node_modules"
    if not node_modules.exists():
        print("Installing npm dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=str(web_dir), check=True)
            print_success("npm dependencies installed.")
        except subprocess.CalledProcessError:
            print_error("npm install failed.")
            return False
    else:
        print_success("npm dependencies already installed.")
    
    # Build frontend
    print("Building frontend...")
    try:
        subprocess.run(["npm", "run", "build"], cwd=str(web_dir), check=True)
        print_success("Frontend built successfully.")
    except subprocess.CalledProcessError:
        print_error("Frontend build failed.")
        return False
    
    return True


def verify_installation():
    """Verify the complete installation."""
    print_step("Verifying Installation...")
    
    venv_path = Path(".venv")
    python_path = (
        venv_path / "Scripts" / "python"
        if sys.platform == "win32"
        else venv_path / "bin" / "python"
    )
    
    # Verify Python imports
    print("Testing Python imports...")
    try:
        result = subprocess.run(
            [str(python_path), "-c", "from src.engine import RaceEngine; print('RaceEngine OK')"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print_success("Python engine imports working.")
        else:
            print_warning(f"Engine import issue: {result.stderr}")
    except Exception as e:
        print_warning(f"Could not verify imports: {e}")
    
    # Verify frontend build
    dist_dir = Path("web/dist")
    if dist_dir.exists():
        files = list(dist_dir.rglob("*.js"))
        print_success(f"Frontend verified: {len(files)} JS bundles in web/dist/")
    else:
        print_warning("Frontend dist not found.")
    
    print_success("Verification complete.")


def main():
    print("=" * 60)
    print("    🐢 TurboShells Station Builder 🐢")
    print("=" * 60)
    
    ensure_directories()
    
    if not check_node():
        print_error("Node.js check failed. Web build will be skipped.")
    
    if not setup_venv():
        print_error("Python setup failed.")
        sys.exit(1)
    
    if not setup_web():
        print_warning("Web setup failed. Backend will still work.")
    
    verify_installation()
    
    print("\n" + "=" * 60)
    print("    🎉 Station Setup Complete! 🎉")
    print("=" * 60)
    print("\nTo activate Python environment:")
    if sys.platform == "win32":
        print("    .venv\\Scripts\\activate")
    else:
        print("    source .venv/bin/activate")
    
    print("\nTo run TurboShells:")
    print("    python launch.bat   (Windows)")
    print("    OR")
    print("    uvicorn src.server.app:app --port 8765")
    print("    cd web && npm run dev")


if __name__ == "__main__":
    main()
