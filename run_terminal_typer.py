#!/usr/bin/env python3
"""
Terminal Typer - Main launcher script.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from terminal_interface import TerminalInterface

def main():
    """Main entry point."""
    print("Starting Terminal Typer...")
    print("Press Ctrl+C to exit")
    print("Press F4 to cycle through visual styles")
    print("-" * 40)
    
    # Use the example keymap file
    keymap_file = os.path.join("examples", "keymap.json")
    
    if not os.path.exists(keymap_file):
        print(f"Error: Keymap file not found at {keymap_file}")
        print("Please ensure the keymap.json file exists in the examples directory.")
        sys.exit(1)
    
    # Check for visual style argument
    visual_style = "bold"  # Default
    if len(sys.argv) > 1:
        visual_style = sys.argv[1]
        print(f"Using visual style: {visual_style}")
    
    # Available styles
    available_styles = ["bold", "reverse", "brackets", "symbols", "exclamation", "hash", "arrows", "stars"]
    
    if visual_style not in available_styles:
        print(f"Warning: Unknown visual style '{visual_style}'")
        print(f"Available styles: {', '.join(available_styles)}")
        print("Using default 'bold' style")
        visual_style = "bold"
    
    # Run the terminal interface
    interface = TerminalInterface(keymap_file, visual_style=visual_style)
    interface.run()

if __name__ == "__main__":
    main() 
