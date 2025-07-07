from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db, redis_client
from app.models import User, Subject, Chapter, QuestionBank, UGCNetMockTest, UGCNetMockAttempt, UGCNetPracticeAttempt
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
    """Get comprehensive analytics overview using UGC NET models"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        # Time period filters
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Basic stats using new models
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
            'total_practice_attempts': UGCNetPracticeAttempt.query.filter_by(is_completed=True).count(),
            'recent_mock_attempts': UGCNetMockAttempt.query.filter(
                UGCNetMockAttempt.is_completed == True,
                UGCNetMockAttempt.completed_at >= start_date
            ).count(),
            'recent_practice_attempts': UGCNetPracticeAttempt.query.filter(
                UGCNetPracticeAttempt.is_completed == True,
                UGCNetPracticeAttempt.completed_at >= start_date
            ).count()
        }
        
        # Performance metrics
        performance = get_performance_metrics(start_date)
        
        # User engagement
        engagement = get_user_engagement_metrics(start_date)
        
        # Subject popularity
        subject_popularity = get_subject_popularity(start_date)
        
        return jsonify({
            'stats': stats,
            'performance': performance,
            'engagement': engagement,
            'subject_popularity': subject_popularity,
            'period_days': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_performance_metrics(start_date):
    """Get performance metrics from UGC NET attempts"""
    try:
        # Mock test performance
        mock_attempts = UGCNetMockAttempt.query.filter(
            UGCNetMockAttempt.is_completed == True,
            UGCNetMockAttempt.completed_at >= start_date
        ).all()
        
        mock_scores = [attempt.percentage for attempt in mock_attempts if attempt.percentage is not None]
        
        # Practice test performance
        practice_attempts = UGCNetPracticeAttempt.query.filter(
            UGCNetPracticeAttempt.is_completed == True,
            UGCNetPracticeAttempt.completed_at >= start_date
        ).all()
        
        practice_scores = [attempt.percentage for attempt in practice_attempts if attempt.percentage is not None]
        
        # Calculate metrics
        avg_mock_score = round(sum(mock_scores) / len(mock_scores), 2) if mock_scores else 0
        avg_practice_score = round(sum(practice_scores) / len(practice_scores), 2) if practice_scores else 0
        
        # Pass rates (UGC NET: 40%, Practice: 60%)
        mock_pass_rate = round((len([s for s in mock_scores if s >= 40]) / len(mock_scores)) * 100, 2) if mock_scores else 0
        practice_pass_rate = round((len([s for s in practice_scores if s >= 60]) / len(practice_scores)) * 100, 2) if practice_scores else 0
        
        # Average time calculation
        mock_times = []
        for attempt in mock_attempts:
            if attempt.start_time and attempt.end_time:
                time_diff = attempt.end_time - attempt.start_time
                mock_times.append(time_diff.total_seconds() / 60)
        
        practice_times = []
        for attempt in practice_attempts:
            if attempt.start_time and attempt.end_time:
                time_diff = attempt.end_time - attempt.start_time
                practice_times.append(time_diff.total_seconds() / 60)
        
        avg_mock_time = round(sum(mock_times) / len(mock_times), 1) if mock_times else 0
        avg_practice_time = round(sum(practice_times) / len(practice_times), 1) if practice_times else 0
        
        return {
            'mock_tests': {
                'average_score': avg_mock_score,
                'pass_rate': mock_pass_rate,
                'average_time_minutes': avg_mock_time,
                'total_attempts': len(mock_attempts)
            },
            'practice_tests': {
                'average_score': avg_practice_score,
                'pass_rate': practice_pass_rate,
                'average_time_minutes': avg_practice_time,
                'total_attempts': len(practice_attempts)
            },
            'overall': {
                'average_score': round((avg_mock_score + avg_practice_score) / 2, 2) if (avg_mock_score > 0 or avg_practice_score > 0) else 0,
                'total_attempts': len(mock_attempts) + len(practice_attempts)
            }
        }
        
    except Exception as e:
        print(f"Error getting performance metrics: {e}")
        return {
            'mock_tests': {'average_score': 0, 'pass_rate': 0, 'average_time_minutes': 0, 'total_attempts': 0},
            'practice_tests': {'average_score': 0, 'pass_rate': 0, 'average_time_minutes': 0, 'total_attempts': 0},
            'overall': {'average_score': 0, 'total_attempts': 0}
        }

def get_user_engagement_metrics(start_date):
    """Get user engagement metrics"""
    try:
        total_users = User.query.filter_by(is_admin=False).count()
        
        # Users who made attempts in the period
        users_with_mock_attempts = db.session.query(UGCNetMockAttempt.user_id).filter(
            UGCNetMockAttempt.started_at >= start_date
        ).distinct().count()
        
        users_with_practice_attempts = db.session.query(UGCNetPracticeAttempt.user_id).filter(
            UGCNetPracticeAttempt.started_at >= start_date
        ).distinct().count()
        
        # Active users (users who made any attempt)
        active_users = db.session.query(
            db.union(
                db.session.query(UGCNetMockAttempt.user_id).filter(UGCNetMockAttempt.started_at >= start_date),
                db.session.query(UGCNetPracticeAttempt.user_id).filter(UGCNetPracticeAttempt.started_at >= start_date)
            )
        ).distinct().count()
        
        # Daily active users (last 7 days)
        daily_active = []
        for i in range(7):
            day_start = datetime.utcnow().date() - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            daily_mock_users = db.session.query(UGCNetMockAttempt.user_id).filter(
                UGCNetMockAttempt.started_at >= day_start,
                UGCNetMockAttempt.started_at < day_end
            ).distinct().count()
            
            daily_practice_users = db.session.query(UGCNetPracticeAttempt.user_id).filter(
                UGCNetPracticeAttempt.started_at >= day_start,
                UGCNetPracticeAttempt.started_at < day_end
            ).distinct().count()
            
            daily_active.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'active_users': daily_mock_users + daily_practice_users
            })
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'users_with_mock_attempts': users_with_mock_attempts,
            'users_with_practice_attempts': users_with_practice_attempts,
            'engagement_rate': round((active_users / total_users) * 100, 2) if total_users > 0 else 0,
            'daily_active_users': daily_active
        }
        
    except Exception as e:
        print(f"Error getting engagement metrics: {e}")
        return {
            'total_users': 0,
            'active_users': 0,
            'users_with_mock_attempts': 0,
            'users_with_practice_attempts': 0,
            'engagement_rate': 0,
            'daily_active_users': []
        }

def get_subject_popularity(start_date):
    """Get subject popularity metrics"""
    try:
        subjects = Subject.query.filter_by(is_active=True).all()
        subject_data = []
        
        for subject in subjects:
            # Mock test attempts for this subject
            mock_attempts = db.session.query(UGCNetMockAttempt).join(UGCNetMockTest).filter(
                UGCNetMockTest.subject_id == subject.id,
                UGCNetMockAttempt.started_at >= start_date
            ).count()
            
            # Practice test attempts for this subject
            practice_attempts = UGCNetPracticeAttempt.query.filter(
                UGCNetPracticeAttempt.subject_id == subject.id,
                UGCNetPracticeAttempt.started_at >= start_date
            ).count()
            
            total_attempts = mock_attempts + practice_attempts
            
            if total_attempts > 0:
                subject_data.append({
                    'subject_name': subject.name,
                    'subject_id': subject.id,
                    'mock_attempts': mock_attempts,
                    'practice_attempts': practice_attempts,
                    'total_attempts': total_attempts,
                    'questions_count': QuestionBank.query.join(Chapter).filter(
                        Chapter.subject_id == subject.id
                    ).count()
                })
        
        # Sort by total attempts
        subject_data.sort(key=lambda x: x['total_attempts'], reverse=True)
        
        return subject_data
        
    except Exception as e:
        print(f"Error getting subject popularity: {e}")
        return []

@analytics_bp.route('/users', methods=['GET'])
@jwt_required()
def get_user_analytics():
    """Get user-specific analytics"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get top performers
        top_performers = get_top_performers(start_date, limit=10)
        
        # Get user registration trends
        registration_trends = get_registration_trends(days)
        
        # Get user activity distribution
        activity_distribution = get_user_activity_distribution(start_date)
        
        return jsonify({
            'top_performers': top_performers,
            'registration_trends': registration_trends,
            'activity_distribution': activity_distribution,
            'period_days': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_top_performers(start_date, limit=10):
    """Get top performing users"""
    try:
        # Get users with their average scores
        user_performance = {}
        
        # Mock test scores
        mock_attempts = UGCNetMockAttempt.query.filter(
            UGCNetMockAttempt.is_completed == True,
            UGCNetMockAttempt.completed_at >= start_date
        ).all()
        
        for attempt in mock_attempts:
            if attempt.user_id not in user_performance:
                user_performance[attempt.user_id] = {
                    'user': attempt.user,
                    'mock_scores': [],
                    'practice_scores': []
                }
            if attempt.percentage is not None:
                user_performance[attempt.user_id]['mock_scores'].append(attempt.percentage)
        
        # Practice test scores
        practice_attempts = UGCNetPracticeAttempt.query.filter(
            UGCNetPracticeAttempt.is_completed == True,
            UGCNetPracticeAttempt.completed_at >= start_date
        ).all()
        
        for attempt in practice_attempts:
            if attempt.user_id not in user_performance:
                user_performance[attempt.user_id] = {
                    'user': attempt.user,
                    'mock_scores': [],
                    'practice_scores': []
                }
            if attempt.percentage is not None:
                user_performance[attempt.user_id]['practice_scores'].append(attempt.percentage)
        
        # Calculate averages and create list
        performers = []
        for user_id, data in user_performance.items():
            all_scores = data['mock_scores'] + data['practice_scores']
            if all_scores:
                avg_score = sum(all_scores) / len(all_scores)
                performers.append({
                    'user_id': user_id,
                    'user_name': data['user'].full_name if data['user'] else 'Unknown',
                    'user_email': data['user'].email if data['user'] else 'Unknown',
                    'average_score': round(avg_score, 2),
                    'total_attempts': len(all_scores),
                    'mock_attempts': len(data['mock_scores']),
                    'practice_attempts': len(data['practice_scores'])
                })
        
        # Sort by average score and return top performers
        performers.sort(key=lambda x: x['average_score'], reverse=True)
        return performers[:limit]
        
    except Exception as e:
        print(f"Error getting top performers: {e}")
        return []

def get_registration_trends(days):
    """Get user registration trends"""
    try:
        trends = []
        for i in range(days - 1, -1, -1):
            date = datetime.utcnow().date() - timedelta(days=i)
            next_date = date + timedelta(days=1)
            
            registrations = User.query.filter(
                User.created_at >= date,
                User.created_at < next_date,
                User.is_admin == False
            ).count()
            
            trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'registrations': registrations
            })
        
        return trends
        
    except Exception as e:
        print(f"Error getting registration trends: {e}")
        return []

