"""MediaPipe Tasks face landmarks, with temporal tracking for a single face."""
from pathlib import Path
import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarksConnections as Connections

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


def _edges(connections):
    return np.array(sorted({tuple(sorted((c.start, c.end))) for c in connections}), dtype=np.int32)


MESH = _edges(Connections.FACE_LANDMARKS_TESSELATION)
CONTOURS = _edges(Connections.FACE_LANDMARKS_CONTOURS)
IRISES = _edges(Connections.FACE_LANDMARKS_LEFT_IRIS + Connections.FACE_LANDMARKS_RIGHT_IRIS)


def draw_landmarks(frame, landmarks, mode='mesh'):
    """Only draw actual detected geometry; never synthesize a face or confidence."""
    if mode not in ('mesh', 'points', 'none'):
        raise ValueError('Unknown landmark drawing mode')
    if not landmarks or mode == 'none':
        return
    height, width = frame.shape[:2]
    xy = np.array([(p.x * width, p.y * height) for p in landmarks])
    if not np.isfinite(xy).all():
        return
    xy = np.clip(xy, [-width, -height], [2*width, 2*height]).astype(np.int32)
    if mode == 'points':
        for x, y in xy:
            cv2.circle(frame, (int(x), int(y)), 1, (130, 245, 125), -1, cv2.LINE_AA)
        return
    for edges, color, thickness in ((MESH, (130, 145, 120), 1),
                                     (CONTOURS, (125, 240, 150), 1),
                                     (IRISES, (100, 235, 245), 1)):
        valid = edges[np.max(edges, axis=1) < len(xy)]
        if len(valid):
            cv2.polylines(frame, xy[valid], False, color, thickness, cv2.LINE_AA)
