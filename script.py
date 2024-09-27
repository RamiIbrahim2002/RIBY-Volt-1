import pyautogui
import keyboard
import os
from datetime import datetime
import logging
import time
import win32gui
import win32com.client
import win32process
import psutil

# Set up logging
logging.basicConfig(filename='vscode_screenshot.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class VSCodeTerminalScreenshotCapture:
    def __init__(self, save_dir='screenshots'):
        self.save_dir = save_dir
        self.ensure_save_directory()
        self.shell = win32com.client.Dispatch("WScript.Shell")

    def ensure_save_directory(self):
        """Ensure the screenshot save directory exists."""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            logging.info(f"Created directory: {self.save_dir}")

    def capture_screenshot(self):
        """Capture a screenshot of the VSCode terminal area."""
        try:
            vscode_window = self.find_vscode_window()
            if vscode_window:
                self.activate_window(vscode_window)
                
                # Wait for a short period to allow command output to appear
                time.sleep(0.5)

                # Get window dimensions
                rect = win32gui.GetWindowRect(vscode_window)
                x, y, x1, y1 = rect
                width = x1 - x
                height = y1 - y

                # Estimate terminal area (bottom 30% of the window)
                terminal_height = int(height * 0.5)
                terminal_y = y + height - terminal_height

                # Capture the terminal area
                screenshot = pyautogui.screenshot(region=(x, terminal_y, width, terminal_height))
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"vscode_terminal_{timestamp}.png"
                filepath = os.path.join(self.save_dir, filename)
                screenshot.save(filepath)
                logging.info(f"Terminal screenshot saved: {filepath}")
            else:
                logging.warning("VSCode window not found")
        except Exception as e:
            logging.error(f"Error capturing screenshot: {str(e)}")

    def find_vscode_window(self):
        """Find the VSCode window using multiple methods."""
        # Method 1: Partial title match
        def enum_window_titles(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "Visual Studio Code" in title:
                    ctx.append(hwnd)
        windows = []
        win32gui.EnumWindows(enum_window_titles, windows)
        if windows:
            logging.debug(f"Found VSCode windows by partial title: {windows}")
            return windows[0]

        # Method 2: Process name
        for proc in psutil.process_iter(['name', 'pid']):
            if proc.info['name'] in ['Code.exe', 'code.exe']:
                def callback(hwnd, hwnds):
                    if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                        if found_pid == proc.info['pid']:
                            hwnds.append(hwnd)
                    return True
                hwnds = []
                win32gui.EnumWindows(callback, hwnds)
                if hwnds:
                    logging.debug(f"Found VSCode windows by process: {hwnds}")
                    return hwnds[0]

        logging.debug("VSCode window not found by any method")
        return None

    def activate_window(self, hwnd):
        """Activate the given window."""
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)  # Short delay to ensure window activation
        except Exception as e:
            logging.error(f"Error activating window: {str(e)}")

    def start_capture(self):
        """Start listening for the Enter key press to capture screenshots."""
        logging.info("Starting VSCode terminal screenshot capture...")
        keyboard.on_press_key("enter", lambda _: self.capture_screenshot())
        keyboard.wait('esc')  # Wait for 'esc' key to stop the script

if __name__ == "__main__":
    capture = VSCodeTerminalScreenshotCapture()
    capture.start_capture()