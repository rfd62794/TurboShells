#!/usr/bin/env python3

import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageDraw, ImageTk

def main():
    """Debug PIL drawing"""
    print("=== Debug PIL Drawing ===")
    
    # Create PIL image with turtle drawing
    size = 200
    pil_image = Image.new('RGBA', (size, size), (240, 248, 255, 255))
    
    # Draw turtle using PIL
    draw = ImageDraw.Draw(pil_image)
    
    center_x = size // 2
    center_y = size // 2
    scale = size / 200.0
    
    print(f"Drawing turtle on {size}x{size} image")
    print(f"Center: ({center_x}, {center_y})")
    print(f"Scale: {scale}")
    
    # Shell
    shell_width = int(80 * scale)
    shell_height = int(60 * scale)
    shell_bbox = [
        center_x - shell_width//2, center_y - shell_height//2,
        center_x + shell_width//2, center_y + shell_height//2
    ]
    print(f"Shell bbox: {shell_bbox}")
    draw.ellipse(shell_bbox, fill=(34, 139, 34), outline=(0, 100, 0))
    
    # Head
    head_radius = int(20 * scale)
    head_bbox = [
        center_x - head_radius, center_y - int(40 * scale) - head_radius,
        center_x + head_radius, center_y - int(40 * scale) + head_radius
    ]
    print(f"Head bbox: {head_bbox}")
    draw.ellipse(head_bbox, fill=(139, 90, 43), outline=(100, 60, 20))
    
    # Eyes
    eye_size = max(2, int(3 * scale))
    print(f"Eye size: {eye_size}")
    
    left_eye_bbox = [
        center_x - int(8 * scale) - eye_size, center_y - int(40 * scale) - eye_size,
        center_x - int(8 * scale) + eye_size, center_y - int(40 * scale) + eye_size
    ]
    print(f"Left eye bbox: {left_eye_bbox}")
    draw.ellipse(left_eye_bbox, fill=(0, 0, 0))
    
    right_eye_bbox = [
        center_x + int(8 * scale) - eye_size, center_y - int(40 * scale) - eye_size,
        center_x + int(8 * scale) + eye_size, center_y - int(40 * scale) + eye_size
    ]
    print(f"Right eye bbox: {right_eye_bbox}")
    draw.ellipse(right_eye_bbox, fill=(0, 0, 0))
    
    # Legs
    leg_width = int(8 * scale)
    leg_length = int(30 * scale)
    leg_positions = [
        (center_x - int(60 * scale), center_y + int(20 * scale)),
        (center_x + int(60 * scale), center_y + int(20 * scale)),
        (center_x - int(40 * scale), center_y + int(40 * scale)),
        (center_x + int(40 * scale), center_y + int(40 * scale))
    ]
    print(f"Leg positions: {leg_positions}")
    print(f"Leg width: {leg_width}, length: {leg_length}")
    
    for i, (leg_x, leg_y) in enumerate(leg_positions):
        leg_bbox = [
            leg_x - leg_width//2, leg_y,
            leg_x + leg_width//2, leg_y + leg_length
        ]
        print(f"Leg {i+1} bbox: {leg_bbox}")
        draw.rectangle(leg_bbox, fill=(101, 67, 33))
    
    # Check pixel data
    pixels = list(pil_image.getdata())
    unique_colors = set(pixels)
    print(f"Total unique colors: {len(unique_colors)}")
    
    # Save to check visually
    pil_image.save("debug_turtle.png")
    print("Saved debug_turtle.png")
    
    # Create window to display
    root = tk.Tk()
    root.title("PIL Drawing Debug")
    
    canvas = Canvas(root, width=400, height=400, bg='white')
    canvas.pack()
    
    # Convert to PhotoImage
    photo_image = ImageTk.PhotoImage(pil_image)
    
    # Center the image
    x = (400 - photo_image.width()) // 2
    y = (400 - photo_image.height()) // 2
    canvas.create_image(x, y, anchor=tk.NW, image=photo_image)
    
    # Keep reference
    root.current_photo = photo_image
    
    print("Displaying image...")
    root.mainloop()

if __name__ == '__main__':
    main()
