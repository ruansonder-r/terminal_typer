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
from corne_keymap_parser import CorneKeymapParser
from wpm_calculator import WPMCalculator

class TestInputListener(unittest.TestCase):
    """Test cases for InputListener class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary keymap file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.keymap')
        keymap_content = """
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
&kp LCTRL  &kp A  &kp S  &kp D  &kp F  &kp G  &kp H  &kp J  &kp K  &kp L  &kp SEMI  &kp SQT
&kp LSHFT  &kp Z  &kp X  &kp C  &kp V  &kp B  &kp N  &kp M  &kp COMMA  &kp DOT  &kp FSLH  &kp ESC
                         &mo 1  &kp LEFT_GUI  &kp SPACE  &kp RET  &kp LCTRL  &mo 2
            >;
        };

        raise_layer {
            bindings = <
&kp TAB  &kp EXCL  &kp AT  &kp HASH  &kp DLLR  &kp PRCNT  &kp CARET  &kp AMPS  &kp ASTRK  &kp LPAR  &kp RPAR  &kp BSPC
&kp LCTRL  &kp A  &kp S  &kp D  &kp F  &kp G  &kp H  &kp J  &kp K  &kp L  &kp SEMI  &kp SQT
&kp LSHFT  &kp Z  &kp X  &kp C  &kp V  &kp B  &kp N  &kp M  &kp COMMA  &kp DOT  &kp FSLH  &kp ESC
                         &mo 1  &kp LEFT_GUI  &kp SPACE  &kp RET  &kp LCTRL  &mo 2
            >;
        };
    };
};
"""
        self.temp_file.write(keymap_content)
        self.temp_file.close()
        
        # Create input listener with test keymap
        self.listener = InputListener()
        self.keymap_parser = CorneKeymapParser(self.temp_file.name)
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
        
        # Test number mapping (updated to display names)
        self.assertEqual(self.listener.key_mapping.get('1'), '1')
        self.assertEqual(self.listener.key_mapping.get('0'), '0')
        
        # Test symbol mapping (updated to display names)
        self.assertEqual(self.listener.key_mapping.get('!'), '!')
        self.assertEqual(self.listener.key_mapping.get('@'), '@')
        
        # Test special key mapping
        self.assertEqual(self.listener.key_mapping.get('space'), 'SPACE')
        self.assertEqual(self.listener.key_mapping.get('tab'), 'TAB')
    
    def test_layer_key_mapping(self):
        """Test layer key mapping."""
        # Test that F1 and F2 are mapped to layer keys (updated format)
        self.assertEqual(self.listener.key_mapping.get('f1'), 'L1')
        self.assertEqual(self.listener.key_mapping.get('f2'), 'L2')
    
    def test_find_layer_for_key(self):
        """Test finding which layer contains a key."""
        # Test keys from different layers
        self.assertEqual(self.listener._find_layer_for_key("Q"), "default_layer")
        self.assertEqual(self.listener._find_layer_for_key("1"), "lower_layer")
        self.assertEqual(self.listener._find_layer_for_key("!"), "raise_layer")
        
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
        self.listener._on_press_simulation("1")
        self.assertIn("1", self.listener.pressed_keys)
        self.assertEqual(self.listener.current_layer, "lower_layer")
        
        # Test key release simulation
        self.listener._on_release_simulation("Q")
        self.assertNotIn("Q", self.listener.pressed_keys)
        self.assertIn("1", self.listener.pressed_keys)  # Should still be pressed
    
    def test_automatic_layer_detection(self):
        """Test automatic layer detection."""
        # Start in default layer
        self.assertEqual(self.listener.current_layer, "default_layer")
        
        # Press key from lower layer
        self.listener._on_press_simulation("1")
        self.assertEqual(self.listener.current_layer, "lower_layer")
        
        # Press key from raise layer
        self.listener._on_press_simulation("!")
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
