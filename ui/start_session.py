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


class StartSessionWidget(QWidget):
    def __init__(self, service_no, name, svc):
        super().__init__()
        self.service_no = service_no
        self.name = name
        self.svc = svc

        self.setWindowTitle("Start Session")
        self.resize(900, 600)

        # Set transparent background
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                color: #2c3e50;
                font-family: 'Segoe UI', sans-serif;
            }
        """)

        # Define folder paths
        self.folder_paths = {
            "video": "assets/videos",
            "2d": "assets/templates_2d",
            "3d": "assets/templates_3d"
        }

        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 20, 25, 20)
        self.main_layout.setSpacing(20)

        # Header Card
        header_card = GlassCard()
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(25, 20, 25, 20)
        
        self.header = QLabel("🎯 Start Training Session")
        self.header.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("color: #2c3e50; background: transparent; margin-bottom: 5px;")
        
        self.sub_label = QLabel(f"Service No: {self.service_no} | Name: {self.name} | SVC: {self.svc}")
        self.sub_label.setAlignment(Qt.AlignCenter)
        self.sub_label.setStyleSheet("""
            font-size: 14px; 
            color: #7f8c8d; 
            font-family: 'Segoe UI', sans-serif;
            background: transparent;
        """)
        
        header_layout.addWidget(self.header)
        header_layout.addWidget(self.sub_label)
        self.main_layout.addWidget(header_card)

        # Navigation Tabs Card
        tabs_card = GlassCard()
        tabs_layout = QHBoxLayout(tabs_card)
        tabs_layout.setContentsMargins(20, 15, 20, 15)
        
        self.video_btn = QPushButton("🎥 Video Templates")
        self.template2d_btn = QPushButton("📄 2D Templates")
        self.template3d_btn = QPushButton("🧊 3D Templates")

        tab_buttons = [self.video_btn, self.template2d_btn, self.template3d_btn]
        
        for btn in tab_buttons:
            btn.setCheckable(True)
            btn.setFixedHeight(45)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.60);
                    color: #2c3e50;
                    border: 1px solid rgba(102, 126, 234, 0.2);
                    border-radius: 8px;
                    padding: 12px 20px;
                    font-weight: bold;
                    font-size: 14px;
                    font-family: 'Segoe UI', sans-serif;
                    margin: 0px 5px;
                }
                QPushButton:checked {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: 1px solid rgba(102, 126, 234, 0.5);
                }
                QPushButton:hover:!checked {
                    background: rgba(102, 126, 234, 0.1);
                    border: 1px solid rgba(102, 126, 234, 0.3);
                }
            """)
            tabs_layout.addWidget(btn)

        self.video_btn.setChecked(True)
        self.main_layout.addWidget(tabs_card)

        # Content Card with Scroll Area
        content_card = GlassCard()
        content_layout = QVBoxLayout(content_card)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        content_title = QLabel("📁 Available Templates")
        content_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        content_title.setStyleSheet("""
            color: #2c3e50;
            background: transparent;
            padding: 20px 25px 10px 25px;
        """)
        content_layout.addWidget(content_title)

        # Scroll Area for Previews
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
                border-radius: 0px 0px 15px 15px;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.80);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(102, 126, 234, 0.5);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(102, 126, 234, 0.7);
            }
        """)
        content_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(content_card)

        # Button Connections
        self.video_btn.clicked.connect(lambda: self.load_files("video"))
        self.template2d_btn.clicked.connect(lambda: self.load_files("2d"))
        self.template3d_btn.clicked.connect(lambda: self.load_files("3d"))

        # Load default video folder on start
        self.load_files("video")

    # =================================================
    # LOAD FILES (VIDEOS / IMAGES) INTO SCROLL AREA
    # =================================================
    def load_files(self, mode):
        folder_path = self.folder_paths.get(mode, "")
        if not os.path.exists(folder_path):
            msg = QLabel(f"⚠️ Folder not found: {folder_path}")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet("""
                font-size: 16px; 
                color: #7f8c8d; 
                padding: 40px;
                background: transparent;
            """)
            self.scroll_area.setWidget(msg)
            return

        # Update active tab button
        self.video_btn.setChecked(mode == "video")
        self.template2d_btn.setChecked(mode == "2d")
        self.template3d_btn.setChecked(mode == "3d")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        files = [f for f in os.listdir(folder_path) if not f.startswith('.')]

        if not files:
            msg = QLabel("No templates found in this category.")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet("""
                font-size: 16px; 
                color: #7f8c8d; 
                padding: 40px;
                background: transparent;
            """)
            layout.addWidget(msg)
        else:
            for f in files:
                file_path = os.path.join(folder_path, f)
                size = os.path.getsize(file_path) / (1024 * 1024)
                ext = os.path.splitext(f)[-1].lower()

                # Create glass card for each file
                card = GlassCard()
                card_layout = QHBoxLayout(card)
                card_layout.setContentsMargins(15, 15, 15, 15)
                card_layout.setSpacing(15)

                # Thumbnail / Preview
                thumb = QLabel("🎞 Preview")
                thumb.setFixedSize(320, 180)
                thumb.setStyleSheet("""
                    QLabel {
                        background: #1a1a1a;
                        color: #ffffff;
                        border-radius: 10px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                """)
                thumb.setAlignment(Qt.AlignCenter)

                # Determine file type
                is_video = ext in [".mp4", ".avi", ".mov", ".mkv"]
                is_image = ext in [".jpg", ".jpeg", ".png", ".bmp"]

                # Hover Preview
                if is_video:
                    cap = cv2.VideoCapture(file_path)
                    timer = QTimer(self)

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
                        cap.release()
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

                # File Info
                info_widget = QWidget()
                info_widget.setStyleSheet("background: transparent;")
                info_layout = QVBoxLayout(info_widget)
                info_layout.setContentsMargins(0, 0, 0, 0)
                
                file_name = QLabel(f"<b>{f}</b>")
                file_name.setStyleSheet("font-size: 16px; color: #2c3e50; font-weight: bold; background: transparent;")
                
                file_details = QLabel(f"Size: {size:.2f} MB • Extension: {ext.upper()}")
                file_details.setStyleSheet("font-size: 13px; color: #7f8c8d; background: transparent; margin-top: 5px;")
                
                info_layout.addWidget(file_name)
                info_layout.addWidget(file_details)
                info_layout.addStretch()
                
                card_layout.addWidget(info_widget)
                card_layout.addStretch()

                # Play Button
                play_btn = QPushButton("▶ Start Session")
                play_btn.setFixedSize(120, 45)
                play_btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #4CAF50, stop:1 #45a049);
                        color: white;
                        border-radius: 8px;
                        padding: 12px 15px;
                        font-weight: bold;
                        font-size: 13px;
                        font-family: 'Segoe UI', sans-serif;
                        border: none;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #45a049, stop:1 #3d8b40);
                    }
                    QPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #3d8b40, stop:1 #357c38);
                    }
                """)
                play_btn.clicked.connect(lambda checked, path=file_path: self.open_shooting_session(path))

                card_layout.addWidget(play_btn)
                layout.addWidget(card)

        layout.addStretch()
        self.scroll_area.setWidget(container)

    # =================================================
    # OPEN FULL SCREEN SHOOTING SESSION
    # =================================================
    def open_shooting_session(self, video_path):
        """Open selected file (video/template) in full window"""
        # Hide the current StartSessionWidget
        self.hide()
        
        # Open the shooting session as a separate window
        self.shooting_session = ShootingSessionWindow(video_path=video_path, parent=self)
        self.shooting_session.session_finished.connect(self.restore_session_ui)
        self.shooting_session.showFullScreen()

    def restore_session_ui(self):
        """Return back from shooting session"""
        # Show the StartSessionWidget again
        self.show()
        
        # Clean up the shooting session
        if hasattr(self, "shooting_session"):
            self.shooting_session = None