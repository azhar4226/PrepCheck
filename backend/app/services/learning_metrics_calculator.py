"""
Learning Metrics Calculator Service
Calculates and updates user learning metrics for AI recommendations
"""
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from app import db
from app.models import (
    User, UserLearningMetrics, UserStudySession, 
    UGCNetMockAttempt, UGCNetPracticeAttempt,
    Subject, Chapter
)
import json


class LearningMetricsCalculator:
    """Service to calculate and update user learning metrics"""
    
    def __init__(self):
        pass
    
    def calculate_all_user_metrics(self, user_id):
        """Calculate comprehensive learning metrics for a user"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('User not found')
            
            # Get existing metrics or create new
            metrics = UserLearningMetrics.query.filter_by(user_id=user_id).first()
            if not metrics:
                metrics = UserLearningMetrics(user_id=user_id)
                db.session.add(metrics)
            
            # Calculate overall performance
            self._calculate_overall_performance(user_id, metrics)
            
            # Calculate learning patterns
            self._calculate_learning_patterns(user_id, metrics)
            
            # Calculate strengths and weaknesses
            self._calculate_strengths_weaknesses(user_id, metrics)
            
            # Calculate progress tracking
            self._calculate_progress_tracking(user_id, metrics)
            
            # Calculate AI insights
            self._calculate_ai_insights(user_id, metrics)
            
            # Update metadata
            metrics.last_calculated = datetime.utcnow()
            metrics.calculation_version = '1.0'
            
            db.session.commit()
            return metrics
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error calculating learning metrics: {str(e)}")
    
    def _calculate_overall_performance(self, user_id, metrics):
        """Calculate overall performance metrics"""
        # Get all completed attempts
        mock_attempts = UGCNetMockAttempt.query.filter_by(
            user_id=user_id, is_completed=True
        ).all()
        
        practice_attempts = UGCNetPracticeAttempt.query.filter_by(
            user_id=user_id, is_completed=True
        ).all()
        
        # Calculate total questions and accuracy
        total_questions = 0
        total_correct = 0
        total_hours = 0
        
        for attempt in mock_attempts:
            if attempt.total_questions and attempt.correct_answers is not None:
                total_questions += attempt.total_questions
                total_correct += attempt.correct_answers
            
            # Estimate study time (assuming 2 minutes per question + review time)
            if attempt.total_questions:
                estimated_time = (attempt.total_questions * 2 + 30) / 60  # Convert to hours
                total_hours += estimated_time
        
        for attempt in practice_attempts:
            if attempt.total_questions and attempt.correct_answers is not None:
                total_questions += attempt.total_questions
                total_correct += attempt.correct_answers
            
            # Estimate study time
            if attempt.total_questions:
                estimated_time = (attempt.total_questions * 1.5 + 15) / 60  # Convert to hours
                total_hours += estimated_time
        
        # Update metrics
        metrics.total_study_hours = total_hours
        metrics.total_questions_attempted = total_questions
        metrics.total_questions_correct = total_correct
        metrics.overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
    
    def _calculate_learning_patterns(self, user_id, metrics):
        """Calculate learning patterns and study habits"""
        # Get recent attempts for pattern analysis
        recent_attempts = []
        
        # Get attempts from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        mock_attempts = UGCNetMockAttempt.query.filter(
            UGCNetMockAttempt.user_id == user_id,
            UGCNetMockAttempt.created_at >= thirty_days_ago
        ).all()
        
        practice_attempts = UGCNetPracticeAttempt.query.filter(
            UGCNetPracticeAttempt.user_id == user_id,
            UGCNetPracticeAttempt.created_at >= thirty_days_ago
        ).all()
        
        # Analyze time patterns
        hour_counts = {}
        session_durations = []
        study_dates = set()
        
        for attempt in mock_attempts + practice_attempts:
            # Track study hour preference
            hour = attempt.created_at.hour
            if hour < 12:
                time_period = 'morning'
            elif hour < 17:
                time_period = 'afternoon'
            elif hour < 21:
                time_period = 'evening'
            else:
                time_period = 'night'
            
            hour_counts[time_period] = hour_counts.get(time_period, 0) + 1
            
            # Track session duration (estimate)
            if attempt.total_questions:
                estimated_duration = attempt.total_questions * 2  # 2 minutes per question
                session_durations.append(estimated_duration)
            
            # Track study dates
            study_dates.add(attempt.created_at.date())
        
        # Determine preferred study time
        if hour_counts:
            preferred_time = max(hour_counts.keys(), key=lambda k: hour_counts[k])
            metrics.preferred_study_time = preferred_time
        
        # Calculate average session duration
        if session_durations:
            metrics.average_session_duration = sum(session_durations) / len(session_durations)
        
        # Calculate study consistency (how many days studied in last 30 days)
        study_days = len(study_dates)
        consistency_score = min(study_days / 30 * 100, 100)
        metrics.study_consistency_score = consistency_score
    
    def _calculate_strengths_weaknesses(self, user_id, metrics):
        """Calculate subject and chapter strengths and weaknesses"""
        # Subject-wise performance
        subject_performance = {}
        
        # Analyze mock attempts
        mock_attempts = UGCNetMockAttempt.query.filter_by(
            user_id=user_id, is_completed=True
        ).all()
        
        for attempt in mock_attempts:
            if attempt.mock_test and attempt.mock_test.subject and attempt.percentage is not None:
                subject_id = attempt.mock_test.subject.id
                if subject_id not in subject_performance:
                    subject_performance[subject_id] = []
                subject_performance[subject_id].append(attempt.percentage)
        
        # Analyze practice attempts
        practice_attempts = UGCNetPracticeAttempt.query.filter_by(
            user_id=user_id, is_completed=True
        ).all()
        
        for attempt in practice_attempts:
            if attempt.subject and attempt.percentage is not None:
                subject_id = attempt.subject.id
                if subject_id not in subject_performance:
                    subject_performance[subject_id] = []
                subject_performance[subject_id].append(attempt.percentage)
        
        # Calculate subject strengths and weaknesses
        strong_subjects = []
        weak_subjects = []
        
        for subject_id, scores in subject_performance.items():
            avg_score = sum(scores) / len(scores)
            if avg_score >= 70:
                strong_subjects.append(subject_id)
            elif avg_score < 50:
                weak_subjects.append(subject_id)
        
        metrics.strong_subjects = strong_subjects
        metrics.weak_subjects = weak_subjects
        
        # Chapter-wise analysis (simplified - would need more detailed tracking)
        # For now, we'll use placeholder logic
        metrics.strong_chapters = []
        metrics.weak_chapters = []
    
    def _calculate_progress_tracking(self, user_id, metrics):
        """Calculate progress trends and improvement patterns"""
        # Get attempts from last 60 days for trend analysis
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Recent 30 days
        recent_attempts = []
        mock_attempts = UGCNetMockAttempt.query.filter(
            UGCNetMockAttempt.user_id == user_id,
            UGCNetMockAttempt.is_completed == True,
            UGCNetMockAttempt.created_at >= thirty_days_ago,
            UGCNetMockAttempt.percentage != None
        ).all()
        
        practice_attempts = UGCNetPracticeAttempt.query.filter(
            UGCNetPracticeAttempt.user_id == user_id,
            UGCNetPracticeAttempt.is_completed == True,
            UGCNetPracticeAttempt.created_at >= thirty_days_ago,
            UGCNetPracticeAttempt.percentage != None
        ).all()
        
        recent_scores = [a.percentage for a in mock_attempts + practice_attempts]
        
        # Previous 30 days (30-60 days ago)
        prev_attempts = []
        prev_mock_attempts = UGCNetMockAttempt.query.filter(
            UGCNetMockAttempt.user_id == user_id,
            UGCNetMockAttempt.is_completed == True,
            UGCNetMockAttempt.created_at >= sixty_days_ago,
            UGCNetMockAttempt.created_at < thirty_days_ago,
            UGCNetMockAttempt.percentage != None
        ).all()
        
        prev_practice_attempts = UGCNetPracticeAttempt.query.filter(
            UGCNetPracticeAttempt.user_id == user_id,
            UGCNetPracticeAttempt.is_completed == True,
            UGCNetPracticeAttempt.created_at >= sixty_days_ago,
            UGCNetPracticeAttempt.created_at < thirty_days_ago,
            UGCNetPracticeAttempt.percentage != None
        ).all()
        
        prev_scores = [a.percentage for a in prev_mock_attempts + prev_practice_attempts]
        
        # Calculate improvement trend
        if recent_scores and prev_scores:
            recent_avg = sum(recent_scores) / len(recent_scores)
            prev_avg = sum(prev_scores) / len(prev_scores)
            improvement = recent_avg - prev_avg
            metrics.improvement_trend = improvement
            
            # Check for plateau (improvement < 2% over 30 days)
            metrics.plateau_warning = abs(improvement) < 2
            
            # Update last significant improvement
            if improvement > 5:  # Significant improvement threshold
                metrics.last_significant_improvement = datetime.utcnow()
        else:
            metrics.improvement_trend = 0
            metrics.plateau_warning = False
    
    def _calculate_ai_insights(self, user_id, metrics):
        """Calculate AI-based insights and recommendations"""
        # Determine learning style based on performance patterns
        # This is simplified - in reality would need more complex analysis
        if metrics.overall_accuracy >= 70:
            learning_style = 'mixed'  # Performing well across different question types
        elif metrics.study_consistency_score >= 80:
            learning_style = 'disciplined'  # Regular study pattern
        else:
            learning_style = 'adaptive'  # Needs structured approach
        
        metrics.learning_style = learning_style
        
        # Recommend daily study hours based on performance and goals
        if metrics.overall_accuracy < 40:
            recommended_hours = 4.0  # Need intensive study
        elif metrics.overall_accuracy < 60:
            recommended_hours = 3.0  # Moderate study needed
        else:
            recommended_hours = 2.0  # Maintenance level
        
        metrics.recommended_daily_hours = recommended_hours
        
        # Estimate exam readiness
        readiness_factors = []
        
        # Performance factor (0-40 points)
        performance_score = min(metrics.overall_accuracy, 40) if metrics.overall_accuracy else 0
        readiness_factors.append(performance_score)
        
        # Consistency factor (0-30 points)
        consistency_score = min(metrics.study_consistency_score * 0.3, 30)
        readiness_factors.append(consistency_score)
        
        # Progress factor (0-20 points)
        progress_score = max(0, min(metrics.improvement_trend * 2, 20))
        readiness_factors.append(progress_score)
        
        # Experience factor (0-10 points)
        experience_score = min(metrics.total_questions_attempted / 100, 10)
        readiness_factors.append(experience_score)
        
        estimated_readiness = sum(readiness_factors)
        metrics.estimated_readiness_percentage = min(estimated_readiness, 100)
    
    def create_study_session(self, user_id, session_data):
        """Create a new study session record"""
        try:
            session = UserStudySession(
                user_id=user_id,
                session_type=session_data.get('session_type', 'practice'),
                subject_id=session_data.get('subject_id'),
                chapter_ids=session_data.get('chapter_ids', []),
                start_time=session_data.get('start_time', datetime.utcnow()),
                end_time=session_data.get('end_time'),
                duration_minutes=session_data.get('duration_minutes'),
                questions_attempted=session_data.get('questions_attempted', 0),
                questions_correct=session_data.get('questions_correct', 0),
                accuracy_percentage=session_data.get('accuracy_percentage'),
                average_time_per_question=session_data.get('average_time_per_question'),
                difficulty_level=session_data.get('difficulty_level'),
                focus_score=session_data.get('focus_score'),
                completion_rate=session_data.get('completion_rate'),
                device_type=session_data.get('device_type', 'desktop')
            )
            
            db.session.add(session)
            db.session.commit()
            
            # Trigger metrics recalculation
            self.calculate_all_user_metrics(user_id)
            
            return session
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error creating study session: {str(e)}")
    
    def get_user_learning_insights(self, user_id):
        """Get comprehensive learning insights for a user"""
        try:
            metrics = UserLearningMetrics.query.filter_by(user_id=user_id).first()
            
            if not metrics:
                # Calculate metrics if they don't exist
                metrics = self.calculate_all_user_metrics(user_id)
            
            # Get recent study sessions
            recent_sessions = UserStudySession.query.filter_by(
                user_id=user_id
            ).order_by(UserStudySession.created_at.desc()).limit(10).all()
            
            return {
                'metrics': metrics.to_dict(),
                'recent_sessions': [session.to_dict() for session in recent_sessions],
                'insights': {
                    'readiness_level': self._get_readiness_level(metrics.estimated_readiness_percentage),
                    'study_recommendations': self._get_study_recommendations(metrics),
                    'focus_areas': self._get_focus_areas(metrics)
                }
            }
            
        except Exception as e:
            raise Exception(f"Error getting learning insights: {str(e)}")
    
    def _get_readiness_level(self, readiness_percentage):
        """Convert readiness percentage to level"""
        if readiness_percentage >= 80:
            return 'excellent'
        elif readiness_percentage >= 60:
            return 'good'
        elif readiness_percentage >= 40:
            return 'fair'
        else:
            return 'needs_improvement'
    
    def _get_study_recommendations(self, metrics):
        """Get study recommendations based on metrics"""
        recommendations = []
        
        if metrics.overall_accuracy < 40:
            recommendations.append('Focus on fundamental concepts')
        
        if metrics.study_consistency_score < 50:
            recommendations.append('Establish regular study routine')
        
        if metrics.improvement_trend < 0:
            recommendations.append('Review study methods and take breaks')
        
        if metrics.plateau_warning:
            recommendations.append('Try different study techniques')
        
        return recommendations
    
    def _get_focus_areas(self, metrics):
        """Get focus areas based on weaknesses"""
        focus_areas = []
        
        if metrics.weak_subjects:
            subjects = Subject.query.filter(Subject.id.in_(metrics.weak_subjects)).all()
            for subject in subjects:
                focus_areas.append(f'Improve {subject.name} performance')
        
        if metrics.weak_chapters:
            chapters = Chapter.query.filter(Chapter.id.in_(metrics.weak_chapters)).all()
            for chapter in chapters:
                focus_areas.append(f'Focus on {chapter.name}')
        
        return focus_areas
