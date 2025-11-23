"""
Centralized styling system for UI components.

This module provides a comprehensive styling system that enables consistent
theming, centralized color management, and font handling across all UI components.
"""

import pygame
from typing import Dict, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import os
import json


class ColorScheme(Enum):
    """Predefined color schemes."""
    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    HIGH_CONTRAST = "high_contrast"
    COLORBLIND_FRIENDLY = "colorblind_friendly"


class FontSize(Enum):
    """Standard font sizes."""
    TITLE = 24
    LARGE = 18
    NORMAL = 14
    SMALL = 12
    TINY = 10


@dataclass
class ColorPalette:
    """Color palette for a theme."""
    # Background colors
    background: Tuple[int, int, int] = (40, 40, 40)
    panel: Tuple[int, int, int] = (60, 60, 60)
    surface: Tuple[int, int, int] = (80, 80, 80)
    
    # Text colors
    text: Tuple[int, int, int] = (255, 255, 255)
    text_disabled: Tuple[int, int, int] = (150, 150, 150)
    text_placeholder: Tuple[int, int, int] = (120, 120, 120)
    
    # Border colors
    border: Tuple[int, int, int] = (100, 100, 100)
    border_active: Tuple[int, int, int] = (150, 150, 150)
    border_disabled: Tuple[int, int, int] = (70, 70, 70)
    
    # Button colors
    button: Tuple[int, int, int] = (80, 80, 80)
    button_hover: Tuple[int, int, int] = (100, 100, 100)
    button_active: Tuple[int, int, int] = (120, 120, 120)
    button_disabled: Tuple[int, int, int] = (60, 60, 60)
    
    # Tab colors
    tab: Tuple[int, int, int] = (70, 70, 70)
    tab_active: Tuple[int, int, int] = (90, 90, 90)
    tab_hover: Tuple[int, int, int] = (80, 80, 80)
    
    # Accent colors
    accent: Tuple[int, int, int] = (100, 150, 200)
    accent_hover: Tuple[int, int, int] = (120, 170, 220)
    accent_active: Tuple[int, int, int] = (80, 130, 180)
    
    # Status colors
    success: Tuple[int, int, int] = (100, 200, 100)
    warning: Tuple[int, int, int] = (200, 200, 100)
    error: Tuple[int, int, int] = (200, 100, 100)
    info: Tuple[int, int, int] = (100, 150, 200)
    
    # Interactive colors
    checkbox: Tuple[int, int, int] = (80, 80, 80)
    checkbox_checked: Tuple[int, int, int] = (100, 150, 200)
    slider_track: Tuple[int, int, int] = (50, 50, 50)
    slider_handle: Tuple[int, int, int] = (120, 120, 120)
    
    # Focus colors
    focus_ring: Tuple[int, int, int] = (150, 200, 250)
    focus_outline: Tuple[int, int, int] = (100, 150, 200)


@dataclass
class FontSet:
    """Font set for different text types."""
    title: pygame.font.Font
    large: pygame.font.Font
    normal: pygame.font.Font
    small: pygame.font.Font
    tiny: pygame.font.Font
    
    @classmethod
    def create_default(cls) -> 'FontSet':
        """Create default font set."""
        return cls(
            title=pygame.font.Font(None, FontSize.TITLE.value),
            large=pygame.font.Font(None, FontSize.LARGE.value),
            normal=pygame.font.Font(None, FontSize.NORMAL.value),
            small=pygame.font.Font(None, FontSize.SMALL.value),
            tiny=pygame.font.Font(None, FontSize.TINY.value)
        )
    
    @classmethod
    def create_from_system(cls, font_name: str = "Arial") -> 'FontSet':
        """Create font set from system font."""
        return cls(
            title=pygame.font.SysFont(font_name, FontSize.TITLE.value),
            large=pygame.font.SysFont(font_name, FontSize.LARGE.value),
            normal=pygame.font.SysFont(font_name, FontSize.NORMAL.value),
            small=pygame.font.SysFont(font_name, FontSize.SMALL.value),
            tiny=pygame.font.SysFont(font_name, FontSize.TINY.value)
        )


