import pyautogui
import keyboard
import os
from datetime import datetime
import logging
import time
import win32gui
from window_utils import find_vscode_window, activate_window
from config import SAVE_DIR

class VSCodeTerminalScreenshotCapture:
    def __init__(self):
        self.ensure_save_directory()
        self.last_command = ""
        self.command_buffer = ""
        self.is_capturing = False

    def ensure_save_directory(self):
        os.makedirs(SAVE_DIR, exist_ok=True)
        logging.info(f"Screenshot directory ensured: {SAVE_DIR}")

    def capture_screenshot(self):
        logging.info("Attempting to capture screenshot...")  # Log this as the first step

        try:
            vscode_window = find_vscode_window()  # Call find_vscode_window
            if vscode_window:
                logging.info("VSCode window found, proceeding with screenshot...")
                activate_window(vscode_window)  # Call activate_window

                # Wait for a short period to allow command output to appear
                time.sleep(0.5)

                # Get window dimensions
                rect = win32gui.GetWindowRect(vscode_window)
                x, y, x1, y1 = rect
                width = x1 - x
                height = y1 - y

                # Estimate terminal area (bottom 50% of the window)
                terminal_height = int(height * 0.5)
                terminal_y = y + height - terminal_height

                # Capture the terminal area
                screenshot = pyautogui.screenshot(region=(x, terminal_y, width, terminal_height))
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"vscode_terminal_{timestamp}.png"
                filepath = os.path.join(SAVE_DIR, filename)  # Use SAVE_DIR here
                screenshot.save(filepath)
                logging.info(f"Terminal screenshot saved: {filepath}")
            else:
                logging.warning("VSCode window not found")
        except Exception as e:
            logging.error(f"Error capturing screenshot: {str(e)}")

    def on_key_event(self, e):
        if not self.is_capturing:
            return

        if e.event_type == keyboard.KEY_DOWN:
            if e.name == 'enter':
                if self.command_buffer.strip() and self.command_buffer != self.last_command:
                    self.capture_screenshot()
                    self.last_command = self.command_buffer.strip()
                self.command_buffer = ""
            elif e.name == 'backspace':
                self.command_buffer = self.command_buffer[:-1]
            elif len(e.name) == 1:  # Single character keys
                self.command_buffer += e.name

    def toggle_capture(self):
        self.is_capturing = not self.is_capturing
        if self.is_capturing:
            keyboard.hook(self.on_key_event)
            logging.info("Started capturing VSCode terminal commands")
        else:
            keyboard.unhook_all()
            logging.info("Stopped capturing VSCode terminal commands")
