#!/usr/bin/env python3
"""
Test to reproduce the formatting issue with empty keybindings.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from keyboard_renderer import KeyboardRenderer
from corne_keymap_parser import CorneKeymapParser

def test_formatting_with_trans_keys():
    """Test formatting when there are transparent keys (no keybindings)."""
    
    # Create a keymap with transparent keys
    test_keymap_content = """
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
        test_layer {
            bindings = <
&kp TAB    &trans  &kp W  &trans  &kp R  &kp T  &kp Y  &kp U  &kp I  &kp O  &kp P  &kp BSPC
&kp LCTRL  &kp A  &trans  &kp D  &trans  &kp G  &kp H  &kp J  &kp K  &kp L  &kp SEMI  &kp SQT
&kp LSHFT  &kp Z  &kp X  &trans  &kp V  &kp B  &kp N  &kp M  &kp COMMA  &kp DOT  &kp FSLH  &kp ESC
                         &mo 1  &kp LEFT_GUI  &kp SPACE  &kp RET  &kp LCTRL  &mo 2
            >;
        };
    };
};
"""
    
    # Write test keymap to file
    with open('test_formatting.keymap', 'w') as f:
        f.write(test_keymap_content)
    
    try:
        # Parse the keymap
        parser = CorneKeymapParser('test_formatting.keymap')
        
        # Get the test layer keys
        layer_keys = parser.get_layer_keys('test_layer')
        print("Layer keys:", layer_keys)
        
        # Render the keyboard
        renderer = KeyboardRenderer()
        result = renderer.render_keyboard(layer_keys)
        
        print("Rendered keyboard:")
        print(result)
        
        # Check if formatting is broken
        lines = result.split('\n')
        print(f"Number of lines: {len(lines)}")
        for i, line in enumerate(lines):
            print(f"Line {i}: '{line}'")
        
    finally:
        # Clean up
        if os.path.exists('test_formatting.keymap'):
            os.unlink('test_formatting.keymap')

if __name__ == '__main__':
    test_formatting_with_trans_keys() 
