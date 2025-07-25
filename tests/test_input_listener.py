#!/usr/bin/env python3
"""
Unit tests for the input listener functionality.
"""

import unittest
import tempfile
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from input_listener import InputListener
from keymap_parser import KeymapParser
from wpm_calculator import WPMCalculator

class TestInputListener(unittest.TestCase):
    """Test cases for InputListener class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary keymap file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        keymap_data = {
            "keymap": {
                "compatible": "zmk,keymap",
                "layers": {
                    "default_layer": [
                        "TAB Q W E R T Y U I O P BSP",
                        "CTL A S D F G H J K L ; '",
                        "SFT Z X C V B N M , . / ESC",
                        "LWR LEF SPC RET CTL RSE"
                    ],
                    "lower_layer": [
                        "TAB N1 N2 N3 N4 N5 N6 N7 N8 N9 N0 BSP",
                        "CTL A S D F G H J K L ; '",
                        "SFT Z X C V B N M , . / ESC",
                        "LWR LEF SPC RET CTL RSE"
                    ],
                    "raise_layer": [
                        "TAB EXCL AT HASH DLR PRCNT CIRC AMPS STAR LPAR RPAR BSP",
                        "CTL A S D F G H J K L ; '",
                        "SFT Z X C V B N M , . / ESC",
                        "LWR LEF SPC RET CTL RSE"
                    ]
                }
            }
        }
        import json
        json.dump(keymap_data, self.temp_file)
        self.temp_file.close()
        
        # Create input listener with test keymap
        self.listener = InputListener()
        self.keymap_parser = KeymapParser(self.temp_file.name)
        self.wpm_calculator = WPMCalculator()
        
        self.listener.set_keymap_parser(self.keymap_parser)
        self.listener.set_wpm_calculator(self.wpm_calculator)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_file'):
            os.unlink(self.temp_file.name)
    
    def test_initial_state(self):
        """Test initial state of input listener."""
        self.assertEqual(len(self.listener.pressed_keys), 0)
        self.assertEqual(self.listener.current_layer, "default_layer")
        self.assertEqual(len(self.listener.layer_keys), 3)  # Now has 3 layer sets
    
    def test_key_mapping(self):
        """Test key mapping functionality."""
        # Test letter mapping
        self.assertEqual(self.listener.key_mapping.get('q'), 'Q')
        self.assertEqual(self.listener.key_mapping.get('a'), 'A')
        self.assertEqual(self.listener.key_mapping.get('z'), 'Z')
        
        # Test number mapping
        self.assertEqual(self.listener.key_mapping.get('1'), 'N1')
        self.assertEqual(self.listener.key_mapping.get('0'), 'N0')
        
        # Test symbol mapping
        self.assertEqual(self.listener.key_mapping.get('!'), 'EXCL')
        self.assertEqual(self.listener.key_mapping.get('@'), 'AT')
        
        # Test special key mapping
        self.assertEqual(self.listener.key_mapping.get('space'), 'SPACE')
        self.assertEqual(self.listener.key_mapping.get('tab'), 'TAB')
    
    def test_layer_key_mapping(self):
        """Test layer key mapping."""
        # Test that F1 and F2 are mapped to layer keys
        self.assertEqual(self.listener.key_mapping.get('f1'), 'mo(1)')
        self.assertEqual(self.listener.key_mapping.get('f2'), 'mo(2)')
    
    def test_find_layer_for_key(self):
        """Test finding which layer contains a key."""
        # Test keys from different layers
        self.assertEqual(self.listener._find_layer_for_key("Q"), "default_layer")
        self.assertEqual(self.listener._find_layer_for_key("N1"), "lower_layer")
        self.assertEqual(self.listener._find_layer_for_key("EXCL"), "raise_layer")
        
        # Test key that exists in multiple layers
        self.assertEqual(self.listener._find_layer_for_key("SPC"), "default_layer")
        
        # Test non-existent key
        self.assertIsNone(self.listener._find_layer_for_key("NONEXISTENT"))
    
    def test_get_current_layer_keys(self):
        """Test getting keys from current layer."""
        keys = self.listener._get_current_layer_keys()
        self.assertIn("Q", keys)
        self.assertIn("A", keys)
        self.assertIn("Z", keys)
        self.assertIn("SPC", keys)
    
    def test_is_printable_key(self):
        """Test printable key detection."""
        # Test printable keys
        self.assertTrue(self.listener._is_printable_key("a"))
        self.assertTrue(self.listener._is_printable_key("A"))
        self.assertTrue(self.listener._is_printable_key("1"))
        self.assertTrue(self.listener._is_printable_key("!"))
        
        # Test non-printable keys
        self.assertFalse(self.listener._is_printable_key("tab"))
        self.assertFalse(self.listener._is_printable_key("space"))
        self.assertFalse(self.listener._is_printable_key("ctrl"))
    
    def test_simulation_methods(self):
        """Test simulation methods for testing."""
        # Test key press simulation
        self.listener._on_press_simulation("Q")
        self.assertIn("Q", self.listener.pressed_keys)
        self.assertEqual(self.listener.current_layer, "default_layer")
        
        # Test key press simulation for key in different layer
        self.listener._on_press_simulation("N1")
        self.assertIn("N1", self.listener.pressed_keys)
        self.assertEqual(self.listener.current_layer, "lower_layer")
        
        # Test key release simulation
        self.listener._on_release_simulation("Q")
        self.assertNotIn("Q", self.listener.pressed_keys)
        self.assertIn("N1", self.listener.pressed_keys)  # Should still be pressed
    
    def test_automatic_layer_detection(self):
        """Test automatic layer detection."""
        # Start in default layer
        self.assertEqual(self.listener.current_layer, "default_layer")
        
        # Press key from lower layer
        self.listener._on_press_simulation("N1")
        self.assertEqual(self.listener.current_layer, "lower_layer")
        
        # Press key from raise layer
        self.listener._on_press_simulation("EXCL")
        self.assertEqual(self.listener.current_layer, "raise_layer")
        
        # Press key from default layer
        self.listener._on_press_simulation("Q")
        self.assertEqual(self.listener.current_layer, "default_layer")
    
    def test_get_methods(self):
        """Test getter methods."""
        self.listener._on_press_simulation("Q")
        self.listener._on_press_simulation("A")
        
        # Test that pressed keys are accessible
        self.assertIn("Q", self.listener.pressed_keys)
        self.assertIn("A", self.listener.pressed_keys)
        
        # Test current layer
        self.assertEqual(self.listener.current_layer, "default_layer")


if __name__ == '__main__':
    unittest.main() 
