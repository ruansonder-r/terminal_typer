#!/usr/bin/env python3
"""
Unit tests for the corne keymap parser functionality.
"""

import unittest
import sys
import os
import tempfile

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from corne_keymap_parser import CorneKeymapParser


class TestCorneKeymapParser(unittest.TestCase):
    """Test cases for CorneKeymapParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary keymap file for testing
        self.keymap_content = """
/ {
    keymap {
        compatible = "zmk,keymap";

        default_layer {
            bindings = <
&kp TAB    &kp Q  &kp W  &kp E  &kp R  &kp T  &kp Y  &kp U  &kp I  &kp O  &kp P  &kp BSPC
&kp LCTRL  &kp A  &kp S  &kp D  &kp F  &kp G  &kp H  &kp J  &kp K  &kp L  &kp SEMI  &kp SQT
&kp LSHFT  &kp Z  &kp X  &kp C  &kp V  &kp B  &kp N  &kp M  &kp COMMA  &kp DOT  &kp FSLH  &kp ESC
                         &mo 1  &kp LEFT_GUI  &kp SPACE  &kp RET  &kp LCTRL  &mo 2
            >;
        };

        lower_layer {
            bindings = <
&kp TAB  &kp N1  &kp N2  &kp N3  &kp N4  &kp N5  &kp N6  &kp N7  &kp N8  &kp N9  &kp N0  &kp BSPC
&bt BT_CLR  &bt BT_SEL 0  &bt BT_SEL 1  &bt BT_SEL 2  &bt BT_SEL 3  &bt BT_SEL 4  &kp LEFT  &kp DOWN  &kp UP  &kp RIGHT  &trans  &trans
&kp LSHFT  &trans  &trans  &kp C_PREV  &kp C_PLAY_PAUSE  &kp C_NEXT  &kp HOME  &kp END  &kp C_VOLUME_UP  &kp C_VOL_DN  &kp C_MUTE  &kp TILDE
                                        &kp LGUI  &kp LCTRL  &kp SPACE  &kp RET  &kp DEL  &kp RALT
            >;
        };

        raise_layer {
            bindings = <
&kp TAB  &kp EXCL  &kp AT  &kp HASH  &kp DLLR  &kp PRCNT  &kp CARET  &kp AMPS  &kp ASTRK  &kp LPAR  &kp RPAR  &kp BSPC
&kp LCTRL  &trans  &trans  &trans  &msc SCRL_LEFT  &msc SCRL_UP  &kp MINUS  &kp EQUAL  &kp LBKT  &kp RBKT  &kp BSLH  &kp GRAVE
&kp LSHFT  &trans  &trans  &trans  &msc SCRL_RIGHT  &msc SCRL_DOWN  &kp UNDER  &kp PLUS  &kp LBRC  &kp RBRC  &kp PIPE  &kp TILDE
                             &msc SCRL_DOWN  &kp LEFT_GUI  &kp SPACE  &kp RET  &trans  &kp RALT
            >;
        };
    };
};
"""
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.keymap', delete=False)
        self.temp_file.write(self.keymap_content)
        self.temp_file.close()
        
        self.parser = CorneKeymapParser(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_file'):
            os.unlink(self.temp_file.name)
    
    def test_load_keymap(self):
        """Test loading a keymap file."""
        self.assertIsNotNone(self.parser.layers)
        self.assertIn('default_layer', self.parser.layers)
        self.assertIn('lower_layer', self.parser.layers)
        self.assertIn('raise_layer', self.parser.layers)
    
    def test_get_layer_names(self):
        """Test getting layer names."""
        layer_names = self.parser.get_layer_names()
        expected_layers = ["default_layer", "lower_layer", "raise_layer"]
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
            CorneKeymapParser("non_existent_file.keymap")
    
    def test_invalid_keymap_format(self):
        """Test handling of invalid keymap format."""
        # Create a file with invalid content
        invalid_file = tempfile.NamedTemporaryFile(mode='w', suffix='.keymap', delete=False)
        invalid_file.write("invalid content")
        invalid_file.close()
        
        # The parser should handle invalid content gracefully by not finding any layers
        parser = CorneKeymapParser(invalid_file.name)
        self.assertEqual(len(parser.get_layer_names()), 0)
        
        os.unlink(invalid_file.name)
    
    def test_find_layer_for_key(self):
        """Test finding which layer contains a key."""
        # Test keys from different layers
        self.assertEqual(self.parser._find_layer_for_key("Q"), "default_layer")
        self.assertEqual(self.parser._find_layer_for_key("1"), "lower_layer")
        self.assertEqual(self.parser._find_layer_for_key("!"), "raise_layer")
        
        # Test non-existent key
        self.assertIsNone(self.parser._find_layer_for_key("NONEXISTENT"))
    
    def test_key_conversion(self):
        """Test key name conversion."""
        # Test that ZMK key names are converted to display names
        lower_keys = self.parser.get_layer_keys("lower_layer")
        self.assertIn("1", lower_keys[0])  # N1 should be converted to 1
        self.assertIn("2", lower_keys[0])  # N2 should be converted to 2
        
        raise_keys = self.parser.get_layer_keys("raise_layer")
        self.assertIn("!", raise_keys[0])  # EXCL should be converted to !
        self.assertIn("@", raise_keys[0])  # AT should be converted to @


if __name__ == '__main__':
    unittest.main() 
