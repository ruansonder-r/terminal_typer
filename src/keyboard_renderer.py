from typing import Dict, List, Set, Optional

class KeyboardRenderer:
    """
    Renders bracket-style ASCII art representations of split ergonomic keyboards.
    Handles the visual layout and key highlighting.
    """
    
    def __init__(self, visual_style: str = "bold"):
        """
        Initialize the keyboard renderer.
        
        Args:
            visual_style: Style for pressed key highlighting
                - "bold": **key** (current style)
                - "reverse": [key] with reverse video
                - "brackets": <key> instead of [key]
                - "symbols": [★key★] with symbols
                - "exclamation": [!key!] with exclamation marks
                - "hash": [#key#] with hash symbols
        """
        self.visual_style = visual_style
        
        # Key name to display character mapping
        self.key_display_map = {
            # Letters
            'Q': 'Q', 'W': 'W', 'E': 'E', 'R': 'R', 'T': 'T', 'Y': 'Y', 'U': 'U', 'I': 'I', 'O': 'O', 'P': 'P',
            'A': 'A', 'S': 'S', 'D': 'D', 'F': 'F', 'G': 'G', 'H': 'H', 'J': 'J', 'K': 'K', 'L': 'L',
            'Z': 'Z', 'X': 'X', 'C': 'C', 'V': 'V', 'B': 'B', 'N': 'N', 'M': 'M',
            
            # Numbers
            'N1': '1', 'N2': '2', 'N3': '3', 'N4': '4', 'N5': '5', 'N6': '6', 'N7': '7', 'N8': '8', 'N9': '9', 'N0': '0',
            
            # Symbols
            'EXCL': '!', 'AT': '@', 'HASH': '#', 'DLLR': '$', 'PRCNT': '%', 'CARET': '^', 'AMPS': '&', 'ASTRK': '*',
            'LPAR': '(', 'RPAR': ')', 'MINUS': '-', 'EQUAL': '=', 'LBKT': '[', 'RBKT': ']', 'BSLH': '\\',
            'LBRC': '{', 'RBRC': '}', 'PIPE': '|', 'TILDE': '~', 'GRAVE': '`', 'UNDER': '_', 'PLUS': '+',
            'SEMI': ';', 'SQT': "'", 'COMMA': ',', 'DOT': '.', 'FSLH': '/',
            
            # Special keys
            'TAB': 'TAB', 'BSPC': 'BSP', 'RET': 'ENT', 'ESC': 'ESC', 'SPACE': 'SPC',
            'LCTRL': 'CTL', 'LSHFT': 'SFT', 'LEFT_GUI': 'GUI', 'LGUI': 'GUI', 'RALT': 'ALT',
            
            # Layer keys
            'mo(1)': 'LWR', 'mo(2)': 'RSE',
            
            # Media keys
            'C_PREV': 'PREV', 'C_PLAY_PAUSE': 'PLAY', 'C_NEXT': 'NEXT', 'C_VOLUME_UP': 'VOL+', 'C_VOL_DN': 'VOL-', 'C_MUTE': 'MUTE',
            
            # Navigation
            'LEFT': 'LFT', 'DOWN': 'DWN', 'UP': 'UP', 'RIGHT': 'RGT', 'HOME': 'HOME', 'END': 'END',
            'SCRL_LEFT': 'SL', 'SCRL_UP': 'SU', 'SCRL_RIGHT': 'SR', 'SCRL_DOWN': 'SD',
            
            # Bluetooth
            'BT_CLR': 'BTCLR', 'BT_SEL_0': 'BT1', 'BT_SEL_1': 'BT2', 'BT_SEL_2': 'BT3', 'BT_SEL_3': 'BT4', 'BT_SEL_4': 'BT5',
            
            # Other
            'DEL': 'DEL', 'trans': '   '  # Transparent keys show as empty
        }
        
        # Currently pressed keys
        self.pressed_keys: Set[str] = set()
        
        # WPM calculator (optional)
        self.wpm_calculator = None
    
    def set_visual_style(self, style: str) -> None:
        """
        Set the visual style for pressed key highlighting.
        
        Args:
            style: Visual style name
        """
        self.visual_style = style
    
    def _format_pressed_key(self, display: str) -> str:
        """
        Format a pressed key according to the current visual style.
        
        Args:
            display: Key display text
            
        Returns:
            Formatted key string
        """
        if self.visual_style == "bold":
            return f"**[{display:^3}]**"
        elif self.visual_style == "reverse":
            return f"REV[{display:^3}]REV"  # Will be processed by terminal interface
        elif self.visual_style == "brackets":
            return f"<{display:^3}>"
        elif self.visual_style == "symbols":
            return f"[★{display:^3}★]"
        elif self.visual_style == "exclamation":
            return f"[!{display:^3}!]"
        elif self.visual_style == "hash":
            return f"[#{display:^3}#]"
        elif self.visual_style == "arrows":
            return f"[▶{display:^3}◀]"
        elif self.visual_style == "stars":
            return f"[*{display:^3}*]"
        else:
            return f"**[{display:^3}]**"  # Default to bold
    
    def _format_normal_key(self, display: str) -> str:
        """
        Format a normal (not pressed) key.
        
        Args:
            display: Key display text
            
        Returns:
            Formatted key string
        """
        return f"[{display:^3}]"
    
    def set_wpm_calculator(self, wpm_calculator) -> None:
        """
        Set the WPM calculator for display.
        
        Args:
            wpm_calculator: WPMCalculator instance
        """
        self.wpm_calculator = wpm_calculator
    
    def get_key_display(self, key_name: str) -> str:
        """
        Get the display character for a key name.
        
        Args:
            key_name: The ZMK key name
            
        Returns:
            Display character for the key
        """
        return self.key_display_map.get(key_name, key_name[:3].upper())
    
    def set_pressed_keys(self, pressed_keys: Set[str]) -> None:
        """
        Set the currently pressed keys for highlighting.
        
        Args:
            pressed_keys: Set of currently pressed key names
        """
        self.pressed_keys = pressed_keys
    
    def render_keyboard(self, layer_keys: List[List[str]], layer_name: str = "") -> str:
        """
        Render the keyboard layout as bracket-style ASCII art.
        
        Args:
            layer_keys: List of key rows, where each row is a list of key names
            layer_name: Name of the layer being rendered
            
        Returns:
            ASCII art representation of the keyboard
        """
        if not layer_keys:
            return "No keys to render"
        
        # Split keyboard layout - left and right halves
        left_half = []
        right_half = []
        
        for row in layer_keys:
            # Split each row into left and right halves
            mid_point = len(row) // 2
            left_row = row[:mid_point]
            right_row = row[mid_point:]
            
            left_half.append(left_row)
            right_half.append(right_row)
        
        # Build the layout
        lines = []
        
        # Render each row (excluding thumb row which is handled separately)
        for i, (left_row, right_row) in enumerate(zip(left_half[:-1], right_half[:-1])):
            # Build left half
            left_keys = []
            for key in left_row:
                display = self.get_key_display(key)
                if key in self.pressed_keys:
                    left_keys.append(self._format_pressed_key(display))
                else:
                    left_keys.append(self._format_normal_key(display))
            
            # Build right half
            right_keys = []
            for key in right_row:
                display = self.get_key_display(key)
                if key in self.pressed_keys:
                    right_keys.append(self._format_pressed_key(display))
                else:
                    right_keys.append(self._format_normal_key(display))
            
            # Combine with proper spacing (4 tabs = 16 spaces)
            left_str = " ".join(left_keys)
            right_str = " ".join(right_keys)
            
            # Add indentation for visual effect (mirror staggering for ergonomic layout)
            left_indent = " " * (i * 2)  # Left half indents progressively to the right
            right_indent = " " * ((2 - i) * 2)  # Right half indents progressively to the left
            
            # Add WPM display in the center if available
            if self.wpm_calculator and i == 1:  # Show WPM on the second row (middle row)
                wpm_display = self.wpm_calculator.get_wpm_display()
                center_line = f"{left_indent}{left_str} {wpm_display} {right_indent}{right_str}"
            else:
                # For rows without WPM, ensure proper alignment with consistent spacing
                # Calculate spacing to align keys properly
                base_spacing = "                "  # 16 spaces between halves
                # Adjust right half positioning for better alignment
                adjusted_right_indent = " " * max(0, (2 - i) * 2)  # Ensure no negative indentation
                center_line = f"{left_indent}{left_str}{base_spacing}{adjusted_right_indent}{right_str}"
            
            lines.append(center_line)
        
        # Add thumb keys row
        if len(layer_keys) >= 4:
            thumb_row = layer_keys[3]
            if len(thumb_row) >= 4:
                # Extract thumb keys (typically the outer keys)
                left_thumb = thumb_row[0] if len(thumb_row) > 0 else ""
                left_gui = thumb_row[1] if len(thumb_row) > 1 else ""
                right_gui = thumb_row[-2] if len(thumb_row) > 2 else ""
                right_thumb = thumb_row[-1] if len(thumb_row) > 3 else ""
                
                # Render thumb keys
                left_thumb_display = self.get_key_display(left_thumb)
                left_gui_display = self.get_key_display(left_gui)
                right_gui_display = self.get_key_display(right_gui)
                right_thumb_display = self.get_key_display(right_thumb)
                
                # Highlight if pressed
                if left_thumb in self.pressed_keys:
                    left_thumb_str = self._format_pressed_key(left_thumb_display)
                else:
                    left_thumb_str = self._format_normal_key(left_thumb_display)
                
                if left_gui in self.pressed_keys:
                    left_gui_str = self._format_pressed_key(left_gui_display)
                else:
                    left_gui_str = self._format_normal_key(left_gui_display)
                
                if right_gui in self.pressed_keys:
                    right_gui_str = self._format_pressed_key(right_gui_display)
                else:
                    right_gui_str = self._format_normal_key(right_gui_display)
                
                if right_thumb in self.pressed_keys:
                    right_thumb_str = self._format_pressed_key(right_thumb_display)
                else:
                    right_thumb_str = self._format_normal_key(right_thumb_display)
                
                # Thumb row with proper spacing (4 tabs = 16 spaces)
                space_str = self._format_pressed_key('SPC') + ' ' if 'SPACE' in self.pressed_keys else self._format_normal_key('SPC') + ' '
                ent_str = self._format_pressed_key('ENT') + ' ' if 'RET' in self.pressed_keys else self._format_normal_key('ENT') + ' '
                thumb_line = f"             {left_gui_str}{left_thumb_str}{space_str}                {ent_str}{right_gui_str}{right_thumb_str}"
                lines.append(thumb_line)
        
        return "\n".join(lines) 
