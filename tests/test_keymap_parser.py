#!/usr/bin/env python3
"""
Unit tests for the keymap parser functionality.

DEPRECATED: This tests the old JSON-based KeymapParser which is no longer used.
The application now uses CorneKeymapParser for DTS format keymaps.
These tests are kept for backward compatibility but should not be relied upon.
"""

import unittest
import sys
import os
import json
import tempfile
import warnings

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from keymap_parser import KeymapParser


class TestKeymapParser(unittest.TestCase):
    """Test cases for KeymapParser class.
    
    DEPRECATED: This tests the old JSON-based parser that is no longer used.
    The application now uses CorneKeymapParser for DTS format keymaps.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Show deprecation warning
        warnings.warn(
            "TestKeymapParser is deprecated. Use TestCorneKeymapParser instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Create a temporary keymap file for testing
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
                    ]
                }
            }
        }
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_keymap, self.temp_file)
        self.temp_file.close()
        
        self.parser = KeymapParser(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_file'):
            os.unlink(self.temp_file.name)
    
    def test_load_keymap(self):
        """Test loading a keymap file."""
        self.assertIsNotNone(self.parser.keymap_data)
        self.assertIn('keymap', self.parser.keymap_data)
        self.assertIn('layers', self.parser.keymap_data['keymap'])
    
    def test_get_layer_names(self):
        """Test getting layer names."""
        layer_names = self.parser.get_layer_names()
        expected_layers = ["default_layer", "lower_layer"]
        self.assertEqual(set(layer_names), set(expected_layers))
    
    def test_get_layer(self):
        """Test getting a specific layer."""
        default_layer = self.parser.get_layer("default_layer")
        self.assertIsNotNone(default_layer)
        self.assertEqual(len(default_layer), 4)  # 4 rows
        
        # Test non-existent layer
        non_existent = self.parser.get_layer("non_existent")
        self.assertIsNone(non_existent)
    
    def test_get_layer_keys(self):
        """Test getting layer keys."""
        default_keys = self.parser.get_layer_keys("default_layer")
        self.assertIsNotNone(default_keys)
        self.assertEqual(len(default_keys), 4)  # 4 rows
        
        # Check first row
        first_row = default_keys[0]
        expected_first_row = ["TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "BSPC"]
        self.assertEqual(first_row, expected_first_row)
    
    def test_parse_key_row(self):
        """Test parsing a key row."""
        test_row = "TAB Q W E R T Y U I O P BSPC"
        parsed = self.parser.parse_key_row(test_row)
        expected = ["TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "BSPC"]
        self.assertEqual(parsed, expected)
    
    def test_invalid_file(self):
        """Test handling of invalid file."""
        with self.assertRaises(Exception):
            KeymapParser("non_existent_file.json")
    
    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        # Create a file with invalid JSON
        invalid_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        invalid_file.write("invalid json content")
        invalid_file.close()
        
        with self.assertRaises(Exception):
            KeymapParser(invalid_file.name)
        
        os.unlink(invalid_file.name)


if __name__ == '__main__':
    unittest.main() 
