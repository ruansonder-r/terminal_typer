# Terminal Typer

A Python tool for visualizing split ergonomic keyboard layouts and training keypresses. This tool parses ZMK keymap files and renders ASCII art representations of the keyboard layout with real-time keypress visualization.

## Current Status: Phase 2 - Real-time Input Capture and Terminal Interface

### Features Implemented

- **KeymapParser**: Parses ZMK keymap JSON files
- **KeyboardRenderer**: Generates ASCII art keyboard layouts
- **InputListener**: Captures global keyboard input using pynput
- **TerminalInterface**: Real-time terminal interface using curses
- **WPMCalculator**: Real-time Words Per Minute (WPM) calculation
- **Key highlighting**: Shows which keys are currently pressed
- **Layer support**: Handles multiple keyboard layers (default, lower, raise)
- **Real-time visualization**: Dynamic updates as you type
- **Automatic layer detection**: Automatically switches to the layer containing a pressed key
- **Layer switching**: Temporary layer switching with F1/F2 keys
- **WPM counter**: Real-time typing speed display between keyboard halves
- **Error handling**: Graceful handling of unsupported keys

### Files

- `keymap_parser.py`: Core parser for ZMK keymap files
- `keyboard_renderer.py`: ASCII art renderer for keyboard layouts
- `input_listener.py`: Global keyboard input capture with automatic layer detection
- `terminal_interface.py`: Curses-based terminal interface
- `wpm_calculator.py`: Real-time WPM calculation and tracking
- `run_terminal_typer.py`: Simple launcher script
- `test_phase2.py`: Phase 2 component tests
- `test_wpm.py`: WPM calculator tests
- `test_complete_wpm.py`: Complete WPM integration tests
- `test_bold_highlighting.py`: Bold highlighting format tests
- `test_auto_layer_detection.py`: Automatic layer detection tests
- `test_clean_interface.py`: Clean interface display tests
- `keymap.json`: Example ZMK keymap file
- `requirements.txt`: Python dependencies

### Quick Start

1. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Run the terminal interface**:
   ```bash
   python3 run_terminal_typer.py
   ```

3. **Test components**:
   ```bash
   python3 test_phase2.py
   python3 test_wpm.py
   ```

### Usage

#### Running the Full Interface

```bash
# Simple launcher (uses keymap.json in current directory)
python3 run_terminal_typer.py

# Direct interface with custom keymap file
python3 terminal_interface.py path/to/your/keymap.json
```

#### Testing Components

```bash
# Test all Phase 2 components
python3 test_phase2.py

# Test input listener (press keys for 10 seconds)
python3 test_phase2.py --test-input
```

#### Using in Your Own Code

```python
from keymap_parser import KeymapParser
from keyboard_renderer import KeyboardRenderer
from input_listener import InputListener

# Load keymap
parser = KeymapParser("keymap.json")

# Create renderer
renderer = KeyboardRenderer()

# Create input listener
listener = InputListener()

# Set up callback for key changes
def on_key_change(pressed_keys, current_layer):
    print(f"Pressed: {pressed_keys}, Layer: {current_layer}")
    
    # Render keyboard with pressed keys
    layer_keys = parser.get_layer_keys(current_layer)
    renderer.set_pressed_keys(pressed_keys)
    keyboard_ascii = renderer.render_keyboard(layer_keys, current_layer)
    print(keyboard_ascii)

# Start listening
listener.start_listening(on_key_change)

# Keep running
import time
time.sleep(60)  # Run for 60 seconds

# Stop listening
listener.stop_listening()
```

### Key Features

#### Real-time Input Capture
- Global keyboard input capture using pynput
- Maps physical keypresses to ZMK key names
- Supports letters, numbers, symbols, and special keys
- Handles unsupported keys gracefully

#### Multiple Visual Styles for Pressed Keys
- **Bold**: `**key**` (default style)
- **Reverse Video**: `[key]` with reverse video highlighting
- **Brackets**: `<key>` instead of `[key]`
- **Symbols**: `[★key★]` with star symbols
- **Exclamation**: `[!key!]` with exclamation marks
- **Hash**: `[#key#]` with hash symbols
- **Arrows**: `[▶key◀]` with arrow symbols
- **Stars**: `[*key*]` with asterisks

**Usage:**
- Press **F4** to cycle through visual styles in real-time
- Start with specific style: `python3 run_terminal_typer.py reverse`
- All styles work well on small terminal windows

