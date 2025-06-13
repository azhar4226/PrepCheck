from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from datetime import datetime
from sqlalchemy import desc
from app import db, redis_client
from app.models import User, Subject, Chapter, Quiz, Question, QuizAttempt
import json

admin_bp = Blueprint('admin', __name__)

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

# Dashboard Statistics
@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_stats():
    try:
        # Check cache first
        cache_key = 'admin_dashboard_stats'
        cached_stats = None
        
        # Safe Redis operation with error handling
        try:
            if redis_client:
                cached_stats = redis_client.get(cache_key)
        except Exception as redis_error:
            print(f"Redis cache error: {redis_error}")
        
        if cached_stats:
            return jsonify(json.loads(cached_stats)), 200
        
        # Calculate statistics
        stats = {
            'total_users': User.query.filter_by(is_admin=False).count(),
            'total_subjects': Subject.query.filter_by(is_active=True).count(),
            'total_quizzes': Quiz.query.filter_by(is_active=True).count(),
            'total_questions': Question.query.count(),
            'total_attempts': QuizAttempt.query.filter_by(is_completed=True).count(),
            'active_users_today': User.query.filter(User.last_login >= datetime.utcnow().date()).count(),
            'recent_attempts': [attempt.to_dict() for attempt in 
                              QuizAttempt.query.filter_by(is_completed=True)
                              .order_by(desc(QuizAttempt.completed_at)).limit(10).all()]
        }
        
        # Cache for 5 minutes with error handling
        try:
            if redis_client:
                redis_client.setex(cache_key, 300, json.dumps(stats))
        except Exception as redis_error:
            print(f"Redis cache set error: {redis_error}")
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Subject Management
@admin_bp.route('/subjects', methods=['GET'])
@admin_required
def get_subjects():
    try:
        subjects = Subject.query.all()
        return jsonify([subject.to_dict() for subject in subjects]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subjects', methods=['POST'])
@admin_required
def create_subject():
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Subject name required'}), 400
        
        # Check if subject already exists
        if Subject.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Subject already exists'}), 400
        
        subject = Subject(
            name=data['name'],
            description=data.get('description', '')
        )
        
        db.session.add(subject)
        db.session.commit()
        
        # Clear cache with error handling
        try:
            if redis_client:
                redis_client.delete('admin_dashboard_stats')
        except Exception as redis_error:
            print(f"Redis cache delete error: {redis_error}")
        
        return jsonify({
            'message': 'Subject created successfully',
            'subject': subject.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@admin_required
def update_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        data = request.get_json()
        
        if 'name' in data:
            # Check if name already exists (excluding current subject)
            existing = Subject.query.filter(Subject.name == data['name'], Subject.id != subject_id).first()
            if existing:
                return jsonify({'error': 'Subject name already exists'}), 400
            subject.name = data['name']
        
        if 'description' in data:
            subject.description = data['description']
        
        if 'is_active' in data:
            subject.is_active = data['is_active']
        
        db.session.commit()
        
        # Clear cache with error handling
        try:
            if redis_client:
                redis_client.delete('admin_dashboard_stats')
        except Exception as redis_error:
            print(f"Redis cache delete error: {redis_error}")
        
        return jsonify({
            'message': 'Subject updated successfully',
            'subject': subject.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@admin_required
def delete_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        # Check if subject has chapters
        if subject.chapters:
            return jsonify({'error': 'Cannot delete subject with existing chapters'}), 400
        
        db.session.delete(subject)
        db.session.commit()
        
        # Clear cache with error handling
        try:
            if redis_client:
                redis_client.delete('admin_dashboard_stats')
        except Exception as redis_error:
            print(f"Redis cache delete error: {redis_error}")
        
        return jsonify({'message': 'Subject deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Chapter Management
@admin_bp.route('/chapters', methods=['GET'])
@admin_required
def get_chapters():
    try:
        subject_id = request.args.get('subject_id', type=int)
        
        if subject_id:
            chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        else:
            chapters = Chapter.query.all()
        
        return jsonify([chapter.to_dict() for chapter in chapters]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/chapters', methods=['POST'])
@admin_required
def create_chapter():
    try:
        data = request.get_json()
        
        required_fields = ['name', 'subject_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify subject exists
        subject = Subject.query.get(data['subject_id'])
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        chapter = Chapter(
            name=data['name'],
            description=data.get('description', ''),
            subject_id=data['subject_id']
        )
        
        db.session.add(chapter)
        db.session.commit()
        
        return jsonify({
            'message': 'Chapter created successfully',
            'chapter': chapter.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Quiz Management
@admin_bp.route('/quizzes', methods=['GET'])
@admin_required
def get_quizzes():
    try:
        chapter_id = request.args.get('chapter_id', type=int)
        
        if chapter_id:
            quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        else:
            quizzes = Quiz.query.all()
        
        return jsonify([quiz.to_dict() for quiz in quizzes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/quizzes', methods=['POST'])
@admin_required
def create_quiz():
    try:
        data = request.get_json()
        
        required_fields = ['title', 'chapter_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify chapter exists
        chapter = Chapter.query.get(data['chapter_id'])
        if not chapter:
            return jsonify({'error': 'Chapter not found'}), 404
        
        quiz = Quiz(
            title=data['title'],
            description=data.get('description', ''),
            chapter_id=data['chapter_id'],
            time_limit=data.get('time_limit', 60),
            is_ai_generated=data.get('is_ai_generated', False)
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        return jsonify({
            'message': 'Quiz created successfully',
            'quiz': quiz.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Question Management
@admin_bp.route('/questions', methods=['POST'])
@admin_required
def create_question():
    try:
        data = request.get_json()
        
        required_fields = ['quiz_id', 'question_text', 'option_a', 'option_b', 
                          'option_c', 'option_d', 'correct_option']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify quiz exists
        quiz = Quiz.query.get(data['quiz_id'])
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Validate correct option
        if data['correct_option'].upper() not in ['A', 'B', 'C', 'D']:
            return jsonify({'error': 'Correct option must be A, B, C, or D'}), 400
        
        question = Question(
            quiz_id=data['quiz_id'],
            question_text=data['question_text'],
            option_a=data['option_a'],
            option_b=data['option_b'],
            option_c=data['option_c'],
            option_d=data['option_d'],
            correct_option=data['correct_option'].upper(),
            explanation=data.get('explanation', ''),
            marks=data.get('marks', 1)
        )
        
        db.session.add(question)
        db.session.commit()
        
        # Update quiz total marks
        quiz.update_total_marks()
        
        return jsonify({
            'message': 'Question created successfully',
            'question': question.to_dict(include_answer=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/questions/<int:quiz_id>', methods=['GET'])
@admin_required
def get_quiz_questions(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        return jsonify({
            'quiz': quiz.to_dict(),
            'questions': [q.to_dict(include_answer=True) for q in questions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Management
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = User.query.filter_by(is_admin=False).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Export Data
@admin_bp.route('/export', methods=['POST'])
@admin_required
def export_data():
    try:
        data = request.get_json()
        export_type = data.get('type', 'all')  # 'users', 'quizzes', 'attempts', 'all'
        
        # Import task dynamically to avoid circular imports
        from app.tasks.export_tasks import export_admin_data
        
        # Start async task
        task = export_admin_data.delay(export_type)
        
        return jsonify({
            'message': 'Export started',
            'task_id': task.id
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/export/<task_id>', methods=['GET'])
@admin_required
def get_export_status(task_id):
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
