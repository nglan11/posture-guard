"""MediaPipe Tasks face landmarks, with temporal tracking for a single face."""
from pathlib import Path
import cv2
import mediapipe as mp

MODEL_PATH = Path(__file__).resolve().parents[3] / "data/models/face_landmarker.task"


class FaceDetector:
    def __init__(self, model_path=MODEL_PATH):
        if not Path(model_path).is_file():
            raise FileNotFoundError("Thiếu model. Chạy: powershell -File scripts/setup.ps1")
        self.detector = mp.tasks.vision.FaceLandmarker.create_from_options(
            mp.tasks.vision.FaceLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
                running_mode=mp.tasks.vision.RunningMode.VIDEO,
                num_faces=1,
                min_face_detection_confidence=0.5,
                min_face_presence_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        )
        self.timestamp = -1

    def detect(self, frame, timestamp_ms):
        self.timestamp = max(self.timestamp + 1, timestamp_ms)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.detector.detect_for_video(
            mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), self.timestamp
        )
        return result.face_landmarks[0] if result.face_landmarks else []

    def close(self):
        self.detector.close()


def draw_landmarks(frame, landmarks):
    height, width = frame.shape[:2]
    for point in landmarks:
        cv2.circle(frame, (int(point.x * width), int(point.y * height)),
                   1, (100, 240, 110), -1, cv2.LINE_AA)
