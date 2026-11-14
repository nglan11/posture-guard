"""Open a laptop camera, releasing failed backend attempts."""
import sys
import cv2


def open_camera(index=0):
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF] if sys.platform == "win32" else [cv2.CAP_ANY]
    for backend in backends:
        camera = cv2.VideoCapture(index, backend)
        if camera.isOpened():
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
            ok, frame = camera.read()
            if ok:
                return camera, frame
        camera.release()
    raise RuntimeError(f"Không mở được webcam {index}. Đóng ứng dụng đang dùng camera và kiểm tra quyền Camera trong Windows Settings.")
