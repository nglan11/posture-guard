# Phạm vi bản demo

Thành viên 1 phụ trách giao diện desktop và nhận diện điểm mốc khuôn mặt bằng webcam RGB, OpenCV và MediaPipe Face Landmarker. Các thuật toán còn lại được nối vào giao diện khi thành viên phụ trách hoàn thành.

Giao diện là sườn cho ứng dụng chung: camera trực tiếp, trạng thái khuôn mặt, tùy chọn lớp hiển thị, các vùng tư thế/khoảng cách/hiệu chuẩn/cảnh báo và thông số phiên tùy chọn. Chỉ phần khuôn mặt có dữ liệu xử lý sẵn. Các vùng module khác hiện Chưa kết nối và có giao tiếp để nhận dữ liệu thật, không giả lập kết quả thuật toán.

Theo quyết định của nhóm tại `docs/decisions.md`, luồng sử dụng không yêu cầu người dùng có thước. Bản demo không cài đặt hay tự diễn giải phương pháp hiệu chuẩn, ngưỡng khoảng cách hoặc kỹ thuật phân tích tư thế thay cho thành viên phụ trách.

Không chỉnh sửa tài liệu PDF, không đưa nội dung đánh giá giả thuyết lên giao diện sử dụng. Đây là triển khai chương trình và điểm nối module, không phải nhiệm vụ viết báo cáo.
