# # ui/shooting_session.py
# import os
# import warnings
# import logging

# # ✅ SUPPRESS ALL WARNINGS
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# os.environ['GLOG_minloglevel'] = '2'
# warnings.filterwarnings("ignore")
# logging.getLogger('tensorflow').setLevel(logging.ERROR)
# logging.getLogger('mediapipe').setLevel(logging.ERROR)

# import cv2
# import time
# import math
# import numpy as np
# import pandas as pd
# from PyQt5.QtCore import Qt, QTimer, pyqtSignal
# from PyQt5.QtGui import QFont, QImage, QPixmap
# from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QApplication
# import mediapipe as mp

# class ShootingSessionWindow(QWidget):
#     session_finished = pyqtSignal()
    
#     def __init__(self, parent=None, video_path=None):
#         super().__init__(parent)
#         self.video_path = video_path
#         self.click_points = []
#         self.session_data = []
#         self.current_detections = []

#         # Full-screen window
#         self.setWindowTitle("Shooting Session")
#         self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
#         screen = QApplication.primaryScreen()
#         self.setGeometry(screen.geometry())
#         self.setStyleSheet("background-color: black;")

#         # Layout
#         self.layout = QVBoxLayout(self)
#         self.layout.setContentsMargins(0,0,0,0)

#         # Video display label
#         self.video_label = QLabel(self)
#         self.video_label.setStyleSheet("background-color: black;")
#         self.video_label.setAlignment(Qt.AlignCenter)
#         self.layout.addWidget(self.video_label)

#         # Back button
#         self.back_btn = QPushButton("⬅ Back (ESC)", self)
#         self.back_btn.setFont(QFont("Arial", 12, QFont.Bold))
#         self.back_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: rgba(255,165,0,180);
#                 color: white;
#                 border-radius: 10px;
#                 padding: 8px 16px;
#             }
#             QPushButton:hover {
#                 background-color: rgba(255,165,0,255);
#             }
#         """)
#         self.back_btn.setFixedSize(120, 40)
#         self.back_btn.move(20,20)
#         self.back_btn.raise_()
#         self.back_btn.clicked.connect(self.close_session)
#         self.back_btn.show()

#         # Initialize detection models
#         self.mp_pose = mp.solutions.pose
#         self.pose_detector = self.mp_pose.Pose(
#             static_image_mode=False,
#             model_complexity=1,
#             enable_segmentation=False,
#             min_detection_confidence=0.4,
#             min_tracking_confidence=0.4
#         )
        
#         # YOLO for person detection
#         self.yolo_initialized = False
#         self.initialize_yolo()

#         # Video capture
#         self.cap = None
#         self.timer = QTimer()
#         self.current_frame = None
#         self.start_time = time.time()
        
#         self.initialize_video()
#         self.setMouseTracking(True)
#         self.installEventFilter(self)

#     def initialize_yolo(self):
#         try:
#             from ultralytics import YOLO
#             self.yolo = YOLO("yolov8n.pt")
#             self.yolo_initialized = True
#             print("✅ YOLOv8 person detection initialized")
#         except Exception as e:
#             print(f"❌ YOLOv8 init error: {e}")
#             self.yolo_initialized = False

#     def point_distance(self, p1, p2):
#         return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

#     def landmarks_to_pixels(self, landmarks, bbox_w, bbox_h, bbox_x, bbox_y):
#         pts = {}
#         for idx, lm in enumerate(landmarks.landmark):
#             px = int(bbox_x + lm.x * bbox_w)
#             py = int(bbox_y + lm.y * bbox_h)
#             pts[idx] = (px, py)
#         return pts

#     def determine_body_part_and_lethality(self, click_x, click_y, person_bbox, frame):
#         """
#         IMPROVED: New body parts with realistic military lethality
#         """
#         x1, y1, x2, y2 = person_bbox
#         w = x2 - x1
#         h = y2 - y1
        
#         # Crop person region with padding
#         pad = 10
#         cx1 = max(0, x1 - pad)
#         cy1 = max(0, y1 - pad)
#         cx2 = min(frame.shape[1], x2 + pad)
#         cy2 = min(frame.shape[0], y2 + pad)
#         crop = frame[cy1:cy2, cx1:cx2].copy()
        
#         if crop.size == 0:
#             return 'unknown', 'none', (180, 180, 180)

#         # Run MediaPipe pose on cropped person
#         image_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
#         results = self.pose_detector.process(image_rgb)

