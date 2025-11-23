#!/usr/bin/env python3

import tkinter as tk
from tkinter import Canvas
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from core.visual_genetics import VisualGenetics
from core.generic_turtle_svg import create_generic_turtle_svg, create_turtle_variations
from core.svg_tkinter_renderer_fixed import get_svg_renderer

def main():
    """Test generic turtle SVG"""
    print("=== Testing Generic Turtle SVG ===")
    
    # Initialize systems
    vg = VisualGenetics()
    renderer = get_svg_renderer()
    
    # Create test genetics
    genetics = vg.generate_random_genetics()
    genetics['shell_base_color'] = (255, 100, 100)  # Red shell
    genetics['shell_pattern_type'] = 'spots'
    
    print(f"Test genetics:")
    print(f"  Shell color: RGB{genetics['shell_base_color']}")
    print(f"  Shell pattern: {genetics['shell_pattern_type']}")
    
    # Generate generic turtle SVG
    svg_content = create_generic_turtle_svg(genetics)
    print(f"Generated SVG: {len(svg_content)} characters")
    
    # Test conversion
    result = renderer.svg_to_photoimage(svg_content, 200)
    
    if result:
        if isinstance(result, str):
            print(f"Image file created: {result}")
            
            # Create window to display
            root = tk.Tk()
            root.title("Generic Turtle Test")
            
            canvas = Canvas(root, width=400, height=400, bg='white')
            canvas.pack()
            
            # Load the file
            from PIL import Image, ImageTk
            pil_image = Image.open(result)
            display_photo = ImageTk.PhotoImage(pil_image)
            
            # Center the image
            x = (400 - display_photo.width()) // 2
            y = (400 - display_photo.height()) // 2
            canvas.create_image(x, y, anchor=tk.NW, image=display_photo)
            
            # Keep reference
            root.display_photo = display_photo
            
            print("Displaying generic turtle...")
            root.mainloop()
        else:
            print(f"PhotoImage created: {result.width()}x{result.height()}")
            
            # Create window to display
            root = tk.Tk()
            root.title("Generic Turtle Test")
            
            canvas = Canvas(root, width=400, height=400, bg='white')
            canvas.pack()
            
            # Center the image
            x = (400 - result.width()) // 2
            y = (400 - result.height()) // 2
            canvas.create_image(x, y, anchor=tk.NW, image=result)
            
            # Keep reference
            root.current_photo = result
            
            print("Displaying generic turtle...")
            root.mainloop()
    else:
        print("Failed to create image")

def test_variations():
    """Test multiple turtle variations"""
    print("\n=== Testing Turtle Variations ===")
    
    vg = VisualGenetics()
    renderer = get_svg_renderer()
    
    # Create base genetics
    base_genetics = vg.generate_random_genetics()
    base_genetics['shell_base_color'] = (100, 200, 100)  # Green shell
    
    # Create variations
    turtles = create_turtle_variations(base_genetics, 5)
    
    print(f"Created {len(turtles)} variations:")
    for turtle in turtles:
        genetics = turtle['genetics']
        print(f"  {turtle['name']}: Shell RGB{genetics['shell_base_color']}, Pattern: {genetics['shell_pattern_type']}")
    
    # Create window to display all variations
    root = tk.Tk()
    root.title("Turtle Variations")
    root.geometry("1200x300")
    
    canvas = Canvas(root, width=1200, height=300, bg='white')
    canvas.pack()
    
    # Display each turtle
    for i, turtle in enumerate(turtles):
        result = renderer.svg_to_photoimage(turtle['svg'], 200)
        
        if result:
            if isinstance(result, str):
                from PIL import Image, ImageTk
                pil_image = Image.open(result)
                photo = ImageTk.PhotoImage(pil_image)
            else:
                photo = result
            
            # Position turtles side by side
            x = 50 + i * 220
            y = 50
            
            canvas.create_image(x, y, anchor=tk.NW, image=photo)
            
            # Add label
            canvas.create_text(x + 100, y + 220, text=turtle['name'], font=('Arial', 10))
            
            # Keep reference
            setattr(root, f'photo_{i}', photo)
    
    print("Displaying variations...")
    root.mainloop()

if __name__ == '__main__':
    main()
    test_variations()
