"""
Automated Test Suite for NEU Events Management System
Tests authentication, permissions, discovery, registration, check-in, feedback, and moderation.
"""
import unittest
from app import app
from models import db, User, Event, EventCategory, Registration, Feedback

class NeuEventsTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        with app.app_context():
            for username in ['11244035', '11240123', 'vieclam@neu.edu.vn', 'quanly@neu.edu.vn']:
                u = User.query.filter((User.username == username) | (User.email == username)).first()
                if u and not u.check_password('123'):
                    u.set_password('123')
            db.session.commit()

    def login(self, username, password):
        return self.client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_01_login_success_student(self):
        """Test student login with valid credentials"""
        response = self.login('11244035', '123')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Nguyễn Thị Thu'.encode('utf-8'), response.data)
        self.logout()

    def test_02_login_invalid_password(self):
        """Test login fails with incorrect password"""
        response = self.login('11244035', 'wrongpass')
        self.assertEqual(response.status_code, 200)
        self.assertIn('không chính xác'.encode('utf-8'), response.data)

    def test_02b_login_invalid_mssv(self):
        """Test login fails when MSSV is not in NEU student registry"""
        response = self.login('99999999', 'anypassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn('không tồn tại trong danh sách sinh viên Đại học Kinh tế Quốc dân'.encode('utf-8'), response.data)

    def test_02c_check_student_api(self):
        """Test API validating active NEU student ID"""
        # Valid MSSV
        res_valid = self.client.get('/api/check-student?student_id=11244035')
        self.assertEqual(res_valid.status_code, 200)
        data_valid = res_valid.get_json()
        self.assertTrue(data_valid['exists'])
        self.assertEqual(data_valid['full_name'], 'Nguyễn Thị Thu')

        # Invalid MSSV
        res_invalid = self.client.get('/api/check-student?student_id=88888888')
        self.assertEqual(res_invalid.status_code, 200)
        data_invalid = res_invalid.get_json()
        self.assertFalse(data_invalid['exists'])

    def test_02d_student_set_password(self):
        """Test student self-setting password and logging in"""
        res = self.client.post('/set-password', data={
            'student_id': '11240123',
            'new_password': 'mypassword2026',
            'confirm_password': 'mypassword2026',
            'remember': 'true'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Nguyễn Minh Anh'.encode('utf-8'), res.data)
        self.logout()

        # Re-login with the newly set password
        login_res = self.login('11240123', 'mypassword2026')
        self.assertEqual(login_res.status_code, 200)
        self.assertIn('Nguyễn Minh Anh'.encode('utf-8'), login_res.data)
        self.logout()

    def test_03_event_discovery_page(self):
        """Test event listing and keyword search"""
        self.login('11244035', '123')
        # View discovery page
        response = self.client.get('/events')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Khám phá sự kiện'.encode('utf-8'), response.data)

        # Search filter
        search_resp = self.client.get('/events?q=Career')
        self.assertEqual(search_resp.status_code, 200)
        self.logout()

    def test_04_event_detail_page(self):
        """Test viewing event detail for an existing event"""
        self.login('11244035', '123')
        with app.app_context():
            event = Event.query.first()
            event_id = event.id
        
        response = self.client.get(f'/events/{event_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(event.title.encode('utf-8'), response.data)
        self.logout()

    def test_05_my_events_page(self):
        """Test student's registered events schedule page"""
        self.login('11244035', '123')
        response = self.client.get('/my-events')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sự kiện đã đăng ký'.encode('utf-8'), response.data)
        self.logout()

    def test_06_checkin_page(self):
        """Test check-in page interface"""
        self.login('11244035', '123')
        response = self.client.get('/checkin')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Điểm danh sự kiện'.encode('utf-8'), response.data)
        self.logout()

    def test_07_moderation_access_control(self):
        """Test RBAC: Student cannot access moderation, but Manager can"""
        # Student access attempt
        self.login('11244035', '123')
        std_resp = self.client.get('/moderation', follow_redirects=True)
        self.assertEqual(std_resp.status_code, 200)
        self.assertIn('không có quyền'.encode('utf-8'), std_resp.data)
        self.logout()

        # Manager access attempt
        self.login('quanly@neu.edu.vn', '123')
        mgr_resp = self.client.get('/moderation')
        self.assertEqual(mgr_resp.status_code, 200)
        self.assertIn('Kiểm duyệt sự kiện'.encode('utf-8'), mgr_resp.data)
        self.logout()

    def test_08_organizer_events_page(self):
        """Test organizer events management page"""
        self.login('vieclam@neu.edu.vn', '123')
        response = self.client.get('/organizer/events')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Quản lý sự kiện'.encode('utf-8'), response.data)
        self.logout()

    def test_09_analytics_page(self):
        """Test reports and analytics page"""
        self.login('quanly@neu.edu.vn', '123')
        response = self.client.get('/analytics')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Báo cáo – thống kê'.encode('utf-8'), response.data)
        self.logout()

    def test_10_feedback_page(self):
        """Test feedback evaluation page"""
        self.login('11244035', '123')
        response = self.client.get('/feedback')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Đánh giá sự kiện'.encode('utf-8'), response.data)
        self.logout()

    def test_11_manager_display_name(self):
        """Test manager login displays 'Đơn vị quản lý' instead of previous department title"""
        login_res = self.login('quanly@neu.edu.vn', '123')
        self.assertEqual(login_res.status_code, 200)
        self.assertIn('Đơn vị quản lý'.encode('utf-8'), login_res.data)
        self.logout()

    def test_12_change_password_flow(self):
        """Test user changes password and can authenticate with new password"""
        # Login as organizer
        self.login('vieclam@neu.edu.vn', '123')

        # Change password
        chg_res = self.client.post('/change-password', data={
            'old_password': '123',
            'new_password': 'organizerNewPass2026',
            'confirm_password': 'organizerNewPass2026'
        }, follow_redirects=True)
        self.assertEqual(chg_res.status_code, 200)
        self.assertIn('Đổi mật khẩu thành công'.encode('utf-8'), chg_res.data)
        self.logout()

        # Re-login with new password
        new_login = self.login('vieclam@neu.edu.vn', 'organizerNewPass2026')
        self.assertEqual(new_login.status_code, 200)
        self.logout()

        # Restore password for future tests
        self.login('vieclam@neu.edu.vn', 'organizerNewPass2026')
        self.client.post('/change-password', data={
            'old_password': 'organizerNewPass2026',
            'new_password': '123',
            'confirm_password': '123'
        }, follow_redirects=True)
        self.logout()

    def test_13_switch_role_disabled(self):
        """Test public role switcher is disabled"""
        self.login('11244035', '123')
        res = self.client.get('/switch-role/MANAGER', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn('vô hiệu hóa'.encode('utf-8'), res.data)
        self.logout()

if __name__ == '__main__':
    unittest.main()
