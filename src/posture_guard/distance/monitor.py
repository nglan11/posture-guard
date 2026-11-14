"""Session calibration and time-filtered proximity warning from the proposal."""
from collections import deque
from statistics import median, pstdev
from posture_guard.distance.eye_geometry import eye_distance, frontal_in_oval
from posture_guard.distance.pinhole import estimate_distance


class DistanceMonitor:
    def __init__(self):
        self.baseline = None
        self.calibrating = False
        self.samples = deque(maxlen=30)
        self.sample_start = None
        self.close_since = None
        self.previous_time = None
        self.filtered = None

    def begin_calibration(self):
        self.__init__()
        self.calibrating = True

    def update(self, landmarks, width, height, now):
        pixels = eye_distance(landmarks, width, height)
        valid = pixels is not None and frontal_in_oval(landmarks, width, height)
        result = dict(distance_cm=None, warning=False, baseline_pixels=self.baseline,
                      calibration_samples=0, message='Chưa hiệu chuẩn: ngồi cách webcam 50 cm, nhìn thẳng và nhấn Hiệu chuẩn.')
        gap = self.previous_time is not None and now - self.previous_time > .5
        self.previous_time = now
        if gap:
            self.close_since = None
            self.filtered = None
            self.samples.clear()
            self.sample_start = None
        if not valid:
            self.samples.clear()
            self.sample_start = None
            self.close_since = None
            self.filtered = None
            result['message'] = 'Không đo: cần thấy rõ hai mắt, nhìn thẳng và đặt mặt trong oval.'
            return result
        if self.calibrating:
            if self.sample_start is None:
                self.sample_start = now
            self.samples.append(pixels)
            result['calibration_samples'] = len(self.samples)
            result['message'] = f'Giữ yên ở 50 cm: {len(self.samples)}/30 mẫu ổn định.'
            if len(self.samples) == 30 and now - self.sample_start >= 1:
                if pstdev(self.samples) / median(self.samples) <= .04:
                    self.baseline = median(self.samples)
                    self.calibrating = False
                    result['baseline_pixels'] = self.baseline
                    result['message'] = 'Hiệu chuẩn thành công ở mốc 50 cm.'
                else:
                    self.samples.clear()
                    self.sample_start = None
                    result['message'] = 'Mẫu dao động quá nhiều; giữ yên, hệ thống sẽ lấy lại mẫu.'
            return result
        if self.baseline is None:
            return result
        self.filtered = pixels if self.filtered is None else .25 * pixels + .75 * self.filtered
        result['distance_cm'] = estimate_distance(self.filtered, self.baseline)
        if self.filtered > self.baseline * 1.25:
            if self.close_since is None:
                self.close_since = now
            result['warning'] = now - self.close_since > 2
            result['message'] = 'Đang nhìn gần; theo dõi thời gian…'
            if result['warning']:
                result['message'] = 'CẢNH BÁO: nhìn quá gần. Hãy ngồi xa webcam hơn.'
        else:
            self.close_since = None
            result['message'] = 'Khoảng cách chưa vượt ngưỡng cảnh báo theo baseline.'
        return result
