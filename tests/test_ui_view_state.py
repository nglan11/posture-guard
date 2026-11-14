import math
import unittest
from posture_guard.ui.view_state import FaceFrame, number


class FaceViewTests(unittest.TestCase):
    def test_presence_comes_only_from_detected_landmarks(self):
        empty = FaceFrame(None, (), 30, 10, 2, 640, 480, 0)
        found = FaceFrame(None, ((.5, .5, 0),), 30, 10, 2, 640, 480, 0)
        self.assertFalse(empty.face_present)
        self.assertTrue(found.face_present)

    def test_unknown_measurements_never_become_zero(self):
        for value in (None, math.nan, math.inf, '30', True):
            self.assertEqual(number(value), '—')
        self.assertEqual(number(0, ' ms'), '0.0 ms')
