"""Hardware-independent checks for release and detection failures."""
import unittest
from unittest.mock import MagicMock, patch
from posture_guard.vision.camera import open_camera
from posture_guard.ui.camera_worker import CameraWorker


class WebcamTests(unittest.TestCase):
    @patch('posture_guard.vision.camera.cv2.VideoCapture')
    def test_failed_backends_release_camera(self, capture):
        capture.return_value.isOpened.return_value = False
        with self.assertRaises(RuntimeError):
            open_camera(0)
        self.assertEqual(capture.return_value.release.call_count, capture.call_count)

    @patch('posture_guard.ui.camera_worker.FaceDetector')
    @patch('posture_guard.ui.camera_worker.open_camera')
    def test_inference_failure_releases_resources(self, open_mock, detector_mock):
        camera = MagicMock()
        open_mock.return_value = camera, MagicMock()
        detector_mock.return_value.detect.side_effect = RuntimeError('inference failed')
        with patch('posture_guard.ui.camera_worker.cv2.flip'):
            worker = CameraWorker()
            worker.run()
        camera.release.assert_called_once()
        detector_mock.return_value.close.assert_called_once()
        self.assertEqual(worker.summary['frames'], 0)
        self.assertEqual(worker.error, 'inference failed')


if __name__ == '__main__':
    unittest.main()
