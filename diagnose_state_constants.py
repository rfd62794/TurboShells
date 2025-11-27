#!/usr/bin/env python3
"""
State Constants Diagnostic Script
Checks for state constant mismatches across the codebase
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def get_official_constants():
    """Get the official state constants from settings.py"""
    try:
        from settings import STATE_MENU, STATE_ROSTER, STATE_RACE, STATE_RACE_RESULT
        from settings import STATE_SHOP, STATE_BREEDING, STATE_PROFILE, STATE_VOTING, STATE_SETTINGS
        
        return {
            'STATE_MENU': STATE_MENU,
            'STATE_ROSTER': STATE_ROSTER,
            'STATE_RACE': STATE_RACE,
            'STATE_RACE_RESULT': STATE_RACE_RESULT,
            'STATE_SHOP': STATE_SHOP,
            'STATE_BREEDING': STATE_BREEDING,
            'STATE_PROFILE': STATE_PROFILE,
            'STATE_VOTING': STATE_VOTING,
            'STATE_SETTINGS': STATE_SETTINGS
        }
    except ImportError as e:
        print(f"Error importing settings: {e}")
        return {}

def find_hardcoded_states():
    """Find hardcoded state strings in Python files"""
    hardcoded_states = []
    
    # Common hardcoded patterns to look for
    patterns = [
        '= "menu"', '= "roster"', '= "race"', '= "race_result"',
        '= "shop"', '= "breeding"', '= "profile"', '= "voting"', '= "settings"',
        "= 'menu'", "= 'roster'", "= 'race'", "= 'race_result'",
        "= 'shop'", "= 'breeding'", "= 'profile'", "= 'voting'", "= 'settings'"
    ]
    
    src_dir = Path(__file__).parent / "src"
    
    for py_file in src_dir.rglob("*.py"):
        if py_file.name == 'settings.py':
            continue  # Skip settings.py as it defines the constants
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                for pattern in patterns:
                    if pattern in line:
                        # Extract the state value more carefully
                        try:
                            # Find the quoted part
                            import re
                            match = re.search(r'["\']([^"\']+)["\']', line)
                            if match:
                                state_value = match.group(1)
                                hardcoded_states.append({
                                    'file': str(py_file.relative_to(src_dir)),
                                    'line': line_num,
                                    'content': line.strip(),
                                    'state_value': state_value
                                })
                        except Exception:
                            # Fallback: just report the line
                            hardcoded_states.append({
                                'file': str(py_file.relative_to(src_dir)),
                                'line': line_num,
                                'content': line.strip(),
                                'state_value': 'PARSE_ERROR'
                            })
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return hardcoded_states

def check_state_mismatches():
    """Check for state constant mismatches"""
    print("=== State Constants Diagnostic ===")
    
    # Get official constants
    official_constants = get_official_constants()
    print(f"Official constants found: {len(official_constants)}")
    for name, value in official_constants.items():
        print(f"  {name} = '{value}'")
    
    print()
    
    # Find hardcoded states
    hardcoded_states = find_hardcoded_states()
    print(f"Hardcoded state strings found: {len(hardcoded_states)}")
    
    mismatches = []
    for item in hardcoded_states:
        state_value = item['state_value']
        
        # Check if this hardcoded value matches any official constant
        matching_constants = [name for name, value in official_constants.items() if value == state_value]
        
        if not matching_constants:
            # This is a mismatch - hardcoded value doesn't match any official constant
            mismatches.append(item)
            print(f"❌ MISMATCH: {item['file']}:{item['line']}")
            print(f"   Code: {item['content']}")
            print(f"   Hardcoded value: '{state_value}' doesn't match any official constant")
            print()
        else:
            print(f"✅ OK: {item['file']}:{item['line']}")
            print(f"   Code: {item['content']}")
            print(f"   Matches: {', '.join(matching_constants)}")
            print()
    
    return mismatches

def check_main_py_fallback():
    """Check main.py fallback constants"""
    print("\n=== main.py Fallback Constants Check ===")
    
    main_py_path = Path(__file__).parent / "src" / "main.py"
    try:
        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if main.py has fallback constants defined
        if 'STATE_MENU = "menu"' in content:
            print("⚠️  WARNING: main.py has lowercase fallback constants")
            print("    These will be used if settings.py import fails")
            print("    This could cause state mismatches")
            
            # Show the fallback section
            lines = content.split('\n')
            in_fallback_section = False
            for line_num, line in enumerate(lines, 1):
                if 'Define basic settings if import fails' in line:
                    in_fallback_section = True
                elif in_fallback_section and 'AUTO_SAVE_INTERVAL' in line:
                    break
                elif in_fallback_section and 'STATE_' in line:
                    print(f"    Line {line_num}: {line.strip()}")
        else:
            print("✅ main.py doesn't have problematic fallback constants")
            
    except Exception as e:
        print(f"Error checking main.py: {e}")

def main():
    """Main diagnostic function"""
    print("TurboShells State Constants Diagnostic")
    print("=" * 50)
    
    # Check for mismatches
    mismatches = check_state_mismatches()
    
    # Check main.py fallbacks
    check_main_py_fallback()
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    
    if mismatches:
        print(f"❌ Found {len(mismatches)} state constant mismatches")
        print("\nRecommended fixes:")
        for item in mismatches:
            state_value = item['state_value']
            # Find the correct constant name
            constant_map = {
                'menu': 'STATE_MENU',
                'roster': 'STATE_ROSTER', 
                'race': 'STATE_RACE',
                'race_result': 'STATE_RACE_RESULT',
                'shop': 'STATE_SHOP',
                'breeding': 'STATE_BREEDING',
                'profile': 'STATE_PROFILE',
                'voting': 'STATE_VOTING',
                'settings': 'STATE_SETTINGS'
            }
            correct_constant = constant_map.get(state_value.lower(), 'UNKNOWN')
            print(f"  {item['file']}:{item['line']}")
            print(f"    Replace '{state_value}' with {correct_constant}")
        return False
    else:
        print("✅ No state constant mismatches found!")
        print("All hardcoded state strings match official constants.")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
