"""Latest-frame worker: a slow UI never builds up a video queue."""
import queue
import threading
import time
import cv2
from posture_guard.vision.camera import open_camera
from posture_guard.vision.face_detector import FaceDetector, draw_landmarks
from posture_guard.distance.monitor import DistanceMonitor


class CameraWorker(threading.Thread):
    def __init__(self, camera_index=0):
        super().__init__(daemon=True)
        self.camera_index = camera_index
        self.stop_event = threading.Event()
        self.frames = queue.Queue(maxsize=1)
        self.error = None
        self.show_landmarks = True
        self.summary = None
        self.commands = queue.Queue()

    def run(self):
        camera = detector = None
        count = detected = 0
        latencies = []
        start = None
        monitor = DistanceMonitor()
        try:
            detector = FaceDetector()
            camera, frame = open_camera(self.camera_index)
            start = time.perf_counter()
            previous = start
            fps = 0.0
            while not self.stop_event.is_set():
                frame = cv2.flip(frame, 1)
                tick = time.perf_counter()
                landmarks = detector.detect(frame, int(tick * 1000))
                try:
                    if self.commands.get_nowait() == 'calibrate':
                        monitor.begin_calibration()
                except queue.Empty:
                    pass
                h, w = frame.shape[:2]
                distance = monitor.update(landmarks, w, h, time.perf_counter())
                color = (60, 60, 240) if distance['warning'] else (220, 180, 60)
                cv2.ellipse(frame, (w // 2, h // 2), (int(w * .28), int(h * .43)), 0, 0, 360, color, 2)
                latency = (time.perf_counter() - tick) * 1000
                latencies.append(latency)
                count += 1
                detected += bool(landmarks)
                if self.show_landmarks:
                    draw_landmarks(frame, landmarks)
                now = time.perf_counter()
                instantaneous = 1 / max(now - previous, 1e-6)
                fps = instantaneous if count == 1 else fps * 0.9 + instantaneous * 0.1
                previous = now
                item = (frame, fps, latency, len(landmarks), detected / count, now - start, distance)
                try:
                    self.frames.get_nowait()
                except queue.Empty:
                    pass
                self.frames.put_nowait(item)
                ok, frame = camera.read()
                if not ok:
                    raise RuntimeError("Webcam ngừng trả hình ảnh. Hãy thử kết nối lại.")
        except Exception as exc:
            self.error = str(exc)
        finally:
            elapsed = time.perf_counter() - start if start else 0
            ordered = sorted(latencies)
            self.summary = {
                "frames": count, "detected_frames": detected,
                "elapsed_seconds": round(elapsed, 2),
                "average_fps": round(count / elapsed, 2) if elapsed else 0,
                "detection_ratio": round(detected / count, 4) if count else 0,
                "inference_p95_ms": round(ordered[min(int(len(ordered) * .95), len(ordered)-1)], 2) if ordered else None,
                "error": self.error,
                "baseline_pixels": monitor.baseline,
                "reference_cm": 50,
                "warning_rule": "eye_pixels > baseline * 1.25 for > 2 seconds",
            }
            if camera is not None:
                camera.release()
            if detector is not None:
                detector.close()
