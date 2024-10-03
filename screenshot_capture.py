import pyautogui
import keyboard
import os
""" import readline   """# For command line input handling
import datetime
import logging
import time
import win32gui
from window_utils import find_vscode_window, activate_window
from config import SAVE_DIR
import platform
import subprocess
import psutil
import json

class VSCodeTerminalScreenshotCapture:
    def __init__(self):
        self.ensure_save_directory()
        self.last_command = ""
        self.is_capturing = False
        self.command_buffer = ""
        self.history_file = os.path.join(SAVE_DIR, "command_history.txt")  # History file
        self.log_file = os.path.join(SAVE_DIR, "command_log.txt")  # Log file to save commands and outputs

        # Load command history if exists
        #self.load_history()

    def ensure_save_directory(self):
        os.makedirs(SAVE_DIR, exist_ok=True)
        logging.info(f"Screenshot directory ensured: {SAVE_DIR}")
    

    def get_windows_command_history(self):
        def get_last_terminal_process():
            terminal_processes = []
            
            # Get PowerShell and Command Prompt processes
            for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                if proc.info['name'] in ['powershell.exe', 'cmd.exe']:
                    terminal_processes.append(proc)
            
            if not terminal_processes:
                return None

            # Sort by the latest creation time to find the most recently used terminal
            terminal_processes.sort(key=lambda p: p.info['create_time'], reverse=True)
            return terminal_processes[0]

        def get_powershell_history():
            powershell_command = ('Get-History | Select-Object -Last 20 | '
                                'ForEach-Object { @{Id=$_.Id; CommandLine=$_.CommandLine; '
                                'ExecutionStatus=$_.ExecutionStatus; StartExecutionTime=$_.StartExecutionTime.ToString("o"); '
                                'EndExecutionTime=$_.EndExecutionTime.ToString("o")} } | ConvertTo-Json')
            try:
                result = subprocess.run(["powershell", "-Command", powershell_command],
                                        capture_output=True, text=True, check=True)
                history_data = json.loads(result.stdout)
                return [(item['CommandLine'], os.getcwd()) for item in history_data]
            except subprocess.CalledProcessError as e:
                return [("Error executing PowerShell command: " + str(e), None)]
            except json.JSONDecodeError:
                return [("Error parsing PowerShell output", None)]

        def get_cmd_history():
            # Command Prompt does not have a native history like PowerShell, but you can retrieve the history
            # using a simple hack of calling `doskey /history` if the session is still open.
            try:
                result = subprocess.run("doskey /history", shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    history_lines = result.stdout.strip().split("\n")
                    return [(line, os.getcwd()) for line in history_lines]
                else:
                    return [("Error retrieving Command Prompt history", None)]
            except subprocess.CalledProcessError as e:
                return [("Error retrieving Command Prompt history: " + str(e), None)]

        last_terminal = get_last_terminal_process()

        if last_terminal:
            if last_terminal.info['name'] == 'powershell.exe':
                return get_powershell_history()
            elif last_terminal.info['name'] == 'cmd.exe':
                return get_cmd_history()
            else:
                return [("Unsupported terminal type: " + last_terminal.info['name'], None)]
        else:
            return [("No active terminal processes found", None)]

    
    def get_unix_shell_history(self):
        possible_history_files = [
            os.path.expanduser("~/.bash_history"),
            os.path.expanduser("~/.zsh_history"),
            os.path.expanduser("~/.history"),
        ]

        for history_file in possible_history_files:
            if os.path.exists(history_file):
                return self.parse_unix_history(history_file)

        return [("No shell history file found", None)]

    def parse_unix_history(self,history_file):
        history = []
        current_dir = os.path.expanduser("~")  # Default to home directory
        
        with open(history_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line.startswith("cd "):
                    # Update current directory for cd commands
                    new_dir = line[3:].strip()
                    if new_dir.startswith("/"):
                        current_dir = new_dir
                    else:
                        current_dir = os.path.join(current_dir, new_dir)
                elif line.startswith(": "):
                    # Some shells (like zsh) prefix lines with ": <unix_timestamp>;"
                    parts = line.split(";", 1)
                    if len(parts) > 1:
                        line = parts[1].strip()
                        history.append((line, current_dir))
                else:
                    history.append((line, current_dir))
        
        return history

    def execute_command(self,command, working_dir):
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                text=True,
                capture_output=True,
                timeout=10,
                cwd=working_dir
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Error executing command: {e}"
        except subprocess.TimeoutExpired:
            return "Command execution timed out"

    def get_history_with_output(self,max_commands=1):
        history = self.get_shell_history()
        results = []
        
        for command, directory in history[-max_commands:]:
            if directory:
                output = self.execute_command(command, directory)
            else:
                output = f"Unable to execute. No working directory available for command: {command}"
            results.append({"command": command, "directory": directory, "output": output})
        print(results)
        return results


    def get_shell_history(self):
        system = platform.system()
        if system == "Windows":
            return self.get_windows_command_history()
        elif system in ["Darwin", "Linux"]:
            return self.get_unix_shell_history()
        else:
            raise NotImplementedError(f"Unsupported operating system: {system}")

    """ def load_history(self):
        try:
            if os.path.exists(self.history_file):
                readline.read_history_file(self.history_file)
                logging.info("Loaded command history.")
        except Exception as e:
            logging.error(f"Error loading command history: {str(e)}")

    def save_history(self):
        try:
            readline.write_history_file(self.history_file)
            logging.info("Saved command history.")
        except Exception as e:
            logging.error(f"Error saving command history: {str(e)}")
 """
    def capture_screenshot(self):
        logging.info("Attempting to capture screenshot...")  # Log this as the first step
        
        

        try:
            last_command = self.get_history_with_output(1)
            #self.log_command_output(last_command[0]["command"], last_command[0]["output"])
            
            
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
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"vscode_terminal_{timestamp}.png"
                filepath = os.path.join(SAVE_DIR, filename)  # Use SAVE_DIR here
                screenshot.save(filepath)
                logging.info(f"Terminal screenshot saved: {filepath}")
            else:
                logging.warning("VSCode window not found")
        except Exception as e:
            logging.error(f"Error capturing screenshot: {str(e)}")

    def log_command_output(self, command, output):
        if command.strip() and command != self.last_command:  
            with open(self.log_file, 'a') as f:
                f.write(f"{datetime.now().strftime('%Y%m%d_%H%M%S')} - Command: {command}\n")
                f.write(f"Output:\n{output}\n\n")
                logging.info(f"Logged command and output: {command}")


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
            """ while self.is_capturing:
                self.execute_command() """
        else:
            keyboard.unhook_all()
            logging.info("Stopped capturing VSCode terminal commands")
