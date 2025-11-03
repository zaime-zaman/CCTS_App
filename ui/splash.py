from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QTimer

class SplashScreen(QWidget):
    def __init__(self, switch_to_login):
        super().__init__()
        self.switch_to_login = switch_to_login
        self.initUI()

    def initUI(self):
        # Window setup
        self.setWindowTitle("CCTS - Loading")
        self.showFullScreen()  # Fullscreen splash
        self.setStyleSheet("background-color: black;")

        # Layout setup
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        # Add animated GIF
        self.label = QLabel(self)
        self.movie = QMovie("D:/CCTS_PRO/assets/splash_video.gif")  # <-- your path
        self.label.setMovie(self.movie)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # resize the gif to fit the screen
        self.label.setFixedSize(1920, 1080)  # Adjust size as needed
        self.label.setScaledContents(True)


        self.setLayout(layout)
        self.movie.start()

        # Auto transition to login page after 8 sec
        QTimer.singleShot(8000, self.switch_to_login)
