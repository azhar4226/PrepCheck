"""
AI Study Recommendation Service
Generates personalized study recommendations and plans based on user performance data
"""
from datetime import datetime, timedelta
from app.services.user_metrics_service import UserMetricsService
from app.services.learning_metrics_calculator import LearningMetricsCalculator
from app.models import Subject, Chapter, QuestionBank, UserLearningMetrics
from app import db
import random


class AIStudyRecommendationService:
    """Service for generating AI-powered study recommendations and plans"""
    
    def __init__(self):
        self.metrics_service = UserMetricsService()
        self.learning_calculator = LearningMetricsCalculator()
    
    def generate_study_recommendations(self, user_id, max_recommendations=5):
        """Generate personalized study recommendations based on user performance"""
        try:
            # Get comprehensive metrics
            metrics = self.metrics_service.get_comprehensive_user_metrics(user_id)
            
            # Get or calculate learning metrics
            learning_metrics = UserLearningMetrics.query.filter_by(user_id=user_id).first()
            if not learning_metrics:
                learning_metrics = self.learning_calculator.calculate_all_user_metrics(user_id)
            
            recommendations = []
            
            # Analyze performance and generate recommendations
            recommendations.extend(self._performance_based_recommendations(metrics))
            recommendations.extend(self._subject_based_recommendations(metrics))
            recommendations.extend(self._pattern_based_recommendations(metrics))
            recommendations.extend(self._progress_based_recommendations(metrics))
            if learning_metrics:
                recommendations.extend(self._learning_style_recommendations(learning_metrics))
            
            # Sort by priority and limit
            recommendations.sort(key=lambda x: self._get_priority_score(x['priority']))
            
            return recommendations[:max_recommendations]
            
        except Exception as e:
            raise Exception(f"Error generating study recommendations: {str(e)}")
    
    def generate_study_plan(self, user_id, plan_duration_weeks=12):
        """Generate a personalized study plan based on user metrics"""
        try:
            # Get comprehensive metrics
            metrics = self.metrics_service.get_comprehensive_user_metrics(user_id)
            user_info = metrics['user_info']
            performance = metrics['performance_metrics']
            subject_performance = metrics['subject_performance']
            weaknesses = metrics['chapter_weaknesses']
            study_patterns = metrics['study_patterns']
            
            # Determine user's preparation level
            preparation_level = self._determine_preparation_level(performance)
            
            # Get user's subject
            user_subject = None
            if user_info['subject_id']:
                user_subject = Subject.query.get(user_info['subject_id'])
            
            # Generate weekly plan
            weekly_plan = []
            
            # Week distribution based on preparation level
            if preparation_level == 'beginner':
                foundation_weeks = plan_duration_weeks // 2
                practice_weeks = plan_duration_weeks // 3
                revision_weeks = plan_duration_weeks - foundation_weeks - practice_weeks
            elif preparation_level == 'intermediate':
                foundation_weeks = plan_duration_weeks // 3
                practice_weeks = plan_duration_weeks // 2
                revision_weeks = plan_duration_weeks - foundation_weeks - practice_weeks
            else:  # advanced
                foundation_weeks = plan_duration_weeks // 4
                practice_weeks = plan_duration_weeks // 2
                revision_weeks = plan_duration_weeks - foundation_weeks - practice_weeks
            
            current_week = 1
            
            # Foundation weeks
            for week in range(foundation_weeks):
                weekly_plan.append(self._create_foundation_week(
                    current_week, user_subject, weaknesses, preparation_level
                ))
                current_week += 1
            
            # Practice weeks
            for week in range(practice_weeks):
                weekly_plan.append(self._create_practice_week(
                    current_week, user_subject, performance, subject_performance
                ))
                current_week += 1
            
            # Revision weeks
            for week in range(revision_weeks):
                weekly_plan.append(self._create_revision_week(
                    current_week, user_subject, weaknesses
                ))
                current_week += 1
            
            # Generate plan metadata
            plan_title = f"Personalized {user_subject.name if user_subject else 'UGC NET'} Study Plan"
            plan_duration = f"{plan_duration_weeks} weeks"
            
            return {
                'title': plan_title,
                'duration': plan_duration,
                'preparation_level': preparation_level,
                'total_weeks': plan_duration_weeks,
                'weekly_plan': weekly_plan,
                'generated_at': datetime.utcnow().isoformat(),
                'based_on_metrics': {
                    'total_attempts': performance['total_attempts'],
                    'average_score': performance['average_score'],
                    'study_frequency': study_patterns['study_frequency']
                }
            }
            
        except Exception as e:
            raise Exception(f"Error generating study plan: {str(e)}")
    
    def _performance_based_recommendations(self, metrics):
        """Generate recommendations based on overall performance"""
        performance = metrics['performance_metrics']
        recommendations = []
        
        # Low completion rate
        if performance['completion_rate'] < 70:
            recommendations.append({
                'title': 'Improve Test Completion Habits',
                'description': f"You complete only {performance['completion_rate']:.1f}% of started tests. Focus on finishing tests to get accurate performance feedback.",
                'icon': 'bi bi-check-circle',
                'priority': 'high',
                'estimated_time': '15 mins per test',
                'action_type': 'habit_improvement'
            })
        
        # Low average score
        if performance['average_score'] < 40:
            recommendations.append({
                'title': 'Strengthen Fundamental Concepts',
                'description': f"Your average score is {performance['average_score']:.1f}%. Focus on building strong fundamentals before attempting mock tests.",
                'icon': 'bi bi-book',
                'priority': 'high',
                'estimated_time': '3-4 hours/day',
                'action_type': 'concept_building'
            })
        elif performance['average_score'] < 55:
            recommendations.append({
                'title': 'Bridge Knowledge Gaps',
                'description': f"Your average score is {performance['average_score']:.1f}%. Identify and work on specific knowledge gaps.",
                'icon': 'bi bi-puzzle',
                'priority': 'medium',
                'estimated_time': '2-3 hours/day',
                'action_type': 'gap_filling'
            })
        
        # Declining trend
        if performance['improvement_trend'] < -5:
            recommendations.append({
                'title': 'Address Performance Decline',
                'description': f"Your scores have declined by {abs(performance['improvement_trend']):.1f}% recently. Review your study approach and take breaks if needed.",
                'icon': 'bi bi-arrow-down-circle',
                'priority': 'high',
                'estimated_time': '1-2 hours/day',
                'action_type': 'performance_recovery'
            })
        
        # Low consistency
        if performance['consistency_score'] < 50:
            recommendations.append({
                'title': 'Improve Score Consistency',
                'description': f"Your performance varies significantly (consistency: {performance['consistency_score']:.1f}%). Focus on regular, structured practice.",
                'icon': 'bi bi-graph-up',
                'priority': 'medium',
                'estimated_time': '1-2 hours/day',
                'action_type': 'consistency_building'
            })
        
        return recommendations
    
    def _subject_based_recommendations(self, metrics):
        """Generate recommendations based on subject performance"""
        subject_performance = metrics['subject_performance']
        recommendations = []
        
        # Find weakest subjects
        weak_subjects = [s for s in subject_performance if s['performance_level'] in ['needs_improvement', 'average']]
        
        for subject in weak_subjects[:2]:  # Top 2 weakest subjects
            if subject['average_score'] < 40:
                priority = 'high'
                time_allocation = '2-3 hours/day'
            else:
                priority = 'medium'
                time_allocation = '1-2 hours/day'
            
            recommendations.append({
                'title': f'Focus on {subject["subject_name"]}',
                'description': f"Your average score in {subject['subject_name']} is {subject['average_score']:.1f}%. This subject needs immediate attention.",
                'icon': 'bi bi-bullseye',
                'priority': priority,
                'estimated_time': time_allocation,
                'action_type': 'subject_focus',
                'subject_id': subject['subject_id']
            })
        
        return recommendations
    
    def _pattern_based_recommendations(self, metrics):
        """Generate recommendations based on study patterns"""
        patterns = metrics['study_patterns']
        recommendations = []
        
        # Infrequent study pattern
        if patterns['study_frequency'] in ['inactive', 'occasional']:
            recommendations.append({
                'title': 'Establish Regular Study Routine',
                'description': f"Your study frequency is {patterns['study_frequency']}. Consistent daily practice is crucial for UGC NET preparation.",
                'icon': 'bi bi-calendar-check',
                'priority': 'high',
                'estimated_time': '2-3 hours/day',
                'action_type': 'routine_building'
            })
        
        # Long gap since last activity
        if patterns['last_activity']:
            last_activity = datetime.fromisoformat(patterns['last_activity'].replace('Z', '+00:00'))
            days_since_activity = (datetime.utcnow() - last_activity).days
            
            if days_since_activity > 7:
                recommendations.append({
                    'title': 'Resume Regular Practice',
                    'description': f"It's been {days_since_activity} days since your last practice. Get back to regular study schedule.",
                    'icon': 'bi bi-play-circle',
                    'priority': 'high',
                    'estimated_time': '1-2 hours/day',
                    'action_type': 'resume_practice'
                })
        
        return recommendations
    
    def _progress_based_recommendations(self, metrics):
        """Generate recommendations based on progress trends"""
        trends = metrics['progress_trends']
        recommendations = []
        
        # Stable but low performance
        if trends['trend_direction'] == 'stable' and metrics['performance_metrics']['average_score'] < 50:
            recommendations.append({
                'title': 'Break Performance Plateau',
                'description': "Your scores have plateaued. Try different study methods, focus on weak areas, or increase practice intensity.",
                'icon': 'bi bi-arrow-up-right',
                'priority': 'medium',
                'estimated_time': '2-3 hours/day',
                'action_type': 'plateau_breaking'
            })
        
        # Improving trend
        if trends['trend_direction'] == 'improving':
            recommendations.append({
                'title': 'Maintain Improvement Momentum',
                'description': f"Great job! Your scores are improving by {trends['improvement_rate']:.1f}%. Keep up the current study approach.",
                'icon': 'bi bi-trophy',
                'priority': 'low',
                'estimated_time': 'Current routine',
                'action_type': 'momentum_maintenance'
            })
        
        return recommendations
    
    def _determine_preparation_level(self, performance):
        """Determine user's preparation level based on performance metrics"""
        avg_score = performance['average_score']
        total_attempts = performance['total_attempts']
        
        if total_attempts < 5:
            return 'beginner'
        elif avg_score < 40:
            return 'beginner'
        elif avg_score < 60:
            return 'intermediate'
        else:
            return 'advanced'
    
    def _create_foundation_week(self, week_number, subject, weaknesses, level):
        """Create a foundation building week"""
        tasks = []
        
        if level == 'beginner':
            daily_hours = 4
            tasks = [
                {'title': 'Read fundamental concepts and syllabus', 'duration': '2 hours', 'completed': False},
                {'title': 'Complete basic concept quizzes', 'duration': '1 hour', 'completed': False},
                {'title': 'Take notes and create summary', 'duration': '1 hour', 'completed': False},
                {'title': 'Review previous day concepts', 'duration': '30 mins', 'completed': False}
            ]
        else:
            daily_hours = 3
            tasks = [
                {'title': 'Review core concepts', 'duration': '1.5 hours', 'completed': False},
                {'title': 'Solve conceptual questions', 'duration': '1 hour', 'completed': False},
                {'title': 'Focus on identified weak areas', 'duration': '30 mins', 'completed': False}
            ]
        
        # Add subject-specific tasks if subject is available
        if subject:
            tasks.insert(0, {
                'title': f'Study {subject.name} fundamentals', 
                'duration': f'{daily_hours//2} hours', 
                'completed': False
            })
        
        return {
            'title': f'Foundation Building',
            'description': 'Establish strong fundamental understanding',
            'completed': False,
            'tasks': tasks,
            'focus_area': 'fundamentals',
            'estimated_daily_hours': daily_hours
        }
    
    def _create_practice_week(self, week_number, subject, performance, subject_performance):
        """Create a practice-focused week"""
        tasks = []
        
        if performance['average_score'] < 40:
            # Focus on chapter-wise practice
            tasks = [
                {'title': 'Chapter-wise practice tests', 'duration': '2 hours', 'completed': False},
                {'title': 'Review incorrect answers', 'duration': '1 hour', 'completed': False},
                {'title': 'Concept clarification', 'duration': '1 hour', 'completed': False},
                {'title': 'Weekly progress assessment', 'duration': '30 mins', 'completed': False}
            ]
        else:
            # Mix of topic tests and mock tests
            tasks = [
                {'title': 'Mixed topic practice tests', 'duration': '1.5 hours', 'completed': False},
                {'title': 'One full-length mock test', 'duration': '3 hours', 'completed': False},
                {'title': 'Detailed error analysis', 'duration': '1 hour', 'completed': False},
                {'title': 'Speed and accuracy drills', 'duration': '45 mins', 'completed': False}
            ]
        
        return {
            'title': f'Intensive Practice',
            'description': 'Build speed, accuracy, and confidence through practice',
            'completed': False,
            'tasks': tasks,
            'focus_area': 'practice',
            'estimated_daily_hours': 3
        }
    
    def _create_revision_week(self, week_number, subject, weaknesses):
        """Create a revision-focused week"""
        tasks = [
            {'title': 'Quick revision of all topics', 'duration': '2 hours', 'completed': False},
            {'title': 'Focus on previously weak areas', 'duration': '1.5 hours', 'completed': False},
            {'title': 'Timed mock test', 'duration': '3 hours', 'completed': False},
            {'title': 'Final doubt clearing', 'duration': '1 hour', 'completed': False}
        ]
        
        # Add weakness-specific tasks
        if weaknesses:
            for weakness in weaknesses[:2]:  # Top 2 weaknesses
                tasks.insert(1, {
                    'title': f'Extra practice on {weakness["chapter_name"]}',
                    'duration': '45 mins',
                    'completed': False
                })
        
        return {
            'title': f'Comprehensive Revision',
            'description': 'Consolidate knowledge and boost confidence',
            'completed': False,
            'tasks': tasks,
            'focus_area': 'revision',
            'estimated_daily_hours': 2.5
        }
    
    def _learning_style_recommendations(self, learning_metrics):
        """Generate recommendations based on learning style and patterns"""
        recommendations = []
        
        # Readiness-based recommendations
        if learning_metrics.estimated_readiness_percentage < 30:
            recommendations.append({
                'title': 'Focus on Foundation Building',
                'description': f'Your exam readiness is {learning_metrics.estimated_readiness_percentage:.1f}%. Start with basic concepts and build systematically.',
                'icon': 'bi bi-building',
                'priority': 'high',
                'estimated_time': f'{learning_metrics.recommended_daily_hours} hours/day',
                'action_type': 'foundation_building'
            })
        elif learning_metrics.estimated_readiness_percentage < 60:
            recommendations.append({
                'title': 'Intensive Practice Required',
                'description': f'Your exam readiness is {learning_metrics.estimated_readiness_percentage:.1f}%. Focus on extensive practice and mock tests.',
                'icon': 'bi bi-lightning',
                'priority': 'high',
                'estimated_time': f'{learning_metrics.recommended_daily_hours} hours/day',
                'action_type': 'intensive_practice'
            })
        
        # Study consistency recommendations
        if learning_metrics.study_consistency_score < 50:
            recommendations.append({
                'title': 'Improve Study Consistency',
                'description': f'Your study consistency is {learning_metrics.study_consistency_score:.1f}%. Establish a regular daily study routine.',
                'icon': 'bi bi-calendar-check',
                'priority': 'high',
                'estimated_time': '30 mins daily routine',
                'action_type': 'consistency_building'
            })
        
        # Learning style specific recommendations
        if learning_metrics.learning_style == 'disciplined':
            recommendations.append({
                'title': 'Leverage Your Discipline',
                'description': 'You have excellent study discipline. Focus on challenging topics and advanced problem-solving.',
                'icon': 'bi bi-award',
                'priority': 'medium',
                'estimated_time': '2-3 hours/day',
                'action_type': 'advanced_practice'
            })
        elif learning_metrics.learning_style == 'adaptive':
            recommendations.append({
                'title': 'Structured Learning Approach',
                'description': 'You learn best with structure. Follow a detailed study plan with clear milestones.',
                'icon': 'bi bi-list-check',
                'priority': 'medium',
                'estimated_time': f'{learning_metrics.recommended_daily_hours} hours/day',
                'action_type': 'structured_learning'
            })
        
        # Plateau warning
        if learning_metrics.plateau_warning:
            recommendations.append({
                'title': 'Break Through Performance Plateau',
                'description': 'Your performance has plateaued. Try new study methods, take mock tests, or review weak areas.',
                'icon': 'bi bi-arrow-up-right',
                'priority': 'high',
                'estimated_time': '1-2 hours/day',
                'action_type': 'plateau_breaking'
            })
        
        # Subject-specific recommendations based on weak subjects
        if learning_metrics.weak_subjects:
            subject_names = []
            if len(learning_metrics.weak_subjects) > 0:
                subjects = Subject.query.filter(Subject.id.in_(learning_metrics.weak_subjects[:2])).all()
                subject_names = [s.name for s in subjects]
            
            if subject_names:
                recommendations.append({
                    'title': f'Focus on Weak Subjects',
                    'description': f'You need improvement in: {", ".join(subject_names)}. Dedicate extra time to these subjects.',
                    'icon': 'bi bi-bullseye',
                    'priority': 'high',
                    'estimated_time': '2-3 hours/day',
                    'action_type': 'subject_improvement'
                })
        
        return recommendations
    
    def _get_priority_score(self, priority):
        """Convert priority to numeric score for sorting"""
        priority_scores = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return priority_scores.get(priority, 0)
