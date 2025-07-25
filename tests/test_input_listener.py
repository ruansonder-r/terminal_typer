#!/usr/bin/env python3
"""
Unit tests for the input listener functionality.
"""

import unittest
import sys
import os
import json
import tempfile

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from input_listener import InputListener
from keymap_parser import KeymapParser


class TestInputListener(unittest.TestCase):
    """Test cases for InputListener class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.listener = InputListener()
        
        # Create a test keymap for layer detection
        self.test_keymap = {
            "keymap": {
                "compatible": "zmk,keymap",
                "layers": {
                    "default_layer": [
                        "TAB Q W E R T Y U I O P BSPC",
                        "LCTRL A S D F G H J K L SEMI SQT",
                        "LSHFT Z X C V B N M COMMA DOT FSLH ESC",
                        "mo(1) LEFT_GUI SPACE RET LCTRL mo(2)"
                    ],
                    "lower_layer": [
                        "TAB N1 N2 N3 N4 N5 N6 N7 N8 N9 N0 BSPC",
                        "BT_CLR BT_SEL_0 BT_SEL_1 BT_SEL_2 BT_SEL_3 BT_SEL_4 LEFT DOWN UP RIGHT trans trans",
                        "LSHFT trans trans C_PREV C_PLAY_PAUSE C_NEXT HOME END C_VOLUME_UP C_VOL_DN C_MUTE TILDE",
                        "LGUI trans SPACE RET DEL RALT"
                    ],
                    "raise_layer": [
                        "TAB EXCL AT HASH DLLR PRCNT CARET AMPS ASTRK LPAR RPAR BSPC",
                        "LCTRL trans trans trans SCRL_LEFT SCRL_UP MINUS EQUAL LBKT RBKT BSLH GRAVE",
                        "LSHFT trans trans trans SCRL_RIGHT SCRL_DOWN UNDER PLUS LBRC RBRC PIPE TILDE",
                        "SCRL_DOWN LEFT_GUI SPACE RET trans RALT"
                    ]
                }
            }
        }
        
        # Create temporary keymap file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_keymap, self.temp_file)
        self.temp_file.close()
        
        self.parser = KeymapParser(self.temp_file.name)
        self.listener.set_keymap_parser(self.parser)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_file'):
            os.unlink(self.temp_file.name)
    
    def test_initial_state(self):
        """Test initial state of input listener."""
        self.assertEqual(len(self.listener.pressed_keys), 0)
        self.assertEqual(self.listener.current_layer, "default_layer")
        self.assertEqual(len(self.listener.layer_keys), 0)
        self.assertEqual(len(self.listener.unsupported_keys), 0)
    
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
        self.assertEqual(self.listener.layer_key_mapping.get('mo(1)'), 'lower_layer')
        self.assertEqual(self.listener.layer_key_mapping.get('mo(2)'), 'raise_layer')
    
    def test_find_layer_for_key(self):
        """Test finding which layer contains a key."""
        # Test keys from different layers
        self.assertEqual(self.listener._find_layer_for_key("Q"), "default_layer")
        self.assertEqual(self.listener._find_layer_for_key("N1"), "lower_layer")
        self.assertEqual(self.listener._find_layer_for_key("EXCL"), "raise_layer")
        
        # Test key that exists in multiple layers
        self.assertEqual(self.listener._find_layer_for_key("SPACE"), "default_layer")
        
        # Test non-existent key
        self.assertIsNone(self.listener._find_layer_for_key("NONEXISTENT"))
    
    def test_get_current_layer_keys(self):
        """Test getting keys from current layer."""
        keys = self.listener._get_current_layer_keys()
        self.assertIn("Q", keys)
        self.assertIn("A", keys)
        self.assertIn("Z", keys)
        self.assertIn("SPACE", keys)
    
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
        
        pressed_keys = self.listener.get_pressed_keys()
        self.assertIn("Q", pressed_keys)
        self.assertIn("A", pressed_keys)
        
        current_layer = self.listener.get_current_layer()
        self.assertEqual(current_layer, "default_layer")
        
        unsupported_keys = self.listener.get_unsupported_keys()
        self.assertEqual(len(unsupported_keys), 0)


if __name__ == '__main__':
    unittest.main() 
