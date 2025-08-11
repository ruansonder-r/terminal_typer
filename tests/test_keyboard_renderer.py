#!/usr/bin/env python3
"""
Unit tests for the keyboard renderer functionality.
"""

import unittest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from keyboard_renderer import KeyboardRenderer
from wpm_calculator import WPMCalculator


class TestKeyboardRenderer(unittest.TestCase):
    """Test cases for KeyboardRenderer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.renderer = KeyboardRenderer()
        self.wpm_calculator = WPMCalculator()
        
        # Test layer keys
        self.test_layer_keys = [
            ["TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "BSP"],
            ["CTL", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'"],
            ["SFT", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "ESC"],
            ["LWR", "LEF", "SPC", "RET", "CTL", "RSE"]
        ]
    
    def test_initial_state(self):
        """Test initial state of renderer."""
        self.assertEqual(self.renderer.visual_style, "reverse")
        self.assertEqual(len(self.renderer.pressed_keys), 0)
        self.assertIsNone(self.renderer.wpm_calculator)
    
    def test_get_key_display(self):
        """Test key display mapping."""
        # Test letters
        self.assertEqual(self.renderer.get_key_display("Q"), "Q")
        self.assertEqual(self.renderer.get_key_display("A"), "A")
        self.assertEqual(self.renderer.get_key_display("Z"), "Z")
        
        # Test numbers
        self.assertEqual(self.renderer.get_key_display("N1"), "1")
        self.assertEqual(self.renderer.get_key_display("N0"), "0")
        
        # Test symbols
        self.assertEqual(self.renderer.get_key_display("EXCL"), "!")
        self.assertEqual(self.renderer.get_key_display("AT"), "@")
        
        # Test special keys
        self.assertEqual(self.renderer.get_key_display("TAB"), "TAB")
        self.assertEqual(self.renderer.get_key_display("SPACE"), "SPC")
        
        # Test unknown keys
        self.assertEqual(self.renderer.get_key_display("UNKNOWN"), "UNK")
    
    def test_set_pressed_keys(self):
        """Test setting pressed keys."""
        pressed_keys = {"Q", "A", "Z"}
        self.renderer.set_pressed_keys(pressed_keys)
        self.assertEqual(self.renderer.pressed_keys, pressed_keys)
    
    def test_render_keyboard_basic(self):
        """Test basic keyboard rendering."""
        result = self.renderer.render_keyboard(self.test_layer_keys)
        
        # Should contain the keyboard layout
        self.assertIn("[TAB]", result)
        self.assertIn("[ Q ]", result)
        self.assertIn("[ A ]", result)
        self.assertIn("[ Z ]", result)
        
        # Should have proper structure
        lines = result.split('\n')
        self.assertGreater(len(lines), 3)  # At least 3 rows
    
    def test_render_keyboard_with_pressed_keys(self):
        """Test keyboard rendering with pressed keys."""
        pressed_keys = {"Q", "A", "Z", "SPC"}
        self.renderer.set_pressed_keys(pressed_keys)
        
        result = self.renderer.render_keyboard(self.test_layer_keys)
        
        # Should show reverse video highlighting for pressed keys
        self.assertIn("REV[ Q ]REV", result)
        self.assertIn("REV[ A ]REV", result)
        self.assertIn("REV[ Z ]REV", result)
        self.assertIn("REV[SPC]REV", result)
        
        # Non-pressed keys should not be reverse video
        self.assertIn("[ W ]", result)
        self.assertNotIn("REV[ W ]REV", result)
    
    def test_render_keyboard_with_wpm(self):
        """Test keyboard rendering with WPM calculator."""
        self.renderer.set_wpm_calculator(self.wpm_calculator)
        
        # Add some keystrokes
        for _ in range(10):
            self.wpm_calculator.add_keystroke()
        
        result = self.renderer.render_keyboard(self.test_layer_keys)
        
        # Should contain WPM display
        self.assertIn("WPM", result)
    
    def test_empty_layer_keys(self):
        """Test rendering with empty layer keys."""
        result = self.renderer.render_keyboard([])
        self.assertEqual(result, "No keys to render")
    
    def test_ergonomic_staggering(self):
        """Test that ergonomic staggering is applied correctly."""
        result = self.renderer.render_keyboard(self.test_layer_keys)
        lines = result.split('\n')
        
        # Should have progressive indentation
        # First row: no indentation
        # Second row: 2 spaces indentation
        # Third row: 4 spaces indentation
        
        # Check that indentation is present
        self.assertGreater(len(lines), 2)
        
        # Second row should have some indentation
        if len(lines) > 1:
            second_line = lines[1]
            self.assertTrue(second_line.startswith("  ") or second_line.startswith("\t"))
    
    def test_thumb_row_rendering(self):
        """Test thumb row rendering."""
        result = self.renderer.render_keyboard(self.test_layer_keys)
        
        # Should contain thumb row elements
        self.assertIn("[SPC]", result)
        self.assertIn("[RET]", result)
        self.assertIn("[LWR]", result)
        self.assertIn("[RSE]", result)

    def test_transparent_keys_formatting(self):
        """Test that transparent keys are handled properly without breaking formatting."""
        # Create a layer with transparent keys
        layer_keys_with_trans = [
            ["TAB", "TRANS", "W", "TRANS", "R", "T", "Y", "U", "I", "O", "P", "BSPC"],
            ["LCTRL", "A", "TRANS", "D", "TRANS", "G", "H", "J", "K", "L", "SEMI", "'"],
            ["LSHFT", "Z", "X", "TRANS", "V", "B", "N", "M", "COMMA", "DOT", "FSLH", "ESC"],
            ["L1", "LEFT_GUI", "SPACE", "RET", "LCTRL", "L2"]
        ]
        
        result = self.renderer.render_keyboard(layer_keys_with_trans)
        
        # Should render without errors
        self.assertIsNotNone(result)
        self.assertNotEqual(result, "No keys to render")
        
        # Should have proper structure (4 lines)
        lines = result.split('\n')
        self.assertEqual(len(lines), 4)
        
        # Should contain the expected keys
        self.assertIn("TAB", result)
        self.assertIn("W", result)
        self.assertIn("R", result)
        
        # Should not contain "TRANS" in the rendered output
        self.assertNotIn("TRANS", result)
        
        # Should have proper spacing for transparent keys
        # Check that there are empty spaces where transparent keys should be
        self.assertIn("     ", result)  # Empty spaces for transparent keys


if __name__ == '__main__':
    unittest.main() 
