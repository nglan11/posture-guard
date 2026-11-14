"""Vietnamese webcam dashboard; inference runs off the Tk event loop."""
import json
from pathlib import Path
import queue
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import cv2
from PIL import Image, ImageTk
from posture_guard.ui.camera_worker import CameraWorker


class MainWindow(tk.Tk):
    def __init__(self):
        if sys.platform == "win32":
            import ctypes
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except (OSError, AttributeError):
                pass
        super().__init__()
        self.title("Posture Guard • Kiểm tra landmarks")
        width = min(1060, self.winfo_screenwidth() - 80)
        height = min(740, self.winfo_screenheight() - 100)
        self.geometry(f"{width}x{height}")
        self.minsize(min(840, width), min(600, height))
        self.configure(bg="#101827")
        self.worker = None
        self.closing = False
        self.last_summary = None
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#101827")
        style.configure("TLabel", background="#101827", foreground="#e2e8f0", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 11), padding=9)
        body = ttk.Frame(self, padding=22)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="POSTURE GUARD", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        ttk.Label(body, text="Kiểm tra webcam và các điểm mốc khuôn mặt • xử lý trên máy").pack(anchor="w", pady=(2, 15))
        controls = ttk.Frame(body)
        controls.pack(fill="x")
        ttk.Label(controls, text="Camera:").pack(side="left")
        self.index = tk.StringVar(value="0")
        ttk.Spinbox(controls, from_=0, to=9, width=4, textvariable=self.index).pack(side="left", padx=8)
        self.start_button = ttk.Button(controls, text="Bắt đầu", command=self.start)
        self.start_button.pack(side="left", padx=5)
        self.stop_button = ttk.Button(controls, text="Dừng", command=self.stop, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        ttk.Button(controls, text="Lưu kết quả", command=self.save).pack(side="right")
        self.overlay = tk.BooleanVar(value=True)
        tk.Checkbutton(controls, text="Hiện landmarks", variable=self.overlay, bg="#101827", fg="#e2e8f0", selectcolor="#101827", activebackground="#101827", activeforeground="white").pack(side="right", padx=12)
        calibration = ttk.Frame(body)
        calibration.pack(fill="x", pady=(8, 0))
        self.calibrate_button = ttk.Button(calibration, text="Hiệu chuẩn 50 cm", command=self.calibrate, state="disabled")
        self.calibrate_button.pack(side="left")
        self.distance_label = ttk.Label(calibration, text="Khoảng cách: chưa hiệu chuẩn", font=("Segoe UI", 12, "bold"))
        self.distance_label.pack(side="left", padx=16)
        self.preview = tk.Label(body, text="Nhấn Bắt đầu để mở webcam", width=1, height=1, bg="#080e18", fg="#94a3b8", font=("Segoe UI", 16))
        self.preview.pack(fill="both", expand=True, pady=16)
        self.metrics = ttk.Label(body, text="FPS: —     Xử lý: —     Landmarks: —     Phát hiện: —", font=("Segoe UI", 13, "bold"))
        self.metrics.pack(anchor="w")
        self.status = ttk.Label(body, text="Sẵn sàng. Ngồi đủ sáng, nhìn thẳng camera; thử quay đầu và đeo kính.", wraplength=950)
        self.status.pack(anchor="w", pady=10)
        ttk.Label(body, text="Khoảng cách ước lượng đến webcam • ngưỡng +25% pixel / >2 giây • chưa đo tư thế.", wraplength=900).pack(anchor="w")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(30, self.poll)

    def start(self):
        try:
            index = int(self.index.get())
            if index < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Camera", "Chỉ số camera phải là số nguyên không âm.")
            return
        self.worker = CameraWorker(index)
        self.last_summary = None
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status.configure(text="Đang tải mô hình và mở camera…")
        self.worker.start()
        self.calibrate_button.configure(state="normal")
        self.distance_label.configure(text="Khoảng cách: chưa hiệu chuẩn")

    def calibrate(self):
        if self.worker and not self.worker.stop_event.is_set():
            messagebox.showinfo("Hiệu chuẩn", "Dùng thước đặt mặt cách webcam 50 cm. Nhìn thẳng, giữ mặt trong oval và giữ yên ít nhất 1 giây. Oval chỉ hướng dẫn vị trí, không xác nhận khoảng cách 50 cm.")
            self.worker.commands.put('calibrate')

    def stop(self):
        if self.worker:
            self.worker.stop_event.set()
            self.stop_button.configure(state="disabled")
            self.calibrate_button.configure(state="disabled")
            self.status.configure(text="Đang dừng và giải phóng webcam…")

    def poll(self):
        if self.worker:
            self.worker.show_landmarks = self.overlay.get()
            try:
                frame, fps, latency, points, ratio, elapsed, distance = self.worker.frames.get_nowait()
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(rgb)
                image.thumbnail((max(self.preview.winfo_width(), 1), max(self.preview.winfo_height(), 1)))
                self.photo = ImageTk.PhotoImage(image)
                self.preview.configure(image=self.photo, text="")
                self.metrics.configure(text=f"FPS: {fps:.1f}     Xử lý: {latency:.1f} ms     Landmarks: {points}     Phát hiện: {ratio:.0%}")
                cm = distance['distance_cm']
                self.distance_label.configure(text=f"Khoảng cách ≈ {cm:.1f} cm" if cm is not None else "Khoảng cách: chưa có phép đo hợp lệ", foreground="#fb7185" if distance['warning'] else "#e2e8f0")
                self.status.configure(text=f"{elapsed:.0f} giây • {distance['message']}", foreground="#fb7185" if distance['warning'] else "#e2e8f0")
            except queue.Empty:
                pass
            if not self.worker.is_alive():
                self.last_summary = self.worker.summary
                self.status.configure(text=self.worker.error or "Đã dừng. Có thể lưu báo cáo kiểm tra.")
                self.worker = None
                self.start_button.configure(state="normal")
                self.stop_button.configure(state="disabled")
                self.calibrate_button.configure(state="disabled")
        if self.closing and self.worker is None:
            self.destroy()
            return
        self.after(30, self.poll)

    def save(self):
        if not self.last_summary:
            messagebox.showinfo("Kết quả", "Dừng phiên kiểm tra trước khi lưu kết quả.")
            return
        folder = Path(__file__).resolve().parents[3] / "results/logs"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"webcam-{datetime.now():%Y%m%d-%H%M%S-%f}.json"
        path.write_text(json.dumps(self.last_summary, ensure_ascii=False, indent=2), encoding="utf-8")
        self.status.configure(text=f"Đã lưu: {path}")

    def close(self):
        self.closing = True
        self.stop()
