"""
NEU Events - Cổng Quản lý và Tổ chức Sự kiện Đại học Kinh tế Quốc dân
Main Flask Web Application
"""
import os
import random
from datetime import datetime, date, time
from io import StringIO
import csv
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, Response
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)

from models import (
    db, User, EventCategory, Event, Registration,
    AttendanceSession, AttendanceRecord, Feedback, ApprovalLog
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'neu-events-super-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///neu_events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Vui lòng đăng nhập để tiếp tục.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context Processors for Templates
@app.context_processor
def inject_global_data():
    today = date.today()
    def get_pending_count():
        return Event.query.filter_by(status='PENDING').count()

    def is_reviewed(event_id):
        if not current_user.is_authenticated:
            return False
        return Feedback.query.filter_by(event_id=event_id, user_id=current_user.id).first() is not None

    return dict(
        today=today,
        get_pending_count=get_pending_count,
        is_reviewed=is_reviewed
    )

# ----------------- AUTHENTICATION -----------------

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('events'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('events'))

    login_id = ''
    if request.method == 'POST':
        login_id = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember = bool(request.form.get('remember'))

        # Find user by MSSV, username, or email
        user = User.query.filter(
            (User.username == login_id) |
            (User.email == login_id) |
            (User.student_id == login_id)
        ).first()

        if not user:
            if login_id.isdigit():
                flash(f'Mã sinh viên "{login_id}" không tồn tại trong danh sách sinh viên Đại học Kinh tế Quốc dân. Vui lòng kiểm tra lại chính xác MSSV.', 'error')
            else:
                flash(f'Tài khoản "{login_id}" không tồn tại trong hệ thống NEU Events.', 'error')
            return render_template('login.html', login_id=login_id)

        if not user.check_password(password):
            flash('Mật khẩu không chính xác. Sinh viên có thể sử dụng chức năng "Kích hoạt / Đặt lại mật khẩu" bên dưới để tự thiết lập mật khẩu.', 'error')
            return render_template('login.html', login_id=login_id)

        login_user(user, remember=remember)
        flash(f'Chào mừng {user.full_name} ({user.role}) đã đăng nhập thành công!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('events'))

    return render_template('login.html', login_id=login_id)

@app.route('/api/check-student', methods=['GET'])
def check_student():
    """Verify if MSSV belongs to an active NEU student"""
    student_id = request.args.get('student_id', '').strip()
    if not student_id:
        return jsonify({'exists': False, 'message': 'Vui lòng cung cấp mã sinh viên.'})

    user = User.query.filter(
        (User.student_id == student_id) |
        (User.username == student_id)
    ).first()

    if user and user.role == 'STUDENT':
        return jsonify({
            'exists': True,
            'full_name': user.full_name,
            'department': user.department or 'Đại học Kinh tế Quốc dân',
            'student_id': user.student_id or user.username,
            'email': user.email
        })
    else:
        return jsonify({
            'exists': False,
            'message': f'Mã sinh viên "{student_id}" không tồn tại trong danh sách sinh viên Đại học Kinh tế Quốc dân.'
        })

@app.route('/set-password', methods=['POST'])
def set_password():
    """Allow NEU students to set/reset their own password without Microsoft SSO integration"""
    student_id = request.form.get('student_id', '').strip()
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    remember = bool(request.form.get('remember'))

    user = User.query.filter(
        (User.student_id == student_id) |
        (User.username == student_id)
    ).first()

    if not user or user.role != 'STUDENT':
        flash('Mã sinh viên không hợp lệ hoặc không thuộc danh sách sinh viên NEU.', 'error')
        return redirect(url_for('login'))

    if len(new_password) < 6:
        flash('Mật khẩu phải có độ dài tối thiểu 6 ký tự để bảo mật tài khoản.', 'error')
        return redirect(url_for('login'))

    if new_password != confirm_password:
        flash('Mật khẩu xác nhận không khớp. Vui lòng nhập lại chính xác.', 'error')
        return redirect(url_for('login'))

    user.set_password(new_password)
    db.session.commit()

    login_user(user, remember=remember)
    flash(f'Thiết lập mật khẩu thành công! Chào mừng sinh viên {user.full_name} ({user.student_id}).', 'success')
    return redirect(url_for('events'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất an toàn.', 'info')
    return redirect(url_for('login'))

@app.route('/switch-role/<role>')
@login_required
def switch_role(role):
    """Quick role switcher for testing the app with different roles"""
    if role not in ['STUDENT', 'ORGANIZER', 'MANAGER']:
        role = 'STUDENT'

    # Find demo user for this role
    if role == 'STUDENT':
        target_user = User.query.filter_by(student_id='11244035').first()
    elif role == 'ORGANIZER':
        target_user = User.query.filter_by(email='vieclam@neu.edu.vn').first()
    else:
        target_user = User.query.filter_by(email='quanly@neu.edu.vn').first()

    if target_user:
        login_user(target_user)
        flash(f'Đã chuyển góc nhìn sang: {target_user.full_name} ({role})', 'info')
    return redirect(request.referrer or url_for('events'))

# ----------------- 1. DISCOVERY & EVENT LIST -----------------

@app.route('/events')
@login_required
def events():
    q = request.args.get('q', '').strip()
    time_filter = request.args.get('time_filter', '')
    location = request.args.get('location', '')
    category_id = request.args.get('category', '')
    tab = request.args.get('tab', 'all')

    query = Event.query

    # Status tab filtering
    today = date.today()
    if tab == 'upcoming':
        query = query.filter(Event.status == 'APPROVED', Event.event_date > today)
    elif tab == 'active':
        query = query.filter(Event.status == 'APPROVED', Event.event_date == today)
    elif tab == 'completed':
        query = query.filter(Event.status == 'COMPLETED')
    elif tab == 'cancelled':
        query = query.filter(Event.status == 'CANCELLED')
    else: # all approved / completed / cancelled
        query = query.filter(Event.status.in_(['APPROVED', 'COMPLETED', 'CANCELLED']))

    # Keyword filter
    if q:
        query = query.filter(
            (Event.title.ilike(f'%{q}%')) |
            (Event.organizer_name.ilike(f'%{q}%')) |
            (Event.code.ilike(f'%{q}%'))
        )

    # Location filter
    if location:
        query = query.filter(Event.location.ilike(f'%{location}%'))

    # Category filter
    if category_id and category_id.isdigit():
        query = query.filter(Event.category_id == int(category_id))

    events_list = query.order_by(Event.event_date.asc()).all()

    # Calculate counts for tabs
    counts = {
        'all': Event.query.filter(Event.status.in_(['APPROVED', 'COMPLETED', 'CANCELLED'])).count(),
        'upcoming': Event.query.filter(Event.status == 'APPROVED', Event.event_date > today).count(),
        'active': Event.query.filter(Event.status == 'APPROVED', Event.event_date == today).count(),
        'completed': Event.query.filter(Event.status == 'COMPLETED').count(),
        'cancelled': Event.query.filter(Event.status == 'CANCELLED').count()
    }

    featured = Event.query.filter_by(is_featured=True).first()
    categories = EventCategory.query.all()

    return render_template(
        'events.html',
        events=events_list,
        categories=categories,
        featured_event=featured,
        current_tab=tab,
        counts=counts
    )

# ----------------- 2. EVENT DETAILS & REGISTRATION -----------------

@app.route('/events/<int:event_id>')
@login_required
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    existing_reg = Registration.query.filter_by(
        user_id=current_user.id,
        event_id=event.id,
        registration_status='REGISTERED'
    ).first()

    return render_template(
        'event_detail.html',
        event=event,
        existing_registration=existing_reg
    )

@app.route('/events/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)

    # Validation
    if not event.is_registration_open:
        flash('Rất tiếc, sự kiện này đã hết chỗ hoặc quá hạn đăng ký!', 'error')
        return redirect(url_for('event_detail', event_id=event.id))

    existing_reg = Registration.query.filter_by(
        user_id=current_user.id,
        event_id=event.id,
        registration_status='REGISTERED'
    ).first()

    if existing_reg:
        flash('Bạn đã đăng ký tham gia sự kiện này rồi!', 'warning')
        return redirect(url_for('event_detail', event_id=event.id))

    # Create new ticket code
    random_num = random.randint(100, 999)
    prefix = event.code.split('-')[1] if '-' in event.code else 'EVT'
    ticket_code = f"NEU-{prefix}-{random_num}"

    new_reg = Registration(
        ticket_code=ticket_code,
        user_id=current_user.id,
        event_id=event.id,
        registration_status='REGISTERED',
        attendance_status='NOT_YET',
        registered_at=datetime.utcnow()
    )

    event.registered_seats += 1
    db.session.add(new_reg)
    db.session.commit()

    flash(f'🎉 Đăng ký thành công! Mã vé của bạn là: {ticket_code}. Hãy đến đúng giờ để điểm danh nhé!', 'success')
    return redirect(url_for('my_events'))

@app.route('/registrations/<int:reg_id>/cancel', methods=['POST'])
@login_required
def cancel_registration(reg_id):
    reg = Registration.query.get_or_404(reg_id)
    if reg.user_id != current_user.id and current_user.role not in ['ORGANIZER', 'MANAGER']:
        flash('Bạn không có quyền thực hiện thao tác này.', 'error')
        return redirect(url_for('my_events'))

    reg.registration_status = 'CANCELLED'
    reg.attendance_status = 'NOT_APPLICABLE'
    if reg.event.registered_seats > 0:
        reg.event.registered_seats -= 1

    db.session.commit()
    flash(f'Đã hủy đăng ký sự kiện "{reg.event.title}". Chỗ trống đã được mở cho sinh viên khác.', 'info')
    return redirect(request.referrer or url_for('my_events'))

# ----------------- 3. REGISTERED EVENTS (MY EVENTS) -----------------

@app.route('/my-events')
@login_required
def my_events():
    filter_type = request.args.get('filter', 'all')
    today = date.today()

    query = Registration.query.filter_by(user_id=current_user.id)

    if filter_type == 'upcoming':
        query = query.join(Event).filter(Event.event_date >= today, Registration.registration_status == 'REGISTERED', Registration.attendance_status != 'ATTENDED')
    elif filter_type == 'attended':
        query = query.filter_by(attendance_status='ATTENDED')
    elif filter_type == 'absent':
        query = query.filter_by(attendance_status='ABSENT')
    elif filter_type == 'cancelled':
        query = query.join(Event).filter((Event.status == 'CANCELLED') | (Registration.registration_status == 'CANCELLED'))

    user_registrations = query.order_by(Registration.registered_at.desc()).all()

    # KPI Statistics
    all_regs = Registration.query.filter_by(user_id=current_user.id).all()
    stats = {
        'total': len([r for r in all_regs if r.registration_status == 'REGISTERED']),
        'upcoming': len([r for r in all_regs if r.registration_status == 'REGISTERED' and r.event.event_date >= today and r.attendance_status != 'ATTENDED']),
        'attended': len([r for r in all_regs if r.attendance_status == 'ATTENDED']),
        'absent': len([r for r in all_regs if r.attendance_status == 'ABSENT'])
    }

    # Find live event today for hero banner
    live_reg = None
    for r in all_regs:
        if r.event.event_date == today and r.registration_status == 'REGISTERED' and r.event.status == 'APPROVED':
            live_reg = r
            break

    return render_template(
        'my_events.html',
        registrations=user_registrations,
        stats=stats,
        live_registration=live_reg,
        current_filter=filter_type
    )

# ----------------- 4. ATTENDANCE & CHECK-IN -----------------

@app.route('/checkin')
@login_required
def checkin():
    event_id = request.args.get('event_id')
    today = date.today()

    all_events = Event.query.filter_by(status='APPROVED').all()

    if event_id and event_id.isdigit():
        active_event = Event.query.get(int(event_id))
    else:
        # Default to event happening today or first approved
        active_event = Event.query.filter_by(event_date=today, status='APPROVED').first()
        if not active_event:
            active_event = Event.query.filter_by(code='NEU-AI-2026').first() or Event.query.first()

    active_session = AttendanceSession.query.filter_by(event_id=active_event.id, is_active=True).first()

    # Student's registration for this event
    active_reg = Registration.query.filter_by(
        event_id=active_event.id,
        user_id=current_user.id
    ).first()

    user_att_record = None
    if active_reg:
        user_att_record = AttendanceRecord.query.filter_by(registration_id=active_reg.id).first()

    # Live attendee list for organizer
    attendees_list = Registration.query.filter_by(
        event_id=active_event.id,
        registration_status='REGISTERED'
    ).all()

    attended_count = len([a for a in attendees_list if a.attendance_status == 'ATTENDED'])
    live_stats = {
        'registered': len(attendees_list),
        'attended': attended_count,
        'not_yet': max(0, len(attendees_list) - attended_count)
    }

    return render_template(
        'checkin.html',
        active_event=active_event,
        all_events=all_events,
        active_session=active_session,
        active_registration=active_reg,
        user_attendance_record=user_att_record,
        attendees_list=attendees_list,
        live_stats=live_stats
    )

@app.route('/checkin/submit', methods=['POST'])
@login_required
def submit_checkin():
    event_id = request.form.get('event_id')
    pin = request.form.get('pin', '').strip().upper()

    event = Event.query.get_or_404(int(event_id))
    session = AttendanceSession.query.filter_by(event_id=event.id, is_active=True).first()

    if not session or session.session_pin != pin:
        flash('Mã điểm danh không hợp lệ hoặc phiên điểm danh đã kết thúc!', 'error')
        return redirect(url_for('checkin', event_id=event.id))

    # Find or create registration for this student
    reg = Registration.query.filter_by(event_id=event.id, user_id=current_user.id).first()
    if not reg:
        # Auto register on the spot if slots available
        reg = Registration(
            ticket_code=f"NEU-{event.code.split('-')[1]}-{random.randint(100, 999)}",
            user_id=current_user.id,
            event_id=event.id,
            registration_status='REGISTERED',
            attendance_status='NOT_YET'
        )
        event.registered_seats += 1
        db.session.add(reg)
        db.session.commit()

    if reg.attendance_status == 'ATTENDED':
        flash('Bạn đã điểm danh sự kiện này rồi!', 'info')
        return redirect(url_for('checkin', event_id=event.id))

    # Record attendance
    reg.attendance_status = 'ATTENDED'
    record = AttendanceRecord(
        session_id=session.id,
        registration_id=reg.id,
        user_id=current_user.id,
        checked_in_at=datetime.now(),
        checkin_method='PIN',
        status='ATTENDED'
    )
    event.attended_seats += 1
    db.session.add(record)
    db.session.commit()

    flash('🎉 Điểm danh thành công! Sự kiện đã được ghi nhận vào lịch sử hoạt động sinh viên của bạn.', 'success')
    return redirect(url_for('checkin', event_id=event.id))

@app.route('/checkin/manual/<int:reg_id>', methods=['POST'])
@login_required
def manual_checkin(reg_id):
    reg = Registration.query.get_or_404(reg_id)
    session = AttendanceSession.query.filter_by(event_id=reg.event_id, is_active=True).first()

    reg.attendance_status = 'ATTENDED'
    if session:
        record = AttendanceRecord(
            session_id=session.id,
            registration_id=reg.id,
            user_id=reg.user_id,
            checked_in_at=datetime.now(),
            checkin_method='MANUAL',
            status='ATTENDED'
        )
        db.session.add(record)
    reg.event.attended_seats += 1
    db.session.commit()

    flash(f'Đã xác nhận điểm danh thủ công cho sinh viên {reg.user.full_name} ({reg.user.student_id}).', 'success')
    return redirect(request.referrer or url_for('checkin', event_id=reg.event_id))

@app.route('/checkin/export/<int:event_id>')
@login_required
def export_attendance(event_id):
    event = Event.query.get_or_404(event_id)
    registrations = Registration.query.filter_by(event_id=event.id, registration_status='REGISTERED').all()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['MSSV', 'Ho va ten', 'Email', 'Khoa/Phong ban', 'Ma ve', 'Trang thai tham du', 'Thoi gian diem danh'])

    for r in registrations:
        att_time = r.attendance_record.checked_in_at.strftime('%H:%M %d/%m/%Y') if r.attendance_record else 'Chua diem danh'
        cw.writerow([
            r.user.student_id or r.user.username,
            r.user.full_name,
            r.user.email,
            r.user.department or '',
            r.ticket_code,
            'Da tham du' if r.attendance_status == 'ATTENDED' else 'Chua diem danh',
            att_time
        ])

    output = si.getvalue()
    filename = f"Diem_danh_{event.code}_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

# ----------------- 5. EVENT MANAGEMENT (ORGANIZER) -----------------

@app.route('/organizer/events')
@login_required
def organizer_events():
    if current_user.role not in ['ORGANIZER', 'MANAGER']:
        flash('Bạn không có quyền truy cập trang quản lý của Ban tổ chức.', 'error')
        return redirect(url_for('events'))

    edit_id = request.args.get('edit_id')

    # All events for unit
    my_events = Event.query.order_by(Event.event_date.desc()).all()

    if edit_id and edit_id.isdigit():
        selected_event = Event.query.get(int(edit_id))
    else:
        selected_event = Event.query.filter_by(code='NEU-JOB-2026').first() or my_events[0]

    categories = EventCategory.query.all()
    selected_registrations = Registration.query.filter_by(
        event_id=selected_event.id,
        registration_status='REGISTERED'
    ).all()

    return render_template(
        'organizer_events.html',
        my_events=my_events,
        selected_event=selected_event,
        selected_registrations=selected_registrations,
        categories=categories
    )

@app.route('/organizer/events/save', methods=['POST'])
@login_required
def save_event():
    event_id = request.form.get('event_id')
    title = request.form.get('title', '').strip()
    category_id = int(request.form.get('category_id'))
    organizer_name = request.form.get('organizer_name', '').strip()
    event_date_str = request.form.get('event_date')
    start_time_str = request.form.get('start_time')
    end_time_str = request.form.get('end_time')
    location = request.form.get('location', '').strip()
    max_seats = int(request.form.get('max_seats', 200))
    reg_deadline_str = request.form.get('reg_deadline')
    fee = request.form.get('fee', 'Miễn phí')
    description = request.form.get('description', '').strip()

    ev_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
    st_time = datetime.strptime(start_time_str, '%H:%M').time()
    ed_time = datetime.strptime(end_time_str, '%H:%M').time()
    reg_dl = datetime.strptime(reg_deadline_str, '%Y-%m-%d')

    if event_id and event_id.isdigit():
        event = Event.query.get_or_404(int(event_id))
        event.title = title
        event.category_id = category_id
        event.organizer_name = organizer_name
        event.event_date = ev_date
        event.start_time = st_time
        event.end_time = ed_time
        event.location = location
        event.max_seats = max_seats
        event.registration_deadline = reg_dl
        event.fee = fee
        event.description = description
        flash('Đã lưu thay đổi thông tin sự kiện thành công!', 'success')
    else:
        # Create new
        code = f"NEU-EVT-{random.randint(1000, 9999)}"
        new_event = Event(
            code=code,
            title=title,
            category_id=category_id,
            organizer_id=current_user.id,
            organizer_name=organizer_name,
            location=location,
            event_date=ev_date,
            start_time=st_time,
            end_time=ed_time,
            registration_deadline=reg_dl,
            max_seats=max_seats,
            fee=fee,
            description=description,
            status='PENDING' # requires approval
        )
        db.session.add(new_event)
        flash('Tạo sự kiện mới thành công! Hồ sơ đã được gửi sang Đơn vị Quản lý để kiểm duyệt.', 'success')

    db.session.commit()
    return redirect(url_for('organizer_events', edit_id=event_id if event_id else None))

@app.route('/organizer/events/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_event(event_id):
    event = Event.query.get_or_404(event_id)
    reason = request.form.get('cancel_reason', 'Kế hoạch tổ chức có thay đổi.')

    event.status = 'CANCELLED'
    event.cancel_reason = reason
    db.session.commit()

    flash(f'Đã hủy sự kiện "{event.title}". Thông báo và lý do hủy đã được gửi đến {event.registered_seats} sinh viên đăng ký.', 'warning')
    return redirect(url_for('organizer_events', edit_id=event.id))

# ----------------- 6. MODERATION (MANAGER) -----------------

@app.route('/moderation')
@login_required
def moderation():
    if current_user.role != 'MANAGER':
        flash('Bạn không có quyền truy cập phân hệ Kiểm duyệt sự kiện.', 'error')
        return redirect(url_for('events'))

    pending = Event.query.filter_by(status='PENDING').order_by(Event.created_at.desc()).all()
    approved = Event.query.filter_by(status='APPROVED').order_by(Event.event_date.desc()).limit(10).all()

    return render_template(
        'moderation.html',
        pending_events=pending,
        approved_events=approved
    )

@app.route('/moderation/approve/<int:event_id>', methods=['POST'])
@login_required
def approve_event(event_id):
    if current_user.role != 'MANAGER':
        flash('Bạn không có quyền thực hiện thao tác này.', 'error')
        return redirect(url_for('events'))

    event = Event.query.get_or_404(event_id)
    event.status = 'APPROVED'

    log = ApprovalLog(
        event_id=event.id,
        manager_id=current_user.id,
        action='APPROVE',
        note='Hồ sơ đáp ứng đầy đủ quy chế tổ chức sự kiện NEU.'
    )
    db.session.add(log)
    db.session.commit()

    flash(f'Đã phê duyệt sự kiện "{event.title}". Sự kiện hiện đã xuất bản công khai trên cổng khám phá!', 'success')
    return redirect(url_for('moderation'))

@app.route('/moderation/reject/<int:event_id>', methods=['POST'])
@login_required
def reject_event(event_id):
    if current_user.role != 'MANAGER':
        flash('Bạn không có quyền thực hiện thao tác này.', 'error')
        return redirect(url_for('events'))

    event = Event.query.get_or_404(event_id)
    reason = request.form.get('reason', 'Nội dung cần bổ sung.')

    event.status = 'REJECTED'
    event.cancel_reason = reason

    log = ApprovalLog(
        event_id=event.id,
        manager_id=current_user.id,
        action='REJECT',
        note=reason
    )
    db.session.add(log)
    db.session.commit()

    flash(f'Đã từ chối sự kiện "{event.title}". Lý do đã được gửi phản hồi về Ban tổ chức đơn vị.', 'info')
    return redirect(url_for('moderation'))

# ----------------- 7. FEEDBACK & EVALUATION -----------------

@app.route('/feedback')
@login_required
def feedback():
    selected_event_id = request.args.get('event_id')
    if selected_event_id and selected_event_id.isdigit():
        selected_event_id = int(selected_event_id)

    # Events attended by this user
    user_attended_regs = Registration.query.filter_by(
        user_id=current_user.id,
        attendance_status='ATTENDED'
    ).all()
    attended_events = [r.event for r in user_attended_regs]

    # All feedbacks for organizer review
    all_feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()

    return render_template(
        'feedback.html',
        attended_events=attended_events,
        selected_event_id=selected_event_id,
        all_feedbacks=all_feedbacks
    )

@app.route('/feedback/submit', methods=['POST'])
@login_required
def submit_feedback():
    event_id = int(request.form.get('event_id'))
    rating_stars = int(request.form.get('rating_stars', 5))
    rating_content = int(request.form.get('rating_content', 5))
    rating_organization = int(request.form.get('rating_organization', 5))
    rating_speaker = int(request.form.get('rating_speaker', 5))
    rating_venue = int(request.form.get('rating_venue', 5))
    comment = request.form.get('comment', '').strip()
    is_anonymous = bool(request.form.get('is_anonymous'))

    # Verify student attended
    reg = Registration.query.filter_by(
        event_id=event_id,
        user_id=current_user.id,
        attendance_status='ATTENDED'
    ).first()

    if not reg and current_user.role == 'STUDENT':
        flash('Chỉ những sinh viên đã điểm danh tham dự mới có quyền đánh giá sự kiện này.', 'error')
        return redirect(url_for('feedback'))

    fb = Feedback(
        event_id=event_id,
        user_id=current_user.id,
        rating_stars=rating_stars,
        rating_content=rating_content,
        rating_organization=rating_organization,
        rating_speaker=rating_speaker,
        rating_venue=rating_venue,
        comment=comment,
        is_anonymous=is_anonymous
    )
    db.session.add(fb)
    db.session.commit()

    flash('Cảm ơn bạn đã gửi đánh giá! Ý kiến của bạn sẽ giúp BTC nâng cao chất lượng các sự kiện tiếp theo.', 'success')
    return redirect(url_for('feedback'))

# ----------------- 8. REPORTS & ANALYTICS -----------------

@app.route('/analytics')
@login_required
def analytics():
    # Render analytics matching Báo cáo – thống kê.jpg
    return render_template('analytics.html')

# ----------------- APP INITIALIZATION -----------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Starting NEU Events Web Server at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
