# Gợi ý báo cáo và video Bài cá nhân 2

Tác giả: Nguyễn Quốc Chuyên · MSSV: 2324802010174. Đề tài dự kiến đăng ký với giảng viên: **Ứng dụng web quản lý ghi chú cá nhân trên VPS**. Chỉ điền kết quả và chèn ảnh sau khi đã chạy thật.

## Báo cáo PDF (7 trang)

1. **Bìa:** tên bài, họ tên, MSSV, đề tài đã đăng ký, link GitHub.
2. **Kiến trúc và môi trường:** sơ đồ Laptop → VMnet4 NAT → Nginx :80 → Gunicorn 127.0.0.1:8000 → PostgreSQL 127.0.0.1:5432. VPS Ubuntu 24.04, IP 192.168.174.20. Ảnh ESXi và VPS có MSSV.
3. **Ứng dụng (4 điểm):** Flask xử lý đăng ký, đăng nhập, CRUD ghi chú; Jinja2 hiển thị giao diện; PostgreSQL lưu users/notes. Ảnh đăng ký, đăng nhập, danh sách và thêm/sửa/xóa; thanh đầu trang hiện MSSV.
4. **Dịch vụ và Nginx (2 điểm):** systemd tự khởi động Gunicorn, chỉ nghe 127.0.0.1:8000; Nginx chuyển tiếp cổng 80. Ảnh `systemctl is-active`, `ss -tlnp`, trình duyệt laptop mở http://192.168.174.20.
5. **Tường lửa (1,5 điểm):** mặc định deny incoming, allow outgoing; SSH chỉ từ 192.168.174.0/24, HTTP 80/tcp. Ảnh `sudo ufw status verbose`.
6. **Bảo mật (1,5 điểm):** mật khẩu băm Werkzeug, CSRF, user CSDL `notes_app`, `.env` không commit, `.env.example` và `.gitignore`. Ảnh cấu trúc repo, `sudo ss -tlnp`; không chụp bí mật thật.
7. **Nộp và kết luận (1 điểm):** link GitHub, README cài lại, kết quả tự kiểm tra, AI đã dùng, tài liệu tham khảo, link video. Nêu hạn chế HTTP chỉ dùng trong mạng ảo nội bộ theo yêu cầu bài.

**Đoạn AI mẫu:** “Tôi dùng AI để tham khảo kiến trúc, tạo mã mẫu Flask/Jinja2, gợi ý lệnh cấu hình và dàn ý báo cáo. Tôi tự triển khai trên VPS, kiểm tra từng chức năng và chỉnh sửa theo kết quả thực tế.”

## Video 4 phút

| Thời gian | Cảnh |
| --- | --- |
| 00:00–00:20 | Giới thiệu họ tên, MSSV, IP VPS, repo GitHub. |
| 00:20–01:00 | Laptop mở http://192.168.174.20, đăng ký và đăng nhập. |
| 01:00–02:20 | Thêm → xem → sửa → xóa một ghi chú; cho thấy kết quả sau mỗi thao tác. |
| 02:20–03:00 | SSH bằng khóa vào VPS; `sudo systemctl status ghichu --no-pager`; Nginx đang chạy. |
| 03:00–03:35 | `sudo ufw status verbose`; chỉ SSH theo dải và HTTP 80. |
| 03:35–04:00 | `sudo ss -tlnp`; chỉ rõ 127.0.0.1:8000, 127.0.0.1:5432, :80, kết thúc. |

Mọi ảnh chụp terminal hãy chạy `hostname` trong cùng cửa sổ để thấy MSSV; giao diện web luôn có MSSV ở đầu trang.

## Vấn đáp ngắn

1. **Frontend/backend/CSDL là gì?** Jinja2 tạo HTML, Flask xử lý yêu cầu và quy tắc, PostgreSQL lưu users/notes.
2. **Mật khẩu lưu thế nào?** `generate_password_hash` tạo hash; `check_password_hash` đối chiếu khi đăng nhập, không lưu mật khẩu rõ.
3. **Vì sao dùng user `notes_app`?** Ứng dụng chỉ dùng quyền của role riêng và sở hữu `notes_db`, không dùng tài khoản quản trị PostgreSQL.
4. **Vì sao Gunicorn chỉ nghe 127.0.0.1?** Laptop chỉ truy cập Nginx :80; backend không lộ trực tiếp trên mạng ảo.
5. **systemd để làm gì?** Chạy Gunicorn dưới dạng dịch vụ, tự khởi động cùng VPS và khởi chạy lại nếu lỗi.
6. **Nginx làm gì?** Nhận HTTP :80, chuyển tiếp tới Gunicorn :8000 trên loopback.
7. **UFW cho phép những gì?** SSH 22/tcp từ 192.168.174.0/24; HTTP 80/tcp; mặc định chặn kết nối vào.
8. **Vì sao `.env` không ở GitHub?** Chứa SECRET_KEY và mật khẩu DB; repo chỉ có `.env.example` để hướng dẫn tạo giá trị riêng.

## Checklist điểm

| Tiêu chí | Minh chứng cần có |
| --- | --- |
| 4,0 ứng dụng | Đăng ký, đăng nhập, thêm/xem/sửa/xóa; PostgreSQL lưu bản ghi, giao diện từ laptop. |
| 2,0 dịch vụ/proxy | Gunicorn systemd `enabled/active`, `127.0.0.1:8000`; Nginx :80. |
| 1,5 UFW | Deny incoming, allow outgoing, 22 chỉ từ 192.168.174.0/24, 80/tcp. |
| 1,5 bảo mật | Hash mật khẩu, .env riêng, .env.example, user `notes_app`. |
| 1,0 nộp | GitHub + README, PDF 5–8 trang, video 3–5 phút, mọi ảnh có MSSV, AI và nguồn. |
