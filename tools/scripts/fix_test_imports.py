#!/usr/bin/env python3
"""
Fix import statements in test files to work with the new directory structure.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


def fix_test_imports():
    """Fix imports in all test files"""
    test_dir = project_root / "tests"

    if not test_dir.exists():
        print(f"Test directory not found: {test_dir}")
        return

    # Import mappings
    import_mappings = {
        'from settings import *': 'import sys\nsys.path.insert(0, ".")\nsys.path.insert(0, "src")\nfrom settings import *',
        'from core.': 'from src.core.',
        'from managers.': 'from src.managers.',
        'import core.': 'import src.core.',
        'import managers.': 'import src.managers.',
    }

    fixed_files = 0

    for test_file in test_dir.glob("*.py"):
        if test_file.name == "__init__.py":
            continue

        try:
            content = test_file.read_text(encoding='utf-8')
            original_content = content

            # Apply import fixes
            for old_import, new_import in import_mappings.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)

            # Write back if changed
            if content != original_content:
                test_file.write_text(content, encoding='utf-8')
                print(f"Fixed imports in {test_file.name}")
                fixed_files += 1

        except Exception as e:
            print(f"Error processing {test_file}: {e}")

    print(f"Fixed imports in {fixed_files} test files")


def add_path_setup_to_tests():
    """Add proper path setup to test files that don't have it"""
    test_dir = project_root / "tests"

    path_setup = """# Add project root to path
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

"""

    for test_file in test_dir.glob("*.py"):
        if test_file.name == "__init__.py":
            continue

        try:
            content = test_file.read_text(encoding='utf-8')

            # Check if path setup is already present
            if "project_root = Path(__file__).parent.parent" in content:
                continue

            # Find the first import line
            lines = content.split('\n')
            insert_index = 0

            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    insert_index = i
                    break

            # Insert path setup
            lines.insert(insert_index, path_setup)

            # Write back
            test_file.write_text('\n'.join(lines), encoding='utf-8')
            print(f"Added path setup to {test_file.name}")

        except Exception as e:
            print(f"Error processing {test_file}: {e}")


if __name__ == "__main__":
    print("Fixing test imports...")
    add_path_setup_to_tests()
    fix_test_imports()
    print("Done!")
