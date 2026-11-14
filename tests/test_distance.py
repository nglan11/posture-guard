import math
from types import SimpleNamespace
import unittest
from posture_guard.distance.eye_geometry import eye_distance
from posture_guard.distance.pinhole import estimate_distance
from posture_guard.distance.monitor import DistanceMonitor


def face(span=.2):
    points = [SimpleNamespace(x=.5, y=.5) for _ in range(478)]
    points[468] = SimpleNamespace(x=.5-span/2, y=.45)
    points[473] = SimpleNamespace(x=.5+span/2, y=.45)
    return points


class DistanceTests(unittest.TestCase):
    def calibrated(self):
        monitor = DistanceMonitor()
        monitor.begin_calibration()
        for i in range(30):
            result = monitor.update(face(), 640, 480, i*.04)
        self.assertAlmostEqual(result['baseline_pixels'], 128)
        return monitor

    def test_pinhole_reference_and_scaling(self):
        self.assertEqual(estimate_distance(100, 100), 50)
        self.assertEqual(estimate_distance(125, 100), 40)
        for invalid in (0, -1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                estimate_distance(invalid, 100)

    def test_eye_geometry_uses_both_pixel_axes(self):
        points = face()
        points[473].y = .55
        self.assertAlmostEqual(eye_distance(points, 640, 480), math.hypot(128, 48))
        self.assertIsNone(eye_distance([], 640, 480))

    def test_calibration_needs_stability(self):
        monitor = DistanceMonitor()
        monitor.begin_calibration()
        for i in range(60):
            monitor.update(face(.16 if i % 2 else .24), 640, 480, i*.04)
        self.assertIsNone(monitor.baseline)

    def test_warning_requires_duration_and_resets_on_missing_face(self):
        monitor = self.calibrated()
        for i in range(20):
            result = monitor.update(face(.28), 640, 480, 1.3+i*.1)
        self.assertFalse(result['warning'])
        for i in range(20, 35):
            result = monitor.update(face(.28), 640, 480, 1.3+i*.1)
        self.assertTrue(result['warning'])
        result = monitor.update([], 640, 480, 4.8)
        self.assertFalse(result['warning'])
        self.assertIsNone(result['distance_cm'])
        result = monitor.update(face(.28), 640, 480, 4.9)
        self.assertFalse(result['warning'])

    def test_frame_gap_cannot_trigger_warning(self):
        monitor = self.calibrated()
        monitor.update(face(.28), 640, 480, 1.3)
        result = monitor.update(face(.28), 640, 480, 10)
        self.assertFalse(result['warning'])

    def test_bad_head_alignment_suppresses_distance(self):
        monitor = self.calibrated()
        points = face()
        points[1].x = .8
        result = monitor.update(points, 640, 480, 1.3)
        self.assertIsNone(result['distance_cm'])


if __name__ == '__main__':
    unittest.main()