#         # Map click relative to crop
#         rel_x = click_x - cx1
#         rel_y = click_y - cy1

#         if not results.pose_landmarks:
#             # Fallback: use bbox proportions
#             rel_norm_y = rel_y / max(1, (cy2 - cy1))
#             if rel_norm_y < 0.15:
#                 return 'head', 'instant_kill', (255, 0, 0)  # Red
#             elif rel_norm_y < 0.25:
#                 return 'neck', 'instant_kill', (255, 50, 50)  # Light Red
#             elif rel_norm_y < 0.45:
#                 return 'chest', 'critical', (255, 165, 0)  # Orange
#             elif rel_norm_y < 0.65:
#                 return 'stomach', 'heavy', (255, 255, 0)  # Yellow
#             else:
#                 return 'limb', 'light', (0, 255, 0)  # Green
#         else:
#             # Convert landmarks to pixel coordinates
#             pts = self.landmarks_to_pixels(results.pose_landmarks, cx2-cx1, cy2-cy1, cx1, cy1)
            
#             # HEAD detection (nose, eyes, ears)
#             head_indices = [0, 1, 2, 3, 4, 5, 6]
#             HEAD_THRESHOLD = int(min(w, h) * 0.08)
#             for idx in head_indices:
#                 if idx in pts:
#                     if self.point_distance(pts[idx], (click_x, click_y)) <= HEAD_THRESHOLD:
#                         return 'head', 'instant_kill', (255, 0, 0)  # Red

#             # NECK detection (between shoulders)
#             if 11 in pts and 12 in pts:  # Left & Right shoulders
#                 neck_x = (pts[11][0] + pts[12][0]) // 2
#                 neck_y = (pts[11][1] + pts[12][1]) // 2
#                 neck_radius = int(self.point_distance(pts[11], pts[12]) * 0.3)
#                 if self.point_distance((neck_x, neck_y), (click_x, click_y)) <= neck_radius:
#                     return 'neck', 'instant_kill', (255, 50, 50)  # Light Red

#             # CHEST detection (upper torso - front)
#             if all(i in pts for i in [11, 12, 23, 24]):  # Shoulders & Hips
#                 left_sh, right_sh = pts[11], pts[12]
#                 left_hip, right_hip = pts[23], pts[24]
                
#                 # Chest area (upper portion of torso)
#                 chest_top_y = min(left_sh[1], right_sh[1])
#                 chest_bottom_y = (left_sh[1] + right_sh[1] + left_hip[1] + right_hip[1]) / 4
#                 chest_left_x = min(left_sh[0], right_sh[0])
#                 chest_right_x = max(left_sh[0], right_sh[0])
                
#                 if (chest_left_x <= click_x <= chest_right_x and 
#                     chest_top_y <= click_y <= chest_bottom_y):
#                     return 'chest', 'critical', (255, 165, 0)  # Orange

#             # STOMACH detection (lower torso - front)
#             if all(i in pts for i in [11, 12, 23, 24]):
#                 left_sh, right_sh = pts[11], pts[12]
#                 left_hip, right_hip = pts[23], pts[24]
                
#                 # Stomach area (lower portion of torso)
#                 stomach_top_y = (left_sh[1] + right_sh[1] + left_hip[1] + right_hip[1]) / 4
#                 stomach_bottom_y = max(left_hip[1], right_hip[1])
#                 stomach_left_x = min(left_hip[0], right_hip[0])
#                 stomach_right_x = max(left_hip[0], right_hip[0])
                
#                 if (stomach_left_x <= click_x <= stomach_right_x and 
#                     stomach_top_y <= click_y <= stomach_bottom_y):
#                     return 'stomach', 'heavy', (255, 255, 0)  # Yellow

#             # BACK detection (if visible from landmarks)
#             # For back, we check if click is in torso area but not in front parts
#             if all(i in pts for i in [11, 12, 23, 24]):
#                 torso_xmin = min(pts[11][0], pts[12][0], pts[23][0], pts[24][0])
#                 torso_xmax = max(pts[11][0], pts[12][0], pts[23][0], pts[24][0])
#                 torso_ymin = min(pts[11][1], pts[12][1], pts[23][1], pts[24][1])
#                 torso_ymax = max(pts[11][1], pts[12][1], pts[23][1], pts[24][1])
                
#                 if (torso_xmin <= click_x <= torso_xmax and 
#                     torso_ymin <= click_y <= torso_ymax):
#                     return 'back', 'critical', (255, 100, 0)  # Dark Orange

