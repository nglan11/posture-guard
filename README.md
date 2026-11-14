# Posture Guard

Sườn giao diện desktop cho ứng dụng giám sát tư thế ngồi và khoảng cách nhìn gần bằng webcam. **Phần việc của thành viên 1 là giao diện và phát hiện điểm mốc khuôn mặt.** Các thuật toán tư thế, khoảng cách, hiệu chuẩn và cảnh báo do các thành viên phụ trách module tương ứng triển khai.

## Chạy demo

Trên máy đã cài môi trường, nhấp đúp **run.cmd** hoặc chạy PowerShell:

```powershell
cd D:\posture-guard
.\.venv\Scripts\python.exe -m posture_guard.main
```

Cài trên máy khác có Python 3.12:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
.\.venv\Scripts\python.exe -m posture_guard.main
```

## Nội dung demo hiện tại

1. Nhấn **Bật camera**. Camera mặc định được chọn sẵn; nhấn **Đổi** nếu muốn chọn camera khác.
2. Đưa mặt vào khung hình để xem trạng thái phát hiện khuôn mặt và landmarks thực tế.
3. Chọn **Lưới khuôn mặt**, **Các điểm mốc** hoặc **Ảnh gốc**; bật/tắt **Xem như trong gương**.
4. Nhấn **Hiện thông số** nếu cần xem FPS, số điểm mốc, thời gian suy luận và thời gian phiên.
5. Nhấn **Dừng** để đóng webcam. **Chi tiết phiên** hiển thị số liệu xử lý của phiên hiện tại hoặc vừa kết thúc.

**Không yêu cầu người dùng có thước hoặc đo thủ công khi chạy demo.** Phần giao diện không tự đặt phương pháp hiệu chuẩn hay ngưỡng cảnh báo thay cho module của nhóm.

## Sườn giao diện cho các phần tiếp theo

| Khu vực | Trạng thái hiện tại | Điểm tích hợp |
|---|---|---|
| Webcam và landmarks | Đã chạy bằng OpenCV + MediaPipe Face Landmarker | `CameraWorker` trả `FaceFrame` với tọa độ thật |
| Tư thế | Chưa kết nối | Nhận trạng thái từ module tư thế |
| Khoảng cách | Chưa kết nối | Nhận số đo centimet hợp lệ từ module khoảng cách |
| Hiệu chuẩn | Chưa kết nối | Nhận tiến trình/kết quả từ module hiệu chuẩn |
| Cảnh báo | Chưa kết nối | Nhận thông báo từ module cảnh báo |

Các ô chưa tích hợp hiển thị **Chưa kết nối**, không hiển thị giá trị khoảng cách hoặc tư thế giả. Khi có module thật, nhóm gửi `MonitoringSnapshot` qua `MainWindow.publish_monitoring_state()`; giao diện chỉ trình bày kết quả. Khi dừng, mất luồng hình hoặc kết quả hết hạn, các số đo giám sát cũ được xóa.

Đây là bản demo **giao diện + khuôn mặt** và khung tích hợp tiếp theo, chưa phải hệ thống đã hoàn thành tất cả thuật toán. Không có các tab giả thuyết nghiên cứu trong giao diện sử dụng.

Hướng dẫn kết nối: [docs/face_module_interface.md](docs/face_module_interface.md).

## Kiểm tra và xử lý lỗi

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/check_webcam.py --seconds 30 --camera 0
```

Nếu camera không mở: đóng Zoom/Teams/Camera, bật quyền camera cho ứng dụng desktop trong Windows Settings hoặc chọn camera khác. Ứng dụng xử lý tại máy, không gửi hay ghi hình webcam. Script kiểm tra chỉ ghi thông số JSON tại `results/logs/webcam-check.json`.

FPS đo luồng lấy hình–nhận diện–vẽ. Thời gian suy luận chỉ đo Face Landmarker, không phải độ trễ toàn bộ camera–màn hình. Số khung hình phát hiện mặt không phải độ chính xác nhận diện.
