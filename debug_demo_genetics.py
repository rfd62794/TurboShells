#!/usr/bin/env python3

from core.visual_genetics import VisualGenetics
from core.voting_system import VotingSystem

def main():
    """Debug the genetics being generated in the demo"""
    print("=== Debug Demo Genetics ===")
    
    # Initialize systems
    voting_system = VotingSystem()
    
    # Generate daily designs
    designs = voting_system.generate_daily_designs()
    
    print(f"Generated {len(designs)} designs")
    
    for i, design in enumerate(designs):
        print(f"\nDesign {i+1}:")
        genetics = design.genetics
        
        # Show key visual traits
        print(f"  Shell color: RGB{genetics['shell_base_color']}")
        print(f"  Body color: RGB{genetics['body_base_color']}")
        print(f"  Shell pattern: {genetics['shell_pattern_type']}")
        print(f"  Body pattern: {genetics['body_pattern_type']}")
        print(f"  Eye color: RGB{genetics['eye_color']}")
        print(f"  Head color: RGB{genetics['head_color']}")
        print(f"  Leg color: RGB{genetics['leg_color']}")
        
        # Check if colors are very similar
        shell_rgb = genetics['shell_base_color']
        body_rgb = genetics['body_base_color']
        
        shell_variance = max(shell_rgb) - min(shell_rgb)
        body_variance = max(body_rgb) - min(body_rgb)
        
        print(f"  Shell color variance: {shell_variance}")
        print(f"  Body color variance: {body_variance}")
        
        if shell_variance < 30 and body_variance < 30:
            print("  -> Colors are very similar (might look the same)")

if __name__ == '__main__':
    main()
