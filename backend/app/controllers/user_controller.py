from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import desc
from werkzeug.utils import secure_filename
import os
import uuid
from app import db, redis_client
from app.models import User, Subject, Chapter, Quiz, Question, QuizAttempt
import json

user_bp = Blueprint('user', __name__)

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))

@user_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_user_dashboard():
    try:
        user = get_current_user()
        if not user or not user.is_active:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's quiz statistics
        total_attempts = QuizAttempt.query.filter_by(user_id=user.id, is_completed=True).count()
        
        # Recent attempts
        recent_attempts = QuizAttempt.query.filter_by(
            user_id=user.id, is_completed=True
        ).order_by(desc(QuizAttempt.completed_at)).limit(5).all()
        
        # Average score
        completed_attempts = QuizAttempt.query.filter_by(
            user_id=user.id, is_completed=True
        ).all()
        
        avg_score = 0
        if completed_attempts:
            total_percentage = sum(
                (attempt.score / attempt.total_marks) * 100 
                for attempt in completed_attempts 
                if attempt.total_marks > 0
            )
            avg_score = round(total_percentage / len(completed_attempts), 2)
        
        # Available subjects
        subjects = Subject.query.filter_by(is_active=True).all()
        
        dashboard_data = {
            'user': user.to_dict(),
            'stats': {
                'total_attempts': total_attempts,
                'average_score': avg_score,
                'subjects_available': len(subjects)
            },
            'recent_attempts': [attempt.to_dict() for attempt in recent_attempts],
            'subjects': [subject.to_dict() for subject in subjects]
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/subjects', methods=['GET'])
@jwt_required()
def get_user_subjects():
    try:
        # Check cache first
        cache_key = 'user_subjects'
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
            # Add chapters with quiz counts
            chapters_data = []
            for chapter in subject.chapters:
                if chapter.is_active:
                    chapter_dict = chapter.to_dict()
                    chapters_data.append(chapter_dict)
            
            subject_dict['chapters'] = chapters_data
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
    try:
        subject = Subject.query.get_or_404(subject_id)
        if not subject.is_active:
            return jsonify({'error': 'Subject not available'}), 404
        
        chapters = Chapter.query.filter_by(
            subject_id=subject_id, is_active=True
        ).all()
        
        return jsonify({
            'subject': subject.to_dict(),
            'chapters': [chapter.to_dict() for chapter in chapters]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/quizzes/<int:chapter_id>', methods=['GET'])
@jwt_required()
def get_user_quizzes(chapter_id):
    try:
        chapter = Chapter.query.get_or_404(chapter_id)
        if not chapter.is_active:
            return jsonify({'error': 'Chapter not available'}), 404
        
        quizzes = Quiz.query.filter_by(
            chapter_id=chapter_id, is_active=True
        ).all()
        
        user = get_current_user()
        quizzes_data = []
        
        for quiz in quizzes:
            quiz_dict = quiz.to_dict()
            # Add user's attempt history for this quiz
            attempts = QuizAttempt.query.filter_by(
                user_id=user.id, quiz_id=quiz.id, is_completed=True
            ).count()
            quiz_dict['user_attempts'] = attempts
            
            # Best score
            best_attempt = QuizAttempt.query.filter_by(
                user_id=user.id, quiz_id=quiz.id, is_completed=True
            ).order_by(QuizAttempt.score.desc()).first()  # type: ignore
            
            quiz_dict['best_score'] = best_attempt.score if best_attempt else 0
            quiz_dict['best_percentage'] = (
                round((best_attempt.score / best_attempt.total_marks) * 100, 2) 
                if best_attempt and best_attempt.total_marks > 0 else 0
            )
            
            quizzes_data.append(quiz_dict)
        
        return jsonify({
            'chapter': chapter.to_dict(),
            'quizzes': quizzes_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/history', methods=['GET'])
@jwt_required()
def get_user_history():
    try:
        user = get_current_user()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        attempts = QuizAttempt.query.filter_by(
            user_id=user.id, is_completed=True
        ).order_by(desc(QuizAttempt.completed_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'attempts': [attempt.to_dict() for attempt in attempts.items],
            'total': attempts.total,
            'pages': attempts.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_user_progress():
    """Get user's learning progress over time"""
    try:
        user = get_current_user()
        if not user or not user.is_active:
            return jsonify({'error': 'User not found'}), 404
        
        # Get completed attempts ordered by date
        attempts = QuizAttempt.query.filter_by(
            user_id=user.id, is_completed=True
        ).order_by(QuizAttempt.completed_at).all()
        
        # Build progress data
        progress_data = []
        for attempt in attempts:
            if attempt.total_marks > 0:
                percentage = round((attempt.score / attempt.total_marks) * 100, 2)
                progress_data.append({
                    'date': attempt.completed_at.strftime('%Y-%m-%d'),
                    'score': attempt.score,
                    'total_marks': attempt.total_marks,
                    'percentage': percentage,
                    'quiz_title': attempt.quiz.title if attempt.quiz else 'Unknown Quiz'
                })
        
        return jsonify({
            'progress': progress_data,
            'total_attempts': len(progress_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/export', methods=['POST'])
@jwt_required()
def export_user_history():
    try:
        user = get_current_user()
        
        # Import here to avoid circular import
        from app.tasks.export_tasks import export_user_data
        
        # Run export task synchronously for now
        result = export_user_data(user.id)
        
        if result['status'] == 'success':
            return jsonify({
                'message': result['message'],
                'files_created': result['files_created']
            }), 200
        else:
            return jsonify({
                'message': 'Export failed',
                'error': result['error']
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/export/<task_id>', methods=['GET'])
@jwt_required()
def get_user_export_status(task_id):
    try:
        from app import celery_app
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {'state': task.state, 'status': 'Task is waiting...'}
        elif task.state == 'PROGRESS':
            response = {
                'state': task.state,
                'status': task.info.get('status', ''),
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1)
            }
        elif task.state == 'SUCCESS':
            response = {
                'state': task.state,
                'download_url': task.result
            }
        else:  # FAILURE
            response = {
                'state': task.state,
                'error': str(task.info)
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Profile Management Endpoints

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile"""
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
            'email', 'full_name', 'phone', 'bio', 'date_of_birth', 
            'gender', 'country', 'timezone', 'notification_email',
            'notification_quiz_reminders', 'theme_preference'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'date_of_birth' and data[field]:
                    # Convert date string to date object
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

@user_bp.route('/profile/password', methods=['PUT'])
@jwt_required()
def change_password():
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

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/profile/picture', methods=['POST'])
@jwt_required()
def upload_profile_picture():
    """Upload profile picture"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
            
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large. Maximum size is 5MB'}), 400
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'profile_pictures')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        if file.filename:
            file_extension = file.filename.rsplit('.', 1)[1].lower()
        else:
            file_extension = 'jpg'  # default extension
        unique_filename = f"{user.id}_{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Delete old profile picture if exists
        if user.profile_picture_url:
            old_filename = user.profile_picture_url.split('/')[-1]
            old_file_path = os.path.join(upload_dir, old_filename)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        
        # Save new file
        file.save(file_path)
        
        # Update user profile
        user.profile_picture_url = f"/uploads/profile_pictures/{unique_filename}"
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile picture uploaded successfully',
            'profile_picture_url': user.profile_picture_url
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile/picture', methods=['DELETE'])
@jwt_required()
def delete_profile_picture():
    """Delete profile picture"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        if not user.profile_picture_url:
            return jsonify({'error': 'No profile picture to delete'}), 400
            
        # Delete file from filesystem
        upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'profile_pictures')
        filename = user.profile_picture_url.split('/')[-1]
        file_path = os.path.join(upload_dir, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Update user profile
        user.profile_picture_url = None
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Profile picture deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download_user_export_file(filename):
    """Download user export files"""
    try:
        import os
        from flask import send_from_directory, abort
        
        user = get_current_user()
        export_dir = os.path.join(os.getcwd(), 'exports')
        
        # Security: Validate filename and ensure it belongs to this user
        if '..' in filename or '/' in filename or '\\' in filename:
            abort(400)
            
        # Check if file exists and belongs to this user
        if not filename.startswith(f'user_{user.id}_'):
            return jsonify({'error': 'Access denied'}), 403
            
        file_path = os.path.join(export_dir, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
            
        # Determine mimetype based on extension
        if filename.endswith('.pdf'):
            mimetype = 'application/pdf'
        elif filename.endswith('.csv'):
            mimetype = 'text/csv'
        elif filename.endswith('.json'):
            mimetype = 'application/json'
        else:
            mimetype = 'application/octet-stream'
            
        return send_from_directory(
            export_dir, 
            filename, 
            as_attachment=True,
            mimetype=mimetype
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
