# Kiểm tra webcam cho bản minh họa khuôn mặt

Phiên kiểm tra ngày 14/11/2026, camera 0, chỉ chạy Face Landmarker và vẽ lưới khuôn mặt. Không chạy module tư thế, khoảng cách hoặc hiệu chuẩn.

Thông số thực tế từ `scripts/check_webcam.py --seconds 20 --camera 0`:

| Chỉ số | Giá trị |
|---|---:|
| Thời gian xử lý | 20,16 giây |
| Khung hình | 308 |
| Khung hình phát hiện mặt | 300 |
| FPS trung bình | 15,28 |
| Suy luận trung bình | 13,21 ms |
| Suy luận p95 | 16,46 ms |
| Lỗi | Không |

Đây là số đo của riêng phiên webcam này, không phải mức FPS bảo đảm hay độ chính xác landmark. FPS gồm luồng lấy hình và vẽ; thời gian suy luận chỉ đo Face Landmarker. Tỷ lệ khung hình có mặt không phải accuracy. Không lưu ảnh hoặc video webcam.

Kiểm thử tự động dùng dữ liệu tổng hợp chỉ để xác minh chuyển trạng thái, lớp hiển thị, xuất đúng tọa độ và giải phóng tài nguyên; các dữ liệu đó không dùng trong chương trình minh họa hoặc kết quả webcam trên.
