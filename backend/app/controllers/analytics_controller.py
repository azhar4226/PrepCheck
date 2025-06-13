from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db, redis_client
from app.models import User, Subject, Chapter, Quiz, Question, QuizAttempt
import json

analytics_bp = Blueprint('analytics', __name__)

def admin_required():
    """Check if current user is admin"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    return user and user.is_admin

@analytics_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_analytics_overview():
    """Get comprehensive analytics overview"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        # Time period filters
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Basic stats
        stats = {
            'total_users': User.query.filter_by(is_admin=False).count(),
            'active_users': User.query.filter(
                User.is_admin == False,
                User.last_login >= start_date
            ).count(),
            'total_quizzes': Quiz.query.filter_by(is_active=True).count(),
            'total_attempts': QuizAttempt.query.filter_by(is_completed=True).count(),
            'recent_attempts': QuizAttempt.query.filter(
                QuizAttempt.is_completed == True,
                QuizAttempt.completed_at >= start_date
            ).count()
        }
        
        # Performance metrics
        performance = get_performance_metrics(start_date)
        
        # User engagement
        engagement = get_user_engagement_metrics(start_date)
        
        # Subject popularity
        subject_stats = get_subject_statistics(start_date)
        
        # Time-based analysis
        daily_stats = get_daily_statistics(start_date)
        
        return jsonify({
            'stats': stats,
            'performance': performance,
            'engagement': engagement,
            'subjects': subject_stats,
            'daily_trends': daily_stats,
            'period_days': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_performance_metrics(start_date):
    """Get performance-related metrics"""
    attempts = QuizAttempt.query.filter(
        QuizAttempt.is_completed == True,
        QuizAttempt.completed_at >= start_date
    ).all()
    
    if not attempts:
        return {
            'average_score': 0,
            'average_percentage': 0,
            'pass_rate': 0,
            'average_time': 0
        }
    
    total_score = sum(attempt.score for attempt in attempts)
    total_possible = sum(attempt.total_marks for attempt in attempts)
    average_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0
    
    # Pass rate (assuming 70% is passing)
    passed = len([a for a in attempts if (a.score / a.total_marks * 100) >= 70 if a.total_marks > 0])
    pass_rate = (passed / len(attempts) * 100) if attempts else 0
    
    # Average time
    total_time = sum(attempt.time_taken or 0 for attempt in attempts)
    average_time = total_time / len(attempts) if attempts else 0
    
    return {
        'average_score': round(total_score / len(attempts), 2),
        'average_percentage': round(average_percentage, 2),
        'pass_rate': round(pass_rate, 2),
        'average_time_minutes': round(average_time / 60, 2)
    }

def get_user_engagement_metrics(start_date):
    """Get user engagement statistics"""
    # Active users by day
    daily_active = db.session.query(
        func.date(User.last_login).label('date'),
        func.count(User.id).label('count')
    ).filter(
        User.is_admin == False,
        User.last_login >= start_date
    ).group_by(func.date(User.last_login)).all()
    
    # User retention
    total_users = User.query.filter_by(is_admin=False).count()
    active_users = User.query.filter(
        User.is_admin == False,
        User.last_login >= start_date
    ).count()
    
    retention_rate = (active_users / total_users * 100) if total_users > 0 else 0
    
    return {
        'daily_active_users': [
            {'date': str(record.date), 'count': record.count}
            for record in daily_active
        ],
        'retention_rate': round(retention_rate, 2),
        'total_registered': total_users,
        'active_users': active_users
    }

def get_subject_statistics(start_date):
    """Get subject-wise statistics"""
    # Quiz attempts by subject
    subject_stats = db.session.query(
        Subject.name.label('subject'),
        func.count(QuizAttempt.id).label('attempts'),
        func.avg(QuizAttempt.score * 100.0 / QuizAttempt.total_marks).label('avg_percentage')
    ).join(Chapter).join(Quiz).join(QuizAttempt).filter(
        QuizAttempt.is_completed == True,
        QuizAttempt.completed_at >= start_date
    ).group_by(Subject.id, Subject.name).all()
    
    return [
        {
            'subject': record.subject,
            'attempts': record.attempts,
            'average_percentage': round(record.avg_percentage or 0, 2)
        }
        for record in subject_stats
    ]

def get_daily_statistics(start_date):
    """Get daily trend statistics"""
    daily_attempts = db.session.query(
        func.date(QuizAttempt.completed_at).label('date'),
        func.count(QuizAttempt.id).label('attempts'),
        func.avg(QuizAttempt.score * 100.0 / QuizAttempt.total_marks).label('avg_score')
    ).filter(
        QuizAttempt.is_completed == True,
        QuizAttempt.completed_at >= start_date
    ).group_by(func.date(QuizAttempt.completed_at)).all()
    
    return [
        {
            'date': str(record.date),
            'attempts': record.attempts,
            'average_score': round(record.avg_score or 0, 2)
        }
        for record in daily_attempts
    ]

@analytics_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_analytics(user_id):
    """Get detailed analytics for a specific user"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        # Allow access if admin or requesting own data
        if not (current_user.is_admin or current_user_id == user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        user = User.query.get_or_404(user_id)
        
        # User's quiz history
        attempts = QuizAttempt.query.filter_by(
            user_id=user_id, is_completed=True
        ).order_by(desc(QuizAttempt.completed_at)).all()
        
        if not attempts:
            return jsonify({
                'user': user.to_dict(),
                'total_attempts': 0,
                'average_score': 0,
                'improvement_trend': [],
                'subject_performance': [],
                'weekly_activity': []
            }), 200
        
        # Calculate metrics
        total_score = sum(attempt.score for attempt in attempts)
        total_possible = sum(attempt.total_marks for attempt in attempts)
        average_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0
        
        # Improvement trend (last 10 attempts)
        recent_attempts = attempts[:10]
        improvement_trend = [
            {
                'attempt_number': len(recent_attempts) - i,
                'percentage': round((attempt.score / attempt.total_marks * 100), 2) if attempt.total_marks > 0 else 0,
                'date': attempt.completed_at.isoformat()
            }
            for i, attempt in enumerate(reversed(recent_attempts))
        ]
        
        # Subject performance
        subject_performance = {}
        for attempt in attempts:
            subject_name = attempt.quiz.chapter.subject.name
            if subject_name not in subject_performance:
                subject_performance[subject_name] = {
                    'attempts': 0,
                    'total_score': 0,
                    'total_possible': 0
                }
            
            subject_performance[subject_name]['attempts'] += 1
            subject_performance[subject_name]['total_score'] += attempt.score
            subject_performance[subject_name]['total_possible'] += attempt.total_marks
        
        subject_stats = [
            {
                'subject': subject,
                'attempts': data['attempts'],
                'average_percentage': round((data['total_score'] / data['total_possible'] * 100), 2) if data['total_possible'] > 0 else 0
            }
            for subject, data in subject_performance.items()
        ]
        
        # Weekly activity (last 4 weeks)
        four_weeks_ago = datetime.utcnow() - timedelta(weeks=4)
        weekly_attempts = QuizAttempt.query.filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.is_completed == True,
            QuizAttempt.completed_at >= four_weeks_ago
        ).all()
        
        weekly_activity = {}
        for attempt in weekly_attempts:
            week = attempt.completed_at.strftime('%Y-W%U')
            if week not in weekly_activity:
                weekly_activity[week] = 0
            weekly_activity[week] += 1
        
        return jsonify({
            'user': user.to_dict(),
            'total_attempts': len(attempts),
            'average_score': round(average_percentage, 2),
            'improvement_trend': improvement_trend,
            'subject_performance': subject_stats,
            'weekly_activity': [
                {'week': week, 'attempts': count}
                for week, count in sorted(weekly_activity.items())
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/quiz/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz_analytics(quiz_id):
    """Get detailed analytics for a specific quiz"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        quiz = Quiz.query.get_or_404(quiz_id)
        
        # Quiz attempts
        attempts = QuizAttempt.query.filter_by(
            quiz_id=quiz_id, is_completed=True
        ).all()
        
        if not attempts:
            return jsonify({
                'quiz': quiz.to_dict(),
                'total_attempts': 0,
                'average_score': 0,
                'question_analysis': []
            }), 200
        
        # Basic stats
        total_score = sum(attempt.score for attempt in attempts)
        total_possible = sum(attempt.total_marks for attempt in attempts)
        average_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0
        
        # Question-wise analysis
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        question_analysis = []
        
        for question in questions:
            correct_count = 0
            total_answered = 0
            
            for attempt in attempts:
                answers = json.loads(attempt.answers) if attempt.answers else {}
                if str(question.id) in answers:
                    total_answered += 1
                    if answers[str(question.id)] == question.correct_option:
                        correct_count += 1
            
            question_analysis.append({
                'question_id': question.id,
                'question_text': question.question_text[:100] + '...' if len(question.question_text) > 100 else question.question_text,
                'correct_percentage': round((correct_count / total_answered * 100), 2) if total_answered > 0 else 0,
                'total_answered': total_answered,
                'difficulty_rating': 'Easy' if (correct_count / total_answered * 100) > 80 else 'Medium' if (correct_count / total_answered * 100) > 60 else 'Hard' if total_answered > 0 else 'Unknown'
            })
        
        return jsonify({
            'quiz': quiz.to_dict(),
            'total_attempts': len(attempts),
            'average_score': round(average_percentage, 2),
            'pass_rate': round(len([a for a in attempts if (a.score / a.total_marks * 100) >= 70 if a.total_marks > 0]) / len(attempts) * 100, 2) if attempts else 0,
            'question_analysis': question_analysis
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
