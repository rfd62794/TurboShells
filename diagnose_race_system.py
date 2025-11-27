#!/usr/bin/env python3
"""
Race System Diagnostic Script
Tests the race system initialization and rendering pipeline
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_race_system():
    """Test the race system components"""
    print("=== Race System Diagnostic ===")
    
    try:
        # Import required modules
        print("1. Importing modules...")
        from game.entities import Turtle
        from managers.race_manager import RaceManager
        from game.game_state import generate_balanced_opponent
        from game.race_track import generate_track
        print("   ✓ All modules imported successfully")
        
        # Create a mock game state
        print("2. Creating mock game state...")
        class MockGameState:
            def __init__(self):
                self.roster = [
                    Turtle("TestTurtle", speed=5, energy=100, recovery=5, swim=5, climb=5),
                    None,
                    None
                ]
                self.active_racer_index = 0
                self.money = 200
                self.current_bet = 0
                self.race_results = []
                self.race_speed_multiplier = 1
                
            def auto_save(self, trigger):
                print(f"   Auto-save triggered: {trigger}")
        
        game_state = MockGameState()
        print("   ✓ Mock game state created")
        
        # Test race manager
        print("3. Testing RaceManager...")
        race_manager = RaceManager(game_state)
        print("   ✓ RaceManager created")
        
        # Test race start
        print("4. Testing race start...")
        race_manager.start_race()
        print(f"   ✓ Race started with {len(race_manager.race_roster)} turtles")
        
        # Test track generation
        print("5. Testing track generation...")
        track = generate_track(100)
        print(f"   ✓ Track generated with {len(track)} segments")
        
        # Test opponent generation
        print("6. Testing opponent generation...")
        player_turtle = game_state.roster[0]
        opponent = generate_balanced_opponent(player_turtle)
        print(f"   ✓ Opponent generated: {opponent.name}")
        
        # Test physics update
        print("7. Testing physics update...")
        for turtle in race_manager.race_roster:
            terrain = "grass"  # Simple test
            move_distance = turtle.update_physics(terrain)
            print(f"   ✓ {turtle.name} moved {move_distance:.2f} units")
        
        print("\n=== Race System Test PASSED ===")
        return True
        
    except Exception as e:
        print(f"\n=== Race System Test FAILED ===")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rendering_pipeline():
    """Test the rendering pipeline"""
    print("\n=== Rendering Pipeline Diagnostic ===")
    
    try:
        import pygame
        pygame.init()
        
        # Create a minimal test surface
        screen = pygame.Surface((800, 600))
        font = pygame.font.Font(None, 24)
        
        print("1. Pygame initialized")
        
        # Test race view import
        from ui.views.race_view import draw_race, draw_turtle_sprite
        print("   ✓ Race view functions imported")
        
        # Create mock game state with race manager
        class MockGameState:
            def __init__(self):
                from managers.race_manager import RaceManager
                self.race_manager = RaceManager(self)
                self.roster = [
                    Turtle("TestTurtle", speed=5, energy=100, recovery=5, swim=5, climb=5)
                ]
                self.active_racer_index = 0
                self.money = 200
                self.current_bet = 0
                self.race_results = []
                self.race_speed_multiplier = 1
                
            def auto_save(self, trigger):
                pass
        
        game_state = MockGameState()
        game_state.race_manager.start_race()
        
        print("2. Mock game state with race created")
        
        # Test drawing
        print("3. Testing race drawing...")
        draw_race(screen, font, game_state)
        print("   ✓ Race drawing completed")
        
        pygame.quit()
        print("\n=== Rendering Pipeline Test PASSED ===")
        return True
        
    except Exception as e:
        print(f"\n=== Rendering Pipeline Test FAILED ===")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("TurboShells Race System Diagnostic")
    print("=" * 50)
    
    # Test race system
    race_ok = test_race_system()
    
    # Test rendering pipeline
    render_ok = test_rendering_pipeline()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Race System: {'PASS' if race_ok else 'FAIL'}")
    print(f"Rendering Pipeline: {'PASS' if render_ok else 'FAIL'}")
    
    if race_ok and render_ok:
        print("\nAll tests passed! The race system should work correctly.")
        sys.exit(0)
    else:
        print("\nSome tests failed. Check the error messages above.")
        sys.exit(1)
