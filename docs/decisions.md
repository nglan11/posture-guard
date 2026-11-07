# Nhật ký quyết định

- Theo đề cương: OpenCV, MediaPipe, Pinhole, khoảng cách đồng tử 6,3 cm, oval tham chiếu 50 cm, 3DMM + Similarity Transform, datasets MultiPosture/BIWI/Face2Cam.
- Quyết định của nhóm: cảnh báo chính tại khoảng cách ước lượng dưới 33 cm sau 2 giây; không yêu cầu người dùng có thước khi sử dụng thông thường.
- **Cần trình bày khác biệt với đề cương:** trong mục 5.2 có quy tắc tăng kích thước mắt trên ảnh 25% so với baseline. Nếu baseline đúng 50 cm, quy tắc này tương đương 40 cm, không phải 33 cm.
- Oval chỉ quy ước mốc khoảng 50 cm; phải kiểm chứng sai số theo người dùng và camera.
- Sai số ±3 cm: mục tiêu kiểm thử, không phải độ chính xác được bảo đảm.