#             # LIMB detection (arms/legs)
#             limb_indices = [13, 14, 15, 16, 23, 24, 25, 26, 27, 28]  # Arms & Legs
#             LIMB_THRESHOLD = int(min(w, h) * 0.06)
#             for idx in limb_indices:
#                 if idx in pts:
#                     if self.point_distance(pts[idx], (click_x, click_y)) <= LIMB_THRESHOLD:
#                         return 'limb', 'light', (0, 255, 0)  # Green

#             # Default fallback
#             return 'torso', 'heavy', (255, 200, 0)  # Light Orange

#     def initialize_video(self):
#         if not self.video_path or not os.path.exists(self.video_path):
#             print(f"❌ Error: Video not found: {self.video_path}")
#             self.close_session()
#             return
            
#         try:
#             self.cap = cv2.VideoCapture(self.video_path)
#             if not self.cap.isOpened():
#                 print(f"❌ Error: Could not open video {self.video_path}")
#                 self.close_session()
#                 return
                
#             self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
#             self.timer.timeout.connect(self.next_frame)
#             self.timer.start(int(1000/self.fps))
#             print(f"✅ Video loaded successfully: {self.video_path}")
            
#         except Exception as e:
#             print(f"❌ Error initializing video: {e}")
#             self.close_session()

#     def eventFilter(self, obj, event):
#         if event.type() == event.KeyPress:
#             if event.key() == Qt.Key_Escape:
#                 self.close_session()
#                 return True
#         return super().eventFilter(obj, event)

#     def next_frame(self):
#         if not self.cap or not self.cap.isOpened():
#             self.close_session()
#             return
            
#         ret, frame = self.cap.read()
#         if not ret:
#             print("✅ Video ended normally")
#             self.close_session()
#             return

#         self.current_frame = frame.copy()
#         h, w = frame.shape[:2]

#         # YOLO Person Detection
#         self.current_detections = []
        
#         if self.yolo_initialized and self.yolo:
#             try:
#                 results = self.yolo(frame, imgsz=640, verbose=False)
                
#                 if len(results) > 0:
#                     for box in results[0].boxes:
#                         cls = int(box.cls.cpu().numpy()) if hasattr(box, 'cls') else None
#                         if cls == 0:  # person class
#                             xyxy = box.xyxy.cpu().numpy().flatten()[:4]
#                             self.current_detections.append(xyxy)
                
#                 # Draw bounding boxes
#                 for i, (x1, y1, x2, y2) in enumerate(self.current_detections, 1):
#                     cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
#                     cv2.putText(frame, f"P{i}", (int(x1), max(12, int(y1) - 6)), 
#                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                               
#             except Exception as e:
#                 print(f"❌ YOLO detection error: {e}")

#         # Draw existing click markers
#         current_time = time.time()
#         self.click_points = [point for point in self.click_points if point[4] > current_time]
        
#         for px, py, color, label, exp in self.click_points:
#             cv2.circle(frame, (px, py), 12, color, -1)
#             cv2.putText(frame, label, (px + 15, py), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

#         # Overlay info
#         elapsed = time.time() - self.start_time
#         detection_count = len(self.current_detections)
#         cv2.putText(frame, f"Persons: {detection_count} | Time: {elapsed:.1f}s | Shots: {len(self.session_data)} | MILITARY MODE",
#                     (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

#         # Show in PyQt label
#         try:
#             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             img_qt = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0],
#                             frame_rgb.strides[0], QImage.Format_RGB888)
            
#             pixmap = QPixmap.fromImage(img_qt)
#             pixmap = pixmap.scaled(self.video_label.width(), self.video_label.height(), 
#                                  Qt.KeepAspectRatio, Qt.SmoothTransformation)
#             self.video_label.setPixmap(pixmap)
#         except Exception as e:
#             print(f"❌ Error displaying frame: {e}")

#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton and self.current_frame is not None:
#             # Get video display area coordinates
#             video_label_rect = self.video_label.geometry()
#             click_pos = event.pos()
            
#             if not video_label_rect.contains(click_pos):
#                 return
                
#             # Get current pixmap
#             pixmap = self.video_label.pixmap()
#             if not pixmap:
#                 return
                
#             # Calculate scaling and offsets
#             pixmap_width = pixmap.width()
#             pixmap_height = pixmap.height()
#             label_width = self.video_label.width()
#             label_height = self.video_label.height()
            
