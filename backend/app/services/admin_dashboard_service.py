"""
Admin Dashboard Service
Handles dashboard analytics and statistics
"""
from datetime import datetime, timedelta
from sqlalchemy import desc
from app import db, redis_client
from app.models import User, Subject, Chapter, QuestionBank, UGCNetMockTest, UGCNetMockAttempt, UGCNetPracticeAttempt
import json


class AdminDashboardService:
    """Service for admin dashboard operations"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def get_basic_stats(self):
        """Get basic system statistics"""
        try:
            return {
                'total_users': User.query.filter_by(is_admin=False).count(),
                'total_subjects': Subject.query.filter_by(is_active=True).count(),
                'total_questions': QuestionBank.query.count(),
                'total_mock_tests': UGCNetMockTest.query.filter_by(is_active=True).count(),
                'total_mock_attempts': UGCNetMockAttempt.query.filter_by(is_completed=True).count(),
                'total_practice_attempts': UGCNetPracticeAttempt.query.filter_by(is_completed=True).count()
            }
        except Exception as e:
            print(f"Error getting basic stats: {e}")
            return {
                'total_users': 0,
                'total_subjects': 0,
                'total_questions': 0,
                'total_mock_tests': 0,
                'total_mock_attempts': 0,
                'total_practice_attempts': 0
            }
    
    def get_time_filtered_stats(self, time_filter='7d'):
        """Get statistics for a specific time period"""
        # Calculate date range
        if time_filter == '24h':
            start_date = datetime.utcnow() - timedelta(hours=24)
        elif time_filter == '7d':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif time_filter == '30d':
            start_date = datetime.utcnow() - timedelta(days=30)
        elif time_filter == '90d':
            start_date = datetime.utcnow() - timedelta(days=90)
        else:
            start_date = datetime.utcnow() - timedelta(days=7)
        
        try:
            active_users = User.query.filter(
                User.is_admin == False,
                User.last_login >= start_date
            ).count()
            
            recent_mock_attempts = UGCNetMockAttempt.query.filter(
                UGCNetMockAttempt.is_completed == True,
                UGCNetMockAttempt.completed_at >= start_date
            ).count()
            
            recent_practice_attempts = UGCNetPracticeAttempt.query.filter(
                UGCNetPracticeAttempt.is_completed == True,
                UGCNetPracticeAttempt.completed_at >= start_date
            ).count()
            
            return {
                'active_users': active_users,
                'recent_mock_attempts': recent_mock_attempts,
                'recent_practice_attempts': recent_practice_attempts,
                'start_date': start_date
            }
        except Exception as e:
            print(f"Error getting time filtered stats: {e}")
            return {
                'active_users': 0,
                'recent_mock_attempts': 0,
                'recent_practice_attempts': 0,
                'start_date': start_date
            }
    
    def get_performance_stats(self, start_date):
        """Calculate performance statistics"""
        try:
            # Mock test performance
            completed_mock_attempts = UGCNetMockAttempt.query.filter(
                UGCNetMockAttempt.is_completed == True,
                UGCNetMockAttempt.completed_at >= start_date
            ).all()
            
            average_mock_score = 0
            mock_pass_rate = 0
            
            if completed_mock_attempts:
                scores = [attempt.percentage for attempt in completed_mock_attempts if attempt.percentage is not None]
                if scores:
                    average_mock_score = round(sum(scores) / len(scores), 1)
                    mock_pass_rate = round((len([s for s in scores if s >= 40]) / len(scores)) * 100, 1)
            
            # Practice test performance
            completed_practice_attempts = UGCNetPracticeAttempt.query.filter(
                UGCNetPracticeAttempt.is_completed == True,
                UGCNetPracticeAttempt.completed_at >= start_date
            ).all()
            
            average_practice_score = 0
            practice_pass_rate = 0
            
            if completed_practice_attempts:
                scores = [attempt.percentage for attempt in completed_practice_attempts if attempt.percentage is not None]
                if scores:
                    average_practice_score = round(sum(scores) / len(scores), 1)
                    practice_pass_rate = round((len([s for s in scores if s >= 60]) / len(scores)) * 100, 1)
            
            return {
                'average_mock_score': average_mock_score,
                'average_practice_score': average_practice_score,
                'mock_pass_rate': mock_pass_rate,
                'practice_pass_rate': practice_pass_rate
            }
        except Exception as e:
            print(f"Error calculating performance: {e}")
            return {
                'average_mock_score': 0,
                'average_practice_score': 0,
                'mock_pass_rate': 0,
                'practice_pass_rate': 0
            }
    
    def get_subject_stats(self, start_date):
        """Get statistics by subject"""
        subject_stats = []
        try:
            subjects = Subject.query.filter_by(is_active=True).all()
            
            for subject in subjects:
                try:
                    # Get attempts for this subject via mock tests
                    subject_mock_attempts = db.session.query(UGCNetMockAttempt).join(UGCNetMockTest).filter(
                        UGCNetMockTest.subject_id == subject.id,
                        UGCNetMockAttempt.is_completed == True,
                        UGCNetMockAttempt.completed_at >= start_date
                    ).all()
                    
                    # Get practice attempts for this subject
                    subject_practice_attempts = UGCNetPracticeAttempt.query.filter(
                        UGCNetPracticeAttempt.subject_id == subject.id,
                        UGCNetPracticeAttempt.is_completed == True,
                        UGCNetPracticeAttempt.completed_at >= start_date
                    ).all()
                    
                    total_subject_attempts = len(subject_mock_attempts) + len(subject_practice_attempts)
                    
                    if total_subject_attempts > 0:
                        all_scores = []
                        all_scores.extend([attempt.percentage for attempt in subject_mock_attempts if attempt.percentage is not None])
                        all_scores.extend([attempt.percentage for attempt in subject_practice_attempts if attempt.percentage is not None])
                        
                        if all_scores:
                            avg_score = round(sum(all_scores) / len(all_scores), 1)
                            subject_stats.append({
                                'name': subject.name,
                                'attempts': total_subject_attempts,
                                'average_score': avg_score
                            })
                except Exception as e:
                    print(f"Error processing subject {subject.name}: {e}")
                    continue
        except Exception as e:
            print(f"Error getting subject stats: {e}")
        
        return subject_stats
    
    def get_top_performers(self, limit=10):
        """Get recent top performers"""
        top_performers = []
        try:
            # Get recent high-scoring mock attempts
            recent_mock_attempts = UGCNetMockAttempt.query.filter(
                UGCNetMockAttempt.is_completed == True,
                UGCNetMockAttempt.percentage >= 80
            ).order_by(desc(UGCNetMockAttempt.completed_at)).limit(5).all()
            
            # Get recent high-scoring practice attempts
            recent_practice_attempts = UGCNetPracticeAttempt.query.filter(
                UGCNetPracticeAttempt.is_completed == True,
                UGCNetPracticeAttempt.percentage >= 80
            ).order_by(desc(UGCNetPracticeAttempt.completed_at)).limit(5).all()
            
            # Combine and sort
            all_attempts = []
            for attempt in recent_mock_attempts:
                all_attempts.append({
                    'type': 'mock',
                    'attempt': attempt,
                    'completed_at': attempt.completed_at
                })
            
            for attempt in recent_practice_attempts:
                all_attempts.append({
                    'type': 'practice',
                    'attempt': attempt,
                    'completed_at': attempt.completed_at
                })
            
            # Sort by completion time and take top results
            all_attempts.sort(key=lambda x: x['completed_at'], reverse=True)
            
            for item in all_attempts[:limit]:
                try:
                    attempt = item['attempt']
                    test_title = ""
                    if item['type'] == 'mock' and attempt.mock_test:
                        test_title = attempt.mock_test.title
                    elif item['type'] == 'practice':
                        test_title = attempt.title
                    
                    top_performers.append({
                        'id': attempt.id,
                        'user_name': attempt.user.full_name if attempt.user else 'Unknown',
                        'test_title': test_title,
                        'test_type': item['type'],
                        'percentage': attempt.percentage,
                        'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None
                    })
                except Exception as e:
                    print(f"Error processing top performer: {e}")
                    continue
        except Exception as e:
            print(f"Error getting top performers: {e}")
        
        return top_performers
    
    def get_daily_trends(self, days=7):
        """Get daily trends for the last N days"""
        daily_trends = []
        try:
            for i in range(days-1, -1, -1):  # Last N days
                date = datetime.utcnow().date() - timedelta(days=i)
                next_date = date + timedelta(days=1)
                
                # Count mock attempts for this day
                day_mock_attempts = UGCNetMockAttempt.query.filter(
                    UGCNetMockAttempt.completed_at >= date,
                    UGCNetMockAttempt.completed_at < next_date,
                    UGCNetMockAttempt.is_completed == True
                ).count()
                
                # Count practice attempts for this day
                day_practice_attempts = UGCNetPracticeAttempt.query.filter(
                    UGCNetPracticeAttempt.completed_at >= date,
                    UGCNetPracticeAttempt.completed_at < next_date,
                    UGCNetPracticeAttempt.is_completed == True
                ).count()
                
                total_day_attempts = day_mock_attempts + day_practice_attempts
                
                # Calculate average score for this day
                day_mock_scores = [attempt.percentage for attempt in UGCNetMockAttempt.query.filter(
                    UGCNetMockAttempt.completed_at >= date,
                    UGCNetMockAttempt.completed_at < next_date,
                    UGCNetMockAttempt.is_completed == True,
                    UGCNetMockAttempt.percentage != None
                ).all()]
                
                day_practice_scores = [attempt.percentage for attempt in UGCNetPracticeAttempt.query.filter(
                    UGCNetPracticeAttempt.completed_at >= date,
                    UGCNetPracticeAttempt.completed_at < next_date,
                    UGCNetPracticeAttempt.is_completed == True,
                    UGCNetPracticeAttempt.percentage != None
                ).all()]
                
                all_day_scores = day_mock_scores + day_practice_scores
                day_avg_score = round(sum(all_day_scores) / len(all_day_scores), 1) if all_day_scores else 0
                
                daily_trends.append({
                    'date': date.strftime('%b %d'),
                    'attempts': total_day_attempts,
                    'average_score': day_avg_score
                })
        except Exception as e:
            print(f"Error calculating daily trends: {e}")
            # Provide fallback data
            for i in range(days-1, -1, -1):
                date = datetime.utcnow().date() - timedelta(days=i)
                daily_trends.append({
                    'date': date.strftime('%b %d'),
                    'attempts': 0,
                    'average_score': 0
                })
        
        return daily_trends
    
    def calculate_retention_rate(self):
        """Calculate user retention rate"""
        try:
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            # Total users
            total_users = User.query.filter_by(is_admin=False).count()
            
            # Users who have made attempts in the last 30 days
            active_users_30_days = db.session.query(User).join(
                db.or_(
                    User.id == UGCNetMockAttempt.user_id,
                    User.id == UGCNetPracticeAttempt.user_id
                )
            ).filter(
                db.or_(
                    UGCNetMockAttempt.started_at >= thirty_days_ago,
                    UGCNetPracticeAttempt.started_at >= thirty_days_ago
                ),
                User.is_admin == False
            ).distinct().count()
            
            if total_users > 0:
                return round((active_users_30_days / total_users) * 100, 1)
            else:
                return 0
        except Exception as e:
            print(f"Error calculating retention rate: {e}")
            return 0
    
    def get_comprehensive_dashboard_stats(self, time_filter='7d'):
        """Get all dashboard statistics in one call"""
        cache_key = f'admin_dashboard_stats_{time_filter}'
        
        # Try to get from cache
        try:
            if redis_client:
                cached_stats = redis_client.get(cache_key)
                if cached_stats:
                    return json.loads(cached_stats)
        except Exception as redis_error:
            print(f"Redis cache error: {redis_error}")
        
        # Generate fresh data
        basic_stats = self.get_basic_stats()
        time_stats = self.get_time_filtered_stats(time_filter)
        performance_stats = self.get_performance_stats(time_stats['start_date'])
        subject_stats = self.get_subject_stats(time_stats['start_date'])
        top_performers = self.get_top_performers()
        daily_trends = self.get_daily_trends()
        retention_rate = self.calculate_retention_rate()
        
        # User management specific stats
        user_management_stats = {
            'total_admins': User.query.filter_by(is_admin=True).count(),
            'active_users_all': User.query.filter_by(is_active=True, is_admin=False).count(),
            'inactive_users': User.query.filter_by(is_active=False, is_admin=False).count(),
            'new_users_today': User.query.filter(
                User.created_at >= datetime.utcnow().date(),
                User.is_admin == False
            ).count()
        }
        
        # Combine all statistics
        combined_average_score = round(
            (performance_stats['average_mock_score'] + performance_stats['average_practice_score']) / 2, 1
        ) if performance_stats['average_mock_score'] > 0 or performance_stats['average_practice_score'] > 0 else 0
        
        combined_pass_rate = round(
            (performance_stats['mock_pass_rate'] + performance_stats['practice_pass_rate']) / 2, 1
        ) if performance_stats['mock_pass_rate'] > 0 or performance_stats['practice_pass_rate'] > 0 else 0
        
        total_attempts = basic_stats['total_mock_attempts'] + basic_stats['total_practice_attempts']
        recent_attempts_count = time_stats['recent_mock_attempts'] + time_stats['recent_practice_attempts']
        
        stats = {
            **basic_stats,
            'active_users': time_stats['active_users'],
            'recent_attempts': recent_attempts_count,
            'today_attempts': recent_attempts_count,
            'week_attempts': recent_attempts_count,
            'total_attempts': total_attempts,
            'average_score': combined_average_score,
            'pass_rate': combined_pass_rate,
            'retention_rate': retention_rate,
            **user_management_stats,
            'subjects': subject_stats,
            'top_performers': top_performers,
            'daily_trends': daily_trends,
            'ugc_net_stats': {
                'total_mock_tests': basic_stats['total_mock_tests'],
                'total_mock_attempts': basic_stats['total_mock_attempts'],
                'total_practice_attempts': basic_stats['total_practice_attempts'],
                **performance_stats
            },
            # Nested structures for compatibility
            'stats': {
                'total_users': basic_stats['total_users'],
                'total_subjects': basic_stats['total_subjects'],
                'total_mock_tests': basic_stats['total_mock_tests'],
                'total_questions': basic_stats['total_questions'],
                'total_attempts': total_attempts,
                'active_users': time_stats['active_users'],
                'recent_attempts': recent_attempts_count
            },
            'performance': {
                'average_percentage': combined_average_score,
                'pass_rate': combined_pass_rate,
                'average_time_minutes': 0,
                'retention_rate': retention_rate
            },
            'engagement': {
                'total_registered': basic_stats['total_users'],
                'active_users': time_stats['active_users']
            },
            'user_management': user_management_stats
        }
        
        # Cache for 5 minutes
        try:
            if redis_client:
                redis_client.setex(cache_key, self.cache_timeout, json.dumps(stats, default=str))
        except Exception as redis_error:
            print(f"Redis cache set error: {redis_error}")
        
        return stats
