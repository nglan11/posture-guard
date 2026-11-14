from types import SimpleNamespace
import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from posture_guard.ui.camera_worker import CameraWorker
from posture_guard.vision.face_detector import draw_landmarks


class FaceDetectionTests(unittest.TestCase):
    def points(self):
        return [SimpleNamespace(x=.3+(i%20)*.02, y=.3+(i//20)*.015, z=0) for i in range(478)]

    def test_overlay_uses_detection_and_original_mode_preserves_pixels(self):
        frame = np.zeros((480, 640, 3), np.uint8)
        draw_landmarks(frame, self.points(), 'none')
        self.assertFalse(frame.any())
        draw_landmarks(frame, [], 'mesh')
        self.assertFalse(frame.any())
        draw_landmarks(frame, self.points(), 'mesh')
        self.assertTrue(frame.any())

    @patch('posture_guard.ui.camera_worker.FaceDetector')
    @patch('posture_guard.ui.camera_worker.open_camera')
    def test_worker_exports_actual_coordinates_and_releases_resources(self, open_mock, detector_mock):
        camera = MagicMock()
        open_mock.return_value = camera, np.zeros((480, 640, 3), np.uint8)
        worker = CameraWorker()
        points = self.points()
        def detect(*args):
            worker.stop_event.set()
            return points
        detector_mock.return_value.detect.side_effect = detect
        worker.run()
        packet = worker.frames.get_nowait()
        self.assertEqual(len(packet.landmarks), 478)
        self.assertEqual(packet.landmarks[0], (points[0].x, points[0].y, 0))
        self.assertIsNone(worker.error)
        self.assertEqual(worker.summary['scope'], 'face_landmarks_only')
        self.assertNotIn('reference_cm', worker.summary)
        camera.release.assert_called_once()
        detector_mock.return_value.close.assert_called_once()
