from pynput import keyboard
from typing import Set, Callable, Dict, Optional
import threading
import time

class InputListener:
    """
    Captures global keyboard input and maps physical keypresses to ZMK key names.
    Handles layer switching and provides real-time key state updates.
    """
    
    def __init__(self):
        """Initialize the input listener."""
        self.pressed_keys: Set[str] = set()
        self.layer_keys: Set[str] = set()  # Currently held layer keys
        self.current_layer: str = "default_layer"
        self.layer_stack: list = ["default_layer"]  # Layer history for proper switching
        
        # WPM calculator (optional)
        self.wpm_calculator = None
        
        # Keymap parser for automatic layer detection (optional)
        self.keymap_parser = None
        
        # Physical key to ZMK key mapping
        self.key_mapping = {
            # Letters
            'q': 'Q', 'w': 'W', 'e': 'E', 'r': 'R', 't': 'T', 'y': 'Y', 'u': 'U', 'i': 'I', 'o': 'O', 'p': 'P',
            'a': 'A', 's': 'S', 'd': 'D', 'f': 'F', 'g': 'G', 'h': 'H', 'j': 'J', 'k': 'K', 'l': 'L',
            'z': 'Z', 'x': 'X', 'c': 'C', 'v': 'V', 'b': 'B', 'n': 'N', 'm': 'M',
            
            # Numbers
            '1': 'N1', '2': 'N2', '3': 'N3', '4': 'N4', '5': 'N5', '6': 'N6', '7': 'N7', '8': 'N8', '9': 'N9', '0': 'N0',
            
            # Symbols
            '!': 'EXCL', '@': 'AT', '#': 'HASH', '$': 'DLLR', '%': 'PRCNT', '^': 'CARET', '&': 'AMPS', '*': 'ASTRK',
            '(': 'LPAR', ')': 'RPAR', '-': 'MINUS', '=': 'EQUAL', '[': 'LBKT', ']': 'RBKT', '\\': 'BSLH',
            '{': 'LBRC', '}': 'RBRC', '|': 'PIPE', '~': 'TILDE', '`': 'GRAVE', '_': 'UNDER', '+': 'PLUS',
            ';': 'SEMI', "'": 'SQT', ',': 'COMMA', '.': 'DOT', '/': 'FSLH',
            
            # Special keys
            'tab': 'TAB', 'backspace': 'BSPC', 'enter': 'RET', 'esc': 'ESC', 'space': 'SPACE',
            'ctrl_l': 'LCTRL', 'ctrl_r': 'LCTRL', 'shift': 'LSHFT', 'shift_l': 'LSHFT', 'shift_r': 'LSHFT',
            'cmd_l': 'LEFT_GUI', 'cmd_r': 'LEFT_GUI', 'alt_l': 'RALT', 'alt_r': 'RALT',
            
            # Layer keys (these will be handled specially)
            'f1': 'mo(1)', 'f2': 'mo(2)', 'f4': 'F4',  # Using F1/F2 as layer keys, F4 for visual style cycling
            
            # Media keys
            'media_previous': 'C_PREV', 'media_play_pause': 'C_PLAY_PAUSE', 'media_next': 'C_NEXT',
            'media_volume_up': 'C_VOLUME_UP', 'media_volume_down': 'C_VOL_DN', 'media_volume_mute': 'C_MUTE',
            
            # Navigation
            'left': 'LEFT', 'down': 'DOWN', 'up': 'UP', 'right': 'RIGHT', 'home': 'HOME', 'end': 'END',
            'page_up': 'SCRL_UP', 'page_down': 'SCRL_DOWN',
            
            # Other
            'delete': 'DEL'
        }
        
        # Reverse mapping for layer keys
        self.layer_key_mapping = {
            'mo(1)': 'lower_layer',
            'mo(2)': 'raise_layer'
        }
        
        # Callback for key state changes
        self.on_key_change: Optional[Callable[[Set[str], str], None]] = None
        
        # Listener thread
        self.listener: Optional[keyboard.Listener] = None
        self.is_listening = False
        
        # Error tracking
        self.unsupported_keys: Set[str] = set()
    
    def start_listening(self, on_key_change: Callable[[Set[str], str], None]) -> None:
        """
        Start listening for keyboard input.
        
        Args:
            on_key_change: Callback function called when key state changes
        """
        self.on_key_change = on_key_change
        self.is_listening = True
        
        # Start the listener
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
    
    def stop_listening(self) -> None:
        """Stop listening for keyboard input."""
        self.is_listening = False
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def _on_press(self, key) -> None:
        """Handle key press events."""
        try:
            # Convert key to string representation
            key_str = self._key_to_string(key)
            if not key_str:
                return
            
            # Track keystroke for WPM calculation (only for printable characters)
            if self.wpm_calculator and self._is_printable_key(key_str):
                self.wpm_calculator.add_keystroke()
            
            # Check if it's a layer key
            if key_str in self.layer_key_mapping:
                self._handle_layer_key_press(key_str)
            else:
                # Regular key press
                zmk_key = self.key_mapping.get(key_str.lower())
                if zmk_key:
                    # Check if this key exists in the current layer
                    current_layer_keys = self._get_current_layer_keys()
                    if zmk_key not in current_layer_keys:
                        # Key not in current layer, try to find which layer contains it
                        target_layer = self._find_layer_for_key(zmk_key)
                        if target_layer and target_layer != self.current_layer:
                            # Switch to the layer that contains this key
                            self.current_layer = target_layer
                            self.layer_stack.append(target_layer)
                    
                    self.pressed_keys.add(zmk_key)
                    self._notify_key_change()
                else:
                    # Unsupported key
                    self.unsupported_keys.add(key_str)
                    self._notify_key_change()
                    
        except Exception as e:
            print(f"Error handling key press: {e}")
    
    def _on_release(self, key) -> None:
        """Handle key release events."""
        try:
            # Convert key to string representation
            key_str = self._key_to_string(key)
            if not key_str:
                return
            
            # Check if it's a layer key
            if key_str in self.layer_key_mapping:
                self._handle_layer_key_release(key_str)
            else:
                # Regular key release
                zmk_key = self.key_mapping.get(key_str.lower())
                if zmk_key and zmk_key in self.pressed_keys:
                    self.pressed_keys.remove(zmk_key)
                    self._notify_key_change()
                    
        except Exception as e:
            print(f"Error handling key release: {e}")
    
    def _key_to_string(self, key) -> Optional[str]:
        """Convert pynput key object to string representation."""
        if hasattr(key, 'char') and key.char:
            return key.char
        elif hasattr(key, 'name'):
            return key.name
        else:
            return None
    
    def _handle_layer_key_press(self, key_str: str) -> None:
        """Handle layer key press (temporary layer switching)."""
        zmk_key = self.key_mapping.get(key_str.lower())
        if zmk_key and zmk_key in self.layer_key_mapping:
            target_layer = self.layer_key_mapping[zmk_key]
            
            # Add to layer keys and switch layer
            self.layer_keys.add(zmk_key)
            self.layer_stack.append(target_layer)
            self.current_layer = target_layer
            
            # Add the layer key to pressed keys for highlighting
            self.pressed_keys.add(zmk_key)
            self._notify_key_change()
    
    def _handle_layer_key_release(self, key_str: str) -> None:
        """Handle layer key release (return to previous layer)."""
        zmk_key = self.key_mapping.get(key_str.lower())
        if zmk_key and zmk_key in self.layer_key_mapping:
            # Remove from layer keys
            self.layer_keys.discard(zmk_key)
            
            # Return to previous layer
            if len(self.layer_stack) > 1:
                self.layer_stack.pop()
                self.current_layer = self.layer_stack[-1]
            
            # Remove the layer key from pressed keys
            self.pressed_keys.discard(zmk_key)
            self._notify_key_change()
    
    def _notify_key_change(self) -> None:
        """Notify callback of key state change."""
        if self.on_key_change:
            self.on_key_change(self.pressed_keys, self.current_layer)
    
    def get_pressed_keys(self) -> Set[str]:
        """Get currently pressed keys."""
        return self.pressed_keys.copy()
    
    def get_current_layer(self) -> str:
        """Get current active layer."""
        return self.current_layer
    
    def get_unsupported_keys(self) -> Set[str]:
        """Get set of unsupported keys that were pressed."""
        return self.unsupported_keys.copy()
    
    def clear_unsupported_keys(self) -> None:
        """Clear the list of unsupported keys."""
        self.unsupported_keys.clear() 

    def set_wpm_calculator(self, wpm_calculator) -> None:
        """
        Set the WPM calculator for keystroke tracking.
        
        Args:
            wpm_calculator: WPMCalculator instance
        """
        self.wpm_calculator = wpm_calculator
    
    def set_keymap_parser(self, keymap_parser) -> None:
        """
        Set the keymap parser for automatic layer detection.
        
        Args:
            keymap_parser: KeymapParser instance
        """
        self.keymap_parser = keymap_parser
    
    def _find_layer_for_key(self, zmk_key: str) -> Optional[str]:
        """
        Find which layer contains the specified ZMK key.
        
        Args:
            zmk_key: The ZMK key name to search for
            
        Returns:
            Layer name if found, None otherwise
        """
        if not self.keymap_parser:
            return None
        
        # Search through all available layers
        available_layers = ["default_layer", "lower_layer", "raise_layer"]
        
        for layer_name in available_layers:
            layer_keys = self.keymap_parser.get_layer_keys(layer_name)
            if layer_keys:
                # Flatten the layer keys into a single list for searching
                all_keys_in_layer = []
                for row in layer_keys:
                    all_keys_in_layer.extend(row)
                
                if zmk_key in all_keys_in_layer:
                    return layer_name
        
        return None

    def _is_printable_key(self, key_str: str) -> bool:
        """Check if a key string represents a printable character."""
        printable_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?`~\'"\\/')
        return key_str in printable_chars
    
    def _on_press_simulation(self, zmk_key: str) -> None:
        """
        Simulate a key press for testing purposes.
        
        Args:
            zmk_key: The ZMK key name to simulate
        """
        # Check if this key exists in the current layer
        current_layer_keys = self._get_current_layer_keys()
        if zmk_key not in current_layer_keys:
            # Key not in current layer, try to find which layer contains it
            target_layer = self._find_layer_for_key(zmk_key)
            if target_layer and target_layer != self.current_layer:
                # Switch to the layer that contains this key
                self.current_layer = target_layer
                self.layer_stack.append(target_layer)
        
        self.pressed_keys.add(zmk_key)
        self._notify_key_change()
    
    def _on_release_simulation(self, zmk_key: str) -> None:
        """
        Simulate a key release for testing purposes.
        
        Args:
            zmk_key: The ZMK key name to simulate
        """
        if zmk_key in self.pressed_keys:
            self.pressed_keys.remove(zmk_key)
            self._notify_key_change()

    def _get_current_layer_keys(self) -> Set[str]:
        """
        Get all keys in the current layer.
        
        Returns:
            Set of all ZMK key names in the current layer
        """
        if not self.keymap_parser:
            return set()
        
        layer_keys = self.keymap_parser.get_layer_keys(self.current_layer)
        if not layer_keys:
            return set()
        
        # Flatten the layer keys into a single set
        all_keys = set()
        for row in layer_keys:
            all_keys.update(row)
        
        return all_keys 