def get_user_activity_distribution(start_date):
    """Get distribution of user activity levels"""
    try:
        # Categorize users by activity level
        all_users = User.query.filter_by(is_admin=False).all()
        
        inactive_users = 0  # No attempts
        low_activity = 0    # 1-5 attempts
        medium_activity = 0 # 6-20 attempts
        high_activity = 0   # 21+ attempts
        
        for user in all_users:
            mock_attempts = UGCNetMockAttempt.query.filter(
                UGCNetMockAttempt.user_id == user.id,
                UGCNetMockAttempt.started_at >= start_date
            ).count()
            
            practice_attempts = UGCNetPracticeAttempt.query.filter(
                UGCNetPracticeAttempt.user_id == user.id,
                UGCNetPracticeAttempt.started_at >= start_date
            ).count()
            
            total_attempts = mock_attempts + practice_attempts
            
            if total_attempts == 0:
                inactive_users += 1
            elif total_attempts <= 5:
                low_activity += 1
            elif total_attempts <= 20:
                medium_activity += 1
            else:
                high_activity += 1
        
        return {
            'inactive': inactive_users,
            'low_activity': low_activity,
            'medium_activity': medium_activity,
            'high_activity': high_activity,
            'total_users': len(all_users)
        }
        
    except Exception as e:
        print(f"Error getting activity distribution: {e}")
        return {
            'inactive': 0,
            'low_activity': 0,
            'medium_activity': 0,
            'high_activity': 0,
            'total_users': 0
        }

