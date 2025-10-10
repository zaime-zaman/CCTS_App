from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QSlider
from PyQt5.QtCore import Qt

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        theme_label = QLabel("Select Theme:")
        theme_combo = QComboBox()
        theme_combo.addItems(["Dark", "Light", "Military"])

        volume_label = QLabel("Volume Settings:")
        gun_slider = QSlider(Qt.Horizontal)
        bg_slider = QSlider(Qt.Horizontal)

        for slider in [gun_slider, bg_slider]:
            slider.setRange(0, 100)
            slider.setValue(50)

        layout.addWidget(theme_label)
        layout.addWidget(theme_combo)
        layout.addWidget(volume_label)
        layout.addWidget(QLabel("Gunfire"))
        layout.addWidget(gun_slider)
        layout.addWidget(QLabel("Background"))
        layout.addWidget(bg_slider)

        self.setLayout(layout)
