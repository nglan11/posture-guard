# Giao tiếp module khuôn mặt

Luồng thực thi: `main.py` → `MainWindow` → `CameraWorker` → OpenCV + `FaceDetector`.

`CameraWorker.frames` là queue giữ tối đa một `FaceFrame` mới nhất. Giao diện đọc queue bằng Tk `after`, không chạy suy luận trên main loop.

`FaceFrame` tại `ui/view_state.py` chứa:

- `frame`: ndarray BGR H×W×3, đã lật gương theo tùy chọn và vẽ lớp hiển thị đã chọn.
- `landmarks`: tuple `(x, y, z)` cho mỗi điểm do MediaPipe trả về; tuple rỗng nếu không tìm thấy mặt. Không chèn điểm giả.
- `fps`: FPS làm mượt của luồng camera, nhận diện và vẽ.
- `inference_ms`: thời gian lời gọi Face Landmarker của khung hình.
- `elapsed_seconds`: thời gian xử lý kể từ khi mở được camera.
- `width`, `height`: kích thước khung hình thực tế.
- `published_at`: mốc `time.perf_counter()` để loại khung hình quá cũ.

Tọa độ landmarks thuộc ảnh đầu vào nhận diện, tức **ảnh đã lật khi bật Lật gương**. x/y được chuẩn hóa theo chiều rộng/chiều cao; z là độ sâu tương đối của MediaPipe, không phải centimet. Không coi ảnh trên giao diện đã co giãn là hệ tọa độ đầu vào thuật toán khác.

Tùy chọn worker: `overlay_mode` là `mesh`, `points` hoặc `none`; `mirror` là bool. Dừng bằng `stop_event.set()`. `summary` chỉ chứa thông số phiên nhận diện khuôn mặt, không chứa khoảng cách hoặc kết quả tư thế.

Phần tích hợp của nhóm có thể lấy tọa độ thật tại đây. Những phương pháp tư thế/khoảng cách/hiệu chuẩn khác cần module và dữ liệu đầu vào do thành viên phụ trách định nghĩa; giao diện minh họa hiện tại không áp đặt chúng.

## Trạng thái giám sát của ứng dụng chung

Giao diện có bốn vùng chờ kết quả: tư thế, khoảng cách, hiệu chuẩn, cảnh báo. Các vùng này mặc định Chưa kết nối. Không có thuật toán tương ứng chạy ngầm trong demo khuôn mặt.

Các kiểu dữ liệu tại `ui/view_state.py`:

- `ModuleStatus(state, text)`: trạng thái và nội dung do module phụ trách trả về. Các state hợp lệ: `disconnected`, `waiting`, `ready`, `warning`, `error`.
- `DistanceStatus(state, text, centimeters)`: chỉ nhận số đo dương, hữu hạn hoặc None. Giao diện chỉ định dạng sang cm; không tính khoảng cách.
- `MonitoringSnapshot(posture, distance, calibration, alert, updated_at)`: một ảnh chụp trạng thái tổng hợp. Các mục không cung cấp mặc định Chưa kết nối. `updated_at` dùng `time.perf_counter()` trong cùng tiến trình.

Module tích hợp gọi `MainWindow.publish_monitoring_state(snapshot)` từ luồng xử lý. Queue chỉ giữ bản mới nhất; main loop Tk cập nhật các vùng hiển thị. Nếu gọi trực tiếp từ main thread có thể dùng `set_monitoring_state(snapshot)`.

Giao diện chỉ lấy kết quả từ inbox khi đang có phiên camera với khung hình mới. Kết quả quá 5 giây bị loại/xóa để tránh giữ số đo cũ; module tổng hợp phải gửi lại snapshot hiện tại trong khoảng này. Dừng camera hoặc mất luồng hình sẽ xóa các trạng thái giám sát và dữ liệu đang chờ.

Để nối hệ thống, thành viên phụ trách pipeline cần tạo `MonitoringSnapshot` từ kết quả thật và gọi hàm publish trên. Việc thêm giao tiếp này không đồng nghĩa các module thuật toán đã được hiện thực.
