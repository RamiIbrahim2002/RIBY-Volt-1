import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import logging
from screenshot_capture import VSCodeTerminalScreenshotCapture

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.capture = VSCodeTerminalScreenshotCapture()  # Initialize capture here
        self.initUI()

    def initUI(self):
        self.setWindowTitle("VSCode Screenshot Capture")
        self.capture_button = QPushButton("Start Capture", self)
        self.capture_button.clicked.connect(self.toggle_capture)

        layout = QVBoxLayout()
        layout.addWidget(self.capture_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def toggle_capture(self):
        self.capture.toggle_capture()  # Call toggle_capture from capture instance
        if self.capture.is_capturing:
            self.capture_button.setText("Stop Capture")
        else:
            self.capture_button.setText("Start Capture")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
