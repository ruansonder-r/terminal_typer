import curses
import signal
import sys
from typing import Set, Optional
from keymap_parser import KeymapParser
from keyboard_renderer import KeyboardRenderer
from input_listener import InputListener
from wpm_calculator import WPMCalculator

class TerminalInterface:
    """
    Terminal interface using curses for real-time keyboard visualization.
    Provides dynamic display of keyboard layout with keypress highlighting.
    """
    
    def __init__(self, keymap_file: str, visual_style: str = "reverse"):
        """
        Initialize the terminal interface.
        
        Args:
            keymap_file: Path to the ZMK keymap JSON file
            visual_style: Visual style for pressed keys (only "reverse" supported)
        """
        self.keymap_file = keymap_file
        self.visual_style = "reverse"  # Only reverse video mode supported
        
        # Initialize components
        self.parser = None
        self.renderer = None
        self.input_listener = None
        self.wpm_calculator = None
        
        # State
        self.pressed_keys: Set[str] = set()
        self.current_layer = "default_layer"
        self.screen = None
        self.error_message = ""
        self.error_timeout = 0
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize all components."""
        # Initialize parser
        self.parser = KeymapParser(self.keymap_file)
        
        # Initialize renderer with reverse video style
        self.renderer = KeyboardRenderer(visual_style="reverse")
        
        # Initialize WPM calculator
        self.wpm_calculator = WPMCalculator()
        
        # Initialize input listener
        self.input_listener = InputListener()
        self.input_listener.set_wpm_calculator(self.wpm_calculator)
        self.input_listener.set_keymap_parser(self.parser)
    
    def run(self) -> None:
        """Start the terminal interface."""
        try:
            # Start curses interface
            curses.wrapper(self._main_loop)
            
        except KeyboardInterrupt:
            print("\nExiting...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self._cleanup()
    
    def _main_loop(self, screen) -> None:
        """Main curses loop."""
        self.screen = screen
        self.is_running = True
        
        # Setup curses
        curses.curs_set(0)  # Hide cursor
        curses.noecho()     # Don't echo keypresses
        curses.cbreak()     # Immediate key input
        
        # Enable colors if available
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_RED, -1)      # Error messages
            curses.init_pair(2, curses.COLOR_GREEN, -1)    # Success messages
            curses.init_pair(3, curses.COLOR_YELLOW, -1)   # Warnings
        
        # Start input listener
        self.input_listener.start_listening(self._on_key_change)
        
        # Main display loop
        while self.is_running:
            try:
                self._update_display()
                curses.napms(50)  # 50ms refresh rate
            except KeyboardInterrupt:
                break
            except Exception as e:
                self._show_error(f"Display error: {e}")
    
    def _on_key_change(self, pressed_keys: Set[str], current_layer: str) -> None:
        """Callback for key state changes."""
        self.pressed_keys = pressed_keys
        self.current_layer = current_layer
        
        # Check for Ctrl+C to exit
        if 'LCTRL' in pressed_keys and 'C' in pressed_keys:
            self.is_running = False
    
    def _update_display(self) -> None:
        """Update the terminal display."""
        if not self.screen:
            return
        
        # Clear screen
        self.screen.clear()
        
        # Get terminal dimensions
        max_y, max_x = self.screen.getmaxyx()
        
        # Display current word at the top
        self._display_current_word(0)
        
        # Render keyboard layout starting below the word display
        self._render_keyboard_layout(2)
        
        # Refresh screen
        self.screen.refresh()
    
    def _display_current_word(self, start_y: int) -> None:
        """Display the current word being typed."""
        if not self.input_listener:
            return
        
        current_word = self.input_listener.get_current_word()
        
        # Create the word display line with space and period symbols
        if current_word:
            word_display = f" {current_word} "
        else:
            word_display = " "
        
        # Calculate keyboard center position based on actual layout
        # From analysis: middle row is 85 characters, center is at position 42
        keyboard_center = 42
        
        # Center the word relative to the keyboard center
        word_x = max(0, keyboard_center - (len(word_display) // 2))
        
        # Display the word
        if self.screen and start_y < curses.LINES - 1:
            self.screen.addstr(start_y, word_x, word_display)
    
    def _render_keyboard_layout(self, start_y: int) -> None:
        """Render the keyboard layout at the specified Y position."""
        if not self.parser or not self.renderer:
            return
        
        # Get current layer keys
        layer_keys = self.parser.get_layer_keys(self.current_layer)
        if not layer_keys:
            return
        
        # Set pressed keys in renderer
        self.renderer.set_pressed_keys(self.pressed_keys)
        
        # Render keyboard
        keyboard_ascii = self.renderer.render_keyboard(layer_keys, self.current_layer)
        
        # Split into lines and display with reverse video formatting
        lines = keyboard_ascii.split('\n')
        for i, line in enumerate(lines):
            if start_y + i < curses.LINES - 1:  # Leave just 1 line for safety
                self._display_line_with_reverse(start_y + i, 0, line)
    
    def _display_line_with_reverse(self, y: int, x: int, line: str) -> None:
        """
        Display a line with reverse video formatting for pressed keys.
        
        Args:
            y: Y position on screen
            x: X position on screen
            line: Line to display
        """
        if not self.screen:
            return
        
        # Handle reverse video formatting
        if "REV" in line:
            # Reverse video style: REV[key]REV
            self._display_reverse_style(y, x, line)
        else:
            # Normal text
            self.screen.addstr(y, x, line)
    
    def _display_reverse_style(self, y: int, x: int, line: str) -> None:
        """Display line with reverse video formatting for REV markers."""
        # Split the line by REV markers
        parts = line.split('REV')
        current_x = x
        
        for i, part in enumerate(parts):
            if part:  # Skip empty parts
                # Apply reverse video formatting for odd-indexed parts (between REV markers)
                if i % 2 == 1:  # This part should be reverse video
                    self.screen.addstr(y, current_x, part, curses.A_REVERSE)
                else:  # This part should be normal
                    self.screen.addstr(y, current_x, part)
                current_x += len(part)
    
    def _show_error(self, message: str) -> None:
        """Show an error message."""
        self.error_message = message
        self.error_timeout = 20  # Show for 20 refresh cycles (~1 second)
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        if self.input_listener:
            self.input_listener.stop_listening()
        
        if self.screen:
            curses.endwin()
    
    def _handle_resize(self, signum, frame) -> None:
        """Handle terminal resize."""
        if self.screen:
            curses.endwin()
            self.screen.refresh()

def main():
    """Main entry point for the terminal interface."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python terminal_interface.py <keymap_file>")
        sys.exit(1)
    
    keymap_file = sys.argv[1]
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGWINCH, lambda s, f: None)  # Ignore resize for now
    
    # Run the interface
    interface = TerminalInterface(keymap_file)
    interface.run()

if __name__ == "__main__":
    main() 
