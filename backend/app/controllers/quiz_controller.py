from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import desc
from app import db, redis_client
from app.models import User, Quiz, Question, QuizAttempt, Subject, Chapter
from app.services.quiz_performance_integration_service import QuizPerformanceIntegrationService
from app.services.question_bank_service import QuestionBankService
import json

quiz_bp = Blueprint('quiz', __name__)

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))

@quiz_bp.route('/browse', methods=['GET'])
@jwt_required()
def browse_quizzes():
    """Browse available quizzes"""
    try:
        user = get_current_user()
        if not user or not user.is_active:
            return jsonify({'error': 'User not found'}), 404
        
        # Get active quizzes
        quizzes = Quiz.query.filter_by(is_active=True).all()
        
        quiz_list = []
        for quiz in quizzes:
            quiz_data = quiz.to_dict()
            # Add chapter and subject info
            if quiz.chapter:
                quiz_data['chapter_name'] = quiz.chapter.name
                quiz_data['subject_name'] = quiz.chapter.subject.name if quiz.chapter.subject else None
            quiz_list.append(quiz_data)
        
        return jsonify({
            'quizzes': quiz_list,
            'total': len(quiz_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@quiz_bp.route('/<int:quiz_id>/start', methods=['POST'])
@jwt_required()
def start_quiz(quiz_id):
    try:
        user = get_current_user()
        if not user or not user.is_active:
            return jsonify({'error': 'User not found'}), 404
        
        quiz = Quiz.query.get_or_404(quiz_id)
        if not quiz.is_active:
            return jsonify({'error': 'Quiz not available'}), 404
        
        # Check if user has an ongoing attempt
        ongoing_attempt = QuizAttempt.query.filter_by(
            user_id=user.id, quiz_id=quiz_id, is_completed=False
        ).first()
        
        if ongoing_attempt:
            # Check if time limit exceeded
            time_elapsed = (datetime.utcnow() - ongoing_attempt.started_at).total_seconds()
            if time_elapsed > (quiz.time_limit * 60):
                # Auto-complete the quiz
                ongoing_attempt.is_completed = True
                ongoing_attempt.completed_at = datetime.utcnow()
                ongoing_attempt.time_taken = int(time_elapsed)
                ongoing_attempt.calculate_score()
                db.session.commit()
                
                return jsonify({
                    'error': 'Previous attempt timed out',
                    'attempt': ongoing_attempt.to_dict()
                }), 400
            else:
                # Return ongoing attempt
                questions = Question.query.filter_by(quiz_id=quiz_id).all()
                return jsonify({
                    'message': 'Resuming ongoing attempt',
                    'attempt': ongoing_attempt.to_dict(),
                    'quiz': quiz.to_dict(),
                    'questions': [q.to_dict(include_answer=False) for q in questions],
                    'time_remaining': (quiz.time_limit * 60) - int(time_elapsed)
                }), 200
        
        # Create new attempt
        attempt = QuizAttempt(
            user_id=user.id,
            quiz_id=quiz_id,
            started_at=datetime.utcnow()
        )
        
        db.session.add(attempt)
        db.session.commit()
        
        # Get quiz questions (without answers)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        return jsonify({
            'message': 'Quiz started successfully',
            'attempt': attempt.to_dict(),
            'quiz': quiz.to_dict(),
            'questions': [q.to_dict(include_answer=False) for q in questions],
            'time_remaining': quiz.time_limit * 60
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/<int:quiz_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(quiz_id):
    try:
        user = get_current_user()
        if not user or not user.is_active:
            return jsonify({'error': 'User not found'}), 404
        
        # Get ongoing attempt
        attempt = QuizAttempt.query.filter_by(
            user_id=user.id, quiz_id=quiz_id, is_completed=False
        ).first()
        
        if not attempt:
            return jsonify({'error': 'No ongoing quiz attempt found'}), 404
        
        data = request.get_json()
        answers = data.get('answers', {})
        
        # Check time limit
        time_elapsed = (datetime.utcnow() - attempt.started_at).total_seconds()
        quiz = Quiz.query.get(quiz_id)
        
        if time_elapsed > (quiz.time_limit * 60):
            return jsonify({'error': 'Time limit exceeded'}), 400
        
        # Save answers and complete attempt
        attempt.set_answers(answers)
        attempt.is_completed = True
        attempt.completed_at = datetime.utcnow()
        attempt.time_taken = int(time_elapsed)
        
        # Calculate score
        score = attempt.calculate_score()
        
        db.session.commit()
        
        # Track performance in question bank
        performance_tracking = QuizPerformanceIntegrationService.track_quiz_attempt_performance(
            attempt=attempt,
            question_time_data=data.get('question_times', {})
        )
        
        # Get detailed results
        results = get_quiz_results(attempt)
        
        return jsonify({
            'message': 'Quiz submitted successfully',
            'attempt': attempt.to_dict(),
            'results': results,
            'performance_tracking': performance_tracking
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/<int:quiz_id>/save', methods=['POST'])
@jwt_required()
def save_quiz_progress(quiz_id):
    try:
        user = get_current_user()
        if not user or not user.is_active:
            return jsonify({'error': 'User not found'}), 404
        
        # Get ongoing attempt
        attempt = QuizAttempt.query.filter_by(
            user_id=user.id, quiz_id=quiz_id, is_completed=False
        ).first()
        
        if not attempt:
            return jsonify({'error': 'No ongoing quiz attempt found'}), 404
        
        data = request.get_json()
        answers = data.get('answers', {})
        
        # Check time limit
        time_elapsed = (datetime.utcnow() - attempt.started_at).total_seconds()
        quiz = Quiz.query.get(quiz_id)
        
        if time_elapsed > (quiz.time_limit * 60):
            # Auto-submit
            attempt.set_answers(answers)
            attempt.is_completed = True
            attempt.completed_at = datetime.utcnow()
            attempt.time_taken = int(time_elapsed)
            attempt.calculate_score()
            db.session.commit()
            
            # Track performance in question bank for auto-submitted quiz
            performance_tracking = QuizPerformanceIntegrationService.track_quiz_attempt_performance(
                attempt=attempt,
                question_time_data=data.get('question_times', {})
            )
            
            return jsonify({
                'message': 'Quiz auto-submitted due to time limit',
                'attempt': attempt.to_dict(),
                'performance_tracking': performance_tracking
            }), 200
        
        # Save progress
        attempt.set_answers(answers)
        db.session.commit()
        
        return jsonify({
            'message': 'Progress saved successfully',
            'time_remaining': (quiz.time_limit * 60) - int(time_elapsed)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/attempt/<int:attempt_id>/results', methods=['GET'])
@jwt_required()
def get_attempt_results(attempt_id):
    try:
        user = get_current_user()
        if not user or not user.is_active:
            return jsonify({'error': 'User not found'}), 404
        
        attempt = QuizAttempt.query.filter_by(
            id=attempt_id, user_id=user.id, is_completed=True
        ).first()
        
        if not attempt:
            return jsonify({'error': 'Quiz attempt not found'}), 404
        
        results = get_quiz_results(attempt)
        
        return jsonify({
            'attempt': attempt.to_dict(),
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_quiz_results(attempt):
    """Get detailed results for a completed quiz attempt"""
    questions = Question.query.filter_by(quiz_id=attempt.quiz_id).all()
    user_answers = attempt.get_answers()
    
    results = []
    correct_count = 0
    
    for question in questions:
        question_id = str(question.id)
        user_answer = user_answers.get(question_id, '').upper()
        is_correct = user_answer == question.correct_option
        
        if is_correct:
            correct_count += 1
        
        result = {
            'question': question.to_dict(include_answer=True),
            'user_answer': user_answer,
            'is_correct': is_correct,
            'marks_obtained': question.marks if is_correct else 0
        }
        results.append(result)
    
    summary = {
        'total_questions': len(questions),
        'correct_answers': correct_count,
        'wrong_answers': len(questions) - correct_count,
        'total_marks': attempt.total_marks,
        'marks_obtained': attempt.score,
        'percentage': round((attempt.score / attempt.total_marks) * 100, 2) if attempt.total_marks > 0 else 0,
        'time_taken': attempt.time_taken,
        'time_taken_formatted': format_time(attempt.time_taken)
    }
    
    return {
        'summary': summary,
        'questions': results
    }

def format_time(seconds):
    """Format time in seconds to MM:SS format"""
    if not seconds:
        return "00:00"
    
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

@quiz_bp.route('/<int:quiz_id>/preview', methods=['GET'])
@jwt_required()
def preview_quiz(quiz_id):
    try:
        user = get_current_user()
        if not user or not user.is_active:
            return jsonify({'error': 'User not found'}), 404
        
        quiz = Quiz.query.get_or_404(quiz_id)
        if not quiz.is_active:
            return jsonify({'error': 'Quiz not available'}), 404
        
        # Get quiz info without questions
        quiz_info = quiz.to_dict()
        quiz_info['total_questions'] = len(quiz.questions)
        
        # User's previous attempts
        attempts_count = QuizAttempt.query.filter_by(
            user_id=user.id, quiz_id=quiz_id, is_completed=True
        ).count()
        
        best_attempt = QuizAttempt.query.filter_by(
            user_id=user.id, quiz_id=quiz_id, is_completed=True
        ).order_by(QuizAttempt.score.desc()).first()  # type: ignore
        
        quiz_info['user_attempts'] = attempts_count
        quiz_info['best_score'] = best_attempt.score if best_attempt else 0
        quiz_info['best_percentage'] = (
            round((best_attempt.score / best_attempt.total_marks) * 100, 2) 
            if best_attempt and best_attempt.total_marks > 0 else 0
        )
        
        return jsonify(quiz_info), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@quiz_bp.route('/user-analytics', methods=['GET'])
@jwt_required()
def get_user_analytics():
    """Get user performance analytics including question bank data"""
    try:
        user = get_current_user()
        if not user or not user.is_active:
            return jsonify({'error': 'User not found'}), 404

        # Get query parameters
        days = request.args.get('days', 30, type=int)
        subject_id = request.args.get('subject_id', type=int)
        chapter_id = request.args.get('chapter_id', type=int)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Build base query for quiz attempts
        attempts_query = QuizAttempt.query.filter(
            QuizAttempt.user_id == user.id,
            QuizAttempt.is_completed == True,
            QuizAttempt.completed_at >= start_date,
            QuizAttempt.completed_at <= end_date
        )
        
        # Add filters if provided
        if subject_id or chapter_id:
            attempts_query = attempts_query.join(Quiz).join(Chapter)
            if subject_id:
                attempts_query = attempts_query.filter(Chapter.subject_id == subject_id)
            if chapter_id:
                attempts_query = attempts_query.filter(Quiz.chapter_id == chapter_id)
        
        attempts = attempts_query.order_by(QuizAttempt.completed_at.desc()).all()
        
        # Calculate basic stats
        total_attempts = len(attempts)
        total_score = sum(attempt.score for attempt in attempts)
        total_possible = sum(attempt.total_marks for attempt in attempts)
        average_score = (total_score / total_possible * 100) if total_possible > 0 else 0
        
        # Calculate trends (compare to previous period)
        prev_start = start_date - timedelta(days=days)
        prev_attempts_query = QuizAttempt.query.filter(
            QuizAttempt.user_id == user.id,
            QuizAttempt.is_completed == True,
            QuizAttempt.completed_at >= prev_start,
            QuizAttempt.completed_at < start_date
        )
        
        if subject_id or chapter_id:
            prev_attempts_query = prev_attempts_query.join(Quiz).join(Chapter)
            if subject_id:
                prev_attempts_query = prev_attempts_query.filter(Chapter.subject_id == subject_id)
            if chapter_id:
                prev_attempts_query = prev_attempts_query.filter(Quiz.chapter_id == chapter_id)
        
        prev_attempts = prev_attempts_query.all()
        prev_total_score = sum(attempt.score for attempt in prev_attempts)
        prev_total_possible = sum(attempt.total_marks for attempt in prev_attempts)
        prev_average_score = (prev_total_score / prev_total_possible * 100) if prev_total_possible > 0 else 0
        
        score_trend = average_score - prev_average_score
        
        # Get recent performance by day
        daily_performance = {}
        for attempt in attempts:
            day_key = attempt.completed_at.strftime('%Y-%m-%d')
            if day_key not in daily_performance:
                daily_performance[day_key] = {'attempts': 0, 'score': 0, 'possible': 0}
            daily_performance[day_key]['attempts'] += 1
            daily_performance[day_key]['score'] += attempt.score
            daily_performance[day_key]['possible'] += attempt.total_marks
        
        # Convert to list and calculate percentages
        performance_data = []
        for day, data in sorted(daily_performance.items()):
            percentage = (data['score'] / data['possible'] * 100) if data['possible'] > 0 else 0
            performance_data.append({
                'date': day,
                'attempts': data['attempts'],
                'percentage': round(percentage, 2)
            })
        
        # Get subject/chapter breakdown
        subject_performance = {}
        for attempt in attempts:
            if attempt.quiz and attempt.quiz.chapter and attempt.quiz.chapter.subject:
                subject_name = attempt.quiz.chapter.subject.name
                chapter_name = attempt.quiz.chapter.name
                
                if subject_name not in subject_performance:
                    subject_performance[subject_name] = {
                        'attempts': 0, 
                        'score': 0, 
                        'possible': 0,
                        'chapters': {}
                    }
                
                subject_performance[subject_name]['attempts'] += 1
                subject_performance[subject_name]['score'] += attempt.score
                subject_performance[subject_name]['possible'] += attempt.total_marks
                
                if chapter_name not in subject_performance[subject_name]['chapters']:
                    subject_performance[subject_name]['chapters'][chapter_name] = {
                        'attempts': 0, 'score': 0, 'possible': 0
                    }
                
                subject_performance[subject_name]['chapters'][chapter_name]['attempts'] += 1
                subject_performance[subject_name]['chapters'][chapter_name]['score'] += attempt.score
                subject_performance[subject_name]['chapters'][chapter_name]['possible'] += attempt.total_marks
        
        # Convert to list with percentages
        subjects_data = []
        for subject_name, data in subject_performance.items():
            percentage = (data['score'] / data['possible'] * 100) if data['possible'] > 0 else 0
            
            chapters_data = []
            for chapter_name, chapter_data in data['chapters'].items():
                chapter_percentage = (chapter_data['score'] / chapter_data['possible'] * 100) if chapter_data['possible'] > 0 else 0
                chapters_data.append({
                    'name': chapter_name,
                    'attempts': chapter_data['attempts'],
                    'percentage': round(chapter_percentage, 2)
                })
            
            subjects_data.append({
                'name': subject_name,
                'attempts': data['attempts'],
                'percentage': round(percentage, 2),
                'chapters': chapters_data
            })
        
        # Get question bank analytics for this user using QuestionBankService
        question_bank_service = QuestionBankService()
        question_analytics = question_bank_service.get_user_question_analytics(user.id, days=days)
        
        return jsonify({
            'summary': {
                'total_attempts': total_attempts,
                'average_score': round(average_score, 2),
                'score_trend': round(score_trend, 2),
                'period_days': days
            },
            'daily_performance': performance_data,
            'subject_performance': subjects_data,
            'question_analytics': question_analytics,
            'filters': {
                'subject_id': subject_id,
                'chapter_id': chapter_id,
                'days': days
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