#             x_offset = (label_width - pixmap_width) // 2
#             y_offset = (label_height - pixmap_height) // 2
            
#             pixmap_x = click_pos.x() - x_offset
#             pixmap_y = click_pos.y() - y_offset
            
#             if (pixmap_x < 0 or pixmap_x >= pixmap_width or 
#                 pixmap_y < 0 or pixmap_y >= pixmap_height):
#                 return
                
#             # Scale to original video frame coordinates
#             frame_h, frame_w = self.current_frame.shape[:2]
#             scale_x = frame_w / pixmap_width
#             scale_y = frame_h / pixmap_height
            
#             fx = int(pixmap_x * scale_x)
#             fy = int(pixmap_y * scale_y)
            
#             fx = max(0, min(fx, frame_w - 1))
#             fy = max(0, min(fy, frame_h - 1))

#             # IMPROVED: New body parts detection
#             result = "miss"
#             label = "MISS"
#             color = (180, 180, 180)
#             hit_person = -1
#             damage_type = "none"
            
#             if self.current_detections:
#                 for person_idx, bbox in enumerate(self.current_detections):
#                     x1, y1, x2, y2 = map(int, bbox)
                    
#                     if x1 <= fx <= x2 and y1 <= fy <= y2:
#                         body_part, damage, hit_color = self.determine_body_part_and_lethality(
#                             fx, fy, (x1, y1, x2, y2), self.current_frame
#                         )
#                         # Line 375 ke baad add karo:
#                         body_part = "none"  # ✅ Initialize the variable
                        
#                         # Set result based on damage type
#                         if damage == 'instant_kill':
#                             result = "instant_kill"
#                             label = f"KILL {body_part.upper()}"
#                         elif damage == 'critical':
#                             result = "critical_hit" 
#                             label = f"CRITICAL {body_part.upper()}"
#                         elif damage == 'heavy':
#                             result = "heavy_damage"
#                             label = f"HEAVY {body_part.upper()}"
#                         elif damage == 'light':
#                             result = "light_damage" 
#                             label = f"LIGHT {body_part.upper()}"
                            
#                         color = hit_color
#                         hit_person = person_idx
#                         damage_type = damage
#                         break

#             # Save marker
#             self.click_points.append((fx, fy, color, label, time.time() + 2.0))
            
#             # Save session data
#             self.session_data.append({
#                 "time": time.time() - self.start_time,
#                 "x": fx,
#                 "y": fy, 
#                 "result": result,
#                 "body_part": body_part if result != "miss" else "none",
#                 "damage_type": damage_type,
#                 "person": hit_person + 1 if hit_person >= 0 else 0
#             })
            
#             print(f"🎯 {result.upper()}: {body_part} at ({fx},{fy}) - Person {hit_person + 1 if hit_person >= 0 else 'None'}")
            
#             # Force immediate frame update
#             self.next_frame()

#     def cleanup_resources(self):
#         if hasattr(self, 'timer') and self.timer.isActive():
#             self.timer.stop()
            
#         if hasattr(self, 'cap') and self.cap and self.cap.isOpened():
#             self.cap.release()
#             self.cap = None
            
#         if hasattr(self, 'pose_detector') and self.pose_detector:
#             try:
#                 self.pose_detector.close()
#             except:
#                 pass

#     def close_session(self):
#         print("🛑 Closing shooting session...")
        
#         self.cleanup_resources()
        
#         # Export CSV
#         if self.session_data:
#             try:
#                 df = pd.DataFrame(self.session_data)
#                 csv_path = "session_summary.csv"
#                 df.to_csv(csv_path, index=False)
#                 print(f"💾 Session summary saved to {csv_path}")
                
#                 # IMPROVED Statistics
#                 total_shots = len(self.session_data)
#                 instant_kills = len([s for s in self.session_data if s['result'] == 'instant_kill'])
#                 critical_hits = len([s for s in self.session_data if s['result'] == 'critical_hit'])
#                 heavy_damage = len([s for s in self.session_data if s['result'] == 'heavy_damage'])
#                 light_damage = len([s for s in self.session_data if s['result'] == 'light_damage'])
#                 misses = len([s for s in self.session_data if s['result'] == 'miss'])
                
#                 accuracy = ((instant_kills + critical_hits + heavy_damage + light_damage) / total_shots * 100) if total_shots > 0 else 0
                
