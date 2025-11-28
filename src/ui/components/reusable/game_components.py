"""
Game-specific reusable components.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any, List, Callable
from ..base_component import BaseComponent
from .display_components import MoneyDisplay, ProgressBar, ImageDisplay
from .input_components import Button, IconButton


class TurtleCard(BaseComponent):
    """Reusable turtle card component."""
    
    def __init__(self, rect: pygame.Rect, turtle=None, manager=None, config: Optional[Dict] = None):
        """Initialize turtle card.
        
        Args:
            rect: Card position and size
            turtle: Turtle object with required attributes
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.turtle = turtle
        self.config = config or {}
        
        # Card options
        self.show_train_button = self.config.get('show_train_button', True)
        self.show_view_button = self.config.get('show_view_button', True)
        self.show_select_button = self.config.get('show_select_button', False)
        self.show_stats = self.config.get('show_stats', True)
        self.is_selected = False
        self.is_active_racer = False
        
        # Sub-components
        self.image_display: Optional[ImageDisplay] = None
        self.name_label: Optional[pygame_gui.elements.UILabel] = None
        self.stats_label: Optional[pygame_gui.elements.UITextBox] = None
        self.energy_bar: Optional[ProgressBar] = None
        self.train_button: Optional[Button] = None
        self.view_button: Optional[Button] = None
        self.select_button: Optional[Button] = None
        
        # Callbacks
        self.on_train: Optional[Callable] = None
        self.on_view: Optional[Callable] = None
        self.on_select: Optional[Callable] = None
        
        if self.manager:
            self._create_components()
            
    def _create_components(self) -> None:
        """Create card sub-components."""
        # Turtle image
        image_rect = pygame.Rect(10, 10, 80, 80)
        self.image_display = ImageDisplay(image_rect, manager=self.manager)
        self.add_child(self.image_display)
        
        # Name label
        name_rect = pygame.Rect(100, 10, self.rect.width - 110, 25)
        self.name_label = pygame_gui.elements.UILabel(
            relative_rect=name_rect,
            text="",
            manager=self.manager
        )
        
        # Stats text box
        if self.show_stats:
            stats_rect = pygame.Rect(100, 35, self.rect.width - 110, 40)
            self.stats_label = pygame_gui.elements.UITextBox(
                relative_rect=stats_rect,
                html_text="",
                manager=self.manager
            )
            
        # Energy bar
        energy_rect = pygame.Rect(10, 95, self.rect.width - 20, 15)
        self.energy_bar = ProgressBar(
            rect=energy_rect,
            manager=self.manager,
            config={'show_text': False, 'fill_color': (0, 200, 0)}
        )
        self.add_child(self.energy_bar)
        
        # Action buttons
        button_y = 115
        button_spacing = 5
        button_width = 60
        button_height = 25
        
        if self.show_train_button:
            train_rect = pygame.Rect(10, button_y, button_width, button_height)
            self.train_button = Button(train_rect, "TRAIN", "train", self.manager)
            self.train_button.set_action_callback(lambda: self._on_train_clicked())
            self.add_child(self.train_button)
            button_y += button_height + button_spacing
            
        if self.show_view_button:
            view_rect = pygame.Rect(10, button_y, button_width, button_height)
            self.view_button = Button(view_rect, "VIEW", "view", self.manager)
            self.view_button.set_action_callback(lambda: self._on_view_clicked())
            self.add_child(self.view_button)
            button_y += button_height + button_spacing
            
        if self.show_select_button:
            select_rect = pygame.Rect(10, button_y, button_width, button_height)
            self.select_button = Button(select_rect, "SELECT", "select", self.manager)
            self.select_button.set_action_callback(lambda: self._on_select_clicked())
            self.add_child(self.select_button)
            
        self._update_display()
        
    def _update_display(self) -> None:
        """Update card display with turtle data."""
        if not self.turtle:
            # Empty slot
            if self.name_label:
                self.name_label.set_text("Empty")
            if self.stats_label:
                self.stats_label.set_text("")
            if self.energy_bar:
                self.energy_bar.set_progress(0, 100)
            self._set_buttons_enabled(False)
            return
            
        # Update name
        if self.name_label:
            self.name_label.set_text(getattr(self.turtle, 'name', 'Unknown'))
            
        # Update stats
        if self.stats_label and self.show_stats:
            stats_text = self._format_stats()
            self.stats_label.set_text(stats_text)
            
        # Update energy bar
        if self.energy_bar:
            current_energy = getattr(self.turtle, 'current_energy', 0)
            max_energy = getattr(self.turtle, 'stats', {}).get('max_energy', 100)
            self.energy_bar.set_progress(current_energy, max_energy)
            
        # Update button states
        self._set_buttons_enabled(True)
        
        # Update turtle image (placeholder for now)
        if self.image_display:
            # Could integrate with turtle render engine here
            pass
            
    def _format_stats(self) -> str:
        """Format turtle stats for display."""
        if not hasattr(self.turtle, 'stats'):
            return ""
            
        stats = self.turtle.stats
        lines = []
        
        if 'speed' in stats:
            lines.append(f"Speed: {stats['speed']}")
        if 'max_energy' in stats:
            lines.append(f"Energy: {stats['max_energy']}")
        if 'strength' in stats:
            lines.append(f"Strength: {stats['strength']}")
        if 'agility' in stats:
            lines.append(f"Agility: {stats['agility']}")
            
        return "<br>".join(lines)
        
    def _set_buttons_enabled(self, enabled: bool) -> None:
        """Enable/disable action buttons."""
        if self.train_button:
            self.train_button.set_enabled(enabled and self.is_active_racer)
        if self.view_button:
            self.view_button.set_enabled(enabled)
        if self.select_button:
            self.select_button.set_enabled(enabled)
            
    def _on_train_clicked(self) -> None:
        """Handle train button click."""
        if self.on_train:
            self.on_train(self.turtle)
        self._emit_event('train', {'turtle': self.turtle})
        
    def _on_view_clicked(self) -> None:
        """Handle view button click."""
        if self.on_view:
            self.on_view(self.turtle)
        self._emit_event('view', {'turtle': self.turtle})
        
    def _on_select_clicked(self) -> None:
        """Handle select button click."""
        if self.on_select:
            self.on_select(self.turtle)
        self._emit_event('select', {'turtle': self.turtle})
        
    def set_turtle(self, turtle) -> None:
        """Update turtle data."""
        self.turtle = turtle
        self._update_display()
        
    def set_selected(self, selected: bool) -> None:
        """Set selection state."""
        self.is_selected = selected
        # Could update visual appearance here
        
    def set_active_racer(self, active: bool) -> None:
        """Set active racer state."""
        self.is_active_racer = active
        self._set_buttons_enabled(True)  # Refresh button states
        
    def render(self, surface: pygame.Surface) -> None:
        """Render turtle card."""
        if not self.visible:
            return
            
        abs_rect = self.get_absolute_rect()
        
        # Draw card border with selection state
        border_color = (0, 200, 0) if self.is_selected else (
            (200, 200, 200) if self.is_active_racer else (150, 150, 150)
        )
        border_width = 3 if self.is_selected else 2
        pygame.draw.rect(surface, border_color, abs_rect, border_width)
        
        # Draw background
        if not self.manager:  # Custom rendering mode
            bg_color = (240, 240, 240) if self.is_selected else (250, 250, 250)
            pygame.draw.rect(surface, bg_color, abs_rect)
            
        # Render sub-components
        super().render(surface)


