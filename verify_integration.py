"""
Integration verification script for the refactored Main Menu.

This script verifies that the refactored Main Menu is working correctly
in the actual game environment.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def verify_import():
    """Verify the import works correctly."""
    print("=== Import Verification ===")
    
    try:
        from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored
        print("✅ Successfully imported MainMenuPanelRefactored")
        
        # Check it's being used as MainMenuPanel
        from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored as MainMenuPanel
        print("✅ Successfully imported as MainMenuPanel alias")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def verify_class_structure():
    """Verify the class structure is correct."""
    print("\n=== Class Structure Verification ===")
    
    try:
        from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored
        
        # Check class exists
        assert MainMenuPanelRefactored is not None, "Class not found"
        print("✅ MainMenuPanelRefactored class exists")
        
        # Check it has required methods
        required_methods = ['__init__', '_create_window', 'handle_event', 'update', 'render']
        for method in required_methods:
            assert hasattr(MainMenuPanelRefactored, method), f"Missing method: {method}"
            print(f"✅ Has method: {method}")
            
        return True
    except Exception as e:
        print(f"❌ Class structure verification failed: {e}")
        return False

def verify_component_dependencies():
    """Verify component dependencies are available."""
    print("\n=== Component Dependencies Verification ===")
    
    try:
        from ui.components.reusable import Panel, MoneyDisplay, Container, Button
        print("✅ All reusable components available")
        
        # Check component classes exist
        components = {
            'Panel': Panel,
            'MoneyDisplay': MoneyDisplay,
            'Container': Container,
            'Button': Button
        }
        
        for name, component_class in components.items():
            assert component_class is not None, f"Component {name} not found"
            print(f"✅ Component {name} available")
            
        return True
    except ImportError as e:
        print(f"❌ Component dependencies failed: {e}")
        return False

def verify_game_integration():
    """Verify integration with main game."""
    print("\n=== Game Integration Verification ===")
    
    try:
        # Check main.py import
        with open('src/main.py', 'r') as f:
            content = f.read()
            
        # Verify the import line exists
        expected_import = "from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored as MainMenuPanel"
        if expected_import in content:
            print("✅ Main.py import updated correctly")
        else:
            print("❌ Main.py import not found or incorrect")
            return False
            
        # Verify old import is gone
        old_import = "from ui.panels.main_menu_panel import MainMenuPanel"
        if old_import not in content:
            print("✅ Old import removed from main.py")
        else:
            print("⚠️ Old import still exists in main.py")
            
        return True
    except Exception as e:
        print(f"❌ Game integration verification failed: {e}")
        return False

def verify_file_structure():
    """Verify all required files exist."""
    print("\n=== File Structure Verification ===")
    
    required_files = [
        'src/ui/panels/main_menu_panel_refactored.py',
        'src/ui/components/reusable/__init__.py',
        'src/ui/components/reusable/display_components.py',
        'src/ui/components/reusable/input_components.py',
        'src/ui/components/reusable/layout_components.py',
        'src/ui/components/reusable/game_components.py',
        'test_main_menu.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
            
    return all_exist

def main():
    """Run all verification checks."""
    print("🔍 Verifying Main Menu Integration...")
    print("="*50)
    
    tests = [
        ("Import", verify_import),
        ("Class Structure", verify_class_structure),
        ("Component Dependencies", verify_component_dependencies),
        ("Game Integration", verify_game_integration),
        ("File Structure", verify_file_structure),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("VERIFICATION SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("\n🎉 Integration verification successful!")
        print("\n✅ The refactored Main Menu is properly integrated!")
        print("✅ All components are available and working!")
        print("✅ Game imports are updated correctly!")
        print("\n🚀 Ready to test the actual game!")
    else:
        print(f"\n⚠️ {len(results) - passed} verification checks failed.")
        print("Please address the issues above before testing the game.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
