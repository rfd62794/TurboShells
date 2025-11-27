"""
Breeding Panel for TurboShells

Modern pygame_gui implementation of the breeding interface.
"""

import pygame
import pygame_gui
from typing import List, Optional, Tuple
from ui.panels.base_panel import BasePanel
from core.rendering.pygame_turtle_renderer import render_turtle_pygame


class BreedingPanel(BasePanel):
    """Breeding interface panel using pygame_gui components."""
    
    def __init__(self, game_state_interface):
        super().__init__("breeding", "Breeding Center")
        
        self.game_state = game_state_interface
        
        # Set default size and position to use full window
        self.size = (900, 700)
        self.position = (50, 25)
        
        # Breeding state
        self.selected_parents = []
        self.breeding_slots = []
        self.parent_labels = []
        
        # UI elements
        self.btn_breed = None
        self.btn_menu = None
        self.info_label = None
        self.warning_label = None
        self.money_label = None
        self.slots_container = None
        
    def _create_window(self) -> None:
        """Create the breeding window and elements."""
        super()._create_window()
        
        if not self.window:
            return
            
        container = self.window.get_container()
        width = self.size[0] - 40
        y_pos = 10
        
        # Header
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_pos), (width, 30)),
            text="BREEDING CENTER",
            manager=self.manager,
            container=container
        )
        
        # Money display
        money = self.game_state.get('money', 0)
        self.money_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((width - 150, y_pos), (140, 30)),
            text=f"$ {money}",
            manager=self.manager,
            container=container
        )
        y_pos += 40
        
        # Instructions
        self.instruction_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_pos), (width, 25)),
            text="Select 2 Parents",
            manager=self.manager,
            container=container
        )
        y_pos += 30
        
        # Warning
        self.warning_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_pos), (width, 25)),
            text="Parent 2 will be lost after breeding.",
            manager=self.manager,
            container=container
        )
        y_pos += 35
        
        # Breed button (initially disabled)
        self.btn_breed = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, y_pos), (120, 35)),
            text="BREED",
            manager=self.manager,
            container=container
        )
        self.btn_breed.disable()
        
        # Info label for breeding info
        self.info_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((140, y_pos), (width - 150, 35)),
            text="",
            manager=self.manager,
            container=container
        )
        y_pos += 45
        
        # Create breeding slots container (using UIPanel instead)
        self.slots_container = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10, y_pos), (width - 20, 380)),
            manager=self.manager,
            container=container
        )
        
        # Create breeding slots
        self._create_breeding_slots()
        
        # Menu button
        self.btn_menu = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 100, 10), (80, 30)),
            text="MENU",
            manager=self.manager,
            container=container
        )
        
    def _create_breeding_slots(self) -> None:
        """Create breeding selection slots with turtle rendering."""
        if not self.slots_container:
            return
            
        # Clear existing slots
        for slot in self.breeding_slots:
            if hasattr(slot, 'kill'):
                slot.kill()
        for label in self.parent_labels:
            if hasattr(label, 'kill'):
                label.kill()
                
        self.breeding_slots = []
        self.parent_labels = []
        
        # Get breeding candidates
        roster = self.game_state.get('roster', [])
        retired_roster = self.game_state.get('retired_roster', [])
        candidates = [t for t in roster if t is not None] + list(retired_roster)
        
        # Create slot buttons in 2x3 grid
        slot_width = 220
        slot_height = 180
        spacing = 10
        
        positions = [
            (10, 10), (240, 10), (470, 10),  # Top row
            (10, 200), (240, 200), (470, 200)  # Bottom row
        ]
        
        for i, pos in enumerate(positions):
            if i < len(candidates):
                turtle = candidates[i]
                is_retired = turtle in retired_roster
                
                # Create slot container with border support
                slot_container = pygame_gui.elements.UIPanel(
                    relative_rect=pygame.Rect(pos, (slot_width, slot_height)),
                    manager=self.manager,
                    container=self.slots_container,
                    object_id=f"#breeding_slot_container_{i}"
                )
                
                # Store reference to container for border updates
                slot_container.slot_index = i
                slot_container.turtle_data = turtle
                
                # Create turtle image (separate from button)
                turtle_img = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect((10, 10), (slot_width - 20, 120)),
                    image_surface=pygame.Surface((slot_width - 20, 120)),  # Placeholder
                    manager=self.manager,
                    container=slot_container,
                    object_id=f"#breeding_turtle_img_{i}"
                )
                
                # Set turtle image
                try:
                    turtle_surface = render_turtle_pygame(turtle, 100)
                    if turtle_surface:
                        turtle_img.set_image(turtle_surface)
                except Exception as e:
                    print(f"Error rendering turtle in breeding slot {i}: {e}")
                
                # Create selection button below image
                select_btn = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((10, 140), (slot_width - 20, 30)),
                    text=f"{turtle.name}\n{'(RETIRED)' if is_retired else ''}",
                    manager=self.manager,
                    container=slot_container,
                    object_id=f"#breeding_slot_{i}"
                )
                
                # Store turtle data with the button
                select_btn.turtle_data = turtle
                select_btn.is_retired = is_retired
                select_btn.slot_index = i
                select_btn.image_element = turtle_img  # Reference to image
                select_btn.container_element = slot_container  # Reference to container for border
                
                self.breeding_slots.append(select_btn)
                
                # Create parent indicator label (initially hidden)
                parent_label = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((pos[0] + 10, pos[1] + slot_height - 25), (slot_width - 20, 20)),
                    text="",
                    manager=self.manager,
                    container=self.slots_container
                )
                parent_label.hide()
                self.parent_labels.append(parent_label)
            else:
                # Empty slot
                empty_label = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(pos, (slot_width, slot_height)),
                    text="EMPTY",
                    manager=self.manager,
                    container=self.slots_container
                )
                self.breeding_slots.append(empty_label)
                
    def update(self, time_delta: float) -> None:
        """Update panel state and UI elements."""
        super().update(time_delta)
        
        # Update money display
        money = self.game_state.get('money', 0)
        if hasattr(self, 'money_label') and self.money_label:
            self.money_label.set_text(f"$ {money}")
        
        # Only update selection indicators (don't recreate slots)
        self._update_selection_indicators()
        
        # Update breed button state
        self._update_breed_button()
        
        # Update info label
        self._update_info_label()
        
    def _update_selection_indicators(self) -> None:
        """Update parent selection indicators with clear visual borders."""
        for slot in self.breeding_slots:
            if hasattr(slot, 'container_element') and hasattr(slot, 'turtle_data'):
                container = slot.container_element
                turtle = slot.turtle_data
                is_selected = turtle in self.selected_parents
                
                # Update parent indicator label with prominent styling
                slot_index = getattr(slot, 'slot_index', 0)
                if slot_index < len(self.parent_labels):
                    parent_label = self.parent_labels[slot_index]
                    if is_selected:
                        parent_num = "1" if self.selected_parents[0] == turtle else "2"
                        loss_text = " (WILL BE LOST)" if parent_num == "2" else " (SURVIVES)"
                        
                        # Make label very prominent
                        parent_label.set_text(f"=== PARENT {parent_num}{loss_text} ===")
                        parent_label.show()
                        
                        # Position label at top of slot for visibility
                        if hasattr(parent_label, 'set_position'):
                            parent_label.set_position(pygame.Rect(
                                container.rect.x + 5, 
                                container.rect.y + 5, 
                                container.rect.width - 10, 
                                25
                            ))
                    else:
                        parent_label.hide()
                        
                # Draw colored border indicator directly on container
                if is_selected:
                    parent_num = "1" if self.selected_parents[0] == turtle else "2"
                    # We'll override the container's draw method to add borders
                    container.draw_border = True
                    container.border_color = (0, 255, 0) if parent_num == "1" else (255, 0, 0)
                    container.border_width = 4
                else:
                    container.draw_border = False
                        
    def _update_breed_button(self) -> None:
        """Update breed button state based on selection."""
        if not self.btn_breed:
            return
            
        if len(self.selected_parents) == 2:
            self.btn_breed.enable()
        else:
            self.btn_breed.disable()
            
    def _update_info_label(self) -> None:
        """Update breeding info label."""
        if not self.info_label:
            return
            
        if len(self.selected_parents) == 2:
            parent1, parent2 = self.selected_parents
            info_text = f"Breeding: {parent1.name} + {parent2.name}"
            self.info_label.set_text(info_text)
        else:
            self.info_label.set_text("")
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle breeding panel events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Check breeding slot clicks
            if hasattr(event.ui_element, 'turtle_data'):
                turtle = event.ui_element.turtle_data
                
                # Toggle selection
                if turtle in self.selected_parents:
                    self.selected_parents.remove(turtle)
                elif len(self.selected_parents) < 2:
                    self.selected_parents.append(turtle)
                else:
                    # Already have 2 parents, replace the second one
                    self.selected_parents[1] = turtle
                    
                # Update game state
                self.game_state.set('breeding_parents', self.selected_parents.copy())
                return True
                
            # Breed button
            elif event.ui_element == self.btn_breed:
                if len(self.selected_parents) == 2:
                    self.game_state.set('breed_now', True)
                    # Clear selection after breeding
                    self.selected_parents = []
                    self.game_state.set('breeding_parents', [])
                return True
                
            # Menu button
            elif event.ui_element == self.btn_menu:
                self.game_state.set('goto_menu', True)
                return True
                
        return False
        
    def refresh_slots(self) -> None:
        """Refresh breeding slots when roster changes (only call when actually needed)."""
        self._create_breeding_slots()
        
    def clear_selection(self) -> None:
        """Clear parent selection."""
        self.selected_parents = []
        self.game_state.set('breeding_parents', [])
        self._update_selection_indicators()
