"""
UI rendering component for settings interface.

Handles all drawing operations following SRP principles.
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import pygame

from core.logging_config import get_logger
from ui.components.tab_manager import TabManager, SettingsTab


@dataclass
class UIElement:
    """Base UI element for settings interface."""
    rect: pygame.Rect
    element_type: str
    label: str
    value: Any
    tooltip: str = ""
    enabled: bool = True


class StyleManager:
    """
    Manages UI styling and appearance.
    
    Single responsibility: Handle colors, fonts, and visual styling.
    """
    
    # UI Colors (can be themed)
    COLORS = {
        "background": (40, 40, 40),
        "panel": (60, 60, 60),
        "border": (100, 100, 100),
        "text": (255, 255, 255),
        "text_disabled": (150, 150, 150),
        "button": (80, 80, 80),
        "button_hover": (100, 100, 100),
        "button_active": (120, 120, 120),
        "tab": (70, 70, 70),
        "tab_active": (90, 90, 90),
        "accent": (100, 150, 200),
        "slider_track": (50, 50, 50),
        "slider_handle": (120, 120, 120),
        "checkbox": (80, 80, 80),
        "checkbox_checked": (100, 150, 200),
    }
    
    # Font sizes
    FONT_SIZES = {
        "title": 24,
        "tab": 16,
        "label": 14,
        "value": 14,
        "tooltip": 12
    }
    
    def __init__(self):
        """Initialize style manager."""
        self.logger = get_logger(__name__)
        self.fonts = {}
        self._initialize_fonts_safe()
    
    def _initialize_fonts_safe(self) -> None:
        """Initialize fonts for the UI with error handling."""
        try:
            # Try to initialize pygame font system
            pygame.font.init()
            
            for name, size in self.FONT_SIZES.items():
                try:
                    self.fonts[name] = pygame.font.Font(None, size)
                except Exception as e:
                    self.logger.warning(f"Failed to create font {name} size {size}: {e}")
                    # Create a simple fallback font
                    self.fonts[name] = pygame.font.SysFont("Arial", size)
            
            self.logger.debug("Fonts initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize font system: {e}")
            # Create minimal font fallbacks without pygame.font.init()
            for name, size in self.FONT_SIZES.items():
                self.fonts[name] = None
    
    def get_color(self, color_name: str) -> Tuple[int, int, int]:
        """Get color by name."""
        return self.COLORS.get(color_name, (255, 255, 255))
    
    def get_font(self, font_name: str) -> pygame.font.Font:
        """Get font by name."""
        font = self.fonts.get(font_name, self.fonts.get("label"))
        
        if font is None:
            # Create a fallback font on demand
            try:
                font = pygame.font.SysFont("Arial", self.FONT_SIZES.get(font_name, 14))
                self.fonts[font_name] = font
            except Exception:
                # Last resort - return a dummy font object
                class DummyFont:
                    def render(self, text, antialias, color):
                        return pygame.Surface((1, 1))
                    def size(self, text):
                        return (len(text) * 8, 16)
                font = DummyFont()
        
        return font


class UIRenderer:
    """
    Handles all UI rendering operations for the settings interface.
    
    Single responsibility: Pure rendering operations only.
    """
    
    def __init__(self, style_manager: Optional[StyleManager] = None):
        """
        Initialize UI renderer.
        
        Args:
            style_manager: Style manager for colors and fonts
        """
        self.style_manager = style_manager or StyleManager()
        self.logger = get_logger(__name__)
        
        # Rendering state
        self.mouse_pos = (0, 0)
        self.hover_element = None
        
        self.logger.debug("UIRenderer initialized")
    
    def update_mouse_position(self, mouse_pos: Tuple[int, int]) -> None:
        """Update current mouse position for hover effects."""
        self.mouse_pos = mouse_pos
    
    def draw_panel(self, screen: pygame.Surface, rect: pygame.Rect, title: str = "") -> None:
        """
        Draw a panel with optional title.
        
        Args:
            screen: Surface to draw on
            rect: Panel rectangle
            title: Optional panel title
        """
        # Draw panel background
        pygame.draw.rect(screen, self.style_manager.get_color("panel"), rect)
        pygame.draw.rect(screen, self.style_manager.get_color("border"), rect, 2)
        
        # Draw title if provided
        if title:
            title_font = self.style_manager.get_font("title")
            title_text = title_font.render(title, True, self.style_manager.get_color("text"))
            title_rect = title_text.get_rect(
                centerx=rect.centerx, 
                y=rect.y + 5
            )
            screen.blit(title_text, title_rect)
    
    def draw_tabs(self, screen: pygame.Surface, tab_manager: TabManager) -> None:
        """
        Draw all tabs.
        
        Args:
            screen: Surface to draw on
            tab_manager: Tab manager with tab data
        """
        for tab_id, tab_element in tab_manager.tabs.items():
            self._draw_single_tab(screen, tab_element, tab_manager.is_tab_active(tab_id))
    
    def _draw_single_tab(self, screen: pygame.Surface, tab_element, is_active: bool) -> None:
        """
        Draw a single tab.
        
        Args:
            screen: Surface to draw on
            tab_element: Tab element to draw
            is_active: Whether tab is currently active
        """
        # Determine tab color
        if not tab_element.config.enabled:
            color = self.style_manager.get_color("text_disabled")
        elif is_active:
            color = self.style_manager.get_color("tab_active")
        else:
            color = self.style_manager.get_color("tab")
        
        # Draw tab background
        pygame.draw.rect(screen, color, tab_element.rect)
        pygame.draw.rect(screen, self.style_manager.get_color("border"), tab_element.rect, 1)
        
        # Draw tab label with appropriate font size
        label_color = (
            self.style_manager.get_color("text") 
            if tab_element.config.enabled and is_active 
            else self.style_manager.get_color("text_disabled")
        )
        
        # Use appropriate font size based on tab width
        if tab_element.rect.width < 95:
            font_size = 11
        elif tab_element.rect.width < 105:
            font_size = 12
        else:
            font_size = 13
        
        tab_font = pygame.font.Font(None, font_size)
        label_text = tab_font.render(tab_element.config.label, True, label_color)
        label_rect = label_text.get_rect(center=tab_element.rect.center)
        
        # Smart text truncation if needed
        max_width = tab_element.rect.width - 6
        if label_rect.width > max_width:
            # Calculate how many characters can fit
            avg_char_width = label_rect.width // len(tab_element.config.label)
            max_chars = max_width // avg_char_width
            
            if max_chars >= 3:
                truncated_label = tab_element.config.label[:max_chars-1] + "…" if len(tab_element.config.label) > max_chars else tab_element.config.label
            else:
                # For very narrow tabs, use first letter only
                truncated_label = tab_element.config.label[0].upper()
            
            label_text = tab_font.render(truncated_label, True, label_color)
            label_rect = label_text.get_rect(center=tab_element.rect.center)
        
        screen.blit(label_text, label_rect)
    
    def draw_ui_element(self, screen: pygame.Surface, element: UIElement) -> None:
        """
        Draw a single UI element based on its type.
        
        Args:
            screen: Surface to draw on
            element: UI element to draw
        """
        if element.element_type == "dropdown":
            self._draw_dropdown(screen, element)
        elif element.element_type == "checkbox":
            self._draw_checkbox(screen, element)
        elif element.element_type == "slider":
            self._draw_slider(screen, element)
        elif element.element_type == "button":
            self._draw_button(screen, element)
        elif element.element_type == "list":
            self._draw_list(screen, element)
        elif element.element_type == "label":
            self._draw_label(screen, element)
        else:
            self.logger.warning(f"Unknown element type: {element.element_type}")
    
    def _draw_dropdown(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a dropdown element."""
        # Draw dropdown background
        pygame.draw.rect(screen, self.style_manager.get_color("button"), element.rect)
        pygame.draw.rect(screen, self.style_manager.get_color("border"), element.rect, 1)
        
        # Draw label
        label_font = self.style_manager.get_font("label")
        label_text = label_font.render(element.label, True, self.style_manager.get_color("text"))
        label_rect = label_text.get_rect(
            right=element.rect.left - 10, 
            centery=element.rect.centery
        )
        screen.blit(label_text, label_rect)
        
        # Draw value
        value_font = self.style_manager.get_font("value")
        value_text = value_font.render(str(element.value), True, self.style_manager.get_color("text"))
        value_rect = value_text.get_rect(
            left=element.rect.left + 5, 
            centery=element.rect.centery
        )
        screen.blit(value_text, value_rect)
        
        # Draw dropdown arrow
        arrow_points = [
            (element.rect.right - 15, element.rect.centery - 5),
            (element.rect.right - 5, element.rect.centery - 5),
            (element.rect.right - 10, element.rect.centery + 5),
        ]
        pygame.draw.polygon(screen, self.style_manager.get_color("text"), arrow_points)
    
    def _draw_checkbox(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a checkbox element."""
        # Draw checkbox
        color = (
            self.style_manager.get_color("checkbox_checked")
            if element.value
            else self.style_manager.get_color("checkbox")
        )
        pygame.draw.rect(screen, color, element.rect)
        pygame.draw.rect(screen, self.style_manager.get_color("border"), element.rect, 2)
        
        # Draw checkmark if checked
        if element.value:
            check_points = [
                (element.rect.left + 3, element.rect.centery),
                (element.rect.left + 8, element.rect.bottom - 3),
                (element.rect.right - 3, element.rect.top + 3),
            ]
            pygame.draw.lines(screen, self.style_manager.get_color("text"), False, check_points, 2)
        
        # Draw label
        label_font = self.style_manager.get_font("label")
        label_text = label_font.render(element.label, True, self.style_manager.get_color("text"))
        label_rect = label_text.get_rect(
            left=element.rect.right + 10, 
            centery=element.rect.centery
        )
        screen.blit(label_text, label_rect)
    
    def _draw_slider(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a slider element."""
        # Draw label
        label_font = self.style_manager.get_font("label")
        label_text = label_font.render(element.label, True, self.style_manager.get_color("text"))
        label_rect = label_text.get_rect(
            left=element.rect.left, 
            top=element.rect.top - 20
        )
        screen.blit(label_text, label_rect)
        
        # Draw track
        track_rect = pygame.Rect(
            element.rect.x, 
            element.rect.centery - 2, 
            element.rect.width, 
            4
        )
        pygame.draw.rect(screen, self.style_manager.get_color("slider_track"), track_rect)
        
        # Draw handle
        handle_x = element.rect.x + int(element.value * element.rect.width)
        handle_rect = pygame.Rect(handle_x - 8, element.rect.centery - 8, 16, 16)
        pygame.draw.rect(screen, self.style_manager.get_color("slider_handle"), handle_rect)
        pygame.draw.rect(screen, self.style_manager.get_color("border"), handle_rect, 1)
        
        # Draw value
        value_font = self.style_manager.get_font("value")
        value_text = value_font.render(f"{int(element.value * 100)}%", True, self.style_manager.get_color("text"))
        value_rect = value_text.get_rect(
            left=element.rect.right + 10, 
            centery=element.rect.centery
        )
        screen.blit(value_text, value_rect)
    
    def _draw_button(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a button element."""
        # Determine button color based on hover state
        if element.rect.collidepoint(self.mouse_pos):
            color = self.style_manager.get_color("button_hover")
        else:
            color = self.style_manager.get_color("button")
        
        # Draw button background
        pygame.draw.rect(screen, color, element.rect)
        pygame.draw.rect(screen, self.style_manager.get_color("border"), element.rect, 1)
        
        # Draw button label
        label_font = self.style_manager.get_font("label")
        label_text = label_font.render(element.label, True, self.style_manager.get_color("text"))
        label_rect = label_text.get_rect(center=element.rect.center)
        screen.blit(label_text, label_rect)
    
    def _draw_list(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a list element."""
        # Draw list background
        pygame.draw.rect(screen, self.style_manager.get_color("button"), element.rect)
        pygame.draw.rect(screen, self.style_manager.get_color("border"), element.rect, 1)
        
        # Draw label
        label_font = self.style_manager.get_font("label")
        label_text = label_font.render(element.label, True, self.style_manager.get_color("text"))
        label_rect = label_text.get_rect(
            left=element.rect.left, 
            top=element.rect.top - 20
        )
        screen.blit(label_text, label_rect)
        
        # Draw sample items (placeholder - would be populated with actual data)
        value_font = self.style_manager.get_font("value")
        sample_items = [
            "Item 1",
            "Item 2", 
            "Item 3",
        ]
        for i, item_name in enumerate(sample_items[:5]):  # Show max 5 items
            item_y = element.rect.y + 5 + i * 25
            if item_y + 20 < element.rect.bottom:
                item_text = value_font.render(item_name, True, self.style_manager.get_color("text"))
                screen.blit(item_text, (element.rect.x + 5, item_y))
    
    def _draw_label(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a label element."""
        label_font = self.style_manager.get_font("label")
        value_font = self.style_manager.get_font("value")
        
        if element.value:  # If there's a value, draw it next to the label
            value_text = value_font.render(str(element.value), True, self.style_manager.get_color("text"))
            
            # Draw label
            label_text = label_font.render(element.label, True, self.style_manager.get_color("text"))
            label_rect = label_text.get_rect(
                left=element.rect.left, 
                centery=element.rect.centery
            )
            screen.blit(label_text, label_rect)
            
            # Draw value
            value_rect = value_text.get_rect(
                left=label_rect.right + 10, 
                centery=element.rect.centery
            )
            screen.blit(value_text, value_rect)
        else:
            # Draw centered label
            label_text = label_font.render(element.label, True, self.style_manager.get_color("text"))
            label_rect = label_text.get_rect(center=element.rect.center)
            screen.blit(label_text, label_rect)
    
    def draw_tooltip(self, screen: pygame.Surface, text: str, position: Tuple[int, int]) -> None:
        """
        Draw a tooltip at the specified position.
        
        Args:
            screen: Surface to draw on
            text: Tooltip text
            position: Position to draw tooltip
        """
        if not text:
            return
        
        tooltip_font = self.style_manager.get_font("tooltip")
        tooltip_text = tooltip_font.render(text, True, self.style_manager.get_color("text"))
        tooltip_rect = tooltip_text.get_rect()
        
        # Add padding
        padding = 5
        tooltip_rect.width += padding * 2
        tooltip_rect.height += padding * 2
        tooltip_rect.topleft = (position[0] + 10, position[1] + 10)
        
        # Ensure tooltip stays on screen
        if tooltip_rect.right > screen.get_width():
            tooltip_rect.right = screen.get_width() - 10
        if tooltip_rect.bottom > screen.get_height():
            tooltip_rect.bottom = screen.get_height() - 10
        
        # Draw tooltip background and text
        pygame.draw.rect(screen, self.style_manager.get_color("panel"), tooltip_rect)
        pygame.draw.rect(screen, self.style_manager.get_color("border"), tooltip_rect, 1)
        screen.blit(tooltip_text, (tooltip_rect.x + padding, tooltip_rect.y + padding))
