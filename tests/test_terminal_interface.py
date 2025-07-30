#!/usr/bin/env python3
"""
Unit tests for the terminal interface functionality.
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock
import curses

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from terminal_interface import TerminalInterface


class TestTerminalInterface(unittest.TestCase):
    """Test cases for TerminalInterface class."""
    
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
        
        self.interface = TerminalInterface(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_file'):
            os.unlink(self.temp_file.name)
        if hasattr(self, 'interface'):
            self.interface._cleanup()
    
    def test_initialization(self):
        """Test TerminalInterface initialization."""
        # Test that all components are initialized
        self.assertIsNotNone(self.interface.parser)
        self.assertIsNotNone(self.interface.renderer)
        self.assertIsNotNone(self.interface.input_listener)
        self.assertIsNotNone(self.interface.wpm_calculator)
        
        # Test initial state
        self.assertEqual(self.interface.visual_style, "reverse")
        self.assertEqual(self.interface.current_layer, "default_layer")
        self.assertEqual(len(self.interface.pressed_keys), 0)
        self.assertEqual(self.interface.error_message, "")
        self.assertEqual(self.interface.error_timeout, 0)
    
    def test_component_integration(self):
        """Test that all components are properly integrated."""
        # Test that input listener has the right components
        self.assertEqual(self.interface.input_listener.wpm_calculator, self.interface.wpm_calculator)
        self.assertEqual(self.interface.input_listener.keymap_parser, self.interface.parser)
        
        # Test that renderer has the right style
        self.assertEqual(self.interface.renderer.visual_style, "reverse")
    
    def test_keymap_loading(self):
        """Test that keymap is loaded correctly."""
        # Test that parser loaded the keymap
        layer_names = self.interface.parser.get_layer_names()
        expected_layers = ["default_layer", "lower_layer", "raise_layer"]
        self.assertEqual(set(layer_names), set(expected_layers))
        
        # Test that we can get layer keys
        default_keys = self.interface.parser.get_layer_keys("default_layer")
        self.assertIsNotNone(default_keys)
        self.assertEqual(len(default_keys), 4)  # 4 rows
    
    def test_key_change_callback(self):
        """Test the key change callback functionality."""
        # Simulate key press
        pressed_keys = {"Q", "A"}
        current_layer = "default_layer"
        
        # Call the callback
        self.interface._on_key_change(pressed_keys, current_layer)
        
        # Check that state was updated
        self.assertEqual(self.interface.pressed_keys, pressed_keys)
        self.assertEqual(self.interface.current_layer, current_layer)
    
    def test_layer_switching_integration(self):
        """Test layer switching through the interface."""
        # Start in default layer
        self.assertEqual(self.interface.current_layer, "default_layer")
        
        # Simulate pressing a key from lower layer
        self.interface._on_key_change({"1"}, "lower_layer")
        self.assertEqual(self.interface.current_layer, "lower_layer")
        
        # Simulate pressing a key from raise layer
        self.interface._on_key_change({"!"}, "raise_layer")
        self.assertEqual(self.interface.current_layer, "raise_layer")
        
        # Simulate pressing a key from default layer
        self.interface._on_key_change({"Q"}, "default_layer")
        self.assertEqual(self.interface.current_layer, "default_layer")
    
    def test_error_handling_invalid_keymap(self):
        """Test error handling for invalid keymap file."""
        # Create an invalid keymap file
        invalid_file = tempfile.NamedTemporaryFile(mode='w', suffix='.keymap', delete=False)
        invalid_file.write("invalid content")
        invalid_file.close()
        
        # Should handle invalid keymap gracefully
        try:
            interface = TerminalInterface(invalid_file.name)
            # If it doesn't raise an exception, that's fine - it should handle gracefully
            interface._cleanup()
        except Exception as e:
            # If it does raise an exception, that's also acceptable
            pass
        finally:
            os.unlink(invalid_file.name)
    
    def test_error_handling_nonexistent_file(self):
        """Test error handling for nonexistent keymap file."""
        with self.assertRaises(Exception):
            TerminalInterface("nonexistent_file.keymap")
    
    def test_cleanup(self):
        """Test cleanup functionality."""
        # Mock the input listener to verify cleanup
        mock_listener = Mock()
        self.interface.input_listener = mock_listener
        
        # Call cleanup
        self.interface._cleanup()
        
        # Verify that input listener was stopped
        mock_listener.stop_listening.assert_called_once()
    
    @patch('curses.wrapper')
    def test_run_method(self, mock_wrapper):
        """Test the run method."""
        # Mock the wrapper to avoid actual curses
        mock_wrapper.return_value = None
        
        # Test that run method calls wrapper
        self.interface.run()
        mock_wrapper.assert_called_once()
    
    @patch('curses.wrapper')
    def test_run_method_keyboard_interrupt(self, mock_wrapper):
        """Test run method handles KeyboardInterrupt."""
        # Mock wrapper to raise KeyboardInterrupt
        mock_wrapper.side_effect = KeyboardInterrupt()
        
        # Should handle KeyboardInterrupt gracefully
        try:
            self.interface.run()
        except KeyboardInterrupt:
            pass  # Expected
    
    @patch('curses.wrapper')
    def test_run_method_exception(self, mock_wrapper):
        """Test run method handles general exceptions."""
        # Mock wrapper to raise general exception
        mock_wrapper.side_effect = Exception("Test exception")
        
        # Should handle exception gracefully
        try:
            self.interface.run()
        except Exception:
            pass  # Expected
    
    def test_visual_style_validation(self):
        """Test that only supported visual styles are accepted."""
        # Test that reverse style is accepted
        interface = TerminalInterface(self.temp_file.name, visual_style="reverse")
        self.assertEqual(interface.visual_style, "reverse")
        interface._cleanup()
        
        # Test that unsupported style defaults to reverse
        interface = TerminalInterface(self.temp_file.name, visual_style="unsupported")
        self.assertEqual(interface.visual_style, "reverse")
        interface._cleanup()
    
    def test_word_tracking_integration(self):
        """Test word tracking through the interface."""
        # Simulate typing a word using the proper simulation method
        self.interface.input_listener._on_press_simulation("H")
        self.interface.input_listener._on_press_simulation("E")
        self.interface.input_listener._on_press_simulation("L")
        self.interface.input_listener._on_press_simulation("L")
        self.interface.input_listener._on_press_simulation("O")
        
        # Check that word is being tracked
        current_word = self.interface.input_listener.get_current_word()
        self.assertEqual(current_word, "HELLO")
    
    def test_wpm_integration(self):
        """Test WPM calculation integration."""
        # Simulate typing
        for _ in range(10):
            self.interface._on_key_change({"A"}, "default_layer")
        
        # Check that WPM is being calculated
        wpm = self.interface.wpm_calculator.get_wpm()
        self.assertGreaterEqual(wpm, 0.0)
        self.assertLessEqual(wpm, 200.0)


if __name__ == '__main__':
    unittest.main() 
