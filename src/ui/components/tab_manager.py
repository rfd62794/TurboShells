"""
Tab management component for settings interface.

Handles tab state, navigation, and organization following SRP principles.
"""

from typing import Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass
import pygame

from core.logging_config import get_logger


class SettingsTab(Enum):
    """Settings tabs enumeration."""
    GRAPHICS = "graphics"
    AUDIO = "audio"
    CONTROLS = "controls"
    GAMEPLAY = "gameplay"
    PROFILE = "profile"
    APPEARANCE = "appearance"
    SYSTEM = "system"


@dataclass
class TabConfig:
    """Configuration for a single tab."""
    tab_id: SettingsTab
    label: str
    tooltip: str = ""
    enabled: bool = True


@dataclass
class TabElement:
    """UI element representing a tab."""
    rect: pygame.Rect
    config: TabConfig
    callback: Callable


class TabManager:
    """
    Manages tab navigation and state for the settings interface.
    
    Single responsibility: Handle tab-related logic only.
    """
    
    def __init__(self, tab_bar_rect: pygame.Rect):
        """
        Initialize tab manager.
        
        Args:
            tab_bar_rect: Rectangle area for tab bar
        """
        self.tab_bar_rect = tab_bar_rect
        self.logger = get_logger(__name__)
        
        # Tab state
        self.active_tab: SettingsTab = SettingsTab.GRAPHICS
        self.tabs: Dict[SettingsTab, TabElement] = {}
        self.tab_configs: List[TabConfig] = []
        
        # Tab layout
        self.tab_spacing = 5
        self.min_tab_width = 100
        self.max_tab_width = 120
        
        # Initialize default tabs
        self._initialize_default_tabs()
        self._calculate_tab_layout()
        
        self.logger.debug("TabManager initialized")
    
    def _initialize_default_tabs(self) -> None:
        """Initialize default tab configurations."""
        self.tab_configs = [
            TabConfig(
                tab_id=SettingsTab.GRAPHICS,
                label="Graphics",
                tooltip="Graphics and display settings"
            ),
            TabConfig(
                tab_id=SettingsTab.AUDIO,
                label="Audio",
                tooltip="Audio and sound settings"
            ),
            TabConfig(
                tab_id=SettingsTab.CONTROLS,
                label="Controls",
                tooltip="Control and input settings"
            ),
            TabConfig(
                tab_id=SettingsTab.GAMEPLAY,
                label="Gameplay",
                tooltip="Gameplay and difficulty settings"
            ),
            TabConfig(
                tab_id=SettingsTab.PROFILE,
                label="Profile",
                tooltip="User profile settings"
            ),
            TabConfig(
                tab_id=SettingsTab.APPEARANCE,
                label="Appearance",
                tooltip="UI appearance settings"
            ),
            TabConfig(
                tab_id=SettingsTab.SYSTEM,
                label="System",
                tooltip="System and privacy settings"
            ),
        ]
    
    def _calculate_tab_layout(self) -> None:
        """Calculate tab positions and create tab elements."""
        num_tabs = len(self.tab_configs)
        if num_tabs == 0:
            return
        
        # Calculate available width
        available_width = self.tab_bar_rect.width - 20  # Leave padding
        
        # Calculate optimal tab width
        tab_width = (available_width - (num_tabs - 1) * self.tab_spacing) // num_tabs
        tab_width = max(self.min_tab_width, min(tab_width, self.max_tab_width))
        
        tab_height = 35
        
        # Create tab elements
        for i, config in enumerate(self.tab_configs):
            x = self.tab_bar_rect.x + 10 + i * (tab_width + self.tab_spacing)
            y = self.tab_bar_rect.y
            
            rect = pygame.Rect(x, y, tab_width, tab_height)
            
            self.tabs[config.tab_id] = TabElement(
                rect=rect,
                config=config,
                callback=lambda t=config.tab_id: self.switch_to_tab(t)
            )
    
    def switch_to_tab(self, tab_id: SettingsTab) -> bool:
        """
        Switch to a specific tab.
        
        Args:
            tab_id: Target tab to switch to
            
        Returns:
            True if tab was switched, False if tab doesn't exist or is disabled
        """
        if tab_id not in self.tabs:
            self.logger.warning(f"Tab {tab_id.value} not found")
            return False
        
        tab_element = self.tabs[tab_id]
        if not tab_element.config.enabled:
            self.logger.warning(f"Tab {tab_id.value} is disabled")
            return False
        
        old_tab = self.active_tab
        self.active_tab = tab_id
        
        self.logger.debug(f"Switched from {old_tab.value} to {tab_id.value}")
        return True
    
    def get_active_tab(self) -> SettingsTab:
        """Get the currently active tab."""
        return self.active_tab
    
    def get_tab_element(self, tab_id: SettingsTab) -> Optional[TabElement]:
        """Get tab element by ID."""
        return self.tabs.get(tab_id)
    
    def get_all_tab_elements(self) -> List[TabElement]:
        """Get all tab elements."""
        return list(self.tabs.values())
    
    def get_enabled_tabs(self) -> List[TabElement]:
        """Get all enabled tab elements."""
        return [tab for tab in self.tabs.values() if tab.config.enabled]
    
    def enable_tab(self, tab_id: SettingsTab, enabled: bool = True) -> None:
        """
        Enable or disable a tab.
        
        Args:
            tab_id: Tab to enable/disable
            enabled: True to enable, False to disable
        """
        if tab_id in self.tabs:
            self.tabs[tab_id].config.enabled = enabled
            self.logger.debug(f"Tab {tab_id.value} {'enabled' if enabled else 'disabled'}")
    
    def set_tab_tooltip(self, tab_id: SettingsTab, tooltip: str) -> None:
        """
        Set tooltip for a tab.
        
        Args:
            tab_id: Tab to set tooltip for
            tooltip: Tooltip text
        """
        if tab_id in self.tabs:
            self.tabs[tab_id].config.tooltip = tooltip
    
    def update_layout(self, new_tab_bar_rect: pygame.Rect) -> None:
        """
        Update tab layout for new tab bar dimensions.
        
        Args:
            new_tab_bar_rect: New tab bar rectangle
        """
        self.tab_bar_rect = new_tab_bar_rect
        self._calculate_tab_layout()
        self.logger.debug("Tab layout updated")
    
    def handle_click(self, mouse_pos: tuple) -> Optional[SettingsTab]:
        """
        Handle mouse click on tabs.
        
        Args:
            mouse_pos: Mouse click position
            
        Returns:
            Clicked tab ID, or None if no tab was clicked
        """
        for tab_id, tab_element in self.tabs.items():
            if tab_element.rect.collidepoint(mouse_pos):
                if tab_element.config.enabled:
                    return tab_id
                else:
                    self.logger.debug(f"Clicked on disabled tab {tab_id.value}")
                    return None
        
        return None
    
    def get_tab_at_position(self, position: tuple) -> Optional[SettingsTab]:
        """
        Get tab ID at specific position.
        
        Args:
            position: Position to check
            
        Returns:
            Tab ID at position, or None if no tab at position
        """
        for tab_id, tab_element in self.tabs.items():
            if tab_element.rect.collidepoint(position):
                return tab_id
        
        return None
    
    def is_tab_active(self, tab_id: SettingsTab) -> bool:
        """
        Check if a tab is currently active.
        
        Args:
            tab_id: Tab to check
            
        Returns:
            True if tab is active, False otherwise
        """
        return self.active_tab == tab_id
    
    def get_tab_count(self) -> int:
        """Get total number of tabs."""
        return len(self.tabs)
    
    def get_enabled_tab_count(self) -> int:
        """Get number of enabled tabs."""
        return len(self.get_enabled_tabs())
    
    def reset_to_default(self) -> None:
        """Reset tab manager to default state."""
        self.active_tab = SettingsTab.GRAPHICS
        self._initialize_default_tabs()
        self._calculate_tab_layout()
        self.logger.debug("TabManager reset to default")
