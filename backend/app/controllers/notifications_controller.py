from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from app.models import User, UGCNetMockAttempt, UGCNetPracticeAttempt
import json
import os

notifications_bp = Blueprint('notifications', __name__)

class NotificationService:
    @staticmethod
    def get_read_notifications_file(user_id):
        """Get path to read notifications file for a user"""
        read_dir = os.path.join('instance', 'read_notifications')
        os.makedirs(read_dir, exist_ok=True)
        return os.path.join(read_dir, f"user_{user_id}.json")
    
    @staticmethod
    def get_read_notifications(user_id):
        """Get set of read notification IDs for a user"""
        try:
            file_path = NotificationService.get_read_notifications_file(user_id)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return set(data.get('read_notifications', []))
        except:
            pass
        return set()
    
    @staticmethod
    def mark_notification_read(user_id, notification_id):
        """Mark a notification as read"""
        try:
            file_path = NotificationService.get_read_notifications_file(user_id)
            read_notifications = NotificationService.get_read_notifications(user_id)
            read_notifications.add(notification_id)
            
            with open(file_path, 'w') as f:
                json.dump({'read_notifications': list(read_notifications)}, f)
            return True
        except:
            return False
    
    @staticmethod
    def mark_all_notifications_read(user_id, notification_ids):
        """Mark multiple notifications as read"""
        try:
            file_path = NotificationService.get_read_notifications_file(user_id)
            read_notifications = NotificationService.get_read_notifications(user_id)
            read_notifications.update(notification_ids)
            
            with open(file_path, 'w') as f:
                json.dump({'read_notifications': list(read_notifications)}, f)
            return True
        except:
            return False

    @staticmethod
    def create_notification(user_id, title, message, type='info', data=None):
        """Create a new notification for a user"""
        notification = {
            'id': f"notif_{datetime.utcnow().timestamp()}_{user_id}",
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': type,  # info, success, warning, error
            'data': data or {},
            'created_at': datetime.utcnow().isoformat(),
            'read': False
        }
        
        # Store in database or cache (using a simple approach for now)
        # In production, you'd want a proper notifications table
        return notification
    
    @staticmethod
    def get_user_notifications(user_id, limit=20):
        """Get notifications for a user"""
        # Get read notification IDs
        read_notifications = NotificationService.get_read_notifications(user_id)
        
        # For demo purposes, create some sample notifications
        notifications = []
        
        user = User.query.get(user_id)
        if not user:
            return notifications
        
        # Recent test completions (both mock and practice tests)
        mock_attempts = UGCNetMockAttempt.query.filter_by(
            user_id=user_id, is_completed=True
        ).order_by(UGCNetMockAttempt.created_at.desc()).limit(3).all()
        
        practice_attempts = UGCNetPracticeAttempt.query.filter_by(
            user_id=user_id, is_completed=True
        ).order_by(UGCNetPracticeAttempt.created_at.desc()).limit(3).all()
        
        # Combine and sort all attempts
        all_attempts = []
        for attempt in mock_attempts:
            all_attempts.append({
                'attempt': attempt,
                'type': 'mock',
                'created_at': attempt.created_at,
                'percentage': attempt.percentage or 0,
                'title': f"Mock Test - {attempt.mock_test.subject.name if attempt.mock_test and attempt.mock_test.subject else 'UGC NET'}"
            })
        
        for attempt in practice_attempts:
            all_attempts.append({
                'attempt': attempt,
                'type': 'practice',
                'created_at': attempt.created_at,
                'percentage': attempt.percentage or 0,
                'title': f"Practice Test - {attempt.subject.name if attempt.subject else 'UGC NET'}"
            })
        
        # Sort by created_at and take top 5
        all_attempts.sort(key=lambda x: x['created_at'], reverse=True)
        recent_attempts = all_attempts[:5]
        
        for attempt_data in recent_attempts:
            attempt = attempt_data['attempt']
            percentage = attempt_data['percentage']
            test_title = attempt_data['title']
            
            if percentage >= 90:
                notification_type = 'success'
                title = '🎉 Excellent Performance!'
                message = f'You scored {percentage:.1f}% on {test_title}'
            elif percentage >= 70:
                notification_type = 'info'
                title = '✅ Good Job!'
                message = f'You scored {percentage:.1f}% on {test_title}'
            else:
                notification_type = 'warning'
                title = '📚 Keep Practicing!'
                message = f'You scored {percentage:.1f}% on {test_title}. Review the topics and try again!'
            
            notification_id = f"{attempt_data['type']}_test_{attempt.id}"
            notifications.append({
                'id': notification_id,
                'title': title,
                'message': message,
                'type': notification_type,
                'created_at': attempt.created_at.isoformat(),
                'read': notification_id in read_notifications,
                'data': {
                    'attempt_id': attempt.id,
                    'attempt_type': attempt_data['type'],
                    'percentage': round(percentage, 2)
                }
            })
        
        # Achievement notifications
        total_mock_attempts = UGCNetMockAttempt.query.filter_by(
            user_id=user_id, is_completed=True
        ).count()
        
        total_practice_attempts = UGCNetPracticeAttempt.query.filter_by(
            user_id=user_id, is_completed=True
        ).count()
        
        total_attempts = total_mock_attempts + total_practice_attempts
        
        if total_attempts == 1:
            notification_id = f"achievement_first_test_{user_id}"
            notifications.append({
                'id': notification_id,
                'title': '🎯 First Test Complete!',
                'message': 'Congratulations on completing your first test!',
                'type': 'success',
                'created_at': (datetime.utcnow() - timedelta(days=1)).isoformat(),
                'read': notification_id in read_notifications,
                'data': {'achievement': 'first_test'}
            })
        elif total_attempts >= 10:
            notification_id = f"achievement_10_tests_{user_id}"
            notifications.append({
                'id': notification_id,
                'title': '🏆 Test Master!',
                'message': 'Amazing! You\'ve completed 10 tests!',
                'type': 'success',
                'created_at': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'read': notification_id in read_notifications,
                'data': {'achievement': '10_tests'}
            })
        
        # Study streak notifications (only if user has some activity)
        if total_attempts > 0:
            notification_id = f"streak_{user_id}"
            notifications.append({
                'id': notification_id,
                'title': '🔥 Study Streak!',
                'message': 'You\'re on a 3-day study streak! Keep it up!',
                'type': 'info',
                'created_at': (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                'read': notification_id in read_notifications,
                'data': {'streak_days': 3}
            })
        
        # Sort by created_at descending
        notifications.sort(key=lambda x: x['created_at'], reverse=True)
        
        return notifications[:limit]

@notifications_bp.route('', methods=['GET'])
@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get notifications for the current user"""
    try:
        user_id = int(get_jwt_identity())
        limit = request.args.get('limit', 20, type=int)
        
        notifications = NotificationService.get_user_notifications(user_id, limit)
        
        return jsonify({
            'notifications': notifications,
            'unread_count': len([n for n in notifications if not n['read']])
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/<notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        user_id = int(get_jwt_identity())
        
        # Mark the notification as read
        success = NotificationService.mark_notification_read(user_id, notification_id)
        
        if success:
            return jsonify({'message': 'Notification marked as read'}), 200
        else:
            return jsonify({'error': 'Failed to mark notification as read'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read for the current user"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get all current notifications to mark them as read
        notifications = NotificationService.get_user_notifications(user_id)
        notification_ids = [n['id'] for n in notifications]
        
        # Mark all as read
        success = NotificationService.mark_all_notifications_read(user_id, notification_ids)
        
        if success:
            return jsonify({'message': 'All notifications marked as read'}), 200
        else:
            return jsonify({'error': 'Failed to mark all notifications as read'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_notification_preferences():
    """Get notification preferences for the current user"""
    try:
        user_id = int(get_jwt_identity())
        
        # Default preferences
        preferences = {
            'email_notifications': True,
            'push_notifications': True,
            'quiz_completion': True,
            'achievement_notifications': True,
            'study_reminders': True,
            'weekly_summary': True,
            'performance_insights': True
        }
        
        return jsonify(preferences), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_notification_preferences():
    """Update notification preferences for the current user"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # In a real implementation, you'd save these preferences to the database
        # For now, we'll just return the updated preferences
        
        return jsonify({
            'message': 'Notification preferences updated',
            'preferences': data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/send-test', methods=['POST'])
@jwt_required()
def send_test_notification():
    """Send a test notification (for development)"""
    try:
        user_id = int(get_jwt_identity())
        
        notification = NotificationService.create_notification(
            user_id=user_id,
            title='🧪 Test Notification',
            message='This is a test notification to verify the system is working!',
            type='info',
            data={'test': True}
        )
        
        return jsonify({
            'message': 'Test notification sent',
            'notification': notification
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
