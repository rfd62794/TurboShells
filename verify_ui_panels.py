import pygame
import os
import sys
import time

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), "src"))

from main import TurboShellsGame
from settings import *

def verify_ui_panels():
    print("Initializing Game for UI Verification...")
    
    # Initialize game
    game = TurboShellsGame()
    
    # Create output directory
    output_dir = "ui_verification"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Helper to run a few frames and capture
    def capture_state(state_name, setup_func=None):
        print(f"Testing state: {state_name}")
        
        # Setup specific state data if needed
        if setup_func:
            setup_func(game)
            
        # Set state
        game.state = state_name
        
        # Run a few frames to let UI settle/animate
        for _ in range(10):
            game.handle_input()
            game.update()
            game.draw()
            
        # Capture
        filename = os.path.join(output_dir, f"screenshot_{state_name}.png")
        pygame.image.save(game.screen, filename)
        print(f"Saved {filename}")

    # 1. Main Menu
    capture_state(STATE_MENU)
    
    # 2. Roster
    def setup_roster(g):
        # Ensure we have some turtles
        from game.entities import Turtle
        if not g.roster[0]:
            g.roster[0] = Turtle("TestTurtle", speed=10, energy=100, recovery=10, swim=10, climb=10)
        g.money = 500
        
    capture_state(STATE_ROSTER, setup_roster)
    
    # 3. Shop
    def setup_shop(g):
        g.shop_manager.refresh_stock(free=True)
        
    capture_state(STATE_SHOP, setup_shop)
    
    # 4. Race HUD
    def setup_race(g):
        # Setup a race
        g.active_racer_index = 0
        g.race_manager.start_race()
        # Force some progress
        if g.race_manager.race_roster:
            g.race_manager.race_roster[0].race_distance = 500
            
    capture_state(STATE_RACE, setup_race)
    
    # 5. Race Result
    def setup_race_result(g):
        # Fake some results
        from game.entities import Turtle
        t1 = Turtle("Winner", speed=20, energy=100, recovery=10, swim=10, climb=10)
        t1.age = 5
        t2 = Turtle("RunnerUp", speed=15, energy=100, recovery=10, swim=10, climb=10)
        t2.age = 4
        g.race_results = [t1, t2]
        g.active_racer_index = 0
        
    capture_state(STATE_RACE_RESULT, setup_race_result)
    
    print("Verification complete.")
    pygame.quit()

if __name__ == "__main__":
    try:
        verify_ui_panels()
    except Exception as e:
        print(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()
