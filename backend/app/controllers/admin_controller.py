"""
Refactored Admin Controller using Service Layer
This is the first step towards microservices - extracting business logic to services
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from datetime import datetime

# Import services
from app.services.admin_dashboard_service import AdminDashboardService
from app.services.content_management_service import ContentManagementService
from app.services.user_management_service import UserManagementService
from app.services.admin_profile_service import AdminProfileService
from app.services.user_analytics_service import UserAnalyticsService

from app.models import User

admin_bp = Blueprint('admin', __name__)

# Initialize services
dashboard_service = AdminDashboardService()
content_service = ContentManagementService()
user_service = UserManagementService()
profile_service = AdminProfileService()
analytics_service = UserAnalyticsService()


def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))


# Dashboard Statistics
@admin_bp.route('/dashboard/test', methods=['GET'])
def test_dashboard_stats():
    """Test endpoint without authentication for debugging"""
    try:
        simple_stats = dashboard_service.get_basic_stats()
        response_data = {**simple_stats, 'debug': 'Updated to use new UGC NET models'}
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({'error': str(e), 'debug': 'Error in test endpoint'}), 500


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Get comprehensive dashboard statistics using service layer"""
    try:
        time_filter = request.args.get('timeFilter', '7d')
        stats = dashboard_service.get_comprehensive_dashboard_stats(time_filter)
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Subject Management
@admin_bp.route('/subjects', methods=['GET'])
@admin_required
def get_subjects():
    try:
        subjects = content_service.get_all_subjects()
        return jsonify(subjects), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/subjects', methods=['POST'])
