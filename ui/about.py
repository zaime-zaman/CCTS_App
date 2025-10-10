from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("CCTS Application")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        version = QLabel("Version 1.0")
        credits = QLabel("Developed by Phoenix Team")

        for w in [title, version, credits]:
            layout.addWidget(w)

        self.setLayout(layout)
