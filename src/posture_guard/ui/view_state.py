"""Values displayed by the face-landmark demonstration."""
from dataclasses import dataclass, field
import math
import time
from numbers import Real


def number(value, suffix='', digits=1):
    if isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(float(value)):
        return f'{value:.{digits}f}{suffix}'
    return '—'


@dataclass(frozen=True)
class FaceFrame:
    frame: object
    landmarks: tuple
    fps: float
    inference_ms: float
    elapsed_seconds: float
    width: int
    height: int
    published_at: float

    @property
    def face_present(self):
        return bool(self.landmarks)


@dataclass(frozen=True)
class ModuleStatus:
    """Presentation status supplied by the module owner, never inferred by UI."""
    state: str = 'disconnected'
    text: str = ''

    def __post_init__(self):
        if self.state not in ('disconnected', 'waiting', 'ready', 'warning', 'error'):
            raise ValueError('Unsupported module state')
        if not isinstance(self.text, str):
            raise ValueError('Status text must be a string')


@dataclass(frozen=True)
class DistanceStatus(ModuleStatus):
    centimeters: float | None = None

    def __post_init__(self):
        super().__post_init__()
        if self.centimeters is not None and (not isinstance(self.centimeters, Real)
                or isinstance(self.centimeters, bool) or not math.isfinite(self.centimeters)
                or self.centimeters <= 0):
            raise ValueError('Distance must be a finite positive measurement or None')


@dataclass(frozen=True)
class MonitoringSnapshot:
    """Integration point for the other team members' processing modules."""
    posture: ModuleStatus = field(default_factory=ModuleStatus)
    distance: DistanceStatus = field(default_factory=DistanceStatus)
    calibration: ModuleStatus = field(default_factory=ModuleStatus)
    alert: ModuleStatus = field(default_factory=ModuleStatus)
    updated_at: float = field(default_factory=time.perf_counter)

    def __post_init__(self):
        for value in (self.posture, self.calibration, self.alert):
            if not isinstance(value, ModuleStatus):
                raise TypeError('Module results must use ModuleStatus')
        if not isinstance(self.distance, DistanceStatus):
            raise TypeError('Distance result must use DistanceStatus')
        if not isinstance(self.updated_at, Real) or not math.isfinite(self.updated_at):
            raise ValueError('updated_at must be a monotonic timestamp')
