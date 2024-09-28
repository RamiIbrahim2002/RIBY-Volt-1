from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from screenshot_capture import VSCodeTerminalScreenshotCapture

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VSCode Terminal Screenshot Capture")
        self.setGeometry(100, 100, 300, 150)

        self.capture = VSCodeTerminalScreenshotCapture()

        layout = QVBoxLayout()
        self.toggle_button = QPushButton("Start Capturing")
        self.toggle_button.clicked.connect(self.toggle_capture)
        layout.addWidget(self.toggle_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def toggle_capture(self):
        if self.toggle_button.text() == "Start Capturing":
            self.capture.toggle_capture(True)
            self.toggle_button.setText("Stop Capturing")
        else:
            self.capture.toggle_capture(False)
            self.toggle_button.setText("Start Capturing")