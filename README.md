# Posture Guard

Ứng dụng desktop kiểm tra landmarks khuôn mặt từ webcam bằng OpenCV và MediaPipe Tasks. Giao diện tiếng Việt dùng Tkinter; xử lý camera ở luồng riêng, chỉ giữ khung hình mới nhất để tránh tích tụ độ trễ.

## Cài đặt (Windows, Python 3.12)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
./.venv/Scripts/python.exe -m posture_guard.main
```

Nếu máy chưa có Python, cài Python 3.12 với pip và Tcl/Tk. Script cũng hỗ trợ Python riêng tại `.python/python.exe`. Model chính thức của Google được tải vào `data/models/face_landmarker.task`; sau cài đặt ứng dụng xử lý tại máy, không gửi hay lưu hình webcam.

## Kiểm tra webcam

Chọn camera 0, nhấn **Bắt đầu**. Thử nhìn thẳng, quay/nghiêng đầu, đeo kính và thay đổi ánh sáng. Theo dõi FPS, thời gian suy luận, số landmarks và tỷ lệ khung hình có mặt. Nhấn **Dừng**, sau đó **Lưu kết quả** để ghi JSON tại `results/logs/`.

Chạy kiểm tra 30 giây không có cửa sổ xem trước:

```powershell
./.venv/Scripts/python.exe scripts/check_webcam.py --seconds 30 --camera 0
./.venv/Scripts/python.exe -m unittest discover -s tests -p test_webcam_runtime.py -v
```

Trong phiên đo, ngồi trước camera. FPS trung bình và p95 thời gian suy luận giúp đánh giá hiệu năng; tỷ lệ phát hiện phụ thuộc việc có mặt trong khung hình. Mục tiêu tham khảo: khoảng 25–30 FPS, p95 suy luận dưới 40 ms trong điều kiện đủ sáng. Đây không phải kết quả thực nghiệm hay bảo đảm cho mọi laptop. Kiểm tra thêm bằng mắt để đánh giá rung/mất điểm khi chuyển động. Thời gian suy luận không bao gồm toàn bộ độ trễ camera–màn hình.

Nếu không mở được webcam: đóng Teams/Zoom/Camera, bật quyền camera cho ứng dụng desktop trong Windows Settings, thử chỉ số camera khác.

## Hiệu chuẩn và cảnh báo khoảng cách

1. Mở webcam, dùng thước đặt mặt cách **webcam 50 cm**.
2. Nhấn **Hiệu chuẩn 50 cm**, nhìn thẳng và giữ mặt trong oval. Giữ yên cho đến khi nhận đủ 30 mẫu trong ít nhất 1 giây; mẫu dao động quá 4% sẽ được lấy lại.
3. Khoảng cách được ước lượng bằng `50 × baseline_pixel / pixel_hiện_tại`, có làm mượt. Khi khoảng cách pixel hai tâm mống mắt tăng hơn 25% liên tục hơn 2 giây, giao diện hiển thị cảnh báo đỏ.

Oval hướng dẫn vị trí, không tự xác định mốc 50 cm. Hiệu chuẩn chỉ có hiệu lực trong phiên camera; cần làm lại khi khởi động, đổi người, webcam, độ phân giải hoặc vị trí camera. Không nhìn thẳng, mất mặt hoặc nằm ngoài oval sẽ không có số đo hợp lệ và sẽ xóa bộ đếm cảnh báo. Bộ lọc 2D chỉ hạn chế góc mặt không phù hợp, không thay thế ước lượng tư thế đầu 3D.

Ngưỡng +25% tương ứng khoảng 40 cm với baseline 50 cm theo mô hình lý tưởng; **khác ngưỡng 33 cm** ở phần đánh giá trong đề cương. Phiên bản này dùng quy tắc +25% / hơn 2 giây. Khoảng cách tính đến webcam, không mặc định là mặt phẳng màn hình. Chưa xác minh sai số bằng thước thực nghiệm.

Kiểm tra tất cả logic đã triển khai:

```powershell
./.venv/Scripts/python.exe -m unittest discover -s tests -v
```

## Phạm vi

Phiên bản này định vị các điểm mốc khuôn mặt, hiệu chuẩn khoảng cách theo phiên và cảnh báo nhìn gần; chưa nhận dạng danh tính. Các module tư thế, hồ sơ hiệu chuẩn lâu dài, lịch sử và các phần nghiên cứu 3DMM vẫn là scaffold; chưa có kết luận độ chính xác ±3 cm.

API tham khảo: https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker/python
