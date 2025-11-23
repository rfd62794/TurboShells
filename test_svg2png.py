#!/usr/bin/env python3

import svg2png
import tempfile
import os

def main():
    """Test svg2png directly"""
    print('Testing svg2png with simple SVG...')
    
    # Simple SVG content
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
<circle cx="100" cy="100" r="50" fill="red" />
</svg>'''
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
        f.write(svg_content)
        temp_svg = f.name
    
    print(f'Saved SVG to: {temp_svg}')
    
    # Convert
    try:
        svg2png.svg2png(temp_svg)  # Only takes input file
        temp_png = temp_svg.replace('.svg', '.png')
        print(f'Converted to: {temp_png}')
        
        if os.path.exists(temp_png):
            print('PNG file created successfully')
            
            # Check file size
            file_size = os.path.getsize(temp_png)
            print(f'File size: {file_size} bytes')
            
            if file_size > 0:
                print('PNG file has content - conversion works!')
            else:
                print('PNG file is empty')
            
            os.unlink(temp_png)
        else:
            print('PNG file not created')
            
    except Exception as e:
        print(f'Error: {e}')
        print('Note: svg2png requires Inkscape to be installed and in PATH')
    
    # Cleanup
    os.unlink(temp_svg)

if __name__ == '__main__':
    main()
