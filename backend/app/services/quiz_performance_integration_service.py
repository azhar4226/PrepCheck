from datetime import datetime
from app import db
from app.models.models import QuestionBank, QuestionPerformance, QuizAttempt, Question
from app.services.question_bank_service import QuestionBankService
from typing import Dict, List, Optional
import json

class QuizPerformanceIntegrationService:
    """Service to integrate quiz attempts with question bank performance tracking"""
    
    @staticmethod
    def track_quiz_attempt_performance(attempt: QuizAttempt, question_time_data: Optional[Dict] = None) -> Dict:
        """
        Track performance for all questions in a quiz attempt and store in question bank
        
        Args:
            attempt: The completed QuizAttempt object
            question_time_data: Optional dict of question_id -> time_taken mapping
            
        Returns:
            Dict with tracking results
        """
        if not attempt.is_completed:
            return {'error': 'Quiz attempt not completed'}
        
        results = {
            'tracked_questions': 0,
            'failed_tracking': 0,
            'question_bank_matches': 0,
            'new_performance_records': 0,
            'errors': []
        }
        
        try:
            # Get all questions and user answers
            questions = Question.query.filter_by(quiz_id=attempt.quiz_id).all()
            user_answers = attempt.get_answers()
            
            for question in questions:
                try:
                    # Try to find matching question in question bank
                    question_bank_entry = QuestionBankService.find_question_in_bank(
                        question_text=question.question_text,
                        options={
                            'A': question.option_a,
                            'B': question.option_b,
                            'C': question.option_c,
                            'D': question.option_d
                        },
                        correct_option=question.correct_option
                    )
                    
                    if question_bank_entry:
                        results['question_bank_matches'] += 1
                        
                        # Get user's answer for this question
                        question_id = str(question.id)
                        user_answer = user_answers.get(question_id, '').upper()
                        is_correct = user_answer == question.correct_option
                        
                        # Get time taken for this specific question (if available)
                        time_taken = None
                        if question_time_data and question_id in question_time_data:
                            time_taken = question_time_data[question_id]
                        elif attempt.time_taken and len(questions) > 0:
                            # Estimate average time per question
                            time_taken = attempt.time_taken // len(questions)
                        
                        # Create performance record
                        performance = QuestionPerformance(
                            question_bank_id=question_bank_entry.id,
                            user_id=attempt.user_id,
                            quiz_attempt_id=attempt.id,
                            selected_option=user_answer if user_answer else 'NONE',
                            is_correct=is_correct,
                            time_taken=time_taken,
                            difficulty_at_time=question_bank_entry.difficulty,
                            topic_at_time=question_bank_entry.topic,
                            answered_at=attempt.completed_at or datetime.utcnow()
                        )
                        
                        db.session.add(performance)
                        results['new_performance_records'] += 1
                        
                        # Update question bank usage stats
                        question_bank_entry.increment_usage()
                        
                    results['tracked_questions'] += 1
                    
                except Exception as e:
                    results['failed_tracking'] += 1
                    results['errors'].append(f"Question {question.id}: {str(e)}")
            
            # Commit all performance records
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            results['errors'].append(f"Database error: {str(e)}")
        
        return results
    
    @staticmethod
    def get_user_performance_summary(user_id: int) -> Dict:
        """Get comprehensive performance summary for a user"""
        try:
            # Get all user's quiz attempts
            attempts = QuizAttempt.query.filter_by(
                user_id=user_id, is_completed=True
            ).order_by(QuizAttempt.completed_at.desc()).all()
            
            # Get all user's question performances
            question_performances = QuestionPerformance.query.filter_by(
                user_id=user_id
            ).order_by(QuestionPerformance.answered_at.desc()).all()
            
            # Calculate overall stats
            total_questions_answered = len(question_performances)
            correct_answers = len([p for p in question_performances if p.is_correct])
            overall_accuracy = (correct_answers / total_questions_answered * 100) if total_questions_answered > 0 else 0
            
            # Topic breakdown
            topic_stats = {}
            for perf in question_performances:
                topic = perf.topic_at_time or 'Unknown'
                if topic not in topic_stats:
                    topic_stats[topic] = {'correct': 0, 'total': 0}
                topic_stats[topic]['total'] += 1
                if perf.is_correct:
                    topic_stats[topic]['correct'] += 1
            
            # Calculate topic accuracy rates
            topic_accuracy = {}
            for topic, stats in topic_stats.items():
                topic_accuracy[topic] = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            # Difficulty breakdown
            difficulty_stats = {}
            for perf in question_performances:
                diff = perf.difficulty_at_time or 'unknown'
                if diff not in difficulty_stats:
                    difficulty_stats[diff] = {'correct': 0, 'total': 0}
                difficulty_stats[diff]['total'] += 1
                if perf.is_correct:
                    difficulty_stats[diff]['correct'] += 1
            
            # Recent performance trend (last 10 attempts)
            recent_attempts = attempts[:10]
            recent_accuracy = []
            for attempt in recent_attempts:
                if attempt.total_marks > 0:
                    accuracy = (attempt.score / attempt.total_marks) * 100
                    recent_accuracy.append({
                        'date': attempt.completed_at.isoformat(),
                        'accuracy': round(accuracy, 2),
                        'quiz_title': attempt.quiz.title if attempt.quiz else 'Unknown'
                    })
            
            return {
                'summary': {
                    'total_quizzes_taken': len(attempts),
                    'total_questions_answered': total_questions_answered,
                    'overall_accuracy': round(overall_accuracy, 2),
                    'correct_answers': correct_answers,
                    'incorrect_answers': total_questions_answered - correct_answers
                },
                'topic_performance': {
                    topic: {
                        'accuracy': round(accuracy, 2),
                        'questions_answered': topic_stats[topic]['total'],
                        'correct_answers': topic_stats[topic]['correct']
                    }
                    for topic, accuracy in topic_accuracy.items()
                },
                'difficulty_performance': {
                    diff: {
                        'accuracy': round((stats['correct'] / stats['total'] * 100), 2),
                        'questions_answered': stats['total'],
                        'correct_answers': stats['correct']
                    }
                    for diff, stats in difficulty_stats.items()
                },
                'recent_performance': recent_accuracy,
                'tracking_enabled': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'tracking_enabled': False
            }
    
    @staticmethod
    def get_quiz_analytics_integration() -> Dict:
        """Get analytics showing integration between quizzes and question bank"""
        try:
            # Total quiz attempts with performance tracking
            total_attempts = QuizAttempt.query.filter_by(is_completed=True).count()
            tracked_questions = QuestionPerformance.query.count()
            
            # Questions with performance data
            questions_with_performance = db.session.query(QuestionBank.id).join(
                QuestionPerformance, QuestionBank.id == QuestionPerformance.question_bank_id
            ).distinct().count()
            
            total_question_bank_questions = QuestionBank.query.count()
            
            # Recent activity
            from sqlalchemy import func
            recent_performances = QuestionPerformance.query.filter(
                QuestionPerformance.answered_at >= func.date('now', '-7 days')
            ).count()
            
            # Top performing topics
            topic_performance = db.session.query(
                QuestionPerformance.topic_at_time,
                func.count(QuestionPerformance.id).label('total'),
                func.sum(func.cast(QuestionPerformance.is_correct, db.Integer)).label('correct')
            ).group_by(QuestionPerformance.topic_at_time).all()
            
            top_topics = []
            for topic, total, correct in topic_performance:
                if total >= 5:  # Only include topics with sufficient data
                    accuracy = (correct / total * 100) if total > 0 else 0
                    top_topics.append({
                        'topic': topic or 'Unknown',
                        'accuracy': round(accuracy, 2),
                        'total_attempts': total
                    })
            
            # Sort by accuracy
            top_topics.sort(key=lambda x: x['accuracy'], reverse=True)
            
            return {
                'integration_stats': {
                    'total_quiz_attempts': total_attempts,
                    'tracked_question_responses': tracked_questions,
                    'questions_with_performance_data': questions_with_performance,
                    'total_question_bank_questions': total_question_bank_questions,
                    'integration_coverage': round((questions_with_performance / max(1, total_question_bank_questions)) * 100, 2)
                },
                'recent_activity': {
                    'performances_last_7_days': recent_performances
                },
                'top_performing_topics': top_topics[:10],
                'tracking_active': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'tracking_active': False
            }
    
    @staticmethod
    def backfill_performance_data() -> Dict:
        """Backfill performance data for existing quiz attempts"""
        results = {
            'processed_attempts': 0,
            'tracked_questions': 0,
            'skipped_attempts': 0,
            'errors': []
        }
        
        try:
            # Get all completed attempts that don't have performance tracking yet
            attempts = QuizAttempt.query.filter_by(is_completed=True).all()
            
            for attempt in attempts:
                # Check if this attempt already has performance records
                existing_records = QuestionPerformance.query.filter_by(
                    quiz_attempt_id=attempt.id
                ).count()
                
                if existing_records > 0:
                    results['skipped_attempts'] += 1
                    continue
                
                # Track performance for this attempt
                tracking_result = QuizPerformanceIntegrationService.track_quiz_attempt_performance(attempt)
                
                if 'error' not in tracking_result:
                    results['processed_attempts'] += 1
                    results['tracked_questions'] += tracking_result.get('tracked_questions', 0)
                else:
                    results['errors'].append(f"Attempt {attempt.id}: {tracking_result['error']}")
            
            return results
            
        except Exception as e:
            return {
                'error': str(e),
                'processed_attempts': results['processed_attempts'],
                'tracked_questions': results['tracked_questions']
            }