@admin_required
def create_subject():
    try:
        data = request.get_json()
        subject = content_service.create_subject(data)
        return jsonify({
            'message': 'Subject created successfully',
            'subject': subject
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@admin_required
def update_subject(subject_id):
    try:
        data = request.get_json()
        subject = content_service.update_subject(subject_id, data)
        return jsonify({
            'message': 'Subject updated successfully',
            'subject': subject
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@admin_required
def delete_subject(subject_id):
    try:
        content_service.delete_subject(subject_id)
        return jsonify({'message': 'Subject deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Chapter Management
@admin_bp.route('/chapters', methods=['GET'])
@admin_required
def get_chapters():
    try:
        subject_id = request.args.get('subject_id', type=int)
        chapters = content_service.get_chapters(subject_id)
        return jsonify(chapters), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/chapters', methods=['POST'])
@admin_required
def create_chapter():
    try:
        data = request.get_json()
        chapter = content_service.create_chapter(data)
        return jsonify({
            'message': 'Chapter created successfully',
            'chapter': chapter
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Mock Test Management
@admin_bp.route('/mock-tests', methods=['GET'])
@admin_required
def get_mock_tests():
    """Get mock tests with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        subject_id = request.args.get('subject_id', type=int)
        
        result = content_service.get_mock_tests(page, per_page, subject_id)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/mock-tests', methods=['POST'])
@admin_required
def create_mock_test():
    """Create mock test"""
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        test = content_service.create_mock_test(data, current_user.id)
        
        return jsonify({
            'message': 'Mock test created successfully',
            'test': test,
            'mock_test': test  # For compatibility
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/mock-tests/<int:test_id>/toggle-status', methods=['PUT'])
@admin_required
def toggle_mock_test_status(test_id):
    """Toggle mock test active status"""
    try:
        test = content_service.update_mock_test_status(test_id)
        status = 'activated' if test['is_active'] else 'deactivated'
        
        return jsonify({
            'message': f'Mock test {status} successfully',
            'test': test,
            'mock_test': test  # For compatibility
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/mock-tests/<int:test_id>/status', methods=['PUT'])
@admin_required
def update_mock_test_status(test_id):
    """Update mock test status"""
    try:
        data = request.get_json()
        if 'is_active' not in data:
            return jsonify({'error': 'is_active field required'}), 400
        
        test = content_service.update_mock_test_status(test_id, data['is_active'])
        status = 'activated' if test['is_active'] else 'deactivated'
        
        return jsonify({
            'message': f'Mock test {status} successfully',
            'test': test,
            'mock_test': test  # For compatibility
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# User Management
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '', type=str)
        filter_type = request.args.get('filter', 'all', type=str)
        role_filter = request.args.get('role', '', type=str)
        status_filter = request.args.get('status', '', type=str)
        
        result = user_service.get_users(page, per_page, search, filter_type, role_filter, status_filter)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    try:
        data = request.get_json()
        user = user_service.update_user(user_id, data)
        return jsonify(user), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/create', methods=['POST'])
@admin_required
def create_user():
    try:
        data = request.get_json()
        user = user_service.create_user(data)
        return jsonify({
            'message': 'User created successfully',
            'user': user
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        user_service.delete_user(user_id)
        return jsonify({'message': 'User deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Admin Profile Management
@admin_bp.route('/profile', methods=['GET'])
@admin_required
def get_admin_profile():
    """Get current admin's profile"""
    try:
        user = get_current_user()
        admin = profile_service.get_admin_profile(user.id)
        return jsonify({'admin': admin}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/profile', methods=['PUT'])
@admin_required
def update_admin_profile():
    """Update current admin's profile"""
    try:
        user = get_current_user()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        admin = profile_service.update_admin_profile(user.id, data)
        return jsonify({
            'message': 'Admin profile updated successfully',
            'admin': admin
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/profile/password', methods=['PUT'])
@admin_required
def change_admin_password():
    """Change admin's password"""
    try:
        user = get_current_user()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        profile_service.change_admin_password(user.id, current_password, new_password)
        return jsonify({'message': 'Password changed successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@admin_bp.route('/profile/picture', methods=['POST'])
@admin_required
def upload_admin_profile_picture():
    """Upload admin profile picture"""
    try:
        user = get_current_user()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        result = profile_service.upload_profile_picture(user.id, file)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/profile/picture', methods=['DELETE'])
@admin_required
def remove_admin_profile_picture():
    """Remove admin profile picture"""
    try:
        user = get_current_user()
        result = profile_service.remove_profile_picture(user.id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Enhanced User Management for Admins
@admin_bp.route('/users/<int:user_id>/profile', methods=['PUT'])
@admin_required
def update_user_profile_by_admin(user_id):
    """Update any user's profile (admin only)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user = user_service.update_user_profile_by_admin(user_id, data)
        return jsonify({
            'message': 'User profile updated successfully',
            'user': user
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# User Analytics for Admin
@admin_bp.route('/user/<int:user_id>/analytics', methods=['GET'])
@admin_required
def get_user_analytics(user_id):
    """Get analytics for any user (admin only)"""
    try:
        days = request.args.get('days', 30, type=int)
        subject_id = request.args.get('subject_id', type=int)
        
        analytics = analytics_service.get_user_analytics(user_id, days, subject_id)
        return jsonify(analytics), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Export & Settings (Simplified for now)
@admin_bp.route('/export', methods=['POST'])
@admin_required
def export_data():
    """Export data (simplified implementation)"""
    try:
        data = request.get_json()
        export_type = data.get('type', 'all')
        
        # Simplified response - full implementation would use celery tasks
        return jsonify({
            'message': f'Export of {export_type} data initiated',
            'status': 'success',
            'note': 'Full export functionality requires celery integration'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/settings', methods=['GET'])
@admin_required
def get_system_settings():
    """Get system settings"""
    try:
        settings = {
            'app_name': 'PrepCheck UGC NET',
            'version': '2.0.0',
            'max_file_size': '5MB',
            'allowed_extensions': ['png', 'jpg', 'jpeg', 'gif', 'webp'],
            'maintenance_mode': False,
            'registration_enabled': True,
            'email_verification_required': False,
            'max_mock_test_time': 180,
            'max_practice_test_time': 30,
            'default_questions_per_test': 20,
            'password_min_length': 6,
            'ugc_net_pass_percentage': 40.0,
            'practice_pass_percentage': 60.0
        }
        return jsonify({'settings': settings}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
