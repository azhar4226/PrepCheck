"""
User Analytics Service
Handles user analytics and reporting for admin
"""
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import desc
from app import db
from app.models import User, UGCNetMockAttempt, UGCNetPracticeAttempt, UGCNetMockTest


class UserAnalyticsService:
    """Service for user analytics operations"""
    
    def get_user_analytics(self, user_id, days=30, subject_id=None, test_type='all'):
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
            
            # Get attempts based on test type
            mock_attempts = mock_attempts_query.all() if test_type in ('all', 'mock') else []
            practice_attempts = practice_attempts_query.all() if test_type in ('all', 'practice') else []
            
            attempts = mock_attempts + practice_attempts if test_type == 'all' else mock_attempts if test_type == 'mock' else practice_attempts
            
            if not attempts:
                return self.get_empty_analytics()
            
            # Calculate overall stats
            total_score = sum(a.percentage for a in attempts if a.percentage is not None)
            total_correct = sum(a.correct_answers for a in attempts if a.correct_answers is not None)
            total_questions = sum(a.total_questions for a in attempts if a.total_questions is not None)
            total_time = sum(a.time_taken for a in attempts if a.time_taken is not None)
            
            return {
                "snapshot": {
                    "overall_average_score": round(total_score / len(attempts), 2) if attempts else 0,
                    "overall_accuracy": round((total_correct / total_questions * 100) if total_questions > 0 else 0, 2),
                    "total_tests_taken": len(attempts),
                    "total_time_studied": total_time
                },
                "performance_over_time": self._calculate_performance_over_time(attempts),
                "strengths": self._calculate_strengths(attempts),
                "weaknesses": self._calculate_weaknesses(attempts),
                "performance_by_paper": self._calculate_paper_performance(attempts),
                "accuracy_by_difficulty": self._calculate_accuracy_by_difficulty(attempts)
            }
            
        except Exception as e:
            raise Exception(f"Failed to get user analytics: {str(e)}")

    def _calculate_performance_over_time(self, attempts):
        """Calculate performance trends over time"""
        attempts_by_date = defaultdict(list)
        for attempt in attempts:
            if attempt.completed_at and attempt.percentage is not None:
                date_key = attempt.completed_at.strftime('%Y-%m-%d')
                attempts_by_date[date_key].append(attempt.percentage)
        
        return [
            {
                "date": date,
                "score": round(sum(scores) / len(scores), 2)
            }
            for date, scores in sorted(attempts_by_date.items())
        ]

    def _calculate_strengths(self, attempts):
        """Calculate areas of strength"""
        topic_scores = defaultdict(lambda: {"correct": 0, "total": 0})
        
        for attempt in attempts:
            if hasattr(attempt, 'get_topic_wise_performance'):
                topic_perf = attempt.get_topic_wise_performance()
                for topic, scores in topic_perf.items():
                    topic_scores[topic]["correct"] += scores["correct"]
                    topic_scores[topic]["total"] += scores["total"]
        
        strengths = []
        for topic, scores in topic_scores.items():
            if scores["total"] > 0:
                percentage = (scores["correct"] / scores["total"]) * 100
                if percentage >= 70:
                    strengths.append({"topic": topic, "score": round(percentage, 2)})
        
        return sorted(strengths, key=lambda x: x["score"], reverse=True)[:5]

    def _calculate_weaknesses(self, attempts):
        """Calculate areas needing improvement"""
        topic_scores = defaultdict(lambda: {"correct": 0, "total": 0})
        
        for attempt in attempts:
            if hasattr(attempt, 'get_topic_wise_performance'):
                topic_perf = attempt.get_topic_wise_performance()
                for topic, scores in topic_perf.items():
                    topic_scores[topic]["correct"] += scores["correct"]
                    topic_scores[topic]["total"] += scores["total"]
        
        weaknesses = []
        for topic, scores in topic_scores.items():
            if scores["total"] > 0:
                percentage = (scores["correct"] / scores["total"]) * 100
                if percentage <= 50:
                    weaknesses.append({"topic": topic, "score": round(percentage, 2)})
        
        return sorted(weaknesses, key=lambda x: x["score"])[:5]

    def _calculate_paper_performance(self, attempts):
        """Calculate performance by paper type"""
        mock_attempts = [a for a in attempts if isinstance(a, UGCNetMockAttempt)]
        paper1_scores = [a.paper1_score for a in mock_attempts if a.paper1_score is not None]
        paper2_scores = [a.paper2_score for a in mock_attempts if a.paper2_score is not None]
        
        return {
            "Paper 1": round(sum(paper1_scores) / len(paper1_scores), 2) if paper1_scores else 0,
            "Paper 2": round(sum(paper2_scores) / len(paper2_scores), 2) if paper2_scores else 0
        }

    def _calculate_accuracy_by_difficulty(self, attempts):
        """Calculate accuracy by question difficulty"""
        difficulty_scores = defaultdict(lambda: {"correct": 0, "total": 0})
        
        for attempt in attempts:
            if hasattr(attempt, 'get_difficulty_wise_performance'):
                diff_perf = attempt.get_difficulty_wise_performance()
                for diff, scores in diff_perf.items():
                    difficulty_scores[diff]["correct"] += scores["correct"]
                    difficulty_scores[diff]["total"] += scores["total"]
        
        return {
            diff: round((scores["correct"] / scores["total"] * 100), 2) if scores["total"] > 0 else 0
            for diff, scores in difficulty_scores.items()
        }

    def get_empty_analytics(self):
        """Return empty analytics structure"""
        return {
            "snapshot": {
                "overall_average_score": 0,
                "overall_accuracy": 0,
                "total_tests_taken": 0,
                "total_time_studied": 0
            },
            "performance_over_time": [],
            "strengths": [],
            "weaknesses": [],
            "performance_by_paper": {
                "Paper 1": 0,
                "Paper 2": 0
            },
            "accuracy_by_difficulty": {
                "Easy": 0,
                "Medium": 0,
                "Hard": 0
            }
        }

    def export_user_analytics(self, user_id, format_type='pdf'):
        """Export user analytics in specified format"""
        try:
            analytics_data = self.get_user_analytics(user_id)
            if format_type == 'pdf':
                return self._generate_pdf_report(analytics_data)
            elif format_type == 'csv':
                return self._generate_csv_report(analytics_data)
            else:
                raise ValueError(f'Unsupported export format: {format_type}')
        except Exception as e:
            raise Exception(f'Failed to export analytics: {str(e)}')

    def _generate_pdf_report(self, analytics_data):
        """Generate PDF report from analytics data"""
        # TODO: Implement PDF generation
        return None

    def _generate_csv_report(self, analytics_data):
        """Generate CSV report from analytics data"""
        # TODO: Implement CSV generation
        return None
