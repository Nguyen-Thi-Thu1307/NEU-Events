# NEU Events - Cổng Quản lý và Tổ chức Sự kiện Đại học Kinh tế Quốc dân

Hệ thống web toàn diện phục vụ công tác tổ chức, quản lý và tham gia sự kiện dành cho sinh viên, ban tổ chức và đơn vị quản trị Trường Đại học Kinh tế Quốc dân (NEU).

---

## 📌 1. Tính năng nổi bật

* **Khám phá & Đăng ký sự kiện (`/events`)**:
  * Bộ lọc tìm kiếm đa tiêu chí: Từ khóa, đơn vị, địa điểm, thể loại (Học thuật, Nghề nghiệp, Hội thảo, Văn hóa,...).
  * Kiểm soát số lượng chỗ còn lại (`max_seats`) và hạn đăng ký trực quan.
* **Theo dõi lịch trình cá nhân (`/my-events`)**:
  * Dashboard trạng thái: Sắp diễn ra, đã tham dự, vắng mặt.
  * Xem mã vé điện tử và quản lý trạng thái đăng ký.
* **Điểm danh 2 chiều thông minh (`/checkin`)**:
  * Sinh viên tự điểm danh trong phiên bằng mã PIN hoặc quét QR Code.
  * Ban tổ chức quản lý phiên trực tiếp, đếm số lượng người tham dự realtime và hỗ trợ xác nhận thủ công.
* **Quản trị & Phê duyệt sự kiện (`/moderation` & `/organizer/events`)**:
  * Ban tổ chức tạo mới, chỉnh sửa, gửi yêu cầu phê duyệt và xuất danh sách người tham gia (CSV/Excel).
  * Nhà trường / Ban quản lý kiểm duyệt nội dung, kiểm tra xung đột lịch trình hội trường và phê duyệt sự kiện.
* **Đánh giá & Phản hồi (`/feedback`)**:
  * Sinh viên đã tham dự được quyền chấm điểm sao và nhận xét chi tiết (có tùy chọn ẩn danh).
* **Báo cáo & Thống kê (`/analytics`)**:
  * Biểu đồ tỷ lệ tham dự, cơ cấu thể loại sự kiện và bảng KPI tổng hợp.

---

## 👥 2. Tài khoản Demo trải nghiệm (Mật khẩu mặc định: `123`)

| Phân quyền (Role) | Mã đăng nhập / Email | Họ tên đại diện | Đơn vị / Chức vụ |
| :--- | :--- | :--- | :--- |
| **Sinh viên (`STUDENT`)** | `11244035` | Nguyễn Hoàng Long | Viện CNTT & Kinh tế số |
| **Ban tổ chức (`ORGANIZER`)** | `vieclam@neu.edu.vn` | TS. Trần Văn Minh | Trung tâm TV Hướng nghiệp & Việc làm |
| **Quản lý (`MANAGER`)** | `quanly@neu.edu.vn` | ThS. Lê Quang Đạo | Phòng CTCT & Quản lý Sinh viên |

> **Mẹo**: Trong thanh điều hướng (Navbar) có menu **"Đổi vai trò"** giúp bạn chuyển đổi nhanh giữa 3 phân quyền mà không cần đăng xuất.

---

## 🚀 3. Hướng dẫn cài đặt & Khởi chạy

### Yêu cầu môi trường
* Python 3.10 trở lên

### Các bước thực hiện:

1. **Cài đặt thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Khởi tạo dữ liệu mẫu (Seeder):**
   *(Dữ liệu mẫu đã có sẵn trong file SQLite `instance/neu_events.db`, nếu muốn tạo mới lại từ đầu có thể chạy:)*
   ```bash
   python data_seeder.py
   ```

3. **Chạy ứng dụng Web:**
   ```bash
   python app.py
   ```

4. **Truy cập hệ thống:**
   Mở trình duyệt web tại địa chỉ: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📁 4. Cấu trúc thư mục

```text
d:/PYTHON/NEU Events/
├── instance/
│   └── neu_events.db           # SQLite database
├── templates/                  # Giao diện Jinja2 HTML Templates
│   ├── base.html               # Khung sườn chung, navbar, footer & modal đổi vai trò
│   ├── login.html              # Trang xác thực người dùng
│   ├── events.html             # Khám phá danh sách sự kiện
│   ├── event_detail.html       # Chi tiết sự kiện & form đăng ký
│   ├── my_events.html          # Lịch trình & sự kiện đã đăng ký
│   ├── checkin.html            # Không gian điểm danh 2 chiều (PIN/QR)
│   ├── organizer_events.html   # Quản lý sự kiện dành cho ban tổ chức
│   ├── moderation.html         # Kiểm duyệt sự kiện dành cho nhà trường
│   ├── feedback.html           # Khảo sát & phản hồi sau sự kiện
│   └── analytics.html          # Báo cáo và bảng chỉ số KPI
├── agent.md                    # Tài liệu đặc tả kỹ thuật và tiêu chuẩn giao diện
├── app.py                      # Flask Application Controller & Routes
├── models.py                   # SQLAlchemy ORM Models
├── data_seeder.py              # Script nạp dữ liệu demo
├── requirements.txt            # Danh sách thư viện phụ thuộc
└── README.md                   # Tài liệu hướng dẫn sử dụng
```
