# # ui/shooting_session.py
# import sys
# import vlc
# from PyQt5.QtWidgets import (
#     QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QSizePolicy
# )
# from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
# from PyQt5.QtGui import QCursor


# class ShootingSession(QWidget):
#     def __init__(self, parent=None, video_path=None, back_callback=None):
#         super().__init__(parent)
#         self.video_path = video_path
#         self.back_callback = back_callback

#         # Fill entire parent area
#         self.setStyleSheet("background-color: black;")
#         self.setGeometry(0, 0, parent.width(), parent.height())
#         self.setAttribute(Qt.WA_StyledBackground, True)

#         # Main layout
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(0)

#         # Video frame
#         self.video_frame = QLabel()
#         self.video_frame.setStyleSheet("background-color: black;")
#         self.video_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         self.video_frame.setAlignment(Qt.AlignCenter)
#         layout.addWidget(self.video_frame)

#         # VLC setup
#         self.instance = vlc.Instance(["--no-xlib", "--quiet", "--no-video-title-show"])
#         self.player = self.instance.media_player_new()

#         if sys.platform.startswith("linux"):
#             self.player.set_xwindow(self.video_frame.winId())
#         elif sys.platform == "win32":
#             self.player.set_hwnd(self.video_frame.winId())
#         elif sys.platform == "darwin":
#             self.player.set_nsobject(int(self.video_frame.winId()))

#         # Overlay controls (hidden by default)
#         self.overlay = QWidget(self)
#         self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 100);")
#         self.overlay.setGeometry(0, self.height() - 100, self.width(), 100)
#         self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents, False)
#         self.overlay.raise_()

#         self.btn_layout = QHBoxLayout(self.overlay)
#         self.btn_layout.setContentsMargins(0, 0, 0, 0)
#         self.btn_layout.setSpacing(30)
#         self.btn_layout.setAlignment(Qt.AlignCenter)

#         # Buttons
#         self.play_btn = QPushButton("▶ Play")
#         self.stop_btn = QPushButton("⏹ Stop")
#         self.back_btn = QPushButton("↩ Back")

#         for btn in (self.play_btn, self.stop_btn, self.back_btn):
#             btn.setFixedSize(120, 50)
#             btn.setStyleSheet("""
#                 QPushButton {
#                     background-color: rgba(255, 165, 0, 220);
#                     color: white;
#                     font-size: 18px;
#                     border-radius: 10px;
#                     font-weight: bold;
#                 }
#                 QPushButton:hover {
#                     background-color: rgba(255, 165, 0, 255);
#                 }
#             """)
#             self.btn_layout.addWidget(btn)

#         # Connections
#         self.play_btn.clicked.connect(self.play_video)
#         self.stop_btn.clicked.connect(self.stop_video)
#         self.back_btn.clicked.connect(self.go_back)

#         # Hover detection
#         self.setMouseTracking(True)
#         self.video_frame.setMouseTracking(True)
#         self.overlay.setMouseTracking(True)

#         # Hide buttons timer
#         self.hide_timer = QTimer()
#         self.hide_timer.timeout.connect(self.fade_out_controls)
#         self.hide_timer.setInterval(1000)

#         # Animation for fade in/out
#         self.fade_anim = QPropertyAnimation(self.overlay, b"windowOpacity")
#         self.fade_anim.setDuration(500)
#         self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)

#         self.overlay.setWindowOpacity(0.0)
#         self.overlay.hide()

#     # ----------------------- Video Controls -----------------------
#     def play_video(self):
#         if not self.video_path:
#             return
#         media = self.instance.media_new(self.video_path)
#         self.player.set_media(media)
#         self.player.play()
#         self.fade_in_controls()

#     def stop_video(self):
#         self.player.stop()
#         self.fade_in_controls()

#     def go_back(self):
#         self.player.stop()
#         if self.back_callback:
#             self.back_callback()
#         self.setParent(None)
#         self.deleteLater()

#     # ----------------------- UI Control Visibility -----------------------
#     def mouseMoveEvent(self, event):
#         self.fade_in_controls()
#         self.hide_timer.start()

#     def fade_in_controls(self):
#         self.overlay.show()
#         self.fade_anim.stop()
#         self.fade_anim.setStartValue(self.overlay.windowOpacity())
#         self.fade_anim.setEndValue(1.0)
#         self.fade_anim.start()
#         self.setCursor(Qt.ArrowCursor)
#         self.hide_timer.start()

#     def fade_out_controls(self):
#         self.fade_anim.stop()
#         self.fade_anim.setStartValue(self.overlay.windowOpacity())
#         self.fade_anim.setEndValue(0.0)
#         self.fade_anim.start()
#         self.setCursor(Qt.BlankCursor)

#     def resizeEvent(self, event):
#         """Keep overlay at bottom when window resizes"""
#         self.overlay.setGeometry(0, self.height() - 100, self.width(), 100)
#         super().resizeEvent(event)

#     def closeEvent(self, event):
#         self.player.stop()
#         self.instance.release()
#         event.accept()


# from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
# from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
# from PyQt5.QtMultimediaWidgets import QVideoWidget
# from PyQt5.QtCore import QUrl, QTimer, Qt, QEvent
# from PyQt5.QtGui import QCursor

# class ShootingSessionWindow(QWidget):
#     def __init__(self, parent=None, video_path=None):
#         super().__init__(parent)
#         self.parent = parent
#         self.video_path = video_path
#         self.init_ui()

