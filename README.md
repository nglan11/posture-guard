# posture-guard

Khung thư mục dự án Đồ án chuyên ngành: Ứng dụng giám sát tư thế ngồi và cảnh báo hành vi nhìn gần bằng webcam.

**Trạng thái:** Chỉ là scaffold (cây thư mục), chưa có thuật toán hay ứng dụng chạy.

## Quyết định đã thống nhất
- Webcam RGB, OpenCV, MediaPipe Pose & Face Mesh.
- Phân tích tư thế hình học và nghiên cứu 3DMM + Similarity Transform.
- Pinhole, IPD giả định 6,3 cm, oval tham chiếu xấp xỉ 50 cm, baseline theo người dùng.
- Cảnh báo chính: khoảng cách ước lượng < 33 cm, duy trì trên 2 giây.
- Ngưỡng pixel tăng 25% trong đề cương **khác** ngưỡng 33 cm; phải giải trình khi viết báo cáo.
- Sai số ±3 cm là mục tiêu thực nghiệm, chưa xác minh.

## Cài GitHub (cần gh CLI và đăng nhập)
```bash
gh auth login
git init
git add .
git commit -m "Initialize posture-guard scaffold"
git branch -M main
gh repo create posture-guard --public --source=. --remote=origin --push
```

Mọi module .py là placeholder, chưa chứa code chức năng.
