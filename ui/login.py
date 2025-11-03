# Login.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QGraphicsOpacityEffect, QMessageBox
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPalette, QBrush, QImage, QPixmap, QMovie, QIcon, QFont, QPainter
import os

class PremiumButton(QPushButton):
    """Premium button with gradient matching dashboard"""
    def __init__(self, text, primary_color="#667eea", hover_color="#764ba2"):
        super().__init__(text)
        self.primary_color = primary_color
        self.hover_color = hover_color
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(45)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {primary_color}, stop:1 {hover_color});
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0px 20px;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6fd8, stop:1 #6a3093);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a5fc8, stop:1 #5a2083);
            }}
        """)


class GlassFrame(QFrame):
    """Glass effect frame matching dashboard"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 15px;
            }
        """)


class LoginPage(QWidget):
    def __init__(self, switch_to_dashboard):
        super().__init__()
        self.switch_to_dashboard = switch_to_dashboard
        self.initUI()
        self.addFadeInAnimation()

    def addFadeInAnimation(self):
        """Add fade-in animation like dashboard"""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setDuration(800)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def initUI(self):
        # Set background using the same approach as dashboard
        self.setAutoFillBackground(True)
        palette = self.palette()
        
        current_dir = os.path.dirname(os.path.dirname(__file__))
        bg_path = os.path.join(current_dir, 'assets', 'bg.png')
        bg_path = bg_path.replace('\\', '/')
        
        # print(f"Looking for background image at: {bg_path}")
        
        if os.path.exists(bg_path):
            image = QImage(bg_path)
            
            # Set fixed resolution for target screen
            screen_width = 1920
            screen_height = 1080
            
            # Scale image to fill the screen while maintaining aspect ratio
            scaled_image = image.scaled(
                screen_width,
                screen_height,
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
            
            # Create semi-transparent version like dashboard
            pixmap = QPixmap.fromImage(scaled_image)
            
            # Apply transparency directly to the palette brush
            brush = QBrush(pixmap)
            palette.setBrush(QPalette.Window, brush)
            self.setPalette(palette)
            # print("Background image loaded successfully")
        else:
            print(f"Error: Background image not found at {bg_path}")
            # Use fallback gradient like dashboard
            self.setFallbackBackground()
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        layout.setContentsMargins(0, 0, 400, 120)  # Adjusted for better positioning

        # Welcome label with dashboard styling
        welcome_label = QLabel("🚀 Welcome to CCTS PRO")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                color: White;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
                background: transparent;
                margin-bottom: 30px;
                padding: 10px;
            }
        """)
        layout.addWidget(welcome_label)

        # Create glass frame card matching dashboard style
        card = GlassFrame()
        card.setFixedWidth(380)
        card.setFixedHeight(280)
        
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignCenter)

        # Title for login card
        login_title = QLabel("Login to Your Account")
        login_title.setAlignment(Qt.AlignCenter)
        login_title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 20px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
                background: transparent;
                margin-bottom: 10px;
            }
        """)
        card_layout.addWidget(login_title)

        # Username field with improved styling
        self.username = QLineEdit()
        self.username.setPlaceholderText("👤 Username")
        self.username.setFixedHeight(45)
        self.username.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(102, 126, 234, 0.3);
                border-radius: 8px;
                padding: 0px 15px;
                font-size: 14px;
                font-family: 'Segoe UI', sans-serif;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
                background: rgba(255, 255, 255, 0.95);
            }
            QLineEdit::placeholder {
                color: #7f8c8d;
                font-family: 'Segoe UI', sans-serif;
            }
        """)

        # Password field with improved styling
        self.password = QLineEdit()
        self.password.setPlaceholderText("🔒 Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedHeight(45)
        self.password.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(102, 126, 234, 0.3);
                border-radius: 8px;
                padding: 0px 15px;
                font-size: 14px;
                font-family: 'Segoe UI', sans-serif;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
                background: rgba(255, 255, 255, 0.95);
            }
            QLineEdit::placeholder {
                color: #7f8c8d;
                font-family: 'Segoe UI', sans-serif;
            }
        """)

        # Define credentials as class attributes
        self._correct_username = "admin"
        self._correct_password = "123"

        # Login button using PremiumButton class
        self.login_btn = PremiumButton("🚀 Login to Dashboard")
        self.login_btn.clicked.connect(self.login)
        self.login_btn.setFixedHeight(50)

        # Add widgets to card layout
        for widget in [self.username, self.password, self.login_btn]:
            card_layout.addWidget(widget)

        card.setLayout(card_layout)
        layout.addWidget(card)
        self.setLayout(layout)

    def setFallbackBackground(self):
        """Set fallback gradient background matching dashboard"""
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f5f7fa, stop:0.5 #c3cfe2, stop:1 #ffffff);
                font-family: 'Segoe UI', sans-serif;
            }
        """)

    def show_loading_animation(self):
        """Show loading animation on login button"""
        loading_label = QLabel()
        loading_movie = QMovie("assets/loading.gif")
        loading_label.setMovie(loading_movie)
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Loading...")
        loading_movie.start()

    def login(self):
        """Handle login with improved user feedback"""
        entered_username = self.username.text()
        entered_password = self.password.text()

        if entered_username == self._correct_username and entered_password == self._correct_password:
            print("Login successful!")
            # Optional: Add loading animation here
            # self.show_loading_animation()
            self.switch_to_dashboard()
        else:
            print("Invalid credentials!")
            # Show error message with dashboard styling
            error_msg = QMessageBox()
            error_msg.setWindowTitle("Login Failed")
            error_msg.setText("Invalid username or password")
            error_msg.setIcon(QMessageBox.Warning)
            error_msg.setStyleSheet("""
                QMessageBox {
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 10px;
                    font-family: 'Segoe UI', sans-serif;
                }
                QMessageBox QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-size: 12px;
                    font-weight: 600;
                    font-family: 'Segoe UI', sans-serif;
                }
            """)
            error_msg.exec_()
            
            # Clear the input fields
            self.username.clear()
            self.password.clear()
            # Set focus back to username field
            self.username.setFocus()