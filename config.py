import os
import logging

# Use current working directory instead of the user's home directory
current_dir = os.getcwd()

# Directory to save screenshots
SAVE_DIR = os.path.join(current_dir, 'RIBY-Volt-1_screenshots')
os.makedirs(SAVE_DIR, exist_ok=True)

# Directory to save logs
LOG_DIR = os.path.join(current_dir, 'RIBY-Volt-1_logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'vscode_screenshot.log'),
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

logging.info("Logging initialized successfully")
