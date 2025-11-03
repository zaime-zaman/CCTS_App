# ui/student_section.py
import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.start_session import StartSessionWidget
DB_PATH = "D:/CCTS_PRO/students.db"


class GlassCard(QFrame):
    """Glass card component"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.80);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 15px;
            }
        """)


class StudentSection(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_student = None
        self.init_db()
        self.initUI()
        self.load_data()

    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_no TEXT NOT NULL,
                student_name TEXT NOT NULL,
                svc TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def initUI(self):
        # Set transparent background to show dashboard background
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                color: #2c3e50;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(25)

        # ========== Left Section ==========
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)

        # Header
        header_card = GlassCard()
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(25, 20, 25, 40)
        
        title = QLabel("🎯 STUDENT MANAGEMENT")
        title.setFont(QFont('Segoe UI', 26, QFont.Bold))
        title.setStyleSheet("""
            color: #2c3e50;
            background: transparent;
            margin-bottom: 5px;
        """)
        
        subtitle = QLabel("Manage your training roster with precision")
        subtitle.setFont(QFont('Segoe UI', 12))
        subtitle.setStyleSheet("color: #7f8c8d; background: transparent;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        left_layout.addWidget(header_card)

        # Search Card
        search_card = GlassCard()
        search_layout = QHBoxLayout(search_card)
        search_layout.setContentsMargins(20, 15, 20, 40)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search students by name or service number...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.80);
                border: 2px solid rgba(102, 126, 234, 0.2);
                border-radius: 10px;
                padding: 12px 20px;
                font-size: 18px;
                color: #2c3e50;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit:focus {
                border: 2px solid rgba(102, 126, 234, 0.5);
                background: rgba(255, 255, 255, 0.80);
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
        """)
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        left_layout.addWidget(search_card)

        # Add Student Card
        add_student_card = GlassCard()
        add_layout = QHBoxLayout(add_student_card)
        add_layout.setContentsMargins(20, 15, 20, 15)
        
        self.service_input = QLineEdit()
        self.service_input.setPlaceholderText("🎖️ Service No.")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("👤 Student Name")
        self.svc_input = QLineEdit()
        self.svc_input.setPlaceholderText("🏷️ SVC")

        input_style = """
            QLineEdit {
                background: rgba(255, 255, 255, 0.80);
                border: 1px solid rgba(102, 126, 234, 0.2);
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 18px;
                color: #2c3e50;
                font-family: 'Segoe UI', sans-serif;
                margin-right: 10px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(102, 126, 234, 0.5);
                background: rgba(255, 255, 255, 0.70);
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
        """
        self.service_input.setStyleSheet(input_style)
        self.name_input.setStyleSheet(input_style)
        self.svc_input.setStyleSheet(input_style)

        add_btn = QPushButton("➕ ADD STUDENT")
        add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 18px;
                font-family: 'Segoe UI', sans-serif;
                border: none;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6fd8, stop:1 #6a3093);
            }
        """)
        add_btn.clicked.connect(self.add_student)

        add_layout.addWidget(self.service_input)
        add_layout.addWidget(self.name_input)
        add_layout.addWidget(self.svc_input)
        add_layout.addWidget(add_btn)
        left_layout.addWidget(add_student_card)

        # Student Roster Card
        roster_card = GlassCard()
        roster_layout = QVBoxLayout(roster_card)
        roster_layout.setContentsMargins(0, 0, 0, 0)
        
        roster_title = QLabel("📊 Student Roster")
        roster_title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        roster_title.setStyleSheet("""
            color: #2c3e50;
            background: transparent;
            padding: 20px 25px 10px 25px;
        """)
        roster_layout.addWidget(roster_title)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Service No", "Student Name", "SVC", "Actions"])
        
        # Table styling
        self.table.setStyleSheet("""
            QTableWidget {
                background: rgba(255, 255, 255, 0.80);
                color: #2c3e50;
                font-size: 18px;
                font-family: 'Segoe UI', sans-serif;
                gridline-color: rgba(102, 126, 234, 0.1);
                border: none;
                border-radius: 0px 0px 30px 30px;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 0.8), stop:1 rgba(118, 75, 162, 0.8));
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px;
                font-size: 18px;
                font-family: 'Segoe UI', sans-serif;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid rgba(102, 126, 234, 0.1);
            }
            QTableWidget::item:selected {
                background: rgba(102, 126, 234, 0.80);
                color: #2c3e50;
            }
            QTableWidget::item:hover {
                background: rgba(102, 126, 234, 0.08);
            }
        """)
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        roster_layout.addWidget(self.table)
        left_layout.addWidget(roster_card)

        # ========== Right Section ==========
        action_card = GlassCard()
        action_card.setFixedWidth(350)
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(25, 25, 25, 25)
        action_layout.setSpacing(20)

        # Panel Header
        panel_header = QLabel("🎮 Quick Actions")
        panel_header.setFont(QFont('Segoe UI', 20, QFont.Bold))
        panel_header.setStyleSheet("color: #2c3e50; background: transparent; margin-bottom: 10px;")
        action_layout.addWidget(panel_header)

        self.info_label = QLabel("👆 Select a student to begin training session")
        self.info_label.setStyleSheet("""
            font-size: 14px; 
            color: #5a6c7d; 
            font-family: 'Segoe UI', sans-serif;
            background: rgba(102, 126, 234, 0.80);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        """)
        self.info_label.setWordWrap(True)
        action_layout.addWidget(self.info_label)

        # Action Buttons
        self.start_btn = self.create_action_button("🚀 START TRAINING", "#667eea", "#764ba2")
        self.download_btn = self.create_action_button("📊 DOWNLOAD METRICS", "#4CAF50", "#45a049")
        self.history_btn = self.create_action_button("📈 VIEW HISTORY", "#2196F3", "#1976D2")
        self.trash_btn = self.create_action_button("🗑️ REMOVE STUDENT", "#ff4757", "#ff3742")

        self.start_btn.clicked.connect(self.start_selected_session)
        self.trash_btn.clicked.connect(self.trash_student)

        action_layout.addWidget(self.start_btn)
        action_layout.addWidget(self.download_btn)
        action_layout.addWidget(self.history_btn)
        action_layout.addWidget(self.trash_btn)
        action_layout.addStretch()

        # Combine sections
        main_layout.addLayout(left_layout, 3)
        main_layout.addWidget(action_card, 1)

        self.setLayout(main_layout)

    def create_action_button(self, text, color1, color2):
        """Create gradient action button"""
        btn = QPushButton(text)
        btn.setFixedHeight(55)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color1}, stop:1 {color2});
                color: white;
                border-radius: 10px;
                padding: 15px;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', sans-serif;
                border: none;
                margin: 5px 0px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color1}, stop:1 {color2});
            }}
        """)
        return btn

    # ========== Action Handlers ==========
    def start_selected_session(self):
        if not self.selected_student:
            QMessageBox.warning(self, "No Selection", "Please select a student first.")
            return

        service_no, name, svc = self.selected_student
        self.open_start_session(service_no, name, svc)

    # ========== Data Functions ==========
    def load_data(self):
        self.table.setRowCount(0)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT service_no, student_name, svc FROM students")
        rows = cur.fetchall()
        conn.close()

        for row_idx, row_data in enumerate(rows):
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            # Action buttons
            action_btn = QPushButton("⚡ ACTION")
            action_btn.setFixedSize(90, 35)  # Fixed size for consistency
            action_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 11px;
                    font-weight: bold;
                    font-family: 'Segoe UI', sans-serif;
                    border: none;
                    margin: 1px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #5a6fd8, stop:1 #6a3093);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #4a5fc8, stop:1 #5a2083);
                    padding: 2px 8px;
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #666666;
                }
            """)
            action_btn.clicked.connect(lambda _, r=row_data: self.show_actions(r))

            delete_btn = QPushButton("🗑️ DELETE")
            delete_btn.setFixedSize(90, 35)  # Same size as action button
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #ff4757, stop:1 #ff3742);
                    color: white;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 11px;
                    font-weight: bold;
                    font-family: 'Segoe UI', sans-serif;
                    border: none;
                    margin: 1px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #e04050, stop:1 #d03040);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #d03040, stop:1 #c02030);
                    padding: 9px 13px;
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #666666;
                }
            """)
            delete_btn.clicked.connect(lambda _, s=row_data[0]: self.delete_student(s))

            # Container for buttons
            button_frame = QFrame()
            button_frame.setStyleSheet("background: transparent; border: none;")
            button_layout = QHBoxLayout(button_frame)
            button_layout.addWidget(action_btn)
            button_layout.addWidget(delete_btn)
            button_layout.setContentsMargins(5, 3, 5, 3)  # Reduced margins
            button_layout.setSpacing(6)  # Reduced spacing
            # CRITICAL: Set proper table dimensions
            self.table.setRowHeight(row_idx, 65)  # Row height to fit buttons
            self.table.setColumnWidth(3, 200)     # Column width for both buttons + spacing

            self.table.setCellWidget(row_idx, 3, button_frame)
            self.table.setCellWidget(row_idx, 3, button_frame)
    def add_student(self):
        service_no = self.service_input.text().strip()
        name = self.name_input.text().strip()
        svc = self.svc_input.text().strip()

        if not service_no or not name or not svc:
            QMessageBox.warning(self, "Missing Info", "Please fill all fields.")
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO students (service_no, student_name, svc) VALUES (?, ?, ?)",
                    (service_no, name, svc))
        conn.commit()
        conn.close()

        self.service_input.clear()
        self.name_input.clear()
        self.svc_input.clear()
        self.load_data()
    
    def open_start_session(self, service_no, name, svc):
        self.session_widget = StartSessionWidget(service_no, name, svc)

        # Find the parent that has 'stack' (DashboardPage)
        parent = self.parentWidget()
        while parent and not hasattr(parent, 'stack'):
            parent = parent.parentWidget()

        # Replace current view with StartSession page
        if parent and hasattr(parent, 'stack'):
            parent.stack.addWidget(self.session_widget)
            parent.stack.setCurrentWidget(self.session_widget)

    def delete_student(self, service_no):
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete student with Service No: {service_no}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("DELETE FROM students WHERE service_no = ?", (service_no,))
            conn.commit()
            conn.close()
            self.load_data()

    def show_actions(self, row_data):
        self.selected_student = row_data
        service_no, name, svc = row_data
        self.info_label.setText(f"<b>Service NO:</b> {service_no}<br><b>Name:</b> {name}<br><b>SVC:</b> {svc}")

    def trash_student(self):
        if not self.selected_student:
            QMessageBox.warning(self, "No Selection", "Please select a student first.")
            return

        service_no = self.selected_student[0]
        self.delete_student(service_no)
        self.selected_student = None
        self.info_label.setText("👆 Select a student to begin training session")
    
    def filter_table(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            service_no = self.table.item(row, 0).text().lower()
            name = self.table.item(row, 1).text().lower()
            if text in service_no or text in name:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)