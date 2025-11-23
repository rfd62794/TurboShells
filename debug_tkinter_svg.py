#!/usr/bin/env python3

import tkinter as tk
from tkinter import Canvas
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from core.visual_genetics import VisualGenetics
from core.turtle_svg_generator import TurtleSVGGenerator
from core.svg_tkinter_renderer import get_svg_renderer

def main():
    """Debug Tkinter SVG rendering"""
    print("=== Debug Tkinter SVG Rendering ===")
    
    # Initialize systems
    vg = VisualGenetics()
    generator = TurtleSVGGenerator()
    renderer = get_svg_renderer()
    
    # Create test genetics with very visible colors
    genetics = vg.generate_random_genetics()
    genetics['shell_base_color'] = (255, 0, 0)  # Bright red
    genetics['body_base_color'] = (0, 255, 0)  # Bright green
    
    print(f"Test genetics:")
    print(f"  Shell color: RGB{genetics['shell_base_color']}")
    print(f"  Body color: RGB{genetics['body_base_color']}")
    
    # Generate SVG
    svg_drawing = generator.generate_turtle_svg(genetics, 200)
    svg_string = svg_drawing.as_svg()
    
    print(f"SVG generated: {len(svg_string)} characters")
    
    # Test conversion
    print("Testing SVG to PhotoImage conversion...")
    photo_image = renderer.svg_to_photoimage(svg_string, 200)
    
    if photo_image:
        print(f"✅ PhotoImage created: {photo_image.width()}x{photo_image.height()}")
        
        # Create simple window to display
        root = tk.Tk()
        root.title("SVG Debug Test")
        
        canvas = Canvas(root, width=400, height=400, bg='white')
        canvas.pack()
        
        # Center the image
        x = (400 - photo_image.width()) // 2
        y = (400 - photo_image.height()) // 2
        canvas.create_image(x, y, anchor=tk.NW, image=photo_image)
        
        # Keep reference
        root.current_photo = photo_image
        
        print("Displaying image in window...")
        print("If you see a blank canvas, the SVG conversion failed")
        print("If you see a turtle, the conversion worked!")
        
        root.mainloop()
        
    else:
        print("❌ Failed to create PhotoImage")
        
        # Try fallback
        print("Trying fallback image...")
        fallback = renderer.create_fallback_photoimage(200)
        if fallback:
            print(f"✅ Fallback created: {fallback.width()}x{fallback.height()}")
            
            root = tk.Tk()
            root.title("Fallback Test")
            
            canvas = Canvas(root, width=400, height=400, bg='white')
            canvas.pack()
            
            x = (400 - fallback.width()) // 2
            y = (400 - fallback.height()) // 2
            canvas.create_image(x, y, anchor=tk.NW, image=fallback)
            
            root.current_fallback = fallback
            root.mainloop()
        else:
            print("❌ Even fallback failed")

if __name__ == '__main__':
    main()
