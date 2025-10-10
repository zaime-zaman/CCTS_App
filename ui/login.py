from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QBrush, QImage, QPixmap, QMovie, QIcon
import os

class LoginPage(QWidget):
    def __init__(self, switch_to_dashboard):
        super().__init__()
        self.switch_to_dashboard = switch_to_dashboard
        self.initUI()

    def initUI(self):
        current_dir = os.path.dirname(os.path.dirname(__file__))
        bg_path = os.path.join(current_dir, 'assets', 'bg.png')
        bg_path = bg_path.replace('\\', '/')
        
        print(f"Looking for background image at: {bg_path}")
        
        if os.path.exists(bg_path):
            palette = self.palette()
            image = QImage(bg_path)
            
            # Set fixed resolution for target screen
            screen_width = 1920
            screen_height = 1080
            
            # Scale image to fill the screen while maintaining aspect ratio
            scaled_image = image.scaled(
                screen_width,
                screen_height,
                Qt.IgnoreAspectRatio,  # Changed to ignore aspect ratio for full coverage
                Qt.SmoothTransformation
            )
            
            # No need for cropping since we're forcing the exact dimensions
            pixmap = QPixmap.fromImage(scaled_image)
            brush = QBrush(pixmap)
            
            brush.setStyle(Qt.TexturePattern)
            palette.setBrush(QPalette.Window, brush)
            self.setPalette(palette)
            self.setAutoFillBackground(True)
        else:
            print(f"Error: Background image not found at {bg_path}")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.setContentsMargins(100, 0, 0, 0)

        # Create welcome label above the card
        welcome_label = QLabel("Welcome to PSS!")
        welcome_label.setStyleSheet("""
            font-size: 36px; 
            font-weight: bold; 
            color: black;
            margin-bottom: 20px;
        """)
        layout.addWidget(welcome_label)

        card = QFrame()
        card.setFixedWidth(400)
        # Remove the welcome label from card since it's now above it
        card.setStyleSheet("""
            QFrame {
                background: rgba(0,0,0,0.6);
                border-radius: 15px;
                color: white;
                padding: 20px;
            }
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border-radius: 5px;
                background: white;
                color: black;
            }
            QPushButton {
                padding: 8px;
                font-size: 14px;
                background: #2196F3;
                border-radius: 5px;
                border: none;
                color: white;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(10)  # Add space between elements

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        # Define credentials as class attributes
        self._correct_username = "admin"
        self._correct_password = "123"

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)

        for widget in [self.username, self.password, login_btn]:
            card_layout.addWidget(widget)
            # Remove individual widget styling as it's now in the card's stylesheet
            
        # Add some vertical spacing in the card
        card_layout.setContentsMargins(20, 20, 20, 20)

        card.setLayout(card_layout)
        layout.addWidget(card)
        self.setLayout(layout)

    # create a method that will show the attractive loading animation on the login button
    def show_loading_animation(self):
        loading_label = QLabel()
        loading_movie = QMovie("assets/loading.gif")  # Make sure to add a loading.gif to your assets folder
        loading_label.setMovie(loading_movie)
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Loading...")
        loading_movie.start()


    def login(self):
        # Get current input values
        entered_username = self.username.text()
        entered_password = self.password.text()

        # Check if credentials match
        if entered_username == self._correct_username and entered_password == self._correct_password:
            print("Login successful!")
            self.switch_to_dashboard()
        else:
            print("Invalid credentials!")
            # Clear the input fields
            self.username.clear()
            self.password.clear()
            # Optional: Set focus back to username field
            self.username.setFocus()
