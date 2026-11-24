# Ghi chú cá nhân · 2324802010174

Ứng dụng Flask/Jinja2 + PostgreSQL; Gunicorn chỉ nghe `127.0.0.1:8000`, Nginx công bố cổng 80. VPS Ubuntu Server 24.04 LTS, IP `192.168.174.20`, mạng ảo VMware VMnet4 `192.168.174.0/24`. Tác giả: Nguyễn Quốc Chuyên.

## Chức năng

- Đăng ký, đăng nhập, đăng xuất. Werkzeug băm mật khẩu; không lưu mật khẩu rõ.
- Mỗi người tự thêm, xem, sửa, xóa ghi chú của mình.
- Các biểu mẫu POST có CSRF token; truy vấn SQL dùng tham số.

## Cài lại từ đầu trên VPS

### 1. Cài gói và đưa mã lên VPS

Trên VPS (đăng nhập SSH bằng khóa dưới tên `chuyenadmin`):

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip postgresql nginx ufw
sudo systemctl enable --now postgresql nginx
```

Sao chép thư mục dự án từ laptop vào VPS rồi đặt tại `/opt/ghichu`:

```powershell
scp -i "$env:USERPROFILE\.ssh\id_ed25519_2324802010174" -r .\bai2-ghichu chuyenadmin@192.168.174.20:~/
```

Sau đó trên VPS:

```bash
sudo mv ~/bai2-ghichu /opt/ghichu
sudo chown -R chuyenadmin:chuyenadmin /opt/ghichu
cd /opt/ghichu
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Nếu dùng GitHub thay cho `scp`: `git clone <LINK_REPO_CUA_BAN> ~/bai2-ghichu`, rồi thực hiện lệnh `mv` ở trên. Không đưa `.env` lên GitHub.

### 2. Tạo CSDL và tài khoản riêng

Tạo mật khẩu CSDL ngẫu nhiên; lưu giá trị hiện ra ở nơi riêng, đừng chụp màn hình:

```bash
openssl rand -hex 24
sudo -u postgres psql
```

Trong `psql`, thay `MAT_KHAU_VUA_TAO` bằng giá trị thật:

```sql
CREATE ROLE notes_app LOGIN PASSWORD 'MAT_KHAU_VUA_TAO';
CREATE DATABASE notes_db OWNER notes_app;
\q
```

Tạo `.env` từ mẫu:

```bash
cd /opt/ghichu
cp .env.example .env
openssl rand -hex 32
nano .env
chmod 600 .env
```

Trong `.env`: thay `SECRET_KEY` bằng chuỗi hex 64 ký tự vừa tạo; thay `CHANGE_ME_DATABASE_PASSWORD` bằng **đúng mật khẩu** đã dùng cho role `notes_app`. Giữ nguyên host `127.0.0.1`. Không chụp, đăng, commit, hoặc gửi `.env`.

Tạo bảng bằng quyền của `notes_app`:

```bash
set -a; source .env; set +a
psql "$DATABASE_URL" -f schema.sql
unset DATABASE_URL SECRET_KEY
```

Mong đợi: `CREATE TABLE` (hai lần) và `CREATE INDEX`. PostgreSQL mặc định chỉ nghe loopback; kiểm tra bằng `sudo ss -tlnp`.

### 3. Dịch vụ và Nginx

```bash
sudo cp deploy/ghichu.service /etc/systemd/system/
sudo cp deploy/nginx-ghichu.conf /etc/nginx/sites-available/ghichu
sudo ln -s /etc/nginx/sites-available/ghichu /etc/nginx/sites-enabled/ghichu
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl daemon-reload
sudo systemctl enable --now ghichu
sudo nginx -t
sudo systemctl reload nginx
systemctl is-active ghichu nginx postgresql
curl -I http://127.0.0.1/
```

Mong đợi: ba dòng `active`, Nginx báo cấu hình đúng, `curl` nhận HTTP 302 tới `/login`. Khi lỗi: `sudo journalctl -u ghichu -n 50 --no-pager` và `sudo nginx -t`.

### 4. UFW (chạy đúng thứ tự để không khóa SSH)

Giữ một phiên SSH đang mở và đã thử đăng nhập bằng khóa ở cửa sổ thứ hai. Xem luật cũ bằng `sudo ufw status numbered`; nếu có luật rộng như `22/tcp ALLOW Anywhere`, xóa **theo số** sau khi đã thêm luật giới hạn bên dưới.

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.174.0/24 to any port 22 proto tcp
sudo ufw allow 80/tcp
sudo ufw enable
sudo ufw status verbose
sudo ss -tlnp
```

Mong đợi: chỉ `22/tcp` từ `192.168.174.0/24`, `80/tcp` mở; Gunicorn ở `127.0.0.1:8000`, PostgreSQL ở `127.0.0.1:5432` (có thể thêm `[::1]:5432`), Nginx ở `0.0.0.0:80`. Nếu UFW khóa truy cập, vào **console VPS qua ESXi** để sửa.

### 5. Kiểm tra

Trên laptop mở `http://192.168.174.20`: đăng ký → đăng nhập → thêm → xem → sửa → xóa ghi chú. Khởi động lại VPS (`sudo reboot`) và kiểm tra ứng dụng tự chạy. Không dùng IP ngoài, chỉ kiểm thử máy của mình.

## Cấu trúc

```text
app.py                     backend Flask, route và bảo mật
schema.sql                 bảng users, notes
templates/                 giao diện Jinja2
static/style.css           CSS
deploy/ghichu.service      dịch vụ tự khởi động
deploy/nginx-ghichu.conf   reverse proxy cổng 80
.env.example               mẫu biến môi trường, không chứa bí mật thật
.gitignore                 loại trừ .env và môi trường Python
requirements.txt           thư viện Python
```

## Nguồn tham khảo và AI

- Flask: https://flask.palletsprojects.com/en/stable/
- Werkzeug password hashing: https://werkzeug.palletsprojects.com/en/stable/utils/
- PostgreSQL: https://www.postgresql.org/docs/
- Gunicorn: https://docs.gunicorn.org/en/stable/
- Ubuntu Nginx và UFW: https://ubuntu.com/server/docs/

AI hỗ trợ đề xuất kiến trúc, sinh mã mẫu, README và các lệnh triển khai. Người thực hiện tự kiểm tra, vận hành và giải thích từng tệp trước khi nộp.
