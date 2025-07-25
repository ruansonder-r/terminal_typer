from pynput import keyboard
from typing import Set, Callable, Optional
import threading
import time
from keymap_parser import KeymapParser
from wpm_calculator import WPMCalculator

class InputListener:
    """
    Global keyboard input listener for capturing keypresses.
    Maps physical keys to ZMK key names and manages layer state.
    """
    
    def __init__(self):
        """Initialize the input listener."""
        # Physical key to ZMK key name mapping
        self.key_mapping = {
            # Letters
            'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F', 'g': 'G', 'h': 'H', 'i': 'I', 'j': 'J',
            'k': 'K', 'l': 'L', 'm': 'M', 'n': 'N', 'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R', 's': 'S', 't': 'T',
            'u': 'U', 'v': 'V', 'w': 'W', 'x': 'X', 'y': 'Y', 'z': 'Z',
            
            # Numbers
            '0': 'N0', '1': 'N1', '2': 'N2', '3': 'N3', '4': 'N4', '5': 'N5', '6': 'N6', '7': 'N7', '8': 'N8', '9': 'N9',
            
            # Symbols
            ',': 'COMMA', '.': 'DOT', '/': 'SLASH', ';': 'SEMI', "'": 'QUOTE', '[': 'LBRC', ']': 'RBRC', '\\': 'BSLH',
            '=': 'EQUAL', '-': 'MINUS', '`': 'GRAVE', '~': 'TILDE', '!': 'EXCL', '@': 'AT', '#': 'HASH', '$': 'DLR',
            '%': 'PRCNT', '^': 'CIRC', '&': 'AMPS', '*': 'STAR', '(': 'LPAR', ')': 'RPAR', '_': 'UNDS', '+': 'PLUS',
            '{': 'LCBR', '}': 'RCBR', '|': 'PIPE', '<': 'LABK', '>': 'RABK', '?': 'QUES', ':': 'COLN', '"': 'DQUO',
            
            # Modifiers
            'ctrl_l': 'LCTRL', 'ctrl_r': 'RCTRL', 'alt_l': 'LALT', 'alt_r': 'RALT', 'cmd': 'LGUI', 'cmd_r': 'RGUI',
            'shift': 'LSHFT', 'shift_r': 'RSHFT', 'ctrl': 'LCTRL', 'ctrl_r': 'RCTRL',
            
            # Special keys
            'space': 'SPACE', 'enter': 'ENTER', 'esc': 'ESCAPE', 'tab': 'TAB', 'backspace': 'BACKSPACE', 'delete': 'DELETE',
            'return': 'ENTER', 'escape': 'ESCAPE', 'tab': 'TAB', 'backspace': 'BACKSPACE', 'delete': 'DELETE',
            
            # Function keys
            'f1': 'F1', 'f2': 'F2', 'f3': 'F3', 'f5': 'F5', 'f6': 'F6',
            'f7': 'F7', 'f8': 'F8', 'f9': 'F9', 'f10': 'F10', 'f11': 'F11', 'f12': 'F12',
            
            # Navigation
            'up': 'UP', 'down': 'DOWN', 'left': 'LEFT', 'right': 'RIGHT', 'home': 'HOME', 'end': 'END',
            'page_up': 'PGUP', 'page_down': 'PGDN', 'insert': 'INS',
            
            # Media keys
            'media_volume_mute': 'MUTE', 'media_volume_up': 'VOLU', 'media_volume_down': 'VOLD',
            'media_next': 'NEXT', 'media_previous': 'PREV', 'media_play_pause': 'PLAY', 'media_stop': 'STOP',
            
            # Layer keys (using F1/F2 as layer keys)
            'f1': 'mo(1)', 'f2': 'mo(2)',  # Using F1/F2 as layer keys
        }
        
        # Currently pressed keys
        self.pressed_keys: Set[str] = set()
        
        # Layer state
        self.current_layer = "default_layer"
        self.layer_keys = {
            "default_layer": set(),
            "lower_layer": set(),
            "raise_layer": set()
        }
        
        # Callback for key changes
        self.key_change_callback: Optional[Callable[[Set[str], str], None]] = None
        
        # Listener instance
        self.listener: Optional[keyboard.Listener] = None
        
        # WPM calculator
        self.wpm_calculator: Optional[WPMCalculator] = None
        
        # Keymap parser for automatic layer detection
        self.keymap_parser: Optional[KeymapParser] = None
        
        # Word tracking
        self.current_word = ""
        self.word_boundaries = {' ', '.'}  # Space and period are word boundaries
    
    def set_wpm_calculator(self, wpm_calculator: WPMCalculator) -> None:
        """Set the WPM calculator for keystroke tracking."""
        self.wpm_calculator = wpm_calculator
    
    def set_keymap_parser(self, keymap_parser: KeymapParser) -> None:
        """Set the keymap parser for automatic layer detection."""
        self.keymap_parser = keymap_parser
    
    def get_current_word(self) -> str:
        """Get the current word being typed."""
        return self.current_word
    
    def start_listening(self, callback: Callable[[Set[str], str], None]) -> None:
        """Start listening for keyboard input."""
        self.key_change_callback = callback
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
    
    def stop_listening(self) -> None:
        """Stop listening for keyboard input."""
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def _on_press(self, key) -> None:
        """Handle key press events."""
        try:
            # Convert key to string
            key_str = self._key_to_string(key)
            if not key_str:
                return
            
            # Handle word building
            self._handle_word_building(key_str)
            
            # Map to ZMK key name
            zmk_key = self.key_mapping.get(key_str.lower(), key_str.upper())
            
            # Add to pressed keys
            if zmk_key not in self.pressed_keys:
                self.pressed_keys.add(zmk_key)
                
                # Track keystroke for WPM calculation if printable
                if self.wpm_calculator and self._is_printable_key(key_str):
                    self.wpm_calculator.add_keystroke()
                
                # Handle layer key press
                self._handle_layer_key_press(zmk_key)
                
                # Check for automatic layer switching
                if self.keymap_parser:
                    self._check_automatic_layer_switch(zmk_key)
                
                # Notify callback
                self._notify_key_change()
                
        except Exception as e:
            print(f"Error handling key press: {e}")
    
    def _on_release(self, key) -> None:
        """Handle key release events."""
        try:
            # Convert key to string
            key_str = self._key_to_string(key)
            if not key_str:
                return
            
            # Map to ZMK key name
            zmk_key = self.key_mapping.get(key_str.lower(), key_str.upper())
            
            # Remove from pressed keys
            if zmk_key in self.pressed_keys:
                self.pressed_keys.remove(zmk_key)
                
                # Handle layer key release
                self._handle_layer_key_release(zmk_key)
                
                # Notify callback
                self._notify_key_change()
                
        except Exception as e:
            print(f"Error handling key release: {e}")
    
    def _handle_word_building(self, key_str: str) -> None:
        """Handle word building logic."""
        # Check if it's a word boundary
        if key_str in self.word_boundaries:
            # Clear the current word when a boundary is reached
            self.current_word = ""
            return
        
        # Check if it's backspace
        if key_str == 'backspace':
            # Remove the last character from the current word
            if self.current_word:
                self.current_word = self.current_word[:-1]
            return
        
        # Check if it's a printable character (for word building)
        if self._is_printable_key(key_str):
            # Add the character to the current word
            self.current_word += key_str
    
    def _key_to_string(self, key) -> Optional[str]:
        """Convert pynput key to string."""
        if hasattr(key, 'char') and key.char:
            return key.char
        elif hasattr(key, 'name'):
            return key.name
        else:
            return None
    
    def _is_printable_key(self, key_str: str) -> bool:
        """Check if a key is printable (for WPM calculation and word building)."""
        return len(key_str) == 1 and key_str.isprintable() and not key_str.isspace()
    
    def _handle_layer_key_press(self, zmk_key: str) -> None:
        """Handle layer key press events."""
        if zmk_key == 'mo(1)':
            self.current_layer = "lower_layer"
        elif zmk_key == 'mo(2)':
            self.current_layer = "raise_layer"
    
    def _handle_layer_key_release(self, zmk_key: str) -> None:
        """Handle layer key release events."""
        if zmk_key in ['mo(1)', 'mo(2)']:
            self.current_layer = "default_layer"
    
    def _check_automatic_layer_switch(self, zmk_key: str) -> None:
        """Check if we need to automatically switch layers based on pressed key."""
        if not self.keymap_parser:
            return
        
        # Get current layer keys
        current_layer_keys = self._get_current_layer_keys()
        
        # If the pressed key is not in the current layer, find which layer contains it
        if zmk_key not in current_layer_keys:
            target_layer = self._find_layer_for_key(zmk_key)
            if target_layer and target_layer != self.current_layer:
                self.current_layer = target_layer
    
    def _find_layer_for_key(self, zmk_key: str) -> Optional[str]:
        """Find which layer contains a specific key."""
        if not self.keymap_parser:
            return None
        
        layer_names = self.keymap_parser.get_layer_names()
        
        for layer_name in layer_names:
            layer_keys = self.keymap_parser.get_layer_keys(layer_name)
            if layer_keys:
                # Flatten the layer keys into a set
                all_keys = set()
                for row in layer_keys:
                    all_keys.update(row)
                
                if zmk_key in all_keys:
                    return layer_name
        
        return None
    
    def _get_current_layer_keys(self) -> Set[str]:
        """Get all keys from the current layer."""
        if not self.keymap_parser:
            return set()
        
        layer_keys = self.keymap_parser.get_layer_keys(self.current_layer)
        if not layer_keys:
            return set()
        
        # Flatten the layer keys into a set
        all_keys = set()
        for row in layer_keys:
            all_keys.update(row)
        
        return all_keys
    
    def _notify_key_change(self) -> None:
        """Notify the callback of key state changes."""
        if self.key_change_callback:
            self.key_change_callback(self.pressed_keys.copy(), self.current_layer)
    
    # Simulation methods for testing
    def _on_press_simulation(self, key_str: str) -> None:
        """Simulate a key press for testing."""
        # Handle word building
        self._handle_word_building(key_str)
        
        zmk_key = self.key_mapping.get(key_str.lower(), key_str.upper())
        if zmk_key not in self.pressed_keys:
            self.pressed_keys.add(zmk_key)
            if self.wpm_calculator and self._is_printable_key(key_str):
                self.wpm_calculator.add_keystroke()
            self._handle_layer_key_press(zmk_key)
            if self.keymap_parser:
                self._check_automatic_layer_switch(zmk_key)
            self._notify_key_change()
    
    def _on_release_simulation(self, key_str: str) -> None:
        """Simulate a key release for testing."""
        zmk_key = self.key_mapping.get(key_str.lower(), key_str.upper())
        if zmk_key in self.pressed_keys:
            self.pressed_keys.remove(zmk_key)
            self._handle_layer_key_release(zmk_key)
            self._notify_key_change() 
