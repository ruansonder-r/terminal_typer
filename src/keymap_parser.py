import json
from typing import Dict, List, Optional

class KeymapParser:
    """
    Parser for ZMK keymap JSON files.
    Handles loading and parsing of keyboard layer configurations.
    """
    
    def __init__(self, keymap_file: str):
        """
        Initialize the parser with a keymap file.
        
        Args:
            keymap_file: Path to the JSON keymap file
        """
        self.keymap_file = keymap_file
        self.keymap_data = None
        self.layers = {}
        self._load_keymap()
    
    def _load_keymap(self) -> None:
        """Load and parse the keymap JSON file."""
        try:
            with open(self.keymap_file, 'r') as f:
                self.keymap_data = json.load(f)
            
            # Extract layers from the keymap
            if 'keymap' in self.keymap_data and 'layers' in self.keymap_data['keymap']:
                self.layers = self.keymap_data['keymap']['layers']
            else:
                raise ValueError("Invalid keymap format: missing 'keymap.layers'")
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Keymap file not found: {self.keymap_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in keymap file: {e}")
    
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
