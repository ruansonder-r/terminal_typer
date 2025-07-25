import json
from typing import List, Set, Optional
from wpm_calculator import WPMCalculator

class KeyboardRenderer:
    """
    Renders ASCII art representations of split ergonomic keyboards.
    Supports key highlighting and WPM display integration.
    """
    
    def __init__(self, visual_style: str = "reverse"):
        """
        Initialize the keyboard renderer.
        
        Args:
            visual_style: Style for pressed key highlighting (only "reverse" supported)
        """
        self.visual_style = "reverse"  # Only reverse video mode supported
        self.pressed_keys: Set[str] = set()
        self.wpm_calculator: Optional[WPMCalculator] = None
        
        # Key display mapping for ZMK key names to display characters
        self.key_display_map = {
            # Letters
            'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G', 'H': 'H', 'I': 'I', 'J': 'J',
            'K': 'K', 'L': 'L', 'M': 'M', 'N': 'N', 'O': 'O', 'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S', 'T': 'T',
            'U': 'U', 'V': 'V', 'W': 'W', 'X': 'X', 'Y': 'Y', 'Z': 'Z',
            
            # Numbers
            'N0': '0', 'N1': '1', 'N2': '2', 'N3': '3', 'N4': '4', 'N5': '5', 'N6': '6', 'N7': '7', 'N8': '8', 'N9': '9',
            
            # Symbols
            'COMMA': ',', 'DOT': '.', 'SLASH': '/', 'SEMI': ';', 'QUOTE': "'", 'LBRC': '[', 'RBRC': ']', 'BSLH': '\\',
            'EQUAL': '=', 'MINUS': '-', 'GRAVE': '`', 'TILDE': '~', 'EXCL': '!', 'AT': '@', 'HASH': '#', 'DLR': '$',
            'PRCNT': '%', 'CIRC': '^', 'AMPS': '&', 'STAR': '*', 'LPAR': '(', 'RPAR': ')', 'UNDS': '_', 'PLUS': '+',
            'LCBR': '{', 'RCBR': '}', 'PIPE': '|', 'LABK': '<', 'RABK': '>', 'QUES': '?', 'COLN': ':', 'DQUO': '"',
            
            # Modifiers
            'LCTRL': 'CTL', 'RCTRL': 'CTL', 'LALT': 'ALT', 'RALT': 'ALT', 'LGUI': 'GUI', 'RGUI': 'GUI',
            'LSHFT': 'SFT', 'RSHFT': 'SFT', 'LCTL': 'CTL', 'RCTL': 'CTL',
            
            # Special keys
            'SPACE': 'SPC', 'ENTER': 'ENT', 'ESCAPE': 'ESC', 'TAB': 'TAB', 'BACKSPACE': 'BSP', 'DELETE': 'DEL',
            'RETURN': 'ENT', 'ESC': 'ESC', 'TAB': 'TAB', 'BSPC': 'BSP', 'DEL': 'DEL',
            
            # Layer keys
            'mo(1)': 'LWR', 'mo(2)': 'RSE', 'mo(3)': 'L3', 'mo(4)': 'L4', 'mo(5)': 'L5',
            'to(1)': 'LWR', 'to(2)': 'RSE', 'to(3)': 'L3', 'to(4)': 'L4', 'to(5)': 'L5',
            'tg(1)': 'LWR', 'tg(2)': 'RSE', 'tg(3)': 'L3', 'tg(4)': 'L4', 'tg(5)': 'L5',
            
            # Function keys
            'F1': 'F1', 'F2': 'F2', 'F3': 'F3', 'F4': 'F4', 'F5': 'F5', 'F6': 'F6',
            'F7': 'F7', 'F8': 'F8', 'F9': 'F9', 'F10': 'F10', 'F11': 'F11', 'F12': 'F12',
            
            # Navigation
            'UP': 'UP', 'DOWN': 'DN', 'LEFT': 'LT', 'RIGHT': 'RT', 'HOME': 'HM', 'END': 'END',
            'PGUP': 'PU', 'PGDN': 'PD', 'INS': 'INS',
            
            # Media keys
            'MUTE': 'MUT', 'VOLU': 'V+', 'VOLD': 'V-', 'NEXT': 'NXT', 'PREV': 'PRV', 'PLAY': 'PLY', 'STOP': 'STP',
            
            # Default for unknown keys
            'DEFAULT': 'KEY'
        }
    
    def set_pressed_keys(self, pressed_keys: Set[str]) -> None:
        """Set the currently pressed keys."""
        self.pressed_keys = pressed_keys
    
    def set_wpm_calculator(self, wpm_calculator: WPMCalculator) -> None:
        """Set the WPM calculator for display integration."""
        self.wpm_calculator = wpm_calculator
    
    def get_key_display(self, key: str) -> str:
        """Get the display character for a key."""
        return self.key_display_map.get(key, key[:3].upper())
    
    def render_keyboard(self, layer_keys: List[List[str]], layer_name: str = "") -> str:
        """
        Render the keyboard layout as ASCII art.
        
        Args:
            layer_keys: List of key rows for the current layer
            layer_name: Name of the current layer (unused, kept for compatibility)
            
        Returns:
            ASCII art representation of the keyboard
        """
        if not layer_keys or len(layer_keys) < 3:
            return "No keys to render"
        
        lines = []
        
        # Split into left and right halves (assuming 6 columns per half)
        left_half = []
        right_half = []
        
        for row in layer_keys:
            if len(row) >= 12:  # Full row with both halves
                left_half.append(row[:6])
                right_half.append(row[6:12])
            else:  # Partial row, pad with empty strings
                left_pad = [''] * (6 - len(row))
                left_half.append(row + left_pad)
                right_half.append([''] * 6)
        
        # Render main rows (excluding thumb row)
        for i, (left_row, right_row) in enumerate(zip(left_half[:-1], right_half[:-1])):
            left_keys = [self._format_pressed_key(self.get_key_display(key)) if key in self.pressed_keys else self._format_normal_key(self.get_key_display(key)) for key in left_row]
            right_keys = [self._format_pressed_key(self.get_key_display(key)) if key in self.pressed_keys else self._format_normal_key(self.get_key_display(key)) for key in right_row]
            
            left_str = " ".join(left_keys)
            right_str = " ".join(right_keys)
            
            left_indent = " " * (i * 2)
            right_indent = " " * (-1*i * 2)
            
            if self.wpm_calculator and i == 1:
                wpm_display = self.wpm_calculator.get_wpm_display()
                adjusted_right_indent = " " * max(0, (2 - i*4) * 2)
                center_line = f"{left_indent}{left_str} {wpm_display} {adjusted_right_indent}{right_str}"
            else:
                base_spacing = "         "
                adjusted_right_indent = " " * max(0, (4 - i*2) * 2)
                center_line = f"{left_indent}{left_str}{base_spacing}{adjusted_right_indent}{right_str}"
            
            lines.append(center_line)
        
        # Render thumb row (last row)
        if len(layer_keys) >= 4:
            thumb_row = layer_keys[-1]
            if len(thumb_row) >= 6:
                left_thumb = thumb_row[:3]
                right_thumb = thumb_row[3:6]
                
                left_thumb_keys = [self._format_pressed_key(self.get_key_display(key)) if key in self.pressed_keys else self._format_normal_key(self.get_key_display(key)) for key in left_thumb]
                right_thumb_keys = [self._format_pressed_key(self.get_key_display(key)) if key in self.pressed_keys else self._format_normal_key(self.get_key_display(key)) for key in right_thumb]
                
                left_thumb_str = " ".join(left_thumb_keys)
                right_thumb_str = " ".join(right_thumb_keys)
                
                # Center the thumb row with proper spacing to align with main rows
                thumb_indent = " " * 24
                thumb_spacing = "     "  # 16 spaces to match main rows
                thumb_line = f"{thumb_indent}{left_thumb_str}{thumb_spacing}{right_thumb_str}"
                lines.append(thumb_line)
        
        return "\n".join(lines)
    
    def _format_pressed_key(self, display: str) -> str:
        """Format a pressed key with reverse video highlighting."""
        return f"REV[{display:^3}]REV"
    
    def _format_normal_key(self, display: str) -> str:
        """Format a normal key."""
        return f"[{display:^3}]" 
