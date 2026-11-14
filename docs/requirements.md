# Đối chiếu đề cương và phạm vi triển khai

Đã đọc đề cương PDF 17 trang tại thư mục gốc.

- Trang 6–7: webcam RGB, một người trong nhà; OpenCV, MediaPipe Pose và Face Mesh; có giao diện hiển thị trạng thái.
- Trang 10: baseline 50 cm, IPD giả định 6,3 cm, ngưỡng tăng khoảng cách pixel 25% trong hơn 2 giây.
- Trang 12: một ngưỡng đánh giá khác là 33 cm; đánh giá hiệu năng bằng FPS, thời gian xử lý, CPU/RAM.
- Trang 14: giai đoạn đầu cài môi trường, thử OpenCV/MediaPipe, xây dựng giao diện cơ bản.

Đã triển khai: giao diện webcam, MediaPipe Face Landmarker (Tasks API), vẽ landmarks, thống kê FPS/thời gian suy luận/tỷ lệ phát hiện, lưu báo cáo JSON. Bước tiếp theo đã bổ sung hiệu chuẩn theo phiên tại 50 cm, hướng dẫn oval, khoảng cách pinhole từ hai tâm mống mắt và cảnh báo +25% pixel duy trì hơn 2 giây. Chưa triển khai Pose hay nhận dạng danh tính. Chưa đo CPU/RAM, rung landmarks hoặc độ trễ đầu-cuối.

Ngưỡng 25% pixel tương ứng khoảng 40 cm nếu baseline 50 cm theo pinhole lý tưởng, khác 33 cm. Chọn quy tắc trang 10 (+25% / >2 giây) làm mặc định cho phiên bản này; chưa dùng 33 cm. Không xem các mục tiêu độ chính xác trong đề cương là kết quả đo.

Kiểm tra bước khoảng cách: 8 unit test đạt (hình học pixel, pinhole, ổn định hiệu chuẩn, thời gian cảnh báo, mất mặt, khoảng ngắt khung hình và giải phóng webcam khi lỗi). Giao diện khởi tạo thành công; kiểm tra webcam xác nhận luồng mới trả đủ dữ liệu và không đo khi chưa hiệu chuẩn. Phiên kiểm tra ngắn này không có landmarks trong khung hình đầu tiên, nên chưa xác minh hiệu chuẩn/khoảng cách thực tế. Cần người dùng đo mốc 50 cm bằng thước và đối chiếu tại 30/40/50/60 cm; chưa công bố sai số.
