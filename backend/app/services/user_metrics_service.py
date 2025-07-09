"""
Enhanced User Metrics Service
Tracks comprehensive user metrics for AI-powered recommendations and study plans
"""
from datetime import datetime, timedelta
from sqlalchemy import desc, func, and_, or_
from app import db
from app.models import (
    User, UGCNetMockAttempt, UGCNetPracticeAttempt, UGCNetMockTest, 
    Chapter, Subject, QuestionBank
)
import json


class UserMetricsService:
    """Service for comprehensive user metrics and analytics"""
    
    def __init__(self):
        pass
    
    def get_comprehensive_user_metrics(self, user_id, days=30):
        """Get comprehensive metrics for AI recommendations and study planning"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('User not found')
            
            # Calculate date ranges for trend analysis
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            recent_start = end_date - timedelta(days=7)  # Last 7 days
            
            # Get all attempts
            mock_attempts = self._get_mock_attempts(user_id, start_date, end_date)
            practice_attempts = self._get_practice_attempts(user_id, start_date, end_date)
            recent_mock_attempts = self._get_mock_attempts(user_id, recent_start, end_date)
            recent_practice_attempts = self._get_practice_attempts(user_id, recent_start, end_date)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(
                mock_attempts, practice_attempts, recent_mock_attempts, recent_practice_attempts
            )
            
            # Get subject-specific performance
            subject_performance = self._get_subject_performance(mock_attempts, practice_attempts)
            
            # Get chapter-specific weaknesses
            chapter_weaknesses = self._identify_chapter_weaknesses(practice_attempts)
            
            # Get study patterns
            study_patterns = self._analyze_study_patterns(mock_attempts, practice_attempts)
            
            # Get difficulty level performance
            difficulty_performance = self._analyze_difficulty_performance(practice_attempts)
            
            # Get time management metrics
            time_metrics = self._analyze_time_management(mock_attempts, practice_attempts)
            
            # Get progress trends
            progress_trends = self._calculate_progress_trends(mock_attempts, practice_attempts, days)
            
            # Get incomplete test patterns
            incomplete_patterns = self._analyze_incomplete_patterns(user_id)
            
            return {
                'user_info': {
                    'id': user.id,
                    'full_name': user.full_name,
                    'subject_id': user.subject_id,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                },
                'performance_metrics': performance_metrics,
                'subject_performance': subject_performance,
                'chapter_weaknesses': chapter_weaknesses,
                'study_patterns': study_patterns,
                'difficulty_performance': difficulty_performance,
                'time_metrics': time_metrics,
                'progress_trends': progress_trends,
                'incomplete_patterns': incomplete_patterns,
                'analysis_period': {
                    'days': days,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'recent_period': 7
                }
            }
        except Exception as e:
            raise Exception(f"Error getting comprehensive metrics: {str(e)}")
    
    def _get_mock_attempts(self, user_id, start_date, end_date):
        """Get mock attempts within date range"""
        return UGCNetMockAttempt.query.filter(
            UGCNetMockAttempt.user_id == user_id,
            UGCNetMockAttempt.created_at >= start_date,
            UGCNetMockAttempt.created_at <= end_date
        ).order_by(UGCNetMockAttempt.created_at.desc()).all()
    
    def _get_practice_attempts(self, user_id, start_date, end_date):
        """Get practice attempts within date range"""
        return UGCNetPracticeAttempt.query.filter(
            UGCNetPracticeAttempt.user_id == user_id,
            UGCNetPracticeAttempt.created_at >= start_date,
            UGCNetPracticeAttempt.created_at <= end_date
        ).order_by(UGCNetPracticeAttempt.created_at.desc()).all()
    
    def _calculate_performance_metrics(self, mock_attempts, practice_attempts, recent_mock, recent_practice):
        """Calculate comprehensive performance metrics"""
        # All attempts
        all_completed_mock = [a for a in mock_attempts if a.is_completed and a.percentage is not None]
        all_completed_practice = [a for a in practice_attempts if a.is_completed and a.percentage is not None]
        
        # Recent attempts (last 7 days)
        recent_completed_mock = [a for a in recent_mock if a.is_completed and a.percentage is not None]
        recent_completed_practice = [a for a in recent_practice if a.is_completed and a.percentage is not None]
        
        # Calculate scores
        all_mock_scores = [a.percentage for a in all_completed_mock]
        all_practice_scores = [a.percentage for a in all_completed_practice]
        all_scores = all_mock_scores + all_practice_scores
        
        recent_mock_scores = [a.percentage for a in recent_completed_mock]
        recent_practice_scores = [a.percentage for a in recent_completed_practice]
        recent_scores = recent_mock_scores + recent_practice_scores
        
        # Calculate statistics
        total_attempts = len(mock_attempts) + len(practice_attempts)
        completed_attempts = len(all_completed_mock) + len(all_completed_practice)
        completion_rate = (completed_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        recent_avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0
        best_score = max(all_scores) if all_scores else 0
        worst_score = min(all_scores) if all_scores else 0
        
        # Calculate improvement trend
        improvement_trend = recent_avg_score - avg_score if all_scores and recent_scores else 0
        
        # Calculate consistency (standard deviation)
        if len(all_scores) > 1:
            variance = sum((x - avg_score) ** 2 for x in all_scores) / len(all_scores)
            consistency_score = 100 - min(variance ** 0.5, 100)  # Lower std dev = higher consistency
        else:
            consistency_score = 0
        
        # Calculate qualified attempts (>=40%)
        qualified_attempts = len([s for s in all_scores if s >= 40])
        qualification_rate = (qualified_attempts / len(all_scores) * 100) if all_scores else 0
        
        return {
            'total_attempts': total_attempts,
            'completed_attempts': completed_attempts,
            'completion_rate': round(completion_rate, 1),
            'average_score': round(avg_score, 1),
            'recent_average_score': round(recent_avg_score, 1),
            'best_score': round(best_score, 1),
            'worst_score': round(worst_score, 1),
            'improvement_trend': round(improvement_trend, 1),
            'consistency_score': round(consistency_score, 1),
            'qualified_attempts': qualified_attempts,
            'qualification_rate': round(qualification_rate, 1),
            'mock_attempts': len(mock_attempts),
            'practice_attempts': len(practice_attempts),
            'mock_completion_rate': round(len(all_completed_mock) / len(mock_attempts) * 100, 1) if mock_attempts else 0,
            'practice_completion_rate': round(len(all_completed_practice) / len(practice_attempts) * 100, 1) if practice_attempts else 0
        }
    
    def _get_subject_performance(self, mock_attempts, practice_attempts):
        """Analyze performance by subject"""
        subject_stats = {}
        
        # Process mock attempts
        for attempt in mock_attempts:
            if attempt.is_completed and attempt.percentage is not None and attempt.mock_test and attempt.mock_test.subject:
                subject_name = attempt.mock_test.subject.name
                subject_id = attempt.mock_test.subject.id
                
                if subject_id not in subject_stats:
                    subject_stats[subject_id] = {
                        'subject_name': subject_name,
                        'mock_scores': [],
                        'practice_scores': [],
                        'mock_attempts': 0,
                        'practice_attempts': 0
                    }
                
                subject_stats[subject_id]['mock_scores'].append(attempt.percentage)
                subject_stats[subject_id]['mock_attempts'] += 1
        
        # Process practice attempts
        for attempt in practice_attempts:
            if attempt.is_completed and attempt.percentage is not None and attempt.subject:
                subject_name = attempt.subject.name
                subject_id = attempt.subject.id
                
                if subject_id not in subject_stats:
                    subject_stats[subject_id] = {
                        'subject_name': subject_name,
                        'mock_scores': [],
                        'practice_scores': [],
                        'mock_attempts': 0,
                        'practice_attempts': 0
                    }
                
                subject_stats[subject_id]['practice_scores'].append(attempt.percentage)
                subject_stats[subject_id]['practice_attempts'] += 1
        
        # Calculate averages and recommendations
        subject_performance = []
        for subject_id, stats in subject_stats.items():
            all_scores = stats['mock_scores'] + stats['practice_scores']
            avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
            total_attempts = stats['mock_attempts'] + stats['practice_attempts']
            
            # Determine performance level
            if avg_score >= 70:
                performance_level = 'excellent'
            elif avg_score >= 55:
                performance_level = 'good'
            elif avg_score >= 40:
                performance_level = 'average'
            else:
                performance_level = 'needs_improvement'
            
            subject_performance.append({
                'subject_id': subject_id,
                'subject_name': stats['subject_name'],
                'average_score': round(avg_score, 1),
                'total_attempts': total_attempts,
                'mock_attempts': stats['mock_attempts'],
                'practice_attempts': stats['practice_attempts'],
                'performance_level': performance_level,
                'recommendation_priority': 'high' if avg_score < 40 else 'medium' if avg_score < 55 else 'low'
            })
        
        return sorted(subject_performance, key=lambda x: x['average_score'])
    
    def _identify_chapter_weaknesses(self, practice_attempts):
        """Identify chapters where user performs poorly"""
        chapter_stats = {}
        
        for attempt in practice_attempts:
            if attempt.is_completed and attempt.percentage is not None:
                # Parse selected chapters from attempt data
                if hasattr(attempt, 'selected_chapters') and attempt.selected_chapters:
                    try:
                        if isinstance(attempt.selected_chapters, str):
                            selected_chapters = json.loads(attempt.selected_chapters)
                        else:
                            selected_chapters = attempt.selected_chapters
                        
                        for chapter_id in selected_chapters:
                            if chapter_id not in chapter_stats:
                                chapter = Chapter.query.get(chapter_id)
                                if chapter:
                                    chapter_stats[chapter_id] = {
                                        'chapter_name': chapter.name,
                                        'subject_name': chapter.subject.name if chapter.subject else 'Unknown',
                                        'scores': [],
                                        'attempts': 0
                                    }
                            
                            if chapter_id in chapter_stats:
                                chapter_stats[chapter_id]['scores'].append(attempt.percentage)
                                chapter_stats[chapter_id]['attempts'] += 1
                    except (json.JSONDecodeError, TypeError):
                        continue
        
        # Calculate chapter performance
        chapter_weaknesses = []
        for chapter_id, stats in chapter_stats.items():
            if stats['scores']:
                avg_score = sum(stats['scores']) / len(stats['scores'])
                
                # Identify as weakness if average score < 50% and has multiple attempts
                if avg_score < 50 and stats['attempts'] >= 2:
                    chapter_weaknesses.append({
                        'chapter_id': chapter_id,
                        'chapter_name': stats['chapter_name'],
                        'subject_name': stats['subject_name'],
                        'average_score': round(avg_score, 1),
                        'attempts': stats['attempts'],
                        'weakness_level': 'critical' if avg_score < 30 else 'moderate' if avg_score < 40 else 'minor'
                    })
        
        return sorted(chapter_weaknesses, key=lambda x: x['average_score'])
    
    def _analyze_study_patterns(self, mock_attempts, practice_attempts):
        """Analyze user's study patterns and habits"""
        all_attempts = mock_attempts + practice_attempts
        
        if not all_attempts:
            return {
                'total_study_days': 0,
                'average_attempts_per_day': 0,
                'most_active_day': None,
                'study_frequency': 'inactive',
                'last_activity': None
            }
        
        # Calculate study frequency
        dates = [attempt.created_at.date() for attempt in all_attempts]
        unique_dates = set(dates)
        total_study_days = len(unique_dates)
        
        # Calculate average attempts per day
        if total_study_days > 0:
            avg_attempts_per_day = len(all_attempts) / total_study_days
        else:
            avg_attempts_per_day = 0
        
        # Find most active day of week
        day_counts = {}
        for attempt in all_attempts:
            day_name = attempt.created_at.strftime('%A')
            day_counts[day_name] = day_counts.get(day_name, 0) + 1
        
        most_active_day = max(day_counts.keys(), key=lambda k: day_counts[k]) if day_counts else None
        
        # Determine study frequency pattern
        if total_study_days == 0:
            frequency = 'inactive'
        elif avg_attempts_per_day >= 3:
            frequency = 'very_active'
        elif avg_attempts_per_day >= 1.5:
            frequency = 'active'
        elif avg_attempts_per_day >= 0.5:
            frequency = 'moderate'
        else:
            frequency = 'occasional'
        
        # Last activity
        last_activity = max(attempt.created_at for attempt in all_attempts) if all_attempts else None
        
        return {
            'total_study_days': total_study_days,
            'average_attempts_per_day': round(avg_attempts_per_day, 1),
            'most_active_day': most_active_day,
            'study_frequency': frequency,
            'last_activity': last_activity.isoformat() if last_activity else None,
            'day_wise_distribution': day_counts
        }
    
    def _analyze_difficulty_performance(self, practice_attempts):
        """Analyze performance across different difficulty levels"""
        # This would require difficulty tracking in practice attempts
        # For now, return basic structure
        return {
            'easy': {'attempts': 0, 'average_score': 0},
            'medium': {'attempts': 0, 'average_score': 0},
            'hard': {'attempts': 0, 'average_score': 0}
        }
    
    def _analyze_time_management(self, mock_attempts, practice_attempts):
        """Analyze time management in tests"""
        completed_mock = [a for a in mock_attempts if a.is_completed and a.time_taken]
        completed_practice = [a for a in practice_attempts if a.is_completed and a.time_taken]
        
        if not (completed_mock or completed_practice):
            return {
                'average_time_per_question': 0,
                'time_management_score': 0,
                'rushed_attempts': 0,
                'overtime_attempts': 0
            }
        
        # Calculate time metrics (this would need actual time tracking)
        return {
            'average_time_per_question': 0,  # Would calculate from actual data
            'time_management_score': 75,     # Placeholder
            'rushed_attempts': 0,
            'overtime_attempts': 0
        }
    
    def _calculate_progress_trends(self, mock_attempts, practice_attempts, days):
        """Calculate progress trends over time"""
        all_completed = []
        
        # Combine all completed attempts with scores
        for attempt in mock_attempts:
            if attempt.is_completed and attempt.percentage is not None:
                all_completed.append({
                    'date': attempt.completed_at or attempt.created_at,
                    'score': attempt.percentage,
                    'type': 'mock'
                })
        
        for attempt in practice_attempts:
            if attempt.is_completed and attempt.percentage is not None:
                all_completed.append({
                    'date': attempt.completed_at or attempt.created_at,
                    'score': attempt.percentage,
                    'type': 'practice'
                })
        
        # Sort by date
        all_completed.sort(key=lambda x: x['date'])
        
        if len(all_completed) < 2:
            return {
                'trend_direction': 'insufficient_data',
                'improvement_rate': 0,
                'recent_performance': 'stable'
            }
        
        # Calculate trend (simple linear regression slope)
        scores = [item['score'] for item in all_completed]
        n = len(scores)
        
        # Simple trend calculation
        first_half_avg = sum(scores[:n//2]) / (n//2) if n >= 4 else scores[0]
        second_half_avg = sum(scores[n//2:]) / (n - n//2) if n >= 4 else scores[-1]
        
        trend = second_half_avg - first_half_avg
        
        if trend > 5:
            trend_direction = 'improving'
        elif trend < -5:
            trend_direction = 'declining'
        else:
            trend_direction = 'stable'
        
        # Recent performance (last 25% of attempts)
        recent_count = max(1, n // 4)
        recent_scores = scores[-recent_count:]
        overall_avg = sum(scores) / len(scores)
        recent_avg = sum(recent_scores) / len(recent_scores)
        
        if recent_avg > overall_avg + 5:
            recent_performance = 'improving'
        elif recent_avg < overall_avg - 5:
            recent_performance = 'declining'
        else:
            recent_performance = 'stable'
        
        return {
            'trend_direction': trend_direction,
            'improvement_rate': round(trend, 1),
            'recent_performance': recent_performance,
            'data_points': n
        }
    
    def _analyze_incomplete_patterns(self, user_id):
        """Analyze patterns in incomplete tests"""
        incomplete_mock = UGCNetMockAttempt.query.filter_by(
            user_id=user_id, is_completed=False
        ).count()
        
        incomplete_practice = UGCNetPracticeAttempt.query.filter_by(
            user_id=user_id, is_completed=False
        ).count()
        
        total_incomplete = incomplete_mock + incomplete_practice
        
        return {
            'total_incomplete': total_incomplete,
            'incomplete_mock': incomplete_mock,
            'incomplete_practice': incomplete_practice,
            'completion_tendency': 'good' if total_incomplete < 3 else 'needs_improvement'
        }
