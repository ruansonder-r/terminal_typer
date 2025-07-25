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
    print("-" * 40)
    
    # Use the example keymap file
    keymap_file = os.path.join("examples", "keymap.json")
    
    if not os.path.exists(keymap_file):
        print(f"Error: Keymap file not found at {keymap_file}")
        print("Please ensure the keymap.json file exists in the examples directory.")
        sys.exit(1)
    
    # Run the terminal interface
    interface = TerminalInterface(keymap_file)
    interface.run()

if __name__ == "__main__":
    main() 
