"""
User Analytics Service
Handles user analytics and reporting for admin
"""
from datetime import datetime, timedelta
from sqlalchemy import desc
from app import db
from app.models import User, UGCNetMockAttempt, UGCNetPracticeAttempt, UGCNetMockTest


class UserAnalyticsService:
    """Service for user analytics operations"""
    
    def __init__(self):
        pass
    
    def get_user_analytics(self, user_id, days=30, subject_id=None):
        """Get comprehensive analytics for a specific user"""
        try:
            # Verify user exists
            user = User.query.get(user_id)
            if not user:
                raise ValueError('User not found')
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Build base query for mock attempts
            mock_attempts_query = UGCNetMockAttempt.query.filter(
                UGCNetMockAttempt.user_id == user_id,
                UGCNetMockAttempt.is_completed == True,
                UGCNetMockAttempt.completed_at >= start_date,
                UGCNetMockAttempt.completed_at <= end_date
            )
            
            # Build base query for practice attempts
            practice_attempts_query = UGCNetPracticeAttempt.query.filter(
                UGCNetPracticeAttempt.user_id == user_id,
                UGCNetPracticeAttempt.is_completed == True,
                UGCNetPracticeAttempt.completed_at >= start_date,
                UGCNetPracticeAttempt.completed_at <= end_date
            )
            
            # Add subject filter if provided
            if subject_id:
                mock_attempts_query = mock_attempts_query.join(UGCNetMockTest).filter(UGCNetMockTest.subject_id == subject_id)
                practice_attempts_query = practice_attempts_query.filter(UGCNetPracticeAttempt.subject_id == subject_id)
            
            mock_attempts = mock_attempts_query.order_by(UGCNetMockAttempt.completed_at.desc()).all()
            practice_attempts = practice_attempts_query.order_by(UGCNetPracticeAttempt.completed_at.desc()).all()
            
            # Calculate basic stats
            total_mock_attempts = len(mock_attempts)
            total_practice_attempts = len(practice_attempts)
            total_attempts = total_mock_attempts + total_practice_attempts
            
            # Calculate averages
            mock_scores = [attempt.percentage for attempt in mock_attempts if attempt.percentage is not None]
            practice_scores = [attempt.percentage for attempt in practice_attempts if attempt.percentage is not None]
            
            average_mock_score = sum(mock_scores) / len(mock_scores) if mock_scores else 0
            average_practice_score = sum(practice_scores) / len(practice_scores) if practice_scores else 0
            average_overall_score = (average_mock_score + average_practice_score) / 2 if (mock_scores or practice_scores) else 0
            
            # Calculate trends (compare to previous period)
            prev_start = start_date - timedelta(days=days)
            prev_mock_attempts = UGCNetMockAttempt.query.filter(
                UGCNetMockAttempt.user_id == user_id,
                UGCNetMockAttempt.is_completed == True,
                UGCNetMockAttempt.completed_at >= prev_start,
                UGCNetMockAttempt.completed_at < start_date
            ).all()
            
            prev_practice_attempts = UGCNetPracticeAttempt.query.filter(
                UGCNetPracticeAttempt.user_id == user_id,
                UGCNetPracticeAttempt.is_completed == True,
                UGCNetPracticeAttempt.completed_at >= prev_start,
                UGCNetPracticeAttempt.completed_at < start_date
            ).all()
            
            prev_mock_scores = [attempt.percentage for attempt in prev_mock_attempts if attempt.percentage is not None]
            prev_practice_scores = [attempt.percentage for attempt in prev_practice_attempts if attempt.percentage is not None]
            prev_average_score = (sum(prev_mock_scores + prev_practice_scores) / len(prev_mock_scores + prev_practice_scores)) if (prev_mock_scores or prev_practice_scores) else 0
            
            score_trend = average_overall_score - prev_average_score
            
            # Get daily performance
            daily_performance = self._get_daily_performance(mock_attempts, practice_attempts)
            
            # Get subject performance
            subject_performance = self._get_subject_performance(mock_attempts, practice_attempts)
            
            return {
                'user': {
                    'id': user.id,
                    'full_name': user.full_name,
                    'email': user.email
                },
                'summary': {
                    'total_attempts': total_attempts,
                    'total_mock_attempts': total_mock_attempts,
                    'total_practice_attempts': total_practice_attempts,
                    'average_score': round(average_overall_score, 2),
                    'average_mock_score': round(average_mock_score, 2),
                    'average_practice_score': round(average_practice_score, 2),
                    'score_trend': round(score_trend, 2),
                    'period_days': days
                },
                'daily_performance': daily_performance,
                'subject_performance': subject_performance,
                'filters': {
                    'subject_id': subject_id,
                    'days': days
                }
            }
        except Exception as e:
            raise Exception(f"Error getting user analytics: {str(e)}")
    
    def _get_daily_performance(self, mock_attempts, practice_attempts):
        """Calculate daily performance data"""
        daily_performance = {}
        all_attempts = []
        
        # Combine all attempts with type info
        for attempt in mock_attempts:
            all_attempts.append({
                'type': 'mock',
                'attempt': attempt,
                'date': attempt.completed_at,
                'percentage': attempt.percentage
            })
        
        for attempt in practice_attempts:
            all_attempts.append({
                'type': 'practice',
                'attempt': attempt,
                'date': attempt.completed_at,
                'percentage': attempt.percentage
            })
        
        for item in all_attempts:
            day_key = item['date'].strftime('%Y-%m-%d')
            if day_key not in daily_performance:
                daily_performance[day_key] = {'attempts': 0, 'scores': []}
            daily_performance[day_key]['attempts'] += 1
            if item['percentage'] is not None:
                daily_performance[day_key]['scores'].append(item['percentage'])
        
        # Convert to list and calculate percentages
        performance_data = []
        for day, data in sorted(daily_performance.items()):
            percentage = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
            performance_data.append({
                'date': day,
                'attempts': data['attempts'],
                'percentage': round(percentage, 2)
            })
        
        return performance_data
    
    def _get_subject_performance(self, mock_attempts, practice_attempts):
        """Calculate subject-wise performance"""
        subject_performance = {}
        
        # Process mock attempts
        for attempt in mock_attempts:
            if attempt.mock_test and attempt.mock_test.subject:
                subject_name = attempt.mock_test.subject.name
                
                if subject_name not in subject_performance:
                    subject_performance[subject_name] = {
                        'mock_attempts': 0, 
                        'practice_attempts': 0,
                        'mock_scores': [],
                        'practice_scores': []
                    }
                
                subject_performance[subject_name]['mock_attempts'] += 1
                if attempt.percentage is not None:
                    subject_performance[subject_name]['mock_scores'].append(attempt.percentage)
        
        # Process practice attempts
        for attempt in practice_attempts:
            if attempt.subject:
                subject_name = attempt.subject.name
                
                if subject_name not in subject_performance:
                    subject_performance[subject_name] = {
                        'mock_attempts': 0,
                        'practice_attempts': 0,
                        'mock_scores': [],
                        'practice_scores': []
                    }
                
                subject_performance[subject_name]['practice_attempts'] += 1
                if attempt.percentage is not None:
                    subject_performance[subject_name]['practice_scores'].append(attempt.percentage)
        
        # Convert to list with percentages
        subjects_data = []
        for subject_name, data in subject_performance.items():
            all_subject_scores = data['mock_scores'] + data['practice_scores']
            total_subject_attempts = data['mock_attempts'] + data['practice_attempts']
            percentage = sum(all_subject_scores) / len(all_subject_scores) if all_subject_scores else 0
            
            subjects_data.append({
                'name': subject_name,
                'attempts': total_subject_attempts,
                'mock_attempts': data['mock_attempts'],
                'practice_attempts': data['practice_attempts'],
                'percentage': round(percentage, 2)
            })
        
        return subjects_data
