import cv2
import mediapipe as mp
import numpy as np
import math
from collections import deque
import threading
import time

mp_face_mesh = mp.solutions.face_mesh

def dist(p1, p2):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1])

def clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))

MOUTH_LEFT = 61
MOUTH_RIGHT = 291
MOUTH_TOP = 13
MOUTH_BOTTOM = 14

LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
LEFT_EYE_LEFT = 33
LEFT_EYE_RIGHT = 133

RIGHT_EYE_TOP = 386
RIGHT_EYE_BOTTOM = 374
RIGHT_EYE_LEFT = 362
RIGHT_EYE_RIGHT = 263

class VisionAnalyzer:
    def __init__(self):
        self.latest = {
            "positivity": 0,
            "attention": 0,
            "confidence": 0,
            "stress": 0,
            "comfort": 0,
            "stability": 0
        }
        self.running = False

        # ✅ ADDED FOR STREAMING (does NOT change logic)
        self.latest_frame = None
        self.lock = threading.Lock()

    def start(self):
        self.running = True

        cap = cv2.VideoCapture(0)

        movement_history = deque(maxlen=15)
        prev_pts = None

        with mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        ) as face_mesh:

            self.running = True
            while self.running and self.start_flag:

                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb)

                if results.multi_face_landmarks:
                    face = results.multi_face_landmarks[0]
                    pts = [(int(lm.x * w), int(lm.y * h)) for lm in face.landmark]

                    mouth_w = dist(pts[MOUTH_LEFT], pts[MOUTH_RIGHT])
                    mouth_h = max(dist(pts[MOUTH_TOP], pts[MOUTH_BOTTOM]), 1)

                    smile_ratio = mouth_w / mouth_h
                    jaw_ratio = mouth_h / mouth_w

                    le_h = dist(pts[LEFT_EYE_TOP], pts[LEFT_EYE_BOTTOM])
                    le_w = dist(pts[LEFT_EYE_LEFT], pts[LEFT_EYE_RIGHT])
                    re_h = dist(pts[RIGHT_EYE_TOP], pts[RIGHT_EYE_BOTTOM])
                    re_w = dist(pts[RIGHT_EYE_LEFT], pts[RIGHT_EYE_RIGHT])

                    eye_ratio = ((le_h / le_w) + (re_h / re_w)) / 2

                    smile = clamp((smile_ratio - 1.4) * 50)
                    eye_open = clamp((eye_ratio - 0.14) * 350)
                    jaw_open = clamp(jaw_ratio * 220)

                    if prev_pts is not None:
                        move = dist(pts[1], prev_pts[1])
                        movement_history.append(move)

                    prev_pts = pts.copy()

                    avg_move = np.mean(movement_history) if movement_history else 0
                    instability = clamp(avg_move * 6)
                    stability = 100 - instability

                    comfort = clamp((eye_open * 0.6 + (100 - jaw_open) * 0.4))
                    uncomfortable = 100 - comfort

                    positivity = clamp(smile * 0.8 + comfort * 0.2)
                    attention = clamp(eye_open * 0.7 + stability * 0.3)
                    stress = clamp(uncomfortable * 0.6 + instability * 0.4)

                    confidence = clamp(
                        comfort * 0.4 +
                        (100 - stress) * 0.3 +
                        stability * 0.2 +
                        positivity * 0.1
                    )

                    # Save metrics (UNCHANGED)
                    self.latest["positivity"] = int(positivity)
                    self.latest["attention"] = int(attention)
                    self.latest["confidence"] = int(confidence)
                    self.latest["stress"] = int(stress)
                    self.latest["comfort"] = int(comfort)
                    self.latest["stability"] = int(stability)

                    # Draw UI (UNCHANGED)
                    y = 40
                    dy = 35
                    # cv2.putText(frame, f"Positivity: {int(positivity)}%", (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2); y += dy
                    # cv2.putText(frame, f"Attention: {int(attention)}%", (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2); y += dy
                    # cv2.putText(frame, f"Confidence: {int(confidence)}%", (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2); y += dy
                    # cv2.putText(frame, f"Stress: {int(stress)}%", (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2); y += dy
                    # cv2.putText(frame, f"Comfort: {int(comfort)}%", (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2); y += dy
                    # cv2.putText(frame, f"Stability: {int(stability)}%", (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

                # ✅ SAVE FRAME FOR STREAMING (ADDED)
                with self.lock:
                    self.latest_frame = frame.copy()

                time.sleep(0.03)  # limit FPS slightly

        cap.release()

    def get_metrics(self):
        return self.latest.copy()

    def get_frame(self):
        with self.lock:
            if self.latest_frame is None:
                return None
            ret, jpeg = cv2.imencode(".jpg", self.latest_frame)
            if not ret:
                return None
            return jpeg.tobytes()

    def stop(self):
        self.running = False
        self.start_flag = False


