#!/usr/bin/env python3
"""
Debug script to test layer switching functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from input_listener import InputListener
from corne_keymap_parser import CorneKeymapParser

def debug_layer_switching():
    """Debug the layer switching functionality."""
    
    # Initialize components
    parser = CorneKeymapParser("examples/corne.keymap")
    listener = InputListener()
    listener.set_keymap_parser(parser)
    
    print("=== Layer Switching Debug ===")
    
    # Test 1: Check if key mapping is working correctly
    print("\n1. Testing key mapping:")
    test_keys = ['1', '!', 'q', 'a']
    for key in test_keys:
        zmk_key = listener.key_mapping.get(key.lower(), key.upper())
        print(f"  '{key}' -> '{zmk_key}'")
    
    # Test 2: Check if layer detection is working
    print("\n2. Testing layer detection:")
    test_zmk_keys = ['1', '!', 'Q', 'A']
    for zmk_key in test_zmk_keys:
        layer = listener._find_layer_for_key(zmk_key)
        print(f"  '{zmk_key}' found in layer: {layer}")
    
    # Test 3: Check current layer keys
    print("\n3. Testing current layer keys:")
    listener.current_layer = "default_layer"
    current_keys = listener._get_current_layer_keys()
    print(f"  Default layer keys: {sorted(list(current_keys))}")
    
    listener.current_layer = "lower_layer"
    current_keys = listener._get_current_layer_keys()
    print(f"  Lower layer keys: {sorted(list(current_keys))}")
    
    listener.current_layer = "raise_layer"
    current_keys = listener._get_current_layer_keys()
    print(f"  Raise layer keys: {sorted(list(current_keys))}")
    
    # Test 4: Simulate key presses and check layer switching
    print("\n4. Testing automatic layer switching:")
    
    # Start in default layer
    listener.current_layer = "default_layer"
    print(f"  Starting in layer: {listener.current_layer}")
    
    # Press '1' - should switch to lower layer
    print("  Pressing '1'...")
    listener._on_press_simulation('1')
    print(f"  Current layer after '1': {listener.current_layer}")
    print(f"  Pressed keys: {listener.pressed_keys}")
    
    # Press '!' - should switch to raise layer
    print("  Pressing '!'...")
    listener._on_press_simulation('!')
    print(f"  Current layer after '!': {listener.current_layer}")
    print(f"  Pressed keys: {listener.pressed_keys}")
    
    # Press 'Q' - should switch back to default layer
    print("  Pressing 'Q'...")
    listener._on_press_simulation('Q')
    print(f"  Current layer after 'Q': {listener.current_layer}")
    print(f"  Pressed keys: {listener.pressed_keys}")
    
    # Test 5: Check if the issue is in the automatic layer switch logic
    print("\n5. Testing automatic layer switch logic:")
    
    # Reset to default layer
    listener.current_layer = "default_layer"
    listener.pressed_keys.clear()
    
    # Test with '1' key
    zmk_key = listener.key_mapping.get('1', '1')
    print(f"  Testing key '{zmk_key}' in default layer...")
    
    # Check if key is in current layer
    current_keys = listener._get_current_layer_keys()
    print(f"  Keys in default layer: {sorted(list(current_keys))}")
    print(f"  Is '{zmk_key}' in default layer? {zmk_key in current_keys}")
    
    # Check which layer contains this key
    target_layer = listener._find_layer_for_key(zmk_key)
    print(f"  Layer containing '{zmk_key}': {target_layer}")
    
    # Manually trigger the check
    if zmk_key not in current_keys:
        if target_layer and target_layer != listener.current_layer:
            print(f"  Should switch from {listener.current_layer} to {target_layer}")
        else:
            print(f"  No layer switch needed")
    else:
        print(f"  Key is in current layer, no switch needed")

if __name__ == '__main__':
    debug_layer_switching() 
