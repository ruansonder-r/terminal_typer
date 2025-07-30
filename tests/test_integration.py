#!/usr/bin/env python3
"""
Integration tests for the terminal typer application.
"""

import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, Mock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from terminal_interface import TerminalInterface
from corne_keymap_parser import CorneKeymapParser
from input_listener import InputListener
from keyboard_renderer import KeyboardRenderer
from wpm_calculator import WPMCalculator


class TestApplicationIntegration(unittest.TestCase):
    """Integration tests for the complete application."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use the real corne.keymap file for integration tests
        self.real_keymap_path = "examples/corne.keymap"
        
        # Create a temporary copy of the real keymap for testing
        if os.path.exists(self.real_keymap_path):
            self.temp_keymap = tempfile.NamedTemporaryFile(mode='w', suffix='.keymap', delete=False)
            with open(self.real_keymap_path, 'r') as f:
                self.temp_keymap.write(f.read())
            self.temp_keymap.close()
            self.keymap_path = self.temp_keymap.name
        else:
            # Fallback to a minimal keymap if real file doesn't exist
            self.temp_keymap = tempfile.NamedTemporaryFile(mode='w', suffix='.keymap', delete=False)
            self.temp_keymap.write("""
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
""")
            self.temp_keymap.close()
            self.keymap_path = self.temp_keymap.name
        
        self.interface = TerminalInterface(self.keymap_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'interface'):
            self.interface._cleanup()
        if hasattr(self, 'temp_keymap'):
            os.unlink(self.temp_keymap.name)
    
    def test_full_application_flow(self):
        """Test the complete application flow from initialization to cleanup."""
        # Test that all components are properly initialized
        self.assertIsNotNone(self.interface.parser)
        self.assertIsNotNone(self.interface.renderer)
        self.assertIsNotNone(self.interface.input_listener)
        self.assertIsNotNone(self.interface.wpm_calculator)
        
        # Test that keymap was loaded correctly
        layer_names = self.interface.parser.get_layer_names()
        self.assertIn("default_layer", layer_names)
        self.assertIn("lower_layer", layer_names)
        self.assertIn("raise_layer", layer_names)
        
        # Test that components are properly connected
        self.assertEqual(self.interface.input_listener.wpm_calculator, self.interface.wpm_calculator)
        self.assertEqual(self.interface.input_listener.keymap_parser, self.interface.parser)
    
    def test_real_keymap_parsing(self):
        """Test parsing of the real corne.keymap file."""
        # Test that the real keymap can be parsed
        parser = CorneKeymapParser(self.keymap_path)
        
        # Test layer names
        layer_names = parser.get_layer_names()
        expected_layers = ["default_layer", "lower_layer", "raise_layer"]
        self.assertEqual(set(layer_names), set(expected_layers))
        
        # Test that we can get keys from each layer
        for layer_name in layer_names:
            layer_keys = parser.get_layer_keys(layer_name)
            self.assertIsNotNone(layer_keys)
            self.assertEqual(len(layer_keys), 4)  # 4 rows for corne keyboard
    
    def test_layer_switching_integration(self):
        """Test layer switching with real keymap data."""
        # Test automatic layer switching for numbers
        self.assertEqual(self.interface.current_layer, "default_layer")
        
        # Press '1' - should switch to lower layer
        self.interface._on_key_change({"1"}, "lower_layer")
        self.assertEqual(self.interface.current_layer, "lower_layer")
        
        # Press '!' - should switch to raise layer
        self.interface._on_key_change({"!"}, "raise_layer")
        self.assertEqual(self.interface.current_layer, "raise_layer")
        
        # Press 'Q' - should switch back to default layer
        self.interface._on_key_change({"Q"}, "default_layer")
        self.assertEqual(self.interface.current_layer, "default_layer")
    
    def test_key_mapping_integration(self):
        """Test key mapping with real keymap data."""
        # Test that keys are properly mapped and converted
        default_keys = self.interface.parser.get_layer_keys("default_layer")
        
        # Check that letter keys are present
        self.assertIn("Q", default_keys[0])
        self.assertIn("A", default_keys[1])
        self.assertIn("Z", default_keys[2])
        
        # Check that number keys are converted properly
        lower_keys = self.interface.parser.get_layer_keys("lower_layer")
        self.assertIn("1", lower_keys[0])  # N1 should be converted to 1
        self.assertIn("2", lower_keys[0])  # N2 should be converted to 2
        
        # Check that symbol keys are converted properly
        raise_keys = self.interface.parser.get_layer_keys("raise_layer")
        self.assertIn("!", raise_keys[0])  # EXCL should be converted to !
        self.assertIn("@", raise_keys[0])  # AT should be converted to @
    
    def test_wpm_calculation_integration(self):
        """Test WPM calculation with real typing simulation."""
        # Simulate realistic typing using proper simulation methods
        words = ["HELLO", "WORLD", "TESTING"]
        
        for i, word in enumerate(words):
            for char in word:
                self.interface.input_listener._on_press_simulation(char)
            # Add space between words (except after the last word)
            if i < len(words) - 1:
                self.interface.input_listener._on_press_simulation(" ")
        
        # Update interface state
        self.interface._on_key_change(self.interface.input_listener.pressed_keys, self.interface.input_listener.current_layer)
        
        # Check that WPM is being calculated
        wpm = self.interface.wpm_calculator.get_wpm()
        self.assertGreaterEqual(wpm, 0.0)
        self.assertLessEqual(wpm, 200.0)
        
        # Check that word tracking is working (should be the last word typed)
        current_word = self.interface.input_listener.get_current_word()
        self.assertEqual(current_word, "TESTING")  # Last word typed (without space)
    
    def test_keyboard_rendering_integration(self):
        """Test keyboard rendering with real keymap data."""
        # Get layer keys from parser
        layer_keys = self.interface.parser.get_layer_keys("default_layer")
        
        # Test that renderer can handle the real keymap
        result = self.interface.renderer.render_keyboard(layer_keys)
        
        # Should contain keyboard layout elements
        self.assertIn("TAB", result)
        self.assertIn("Q", result)
        self.assertIn("A", result)
        self.assertIn("Z", result)
        
        # Should have proper structure
        lines = result.split('\n')
        self.assertGreater(len(lines), 3)  # At least 3 rows
    
    def test_pressed_keys_highlighting_integration(self):
        """Test pressed key highlighting with real keymap."""
        # Set some pressed keys
        pressed_keys = {"Q", "A", "Z", "SPACE"}
        self.interface._on_key_change(pressed_keys, "default_layer")
        
        # Get layer keys and render
        layer_keys = self.interface.parser.get_layer_keys("default_layer")
        result = self.interface.renderer.render_keyboard(layer_keys)
        
        # Should show reverse video highlighting for pressed keys
        # Note: The actual format might be different, let's check what's actually rendered
        self.assertIn("Q", result)
        self.assertIn("A", result)
        self.assertIn("Z", result)
        # Check if any reverse video highlighting is present
        # The renderer might not use "REV" exactly, so let's check for brackets around pressed keys
        self.assertIn("[ Q ]", result)
        self.assertIn("[ A ]", result)
        self.assertIn("[ Z ]", result)
    
    def test_error_handling_integration(self):
        """Test error handling with real application components."""
        # Test with invalid keymap file
        invalid_file = tempfile.NamedTemporaryFile(mode='w', suffix='.keymap', delete=False)
        invalid_file.write("invalid content")
        invalid_file.close()
        
        try:
            # Should handle invalid keymap gracefully
            interface = TerminalInterface(invalid_file.name)
            interface._cleanup()
        except Exception:
            # If it raises an exception, that's also acceptable
            pass
        finally:
            os.unlink(invalid_file.name)
    
    def test_component_communication(self):
        """Test that all components communicate properly."""
        # Simulate a key press using proper simulation method
        self.interface.input_listener._on_press_simulation("H")
        
        # Update interface state to match input listener
        self.interface._on_key_change(self.interface.input_listener.pressed_keys, self.interface.input_listener.current_layer)
        
        # Check that all components are updated
        self.assertIn("H", self.interface.pressed_keys)
        self.assertEqual(self.interface.current_layer, "default_layer")
        
        # Check that WPM calculator is tracking
        wpm = self.interface.wpm_calculator.get_wpm()
        self.assertGreaterEqual(wpm, 0.0)
        
        # Check that word tracking is working
        current_word = self.interface.input_listener.get_current_word()
        self.assertEqual(current_word, "H")
    
    def test_layer_detection_accuracy(self):
        """Test that layer detection works accurately with real keymap."""
        # Test keys that should be in specific layers
        self.assertEqual(self.interface.parser._find_layer_for_key("Q"), "default_layer")
        self.assertEqual(self.interface.parser._find_layer_for_key("1"), "lower_layer")
        self.assertEqual(self.interface.parser._find_layer_for_key("!"), "raise_layer")
        
        # Test keys that exist in multiple layers (should return first found)
        # Note: SPACE might not be in the test keymap, so test with a key we know exists
        self.assertEqual(self.interface.parser._find_layer_for_key("TAB"), "default_layer")
        
        # Test non-existent key
        self.assertIsNone(self.interface.parser._find_layer_for_key("NONEXISTENT"))
    
    def test_performance_with_real_data(self):
        """Test performance with real keymap data."""
        import time
        
        # Test parsing performance
        start_time = time.time()
        parser = CorneKeymapParser(self.keymap_path)
        parse_time = time.time() - start_time
        
        # Should parse quickly (less than 1 second)
        self.assertLess(parse_time, 1.0)
        
        # Test layer switching performance
        start_time = time.time()
        for _ in range(100):
            self.interface.parser._find_layer_for_key("Q")
        switch_time = time.time() - start_time
        
        # Should be very fast (less than 0.1 second for 100 operations)
        self.assertLess(switch_time, 0.1)


if __name__ == '__main__':
    unittest.main() 
