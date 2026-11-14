"""Personal baseline pinhole estimate; centimeters refer to camera distance."""
import math


def estimate_distance(current_pixels, baseline_pixels, reference_cm=50.0):
    if not all(math.isfinite(x) and x > 0 for x in (current_pixels, baseline_pixels, reference_cm)):
        raise ValueError('Distances must be finite and positive')
    return reference_cm * baseline_pixels / current_pixels
