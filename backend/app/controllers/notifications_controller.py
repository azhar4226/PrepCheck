from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from app.models import User, Quiz, QuizAttempt
import json

notifications_bp = Blueprint('notifications', __name__)

class NotificationService:
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
        # For demo purposes, create some sample notifications
        notifications = []
        
        user = User.query.get(user_id)
        if not user:
            return notifications
        
        # Recent quiz completions
        recent_attempts = QuizAttempt.query.filter_by(
            user_id=user_id, is_completed=True
        ).order_by(QuizAttempt.completed_at.desc()).limit(5).all()
        
        for attempt in recent_attempts:
            percentage = (attempt.score / attempt.total_marks * 100) if attempt.total_marks > 0 else 0
            
            if percentage >= 90:
                notification_type = 'success'
                title = '🎉 Excellent Performance!'
                message = f'You scored {percentage}% on {attempt.quiz.title}'
            elif percentage >= 70:
                notification_type = 'info'
                title = '✅ Good Job!'
                message = f'You scored {percentage}% on {attempt.quiz.title}'
            else:
                notification_type = 'warning'
                title = '📚 Keep Practicing!'
                message = f'You scored {percentage}% on {attempt.quiz.title}. Review the topics and try again!'
            
            notifications.append({
                'id': f"quiz_{attempt.id}",
                'title': title,
                'message': message,
                'type': notification_type,
                'created_at': attempt.completed_at.isoformat(),
                'read': False,
                'data': {
                    'quiz_id': attempt.quiz_id,
                    'attempt_id': attempt.id,
                    'score': attempt.score,
                    'percentage': round(percentage, 2)
                }
            })
        
        # Achievement notifications
        total_attempts = QuizAttempt.query.filter_by(
            user_id=user_id, is_completed=True
        ).count()
        
        if total_attempts == 1:
            notifications.append({
                'id': f"achievement_first_quiz_{user_id}",
                'title': '🎯 First Quiz Complete!',
                'message': 'Congratulations on completing your first quiz!',
                'type': 'success',
                'created_at': (datetime.utcnow() - timedelta(days=1)).isoformat(),
                'read': False,
                'data': {'achievement': 'first_quiz'}
            })
        elif total_attempts == 10:
            notifications.append({
                'id': f"achievement_10_quizzes_{user_id}",
                'title': '🏆 Quiz Master!',
                'message': 'Amazing! You\'ve completed 10 quizzes!',
                'type': 'success',
                'created_at': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'read': False,
                'data': {'achievement': '10_quizzes'}
            })
        
        # Study streak notifications
        notifications.append({
            'id': f"streak_{user_id}",
            'title': '🔥 Study Streak!',
            'message': 'You\'re on a 3-day study streak! Keep it up!',
            'type': 'info',
            'created_at': (datetime.utcnow() - timedelta(hours=6)).isoformat(),
            'read': False,
            'data': {'streak_days': 3}
        })
        
        # Sort by created_at descending
        notifications.sort(key=lambda x: x['created_at'], reverse=True)
        
        return notifications[:limit]

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
        
        # In a real implementation, you'd update the notification in the database
        # For now, we'll just return success
        
        return jsonify({'message': 'Notification marked as read'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read for the current user"""
    try:
        user_id = int(get_jwt_identity())
        
        # In a real implementation, you'd update all notifications in the database
        # For now, we'll just return success
        
        return jsonify({'message': 'All notifications marked as read'}), 200
        
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
