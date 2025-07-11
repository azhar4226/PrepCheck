from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, timezone
from sqlalchemy import desc, func, distinct, cast, Date
from app import db, redis_client
from app.models import User, Subject, Chapter, QuestionBank, UGCNetMockTest, UGCNetMockAttempt, UGCNetPracticeAttempt
from app.services.user_profile_service import UserProfileService
import json
import traceback

user_bp = Blueprint('user', __name__)

# Initialize profile service
profile_service = UserProfileService()

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))

def calculate_study_streak(user_id):
    """Calculate the current study streak for a user using new models"""
    try:
        # Use func.date for cross-database compatibility
        mock_dates = db.session.query(
            func.date(UGCNetMockAttempt.completed_at).label('date')
        ).filter(
            UGCNetMockAttempt.user_id == user_id,
            UGCNetMockAttempt.is_completed == True
        ).distinct()
        
        practice_dates = db.session.query(
            func.date(UGCNetPracticeAttempt.completed_at).label('date')
        ).filter(
            UGCNetPracticeAttempt.user_id == user_id,
            UGCNetPracticeAttempt.is_completed == True
        ).distinct()
        
        # Combine both date queries
        all_dates = mock_dates.union(practice_dates).order_by(desc('date')).all()
        if not all_dates:
            return 0
        # Convert to list of dates
        def normalize_date(d):
            print(f'normalize_date got: {d} ({type(d)})')
            if isinstance(d, datetime):
                return d.date()
            if hasattr(d, 'isoformat'):
                # date or datetime
                return d
            if isinstance(d, str):
                try:
                    return datetime.strptime(d, '%Y-%m-%d').date()
                except Exception as e:
                    print(f'Failed to parse date string: {d}, error: {e}')
                    return None
            return d  # already a date
        dates = [normalize_date(date.date) for date in all_dates if normalize_date(date.date) is not None]
        if not dates:
            return 0
        
        # Remove any None values and sort descending (latest first)
        dates = [d for d in dates if d is not None]
        if not dates:
            return 0
        dates.sort(reverse=True)
        
        # Check if user studied today or yesterday (streak can continue)
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # If user hasn't studied today or yesterday, streak is broken
        if dates[0] is None or (dates[0] != today and dates[0] != yesterday):
            return 0
        
        # Count consecutive days
        streak = 1
        current_date = dates[0]
        
        for i in range(1, len(dates)):
            if dates[i] is None:
                continue
            expected_date = current_date - timedelta(days=1)
            if dates[i] == expected_date:
                streak += 1
                current_date = dates[i]
            else:
                break
        
        return streak
        
    except Exception as e:
        import traceback
        print(f"Error calculating study streak: {e}")
        traceback.print_exc()
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
        
        # Get all completed attempts (mock + practice)
        completed_mock_attempts = UGCNetMockAttempt.query.filter_by(user_id=user.id, is_completed=True).all()
        completed_practice_attempts = UGCNetPracticeAttempt.query.filter_by(user_id=user.id, is_completed=True).all()
        all_attempts = completed_mock_attempts + completed_practice_attempts

        # Hours studied: sum of all time_taken (in seconds), convert to hours
        total_seconds = sum([a.time_taken or 0 for a in all_attempts])
        hours_studied = round(total_seconds / 3600, 1)

        # Accuracy rate: total correct / total attempted
        total_correct = sum([a.correct_answers or 0 for a in all_attempts])
        total_questions = sum([a.total_questions or 0 for a in all_attempts])
        accuracy_rate = round((total_correct / total_questions) * 100, 1) if total_questions > 0 else 0.0

        # Last activity: most recent completed_at
        last_activity = None
        if all_attempts:
            last_activity = max([a.completed_at for a in all_attempts if a.completed_at is not None], default=None)

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
                'qualification_status': qualification_status,
                'hours_studied': hours_studied,
                'accuracy_rate': accuracy_rate,
                'last_activity': last_activity.isoformat() if last_activity else None
            },
            'recent_attempts': recent_attempts,
            'subjects': [subject.to_dict() for subject in subjects]
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        print(f"Error in get_user_dashboard: {e}")
        return jsonify({'error': str(e)}), 500

@user_bp.route('/subjects', methods=['GET'])
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
        print(f"[Analytics API] Returning analytics: {json.dumps(analytics, default=str)}")
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Profile Management
@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get current user's profile"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        profile = profile_service.get_user_profile(user.id)
        return jsonify({'user': profile}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """Update current user's profile"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        updated_profile = profile_service.update_user_profile(user.id, data)
        return jsonify({
            'message': 'Profile updated successfully',
            'user': updated_profile
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/profile/password', methods=['PUT'])
@jwt_required()
def change_user_password():
    """Change user's password"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        profile_service.change_user_password(user.id, current_password, new_password)
        return jsonify({'message': 'Password changed successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile/picture', methods=['POST'])
@jwt_required()
def upload_user_profile_picture():
    """Upload user profile picture"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
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


@user_bp.route('/profile/picture', methods=['DELETE'])
@jwt_required()
def remove_user_profile_picture():
    """Remove user profile picture"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        result = profile_service.remove_profile_picture(user.id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
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
                try:
                    mock_attempts.append({
                        'type': 'mock',
                        'data': attempt.to_dict(),
                        'completed_at': attempt.completed_at
                    })
                except Exception as e:
                    print(f"Error serializing mock attempt {attempt.id}: {e}")
                    traceback.print_exc()
        
        # Get practice attempts
        practice_attempts = []
        if test_type in ['all', 'practice']:
            practice_query = UGCNetPracticeAttempt.query.filter_by(
                user_id=user.id, is_completed=True
            ).order_by(desc(UGCNetPracticeAttempt.completed_at))
            
            for attempt in practice_query.all():
                try:
                    practice_attempts.append({
                        'type': 'practice',
                        'data': attempt.to_dict(),
                        'completed_at': attempt.completed_at
                    })
                except Exception as e:
                    print(f"Error serializing practice attempt {attempt.id}: {e}")
                    traceback.print_exc()
        
        # Combine and sort all attempts
        all_attempts = mock_attempts + practice_attempts
        def to_utc(dt):
            if dt is None:
                return datetime.min.replace(tzinfo=timezone.utc)
            if dt.tzinfo is None:
                # Assume naive datetimes are UTC
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        all_attempts.sort(
            key=lambda x: to_utc(x['completed_at']),
            reverse=True
        )
        
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
        print(f"Error in get_attempts_history: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/subjects/paper2', methods=['GET'])
@jwt_required()
def get_paper2_subjects():
    """Get only Paper 2 subjects for profile settings"""
    try:
        # Get only Paper 2 subjects (these are the elective subjects users can choose)
        subjects = Subject.query.filter_by(
            is_active=True, 
            paper_type=2
        ).all()
        
        subjects_data = []
        for subject in subjects:
            subject_dict = subject.to_dict()
            subjects_data.append(subject_dict)
        
        return jsonify(subjects_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

