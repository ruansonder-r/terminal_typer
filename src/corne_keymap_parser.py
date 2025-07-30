import re
from typing import Dict, List, Optional

class CorneKeymapParser:
    """
    Parser for ZMK corne.keymap files in Device Tree Source (DTS) format.
    Handles loading and parsing of keyboard layer configurations.
    """
    
    def __init__(self, keymap_file: str):
        """
        Initialize the parser with a keymap file.
        
        Args:
            keymap_file: Path to the corne.keymap file
        """
        self.keymap_file = keymap_file
        self.layers = {}
        self._load_keymap()
    
    def _load_keymap(self) -> None:
        """Load and parse the corne.keymap file."""
        try:
            with open(self.keymap_file, 'r') as f:
                content = f.read()
            
            # Extract layers from the keymap
            self._parse_layers(content)
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Keymap file not found: {self.keymap_file}")
        except Exception as e:
            raise ValueError(f"Error parsing keymap file: {e}")
    
    def _parse_layers(self, content: str) -> None:
        """Parse the DTS content to extract layer definitions."""
        # Find all layer definitions
        # Updated pattern to be more flexible with whitespace and comments
        layer_pattern = r'(\w+_layer)\s*\{[^}]*?bindings\s*=\s*<([^>]+)>[^}]*?\};'
        matches = re.findall(layer_pattern, content, re.DOTALL)
        
        for layer_name, bindings_content in matches:
            # Parse the bindings for this layer
            keys = self._parse_bindings(bindings_content)
            if keys:
                self.layers[layer_name] = keys
        
        # Fallback: manually parse raise_layer if not found by regex
        if 'raise_layer' not in self.layers and 'raise_layer' in content:
            self._parse_raise_layer_fallback(content)
    
    def _parse_raise_layer_fallback(self, content: str) -> None:
        """Fallback method to parse raise_layer manually."""
        try:
            # Find the raise_layer section
            raise_start = content.find('raise_layer {')
            if raise_start == -1:
                return
            
            # Find the end of the raise_layer section
            raise_section = content[raise_start:]
            raise_end = raise_section.find('};')
            if raise_end == -1:
                return
            
            raise_section = raise_section[:raise_end]
            
            # Find bindings in the raise_layer section
            bindings_start = raise_section.find('bindings = <')
            if bindings_start == -1:
                return
            
            bindings_end = raise_section.find('>', bindings_start)
            if bindings_end == -1:
                return
            
            bindings_content = raise_section[bindings_start + 12:bindings_end]
            
            # Parse the bindings
            keys = self._parse_bindings(bindings_content)
            if keys:
                self.layers['raise_layer'] = keys
                
        except Exception as e:
            print(f"Warning: Failed to parse raise_layer fallback: {e}")
    
    def _parse_bindings(self, bindings_content: str) -> List[str]:
        """Parse the bindings content into a list of key rows."""
        # Split by lines and clean up
        lines = [line.strip() for line in bindings_content.split('\n') if line.strip()]
        
        # Parse each line into key names
        key_rows = []
        for line in lines:
            keys = self._parse_key_line(line)
            if keys:
                # Join keys with spaces to match the expected format
                key_rows.append(' '.join(keys))
        
        return key_rows
    
    def _parse_key_line(self, line: str) -> List[str]:
        """Parse a single line of key bindings."""
        # Find all key bindings in the line
        # Pattern to match &kp KEY, &mo NUMBER, &bt KEY, &msc KEY
        key_pattern = r'&(kp|mo|bt|msc)\s+([A-Z_0-9]+(?:\s+[0-9]+)?)'
        matches = re.findall(key_pattern, line)
        
        # Convert ZMK key names to more readable format
        converted_keys = []
        for key_type, key_name in matches:
            # Handle the case where we have a number after the key name (like in &mo 1)
            if ' ' in key_name:
                base_name, number = key_name.split(' ', 1)
                full_key = f"{base_name} {number}"
            else:
                full_key = key_name
            
            # Pass the key type and name to the converter
            converted_key = self._convert_key_name(full_key, key_type)
            converted_keys.append(converted_key)
        
        return converted_keys
    
    def _convert_key_name(self, key: str, key_type: str) -> str:
        """Convert ZMK key names to more readable format."""
        # Common key name mappings
        key_mappings = {
            'TAB': 'TAB',
            'Q': 'Q', 'W': 'W', 'E': 'E', 'R': 'R', 'T': 'T', 'Y': 'Y', 'U': 'U', 'I': 'I', 'O': 'O', 'P': 'P',
            'A': 'A', 'S': 'S', 'D': 'D', 'F': 'F', 'G': 'G', 'H': 'H', 'J': 'J', 'K': 'K', 'L': 'L',
            'Z': 'Z', 'X': 'X', 'C': 'C', 'V': 'V', 'B': 'B', 'N': 'N', 'M': 'M',
            'LCTRL': 'CTRL', 'LSHFT': 'SHFT', 'LEFT_GUI': 'GUI', 'SPACE': 'SPC', 'RET': 'ENT',
            'SEMI': ';', 'SQT': "'", 'COMMA': ',', 'DOT': '.', 'FSLH': '/', 'ESC': 'ESC',
            'BSPC': 'BSPC',
            'N1': '1', 'N2': '2', 'N3': '3', 'N4': '4', 'N5': '5',
            'N6': '6', 'N7': '7', 'N8': '8', 'N9': '9', 'N0': '0',
            'LEFT': 'LFT', 'DOWN': 'DWN', 'UP': 'UP', 'RIGHT': 'RGT',
            'EXCL': '!', 'AT': '@', 'HASH': '#', 'DLLR': '$', 'PRCNT': '%',
            'CARET': '^', 'AMPS': '&', 'ASTRK': '*', 'LPAR': '(', 'RPAR': ')',
            'MINUS': '-', 'EQUAL': '=', 'LBKT': '[', 'RBKT': ']', 'BSLH': '\\', 'GRAVE': '`',
            'UNDER': '_', 'PLUS': '+', 'LBRC': '{', 'RBRC': '}', 'PIPE': '|', 'TILDE': '~',
            'HOME': 'HOME', 'END': 'END', 'DEL': 'DEL',
            'C_PREV': 'PREV', 'C_PLAY_PAUSE': 'PLAY', 'C_NEXT': 'NEXT',
            'C_VOLUME_UP': 'VOL+', 'C_VOL_DN': 'VOL-', 'C_MUTE': 'MUTE',
            'BT_CLR': 'BTCLR', 'BT_SEL': 'BT',
            'SCRL_LEFT': 'SCRL_L', 'SCRL_UP': 'SCRL_U', 'SCRL_RIGHT': 'SCRL_R', 'SCRL_DOWN': 'SCRL_D',
            'LGUI': 'GUI', 'RALT': 'ALT', 'RCTRL': 'CTRL',
            'trans': 'TRANS'
        }
        
        # Handle special cases
        if key.startswith('BT_SEL '):
            # Extract the number from BT_SEL 0, BT_SEL 1, etc.
            number = key.split()[-1]
            return f'BT{number}'
        
        # Handle layer modifiers like "mo 1", "mo 2"
        if key.startswith('mo '):
            number = key.split()[-1]
            return f'L{number}'
        
        # Handle key types
        if key_type == 'kp':
            return key_mappings.get(key, key)
        elif key_type == 'mo':
            return f'L{key}' # Assuming 'mo' is a layer modifier
        elif key_type == 'bt':
            return key_mappings.get(key, key)
        elif key_type == 'msc':
            return key_mappings.get(key, key)
        
        return key_mappings.get(key, key)
    
    def get_layer(self, layer_name: str) -> Optional[List[str]]:
        """
        Get a specific layer by name.
        
        Args:
            layer_name: Name of the layer (e.g., 'default_layer', 'lower_layer')
            
        Returns:
            List of key rows for the layer, or None if layer doesn't exist
        """
        return self.layers.get(layer_name)
    
    def get_all_layers(self) -> Dict[str, List[str]]:
        """
        Get all available layers.
        
        Returns:
            Dictionary mapping layer names to their key configurations
        """
        return self.layers.copy()
    
    def get_layer_names(self) -> List[str]:
        """
        Get list of all available layer names.
        
        Returns:
            List of layer names
        """
        return list(self.layers.keys())
    
    def parse_key_row(self, row: str) -> List[str]:
        """
        Parse a single row of keys into individual key names.
        
        Args:
            row: Space-separated string of key names
            
        Returns:
            List of individual key names
        """
        return row.strip().split()
    
    def get_layer_keys(self, layer_name: str) -> Optional[List[List[str]]]:
        """
        Get parsed key configuration for a specific layer.
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            List of key rows, where each row is a list of key names
        """
        layer = self.get_layer(layer_name)
        if layer is None:
            return None
        
        return [self.parse_key_row(row) for row in layer]
    
    def _find_layer_for_key(self, zmk_key: str) -> Optional[str]:
        """
        Find which layer contains a specific key.
        
        Args:
            zmk_key: The ZMK key name to search for
            
        Returns:
            Layer name that contains the key, or None if not found
        """
        layer_names = self.get_layer_names()
        
        for layer_name in layer_names:
            layer_keys = self.get_layer_keys(layer_name)
            if layer_keys:
                # Flatten the layer keys into a set
                all_keys = set()
                for row in layer_keys:
                    all_keys.update(row)
                
                if zmk_key in all_keys:
                    return layer_name
        
        return None 
