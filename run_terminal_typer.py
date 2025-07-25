#!/usr/bin/env python3
"""
Terminal Typer - Real-time keyboard visualization tool for split ergonomic keyboards.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from terminal_interface import TerminalInterface

def main():
    """Main entry point for the terminal typer application."""
    print("Starting Terminal Typer...")
    print("Press Ctrl+C to exit")
    print("----------------------------------------")
    
    # Default to reverse video mode
    visual_style = "reverse"
    
    # Check if a visual style was provided as command line argument
    if len(sys.argv) > 1:
        if sys.argv[1] == "reverse":
            visual_style = sys.argv[1]
            print(f"Using visual style: {visual_style}")
        else:
            print(f"Warning: Only 'reverse' visual style is supported")
            print("Using default 'reverse' style")
    
    # Keymap file path
    keymap_file = "examples/keymap.json"
    
    # Check if keymap file exists
    if not os.path.exists(keymap_file):
        print(f"Error: Keymap file '{keymap_file}' not found!")
        print("Please ensure the keymap file exists in the examples directory.")
        sys.exit(1)
    
    # Create and run the interface
    interface = TerminalInterface(keymap_file, visual_style=visual_style)
    interface.run()

if __name__ == "__main__":
    main() 
