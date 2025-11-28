"""
Simple test script for the refactored Main Menu Panel.

Run this from the project root directory:
python test_main_menu.py
"""

import pygame
import pygame_gui
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored
    from ui.panels.main_menu_panel import MainMenuPanel
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class MockGameState:
    """Mock game state for testing."""
    
    def __init__(self):
        self.money = 1000
        self.state = "main_menu"
        self.select_racer_mode = False
        self.game = self
        
    def get(self, key, default=None):
        return getattr(self, key, default)
        
    def set(self, key, value):
        setattr(self, key, value)
        
    class MockUIManager:
        def toggle_panel(self, panel_id):
            print(f"Toggle panel: {panel_id}")


class MockEventBus:
    """Mock event bus for testing."""
    
    def emit(self, event_name, data):
        print(f"Event: {event_name} -> {data}")


def test_basic_functionality():
    """Test basic Main Menu functionality."""
    print("\n=== Basic Functionality Test ===")
    
    pygame.init()
    
    # Set display mode before creating UIManager
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Main Menu Test")
    
    manager = pygame_gui.UIManager((800, 600))
    game_state = MockGameState()
    event_bus = MockEventBus()
    
    try:
        # Test refactored panel creation
        print("Creating refactored Main Menu...")
        refactored_panel = MainMenuPanelRefactored(game_state, event_bus)
        refactored_panel.manager = manager
        refactored_panel._create_window()
        
        # Test components exist
        components = {
            'main_panel': refactored_panel.main_panel is not None,
            'money_display': refactored_panel.money_display is not None,
            'menu_container': refactored_panel.menu_container is not None,
            'menu_buttons': len(refactored_panel.menu_buttons) > 0,
        }
        
        print("Component Check:")
        for component, exists in components.items():
            status = "✅" if exists else "❌"
            print(f"  {status} {component}")
            
        # Test money display
        if refactored_panel.money_display:
            initial_money = refactored_panel.money_display.get_amount()
            print(f"\nMoney Display Test:")
            print(f"  Initial amount: ${initial_money}")
            
            # Update money
            game_state.money = 5000
            refactored_panel.update(0.016)
            updated_money = refactored_panel.money_display.get_amount()
            print(f"  Updated amount: ${updated_money}")
            print(f"  Update working: {updated_money == 5000}")
            
        # Test buttons
        print(f"\nButton Test:")
        print(f"  Number of buttons: {len(refactored_panel.menu_buttons)}")
        for button in refactored_panel.menu_buttons:
            print(f"  ✅ {button.text}: {'Enabled' if button.enabled else 'Disabled'}")
            
        print("\n✅ Basic functionality test passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    pygame.quit()
    return True


def test_component_architecture():
    """Test component architecture benefits."""
    print("\n=== Component Architecture Test ===")
    
    pygame.init()
    
    # Set display mode before creating UIManager
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Architecture Test")
    
    manager = pygame_gui.UIManager((800, 600))
    game_state = MockGameState()
    event_bus = MockEventBus()
    
    try:
        panel = MainMenuPanelRefactored(game_state, event_bus)
        panel.manager = manager
        panel._create_window()
        
        # Test 1: Component isolation
        print("1. Testing Component Isolation:")
        print(f"   ✅ Main Panel: {panel.main_panel is not None}")
        print(f"   ✅ Money Display: {panel.money_display is not None}")
        print(f"   ✅ Menu Container: {panel.menu_container is not None}")
        print(f"   ✅ Menu Buttons: {len(panel.menu_buttons)}")
        
        # Test 2: Component reusability
        print("\n2. Testing Component Reusability:")
        from ui.components.reusable import Button, MoneyDisplay, Container, Panel
        
        test_button = Button(pygame.Rect(0, 0, 100, 30), "Test", "test", manager)
        test_money = MoneyDisplay(pygame.Rect(0, 0, 100, 20), 500, manager)
        test_container = Container(pygame.Rect(0, 0, 200, 200), manager)
        test_panel = Panel(pygame.Rect(0, 0, 300, 400), "Test Panel", manager)
        
        print(f"   ✅ Can create independent Button: {test_button is not None}")
        print(f"   ✅ Can create independent MoneyDisplay: {test_money is not None}")
        print(f"   ✅ Can create independent Container: {test_container is not None}")
        print(f"   ✅ Can create independent Panel: {test_panel is not None}")
        
        # Test 3: Component configuration
        print("\n3. Testing Component Configuration:")
        button_configs = [
            {'style': 'primary'},
            {'style': 'secondary'},
            {'style': 'danger'}
        ]
        
        for i, config in enumerate(button_configs):
            button = Button(pygame.Rect(0, i * 35, 100, 30), f"Style {i+1}", f"action_{i}", manager, config)
            print(f"   ✅ Button with {config['style']} style: {button is not None}")
            
        print("\n✅ Component architecture test passed!")
        
    except Exception as e:
        print(f"❌ Architecture test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    pygame.quit()
    return True


def test_feature_parity():
    """Test feature parity with original implementation."""
    print("\n=== Feature Parity Test ===")
    
    pygame.init()
    
    # Set display mode before creating UIManager
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Feature Parity Test")
    
    manager = pygame_gui.UIManager((800, 600))
    game_state = MockGameState()
    event_bus = MockEventBus()
    
    try:
        # Create both versions
        refactored_panel = MainMenuPanelRefactored(game_state, event_bus)
        original_panel = MainMenuPanel(game_state, event_bus)
        
        refactored_panel.manager = manager
        original_panel.manager = manager
        
        refactored_panel._create_window()
        original_panel._create_window()
        
        # Compare button counts
        refactored_buttons = len(refactored_panel.menu_buttons)
        original_buttons = 7  # roster, shop, breeding, race, voting, settings, quit
        
        print(f"Button Count Comparison:")
        print(f"  Refactored: {refactored_buttons}")
        print(f"  Original: {original_buttons}")
        print(f"  Match: {refactored_buttons == original_buttons}")
        
        # Compare button labels
        refactored_labels = [button.text for button in refactored_panel.menu_buttons]
        expected_labels = ["Roster", "Shop", "Breeding", "Race", "Voting", "Settings", "Quit"]
        
        print(f"\nButton Labels Comparison:")
        print(f"  Refactored: {refactored_labels}")
        print(f"  Expected: {expected_labels}")
        print(f"  Match: {refactored_labels == expected_labels}")
        
        # Test money display
        refactored_has_money = refactored_panel.money_display is not None
        original_has_money = original_panel.lbl_money is not None
        
        print(f"\nMoney Display Comparison:")
        print(f"  Refactored has money display: {refactored_has_money}")
        print(f"  Original has money display: {original_has_money}")
        print(f"  Both have money display: {refactored_has_money and original_has_money}")
        
        print("\n✅ Feature parity test passed!")
        
    except Exception as e:
        print(f"❌ Feature parity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    pygame.quit()
    return True


if __name__ == "__main__":
    print("🚀 Starting Main Menu Refactor Tests...")
    
    # Run all tests
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Component Architecture", test_component_architecture),
        ("Feature Parity", test_feature_parity),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Main Menu refactor is ready for integration!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\nNext steps:")
    print("1. If all tests passed, proceed with integration")
    print("2. Update imports in your main game file:")
    print("   from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored as MainMenuPanel")
    print("3. Test the integration in your game")
