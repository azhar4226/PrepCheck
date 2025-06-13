from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import desc
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

@user_bp.route('/export', methods=['POST'])
@jwt_required()
def export_user_history():
    try:
        user = get_current_user()
        
        # Import here to avoid circular import
        from app.tasks.export_tasks import export_user_data
        
        # Start async task
        task = export_user_data.delay(user.id)
        
        return jsonify({
            'message': 'Export started',
            'task_id': task.id
        }), 202
        
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
