import pyautogui
import pywinauto
from pywinauto import Application
import subprocess
import time
import os
from typing import Optional

class SystemController:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
    
    def open_application(self, app_name: str) -> bool:
        """Open Windows application."""
        try:
            app_paths = {
                "notepad": "notepad.exe",
                "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                "calculator": "calc.exe",
                "explorer": "explorer.exe",
                "cmd": "cmd.exe",
                "paint": "mspaint.exe"
            }
            
            app_name_lower = app_name.lower()
            
            if app_name_lower in app_paths:
                subprocess.Popen(app_paths[app_name_lower])
                time.sleep(2)
                return True
            else:
                # Try to open directly
                subprocess.Popen(app_name)
                time.sleep(2)
                return True
        except Exception as e:
            print(f"App open error: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """Type text using keyboard."""
        try:
            pyautogui.write(text, interval=interval)
            return True
        except Exception as e:
            print(f"Type error: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Press keyboard key."""
        try:
            pyautogui.press(key)
            return True
        except Exception as e:
            print(f"Key press error: {e}")
            return False
    
    def press_hotkey(self, *keys) -> bool:
        """Press hotkey combination."""
        try:
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            print(f"Hotkey error: {e}")
            return False
    
    def click_at(self, x: int, y: int) -> bool:
        """Click at coordinates."""
        try:
            pyautogui.click(x, y)
            return True
        except Exception as e:
            print(f"Click error: {e}")
            return False
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> bool:
        """Move mouse to coordinates."""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            print(f"Mouse move error: {e}")
            return False
    
    def screenshot(self, filename: str = "screenshot.png") -> Optional[str]:
        """Take screenshot."""
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            return filename
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None
    
    def get_screen_size(self) -> tuple:
        """Get screen resolution."""
        return pyautogui.size()