#### Automatic Layer Detection
- Automatically switches to the layer containing a pressed key
- No need to remember layer modifier keys for basic navigation
- Works alongside existing layer modifier functionality
- Searches through all available layers to find the correct one
- Immediate visual feedback showing the correct layer layout
- Ideal for learning and exploring different keyboard layers

#### Bracket Layout Style
- Clean, terminal-friendly layout with brackets and indentation
- Increased spacing between left and right halves (4 tabs)
- Progressive indentation for visual effect
- Multiple visual indicators for pressed keys (see above)

#### Terminal Interface
- Full-screen curses interface
- **Minimal, clean display** with no distracting text
- Real-time keyboard layout display
- Multiple visual styles for key highlighting
- **WPM counter integrated into layout**
- Ctrl+C to exit gracefully
- F4 to cycle through visual styles

#### Key Mapping
The tool maps physical keys to ZMK key names:
- Letters: q → Q, w → W, etc.
- Numbers: 1 → N1, 2 → N2, etc.
- Symbols: ! → EXCL, @ → AT, etc.
- Special keys: tab → TAB, space → SPACE, etc.

#### WPM Counter
- Real-time Words Per Minute (WPM) calculation and display
- Rolling 60-second average for stable measurements
- Displayed centered between the left and right keyboard halves
- Updates every keystroke for immediate feedback
- Only counts printable characters (letters, numbers, symbols)
- Never resets - maintains session statistics
- Format: "[45.2 WPM]" with units displayed

### Keymap Format

The tool expects ZMK keymap files in the following format:
```json
{
    "keymap": {
        "compatible": "zmk,keymap",
        "layers": {
            "default_layer": [
                "TAB Q W E R T Y U I O P BSPC",
                "LCTRL A S D F G H J K L SEMI SQT",
                "LSHFT Z X C V B N M COMMA DOT FSLH ESC",
                "mo(1) LEFT_GUI SPACE RET LCTRL mo(2)"
            ]
        }
    }
}
```

### Supported Key Names

The renderer supports most ZMK key names including:
- Letters: Q, W, E, R, T, Y, U, I, O, P, A, S, D, F, G, H, J, K, L, Z, X, C, V, B, N, M
- Numbers: N1, N2, N3, N4, N5, N6, N7, N8, N9, N0
- Symbols: EXCL, AT, HASH, DLLR, PRCNT, CARET, AMPS, ASTRK, LPAR, RPAR, etc.
- Special keys: TAB, BSPC, RET, ESC, SPACE, LCTRL, LSHFT, LEFT_GUI, etc.
- Layer keys: mo(1), mo(2)
- Media keys: C_PREV, C_PLAY_PAUSE, C_NEXT, C_VOLUME_UP, C_VOL_DN, C_MUTE
- Navigation: LEFT, DOWN, UP, RIGHT, HOME, END
- Bluetooth: BT_CLR, BT_SEL_0, BT_SEL_1, BT_SEL_2, BT_SEL_3, BT_SEL_4

### Controls

- **Any key**: See it highlighted on the keyboard layout
- **Automatic layer switching**: Press any key to automatically switch to its layer
- **F1**: Switch to lower layer (numbers, media controls)
- **F2**: Switch to raise layer (symbols, navigation)
- **F4**: Cycle through visual styles for pressed keys
- **Ctrl+C**: Exit the application

### Requirements

- Python 3.7+
- pynput>=1.7.6 (for keyboard input capture)
- curses (built into Python standard library)
- Linux terminal with curses support (gnome-terminal, xterm, etc.)

### Installation

1. Clone or download the project
2. Install dependencies: `pip3 install -r requirements.txt`
3. Ensure you have a ZMK keymap JSON file
4. Run: `python3 run_terminal_typer.py`

### Troubleshooting

#### Permission Issues
If you get permission errors for keyboard input:
```bash
# On some systems, you may need to run with sudo
sudo python3 run_terminal_typer.py
```

#### Terminal Compatibility
If the display looks wrong:
- Try a different terminal emulator (xterm, kitty, etc.)
- Ensure your terminal supports curses
- Check terminal size (minimum 80x24 recommended)

#### Unsupported Keys
If you press keys that aren't mapped:
- The tool will show them as "Unsupported" at the bottom
- The tool continues running normally
- Only mapped keys will be highlighted on the keyboard layout

## Next Steps (Phase 3)

- [x] Improved ASCII layout formatting (Multiple visual styles implemented)
- [ ] Better layer switching visualization
- [ ] Configuration file support
- [ ] Custom key mapping support
- [ ] Performance optimizations 
