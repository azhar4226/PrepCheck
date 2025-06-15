from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import desc
from app import db, redis_client
from app.models import User, Subject, Chapter, Quiz, Question, QuizAttempt
import json
import os

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
            # Continue without cache
        
        if cached_stats:
            try:
                return jsonify(json.loads(cached_stats)), 200
            except:
                print("Failed to parse cached data, regenerating...")
        
        print("Generating fresh analytics data...")
        
        # Basic counts with error handling
        try:
            total_users = User.query.filter_by(is_admin=False).count()
            total_subjects = Subject.query.filter_by(is_active=True).count()
            total_quizzes = Quiz.query.filter_by(is_active=True).count()
            total_questions = Question.query.count()
            total_attempts = QuizAttempt.query.filter_by(is_completed=True).count()
            active_users_today = User.query.filter(User.last_login >= datetime.utcnow().date()).count()
        except Exception as e:
            print(f"Error getting basic counts: {e}")
            # Provide defaults
            total_users = 0
            total_subjects = 0
            total_quizzes = 0
            total_questions = 0
            total_attempts = 0
            active_users_today = 0
        
        # Performance calculations with error handling
        average_score = 0
        pass_rate = 0
        average_time = 0
        
        try:
            completed_attempts = QuizAttempt.query.filter_by(is_completed=True).all()
            
            if completed_attempts:
                scores = [attempt.score for attempt in completed_attempts if attempt.score is not None]
                if scores:
                    average_score = round(sum(scores) / len(scores), 1)
                    pass_rate = round((len([s for s in scores if s >= 70]) / len(scores)) * 100, 1)
                
                # Calculate average time (in minutes)
                times = []
                for attempt in completed_attempts:
                    if attempt.started_at and attempt.completed_at:
                        time_diff = attempt.completed_at - attempt.started_at
                        times.append(time_diff.total_seconds() / 60)
                
                if times:
                    average_time = round(sum(times) / len(times), 1)
        except Exception as e:
            print(f"Error calculating performance: {e}")
        
        # Subject statistics with error handling
        subject_stats = []
        try:
            subjects = Subject.query.filter_by(is_active=True).all()
            
            for subject in subjects:
                try:
                    subject_attempts = db.session.query(QuizAttempt).join(Quiz).join(Chapter).filter(
                        Chapter.subject_id == subject.id,
                        QuizAttempt.is_completed == True
                    ).all()
                    
                    if subject_attempts:
                        subject_scores = [attempt.score for attempt in subject_attempts if attempt.score is not None]
                        if subject_scores:
                            avg_score = round(sum(subject_scores) / len(subject_scores), 1)
                            subject_stats.append({
                                'subject': subject.name,
                                'attempts': len(subject_attempts),
                                'average_percentage': avg_score
                            })
                except Exception as e:
                    print(f"Error processing subject {subject.name}: {e}")
                    continue
        except Exception as e:
            print(f"Error getting subject stats: {e}")
        
        # Recent top performers with error handling
        top_performers = []
        try:
            recent_attempts = QuizAttempt.query.filter_by(is_completed=True).filter(
                QuizAttempt.score >= 80
            ).order_by(desc(QuizAttempt.completed_at)).limit(10).all()
            
            for attempt in recent_attempts:
                try:
                    top_performers.append({
                        'id': attempt.id,
                        'user_name': attempt.user.full_name if attempt.user else 'Unknown',
                        'quiz_title': attempt.quiz.title if attempt.quiz else 'Unknown Quiz',
                        'percentage': attempt.score,
                        'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None
                    })
                except Exception as e:
                    print(f"Error processing top performer: {e}")
                    continue
        except Exception as e:
            print(f"Error getting top performers: {e}")
        
        # Calculate retention rate with error handling
        retention_rate = 0
        try:
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            active_users_30_days = db.session.query(User).join(QuizAttempt).filter(
                QuizAttempt.created_at >= thirty_days_ago,
                User.is_admin == False
            ).distinct().count()
            
            if total_users > 0:
                retention_rate = round((active_users_30_days / total_users) * 100, 1)
        except Exception as e:
            print(f"Error calculating retention rate: {e}")
        
        # Calculate recent attempts count
        recent_attempts_count = 0
        try:
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_attempts_count = QuizAttempt.query.filter(
                QuizAttempt.completed_at >= thirty_days_ago,
                QuizAttempt.is_completed == True
            ).count()
        except Exception as e:
            print(f"Error calculating recent attempts: {e}")
        
        # Calculate daily trends for the last 7 days
        daily_trends = []
        try:
            for i in range(6, -1, -1):  # Last 7 days
                date = datetime.utcnow().date() - timedelta(days=i)
                next_date = date + timedelta(days=1)
                
                # Count attempts for this day
                day_attempts = QuizAttempt.query.filter(
                    QuizAttempt.completed_at >= date,
                    QuizAttempt.completed_at < next_date,
                    QuizAttempt.is_completed == True
                ).count()
                
                # Calculate average score for this day
                day_scores = [attempt.score for attempt in QuizAttempt.query.filter(
                    QuizAttempt.completed_at >= date,
                    QuizAttempt.completed_at < next_date,
                    QuizAttempt.is_completed == True,
                    QuizAttempt.score != None
                ).all()]
                
                day_avg_score = round(sum(day_scores) / len(day_scores), 1) if day_scores else 0
                
                daily_trends.append({
                    'date': date.strftime('%b %d'),
                    'attempts': day_attempts,
                    'average_score': day_avg_score
                })
        except Exception as e:
            print(f"Error calculating daily trends: {e}")
            # Provide fallback data
            for i in range(6, -1, -1):
                date = datetime.utcnow().date() - timedelta(days=i)
                daily_trends.append({
                    'date': date.strftime('%b %d'),
                    'attempts': 0,
                    'average_score': 0
                })
        
        stats = {
            'total_users': total_users,
            'total_subjects': total_subjects,
            'total_quizzes': total_quizzes,
            'total_questions': total_questions,
            'total_attempts': total_attempts,
            'active_users': active_users_today,
            'recent_attempts': recent_attempts_count,
            'average_score': average_score,
            'pass_rate': pass_rate,
            'average_time': average_time,
            'retention_rate': retention_rate,
            'subject_stats': subject_stats,
            'top_performers': top_performers,
            'daily_trends': daily_trends
        }
        
        print(f"Generated stats: {stats}")
        
        # Cache for 5 minutes with error handling
        try:
            if redis_client:
                redis_client.setex(cache_key, 300, json.dumps(stats, default=str))
        except Exception as redis_error:
            print(f"Redis cache set error: {redis_error}")
            # Continue without caching
        
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"Dashboard stats error: {e}")
        import traceback
        traceback.print_exc()
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
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        chapter_id = request.args.get('chapter_id', type=int)
        
        query = Quiz.query
        
        if chapter_id:
            query = query.filter_by(chapter_id=chapter_id)
        
        # Get paginated results
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        quizzes_data = []
        for quiz in pagination.items:
            quiz_dict = quiz.to_dict()
            # Add related data for better filtering
            if quiz.chapter:
                quiz_dict['chapter_name'] = quiz.chapter.name
                if quiz.chapter.subject:
                    quiz_dict['subject_id'] = quiz.chapter.subject.id
                    quiz_dict['subject_name'] = quiz.chapter.subject.name
            quizzes_data.append(quiz_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'quizzes': quizzes_data,
                'total_pages': pagination.pages,
                'current_page': page,
                'total_items': pagination.total,
                'per_page': per_page
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent deletion of admin users
        if user.is_admin:
            return jsonify({'error': 'Cannot delete admin users'}), 400
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
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
        
        # Run export task synchronously for now
        result = export_admin_data(export_type)
        
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

# Admin Profile Management

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))