class ItemCard(BaseComponent):
    """Reusable item card for shop/inventory."""
    
    def __init__(self, rect: pygame.Rect, item=None, manager=None, config: Optional[Dict] = None):
        """Initialize item card.
        
        Args:
            rect: Card position and size
            item: Item object with required attributes
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.item = item
        self.config = config or {}
        
        # Card options
        self.show_price = self.config.get('show_price', True)
        self.show_buy_button = self.config.get('show_buy_button', True)
        self.show_quantity = self.config.get('show_quantity', False)
        self.is_affordable = True
        
        # Sub-components
        self.image_display: Optional[ImageDisplay] = None
        self.name_label: Optional[pygame_gui.elements.UILabel] = None
        self.description_label: Optional[pygame_gui.elements.UILabel] = None
        self.price_display: Optional[MoneyDisplay] = None
        self.quantity_label: Optional[pygame_gui.elements.UILabel] = None
        self.buy_button: Optional[Button] = None
        
        # Callbacks
        self.on_buy: Optional[Callable] = None
        
        if self.manager:
            self._create_components()
            
    def _create_components(self) -> None:
        """Create card sub-components."""
        # Item image
        image_rect = pygame.Rect(10, 10, 60, 60)
        self.image_display = ImageDisplay(image_rect, manager=self.manager)
        self.add_child(self.image_display)
        
        # Name label
        name_rect = pygame.Rect(80, 10, self.rect.width - 90, 20)
        self.name_label = pygame_gui.elements.UILabel(
            relative_rect=name_rect,
            text="",
            manager=self.manager
        )
        
        # Description label
        desc_rect = pygame.Rect(80, 30, self.rect.width - 90, 25)
        self.description_label = pygame_gui.elements.UILabel(
            relative_rect=desc_rect,
            text="",
            manager=self.manager
        )
        
        # Price display
        if self.show_price:
            price_rect = pygame.Rect(10, 75, self.rect.width - 20, 20)
            self.price_display = MoneyDisplay(price_rect, 0, self.manager)
            self.add_child(self.price_display)
            
        # Quantity label
        if self.show_quantity:
            qty_rect = pygame.Rect(10, 95, self.rect.width - 20, 20)
            self.quantity_label = pygame_gui.elements.UILabel(
                relative_rect=qty_rect,
                text="",
                manager=self.manager
            )
            
        # Buy button
        if self.show_buy_button:
            buy_rect = pygame.Rect(10, self.rect.height - 35, self.rect.width - 20, 25)
            self.buy_button = Button(buy_rect, "BUY", "buy", self.manager)
            self.buy_button.set_action_callback(lambda: self._on_buy_clicked())
            self.add_child(self.buy_button)
            
        self._update_display()
        
    def _update_display(self) -> None:
        """Update card display with item data."""
        if not self.item:
            # Empty slot
            if self.name_label:
                self.name_label.set_text("")
            if self.description_label:
                self.description_label.set_text("")
            if self.price_display:
                self.price_display.set_amount(0)
            if self.quantity_label:
                self.quantity_label.set_text("")
            if self.buy_button:
                self.buy_button.set_enabled(False)
            return
            
        # Update name
        if self.name_label:
            self.name_label.set_text(getattr(self.item, 'name', 'Unknown'))
            
        # Update description
        if self.description_label:
            desc = getattr(self.item, 'description', '')
            # Truncate if too long
            if len(desc) > 40:
                desc = desc[:37] + "..."
            self.description_label.set_text(desc)
            
        # Update price
        if self.price_display and self.show_price:
            price = getattr(self.item, 'price', 0)
            self.price_display.set_amount(price)
            
        # Update quantity
        if self.quantity_label and self.show_quantity:
            quantity = getattr(self.item, 'quantity', 0)
            self.quantity_label.set_text(f"Quantity: {quantity}")
            
        # Update buy button
        if self.buy_button:
            self.buy_button.set_enabled(self.is_affordable)
            
        # Update item image (placeholder for now)
        if self.image_display:
            # Could integrate with item render system here
            pass
            
    def _on_buy_clicked(self) -> None:
        """Handle buy button click."""
        if self.on_buy:
            self.on_buy(self.item)
        self._emit_event('buy', {'item': self.item})
        
    def set_item(self, item) -> None:
        """Update item data."""
        self.item = item
        self._update_display()
        
    def set_affordable(self, affordable: bool) -> None:
        """Set affordability state."""
        self.is_affordable = affordable
        if self.buy_button:
            self.buy_button.set_enabled(affordable)
            
    def render(self, surface: pygame.Surface) -> None:
        """Render item card."""
        if not self.visible:
            return
            
        abs_rect = self.get_absolute_rect()
        
        # Draw card border
        border_color = (200, 200, 200)
        if not self.is_affordable:
            border_color = (150, 100, 100)
        pygame.draw.rect(surface, border_color, abs_rect, 2)
        
        # Draw background
        if not self.manager:  # Custom rendering mode
            bg_color = (250, 250, 250)
            if not self.is_affordable:
                bg_color = (240, 230, 230)
            pygame.draw.rect(surface, bg_color, abs_rect)
            
        # Render sub-components
        super().render(surface)


class BetSelector(BaseComponent):
    """Component for selecting bet amounts."""
    
    def __init__(self, rect: pygame.Rect, amounts: List[int] = None, 
                 manager=None, config: Optional[Dict] = None):
        """Initialize bet selector.
        
        Args:
            rect: Component position and size
            amounts: List of bet amounts
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.amounts = amounts or [0, 5, 10, 25, 50]
        self.selected_amount = 0
        self.config = config or {}
        
        # Options
        self.show_custom = self.config.get('show_custom', True)
        self.custom_amount = 0
        
        # Sub-components
        self.bet_buttons: List[Button] = []
        self.custom_input: Optional[pygame_gui.elements.UITextEntryLine] = None
        self.current_bet_label: Optional[pygame_gui.elements.UILabel] = None
        
        # Callback
        self.on_bet_changed: Optional[Callable[[int], None]] = None
        
        if self.manager:
            self._create_components()
            
    def _create_components(self) -> None:
        """Create bet selector components."""
        # Bet amount buttons
        button_width = 60
        button_height = 30
        button_spacing = 5
        x = 0
        
        for amount in self.amounts:
            button_rect = pygame.Rect(x, 0, button_width, button_height)
            button = Button(button_rect, f"${amount}", f"bet_{amount}", self.manager)
            button.set_action_callback(lambda amt=amount: self._select_amount(amt))
            self.bet_buttons.append(button)
            self.add_child(button)
            x += button_width + button_spacing
            
        # Custom amount input
        if self.show_custom:
            custom_rect = pygame.Rect(x, 0, 80, button_height)
            self.custom_input = pygame_gui.elements.UITextEntryLine(
                relative_rect=custom_rect,
                manager=self.manager
            )
            self.custom_input.set_text("0")
            
        # Current bet display
        bet_rect = pygame.Rect(0, 40, self.rect.width, 25)
        self.current_bet_label = pygame_gui.elements.UILabel(
            relative_rect=bet_rect,
            text="Current Bet: $0",
            manager=self.manager
        )
        
    def _select_amount(self, amount: int) -> None:
        """Select bet amount."""
        self.selected_amount = amount
        self._update_display()
        
        if self.on_bet_changed:
            self.on_bet_changed(amount)
        self._emit_event('bet_changed', {'amount': amount})
        
    def _update_display(self) -> None:
        """Update display with current bet."""
        if self.current_bet_label:
            self.current_bet_label.set_text(f"Current Bet: ${self.selected_amount}")
            
        # Update button states
        for i, button in enumerate(self.bet_buttons):
            amount = self.amounts[i]
            button.set_enabled(True)  # Could add affordability checks
            
    def set_bet_amount(self, amount: int) -> None:
        """Set bet amount programmatically."""
        self.selected_amount = amount
        self._update_display()
        
    def get_bet_amount(self) -> int:
        """Get current bet amount."""
        return self.selected_amount
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle custom input events."""
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.custom_input:
                try:
                    custom_amount = int(event.text)
                    self._select_amount(custom_amount)
                except ValueError:
                    pass
                return True
        return False


class RaceHUD(BaseComponent):
    """Race heads-up display component."""
    
    def __init__(self, rect: pygame.Rect, manager=None, config: Optional[Dict] = None):
        """Initialize race HUD.
        
        Args:
            rect: HUD position and size
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.config = config or {}
        
        # Race data
        self.race_time = 0
        self.race_progress = 0
        self.player_position = 1
        self.total_racers = 4
        
        # Sub-components
        self.time_label: Optional[pygame_gui.elements.UILabel] = None
        self.position_label: Optional[pygame_gui.elements.UILabel] = None
        self.progress_bar: Optional[ProgressBar] = None
        self.speed_multiplier_buttons: List[Button] = []
        
        # Callbacks
        self.on_speed_change: Optional[Callable[[int], None]] = None
        
        if self.manager:
            self._create_components()
            
    def _create_components(self) -> None:
        """Create HUD components."""
        # Time display
        time_rect = pygame.Rect(10, 10, 100, 25)
        self.time_label = pygame_gui.elements.UILabel(
            relative_rect=time_rect,
            text="Time: 0.0s",
            manager=self.manager
        )
        
        # Position display
        pos_rect = pygame.Rect(120, 10, 150, 25)
        self.position_label = pygame_gui.elements.UILabel(
            relative_rect=pos_rect,
            text="Position: 1/4",
            manager=self.manager
        )
        
        # Progress bar
        progress_rect = pygame.Rect(10, 40, self.rect.width - 20, 20)
        self.progress_bar = ProgressBar(
            rect=progress_rect,
            manager=self.manager,
            config={'show_text': True}
        )
        self.add_child(self.progress_bar)
        
        # Speed multiplier buttons
        speeds = [1, 2, 4]
        button_width = 40
        button_height = 25
        button_spacing = 5
        x = 10
        
        for speed in speeds:
            button_rect = pygame.Rect(x, 70, button_width, button_height)
            button = Button(button_rect, f"{speed}x", f"speed_{speed}", self.manager)
            button.set_action_callback(lambda s=speed: self._set_speed(s))
            self.speed_multiplier_buttons.append(button)
            self.add_child(button)
            x += button_width + button_spacing
            
    def _set_speed(self, speed: int) -> None:
        """Set race speed multiplier."""
        if self.on_speed_change:
            self.on_speed_change(speed)
        self._emit_event('speed_change', {'speed': speed})
        
    def update_race_data(self, time: float, progress: float, position: int, total: int) -> None:
        """Update race data display."""
        self.race_time = time
        self.race_progress = progress
        self.player_position = position
        self.total_racers = total
        self._update_display()
        
    def _update_display(self) -> None:
        """Update HUD display."""
        if self.time_label:
            self.time_label.set_text(f"Time: {self.race_time:.1f}s")
            
        if self.position_label:
            self.position_label.set_text(f"Position: {self.player_position}/{self.total_racers}")
            
        if self.progress_bar:
            self.progress_bar.set_progress(self.race_progress, 100)
            
    def render(self, surface: pygame.Surface) -> None:
        """Render race HUD."""
        if not self.visible:
            return
            
        # Draw background
        abs_rect = self.get_absolute_rect()
        pygame.draw.rect(surface, (50, 50, 50), abs_rect)
        pygame.draw.rect(surface, (100, 100, 100), abs_rect, 2)
        
        # Render sub-components
        super().render(surface)
