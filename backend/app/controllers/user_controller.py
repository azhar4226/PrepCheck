from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import desc, func, distinct, cast, Date
from werkzeug.utils import secure_filename
import os
import uuid
from app import db, redis_client
from app.models import User, Subject, Chapter, QuestionBank, UGCNetMockTest, UGCNetMockAttempt, UGCNetPracticeAttempt
import json

user_bp = Blueprint('user', __name__)

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))

def calculate_study_streak(user_id):
    """Calculate the current study streak for a user using new models"""
    try:
        # Get distinct dates when user completed tests (both mock and practice), ordered by date descending
        mock_dates = db.session.query(
            cast(UGCNetMockAttempt.completed_at, Date).label('date')
        ).filter(
            UGCNetMockAttempt.user_id == user_id,
            UGCNetMockAttempt.is_completed == True
        ).distinct()
        
        practice_dates = db.session.query(
            cast(UGCNetPracticeAttempt.completed_at, Date).label('date')
        ).filter(
            UGCNetPracticeAttempt.user_id == user_id,
            UGCNetPracticeAttempt.is_completed == True
        ).distinct()
        
        # Combine both date queries
        all_dates = mock_dates.union(practice_dates).order_by(desc('date')).all()
        
        if not all_dates:
            return 0
        
        # Convert to list of dates
        dates = [date.date for date in all_dates]
        
        # Check if user studied today or yesterday (streak can continue)
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # If user hasn't studied today or yesterday, streak is broken
        if dates[0] != today and dates[0] != yesterday:
            return 0
        
        # Count consecutive days
        streak = 1
        current_date = dates[0]
        
        for i in range(1, len(dates)):
            expected_date = current_date - timedelta(days=1)
            if dates[i] == expected_date:
                streak += 1
                current_date = dates[i]
            else:
                break
        
        return streak
        
    except Exception as e:
        print(f"Error calculating study streak: {e}")
        return 0