#     def init_ui(self):
#         # Full window layout
#         self.layout = QVBoxLayout(self)
#         self.layout.setContentsMargins(0, 0, 0, 0)

#         # Video widget
#         self.video_widget = QVideoWidget()
#         self.layout.addWidget(self.video_widget)

#         # Media player
#         self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
#         self.media_player.setVideoOutput(self.video_widget)
#         self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))

#         # Control buttons layout
#         self.controls_layout = QHBoxLayout()
#         self.controls_layout.setAlignment(Qt.AlignCenter)

#         self.play_pause_btn = QPushButton("⏯")
#         self.play_pause_btn.clicked.connect(self.toggle_play_pause)
#         self.back_btn = QPushButton("⬅ Back")
#         self.back_btn.clicked.connect(self.go_back)

#         for btn in (self.play_pause_btn, self.back_btn):
#             btn.setFixedSize(100, 40)
#             btn.setStyleSheet("""
#                 QPushButton {
#                     background-color: rgba(0, 0, 0, 120);
#                     color: white;
#                     border-radius: 8px;
#                     font-size: 16px;
#                 }
#                 QPushButton:hover {
#                     background-color: rgba(255, 255, 255, 150);
#                     color: black;
#                 }
#             """)

#         self.controls_layout.addWidget(self.play_pause_btn)
#         self.controls_layout.addWidget(self.back_btn)
#         self.layout.addLayout(self.controls_layout)

#         # Hide controls initially
#         self.hide_controls()

#         # Detect mouse movement
#         self.video_widget.setMouseTracking(True)
#         self.video_widget.installEventFilter(self)

#         # Timer to auto-hide controls after inactivity
#         self.hide_timer = QTimer()
#         self.hide_timer.setInterval(2000)
#         self.hide_timer.timeout.connect(self.hide_controls)

#         # Full window mode (hide parent UI)
#         if self.parent:
#             self.parent.hide_navbar()
#         self.showFullScreen()
#         self.media_player.play()

#     def toggle_play_pause(self):
#         if self.media_player.state() == QMediaPlayer.PlayingState:
#             self.media_player.pause()
#         else:
#             self.media_player.play()

#     def go_back(self):
#         # Stop video and go back to parent
#         self.media_player.stop()
#         if self.parent:
#             self.parent.show_navbar()
#         self.close()

#     def hide_controls(self):
#         self.play_pause_btn.hide()
#         self.back_btn.hide()
#         self.setCursor(Qt.BlankCursor)

#     def show_controls(self):
#         self.play_pause_btn.show()
#         self.back_btn.show()
#         self.setCursor(Qt.ArrowCursor)
#         self.hide_timer.start()

#     def eventFilter(self, obj, event):
#         if obj == self.video_widget and event.type() == QEvent.MouseMove:
#             self.show_controls()
#         return super().eventFilter(obj, event)
    
    
#     self.parent.hide_navbar()


from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, QTimer, Qt, QEvent
from PyQt5.QtGui import QCursor


class ShootingSessionWindow(QWidget):
    def __init__(self, parent=None, video_path=None):
        super().__init__(parent)
        self.parent = parent
        self.video_path = video_path
        self.init_ui()

    def init_ui(self):
        # Main layout (no margins → full window)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Video area
        self.video_widget = QVideoWidget()
        self.layout.addWidget(self.video_widget)

        # Media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        if self.video_path:
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))

        # --- Control buttons ---
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setAlignment(Qt.AlignCenter)

        self.play_pause_btn = QPushButton("⏯")
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.back_btn = QPushButton("⬅ Back")
        self.back_btn.clicked.connect(self.go_back)

        for btn in (self.play_pause_btn, self.back_btn):
            btn.setFixedSize(100, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 120);
                    color: white;
                    border-radius: 8px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 150);
                    color: black;
                }
            """)

        self.controls_layout.addWidget(self.play_pause_btn)
        self.controls_layout.addWidget(self.back_btn)
        self.layout.addLayout(self.controls_layout)

        # Hide controls initially
        self.hide_controls()

        # Detect mouse movement for showing controls
        self.video_widget.setMouseTracking(True)
        self.video_widget.installEventFilter(self)

        # Timer → auto-hide controls after inactivity
        self.hide_timer = QTimer(self)
        self.hide_timer.setInterval(2000)
        self.hide_timer.timeout.connect(self.hide_controls)

        # Go fullscreen (hide navbar if parent has one)
        if self.parent and hasattr(self.parent, "hide_navbar"):
            self.parent.hide_navbar()
        self.showFullScreen()

        # Auto-play
        self.media_player.play()

    # --- Button Actions ---
    def toggle_play_pause(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def go_back(self):
        """Stop video and return to previous window."""
        self.media_player.stop()
        if self.parent and hasattr(self.parent, "show_navbar"):
            self.parent.show_navbar()
        self.close()

    # --- Control Visibility ---
    def hide_controls(self):
        self.play_pause_btn.hide()
        self.back_btn.hide()
        self.setCursor(Qt.BlankCursor)

    def show_controls(self):
        self.play_pause_btn.show()
        self.back_btn.show()
        self.setCursor(Qt.ArrowCursor)
        self.hide_timer.start()

    # --- Mouse Movement Event ---
    def eventFilter(self, obj, event):
        if obj == self.video_widget and event.type() == QEvent.MouseMove:
            self.show_controls()
        return super().eventFilter(obj, event)
