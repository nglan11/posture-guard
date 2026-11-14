"""Run a bounded physical webcam benchmark; never store camera images."""
import argparse
import json
import time
from pathlib import Path
from posture_guard.ui.camera_worker import CameraWorker


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--seconds', type=float, default=30)
    args = parser.parse_args()
    if args.seconds <= 0:
        parser.error('--seconds must be positive')
    worker = CameraWorker(args.camera)
    worker.start()
    startup_deadline = time.monotonic() + 30
    while worker.is_alive() and worker.frames.empty() and time.monotonic() < startup_deadline:
        time.sleep(.1)
    deadline = time.monotonic() + args.seconds if not worker.frames.empty() else time.monotonic()
    while worker.is_alive() and time.monotonic() < deadline:
        time.sleep(.1)
    worker.stop_event.set()
    worker.join(timeout=15)
    if worker.is_alive():
        raise SystemExit('Camera/model startup did not finish; no benchmark result available.')
    summary = worker.summary
    output = Path('results/logs/webcam-check.json')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary['error'] or not summary['frames']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
