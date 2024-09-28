from PyQt5.QtWidgets import QApplication
import win32gui
import win32com.client
import win32process
import psutil
import logging

# Example function to find VSCode window using only Win32 API
def find_vscode_window():
    def window_enum_handler(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if "Visual Studio Code" in window_title:
                windows.append(hwnd)

    windows = []
    win32gui.EnumWindows(window_enum_handler, windows)
    return windows[0] if windows else None  # Ensure returning the HWND


def activate_window(hwnd):
    try:
        win32gui.SetForegroundWindow(hwnd)
        logging.info("Window activated successfully")
    except Exception as e:
        logging.error(f"Error activating window: {str(e)}")
