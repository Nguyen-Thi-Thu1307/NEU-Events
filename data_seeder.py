"""
Data Seeder for NEU Events
Populates the database with realistic initial data matching the UI mockups.
"""
from datetime import datetime, date, time, timedelta
import json
from models import db, User, EventCategory, Event, Registration, AttendanceSession, AttendanceRecord, Feedback, ApprovalLog

def seed_database(app):
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()

        print("Creating Users...")
        # 1. Users
        student_thu = User(
            username='11244035',
            email='thunguyen@st.neu.edu.vn',
            full_name='Nguyễn Thị Thu',
            role='STUDENT',
            department='Viện CNTT & Kinh tế số',
            student_id='11244035',
            phone='0987123456',
            avatar_initials='MA'
        )
        student_thu.set_password('123')

        student_anh = User(
            username='11240123',
            email='anhnguyen@st.neu.edu.vn',
            full_name='Nguyễn Minh Anh',
            role='STUDENT',
            department='Khoa Marketing',
            student_id='11240123',
            phone='0912345678',
            avatar_initials='MA'
        )
        student_anh.set_password('123')

        student_huy = User(
            username='11240218',
            email='11240218@st.neu.edu.vn',
            full_name='Trần Đức Huy',
            role='STUDENT',
            department='Khoa Tài chính - Ngân hàng',
            student_id='11240218',
            phone='0934567890',
            avatar_initials='DH'
        )
        student_huy.set_password('123')

        student_linh = User(
            username='11240086',
            email='11240086@st.neu.edu.vn',
            full_name='Lê Phương Linh',
            role='STUDENT',
            department='Khoa Quản trị Kinh doanh',
            student_id='11240086',
            phone='0945678901',
            avatar_initials='PL'
        )
        student_linh.set_password('123')

        student_an = User(
            username='11240305',
            email='11240305@st.neu.edu.vn',
            full_name='Phạm Khánh An',
            role='STUDENT',
            department='Khoa Kinh tế Quốc tế',
            student_id='11240305',
            phone='0956789012',
            avatar_initials='KA'
        )
        student_an.set_password('123')

        student_nam = User(
            username='11240172',
            email='11240172@st.neu.edu.vn',
            full_name='Vũ Hoàng Nam',
            role='STUDENT',
            department='Khoa Kế toán',
            student_id='11240172',
            phone='0967890123',
            avatar_initials='HN'
        )
        student_nam.set_password('123')

        organizer_thu = User(
            username='vieclam@neu.edu.vn',
            email='vieclam@neu.edu.vn',
            full_name='Trần Hoài Thu',
            role='ORGANIZER',
            department='Trung tâm Tư vấn hướng nghiệp & Việc làm',
            phone='024 3628 0280',
            avatar_initials='HT'
        )
        organizer_thu.set_password('123')

        manager_admin = User(
            username='quanly@neu.edu.vn',
            email='quanly@neu.edu.vn',
            full_name='Đơn vị Quản lý',
            role='MANAGER',
            department='Đơn vị Quản lý',
            phone='024 3628 0280',
            avatar_initials='QL'
        )
        manager_admin.set_password('123')

        db.session.add_all([student_thu, student_anh, student_huy, student_linh, student_an, student_nam, organizer_thu, manager_admin])
        db.session.commit()

        print("Creating Event Categories...")
        # 2. Categories
        cat_career = EventCategory(name='Nghề nghiệp', color_class='blue')
        cat_academic = EventCategory(name='Học thuật', color_class='emerald')
        cat_seminar = EventCategory(name='Hội thảo', color_class='cyan')
        cat_community = EventCategory(name='Cộng đồng', color_class='amber')
        cat_culture = EventCategory(name='Văn hóa', color_class='purple')

        db.session.add_all([cat_career, cat_academic, cat_seminar, cat_community, cat_culture])
        db.session.commit()

        print("Creating Events...")
        # 3. Events matching exact images
        # Event 1: Ngày hội việc làm NEU 2026
        e_job = Event(
            code='NEU-JOB-2026',
            title='Ngày hội việc làm NEU 2026',
            subtitle='Mở lối sự nghiệp, kết nối tương lai. 50+ doanh nghiệp đồng hành',
            category_id=cat_career.id,
            organizer_id=organizer_thu.id,
            organizer_name='Trung tâm Tư vấn hướng nghiệp & Việc làm',
            organizer_email='vieclam@neu.edu.vn',
            organizer_phone='024 3628 0280 • Máy lẻ 6032',
            location='Hội trường A2 & sảnh nhà A1, 207 Giải Phóng, Hà Nội',
            target_audience='Sinh viên & cựu sinh viên NEU',
            fee='Miễn phí',
            event_date=date(2026, 10, 24),
            start_time=time(8, 0),
            end_time=time(16, 30),
            registration_deadline=datetime(2026, 10, 22, 23, 59),
            max_seats=500,
            registered_seats=320,
            attended_seats=0,
            description="""Ngày hội việc làm NEU 2026 mang đến cơ hội gặp gỡ hơn 50 doanh nghiệp hàng đầu trong lĩnh vực tài chính, công nghệ, tư vấn và kinh doanh. Khám phá vị trí thực tập, tuyển dụng và trao đổi trực tiếp với nhà tuyển dụng.""",
            agenda_json=json.dumps([
                {"time": "08:00–08:30", "title": "Đón tiếp và điểm danh", "venue": "Sảnh nhà A1"},
                {"time": "08:30–09:30", "title": "Khai mạc & đối thoại nghề nghiệp", "venue": "Hội trường A2"},
                {"time": "09:30–15:30", "title": "Kết nối tuyển dụng và tư vấn hồ sơ", "venue": "Các gian hàng doanh nghiệp"},
                {"time": "15:30–16:30", "title": "Chia sẻ kinh nghiệm & tổng kết", "venue": "Hội trường A2"}
            ]),
            checklist_json=json.dumps([
                "Mang theo thẻ sinh viên và mã đăng ký để điểm danh.",
                "Chuẩn bị hồ sơ ứng tuyển; trang phục lịch sự.",
                "Có mặt trước giờ khai mạc ít nhất 15 phút."
            ]),
            handbook_name='Cẩm nang Ngày hội việc làm NEU 2026.pdf',
            cover_image_url='https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&auto=format&fit=crop&q=80',
            status='APPROVED',
            is_featured=True
        )

        # Event 2: Ứng dụng AI trong học tập & nghiên cứu (Currently active check-in!)
        e_ai = Event(
            code='NEU-AI-2026',
            title='Ứng dụng AI trong học tập & nghiên cứu',
            subtitle='Khai phá tiềm năng Generative AI trong xử lý dữ liệu và học tập học thuật',
            category_id=cat_academic.id,
            organizer_id=organizer_thu.id,
            organizer_name='Viện CNTT & Kinh tế số',
            organizer_email='it@neu.edu.vn',
            organizer_phone='024 3628 0280',
            location='Phòng B101, nhà A2',
            target_audience='Sinh viên toàn trường',
            fee='Miễn phí',
            event_date=date.today(),
            start_time=time(14, 0),
            end_time=time(16, 30),
            registration_deadline=datetime.now() + timedelta(days=1),
            max_seats=200,
            registered_seats=180,
            attended_seats=142,
            description="""Hội thảo trang bị kỹ năng ứng dụng các mô hình AI tạo sinh, tự động hóa quy trình tra cứu tài liệu học thuật, viết luận văn và phân tích dữ liệu nghiên cứu kinh tế.""",
            agenda_json=json.dumps([
                {"time": "14:00–14:20", "title": "Đón tiếp và xác nhận điểm danh", "venue": "Phòng B101, nhà A2"},
                {"time": "14:20–15:30", "title": "Chuyên đề: AI trong phân tích kinh tế định lượng", "venue": "Phòng B101"},
                {"time": "15:30–16:30", "title": "Thực hành Prompt Engineering & Hỏi đáp", "venue": "Phòng B101"}
            ]),
            checklist_json=json.dumps([
                "Mang theo laptop cá nhân để thực hành.",
                "Cài đặt trước tài khoản công cụ thực hành theo email hướng dẫn.",
                "Có mặt đúng khung giờ điểm danh 13:45–14:30."
            ]),
            cover_image_url='https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1200&auto=format&fit=crop&q=80',
            status='APPROVED',
            is_featured=False
        )

        # Event 3: Diễn đàn Tài chính bền vững 2026
        e_fin = Event(
            code='NEU-FIN-2026',
            title='Diễn đàn Tài chính bền vững 2026',
            subtitle='Xu hướng ESG và chuyển đổi số trong hệ thống ngân hàng tài chính',
            category_id=cat_seminar.id,
            organizer_id=organizer_thu.id,
            organizer_name='Khoa Tài chính - Ngân hàng',
            location='Hội trường A2',
            target_audience='Sinh viên khối ngành Kinh tế & Tài chính',
            fee='Miễn phí',
            event_date=date(2026, 10, 28),
            start_time=time(8, 30),
            end_time=time(11, 30),
            registration_deadline=datetime(2026, 10, 27, 18, 0),
            max_seats=300,
            registered_seats=156,
            attended_seats=0,
            description="""Quy tụ các chuyên gia kinh tế đầu ngành thảo luận về tiêu chuẩn ESG, tài chính xanh và cơ hội nghề nghiệp trong ngành ngân hàng bền vững.""",
            cover_image_url='https://images.unsplash.com/photo-1591115765373-5207764f72e7?w=1200&auto=format&fit=crop&q=80',
            status='APPROVED'
        )

        # Event 4: NEU xanh: Từ ý tưởng đến hành động (Completed)
        e_green = Event(
            code='NEU-GREEN-2026',
            title='NEU xanh: Từ ý tưởng đến hành động',
            subtitle='Chiến dịch bảo vệ môi trường học đường và tái chế xanh',
            category_id=cat_community.id,
            organizer_id=organizer_thu.id,
            organizer_name='Đoàn Thanh niên - Hội Sinh viên NEU',
            location='Khuôn viên NEU',
            target_audience='Toàn thể sinh viên NEU',
            fee='Miễn phí',
            event_date=date(2026, 10, 5),
            start_time=time(7, 30),
            end_time=time(11, 0),
            registration_deadline=datetime(2026, 10, 4, 18, 0),
            max_seats=250,
            registered_seats=240,
            attended_seats=216,
            description="""Hoạt động trồng cây, thu gom rác thải điện tử và lan tỏa ý thức bảo vệ môi trường vì một NEU xanh, sạch, đẹp.""",
            cover_image_url='https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=1200&auto=format&fit=crop&q=80',
            status='COMPLETED'
        )

        # Event 5: Đêm nhạc Chào tân sinh viên K68
        e_music = Event(
            code='NEU-MUSIC-2026',
            title='Đêm nhạc Chào tân sinh viên K68',
            subtitle='Đại nhạc hội bùng nổ âm thanh và ánh sáng chào đón tân sinh viên',
            category_id=cat_culture.id,
            organizer_id=organizer_thu.id,
            organizer_name='Hội Sinh viên & CLB Âm nhạc MEC',
            location='Sân quảng trường NEU',
            target_audience='Tân sinh viên K68 & sinh viên NEU',
            fee='Miễn phí',
            event_date=date(2026, 10, 18),
            start_time=time(18, 0),
            end_time=time(21, 0),
            registration_deadline=datetime(2026, 10, 17, 20, 0),
            max_seats=600,
            registered_seats=420,
            attended_seats=0,
            description="""Chương trình nghệ thuật đặc sắc chào đón tân sinh viên K68 với sự góp mặt của các ca sĩ khách mời nổi tiếng và các CLB nghệ thuật đình đám NEU.""",
            cover_image_url='https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=1200&auto=format&fit=crop&q=80',
            status='APPROVED'
        )

        # Event 6: Ngày hội tình nguyện Thu yêu thương (Cancelled)
        e_volunteer = Event(
            code='NEU-VOL-2026',
            title='Ngày hội tình nguyện Thu yêu thương',
            subtitle='Chiến dịch tình nguyện mùa thu sẻ chia yêu thương tới cộng đồng khó khăn',
            category_id=cat_community.id,
            organizer_id=organizer_thu.id,
            organizer_name='Đội Tình nguyện NEU',
            location='Điểm tập trung: cổng NEU',
            target_audience='Sinh viên tình nguyện',
            fee='Miễn phí',
            event_date=date(2026, 10, 20),
            start_time=time(7, 0),
            end_time=time(12, 0),
            registration_deadline=datetime(2026, 10, 19, 12, 0),
            max_seats=150,
            registered_seats=80,
            attended_seats=0,
            description="""Chương trình thiện nguyện thăm hỏi và trao quà tại trung tâm bảo trợ xã hội.""",
            cover_image_url='https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=1200&auto=format&fit=crop&q=80',
            status='CANCELLED',
            cancel_reason='Thời tiết mưa bão không đảm bảo an toàn di chuyển, Ban tổ chức xin tạm hoãn và thông báo lịch mới sau.'
        )

        # Event 7: Cuộc thi Ý tưởng khởi nghiệp NEU 2026 (Pending Moderation)
        e_startup = Event(
            code='NEU-STARTUP-2026',
            title='Cuộc thi Ý tưởng khởi nghiệp NEU 2026',
            subtitle='Vườn ươm tài năng đổi mới sáng tạo và khởi nghiệp sinh viên',
            category_id=cat_academic.id,
            organizer_id=organizer_thu.id,
            organizer_name='Trung tâm Khởi nghiệp & ĐMST NEU',
            location='Hội trường A1 & A2',
            target_audience='Sinh viên toàn quốc',
            fee='Miễn phí',
            event_date=date(2026, 10, 30),
            start_time=time(8, 0),
            end_time=time(17, 0),
            registration_deadline=datetime(2026, 10, 28, 23, 59),
            max_seats=250,
            registered_seats=0,
            attended_seats=0,
            description="""Sân chơi thường niên tìm kiếm và hỗ trợ hiện thực hóa các đề tài khởi nghiệp công nghệ, kinh tế tuần hoàn và dịch vụ cộng đồng.""",
            cover_image_url='https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=1200&auto=format&fit=crop&q=80',
            status='PENDING'
        )

        # Event 8: Phương pháp nghiên cứu khoa học (Completed)
        e_research = Event(
            code='NEU-RES-2026',
            title='Phương pháp nghiên cứu khoa học',
            subtitle='Hướng dẫn phương pháp luận và viết bài báo khoa học chuẩn Scopus',
            category_id=cat_academic.id,
            organizer_id=organizer_thu.id,
            organizer_name='Phòng Quản lý Khoa học',
            location='Phòng B203, nhà A2',
            target_audience='Sinh viên làm NCKH & Luận văn',
            fee='Miễn phí',
            event_date=date(2026, 9, 30),
            start_time=time(14, 0),
            end_time=time(16, 0),
            registration_deadline=datetime(2026, 9, 29, 18, 0),
            max_seats=150,
            registered_seats=150,
            attended_seats=138,
            description="""Hội thảo chuyên sâu về kỹ năng chọn đề tài, xử lý dữ liệu định lượng và trích dẫn chuẩn học thuật quốc tế.""",
            cover_image_url='https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1200&auto=format&fit=crop&q=80',
            status='COMPLETED'
        )

        # Event 9: Kỹ năng thuyết trình tự tin (Completed)
        e_presentation = Event(
            code='NEU-SKILL-2026',
            title='Kỹ năng thuyết trình tự tin',
            subtitle='Làm chủ sân khấu, thu hút người nghe và truyền tải thông điệp sắc sảo',
            category_id=cat_career.id,
            organizer_id=organizer_thu.id,
            organizer_name='CLB Thuyết trình & MC NEU',
            location='Phòng B105, nhà A2',
            target_audience='Sinh viên toàn trường',
            fee='Miễn phí',
            event_date=date(2026, 9, 25),
            start_time=time(9, 0),
            end_time=time(11, 0),
            registration_deadline=datetime(2026, 9, 24, 18, 0),
            max_seats=100,
            registered_seats=100,
            attended_seats=88,
            description="""Workshop rèn luyện kỹ năng ngôn ngữ cơ thể, thiết kế slide thuyết trình ấn tượng và phong thái tự tin trước đám đông.""",
            cover_image_url='https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=1200&auto=format&fit=crop&q=80',
            status='COMPLETED'
        )

        db.session.add_all([e_job, e_ai, e_fin, e_green, e_music, e_volunteer, e_startup, e_research, e_presentation])
        db.session.commit()

        print("Creating Registrations & Attendance for Students...")
        # 4. Registrations matching mockup for student_thu (Nguyễn Thị Thu - MSSV: 11244035)
        # Event 2 (AI): Registered, not checked-in yet, ready for check-in
        reg_thu_ai = Registration(
            ticket_code='NEU-AI-0123',
            user_id=student_thu.id,
            event_id=e_ai.id,
            registration_status='REGISTERED',
            attendance_status='NOT_YET',
            registered_at=datetime.now() - timedelta(days=2)
        )

        # Event 5 (Music): Registered, event not yet happened
        reg_thu_music = Registration(
            ticket_code='NEU-MUSIC-0456',
            user_id=student_thu.id,
            event_id=e_music.id,
            registration_status='REGISTERED',
            attendance_status='NOT_YET',
            registered_at=datetime.now() - timedelta(days=4)
        )

        # Event 3 (Finance): Registered, event not yet happened
        reg_thu_fin = Registration(
            ticket_code='NEU-FIN-0789',
            user_id=student_thu.id,
            event_id=e_fin.id,
            registration_status='REGISTERED',
            attendance_status='NOT_YET',
            registered_at=datetime.now() - timedelta(days=5)
        )

        # Event 4 (Green): Registered, ATTENDED
        reg_thu_green = Registration(
            ticket_code='NEU-GREEN-0321',
            user_id=student_thu.id,
            event_id=e_green.id,
            registration_status='REGISTERED',
            attendance_status='ATTENDED',
            registered_at=datetime(2026, 10, 1, 9, 30)
        )

        # Event 8 (Research): Registered, ATTENDED, already reviewed
        reg_thu_res = Registration(
            ticket_code='NEU-RES-0654',
            user_id=student_thu.id,
            event_id=e_research.id,
            registration_status='REGISTERED',
            attendance_status='ATTENDED',
            registered_at=datetime(2026, 9, 20, 10, 0)
        )

        # Event 9 (Presentation): Registered, ABSENT
        reg_thu_pres = Registration(
            ticket_code='NEU-SKILL-0987',
            user_id=student_thu.id,
            event_id=e_presentation.id,
            registration_status='REGISTERED',
            attendance_status='ABSENT',
            registered_at=datetime(2026, 9, 15, 8, 30)
        )

        # Event 6 (Volunteer): Registered, EVENT CANCELLED
        reg_thu_vol = Registration(
            ticket_code='NEU-VOL-0112',
            user_id=student_thu.id,
            event_id=e_volunteer.id,
            registration_status='REGISTERED',
            attendance_status='NOT_APPLICABLE',
            registered_at=datetime(2026, 10, 10, 14, 0)
        )

        db.session.add_all([reg_thu_ai, reg_thu_music, reg_thu_fin, reg_thu_green, reg_thu_res, reg_thu_pres, reg_thu_vol])
        db.session.commit()

        # Also add other students for live attendance table in Event 2 (AI) matching "Điểm danh.jpg"
        reg_anh_ai = Registration(
            ticket_code='NEU-AI-0124',
            user_id=student_anh.id,
            event_id=e_ai.id,
            registration_status='REGISTERED',
            attendance_status='NOT_YET',
            registered_at=datetime.now() - timedelta(days=2)
        )

        reg_huy_ai = Registration(
            ticket_code='NEU-AI-0125',
            user_id=student_huy.id,
            event_id=e_ai.id,
            registration_status='REGISTERED',
            attendance_status='ATTENDED',
            registered_at=datetime.now() - timedelta(days=2)
        )

        reg_linh_ai = Registration(
            ticket_code='NEU-AI-0126',
            user_id=student_linh.id,
            event_id=e_ai.id,
            registration_status='REGISTERED',
            attendance_status='ATTENDED',
            registered_at=datetime.now() - timedelta(days=2)
        )

        reg_an_ai = Registration(
            ticket_code='NEU-AI-0127',
            user_id=student_an.id,
            event_id=e_ai.id,
            registration_status='REGISTERED',
            attendance_status='ATTENDED',
            registered_at=datetime.now() - timedelta(days=2)
        )

        reg_nam_ai = Registration(
            ticket_code='NEU-AI-0128',
            user_id=student_nam.id,
            event_id=e_ai.id,
            registration_status='REGISTERED',
            attendance_status='NOT_YET',
            registered_at=datetime.now() - timedelta(days=2)
        )

        # Registrations for Event 1 (Job Fair) matching "Quản lý sự kiện.jpg"
        reg_huy_job = Registration(
            ticket_code='NEU-JOB-001',
            user_id=student_huy.id,
            event_id=e_job.id,
            registration_status='REGISTERED',
            registered_at=datetime(2026, 10, 9, 10, 15)
        )
        reg_linh_job = Registration(
            ticket_code='NEU-JOB-002',
            user_id=student_linh.id,
            event_id=e_job.id,
            registration_status='REGISTERED',
            registered_at=datetime(2026, 10, 9, 14, 20)
        )
        reg_an_job = Registration(
            ticket_code='NEU-JOB-003',
            user_id=student_an.id,
            event_id=e_job.id,
            registration_status='REGISTERED',
            registered_at=datetime(2026, 10, 10, 8, 45)
        )
        reg_nam_job = Registration(
            ticket_code='NEU-JOB-004',
            user_id=student_nam.id,
            event_id=e_job.id,
            registration_status='REGISTERED',
            registered_at=datetime(2026, 10, 11, 16, 10)
        )

        db.session.add_all([reg_anh_ai, reg_huy_ai, reg_linh_ai, reg_an_ai, reg_nam_ai, reg_huy_job, reg_linh_job, reg_an_job, reg_nam_job])
        db.session.commit()

        print("Creating Active Attendance Session for Event AI...")
        # 5. Active Attendance Session for Event AI matching "Điểm danh.jpg"
        ai_session = AttendanceSession(
            event_id=e_ai.id,
            session_pin='AI1210',
            qr_token='NEU-QR-AI1210-ACTIVE',
            valid_from=datetime.now() - timedelta(minutes=45),
            valid_to=datetime.now() + timedelta(minutes=75),
            is_active=True
        )
        db.session.add(ai_session)
        db.session.commit()

        # Add records for checked-in students
        rec_huy = AttendanceRecord(
            session_id=ai_session.id,
            registration_id=reg_huy_ai.id,
            user_id=student_huy.id,
            checked_in_at=datetime.now().replace(hour=13, minute=52),
            checkin_method='PIN',
            status='ATTENDED'
        )
        rec_linh = AttendanceRecord(
            session_id=ai_session.id,
            registration_id=reg_linh_ai.id,
            user_id=student_linh.id,
            checked_in_at=datetime.now().replace(hour=13, minute=56),
            checkin_method='PIN',
            status='ATTENDED'
        )
        rec_an = AttendanceRecord(
            session_id=ai_session.id,
            registration_id=reg_an_ai.id,
            user_id=student_an.id,
            checked_in_at=datetime.now().replace(hour=14, minute=2),
            checkin_method='QR',
            status='ATTENDED'
        )
        db.session.add_all([rec_huy, rec_linh, rec_an])
        db.session.commit()

        print("Creating Feedbacks...")
        # 6. Feedbacks
        fb1 = Feedback(
            event_id=e_green.id,
            user_id=student_huy.id,
            rating_stars=5,
            rating_content=5,
            rating_organization=5,
            rating_speaker=5,
            rating_venue=5,
            comment='Sự kiện rất ý nghĩa và lan tỏa được năng lượng tích cực tới các bạn sinh viên. Ban tổ chức chuẩn bị chu đáo!',
            is_anonymous=False,
            created_at=datetime(2026, 10, 6, 9, 0)
        )
        fb2 = Feedback(
            event_id=e_green.id,
            user_id=student_linh.id,
            rating_stars=5,
            rating_content=5,
            rating_organization=4,
            rating_speaker=5,
            rating_venue=5,
            comment='Rất thích hoạt động trồng cây và đổi rác lấy quà. Hy vọng NEU sẽ tổ chức nhiều chương trình bảo vệ môi trường như thế này.',
            is_anonymous=True,
            created_at=datetime(2026, 10, 6, 11, 30)
        )
        fb3 = Feedback(
            event_id=e_research.id,
            user_id=student_thu.id,
            rating_stars=5,
            rating_content=5,
            rating_organization=5,
            rating_speaker=5,
            rating_venue=4,
            comment='Thầy cô chia sẻ phương pháp luận rất thực tế và chi tiết, giúp ích nhiều cho bài nghiên cứu khoa học của mình.',
            is_anonymous=False,
            created_at=datetime(2026, 10, 1, 15, 0)
        )
        db.session.add_all([fb1, fb2, fb3])
        db.session.commit()

        print("Creating Approval Logs...")
        # 7. Approval Logs
        log1 = ApprovalLog(
            event_id=e_job.id,
            manager_id=manager_admin.id,
            action='APPROVE',
            note='Hồ sơ đầy đủ, kế hoạch an ninh và cơ sở vật chất sảnh A1, hội trường A2 được duyệt.',
            created_at=datetime(2026, 10, 8, 14, 30)
        )
        log2 = ApprovalLog(
            event_id=e_ai.id,
            manager_id=manager_admin.id,
            action='APPROVE',
            note='Nội dung chuyên môn cập nhật, phù hợp định hướng nghiên cứu sinh viên.',
            created_at=datetime(2026, 10, 5, 10, 15)
        )
        db.session.add_all([log1, log2])
        db.session.commit()

        print("Database seeded successfully with all mock data!")

if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///neu_events.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    seed_database(app)
