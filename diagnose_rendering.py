"""Diagnostic script to test turtle rendering pipeline."""
import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from game.entities import Turtle
from core.rendering.pygame_turtle_renderer import render_turtle_pygame

def test_turtle_rendering():
    """Test the complete turtle rendering pipeline."""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Turtle Rendering Diagnostic")
    
    print("=== Turtle Rendering Diagnostic ===\n")
    
    # Test 1: Create turtle with default genetics
    print("Test 1: Create turtle with default parameters")
    turtle1 = Turtle("TestDefault", speed=10, energy=100, recovery=10, swim=10, climb=10)
    print(f"  Turtle created: {turtle1.name}")
    print(f"  Has genetics_system: {turtle1.genetics_system is not None}")
    print(f"  visual_genetics keys: {list(turtle1.visual_genetics.keys())[:5] if turtle1.visual_genetics else 'EMPTY'}")
    
    # Test 2: Try rendering
    print("\nTest 2: Attempt to render turtle")
    try:
        surface = render_turtle_pygame(turtle1, size=200)
        print(f"  ✓ Rendering succeeded!")
        print(f"  Surface type: {type(surface)}")
        print(f"  Surface size: {surface.get_size() if hasattr(surface, 'get_size') else 'N/A'}")
        
        # Display it
        screen.fill((50, 50, 50))
        screen.blit(surface, (50, 50))
        
        # Add label
        font = pygame.font.Font(None, 24)
        text = font.render(f"Turtle: {turtle1.name}", True, (255, 255, 255))
        screen.blit(text, (50, 270))
        
        pygame.display.flip()
        print("\n  Visual check: Look at the window - do you see a turtle?")
        print("  Press any key to continue...")
        
        # Wait for key
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    waiting = False
                    
    except Exception as e:
        print(f"  ✗ Rendering FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Create turtle with provided genetics
    print("\nTest 3: Create turtle with specific genetics")
    genetics = {
        'shell_base_color': (34, 139, 34),
        'head_color': (46, 125, 50),
        'pattern_color': (20, 83, 20),
        'eye_color': (0, 0, 0),
        'shell_pattern_type': 'hex'
    }
    turtle2 = Turtle("TestGenetics", speed=10, energy=100, recovery=10, swim=10, climb=10, genetics=genetics)
    print(f"  Turtle created: {turtle2.name}")
    print(f"  visual_genetics: {turtle2.visual_genetics}")
    
    try:
        surface2 = render_turtle_pygame(turtle2, size=200)
        print(f"  ✓ Rendering succeeded!")
        
        screen.fill((50, 50, 50))
        screen.blit(surface2, (300, 50))
        
        text2 = font.render(f"Turtle: {turtle2.name}", True, (255, 255, 255))
        screen.blit(text2, (300, 270))
        
        pygame.display.flip()
        print("\n  Visual check: Look at the window - do you see a turtle?")
        print("  Press any key to exit...")
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    waiting = False
                    
    except Exception as e:
        print(f"  ✗ Rendering FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Diagnostic Complete ===")
    pygame.quit()

if __name__ == "__main__":
    test_turtle_rendering()
