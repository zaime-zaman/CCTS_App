import sqlite3
from unicodedata import name
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QMessageBox, QFrame
)
from PyQt5.QtCore import Qt

from ui.start_session import StartSessionWidget
DB_PATH = "D:/CCTS_PRO/students.db"


class StudentSection(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_student = None
        self.init_db()
        self.initUI()
        self.load_data()

    # ========== Database Setup ==========
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

    # ========== UI Setup ==========
    def initUI(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(15)

        # ========== Left Section (Table + Add) ==========
        left_layout = QVBoxLayout()

        # Header
        title = QLabel("Students")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #333;")
        left_layout.addWidget(title)

        # Input Fields
        input_layout = QHBoxLayout()
        self.service_input = QLineEdit()
        self.service_input.setPlaceholderText("Service No.")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Student Name")
        self.svc_input = QLineEdit()
        self.svc_input.setPlaceholderText("SVC")

        add_btn = QPushButton("Add Student")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #f04e23;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #d63d15;
            }
        """)
        add_btn.clicked.connect(self.add_student)

        input_layout.addWidget(self.service_input)
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.svc_input)
        input_layout.addWidget(add_btn)

        left_layout.addLayout(input_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Service No", "Student Name", "SVC", "Manage"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                font-size: 14px;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                font-weight: bold;
                border: 1px solid #ddd;
                padding: 6px;
            }
        """)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Service No. or Name")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)
        left_layout.addWidget(self.table)

        # ========== Right Section (Actions Panel) ==========
        self.actions_panel = QFrame()
        self.actions_panel.setFixedWidth(300)
        self.actions_panel.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 6px;
            }
        """)

        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(15, 15, 15, 15)
        panel_layout.setSpacing(12)

        self.info_label = QLabel("Select a student for actions")
        self.info_label.setStyleSheet("font-size: 14px; color: #444;")
        panel_layout.addWidget(self.info_label)

        self.start_btn = QPushButton("Start Session")
        self.start_btn.clicked.connect(self.start_selected_session)

        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        self.download_btn = QPushButton("Download History")
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)

        self.history_btn = QPushButton("Student History")
        self.history_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)

        self.trash_btn = QPushButton("Trash Student")
        self.trash_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.trash_btn.clicked.connect(self.trash_student)

        panel_layout.addWidget(self.start_btn)
        panel_layout.addWidget(self.download_btn)
        panel_layout.addWidget(self.history_btn)
        panel_layout.addWidget(self.trash_btn)
        panel_layout.addStretch()

        self.actions_panel.setLayout(panel_layout)

        # Combine both sections
        main_layout.addLayout(left_layout, 3)
        main_layout.addWidget(self.actions_panel, 1)

        self.setLayout(main_layout)
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

            # Create Manage Buttons Layout (Actions + Delete)
            manage_layout = QHBoxLayout()
            manage_layout.setContentsMargins(5, 0, 5, 0)
            manage_layout.setSpacing(6)

            action_btn = QPushButton("Actions")
            action_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            action_btn.clicked.connect(lambda _, r=row_data: self.show_actions(r))

            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            delete_btn.clicked.connect(lambda _, s=row_data[0]: self.delete_student(s))

            # Put both buttons in a frame (so they align properly)
            manage_frame = QFrame()
            hlayout = QHBoxLayout(manage_frame)
            hlayout.addWidget(action_btn)
            hlayout.addWidget(delete_btn)
            hlayout.setContentsMargins(0, 0, 0, 0)
            hlayout.setSpacing(8)
            self.table.setCellWidget(row_idx, 3, manage_frame)

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
        self.info_label.setText(f"<b>Service NO:</b> {service_no}<br><b>Name:</b> {name}")

    def trash_student(self):
        if not self.selected_student:
            QMessageBox.warning(self, "No Selection", "Please select a student first.")
            return

        service_no = self.selected_student[0]
        self.delete_student(service_no)
        self.selected_student = None
        self.info_label.setText("Select a student for actions")
    
    def filter_table(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            service_no = self.table.item(row, 0).text().lower()
            name = self.table.item(row, 1).text().lower()
            if text in service_no or text in name:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
