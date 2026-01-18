"""Genome Codec: Encode/decode turtle genetics to compact strings.

The genome string format is designed for efficient transmission and
easy parsing in the JavaScript Paper Doll assembler:

Format: B{body}-S{shell}-P{pattern}-C{hex_color}

Examples:
    B1-S3-P2-CFF00FF  → Body type 1, Shell 3, Pattern 2, Color #FF00FF
    B0-S0-P0-C228B22  → Default green turtle

The codec maps the rich genetics dictionary to this compact format
and vice versa, abstracting the internal genetics structure from
the transport layer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class GenomeCodec:
    """Encode/decode genetics dictionaries to compact genome strings.
    
    Single Responsibility: Translation between genetics dict and wire format.
    """
    
    BODY_PATTERNS = ["solid", "mottled", "speckled", "marbled"]
    SHELL_PATTERNS = ["hex", "spots", "stripes", "rings"]
    LIMB_SHAPES = ["flippers", "feet", "fins"]
    
    @classmethod
    def encode(cls, genetics: dict[str, Any]) -> str:
        """Encode a genetics dictionary to a compact genome string.
        
        Args:
            genetics: Full genetics dictionary from Turtle.visual_genetics
            
        Returns:
            Compact genome string: B{body}-S{shell}-P{pattern}-C{hex_color}
        """
        body_pattern = genetics.get("body_pattern_type", "solid")
        body_idx = cls._safe_index(cls.BODY_PATTERNS, body_pattern, 0)
        
        shell_pattern = genetics.get("shell_pattern_type", "hex")
        shell_idx = cls._safe_index(cls.SHELL_PATTERNS, shell_pattern, 0)
        
        limb_shape = genetics.get("limb_shape", "flippers")
        limb_idx = cls._safe_index(cls.LIMB_SHAPES, limb_shape, 0)
        
        shell_color = genetics.get("shell_base_color", (34, 139, 34))
        hex_color = cls._rgb_to_hex(shell_color)
        
        return f"B{body_idx}-S{shell_idx}-P{limb_idx}-C{hex_color}"
    
    @classmethod
    def decode(cls, genome: str) -> dict[str, Any]:
        """Decode a genome string back to a genetics dictionary.
        
        Args:
            genome: Compact genome string: B{body}-S{shell}-P{pattern}-C{hex_color}
            
        Returns:
            Partial genetics dictionary with decoded values
        """
        parts = genome.split("-")
        result: dict[str, Any] = {}
        
        for part in parts:
            if not part:
                continue
            prefix, value = part[0], part[1:]
            
            if prefix == "B" and value.isdigit():
                idx = int(value)
                if 0 <= idx < len(cls.BODY_PATTERNS):
                    result["body_pattern_type"] = cls.BODY_PATTERNS[idx]
                    
            elif prefix == "S" and value.isdigit():
                idx = int(value)
                if 0 <= idx < len(cls.SHELL_PATTERNS):
                    result["shell_pattern_type"] = cls.SHELL_PATTERNS[idx]
                    
            elif prefix == "P" and value.isdigit():
                idx = int(value)
                if 0 <= idx < len(cls.LIMB_SHAPES):
                    result["limb_shape"] = cls.LIMB_SHAPES[idx]
                    
            elif prefix == "C" and len(value) == 6:
                result["shell_base_color"] = cls._hex_to_rgb(value)
        
        return result
    
    @staticmethod
    def _safe_index(items: list[str], value: str, default: int) -> int:
        """Get index of value in list, returning default if not found."""
        try:
            return items.index(value)
        except ValueError:
            return default
    
    @staticmethod
    def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex string without # prefix."""
        r, g, b = rgb
        return f"{r:02X}{g:02X}{b:02X}"
    
    @staticmethod
    def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
        """Convert hex string to RGB tuple."""
        hex_str = hex_str.lstrip("#")
        return (
            int(hex_str[0:2], 16),
            int(hex_str[2:4], 16),
            int(hex_str[4:6], 16),
        )
