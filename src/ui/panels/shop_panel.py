import pygame
import pygame_gui
from .base_panel import BasePanel
from game.game_state_interface import TurboShellsGameStateInterface
from core.rendering.pygame_turtle_renderer import render_turtle_pygame

class ShopPanel(BasePanel):
    """Shop Panel using pygame_gui."""
    
    def __init__(self, game_state_interface: TurboShellsGameStateInterface):
        super().__init__("shop", "Turtle Shop")
        self.game_state = game_state_interface
        
        self.size = (800, 600)
        self.position = (112, 84) # Centered roughly
        
        self.lbl_money = None
        self.lbl_message = None
        self.container_inventory = None
        self.btn_refresh = None
        self.btn_back = None
        
        self.inventory_slots = [] # List of dicts holding UI elements for each slot
        
        # Observers
        self.game_state.observe('money', self._on_money_changed)
        self.game_state.observe('shop_inventory', self._on_inventory_changed)
        self.game_state.observe('shop_message', self._on_message_changed)
        
    def _create_window(self) -> None:
        super()._create_window()
        if not self.window:
            return
            
        if self.manager and self.manager.window_resolution:
            screen_w, screen_h = self.manager.window_resolution
            self.position = ((screen_w - self.size[0]) // 2, (screen_h - self.size[1]) // 2)
            self.window.set_position(self.position)
            
        container = self.window.get_container()
        width = self.size[0] - 40
        
        # Header
        top_bar = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (width + 40, 60)),
            manager=self.manager,
            container=container,
            object_id="#shop_header"
        )
        
        self.lbl_money = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 15), (200, 30)),
            text=f"Funds: ${self.game_state.get('money', 0)}",
            manager=self.manager,
            container=top_bar
        )
        
        self.btn_back = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 100, 10), (100, 40)),
            text="Back",
            manager=self.manager,
            container=top_bar
        )
        
        # Message Area
        self.lbl_message = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 70), (width, 30)),
            text=self.game_state.get('shop_message', ''),
            manager=self.manager,
            container=container
        )
        
        # Inventory Container (Scrolling)
        self.container_inventory = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect((20, 110), (width, 400)),
            manager=self.manager,
            container=container
        )
        
        # Refresh Button
        self.btn_refresh = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width // 2 - 75, 520), (150, 40)),
            text="Refresh ($5)",
            manager=self.manager,
            container=container
        )
        
        self._populate_inventory()
        
    def _populate_inventory(self):
        """Populate the inventory container with turtle cards."""
        if not self.container_inventory:
            return
            
        # Clear existing
        for slot in self.inventory_slots:
            if 'card' in slot:
                slot['card'].kill()
        self.inventory_slots = []
        
        inventory = self.game_state.get('shop_inventory', [])
        
        card_width = 220
        card_height = 350
        spacing = 20
        start_x = 10
        start_y = 10
        
        for i, turtle in enumerate(inventory):
            x = start_x + (i * (card_width + spacing))
            y = start_y
            
            # Card Panel
            card = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((x, y), (card_width, card_height)),
                manager=self.manager,
                container=self.container_inventory,
                object_id="#shop_card"
            )
            
            # Turtle Image
            try:
                turtle_surface = render_turtle_pygame(turtle, size=100)
                pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect((60, 10), (100, 100)),
                    image_surface=turtle_surface,
                    manager=self.manager,
                    container=card
                )
            except Exception:
                pass
                
            # Name
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, 120), (200, 25)),
                text=turtle.name,
                manager=self.manager,
                container=card
            )
            
            # Stats
            stats_text = (
                f"Spd: {turtle.stats['speed']}<br>"
                f"Eng: {turtle.stats['max_energy']}<br>"
                f"Rec: {turtle.stats['recovery']}<br>"
                f"Swm: {turtle.stats['swim']}<br>"
                f"Clm: {turtle.stats['climb']}"
            )
            
            pygame_gui.elements.UITextBox(
                relative_rect=pygame.Rect((10, 150), (200, 120)),
                html_text=stats_text,
                manager=self.manager,
                container=card
            )
            
            # Cost
            cost = getattr(turtle, 'shop_cost', 50)
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, 280), (200, 25)),
                text=f"${cost}",
                manager=self.manager,
                container=card,
                object_id="#shop_cost"
            )
            
            # Buy Button
            btn_buy = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((60, 310), (100, 30)),
                text="BUY",
                manager=self.manager,
                container=card,
                object_id="#btn_buy"
            )
            
            self.inventory_slots.append({
                'card': card,
                'index': i,
                'btn_buy': btn_buy
            })
            
        # Update scrolling area
        total_width = len(inventory) * (card_width + spacing) + 20
        self.container_inventory.set_scrollable_area_dimensions((max(total_width, self.container_inventory.relative_rect.width), 400))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_back:
                self.game_state.set('state', 'menu')
                return True
            elif event.ui_element == self.btn_refresh:
                self.game_state.set('shop_refresh', True)
                return True
            else:
                # Check buy buttons
                for slot in self.inventory_slots:
                    if event.ui_element == slot['btn_buy']:
                        self.game_state.set('shop_buy', slot['index'])
                        return True
        return False

    def _on_money_changed(self, key, old, new):
        if self.lbl_money:
            self.lbl_money.set_text(f"Funds: ${new}")
            
    def _on_inventory_changed(self, key, old, new):
        self._populate_inventory()
        
    def _on_message_changed(self, key, old, new):
        if self.lbl_message:
            self.lbl_message.set_text(new)

    def show(self):
        super().show()
        # Refresh inventory on show to ensure up to date
        self._populate_inventory()
