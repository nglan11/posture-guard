import time
import tkinter as tk
import unittest
from unittest.mock import patch
import numpy as np
from posture_guard.ui.main_window import MainWindow, MODES
from posture_guard.ui.view_state import FaceFrame, MonitoringSnapshot, ModuleStatus, DistanceStatus


class FaceWindowTests(unittest.TestCase):
    def setUp(self):
        try:
            self.app = MainWindow()
        except tk.TclError as exc:
            self.skipTest(str(exc))
        self.app.withdraw()
        self.app.update_idletasks()

    def tearDown(self):
        if hasattr(self, 'app'):
            self.app.destroy()

    def frame(self, landmarks):
        return FaceFrame(np.zeros((480, 640, 3), np.uint8), landmarks, 30, 12, 10, 640, 480, time.perf_counter())

    def test_face_loss_clears_previous_result(self):
        self.app._render(self.frame(((.5, .5, 0),)*478))
        self.assertEqual(self.app.values['landmarks'].get(), '478')
        self.assertIn('Đã tìm thấy', self.app.face_status.cget('text'))
        self.app._render(self.frame(()))
        self.assertEqual(self.app.values['landmarks'].get(), '0')
        self.assertIn('Đang tìm', self.app.face_status.cget('text'))

    @patch('posture_guard.ui.main_window.CameraWorker')
    def test_options_and_stop_do_not_reopen_or_block_camera(self, worker_class):
        worker = worker_class.return_value
        self.app.start()
        self.app.start()
        worker_class.assert_called_once_with(0)
        self.app.mode.set('Ảnh gốc')
        self.app.mirror.set(False)
        self.app.update_options()
        self.assertEqual(worker.overlay_mode, 'none')
        self.assertFalse(worker.mirror)
        self.app.stop()
        worker.stop_event.set.assert_called_once()
        worker.join.assert_not_called()

    def test_stopped_values_do_not_remain_live(self):
        self.app._render(self.frame(((.5, .5, 0),)))
        self.app._clear_metrics()
        self.assertIsNone(self.app.last_state)
        self.assertEqual(self.app.values['fps'].get(), '—')

    def test_primary_controls_remain_visible_in_compact_window(self):
        self.app.deiconify()
        self.app.geometry('940x660')
        self.app.update()
        bottom = self.app.winfo_rooty()+self.app.winfo_height()
        for widget in (self.app.start_button, self.app.stop_button, self.app.face_status, self.app.status):
            self.assertTrue(widget.winfo_ismapped())
            self.assertLessEqual(widget.winfo_rooty()+widget.winfo_height(), bottom)

    def test_system_scaffold_does_not_invent_unconnected_results(self):
        for label in self.app.monitoring_labels.values():
            self.assertEqual(label.cget('text'), 'Chưa kết nối')
        self.app.set_monitoring_state(MonitoringSnapshot(distance=DistanceStatus(state='ready')))
        self.assertEqual(self.app.monitoring_labels['distance'].cget('text'), 'Chưa có số đo')

    def test_real_module_results_can_be_bound_then_cleared(self):
        # Synthetic fixture tests the interface only, not an implemented algorithm.
        self.app.set_monitoring_state(MonitoringSnapshot(
            posture=ModuleStatus('ready', 'Kết quả từ module tư thế'),
            distance=DistanceStatus('ready', centimeters=47.2),
            alert=ModuleStatus('warning', 'Thông báo từ module cảnh báo')))
        self.assertEqual(self.app.monitoring_labels['distance'].cget('text'), '47.2 cm')
        self.assertEqual(self.app.monitoring_labels['alert'].cget('text'), 'Thông báo từ module cảnh báo')
        self.app._clear_metrics()
        self.assertEqual(self.app.monitoring_labels['distance'].cget('text'), 'Chưa kết nối')

    def test_module_inbox_keeps_only_latest_snapshot(self):
        self.app.publish_monitoring_state(MonitoringSnapshot())
        latest = MonitoringSnapshot(posture=ModuleStatus('waiting'))
        self.app.publish_monitoring_state(latest)
        self.assertEqual(self.app.monitoring_queue.qsize(), 1)
        self.assertIs(self.app.monitoring_queue.get_nowait(), latest)