@dataclass
class Style:
    """
    Complete style definition for UI components.
    
    This class encapsulates all styling information needed by UI components,
    including colors, fonts, sizes, and visual properties.
    """
    colors: ColorPalette = field(default_factory=ColorPalette)
    fonts: FontSet = field(default_factory=FontSet.create_default)
    
    # Sizes and spacing
    border_width: int = 1
    corner_radius: int = 4
    padding: int = 10
    spacing: int = 5
    
    # Animation settings
    transition_duration: float = 0.2
    animation_enabled: bool = True
    
    # Accessibility settings
    high_contrast: bool = False
    large_text: bool = False
    reduced_motion: bool = False
    
    # Theme metadata
    theme_name: str = "default"
    version: str = "1.0"
    
    def get_color(self, color_name: str, state: str = "normal") -> Tuple[int, int, int]:
        """
        Get color by name and state.
        
        Args:
            color_name: Name of the color (e.g., "button", "text")
            state: State ("normal", "hover", "active", "disabled")
            
        Returns:
            RGB color tuple
        """
        base_color = getattr(self.colors, color_name, (255, 255, 255))
        
        # Apply state modifications
        if state == "hover":
            return self._lighten_color(base_color, 20)
        elif state == "active":
            return self._lighten_color(base_color, 40)
        elif state == "disabled":
            return self._darken_color(base_color, 30)
        
        return base_color
    
    def get_font(self, size: Union[FontSize, str]) -> pygame.font.Font:
        """
        Get font by size.
        
        Args:
            size: Font size enum or string name
            
        Returns:
            Pygame font object
        """
        if isinstance(size, str):
            size_map = {
                "title": FontSize.TITLE,
                "large": FontSize.LARGE,
                "normal": FontSize.NORMAL,
                "small": FontSize.SMALL,
                "tiny": FontSize.TINY
            }
            size = size_map.get(size.lower(), FontSize.NORMAL)
        
        font_map = {
            FontSize.TITLE: self.fonts.title,
            FontSize.LARGE: self.fonts.large,
            FontSize.NORMAL: self.fonts.normal,
            FontSize.SMALL: self.fonts.small,
            FontSize.TINY: self.fonts.tiny
        }
        
        font = font_map.get(size, self.fonts.normal)
        
        # Apply large text accessibility setting
        if self.large_text and size in [FontSize.SMALL, FontSize.TINY]:
            return font_map[FontSize.NORMAL]
        
        return font
    
    def apply_accessibility_overrides(self) -> None:
        """Apply accessibility overrides to style."""
        if self.high_contrast:
            self._apply_high_contrast()
        
        if self.large_text:
            self._apply_large_text()
        
        if self.reduced_motion:
            self.transition_duration = 0.0
            self.animation_enabled = False
    
    def _apply_high_contrast(self) -> None:
        """Apply high contrast mode."""
        self.colors.background = (0, 0, 0)
        self.colors.panel = (20, 20, 20)
        self.colors.text = (255, 255, 255)
        self.colors.border = (255, 255, 255)
        self.colors.focus_ring = (255, 255, 0)
    
    def _apply_large_text(self) -> None:
        """Apply large text mode."""
        self.fonts = FontSet.create_from_system()
        self.fonts.title = pygame.font.Font(None, FontSize.TITLE.value + 4)
        self.fonts.large = pygame.font.Font(None, FontSize.LARGE.value + 4)
        self.fonts.normal = pygame.font.Font(None, FontSize.NORMAL.value + 2)
        self.fonts.small = pygame.font.Font(None, FontSize.NORMAL.value)
        self.fonts.tiny = pygame.font.Font(None, FontSize.SMALL.value)
    
    def _lighten_color(self, color: Tuple[int, int, int], amount: int) -> Tuple[int, int, int]:
        """Lighten a color by the given amount."""
        return tuple(min(255, c + amount) for c in color)
    
    def _darken_color(self, color: Tuple[int, int, int], amount: int) -> Tuple[int, int, int]:
        """Darken a color by the given amount."""
        return tuple(max(0, c - amount) for c in color)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert style to dictionary for serialization."""
        return {
            "theme_name": self.theme_name,
            "version": self.version,
            "colors": {
                "background": self.colors.background,
                "panel": self.colors.panel,
                "surface": self.colors.surface,
                "text": self.colors.text,
                "text_disabled": self.colors.text_disabled,
                "border": self.colors.border,
                "border_active": self.colors.border_active,
                "button": self.colors.button,
                "button_hover": self.colors.button_hover,
                "button_active": self.colors.button_active,
                "tab": self.colors.tab,
                "tab_active": self.colors.tab_active,
                "accent": self.colors.accent,
                "success": self.colors.success,
                "warning": self.colors.warning,
                "error": self.colors.error,
                "checkbox": self.colors.checkbox,
                "checkbox_checked": self.colors.checkbox_checked,
                "focus_ring": self.colors.focus_ring,
            },
            "sizes": {
                "border_width": self.border_width,
                "corner_radius": self.corner_radius,
                "padding": self.padding,
                "spacing": self.spacing,
            },
            "accessibility": {
                "high_contrast": self.high_contrast,
                "large_text": self.large_text,
                "reduced_motion": self.reduced_motion,
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Style':
        """Create style from dictionary."""
        colors = ColorPalette()
        if "colors" in data:
            for key, value in data["colors"].items():
                if hasattr(colors, key):
                    setattr(colors, key, tuple(value))
        
        style = cls(colors=colors)
        
        if "sizes" in data:
            for key, value in data["sizes"].items():
                if hasattr(style, key):
                    setattr(style, key, value)
        
        if "accessibility" in data:
            for key, value in data["accessibility"].items():
                if hasattr(style, key):
                    setattr(style, key, value)
        
        if "theme_name" in data:
            style.theme_name = data["theme_name"]
        
        if "version" in data:
            style.version = data["version"]
        
        return style


class StyleManager:
    """
    Centralized style management system.
    
    This class manages style creation, theme switching, and provides
    a singleton interface for accessing styles throughout the application.
    """
    
    _instance: Optional['StyleManager'] = None
    
    def __init__(self):
        self._current_style: Optional[Style] = None
        self._style_cache: Dict[str, Style] = {}
        self._theme_configs: Dict[str, Dict[str, Any]] = {}
        self._load_builtin_themes()
    
    @classmethod
    def instance(cls) -> 'StyleManager':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = StyleManager()
        return cls._instance
    
    def get_default(self) -> Style:
        """Get default style."""
        if self._current_style is None:
            self._current_style = self.create_style("default")
        return self._current_style
    
    def create_style(self, theme_name: str) -> Style:
        """
        Create style by theme name.
        
        Args:
            theme_name: Name of the theme to create
            
        Returns:
            Style instance
        """
        if theme_name in self._style_cache:
            return self._style_cache[theme_name]
        
        if theme_name in self._theme_configs:
            style = Style.from_dict(self._theme_configs[theme_name])
            style.theme_name = theme_name
        else:
            style = Style()
            style.theme_name = theme_name
        
        # Apply accessibility overrides
        style.apply_accessibility_overrides()
        
        self._style_cache[theme_name] = style
        return style
    
    def set_current_theme(self, theme_name: str) -> None:
        """
        Set current theme.
        
        Args:
            theme_name: Name of the theme to set as current
        """
        self._current_style = self.create_style(theme_name)
    
    def register_theme(self, theme_name: str, theme_config: Dict[str, Any]) -> None:
        """
        Register a custom theme.
        
        Args:
            theme_name: Name of the theme
            theme_config: Theme configuration dictionary
        """
        self._theme_configs[theme_name] = theme_config
        # Clear cache to force regeneration
        if theme_name in self._style_cache:
            del self._style_cache[theme_name]
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        return list(self._theme_configs.keys())
    
    def _load_builtin_themes(self) -> None:
        """Load built-in theme configurations."""
        
        # Default theme
        self._theme_configs["default"] = Style().to_dict()
        
        # Dark theme
        self._theme_configs["dark"] = {
            "theme_name": "dark",
            "colors": {
                "background": (20, 20, 20),
                "panel": (30, 30, 30),
                "surface": (40, 40, 40),
                "text": (240, 240, 240),
                "text_disabled": (120, 120, 120),
                "border": (80, 80, 80),
                "border_active": (120, 120, 120),
                "button": (50, 50, 50),
                "button_hover": (70, 70, 70),
                "button_active": (90, 90, 90),
                "tab": (40, 40, 40),
                "tab_active": (60, 60, 60),
                "accent": (100, 150, 200),
                "success": (80, 180, 80),
                "warning": (180, 180, 80),
                "error": (180, 80, 80),
                "focus_ring": (120, 170, 220),
            }
        }
        
        # Light theme
        self._theme_configs["light"] = {
            "theme_name": "light",
            "colors": {
                "background": (240, 240, 240),
                "panel": (255, 255, 255),
                "surface": (230, 230, 230),
                "text": (20, 20, 20),
                "text_disabled": (120, 120, 120),
                "border": (150, 150, 150),
                "border_active": (100, 100, 100),
                "button": (200, 200, 200),
                "button_hover": (180, 180, 180),
                "button_active": (160, 160, 160),
                "tab": (220, 220, 220),
                "tab_active": (190, 190, 190),
                "accent": (50, 100, 150),
                "success": (50, 150, 50),
                "warning": (150, 150, 50),
                "error": (150, 50, 50),
                "focus_ring": (70, 120, 170),
            }
        }
        
        # High contrast theme
        self._theme_configs["high_contrast"] = {
            "theme_name": "high_contrast",
            "colors": {
                "background": (0, 0, 0),
                "panel": (0, 0, 0),
                "surface": (0, 0, 0),
                "text": (255, 255, 255),
                "text_disabled": (128, 128, 128),
                "border": (255, 255, 255),
                "border_active": (255, 255, 255),
                "button": (0, 0, 0),
                "button_hover": (32, 32, 32),
                "button_active": (64, 64, 64),
                "tab": (0, 0, 0),
                "tab_active": (32, 32, 32),
                "accent": (255, 255, 0),
                "success": (0, 255, 0),
                "warning": (255, 255, 0),
                "error": (255, 0, 0),
                "focus_ring": (255, 255, 0),
            },
            "accessibility": {
                "high_contrast": True,
                "large_text": True,
            }
        }
        
        # Colorblind friendly theme
        self._theme_configs["colorblind_friendly"] = {
            "theme_name": "colorblind_friendly",
            "colors": {
                "background": (40, 40, 40),
                "panel": (60, 60, 60),
                "surface": (80, 80, 80),
                "text": (240, 240, 240),
                "text_disabled": (120, 120, 120),
                "border": (140, 140, 140),
                "border_active": (180, 180, 180),
                "button": (80, 80, 80),
                "button_hover": (100, 100, 100),
                "button_active": (120, 120, 120),
                "tab": (70, 70, 70),
                "tab_active": (90, 90, 90),
                "accent": (255, 179, 0),  # Orange instead of blue
                "success": (0, 158, 115),  # Bluish green
                "warning": (255, 179, 0),  # Orange
                "error": (213, 94, 0),  # Red-orange
                "focus_ring": (255, 179, 0),
            }
        }
    
    def load_theme_from_file(self, file_path: str) -> None:
        """
        Load theme from JSON file.
        
        Args:
            file_path: Path to theme JSON file
        """
        try:
            with open(file_path, 'r') as f:
                theme_config = json.load(f)
            
            theme_name = theme_config.get("theme_name", os.path.basename(file_path).replace(".json", ""))
            self.register_theme(theme_name, theme_config)
            
        except Exception as e:
            print(f"Failed to load theme from {file_path}: {e}")
    
    def save_theme_to_file(self, theme_name: str, file_path: str) -> None:
        """
        Save theme to JSON file.
        
        Args:
            theme_name: Name of theme to save
            file_path: Path to save theme JSON file
        """
        try:
            style = self.create_style(theme_name)
            theme_config = style.to_dict()
            
            with open(file_path, 'w') as f:
                json.dump(theme_config, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save theme {theme_name} to {file_path}: {e}")


# Convenience functions for backward compatibility
def get_default_style() -> Style:
    """Get default style instance."""
    return StyleManager.instance().get_default()


def create_style(theme_name: str) -> Style:
    """Create style by theme name."""
    return StyleManager.instance().create_style(theme_name)


def set_current_theme(theme_name: str) -> None:
    """Set current theme."""
    StyleManager.instance().set_current_theme(theme_name)


def get_available_themes() -> List[str]:
    """Get list of available themes."""
    return StyleManager.instance().get_available_themes()
