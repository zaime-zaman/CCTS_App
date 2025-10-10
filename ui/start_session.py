# ui/start_session.py
import os
import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame
)

from ui.shooting_session import ShootingSessionWindow


class StartSessionWidget(QWidget):
    def __init__(self, service_no, name, svc):
        super().__init__()
        self.service_no = service_no
        self.name = name
        self.svc = svc

        self.setWindowTitle("Start Session")
        self.resize(900, 600)

        self.folder_paths = {
            "video": "assets/videos",
            "2d": "assets/templates_2d",
            "3d": "assets/templates_3d"
        }

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # Header
        header = QLabel("🎯 Start Session")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        sub_label = QLabel(f"Service No: {self.service_no} | Name: {self.name} | SVC: {self.svc}")
        sub_label.setAlignment(Qt.AlignCenter)
        sub_label.setStyleSheet("font-size: 14px; color: #555;")
        main_layout.addWidget(sub_label)

        # Tabs
        tab_layout = QHBoxLayout()
        self.video_btn = QPushButton("🎥 Video")
        self.video_btn.setCheckable(True)
        self.video_btn.setChecked(True)
        self.template2d_btn = QPushButton("📄 2D Template")
        self.template2d_btn.setCheckable(True)
        self.template3d_btn = QPushButton("🧊 3D Template")
        self.template3d_btn.setCheckable(True)

        for btn in (self.video_btn, self.template2d_btn, self.template3d_btn):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f8f8;
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background-color: orange;
                    color: white;
                }
            """)
            tab_layout.addWidget(btn)
        main_layout.addLayout(tab_layout)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        # Events
        self.video_btn.clicked.connect(lambda: self.load_files("video"))
        self.template2d_btn.clicked.connect(lambda: self.load_files("2d"))
        self.template3d_btn.clicked.connect(lambda: self.load_files("3d"))

        self.load_files("video")

    # =================================================
    # MAIN FUNCTION TO LOAD FILE CARDS WITH HOVER PREVIEW
    # =================================================
    def load_files(self, mode):
        folder_path = self.folder_paths.get(mode, "")
        if not os.path.exists(folder_path):
            msg = QLabel(f"⚠️ Folder not found: {folder_path}")
            msg.setAlignment(Qt.AlignCenter)
            self.scroll_area.setWidget(msg)
            return

        # Update button selection
        self.video_btn.setChecked(mode == "video")
        self.template2d_btn.setChecked(mode == "2d")
        self.template3d_btn.setChecked(mode == "3d")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)

        files = [f for f in os.listdir(folder_path) if not f.startswith('.')]

        if not files:
            msg = QLabel("No files found in this category.")
            msg.setAlignment(Qt.AlignCenter)
            layout.addWidget(msg)
        else:
            for f in files:
                file_path = os.path.join(folder_path, f)
                size = os.path.getsize(file_path) / (1024 * 1024)
                ext = os.path.splitext(f)[-1].lower()

                card = QFrame()
                card_layout = QHBoxLayout(card)
                card.setStyleSheet("""
                    QFrame {
                        border: 1px solid #ccc;
                        border-radius: 10px;
                        margin: 4px;
                        padding: 8px;
                        background-color: #fff;
                    }
                    QFrame:hover {
                        background-color: #fff7e6;
                    }
                """)

                # ===============================
                # UNIVERSAL PREVIEW (VIDEO/IMAGE)
                # ===============================
                thumb = QLabel("🎞 Preview")
                thumb.setFixedSize(400, 200)
                thumb.setStyleSheet("border-radius: 8px; background-color: black; color: white;")
                thumb.setAlignment(Qt.AlignCenter)

                cap = None
                timer = QTimer(self)

                # Handle both videos and images
                is_video = ext in [".mp4", ".avi", ".mov", ".mkv"]
                is_image = ext in [".jpg", ".jpeg", ".png", ".bmp"]

                if is_video:
                    cap = cv2.VideoCapture(file_path)

                    def update_frame():
                        if cap.isOpened():
                            ret, frame = cap.read()
                            if ret:
                                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                h, w, ch = frame.shape
                                qimg = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
                                pixmap = QPixmap.fromImage(qimg).scaled(
                                    thumb.width(), thumb.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                                )
                                thumb.setPixmap(pixmap)
                            else:
                                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

                    timer.timeout.connect(update_frame)

                    def start_preview(event):
                        timer.start(40)

                    def stop_preview(event):
                        timer.stop()
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        thumb.clear()
                        thumb.setText("🎞 Preview")

                    thumb.enterEvent = start_preview
                    thumb.leaveEvent = stop_preview

                elif is_image:
                    img = cv2.imread(file_path)

                    def start_preview(event):
                        if img is not None:
                            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            h, w, ch = rgb.shape
                            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
                            pixmap = QPixmap.fromImage(qimg).scaled(
                                thumb.width(), thumb.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                            )
                            thumb.setPixmap(pixmap)

                    def stop_preview(event):
                        thumb.clear()
                        thumb.setText("🎞 Preview")

                    thumb.enterEvent = start_preview
                    thumb.leaveEvent = stop_preview

                card_layout.addWidget(thumb)

                # =========================
                # FILE INFO + PLAY BUTTON
                # =========================
                label = QLabel(f"<b>{f}</b><br>Size: {size:.2f} MB<br>Extension: {ext}")
                label.setStyleSheet("font-size: 13px; color: #333;")

                play_btn = QPushButton("▶")
                play_btn.setFixedSize(80, 40)
                play_btn.setStyleSheet(
                    "border-radius: 20px; background-color: orange; color: white; font-weight: bold;"
                )
                play_btn.clicked.connect(lambda checked, path=file_path: self.open_shooting_session(path))
                card_layout.addWidget(label)
                card_layout.addStretch()
                card_layout.addWidget(play_btn)
                layout.addWidget(card)

        layout.addStretch()
        self.scroll_area.setWidget(container)

    
    def open_shooting_session(self, video_path):
        # Hide all current widgets (navbar, etc.)
        for child in self.findChildren(QWidget):
            if child is not self:
                child.hide()

        # Create shooting overlay full window
        self.shooting_session = ShootingSessionWindow(
            parent=self,
            video_path=video_path
        )
        self.layout().addWidget(self.shooting_session)
        self.shooting_session.raise_()
        self.shooting_session.show()
        self.shooting_session.play_video()


    def restore_session_ui(self):
        # Destroy shooting session and show UI back
        if hasattr(self, "shooting_session"):
            self.shooting_session.setParent(None)
            self.shooting_session.deleteLater()
            del self.shooting_session

        for child in self.findChildren(QWidget):
            child.show()
    
    def hide_navbar(self):
        self.navbar.hide()

    def show_navbar(self):
        self.navbar.show()