from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class SimulatorPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("Simulator Coming Soon...")
        label.setStyleSheet("font-size: 24px; color: white;")
        layout.addWidget(label)

        self.setStyleSheet("background-color: #2b2b2b;")
        self.setLayout(layout)
