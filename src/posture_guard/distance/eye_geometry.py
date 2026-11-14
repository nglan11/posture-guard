"""Iris centres (468, 473) in image pixels, not normalized coordinates."""
import math


def eye_distance(landmarks, width, height):
    if len(landmarks) < 478:
        return None
    a, b = landmarks[468], landmarks[473]
    values = (a.x, a.y, b.x, b.y)
    if not all(math.isfinite(v) and 0 <= v <= 1 for v in values):
        return None
    distance = math.hypot((a.x - b.x) * width, (a.y - b.y) * height)
    return distance if distance >= 5 else None


def frontal_in_oval(landmarks, width, height):
    """Conservative 2D quality gate, not a calibrated head-pose estimate."""
    ipd = eye_distance(landmarks, width, height)
    if ipd is None:
        return False
    a, b, nose = landmarks[468], landmarks[473], landmarks[1]
    if abs(a.y - b.y) * height / ipd > .18:
        return False
    if abs(nose.x - (a.x + b.x) / 2) * width / ipd > .25:
        return False
    for index in (10, 152, 234, 454):
        p = landmarks[index]
        if not (math.isfinite(p.x) and math.isfinite(p.y)):
            return False
        if ((p.x - .5) / .28) ** 2 + ((p.y - .5) / .43) ** 2 > 1:
            return False
    return True
