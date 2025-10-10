# ui/dashboard.py
import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QFrame, QGraphicsOpacityEffect, QComboBox,
    QMessageBox
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QEvent
from PyQt5.QtGui import QFont

# Import the Student section
from ui.student_section import StudentSection


# ================== Database Setup ==================
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


# ================== Custom Animated Button ==================
class AnimatedButton(QPushButton):
    """Custom button with hover animation"""
    def __init__(self, text, color="#f04e23", hover_color="#d63d15"):
        super().__init__(text)
        self.default_color = color
        self.hover_color = hover_color
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.default_color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 500;
            }}
        """)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            self.setStyleSheet(self.styleSheet().replace(self.default_color, self.hover_color))
        elif event.type() == QEvent.Leave:
            self.setStyleSheet(self.styleSheet().replace(self.hover_color, self.default_color))
        return super().eventFilter(obj, event)


# ================== Main Dashboard Page ==================
class DashboardPage(QWidget):
    def __init__(self, show_simulator=None, show_settings=None, show_about=None):
        super().__init__()
        self.show_simulator = show_simulator
        self.show_settings = show_settings
        self.show_about = show_about
        self.active_button = None
        create_db()  # Ensure DB exists
        self.initUI()
        self.addFadeInAnimation()

    # ================== Fade-in animation ==================
    def addFadeInAnimation(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setDuration(600)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()

    # ================== Main UI Layout ==================
    def initUI(self):
        self.setStyleSheet("background-color: #fafafa; font-family: Segoe UI;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== Top Navigation Bar =====
        nav_bar = QFrame()
        nav_bar.setFixedHeight(60)
        nav_bar.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border-bottom: 1px solid #ddd;
            }
        """)
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(20, 5, 20, 5)
        nav_layout.setSpacing(15)

        buttons = [
            ("Students", "👥"),
            ("Summary", "📊"),
            ("Damage", "⚙️"),
            ("Initializer", "🔧"),
            ("Troubleshoot", "🧰"),
            ("Settings", "⚙️"),
            ("Logout", "⏻")
        ]

        self.nav_buttons = {}
        for name, icon in buttons:
            btn = QPushButton(f"{icon}  {name}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    color: #333;
                    background: transparent;
                    font-size: 14px;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #f04e23;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, n=name, b=btn: self.setActiveButton(n, b))
            nav_layout.addWidget(btn)
            self.nav_buttons[name] = btn

        nav_bar.setLayout(nav_layout)
        main_layout.addWidget(nav_bar)

        # ===== Dynamic Content (Stacked Widget) =====
        self.stack = QStackedWidget()

        # Add sections
        self.student_section = StudentSection()
        self.summary_placeholder = QLabel("📊 Summary Section Coming Soon...")
        self.summary_placeholder.setAlignment(Qt.AlignCenter)
        self.summary_placeholder.setStyleSheet("font-size: 18px; color: gray;")

        self.stack.addWidget(self.student_section)      # index 0
        self.stack.addWidget(self.summary_placeholder)  # index 1

        main_layout.addWidget(self.stack)

        self.setLayout(main_layout)
        self.setActiveButton("Students", self.nav_buttons["Students"])  # Default

    # ================== Button Handling ==================
    def setActiveButton(self, name, button):
        """Highlight active button and change section"""
        # Reset all buttons to default
        for b in self.nav_buttons.values():
            b.setStyleSheet("""
                QPushButton {
                    color: #333;
                    background: transparent;
                    font-size: 14px;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #f04e23;
                    color: white;
                }
            """)

        # Highlight selected button
        button.setStyleSheet("""
            QPushButton {
                background-color: #f04e23;
                color: white;
                font-size: 14px;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
            }
        """)
        self.active_button = button

        # Switch section dynamically
        if name == "Students":
            self.stack.setCurrentWidget(self.student_section)
        elif name == "Summary":
            self.stack.setCurrentWidget(self.summary_placeholder)
        elif name == "Logout":
            reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.close()
