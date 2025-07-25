import time
from typing import List, Tuple
from collections import deque

class WPMCalculator:
    """
    Calculates Words Per Minute (WPM) using a rolling average.
    Tracks keystrokes with timestamps and maintains a rolling window.
    """
    
    def __init__(self, window_seconds: int = 60):
        """
        Initialize the WPM calculator.
        
        Args:
            window_seconds: Size of the rolling window in seconds (default: 60)
        """
        self.window_seconds = window_seconds
        self.keystrokes: deque = deque()  # (timestamp, character_count) tuples
        self.total_characters = 0
        self.start_time = time.time()
    
    def add_keystroke(self, character_count: int = 1) -> None:
        """
        Add a keystroke to the calculation.
        
        Args:
            character_count: Number of characters in this keystroke (default: 1)
        """
        current_time = time.time()
        self.keystrokes.append((current_time, character_count))
        self.total_characters += character_count
        
        # Remove old keystrokes outside the window
        self._cleanup_old_keystrokes(current_time)
    
    def _cleanup_old_keystrokes(self, current_time: float) -> None:
        """Remove keystrokes older than the window."""
        cutoff_time = current_time - self.window_seconds
        
        while self.keystrokes and self.keystrokes[0][0] < cutoff_time:
            _, chars = self.keystrokes.popleft()
            self.total_characters -= chars
    
    def get_wpm(self) -> float:
        """
        Calculate current WPM based on the rolling window.
        
        Returns:
            Words per minute (float)
        """
        if not self.keystrokes:
            return 0.0
        
        current_time = time.time()
        self._cleanup_old_keystrokes(current_time)
        
        if not self.keystrokes:
            return 0.0
        
        # Calculate time span of the window
        oldest_time = self.keystrokes[0][0]
        time_span = current_time - oldest_time
        
        # For very short time spans, use a minimum time to avoid extreme values
        if time_span < 1.0:  # Less than 1 second
            time_span = 1.0
        
        # Calculate characters in the window
        window_characters = sum(chars for _, chars in self.keystrokes)
        
        # Convert to words (5 characters = 1 word)
        words = window_characters / 5.0
        
        # Convert to WPM (words per minute)
        minutes = time_span / 60.0
        wpm = words / minutes if minutes > 0 else 0.0
        
        # Cap WPM at a reasonable maximum (e.g., 200 WPM)
        wpm = min(wpm, 200.0)
        
        return round(wpm, 1)
    
    def get_wpm_display(self) -> str:
        """
        Get WPM formatted for display.
        
        Returns:
            Formatted WPM string like "[45 WPM]"
        """
        wpm = self.get_wpm()
        return f"[{wpm:4.1f} WPM]"
    
    def reset(self) -> None:
        """Reset the WPM calculator (clears all data)."""
        self.keystrokes.clear()
        self.total_characters = 0
        self.start_time = time.time()
    
    def get_stats(self) -> dict:
        """
        Get statistics about the WPM calculation.
        
        Returns:
            Dictionary with WPM statistics
        """
        current_time = time.time()
        self._cleanup_old_keystrokes(current_time)
        
        return {
            'current_wpm': self.get_wpm(),
            'window_seconds': self.window_seconds,
            'keystrokes_in_window': len(self.keystrokes),
            'characters_in_window': sum(chars for _, chars in self.keystrokes),
            'total_characters': self.total_characters,
            'session_duration': current_time - self.start_time
        } 
