"""Camera -> Face Landmarker -> optional drawing -> latest frame for UI."""
from collections import deque
import queue
import threading
import time
import cv2
from posture_guard.vision.camera import open_camera
from posture_guard.vision.face_detector import FaceDetector, draw_landmarks
from posture_guard.ui.view_state import FaceFrame


class CameraWorker(threading.Thread):
    def __init__(self, camera_index=0):
        super().__init__(daemon=True)
        self.camera_index = camera_index
        self.stop_event = threading.Event()
        self.frames = queue.Queue(maxsize=1)
        self.overlay_mode = 'mesh'
        self.mirror = True
        self.error = None
        self.summary = None

    def run(self):
        camera = detector = None
        count = detected = 0
        latencies = deque(maxlen=4096)
        inference_total = 0.0
        start = None
        try:
            detector = FaceDetector()
            if self.stop_event.is_set():
                return
            camera, frame = open_camera(self.camera_index)
            start = time.perf_counter()
            previous, fps = start, 0.0
            while not self.stop_event.is_set():
                if self.mirror:
                    frame = cv2.flip(frame, 1)
                tick = time.perf_counter()
                landmarks = detector.detect(frame, int(tick * 1000))
                inference_ms = (time.perf_counter() - tick) * 1000
                inference_total += inference_ms
                latencies.append(inference_ms)
                count += 1
                detected += bool(landmarks)
                draw_landmarks(frame, landmarks, self.overlay_mode)
                now = time.perf_counter()
                instant = 1 / max(now - previous, 1e-6)
                fps = instant if count == 1 else .9 * fps + .1 * instant
                previous = now
                height, width = frame.shape[:2]
                # Copy numerical landmarks out of the MediaPipe result for integration.
                coordinates = tuple((p.x, p.y, p.z) for p in landmarks)
                item = FaceFrame(frame, coordinates, fps, inference_ms, now-start,
                                 width, height, now)
                try:
                    self.frames.get_nowait()
                except queue.Empty:
                    pass
                self.frames.put_nowait(item)
                if self.stop_event.is_set():
                    break
                ok, frame = camera.read()
                if not ok:
                    raise RuntimeError('Webcam ngừng trả hình ảnh. Hãy thử mở lại camera.')
        except Exception as exc:
            self.error = str(exc)
        finally:
            elapsed = time.perf_counter()-start if start else 0
            ordered = sorted(latencies)
            self.summary = {
                'scope': 'face_landmarks_only',
                'camera_index': self.camera_index,
                'frames': count, 'detected_frames': detected,
                'elapsed_seconds': round(elapsed, 2),
                'average_fps': round(count/elapsed, 2) if elapsed else 0,
                'detection_ratio': round(detected/count, 4) if count else 0,
                'inference_mean_ms': round(inference_total/count, 2) if count else None,
                'inference_p95_ms': round(ordered[min(int(len(ordered)*.95), len(ordered)-1)], 2) if ordered else None,
                'p95_window_frames': len(ordered),
                'error': self.error,
            }
            if camera is not None:
                camera.release()
            if detector is not None:
                detector.close()
