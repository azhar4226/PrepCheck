from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db, redis_client
from app.models import User, Subject, Chapter, QuestionBank, UGCNetMockTest, UGCNetMockAttempt, UGCNetPracticeAttempt
from app.services.user_analytics_service import UserAnalyticsService
import json
import traceback

analytics_bp = Blueprint('analytics', __name__)
analytics_service = UserAnalyticsService()

def admin_required():
    """Check if current user is admin"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return user and user.is_admin

@analytics_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_analytics_overview():
    """Get comprehensive analytics overview using UGC NET models"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        # Time period filters
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Stats
        stats = {
            'total_users': User.query.filter_by(is_admin=False).count(),
            'active_users': User.query.filter(
                User.is_admin == False,
                User.last_login >= start_date
            ).count(),
            'total_subjects': Subject.query.filter_by(is_active=True).count(),
            'total_questions': QuestionBank.query.count(),
            'total_mock_tests': UGCNetMockTest.query.filter_by(is_active=True).count(),
            'total_mock_attempts': UGCNetMockAttempt.query.filter_by(is_completed=True).count(),
            'total_practice_attempts': UGCNetPracticeAttempt.query.filter_by(is_completed=True).count()
        }
        
        return jsonify({
            'stats': stats,
            'period_days': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_performance():
    """Get analytics for the current user"""
    try:
        user_id = get_jwt_identity()
        days = request.args.get('days', 30, type=int)
        subject_id = request.args.get('subject_id', type=int)
        test_type = request.args.get('test_type', 'all')
        
        analytics_data = analytics_service.get_user_analytics(
            user_id=user_id,
            days=days,
            subject_id=subject_id,
            test_type=test_type
        )
        
        return jsonify(analytics_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export', methods=['GET'])
@jwt_required()
def export_analytics():
    """Export analytics in specified format"""
    try:
        user_id = get_jwt_identity()
        format_type = request.args.get('format', 'pdf')
        
        if format_type not in ['pdf', 'csv']:
            return jsonify({'error': 'Unsupported export format'}), 400
            
        export_data = analytics_service.export_user_analytics(user_id, format_type)
        if export_data is None:
            return jsonify({'error': 'Failed to generate export'}), 500
            
        return send_file(
            export_data,
            mimetype='application/pdf' if format_type == 'pdf' else 'text/csv',
            as_attachment=True,
            download_name=f'analytics.{format_type}'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
