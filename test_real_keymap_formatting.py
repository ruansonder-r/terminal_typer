#!/usr/bin/env python3
"""
Test formatting with the actual corne.keymap file.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from keyboard_renderer import KeyboardRenderer
from corne_keymap_parser import CorneKeymapParser

def test_real_keymap_formatting():
    """Test formatting with the actual corne.keymap file."""
    
    keymap_file = "examples/corne.keymap"
    if not os.path.exists(keymap_file):
        print(f"Keymap file not found: {keymap_file}")
        return
    
    # Parse the real keymap
    parser = CorneKeymapParser(keymap_file)
    
    # Test each layer
    for layer_name in ['default_layer', 'lower_layer', 'raise_layer']:
        print(f"\n=== Testing {layer_name} ===")
        
        layer_keys = parser.get_layer_keys(layer_name)
        if layer_keys:
            print(f"Layer keys: {layer_keys}")
            
            # Render the keyboard
            renderer = KeyboardRenderer()
            result = renderer.render_keyboard(layer_keys)
            
            print("Rendered keyboard:")
            print(result)
            
            # Check if formatting is consistent
            lines = result.split('\n')
            print(f"Number of lines: {len(lines)}")
            
            # Verify each line has proper formatting
            for i, line in enumerate(lines):
                print(f"Line {i}: '{line}'")
        else:
            print(f"No keys found for {layer_name}")

if __name__ == '__main__':
    test_real_keymap_formatting() 
