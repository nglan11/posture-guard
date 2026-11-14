"""Desktop demonstration for webcam face detection and facial landmarks."""
import queue
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
from posture_guard.ui.camera_worker import CameraWorker
from posture_guard.ui.view_state import FaceFrame, number, MonitoringSnapshot

BG, WHITE, INK, MUTED = '#f3f6fa', '#ffffff', '#183044', '#647789'
TEAL, SOFT, LINE, RED = '#087f75', '#e7f6f1', '#dce5ec', '#bd3f52'
MODES = {'Lưới khuôn mặt': 'mesh', 'Các điểm mốc': 'points', 'Ảnh gốc': 'none'}


class CameraPreview(tk.Canvas):
    """Fit video without cropping; idle illustration is explicitly not a face result."""
    def __init__(self, parent):
        super().__init__(parent, bg='#101f2b', highlightthickness=0, height=1, width=1)
        self.source = None
        self.photo = None
        self.title = 'Camera chưa bật'
        self.bind('<Configure>', lambda event: self.redraw())

    def idle(self, title):
        self.source = self.photo = None
        self.title = title
        self.redraw()

    def show_frame(self, frame):
        self.source = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        self.redraw()

    def redraw(self):
        width, height = self.winfo_width(), self.winfo_height()
        if width < 2 or height < 2:
            return
        self.delete('all')
        if self.source is not None:
            image = self.source.copy()
            image.thumbnail((width, height), Image.Resampling.BILINEAR)
            self.photo = ImageTk.PhotoImage(image)
            self.create_image(width/2, height/2, image=self.photo)
            return
        if height < 180:
            self.create_text(width/2, height*.3, text=self.title, fill='#eef7fa',
                             font=('Segoe UI', 12, 'bold'), width=max(100, width-40))
            return
        x, y = width/2, max(45, height/2-58)
        self.create_oval(x-47, y-47, x+47, y+47, fill='#193340', outline='')
        self.create_rectangle(x-24, y-15, x+17, y+16, outline='#75d6c1', width=2)
        self.create_polygon(x+18, y-8, x+31, y-15, x+31, y+16, x+18, y+8, fill='', outline='#75d6c1', width=2)
        self.create_oval(x-12, y-7, x+3, y+8, outline='#75d6c1', width=2)
        self.create_text(x, y+72, text=self.title, fill='#eef7fa', font=('Segoe UI', 18, 'bold'), width=max(100, width-40))