@user_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_user_dashboard():
    """Get user dashboard with UGC NET specific data"""
    try:
        user = get_current_user()
        if not user or not user.is_active:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's test statistics using new models
        total_mock_attempts = UGCNetMockAttempt.query.filter_by(user_id=user.id, is_completed=True).count()
        total_practice_attempts = UGCNetPracticeAttempt.query.filter_by(user_id=user.id, is_completed=True).count()
        total_attempts = total_mock_attempts + total_practice_attempts
        
        # Recent mock attempts
        recent_mock_attempts = UGCNetMockAttempt.query.filter_by(
            user_id=user.id, is_completed=True
        ).order_by(desc(UGCNetMockAttempt.completed_at)).limit(3).all()
        
        # Recent practice attempts
        recent_practice_attempts = UGCNetPracticeAttempt.query.filter_by(
            user_id=user.id, is_completed=True
        ).order_by(desc(UGCNetPracticeAttempt.completed_at)).limit(3).all()
        
        # Combine and sort recent attempts
        all_recent = []
        for attempt in recent_mock_attempts:
            all_recent.append({
                'type': 'mock',
                'data': attempt.to_dict(),
                'completed_at': attempt.completed_at
            })
        
        for attempt in recent_practice_attempts:
            all_recent.append({
                'type': 'practice',
                'data': attempt.to_dict(),
                'completed_at': attempt.completed_at
            })
        
        # Sort by completion time and take top 5
        all_recent.sort(key=lambda x: x['completed_at'], reverse=True)
        recent_attempts = all_recent[:5]
        
        # Calculate average scores
        completed_mock_attempts = UGCNetMockAttempt.query.filter_by(
            user_id=user.id, is_completed=True
        ).all()
        
        completed_practice_attempts = UGCNetPracticeAttempt.query.filter_by(
            user_id=user.id, is_completed=True
        ).all()
        
        # Calculate average mock score
        avg_mock_score = 0
        if completed_mock_attempts:
            mock_scores = [attempt.percentage for attempt in completed_mock_attempts if attempt.percentage is not None]
            if mock_scores:
                avg_mock_score = round(sum(mock_scores) / len(mock_scores), 2)
        
        # Calculate average practice score
        avg_practice_score = 0
        if completed_practice_attempts:
            practice_scores = [attempt.percentage for attempt in completed_practice_attempts if attempt.percentage is not None]
            if practice_scores:
                avg_practice_score = round(sum(practice_scores) / len(practice_scores), 2)
        
        # Overall average score
        all_scores = []
        if completed_mock_attempts:
            all_scores.extend([attempt.percentage for attempt in completed_mock_attempts if attempt.percentage is not None])
        if completed_practice_attempts:
            all_scores.extend([attempt.percentage for attempt in completed_practice_attempts if attempt.percentage is not None])
        
        avg_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0
        
        # Calculate user rank based on average score
        user_rank = None
        if avg_score > 0:
            # Get all users with their average scores (combining mock and practice)
            try:
                # This is a complex query, so we'll calculate it differently
                # For now, we'll use a simplified ranking based on mock test performance
                mock_user_averages = db.session.query(
                    UGCNetMockAttempt.user_id,
                    func.avg(UGCNetMockAttempt.percentage).label('avg_score')
                ).filter(
                    UGCNetMockAttempt.is_completed == True
                ).group_by(UGCNetMockAttempt.user_id).all()
                
                # Sort by average score descending and find user's rank
                sorted_users = sorted(mock_user_averages, key=lambda x: x.avg_score or 0, reverse=True)
                for i, user_avg in enumerate(sorted_users, 1):
                    if user_avg.user_id == user.id:
                        user_rank = i
                        break
            except Exception as e:
                print(f"Error calculating user rank: {e}")
                user_rank = None
        
        # Calculate study streak
        study_streak = calculate_study_streak(user.id)
        
        # Available subjects
        subjects = Subject.query.filter_by(is_active=True).all()
        
        # Get qualification status from latest mock attempt
        latest_mock_attempt = UGCNetMockAttempt.query.filter_by(
            user_id=user.id, is_completed=True
        ).order_by(desc(UGCNetMockAttempt.completed_at)).first()
        
        qualification_status = None
        if latest_mock_attempt:
            qualification_status = latest_mock_attempt.qualification_status
        
        dashboard_data = {
            'user': user.to_dict(),
            'stats': {
                'total_attempts': total_attempts,
                'total_mock_attempts': total_mock_attempts,
                'total_practice_attempts': total_practice_attempts,
                'average_score': avg_score,
                'average_mock_score': avg_mock_score,
                'average_practice_score': avg_practice_score,
                'subjects_available': len(subjects),
                'rank': user_rank,
                'study_streak': study_streak,
                'qualification_status': qualification_status
            },
            'recent_attempts': recent_attempts,
            'subjects': [subject.to_dict() for subject in subjects]
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        print(f"Error in get_user_dashboard: {e}")
        return jsonify({'error': str(e)}), 500

@user_bp.route('/subjects', methods=['GET'])
@jwt_required()
def get_user_subjects():
    """Get subjects with UGC NET specific data"""
    try:
        # Check cache first
        cache_key = 'user_subjects_ugc_net'
        cached_subjects = None
        
        # Safe Redis operation with error handling
        try:
            if redis_client:
                cached_subjects = redis_client.get(cache_key)
        except Exception as redis_error:
            print(f"Redis cache error: {redis_error}")
        
        if cached_subjects:
            return jsonify(json.loads(cached_subjects)), 200
        
        subjects = Subject.query.filter_by(is_active=True).all()
        subjects_data = []
        
        for subject in subjects:
            subject_dict = subject.to_dict()
            # Add chapters with question counts
            chapters_data = []
            for chapter in subject.chapters:
                if chapter.is_active:
                    chapter_dict = chapter.to_dict()
                    chapters_data.append(chapter_dict)
            
            subject_dict['chapters'] = chapters_data
            
            # Add mock test count for this subject
            subject_dict['mock_tests_count'] = UGCNetMockTest.query.filter_by(
                subject_id=subject.id, is_active=True
            ).count()
            
            subjects_data.append(subject_dict)
        
        # Cache for 10 minutes with error handling
        try:
            if redis_client:
                redis_client.setex(cache_key, 600, json.dumps(subjects_data))
        except Exception as redis_error:
            print(f"Redis cache set error: {redis_error}")
        
        return jsonify(subjects_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/chapters/<int:subject_id>', methods=['GET'])
@jwt_required()
def get_user_chapters(subject_id):
    """Get chapters for a subject with UGC NET specific data"""
    try:
        subject = Subject.query.get_or_404(subject_id)
        if not subject.is_active:
            return jsonify({'error': 'Subject not available'}), 404
        
        chapters = Chapter.query.filter_by(
            subject_id=subject_id, is_active=True
        ).all()
        
        chapters_data = []
        for chapter in chapters:
            chapter_dict = chapter.to_dict()
            # Add question count from QuestionBank
            chapter_dict['questions_count'] = QuestionBank.query.filter_by(
                chapter_id=chapter.id
            ).count()
            chapters_data.append(chapter_dict)
        
        return jsonify({
            'subject': subject.to_dict(),
            'chapters': chapters_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/mock-tests/<int:subject_id>', methods=['GET'])
@jwt_required()
def get_user_mock_tests(subject_id):
    """Get available mock tests for a subject"""
    try:
        subject = Subject.query.get_or_404(subject_id)
        if not subject.is_active:
            return jsonify({'error': 'Subject not available'}), 404
        
        mock_tests = UGCNetMockTest.query.filter_by(
            subject_id=subject_id, is_active=True
        ).all()
        
        return jsonify({
            'subject': subject.to_dict(),
            'mock_tests': [test.to_dict() for test in mock_tests]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_user_analytics():
    """Get user's performance analytics"""
    try:
        user = get_current_user()
        if not user or not user.is_active:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        subject_id = request.args.get('subject_id', type=int)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get mock attempts
        mock_query = UGCNetMockAttempt.query.filter(
            UGCNetMockAttempt.user_id == user.id,
            UGCNetMockAttempt.is_completed == True,
            UGCNetMockAttempt.completed_at >= start_date
        )
        
        # Get practice attempts
        practice_query = UGCNetPracticeAttempt.query.filter(
            UGCNetPracticeAttempt.user_id == user.id,
            UGCNetPracticeAttempt.is_completed == True,
            UGCNetPracticeAttempt.completed_at >= start_date
        )
        
        # Apply subject filter if provided
        if subject_id:
            mock_query = mock_query.join(UGCNetMockTest).filter(UGCNetMockTest.subject_id == subject_id)
            practice_query = practice_query.filter(UGCNetPracticeAttempt.subject_id == subject_id)
        
        mock_attempts = mock_query.all()
        practice_attempts = practice_query.all()
        
        # Calculate performance metrics
        mock_scores = [attempt.percentage for attempt in mock_attempts if attempt.percentage is not None]
        practice_scores = [attempt.percentage for attempt in practice_attempts if attempt.percentage is not None]
        
        analytics = {
            'summary': {
                'total_mock_attempts': len(mock_attempts),
                'total_practice_attempts': len(practice_attempts),
                'average_mock_score': round(sum(mock_scores) / len(mock_scores), 2) if mock_scores else 0,
                'average_practice_score': round(sum(practice_scores) / len(practice_scores), 2) if practice_scores else 0,
                'best_mock_score': max(mock_scores) if mock_scores else 0,
                'best_practice_score': max(practice_scores) if practice_scores else 0
            },
            'trends': {
                'mock_attempts': [attempt.to_dict() for attempt in mock_attempts[-10:]],
                'practice_attempts': [attempt.to_dict() for attempt in practice_attempts[-10:]]
            },
            'period_days': days
        }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate email uniqueness if changed
        if 'email' in data and data['email'] != user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'error': 'Email already exists'}), 400
        
        # Update allowed fields
        updatable_fields = [
            'full_name', 'email', 'phone', 'bio', 'date_of_birth', 
            'gender', 'country', 'timezone', 'notification_email',
            'notification_quiz_reminders', 'theme_preference'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'date_of_birth' and data[field]:
                    try:
                        user.date_of_birth = datetime.strptime(data[field], '%Y-%m-%d').date()
                    except ValueError:
                        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
                else:
                    setattr(user, field, data[field])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
            
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
            
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
            
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/upload-avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """Upload user avatar"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'avatar' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['avatar']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, GIF, and WEBP are allowed'}), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{user.id}_{uuid.uuid4().hex}_{filename}"
        
        # Save file
        upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'avatars')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Update user profile
        user.profile_picture_url = f"/uploads/avatars/{unique_filename}"
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Avatar uploaded successfully',
            'avatar_url': user.profile_picture_url
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/attempts/history', methods=['GET'])
@jwt_required()
def get_attempts_history():
    """Get user's test attempt history"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        test_type = request.args.get('type', 'all')  # 'all', 'mock', 'practice'
        
        # Get mock attempts
        mock_attempts = []
        if test_type in ['all', 'mock']:
            mock_query = UGCNetMockAttempt.query.filter_by(
                user_id=user.id, is_completed=True
            ).order_by(desc(UGCNetMockAttempt.completed_at))
            
            for attempt in mock_query.all():
                mock_attempts.append({
                    'type': 'mock',
                    'data': attempt.to_dict(),
                    'completed_at': attempt.completed_at
                })
        
        # Get practice attempts
        practice_attempts = []
        if test_type in ['all', 'practice']:
            practice_query = UGCNetPracticeAttempt.query.filter_by(
                user_id=user.id, is_completed=True
            ).order_by(desc(UGCNetPracticeAttempt.completed_at))
            
            for attempt in practice_query.all():
                practice_attempts.append({
                    'type': 'practice',
                    'data': attempt.to_dict(),
                    'completed_at': attempt.completed_at
                })
        
        # Combine and sort all attempts
        all_attempts = mock_attempts + practice_attempts
        all_attempts.sort(key=lambda x: x['completed_at'], reverse=True)
        
        # Manual pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_attempts = all_attempts[start:end]
        
        total_attempts = len(all_attempts)
        total_pages = (total_attempts + per_page - 1) // per_page
        
        return jsonify({
            'attempts': paginated_attempts,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_attempts,
                'pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Legacy endpoint compatibility