@analytics_bp.route('/subjects/<int:subject_id>', methods=['GET'])
@jwt_required()
def get_subject_analytics(subject_id):
    """Get analytics for a specific subject"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        subject = Subject.query.get_or_404(subject_id)
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Subject performance
        subject_performance = get_subject_performance(subject_id, start_date)
        
        # Chapter breakdown
        chapter_breakdown = get_chapter_breakdown(subject_id, start_date)
        
        # Question bank stats
        question_stats = get_question_bank_stats(subject_id)
        
        return jsonify({
            'subject': subject.to_dict(),
            'performance': subject_performance,
            'chapters': chapter_breakdown,
            'questions': question_stats,
            'period_days': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_subject_performance(subject_id, start_date):
    """Get performance metrics for a specific subject"""
    try:
        # Mock test performance
        mock_attempts = db.session.query(UGCNetMockAttempt).join(UGCNetMockTest).filter(
            UGCNetMockTest.subject_id == subject_id,
            UGCNetMockAttempt.is_completed == True,
            UGCNetMockAttempt.completed_at >= start_date
        ).all()
        
        # Practice test performance
        practice_attempts = UGCNetPracticeAttempt.query.filter(
            UGCNetPracticeAttempt.subject_id == subject_id,
            UGCNetPracticeAttempt.is_completed == True,
            UGCNetPracticeAttempt.completed_at >= start_date
        ).all()
        
        mock_scores = [attempt.percentage for attempt in mock_attempts if attempt.percentage is not None]
        practice_scores = [attempt.percentage for attempt in practice_attempts if attempt.percentage is not None]
        
        return {
            'mock_tests': {
                'total_attempts': len(mock_attempts),
                'average_score': round(sum(mock_scores) / len(mock_scores), 2) if mock_scores else 0,
                'pass_rate': round((len([s for s in mock_scores if s >= 40]) / len(mock_scores)) * 100, 2) if mock_scores else 0
            },
            'practice_tests': {
                'total_attempts': len(practice_attempts),
                'average_score': round(sum(practice_scores) / len(practice_scores), 2) if practice_scores else 0,
                'pass_rate': round((len([s for s in practice_scores if s >= 60]) / len(practice_scores)) * 100, 2) if practice_scores else 0
            }
        }
        
    except Exception as e:
        print(f"Error getting subject performance: {e}")
        return {
            'mock_tests': {'total_attempts': 0, 'average_score': 0, 'pass_rate': 0},
            'practice_tests': {'total_attempts': 0, 'average_score': 0, 'pass_rate': 0}
        }

def get_chapter_breakdown(subject_id, start_date):
    """Get chapter-wise analytics for a subject"""
    try:
        chapters = Chapter.query.filter_by(subject_id=subject_id, is_active=True).all()
        chapter_data = []
        
        for chapter in chapters:
            # Count questions in this chapter
            questions_count = QuestionBank.query.filter_by(chapter_id=chapter.id).count()
            
            # This would require more complex queries to get chapter-wise attempt data
            # For now, we'll provide basic info
            chapter_data.append({
                'chapter_id': chapter.id,
                'chapter_name': chapter.name,
                'questions_count': questions_count,
                'weightage_paper1': chapter.weightage_paper1,
                'weightage_paper2': chapter.weightage_paper2
            })
        
        return chapter_data
        
    except Exception as e:
        print(f"Error getting chapter breakdown: {e}")
        return []

def get_question_bank_stats(subject_id):
    """Get question bank statistics for a subject"""
    try:
        # Get all questions for chapters in this subject
        questions = db.session.query(QuestionBank).join(Chapter).filter(
            Chapter.subject_id == subject_id
        ).all()
        
        total_questions = len(questions)
        verified_questions = len([q for q in questions if q.is_verified])
        
        # Difficulty distribution
        difficulty_counts = {
            'easy': len([q for q in questions if q.difficulty == 'easy']),
            'medium': len([q for q in questions if q.difficulty == 'medium']),
            'hard': len([q for q in questions if q.difficulty == 'hard'])
        }
        
        # Source distribution
        source_counts = {}
        for question in questions:
            source = question.source or 'unknown'
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return {
            'total_questions': total_questions,
            'verified_questions': verified_questions,
            'verification_rate': round((verified_questions / total_questions) * 100, 2) if total_questions > 0 else 0,
            'difficulty_distribution': difficulty_counts,
            'source_distribution': source_counts
        }
        
    except Exception as e:
        print(f"Error getting question bank stats: {e}")
        return {
            'total_questions': 0,
            'verified_questions': 0,
            'verification_rate': 0,
            'difficulty_distribution': {'easy': 0, 'medium': 0, 'hard': 0},
            'source_distribution': {}
        }