class MainWindow(tk.Tk):
    def __init__(self):
        if sys.platform == 'win32':
            import ctypes
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except (OSError, AttributeError):
                pass
        super().__init__()
        self.title('Posture Guard · Giám sát với webcam')
        width, height = min(1240, self.winfo_screenwidth()-60), min(850, self.winfo_screenheight()-90)
        self.geometry(f'{width}x{height}')
        self.minsize(min(940, width), min(660, height))
        self.configure(bg=BG)
        self.worker = None
        self.last_state = None
        self.last_summary = None
        self.last_frame_at = None
        self.stale = False
        self.closing = False
        self.values = {}
        self.details_visible = False
        self.monitoring_queue = queue.Queue(maxsize=1)
        self.monitoring_snapshot = MonitoringSnapshot()
        self.monitoring_labels = {}
        self._styles()
        self._build()
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.poll_id = self.after(25, self.poll)

    def _styles(self):
        s = ttk.Style(self)
        s.theme_use('clam')
        s.configure('TFrame', background=BG)
        s.configure('White.TFrame', background=WHITE)
        s.configure('TLabel', background=BG, foreground=INK, font=('Segoe UI', 10))
        s.configure('White.TLabel', background=WHITE)
        s.configure('Muted.TLabel', background=WHITE, foreground=MUTED)
        s.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=(14, 10), background='#e9eff3', foreground=INK, borderwidth=0)
        s.map('TButton', background=[('active', '#dce8ed')], foreground=[('disabled', '#9baab5')])
        s.configure('Start.TButton', background=TEAL, foreground=WHITE)
        s.map('Start.TButton', background=[('active', '#076b63'), ('disabled', '#dce7e4')], foreground=[('disabled', '#90a49c')])
        s.configure('Stop.TButton', foreground=RED)
        s.configure('TCheckbutton', background=WHITE, foreground=INK, font=('Segoe UI', 10))
        s.map('TCheckbutton', background=[('active', WHITE)])
        s.configure('TCombobox', fieldbackground=WHITE, foreground=INK, padding=7)
        s.map('TCombobox', fieldbackground=[('readonly', WHITE)], selectbackground=[('readonly', WHITE)], selectforeground=[('readonly', INK)])
        s.configure('TSpinbox', fieldbackground=WHITE, foreground=INK, padding=6)

    def _value(self, key, default='—'):
        self.values[key] = tk.StringVar(value=default)
        return self.values[key]

    def _card(self, parent, padding=18):
        card = tk.Frame(parent, bg=WHITE, highlightbackground=LINE, highlightthickness=1, padx=padding, pady=padding)
        return card

    def _build(self):
        outer = ttk.Frame(self, padding=22)
        outer.pack(fill='both', expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)
        header = ttk.Frame(outer)
        header.grid(row=0, column=0, sticky='ew', pady=(0, 18))
        brand = tk.Canvas(header, width=44, height=44, highlightthickness=0, bg=BG)
        brand.pack(side='left', padx=(0, 12))
        brand.create_oval(1, 1, 43, 43, fill=TEAL, outline='')
        brand.create_text(22, 22, text='PG', fill=WHITE, font=('Segoe UI', 12, 'bold'))
        heading = ttk.Frame(header)
        heading.pack(side='left')
        ttk.Label(heading, text='Posture Guard', font=('Segoe UI', 21, 'bold')).pack(anchor='w')
        workspace = ttk.Frame(outer)
        workspace.grid(row=1, column=0, sticky='nsew')
        workspace.columnconfigure(0, weight=1)
        workspace.columnconfigure(1, minsize=310)
        workspace.rowconfigure(0, weight=1)
        video = self._card(workspace, padding=0)
        video.grid(row=0, column=0, sticky='nsew', padx=(0, 16))
        video.columnconfigure(0, weight=1)
        video.rowconfigure(1, weight=1)
        video_header = tk.Frame(video, bg=WHITE, padx=16, pady=12)
        video_header.grid(row=0, column=0, sticky='ew')
        ttk.Label(video_header, text='Camera trực tiếp', style='White.TLabel', font=('Segoe UI', 11, 'bold')).pack(side='left')
        self.connection = tk.Label(video_header, text='●  Chưa kết nối', bg=WHITE, fg=MUTED, font=('Segoe UI', 9))
        self.connection.pack(side='right')
        self.preview = CameraPreview(video)
        self.preview.grid(row=1, column=0, sticky='nsew', padx=1)
        self.preview_start = ttk.Button(self.preview, text='Bật camera', style='Start.TButton', command=self.start)
        self.preview_start.place(relx=.5, rely=.84, anchor='center')
        video_bottom = tk.Frame(video, bg=WHITE, padx=16, pady=10)
        video_bottom.grid(row=2, column=0, sticky='ew')
        ttk.Label(video_bottom, textvariable=self._value('resolution', 'Webcam laptop'), style='Muted.TLabel').pack(side='left')
        ttk.Label(video_bottom, textvariable=self._value('mode', 'Lưới khuôn mặt'), style='Muted.TLabel').pack(side='right')
        sidebar = ttk.Frame(workspace, width=310)
        sidebar.grid(row=0, column=1, sticky='nsew')
        sidebar.pack_propagate(False)
        self._recognition_card(sidebar)
        actions = ttk.Frame(sidebar)
        actions.pack(side='bottom', fill='x', pady=(12, 0))
        self.start_button = ttk.Button(actions, text='Bật camera', style='Start.TButton', command=self.start)
        self.start_button.pack(side='left', fill='x', expand=True, padx=(0, 8))
        self.stop_button = ttk.Button(actions, text='Dừng', style='Stop.TButton', command=self.stop, state='disabled')
        self.stop_button.pack(side='right', fill='x', expand=True)
        canvas = tk.Canvas(sidebar, bg=BG, highlightthickness=0, width=306)
        scrollbar = ttk.Scrollbar(sidebar, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        content = ttk.Frame(canvas)
        window = canvas.create_window((0, 0), window=content, anchor='nw')
        content.bind('<Configure>', lambda event: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda event: canvas.itemconfigure(window, width=event.width))
        self._controls(content)
        tag = 'SidebarWheel'
        self.bind_class(tag, '<MouseWheel>', lambda event: canvas.yview_scroll(-int(event.delta/120), 'units'))
        def register(widget):
            widget.bindtags((widget.bindtags()[0], tag, *widget.bindtags()[1:]))
            for child in widget.winfo_children():
                register(child)
        register(content)
        self._monitoring_panel(outer)
        self._metrics(outer)
        footer = ttk.Frame(outer)
        footer.grid(row=4, column=0, sticky='ew', pady=(10, 0))
        self.status = ttk.Label(footer, text='Sẵn sàng', foreground=MUTED, wraplength=1100)
        self.status.pack(side='left', fill='x', expand=True)
        self.info_button = ttk.Button(footer, text='Chi tiết phiên', command=self.show_session, state='disabled')
        self.info_button.pack(side='right', padx=(12, 0))
        self.details_button = ttk.Button(footer, text='Hiện thông số', command=self.toggle_details)
        self.details_button.pack(side='right')
        self.bind('<Configure>', self._resize)

    def _controls(self, parent):
        controls = self._card(parent)
        controls.pack(fill='x', pady=(0, 12))
        ttk.Label(controls, text='Tùy chỉnh cách xem', style='White.TLabel', font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        camera_row = tk.Frame(controls, bg=WHITE)
        camera_row.pack(fill='x', pady=(14, 0))
        self.camera_name = ttk.Label(camera_row, text='Camera mặc định', style='Muted.TLabel')
        self.camera_name.pack(side='left')
        self.change_camera_button = ttk.Button(camera_row, text='Đổi', command=self.toggle_camera_choice)
        self.change_camera_button.pack(side='right')
        self.camera_choice = tk.Frame(controls, bg=WHITE)
        ttk.Label(self.camera_choice, text='Chỉ số camera khác', style='Muted.TLabel').pack(anchor='w', pady=(10, 6))
        self.index = tk.StringVar(value='0')
        self.camera_input = ttk.Spinbox(self.camera_choice, from_=0, to=9, textvariable=self.index, width=4)
        self.camera_input.pack(fill='x')
        self.camera_anchor = ttk.Label(controls, text='Hiển thị trên khuôn mặt', style='Muted.TLabel')
        self.camera_anchor.pack(anchor='w', pady=(14, 6))
        self.mode = tk.StringVar(value='Lưới khuôn mặt')
        self.mode_input = ttk.Combobox(controls, values=list(MODES), textvariable=self.mode, state='readonly')
        self.mode_input.pack(fill='x')
        self.mode_input.bind('<<ComboboxSelected>>', lambda event: self.update_options())
        self.mirror = tk.BooleanVar(value=True)
        ttk.Checkbutton(controls, text='Xem như trong gương', variable=self.mirror, command=self.update_options).pack(anchor='w', pady=(14, 8))

    def _recognition_card(self, parent):
        card = self._card(parent)
        card.pack(fill='x', pady=(0, 12))
        ttk.Label(card, text='Nhận diện khuôn mặt', style='White.TLabel', font=('Segoe UI', 11, 'bold')).pack(anchor='w')
        self.face_status = tk.Label(card, text='●  Chưa bắt đầu', bg=SOFT, fg=TEAL, font=('Segoe UI', 11, 'bold'), padx=10, pady=10, anchor='w')
        self.face_status.pack(fill='x', pady=(12, 10))

    def _metrics(self, parent):
        metrics = self.metrics = ttk.Frame(parent)
        metrics.grid(row=3, column=0, sticky='ew', pady=(12, 0))
        for col, (key, title) in enumerate([('fps', 'Khung hình / giây'), ('landmarks', 'Điểm mốc khuôn mặt'), ('inference', 'Xử lý nhận diện'), ('elapsed', 'Thời gian phiên')]):
            metrics.columnconfigure(col, weight=1, uniform='metric')
            card = self._card(metrics, padding=13)
            card.grid(row=0, column=col, sticky='ew', padx=(0 if col == 0 else 10, 0))
            ttk.Label(card, text=title, style='Muted.TLabel', font=('Segoe UI', 9)).pack(anchor='w')
            ttk.Label(card, textvariable=self._value(key), style='White.TLabel', font=('Segoe UI', 18, 'bold')).pack(anchor='w', pady=(4, 0))
        metrics.grid_remove()

    def _monitoring_panel(self, parent):
        panel = ttk.Frame(parent)
        panel.grid(row=2, column=0, sticky='ew', pady=(14, 0))
        ttk.Label(panel, text='Trạng thái giám sát', font=('Segoe UI', 11, 'bold')).grid(row=0, column=0, columnspan=4, sticky='w', pady=(0, 8))
        titles = [('posture', 'Tư thế'), ('distance', 'Khoảng cách'),
                  ('calibration', 'Hiệu chuẩn'), ('alert', 'Cảnh báo')]
        for column, (key, title) in enumerate(titles):
            panel.columnconfigure(column, weight=1, uniform='module')
            card = self._card(panel, padding=11)
            card.grid(row=1, column=column, sticky='nsew', padx=(0 if column == 0 else 10, 0))
            ttk.Label(card, text=title, style='Muted.TLabel', font=('Segoe UI', 9)).pack(anchor='w')
            label = tk.Label(card, text='Chưa kết nối', bg=WHITE, fg=MUTED, anchor='w',
                             font=('Segoe UI', 11, 'bold'), wraplength=200, justify='left')
            label.pack(anchor='w', fill='x', pady=(5, 0))
            label.bind('<Configure>', lambda event, label=label: label.configure(wraplength=max(80, event.width)))
            self.monitoring_labels[key] = label

    def set_monitoring_state(self, snapshot):
        """Main-thread presentation hook; no calculations or alert rules here."""
        if not isinstance(snapshot, MonitoringSnapshot):
            raise TypeError('Expected MonitoringSnapshot')
        self.monitoring_snapshot = snapshot
        default = {'disconnected': 'Chưa kết nối', 'waiting': 'Đang chờ dữ liệu',
                   'ready': 'Đã sẵn sàng', 'warning': 'Cần chú ý', 'error': 'Tạm không khả dụng'}
        colors = {'disconnected': MUTED, 'waiting': MUTED, 'ready': TEAL,
                  'warning': '#9c681a', 'error': RED}
        for key, label in self.monitoring_labels.items():
            result = getattr(snapshot, key)
            text = result.text or default[result.state]
            if key == 'distance' and result.state in ('ready', 'warning'):
                # Only format an actual measurement explicitly provided by the owner.
                text = number(result.centimeters, ' cm') if result.centimeters is not None else (result.text or 'Chưa có số đo')
            label.configure(text=text, fg=colors[result.state])

    def publish_monitoring_state(self, snapshot):
        """Thread-safe latest-result inbox for later system integration."""
        if not isinstance(snapshot, MonitoringSnapshot):
            raise TypeError('Expected MonitoringSnapshot')
        try:
            self.monitoring_queue.put_nowait(snapshot)
        except queue.Full:
            try:
                self.monitoring_queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self.monitoring_queue.put_nowait(snapshot)
            except queue.Full:
                pass

    def toggle_details(self):
        self.details_visible = not self.details_visible
        if self.details_visible:
            self.metrics.grid()
        else:
            self.metrics.grid_remove()
        self.details_button.configure(text='Ẩn thông số' if self.details_visible else 'Hiện thông số')

    def toggle_camera_choice(self):
        if self.camera_choice.winfo_manager():
            self.camera_choice.pack_forget()
        else:
            self.camera_choice.pack(fill='x', before=self.camera_anchor)
            self.camera_input.focus_set()

    def _resize(self, event):
        if event.widget is self and hasattr(self, 'status'):
            self.status.configure(wraplength=max(400, event.width-230))

    def update_options(self):
        self.values['mode'].set(self.mode.get())
        if self.worker:
            self.worker.overlay_mode = MODES[self.mode.get()]
            self.worker.mirror = self.mirror.get()

    def _clear_metrics(self):
        for key in ('fps', 'landmarks', 'inference', 'elapsed'):
            self.values[key].set('—')
        self.last_state = None
        self.set_monitoring_state(MonitoringSnapshot())
        try:
            self.monitoring_queue.get_nowait()
        except queue.Empty:
            pass

    def start(self):
        if self.worker is not None:
            return
        try:
            index = int(self.index.get())
            if index < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror('Chọn camera', 'Nhập chỉ số camera là số nguyên từ 0 trở lên.')
            return
        self._clear_metrics()
        self.last_summary = self.last_frame_at = None
        self.stale = False
        self.worker = CameraWorker(index)
        self.update_options()
        self.start_button.configure(state='disabled', text='Bật camera')
        self.camera_name.configure(text='Camera mặc định' if index == 0 else f'Camera {index}')
        self.preview_start.place_forget()
        self.change_camera_button.configure(state='disabled')
        self.camera_input.configure(state='disabled')
        self.stop_button.configure(state='normal')
        self.info_button.configure(state='disabled')
        self.preview.idle('Đang mở camera…')
        self.face_status.configure(text='●  Đang kết nối', fg=MUTED, bg=BG)
        self.connection.configure(text='●  Đang kết nối', fg=MUTED)
        self.status.configure(text='Đang mở webcam…', foreground=MUTED)
        self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop_event.set()
            self.stop_button.configure(state='disabled')
            self.connection.configure(text='●  Đang dừng', fg=MUTED)
            self.status.configure(text='Đang đóng camera…', foreground=MUTED)

    def _render(self, state):
        if not isinstance(state, FaceFrame):
            raise ValueError('Gói dữ liệu webcam không đúng định dạng FaceFrame.')
        self.last_state = state
        self.last_frame_at = time.perf_counter()
        self.stale = False
        self.preview.show_frame(state.frame)
        for key, value in [('fps', number(state.fps)), ('landmarks', str(len(state.landmarks))), ('inference', number(state.inference_ms, ' ms')), ('elapsed', self._clock(state.elapsed_seconds))]:
            self.values[key].set(value)
        self.values['resolution'].set(f'Camera {self.index.get()} · {state.width} × {state.height}')
        self.connection.configure(text='●  Trực tiếp', fg=TEAL)
        if state.face_present:
            self.face_status.configure(text='●  Đã tìm thấy mặt', fg=TEAL, bg=SOFT)
            self.status.configure(text='Đang theo dõi khuôn mặt.', foreground=TEAL)
        else:
            self.face_status.configure(text='●  Đang tìm khuôn mặt', fg='#9c681a', bg='#fff5df')
            self.status.configure(text='Chưa thấy khuôn mặt', foreground=MUTED)
        self.info_button.configure(state='normal')

    @staticmethod
    def _clock(seconds):
        seconds = max(0, int(seconds))
        return f'{seconds//60:02}:{seconds%60:02}'

    def poll(self):
        if self.worker:
            try:
                frame = self.worker.frames.get_nowait()
                # Old queued images must never appear as a live camera feed.
                if time.perf_counter()-frame.published_at <= 2:
                    self._render(frame)
            except queue.Empty:
                pass
            except (ValueError, TypeError, AttributeError, cv2.error):
                self.status.configure(text='Không hiển thị được hình ảnh', foreground=RED)
            if not self.worker.is_alive():
                self.last_summary = self.worker.summary
                error = self.worker.error
                self.worker = None
                self._clear_metrics()
                self.preview.idle('Chưa mở được camera' if error else 'Camera đã dừng')
                self.connection.configure(text='●  Lỗi kết nối' if error else '●  Đã dừng', fg=RED if error else MUTED)
                self.face_status.configure(text='●  Chưa có hình ảnh' if error else '●  Đã dừng nhận diện', fg=MUTED, bg=BG)
                self.start_button.configure(state='normal')
                self.start_button.configure(text='Thử lại' if error else 'Bật camera')
                self.preview_start.configure(text='Thử lại' if error else 'Bật lại camera')
                self.preview_start.place(relx=.5, rely=.84, anchor='center')
                self.change_camera_button.configure(state='normal')
                self.camera_input.configure(state='normal')
                self.stop_button.configure(state='disabled')
                self.info_button.configure(state='normal' if self.last_summary else 'disabled')
                self.status.configure(text='Không kết nối được camera' if error else 'Camera đã tắt', foreground=RED if error else MUTED)
            elif self.last_frame_at and time.perf_counter()-self.last_frame_at > 2 and not self.stale:
                self._clear_metrics()
                self.stale = True
                self.preview.idle('Đang chờ hình ảnh…')
                self.face_status.configure(text='●  Tạm ngừng nhận diện', fg=MUTED, bg=BG)
                self.connection.configure(text='●  Đang chờ camera', fg=MUTED)
                self.status.configure(text='Đang chờ webcam trả hình ảnh mới.', foreground=MUTED)
            if self.worker and self.last_state and not self.stale:
                try:
                    snapshot = self.monitoring_queue.get_nowait()
                    if time.perf_counter()-snapshot.updated_at <= 5:
                        self.set_monitoring_state(snapshot)
                except queue.Empty:
                    pass
                # Do not keep a former warning/measurement on screen indefinitely.
                if time.perf_counter()-self.monitoring_snapshot.updated_at > 5:
                    self.set_monitoring_state(MonitoringSnapshot())
        if self.closing and self.worker is None:
            self.destroy()
            return
        self.poll_id = self.after(25, self.poll)

    def show_session(self):
        if self.last_summary:
            s = self.last_summary
            rows = [('Khung hình đã xử lý', str(s.get('frames', '—'))),
                    ('Khung hình có mặt', str(s.get('detected_frames', '—'))),
                    ('FPS trung bình', number(s.get('average_fps'))),
                    ('Xử lý nhận diện trung bình', number(s.get('inference_mean_ms'), ' ms')),
                    ('Thời gian phiên', number(s.get('elapsed_seconds'), ' s'))]
        elif self.last_state:
            s = self.last_state
            rows = [('Trạng thái', 'Phiên đang chạy'), ('FPS hiện tại', number(s.fps)),
                    ('Điểm mốc trên khung hình', str(len(s.landmarks))),
                    ('Xử lý nhận diện', number(s.inference_ms, ' ms')),
                    ('Thời gian phiên', self._clock(s.elapsed_seconds))]
        else:
            return
        dialog = tk.Toplevel(self)
        dialog.title('Thông tin phiên nhận diện')
        dialog.configure(bg=WHITE)
        dialog.transient(self)
        dialog.resizable(False, False)
        content = tk.Frame(dialog, bg=WHITE, padx=24, pady=22)
        content.pack(fill='both', expand=True)
        tk.Label(content, text='Phiên nhận diện khuôn mặt', bg=WHITE, fg=INK, font=('Segoe UI', 14, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 16))
        for row, (title, value) in enumerate(rows, 1):
            tk.Label(content, text=title, bg=WHITE, fg=MUTED, font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=7, padx=(0, 35))
            tk.Label(content, text=value, bg=WHITE, fg=INK, font=('Segoe UI', 10, 'bold')).grid(row=row, column=1, sticky='e', pady=7)
        ttk.Button(content, text='Đóng', command=dialog.destroy).grid(row=len(rows)+1, column=0, columnspan=2, sticky='e', pady=(18, 0))
        dialog.bind('<Escape>', lambda event: dialog.destroy())

    def close(self):
        self.closing = True
        self.stop()

    def destroy(self):
        if getattr(self, 'poll_id', None):
            self.after_cancel(self.poll_id)
            self.poll_id = None
        super().destroy()