#                 print(f"📊 MILITARY SESSION STATS:")
#                 print(f"   Instant Kills: {instant_kills} (HEAD/NECK)")
#                 print(f"   Critical Hits: {critical_hits} (CHEST/BACK)")
#                 print(f"   Heavy Damage: {heavy_damage} (STOMACH)")
#                 print(f"   Light Damage: {light_damage} (LIMBS)")
#                 print(f"   Misses: {misses}")
#                 print(f"   Total Shots: {total_shots}")
#                 print(f"   Accuracy: {accuracy:.1f}%")
#                 print(f"   Lethality Rate: {(instant_kills/total_shots*100 if total_shots>0 else 0):.1f}%")
                
#             except Exception as e:
#                 print(f"❌ Error saving session summary: {e}")
            
#         self.hide()
#         self.session_finished.emit()
#         QTimer.singleShot(50, self.close)
#         print("⬅ Returned to Start Session")

#     def showEvent(self, event):
#         super().showEvent(event)
#         self.showFullScreen()
        
#     def closeEvent(self, event):
#         print("🔚 Close event triggered")
#         self.cleanup_resources()
#         event.accept()


# ui/shooting_session.py
import os
import warnings
import logging

# ✅ SUPPRESS ALL WARNINGS
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '2'
warnings.filterwarnings("ignore")
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('mediapipe').setLevel(logging.ERROR)

import cv2
import time
import math
import numpy as np
import pandas as pd
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QApplication
import mediapipe as mp

