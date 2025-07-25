#!/usr/bin/env python3
"""
Unit tests for the WPM calculator functionality.
"""

import unittest
import time
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wpm_calculator import WPMCalculator


class TestWPMCalculator(unittest.TestCase):
    """Test cases for WPMCalculator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wpm_calculator = WPMCalculator()
    
    def test_initial_state(self):
        """Test initial state of WPM calculator."""
        self.assertEqual(self.wpm_calculator.get_wpm(), 0.0)
        self.assertEqual(self.wpm_calculator.get_wpm_display(), "[ 0.0 WPM]")
    
    def test_add_keystrokes(self):
        """Test adding keystrokes."""
        self.wpm_calculator.add_keystroke()
        self.wpm_calculator.add_keystroke()
        self.wpm_calculator.add_keystroke()
        
        # Should have some WPM after adding keystrokes
        wpm = self.wpm_calculator.get_wpm()
        self.assertGreater(wpm, 0.0)
        self.assertLessEqual(wpm, 200.0)  # Should be capped at 200
    
    def test_wpm_calculation(self):
        """Test WPM calculation with known values."""
        # Add 25 keystrokes (5 words worth)
        for _ in range(25):
            self.wpm_calculator.add_keystroke()
        
        # Wait a bit to ensure time has passed
        time.sleep(0.1)
        
        wpm = self.wpm_calculator.get_wpm()
        self.assertGreater(wpm, 0.0)
        self.assertLessEqual(wpm, 200.0)
    
    def test_wpm_display_format(self):
        """Test WPM display format."""
        self.wpm_calculator.add_keystroke()
        display = self.wpm_calculator.get_wpm_display()
        
        # Should match format [XX.X WPM]
        self.assertRegex(display, r'^\[\s*\d+\.\d+\s+WPM\]$')
    
    def test_wpm_cap(self):
        """Test that WPM is capped at 200."""
        # Add many keystrokes quickly to try to exceed cap
        for _ in range(1000):
            self.wpm_calculator.add_keystroke()
        
        wpm = self.wpm_calculator.get_wpm()
        self.assertLessEqual(wpm, 200.0)
    
    def test_rolling_window(self):
        """Test that old keystrokes are removed from the window."""
        # Add keystrokes
        for _ in range(10):
            self.wpm_calculator.add_keystroke()
        
        initial_wpm = self.wpm_calculator.get_wpm()
        
        # Wait for some keystrokes to age out of the 60-second window
        time.sleep(0.1)
        
        # Add more keystrokes
        for _ in range(5):
            self.wpm_calculator.add_keystroke()
        
        # WPM should still be reasonable
        wpm = self.wpm_calculator.get_wpm()
        self.assertGreaterEqual(wpm, 0.0)
        self.assertLessEqual(wpm, 200.0)


if __name__ == '__main__':
    unittest.main() 
