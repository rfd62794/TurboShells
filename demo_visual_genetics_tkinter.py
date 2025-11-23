#!/usr/bin/env python3

"""
Tkinter-based Visual Genetics Demo for TurboShells
Uses direct SVG rendering in GUI toolkit
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from core.visual_genetics import VisualGenetics
from core.genetic_svg_mapper import GeneticToSVGMapper
from core.turtle_svg_generator import TurtleSVGGenerator
from core.svg_tkinter_renderer import get_svg_renderer
from core.voting_system import VotingSystem
from core.genetic_pool_manager import GeneticPoolManager


class VisualGeneticsDemo:
    """Tkinter-based visual genetics demonstration"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TurboShells Visual Genetics System - Tkinter Demo")
        self.root.geometry("1000x700")
        
        # Initialize systems
        self.vg = VisualGenetics()
        self.mapper = GeneticToSVGMapper()
        self.generator = TurtleSVGGenerator()
        self.renderer = get_svg_renderer()
        self.voting_system = VotingSystem()
        self.pool_manager = GeneticPoolManager()
        
        self.voting_system.set_genetic_pool_manager(self.pool_manager)
        
        # Demo state
        self.designs = []
        self.current_design_index = 0
        self.demo_complete = False
        
        # Setup UI
        self.setup_ui()
        
        # Generate designs
        self.generate_designs()
        
        # Display first design
        self.display_current_design()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="TurboShells Visual Genetics System", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Left panel - Turtle display
        left_frame = ttk.LabelFrame(main_frame, text="Turtle Design", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        self.canvas = tk.Canvas(left_frame, width=400, height=400, bg='alice blue')
        self.canvas.pack()
        
        # Right panel - Controls and info
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Design info
        info_frame = ttk.LabelFrame(right_frame, text="Design Information", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.design_info_text = tk.Text(info_frame, width=40, height=15, wrap=tk.WORD)
        self.design_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Controls
        control_frame = ttk.LabelFrame(right_frame, text="Controls", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Navigation buttons
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.prev_button = ttk.Button(nav_frame, text="← Previous", command=self.prev_design)
        self.prev_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.design_label = ttk.Label(nav_frame, text="Design 1/5")
        self.design_label.pack(side=tk.LEFT, expand=True)
        
        self.next_button = ttk.Button(nav_frame, text="Next →", command=self.next_design)
        self.next_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Vote button
        self.vote_button = ttk.Button(control_frame, text="Vote for This Design", 
                                     command=self.vote_for_design)
        self.vote_button.pack(fill=tk.X, pady=(0, 10))
        
        # Status
        status_frame = ttk.LabelFrame(right_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Ready to vote")
        self.status_label.pack()
        
        # Bottom panel - Statistics
        stats_frame = ttk.LabelFrame(main_frame, text="Demo Statistics", padding="10")
        stats_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, text="Loading...")
        self.stats_label.pack()
        
        # Keyboard bindings
        self.root.bind('<Left>', lambda e: self.prev_design())
        self.root.bind('<Right>', lambda e: self.next_design())
        self.root.bind('<space>', lambda e: self.vote_for_design())
        self.root.bind('<Escape>', lambda e: self.root.quit())
    
    def generate_designs(self):
        """Generate daily designs for voting"""
        print("Generating daily designs...")
        self.designs = self.voting_system.generate_daily_designs()
        print(f"Generated {len(self.designs)} designs for voting")
        
        # Update design label
        self.design_label.config(text=f"Design 1/{len(self.designs)}")
    
    def display_current_design(self):
        """Display the current turtle design"""
        if not self.designs or self.current_design_index >= len(self.designs):
            return
        
        design = self.designs[self.current_design_index]
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Render turtle
        photo_image = self.renderer.render_turtle_to_photoimage(design.genetics, 300)
        
        if photo_image:
            # Center image on canvas
            x = (400 - photo_image.width()) // 2
            y = (400 - photo_image.height()) // 2
            self.canvas.create_image(x, y, anchor=tk.NW, image=photo_image)
            
            # Keep reference to prevent garbage collection
            self.current_photo = photo_image
        else:
            # Show error
            self.canvas.create_text(200, 200, text="Failed to render turtle", 
                                   fill="red", font=('Arial', 14))
        
        # Update design info
        self.update_design_info(design)
        
        # Update navigation
        self.design_label.config(text=f"Design {self.current_design_index + 1}/{len(self.designs)}")
        
        # Update vote button
        if design.voting_status == 'completed':
            self.vote_button.config(text="Already Voted", state='disabled')
        else:
            self.vote_button.config(text="Vote for This Design", state='normal')
    
    def update_design_info(self, design):
        """Update the design information display"""
        genetics = design.genetics
        
        info = f"Design ID: {design.id}\n"
        info += f"Status: {design.voting_status.title()}\n\n"
        info += "=== Genetic Traits ===\n\n"
        
        # Key visual traits
        info += f"Shell Color: RGB{genetics['shell_base_color']}\n"
        info += f"Body Color: RGB{genetics['body_base_color']}\n"
        info += f"Shell Pattern: {genetics['shell_pattern_type'].title()}\n"
        info += f"Body Pattern: {genetics['body_pattern_type'].title()}\n"
        info += f"Eye Color: RGB{genetics['eye_color']}\n"
        info += f"Head Color: RGB{genetics['head_color']}\n"
        info += f"Leg Color: RGB{genetics['leg_color']}\n\n"
        
        # Modifiers
        info += "=== Size Modifiers ===\n\n"
        info += f"Shell Size: {genetics['shell_size_modifier']:.2f}\n"
        info += f"Head Size: {genetics['head_size_modifier']:.2f}\n"
        info += f"Eye Size: {genetics['eye_size_modifier']:.2f}\n"
        info += f"Leg Length: {genetics['leg_length_modifier']:.2f}\n"
        info += f"Leg Thickness: {genetics['leg_thickness_modifier']:.2f}\n"
        
        # Rarity (using a simple calculation)
        numeric_values = [v for v in genetics.values() if isinstance(v, (int, float))]
        info += f"\nRarity Score: {(sum(numeric_values) / len(numeric_values)) % 10:.2f}\n"
        
        # Update text widget
        self.design_info_text.delete(1.0, tk.END)
        self.design_info_text.insert(1.0, info)
    
    def prev_design(self):
        """Navigate to previous design"""
        if self.designs:
            self.current_design_index = (self.current_design_index - 1) % len(self.designs)
            self.display_current_design()
    
    def next_design(self):
        """Navigate to next design"""
        if self.designs:
            self.current_design_index = (self.current_design_index + 1) % len(self.designs)
            self.display_current_design()
    
    def vote_for_design(self):
        """Vote for the current design"""
        if not self.designs or self.current_design_index >= len(self.designs):
            return
        
        design = self.designs[self.current_design_index]
        
        if design.voting_status == 'completed':
            messagebox.showinfo("Already Voted", "You have already voted for this design!")
            return
        
        # Generate automatic ratings for demo
        ratings = {
            'overall': 3.0 + (self.current_design_index * 0.5),
            'shell_appearance': 3.5,
            'color_harmony': 4.0,
            'pattern_quality': 3.0,
            'proportions': 4.0
        }
        
        # Submit vote
        result = self.voting_system.submit_ratings(design.id, ratings)
        
        if result['success']:
            messagebox.showinfo("Vote Submitted", 
                              f"Successfully voted for Design {self.current_design_index + 1}!\n"
                              f"Earned ${result['reward_earned']}\n"
                              f"Your ratings influenced future turtle genetics!")
            
            # Update display
            design.voting_status = 'completed'
            self.display_current_design()
            
            # Check if all designs are voted
            status = self.voting_system.get_daily_status()
            if status['completed_votes'] == status['total_designs']:
                self.demo_complete = True
                messagebox.showinfo("Demo Complete!", 
                                  f"Congratulations! You completed all votes!\n"
                                  f"Total earned: ${status['potential_earnings']}\n"
                                  f"Your votes have influenced the genetic pool!")
            
            # Update statistics
            self.update_statistics()
        else:
            messagebox.showerror("Vote Failed", f"Failed to submit vote: {result.get('error', 'Unknown error')}")
    
    def update_statistics(self):
        """Update the statistics display"""
        status = self.voting_system.get_daily_status()
        pool_stats = self.pool_manager.get_genetic_pool_status()
        
        stats_text = f"Votes Cast: {status['completed_votes']}/{status['total_designs']}\n"
        stats_text += f"Total Earned: ${status['total_earned']}\n"
        stats_text += f"Genetic Pool Influence: {pool_stats['average_weight']:.2f} average weight\n"
        
        if pool_stats['most_influenced_traits']:
            traits = ', '.join(pool_stats['most_influenced_traits'][:3])
            stats_text += f"Most Influenced Traits: {traits}"
        
        self.stats_label.config(text=stats_text)
    
    def run(self):
        """Start the demo"""
        print("=== TurboShells Visual Genetics System Demo (Tkinter) ===")
        print()
        print("Use LEFT/RIGHT arrows to navigate, SPACE to vote, ESC to exit")
        print()
        
        # Initial statistics update
        self.update_statistics()
        
        # Show renderer capabilities
        capabilities = self.renderer.get_rendering_capabilities()
        print(f"Renderer: {capabilities['renderer_type']}")
        print(f"Primary converter: {capabilities['primary_converter']}")
        print(f"Available converters: {', '.join(capabilities['available_converters']) or 'none'}")
        print(f"Can render SVG: {capabilities['can_render_svg']}")
        print()
        
        # Start the GUI
        self.root.mainloop()


def main():
    """Run the Tkinter visual genetics demonstration"""
    try:
        demo = VisualGeneticsDemo()
        demo.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start demo: {e}")
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
