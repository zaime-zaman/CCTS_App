# ui/dashboard.py
import sqlite3
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QFrame, QGraphicsOpacityEffect, QComboBox,
    QMessageBox
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QEvent
from PyQt5.QtGui import QFont, QPalette, QPixmap, QBrush, QPainter

# Import the Student section
from ui.student_section import StudentSection
from PyQt5.QtWidgets import QApplication


# ================== Database Setup ==================
def create_db():
    """Ensure the students database exists"""
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_no TEXT,
            student_name TEXT,
            svc TEXT
        )
    """)
    conn.commit()
    conn.close()


# ================== Premium Button ==================
class PremiumButton(QPushButton):
    """Premium button with gradient"""
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


# ================== Glass Frame ==================
class GlassFrame(QFrame):
    """Glass effect frame"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.80);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 15px;
            }
        """)


# ================== Main Dashboard Page ==================
class DashboardPage(QWidget):
    def __init__(self, show_simulator=None, show_settings=None, show_about=None):
        super().__init__()
        self.show_simulator = show_simulator
        self.show_settings = show_settings
        self.show_about = show_about
        self.active_button = None
        create_db()
        self.initUI()
        self.addFadeInAnimation()

    # ================== Fade-in Animation ==================
    def addFadeInAnimation(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setDuration(800)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    # ================== UI Layout ==================
    def initUI(self):
        # Set background using QPalette (more reliable)
        self.setAutoFillBackground(True)
        palette = self.palette()
        
        # Try to load background image
        bg_path = "D:/CCTS_PRO/assets/bg.png"
        # print(f"Looking for background image at: {bg_path}")
        
        if os.path.exists(bg_path):
            pixmap = QPixmap(bg_path)
            if not pixmap.isNull():
                # Create a semi-transparent version of the pixmap
                transparent_pixmap = QPixmap(pixmap.size())
                transparent_pixmap.fill(Qt.transparent)
                painter = QPainter(transparent_pixmap)
                painter.setOpacity(0.8)  # 60% opaque (40% transparent)
                painter.drawPixmap(0, 0, pixmap)
                painter.end()
                
                # Set the transparent background
                brush = QBrush(transparent_pixmap)
                palette.setBrush(QPalette.Window, brush)
                self.setPalette(palette)
                # print("Background image loaded successfully with transparency")
            else:
                print("Failed to load background image - invalid file")
                self.setFallbackBackground()
        else:
            print(f"Background image not found at: {bg_path}")
            self.setFallbackBackground()
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== Navigation Bar =====
        nav_bar = GlassFrame()
        nav_bar.setFixedHeight(80)
        nav_bar.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.85);
                border-bottom: 2px solid rgba(102, 126, 234, 0.1);
            }
        """)
        
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(30, 15, 30, 15)
        nav_layout.setSpacing(25)

        # App Logo/Title
        app_title = QLabel("🚀 CCTS PRO")
        app_title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 22px;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
                # background: transparent;
            }
        """)
        nav_layout.addWidget(app_title)

        nav_layout.addStretch()

        buttons = [
            ("Students", "👥"),
            ("Summary", "📊"), 
            ("Damage", "⚡"),
            ("Initializer", "🔧"),
            ("Troubleshoot", "🛠️"),
            ("Settings", "⚙️")
        ]

        self.nav_buttons = {}
        for name, icon in buttons:
            btn = QPushButton(f"{icon}  {name}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    color: #5a6c7d;
                    background: transparent;
                    font-size: 28px;
                    font-weight: 500;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 8px;
                    font-family: 'Segoe UI', sans-serif;
                }
                QPushButton:hover {
                    background: rgba(102, 126, 234, 0.1);
                    color: #667eea;
                }
            """)
            btn.clicked.connect(lambda checked, n=name, b=btn: self.setActiveButton(n, b))
            nav_layout.addWidget(btn)
            self.nav_buttons[name] = btn

        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setFixedHeight(40)
        logout_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 59, 59, 0.40);
                color: #ff3b3b;
                font-size: 16px;
                font-weight: 500;
                border: 1px solid rgba(255, 59, 59, 0.2);
                padding: 8px 20px;
                border-radius: 8px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: rgba(255, 59, 59, 0.95);
                border: 1px solid rgba(255, 59, 59, 0.3);
                color: #e03535;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        nav_layout.addWidget(logout_btn)

        nav_bar.setLayout(nav_layout)
        main_layout.addWidget(nav_bar)

        # ===== Content Area =====
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 25, 30, 25)
        content_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("""
            QStackedWidget {
                background: transparent;
                border: none;
            }
        """)

        # Add sections
        self.student_section = StudentSection()
        self.summary_placeholder = QLabel("🎯 Analytics Dashboard Coming Soon")
        self.summary_placeholder.setAlignment(Qt.AlignCenter)
        self.summary_placeholder.setStyleSheet("""
            QLabel {
                font-size: 24px; 
                color: #7f8c8d; 
                font-family: 'Segoe UI', sans-serif;
                font-weight: 300;
                background: transparent;
            }
        """)

        self.stack.addWidget(self.student_section)
        self.stack.addWidget(self.summary_placeholder)

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_frame)

        self.setLayout(main_layout)
        self.setActiveButton("Students", self.nav_buttons["Students"])

    def setFallbackBackground(self):
        """Set fallback gradient background if image fails"""
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f5f7fa, stop:0.5 #c3cfe2, stop:1 #ffffff);
                font-family: 'Segoe UI', sans-serif;
            }
        """)

    def logout(self):
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.instance().quit()

    # ================== Button Handling ==================
    def setActiveButton(self, name, button):
        """Active button styling"""
        # Reset all buttons
        for b in self.nav_buttons.values():
            b.setStyleSheet("""
                QPushButton {
                    color: #5a6c7d;
                    background: transparent;
                    font-size: 14px;
                    font-weight: 500;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 8px;
                    font-family: 'Segoe UI', sans-serif;
                }
                QPushButton:hover {
                    background: rgba(102, 126, 234, 0.1);
                    color: #667eea;
                }
            """)

        # Active state
        button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                padding: 8px 20px;
                border-radius: 8px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        self.active_button = button

        # Switch section
        if name == "Students":
            self.stack.setCurrentWidget(self.student_section)
        elif name == "Summary":
            self.stack.setCurrentWidget(self.summary_placeholder)