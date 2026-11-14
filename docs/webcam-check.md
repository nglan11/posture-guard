# Kết quả kiểm tra webcam

Ngày kiểm tra: 14/11/2026, camera 0, khung hình yêu cầu 640×480, CPU/XNNPACK.

Môi trường: Python 3.12.10, MediaPipe 0.10.35, OpenCV/contrib 4.14.0.94, Pillow 12.3.0. `pip check` không phát hiện phụ thuộc hỏng.

Phiên cuối sau khi đồng bộ thư viện:

| Chỉ số | Kết quả |
|---|---:|
| Thời gian xử lý thực tế | 30,14 giây |
| Tổng khung hình | 904 |
| Khung hình có landmarks mặt | 864 |
| FPS trung bình | 29,99 |
| Tỷ lệ phát hiện | 95,58% |
| p95 thời gian suy luận | 16,09 ms |
| Lỗi | Không |

Báo cáo JSON tại `results/logs/webcam-check.json` (không đưa vào Git). Không lưu hình ảnh webcam. Phiên đo dùng worker và vẽ landmarks, không đo thời gian hiển thị Tk hay độ trễ đầu-cuối. 40 khung hình không phát hiện mặt có thể do người dùng rời khung hình hoặc chuyển động/ánh sáng; chưa có nhãn tham chiếu nên không gọi 95,58% là độ chính xác.

Kết quả chứng minh tốc độ xử lý gần 30 FPS trong phiên thử này. Chưa có phép đo độ rung/sai lệch vị trí landmark hoặc đánh giá chủ quan về độ mượt khi quay đầu. Cần kiểm tra thêm trong giao diện ở các điều kiện ánh sáng và tư thế khác nhau.

Kiểm tra bổ sung: 2 unit test giải phóng tài nguyên khi lỗi đều đạt; kiểm tra cú pháp đạt; giao diện Tk khởi tạo thành công và đã kiểm tra bố cục trên màn hình laptop.
