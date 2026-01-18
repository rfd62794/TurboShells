"""
TurboShells Build Web
Builds the React/PixiJS frontend using npm.
"""

import subprocess
import sys
import shutil
from pathlib import Path


def build_web():
    """Build the web frontend using npm."""
    print("[WEB] Building React/PixiJS Frontend...")

    web_dir = Path.cwd() / "web"
    if not web_dir.exists():
        print("[ERROR] 'web' directory not found.")
        sys.exit(1)

    # Check for npm
    npm_executable = shutil.which("npm")
    if not npm_executable:
        print("[ERROR] npm not found. Please install Node.js.")
        sys.exit(1)

    # Check for node_modules
    node_modules = web_dir / "node_modules"
    if not node_modules.exists():
        print("[NPM] Installing dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=str(web_dir), check=True)
            print("[OK] Dependencies installed.")
        except subprocess.CalledProcessError:
            print("[ERROR] npm install failed.")
            sys.exit(1)

    # Run build
    print("[NPM] Running production build...")
    try:
        subprocess.run(["npm", "run", "build"], cwd=str(web_dir), check=True)
        print("[OK] Frontend Built Successfully!")

        # Verify output
        dist_dir = web_dir / "dist"
        if dist_dir.exists():
            files = list(dist_dir.rglob("*"))
            print(f"[OK] Build output: {len(files)} files in web/dist/")
        else:
            print("[ERROR] Build output directory not found.")
            sys.exit(1)

    except subprocess.CalledProcessError:
        print("[ERROR] Build Failed.")
        sys.exit(1)


if __name__ == "__main__":
    build_web()