@admin_bp.route('/profile', methods=['GET'])
@admin_required
def get_admin_profile():
    """Get current admin's profile"""
    try:
        user = get_current_user()
        return jsonify({'admin': user.to_dict()}), 200
        
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
        
        # Validate email uniqueness if changed
        if 'email' in data and data['email'] != user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'error': 'Email already exists'}), 400
        
        # Update allowed fields (admins can update more fields)
        updatable_fields = [
            'email', 'full_name', 'phone', 'bio', 'date_of_birth', 
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
            'message': 'Admin profile updated successfully',
            'admin': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
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

# Enhanced User Management for Admins

@admin_bp.route('/users/<int:user_id>/profile', methods=['PUT'])
@admin_required
def update_user_profile_by_admin(user_id):
    """Update any user's profile (admin only)"""
    try:
        user = User.query.get(user_id)
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
        
        # Admin can update all fields including admin status
        updatable_fields = [
            'email', 'full_name', 'phone', 'bio', 'date_of_birth', 
            'gender', 'country', 'timezone', 'is_admin', 'is_active',
            'notification_email', 'notification_quiz_reminders', 'theme_preference',
            'email_verified'
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
        
        # Update password if provided
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'error': 'Password must be at least 6 characters long'}), 400
            user.set_password(data['password'])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'User profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/create', methods=['POST'])
@admin_required
def create_user_by_admin():
    """Create a new user (admin only)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['email', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            full_name=data['full_name'],
            is_admin=data.get('is_admin', False),
            is_active=data.get('is_active', True),
            phone=data.get('phone'),
            bio=data.get('bio'),
            gender=data.get('gender'),
            country=data.get('country'),
            timezone=data.get('timezone', 'UTC'),
            email_verified=data.get('email_verified', False)
        )
        user.set_password(data['password'])
        
        if data.get('date_of_birth'):
            try:
                user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# System Settings Management

@admin_bp.route('/settings', methods=['GET'])
@admin_required
def get_system_settings():
    """Get system settings"""
    try:
        # This could be extended to include actual system settings from a settings table
        settings = {
            'app_name': 'PrepCheck',
            'version': '1.0.0',
            'max_file_size': '5MB',
            'allowed_extensions': ['png', 'jpg', 'jpeg', 'gif', 'webp'],
            'maintenance_mode': False,
            'registration_enabled': True,
            'email_verification_required': False,
            'max_quiz_time': 120,  # minutes
            'default_questions_per_quiz': 10,
            'password_min_length': 6
        }
        
        return jsonify({'settings': settings}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/download/<filename>', methods=['GET'])
@admin_required
def download_export_file(filename):
    """Download exported files"""
    try:
        from flask import send_from_directory, abort
        
        # Security: Only allow files from exports directory and validate filename
        export_dir = os.path.join(os.getcwd(), 'exports')
        
        # Validate filename to prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            abort(400)
            
        # Check if file exists
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