class ShootingSessionWindow(QWidget):
    session_finished = pyqtSignal()
    
    def __init__(self, parent=None, video_path=None):
        super().__init__(parent)
        self.video_path = video_path
        self.click_points = []
        self.session_data = []
        self.current_detections = []

        # Full-screen window
        self.setWindowTitle("Shooting Session")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        screen = QApplication.primaryScreen()
        self.setGeometry(screen.geometry())
        self.setStyleSheet("background-color: black;")

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        # Video display label
        self.video_label = QLabel(self)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.video_label)

        # Back button
        self.back_btn = QPushButton("⬅ Back (ESC)", self)
        self.back_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,165,0,180);
                color: white;
                border-radius: 10px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: rgba(255,165,0,255);
            }
        """)
        self.back_btn.setFixedSize(120, 40)
        self.back_btn.move(20,20)
        self.back_btn.raise_()
        self.back_btn.clicked.connect(self.close_session)
        self.back_btn.show()

        # Initialize detection models
        self.mp_pose = mp.solutions.pose
        self.pose_detector = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.4
        )
        
        # YOLO for person detection
        self.yolo_initialized = False
        self.initialize_yolo()

        # Video capture
        self.cap = None
        self.timer = QTimer()
        self.current_frame = None
        self.start_time = time.time()
        
        self.initialize_video()
        self.setMouseTracking(True)
        self.installEventFilter(self)

    def initialize_yolo(self):
        try:
            from ultralytics import YOLO
            self.yolo = YOLO("yolov8n.pt")
            self.yolo_initialized = True
            print("✅ YOLOv8 person detection initialized")
        except Exception as e:
            print(f"❌ YOLOv8 init error: {e}")
            self.yolo_initialized = False

    def point_distance(self, p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def landmarks_to_pixels(self, landmarks, bbox_w, bbox_h, bbox_x, bbox_y):
        pts = {}
        for idx, lm in enumerate(landmarks.landmark):
            px = int(bbox_x + lm.x * bbox_w)
            py = int(bbox_y + lm.y * bbox_h)
            pts[idx] = (px, py)
        return pts

    def determine_body_part_and_lethality(self, click_x, click_y, person_bbox, frame):
        """
        IMPROVED: New body parts with realistic military lethality
        """
        x1, y1, x2, y2 = person_bbox
        w = x2 - x1
        h = y2 - y1
        
        # Crop person region with padding
        pad = 10
        cx1 = max(0, x1 - pad)
        cy1 = max(0, y1 - pad)
        cx2 = min(frame.shape[1], x2 + pad)
        cy2 = min(frame.shape[0], y2 + pad)
        crop = frame[cy1:cy2, cx1:cx2].copy()
        
        if crop.size == 0:
            return 'unknown', 'none', (180, 180, 180)

        # Run MediaPipe pose on cropped person
        image_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        results = self.pose_detector.process(image_rgb)

        # Map click relative to crop
        rel_x = click_x - cx1
        rel_y = click_y - cy1

        if not results.pose_landmarks:
            # Fallback: use bbox proportions
            rel_norm_y = rel_y / max(1, (cy2 - cy1))
            if rel_norm_y < 0.15:
                return 'head', 'instant_kill', (255, 0, 0)  # Red
            elif rel_norm_y < 0.25:
                return 'neck', 'instant_kill', (255, 50, 50)  # Light Red
            elif rel_norm_y < 0.45:
                return 'chest', 'critical', (255, 165, 0)  # Orange
            elif rel_norm_y < 0.65:
                return 'stomach', 'heavy', (255, 255, 0)  # Yellow
            else:
                return 'limb', 'light', (0, 255, 0)  # Green
        else:
            # Convert landmarks to pixel coordinates
            pts = self.landmarks_to_pixels(results.pose_landmarks, cx2-cx1, cy2-cy1, cx1, cy1)
            
            # HEAD detection (nose, eyes, ears)
            head_indices = [0, 1, 2, 3, 4, 5, 6]
            HEAD_THRESHOLD = int(min(w, h) * 0.08)
            for idx in head_indices:
                if idx in pts:
                    if self.point_distance(pts[idx], (click_x, click_y)) <= HEAD_THRESHOLD:
                        return 'head', 'instant_kill', (255, 0, 0)  # Red

            # NECK detection (between shoulders)
            if 11 in pts and 12 in pts:  # Left & Right shoulders
                neck_x = (pts[11][0] + pts[12][0]) // 2
                neck_y = (pts[11][1] + pts[12][1]) // 2
                neck_radius = int(self.point_distance(pts[11], pts[12]) * 0.3)
                if self.point_distance((neck_x, neck_y), (click_x, click_y)) <= neck_radius:
                    return 'neck', 'instant_kill', (255, 50, 50)  # Light Red

            # CHEST detection (upper torso - front)
            if all(i in pts for i in [11, 12, 23, 24]):  # Shoulders & Hips
                left_sh, right_sh = pts[11], pts[12]
                left_hip, right_hip = pts[23], pts[24]
                
                # Chest area (upper portion of torso)
                chest_top_y = min(left_sh[1], right_sh[1])
                chest_bottom_y = (left_sh[1] + right_sh[1] + left_hip[1] + right_hip[1]) / 4
                chest_left_x = min(left_sh[0], right_sh[0])
                chest_right_x = max(left_sh[0], right_sh[0])
                
                if (chest_left_x <= click_x <= chest_right_x and 
                    chest_top_y <= click_y <= chest_bottom_y):
                    return 'chest', 'critical', (255, 165, 0)  # Orange

            # STOMACH detection (lower torso - front)
            if all(i in pts for i in [11, 12, 23, 24]):
                left_sh, right_sh = pts[11], pts[12]
                left_hip, right_hip = pts[23], pts[24]
                
                # Stomach area (lower portion of torso)
                stomach_top_y = (left_sh[1] + right_sh[1] + left_hip[1] + right_hip[1]) / 4
                stomach_bottom_y = max(left_hip[1], right_hip[1])
                stomach_left_x = min(left_hip[0], right_hip[0])
                stomach_right_x = max(left_hip[0], right_hip[0])
                
                if (stomach_left_x <= click_x <= stomach_right_x and 
                    stomach_top_y <= click_y <= stomach_bottom_y):
                    return 'stomach', 'heavy', (255, 255, 0)  # Yellow

            # BACK detection (if visible from landmarks)
            # For back, we check if click is in torso area but not in front parts
            if all(i in pts for i in [11, 12, 23, 24]):
                torso_xmin = min(pts[11][0], pts[12][0], pts[23][0], pts[24][0])
                torso_xmax = max(pts[11][0], pts[12][0], pts[23][0], pts[24][0])
                torso_ymin = min(pts[11][1], pts[12][1], pts[23][1], pts[24][1])
                torso_ymax = max(pts[11][1], pts[12][1], pts[23][1], pts[24][1])
                
                if (torso_xmin <= click_x <= torso_xmax and 
                    torso_ymin <= click_y <= torso_ymax):
                    return 'back', 'critical', (255, 100, 0)  # Dark Orange

            # LIMB detection (arms/legs)
            limb_indices = [13, 14, 15, 16, 23, 24, 25, 26, 27, 28]  # Arms & Legs
            LIMB_THRESHOLD = int(min(w, h) * 0.06)
            for idx in limb_indices:
                if idx in pts:
                    if self.point_distance(pts[idx], (click_x, click_y)) <= LIMB_THRESHOLD:
                        return 'limb', 'light', (0, 255, 0)  # Green

            # Default fallback
            return 'torso', 'heavy', (255, 200, 0)  # Light Orange

    def initialize_video(self):
        if not self.video_path or not os.path.exists(self.video_path):
            print(f"❌ Error: Video not found: {self.video_path}")
            self.close_session()
            return
            
        try:
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                print(f"❌ Error: Could not open video {self.video_path}")
                self.close_session()
                return
                
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
            self.timer.timeout.connect(self.next_frame)
            self.timer.start(int(1000/self.fps))
            print(f"✅ Video loaded successfully: {self.video_path}")
            
        except Exception as e:
            print(f"❌ Error initializing video: {e}")
            self.close_session()

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.close_session()
                return True
        return super().eventFilter(obj, event)

    def next_frame(self):
        if not self.cap or not self.cap.isOpened():
            self.close_session()
            return
            
        ret, frame = self.cap.read()
        if not ret:
            print("✅ Video ended normally")
            self.close_session()
            return

        self.current_frame = frame.copy()
        h, w = frame.shape[:2]

        # YOLO Person Detection
        self.current_detections = []
        
        if self.yolo_initialized and self.yolo:
            try:
                results = self.yolo(frame, imgsz=640, verbose=False)
                
                if len(results) > 0:
                    for box in results[0].boxes:
                        cls = int(box.cls.cpu().numpy()) if hasattr(box, 'cls') else None
                        if cls == 0:  # person class
                            xyxy = box.xyxy.cpu().numpy().flatten()[:4]
                            self.current_detections.append(xyxy)
                
                # Draw bounding boxes
                for i, (x1, y1, x2, y2) in enumerate(self.current_detections, 1):
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(frame, f"P{i}", (int(x1), max(12, int(y1) - 6)), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                               
            except Exception as e:
                print(f"❌ YOLO detection error: {e}")

        # Draw existing click markers
        current_time = time.time()
        self.click_points = [point for point in self.click_points if point[4] > current_time]
        
        for px, py, color, label, exp in self.click_points:
            cv2.circle(frame, (px, py), 12, color, -1)
            cv2.putText(frame, label, (px + 15, py), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Overlay info
        elapsed = time.time() - self.start_time
        detection_count = len(self.current_detections)
        cv2.putText(frame, f"Persons: {detection_count} | Time: {elapsed:.1f}s | Shots: {len(self.session_data)} | MILITARY MODE",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Show in PyQt label
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_qt = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0],
                            frame_rgb.strides[0], QImage.Format_RGB888)
            
            pixmap = QPixmap.fromImage(img_qt)
            pixmap = pixmap.scaled(self.video_label.width(), self.video_label.height(), 
                                 Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.video_label.setPixmap(pixmap)
        except Exception as e:
            print(f"❌ Error displaying frame: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.current_frame is not None:
            # ✅ FIX: Initialize ALL variables at the start
            result = "miss"
            label = "MISS"
            color = (180, 180, 180)
            hit_person = -1
            damage_type = "none"
            body_part = "none"  # ✅ CRITICAL FIX: Initialize here
            
            # Get video display area coordinates
            video_label_rect = self.video_label.geometry()
            click_pos = event.pos()
            
            if not video_label_rect.contains(click_pos):
                # Save miss with initialized variables
                self.save_shot_data(click_pos, result, label, color, hit_person, damage_type, body_part)
                return
                
            # Get current pixmap
            pixmap = self.video_label.pixmap()
            if not pixmap:
                self.save_shot_data(click_pos, result, label, color, hit_person, damage_type, body_part)
                return
                
            # Calculate scaling and offsets
            pixmap_width = pixmap.width()
            pixmap_height = pixmap.height()
            label_width = self.video_label.width()
            label_height = self.video_label.height()
            
            x_offset = (label_width - pixmap_width) // 2
            y_offset = (label_height - pixmap_height) // 2
            
            pixmap_x = click_pos.x() - x_offset
            pixmap_y = click_pos.y() - y_offset
            
            if (pixmap_x < 0 or pixmap_x >= pixmap_width or 
                pixmap_y < 0 or pixmap_y >= pixmap_height):
                self.save_shot_data(click_pos, result, label, color, hit_person, damage_type, body_part)
                return
                
            # Scale to original video frame coordinates
            frame_h, frame_w = self.current_frame.shape[:2]
            scale_x = frame_w / pixmap_width
            scale_y = frame_h / pixmap_height
            
            fx = int(pixmap_x * scale_x)
            fy = int(pixmap_y * scale_y)
            
            fx = max(0, min(fx, frame_w - 1))
            fy = max(0, min(fy, frame_h - 1))

            # Check if hit any detection
            if self.current_detections:
                for person_idx, bbox in enumerate(self.current_detections):
                    x1, y1, x2, y2 = map(int, bbox)
                    
                    if x1 <= fx <= x2 and y1 <= fy <= y2:
                        body_part, damage, hit_color = self.determine_body_part_and_lethality(
                            fx, fy, (x1, y1, x2, y2), self.current_frame
                        )
                        
                        # Set result based on damage type
                        if damage == 'instant_kill':
                            result = "instant_kill"
                            label = f"KILL {body_part.upper()}"
                        elif damage == 'critical':
                            result = "critical_hit" 
                            label = f"CRITICAL {body_part.upper()}"
                        elif damage == 'heavy':
                            result = "heavy_damage"
                            label = f"HEAVY {body_part.upper()}"
                        elif damage == 'light':
                            result = "light_damage" 
                            label = f"LIGHT {body_part.upper()}"
                            
                        color = hit_color
                        hit_person = person_idx
                        damage_type = damage
                        break

            # Save the shot data
            self.save_shot_data(click_pos, result, label, color, hit_person, damage_type, body_part, fx, fy)

    def save_shot_data(self, click_pos, result, label, color, hit_person, damage_type, body_part, fx=None, fy=None):
        """Save shot data to avoid code duplication"""
        if fx is None or fy is None:
            # If coordinates not provided, use click position
            fx, fy = click_pos.x(), click_pos.y()
        
        # Save marker
        self.click_points.append((fx, fy, color, label, time.time() + 2.0))
        
        # Save session data
        self.session_data.append({
            "time": time.time() - self.start_time,
            "x": fx,
            "y": fy, 
            "result": result,
            "body_part": body_part,
            "damage_type": damage_type,
            "person": hit_person + 1 if hit_person >= 0 else 0
        })
        
        print(f"🎯 {result.upper()}: {body_part} at ({fx},{fy}) - Person {hit_person + 1 if hit_person >= 0 else 'None'}")
        
        # Force immediate frame update
        self.next_frame()

    def cleanup_resources(self):
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
            
        if hasattr(self, 'cap') and self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
            
        if hasattr(self, 'pose_detector') and self.pose_detector:
            try:
                self.pose_detector.close()
            except:
                pass

    def close_session(self):
        print("🛑 Closing shooting session...")
        
        self.cleanup_resources()
        
        # Export CSV
        if self.session_data:
            try:
                df = pd.DataFrame(self.session_data)
                csv_path = "session_summary.csv"
                df.to_csv(csv_path, index=False)
                print(f"💾 Session summary saved to {csv_path}")
                
                # IMPROVED Statistics
                total_shots = len(self.session_data)
                instant_kills = len([s for s in self.session_data if s['result'] == 'instant_kill'])
                critical_hits = len([s for s in self.session_data if s['result'] == 'critical_hit'])
                heavy_damage = len([s for s in self.session_data if s['result'] == 'heavy_damage'])
                light_damage = len([s for s in self.session_data if s['result'] == 'light_damage'])
                misses = len([s for s in self.session_data if s['result'] == 'miss'])
                
                accuracy = ((instant_kills + critical_hits + heavy_damage + light_damage) / total_shots * 100) if total_shots > 0 else 0
                
                print(f"📊 MILITARY SESSION STATS:")
                print(f"   Instant Kills: {instant_kills} (HEAD/NECK)")
                print(f"   Critical Hits: {critical_hits} (CHEST/BACK)")
                print(f"   Heavy Damage: {heavy_damage} (STOMACH)")
                print(f"   Light Damage: {light_damage} (LIMBS)")
                print(f"   Misses: {misses}")
                print(f"   Total Shots: {total_shots}")
                print(f"   Accuracy: {accuracy:.1f}%")
                print(f"   Lethality Rate: {(instant_kills/total_shots*100 if total_shots>0 else 0):.1f}%")
                
            except Exception as e:
                print(f"❌ Error saving session summary: {e}")
            
        self.hide()
        self.session_finished.emit()
        QTimer.singleShot(50, self.close)
        print("⬅ Returned to Start Session")

    def showEvent(self, event):
        super().showEvent(event)
        self.showFullScreen()
        
    def closeEvent(self, event):
        print("🔚 Close event triggered")
        self.cleanup_resources()
        event.accept()