"""UGC NET Practice Test Management Controller"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import desc
from app import db
from app.models import User, Subject, Chapter, QuestionBank, UGCNetPracticeAttempt
from app.services.ugc_net_paper_generator import UGCNetPaperGenerator
import json

ugc_net_practice_bp = Blueprint('ugc_net_practice', __name__)


def get_current_user():
    """Get current user from JWT token"""
    try:
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except:
        return None


@ugc_net_practice_bp.route('/practice-tests/generate', methods=['POST'])
@jwt_required()
def generate_practice_test():
    """Generate a practice test based on user configuration"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # Validate required fields
        required_fields = ['subject_id', 'selected_chapters', 'total_questions']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate subject
        subject = Subject.query.get(data['subject_id'])
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Validate chapters
        selected_chapter_ids = data['selected_chapters']
        if not selected_chapter_ids:
            return jsonify({'error': 'At least one chapter must be selected'}), 400
        
        chapters = Chapter.query.filter(
            Chapter.id.in_(selected_chapter_ids),
            Chapter.subject_id == data['subject_id']
        ).all()
        
        if len(chapters) != len(selected_chapter_ids):
            return jsonify({'error': 'One or more selected chapters are invalid'}), 400
        
        # Create practice test configuration
        config = {
            'subject_id': data['subject_id'],
            'paper_type': data.get('paper_type', 'paper2'),
            'practice_type': data.get('practice_type', 'chapter_wise'),
            'total_questions': data['total_questions'],
            'chapter_ids': selected_chapter_ids,
            'difficulty_distribution': data.get('difficulty_distribution', {
                'easy': 30,
                'medium': 50,
                'hard': 20
            }),
            'source_distribution': data.get('source_distribution', {
                'previous_year': 70,
                'ai_generated': 30
            })
        }
        
        # Generate practice test using paper generator
        generator = UGCNetPaperGenerator()
        result = generator.generate_practice_test(config)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        # Extract questions from the result
        practice_test_data = result['practice_test']
        questions = practice_test_data['questions']
        
        # Create practice attempt record
        attempt = UGCNetPracticeAttempt(
            user_id=user.id,
            subject_id=data['subject_id'],
            title=f"Practice Test - {subject.name}",
            paper_type=data.get('paper_type', 'paper2'),
            practice_type=data.get('practice_type', 'chapter_wise'),
            total_questions=len(questions),
            difficulty_easy=data.get('difficulty_distribution', {}).get('easy', 30),
            difficulty_medium=data.get('difficulty_distribution', {}).get('medium', 50),  
            difficulty_hard=data.get('difficulty_distribution', {}).get('hard', 20),
            time_limit=data.get('time_limit', 30),
            status='generated'
        )
        
        # Set JSON fields
        attempt.set_selected_chapters(selected_chapter_ids)
        attempt.set_questions_data(questions)
        
        db.session.add(attempt)
        db.session.commit()
        
        return jsonify({
            'message': 'Practice test generated successfully',
            'attempt_id': attempt.id,
            'questions': questions,
            'statistics': result['statistics'],
            'practice_stats': result.get('practice_stats', {})
        }), 201
        
    except Exception as e:
        print(f"ERROR in generate_practice_test: {str(e)}")
        print(f"ERROR traceback: {e.__class__.__name__}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Failed to generate practice test: {str(e)}'}), 500


@ugc_net_practice_bp.route('/practice-tests/attempts/<int:attempt_id>/answers', methods=['PUT'])
@jwt_required()
def auto_save_answers(attempt_id):
    """Auto-save answers for a practice test attempt (for progressive saving)"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get the practice attempt
        attempt = UGCNetPracticeAttempt.query.filter_by(
            id=attempt_id,
            user_id=user.id
        ).first()
        
        if not attempt:
            return jsonify({'error': 'Practice attempt not found'}), 404
        
        if attempt.status not in ['generated', 'in_progress']:
            # Allow viewing completed tests but not saving new answers
            if attempt.status == 'completed':
                return jsonify({'error': 'This practice test has already been completed. Please start a new practice test to continue practicing.'}), 400
            else:
                return jsonify({'error': 'Cannot save answers for this attempt'}), 400
        
        data = request.get_json()
        if not data or 'answers' not in data:
            return jsonify({'error': 'Answers data is required'}), 400
        
        answers = data['answers']
        print(f"DEBUG: Auto-saving answers for attempt {attempt_id}: {answers}")
        
        # Update the attempt status to in_progress if it was generated
        if attempt.status == 'generated':
            attempt.status = 'in_progress'
            attempt.started_at = datetime.utcnow()
        
        # Save the current answers (auto-save)
        attempt.set_answers_data(answers)
        db.session.commit()
        
        return jsonify({
            'message': 'Answers saved successfully',
            'saved_answers': len(answers),
            'status': attempt.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to save answers: {str(e)}'}), 500


@ugc_net_practice_bp.route('/practice-tests/attempts/<int:attempt_id>/submit', methods=['POST'])
@jwt_required()
def submit_practice_test(attempt_id):
    """Submit answers for a practice test attempt"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get the practice attempt
        attempt = UGCNetPracticeAttempt.query.filter_by(
            id=attempt_id,
            user_id=user.id
        ).first()
        
        if not attempt:
            return jsonify({'error': 'Practice attempt not found'}), 404
        
        if attempt.status == 'completed':
            return jsonify({'error': 'Practice test already submitted'}), 400
        
        data = request.get_json()
        if not data or 'answers' not in data:
            return jsonify({'error': 'Answers are required'}), 400
        
        answers = data['answers']
        
        # Load questions from attempt data
        questions_data = json.loads(attempt.questions_data)
        questions = []
        for q_data in questions_data:
            # Reconstruct question bank objects for evaluation
            question = QuestionBank.query.get(q_data['id'])
            if question:
                questions.append(question)
        
        # Calculate score
        score = 0
        total_marks = sum(getattr(question, 'marks', 1) for question in questions)  # Sum of all question marks
        correct_answers = 0
        wrong_answers = 0
        question_results = []
        
        for question in questions:
            question_id = str(question.id)
            user_answer = answers.get(question_id)
            is_correct = user_answer and user_answer.upper() == question.correct_option.upper()
            
            if is_correct:
                score += getattr(question, 'marks', 1)  # Default to 1 mark if not set
                correct_answers += 1
            else:
                wrong_answers += 1
            
            question_results.append({
                'question_id': question.id,
                'user_answer': user_answer,
                'correct_answer': question.correct_option,
                'is_correct': is_correct,
                'explanation': question.explanation
            })
        
        percentage = min((score / total_marks * 100), 100) if total_marks > 0 else 0
        
        # Update attempt with results
        attempt.status = 'completed'
        attempt.is_completed = True  # Also update the boolean field for consistency
        attempt.completed_at = datetime.utcnow()
        attempt.score = score
        attempt.total_marks = total_marks
        attempt.percentage = percentage
        attempt.correct_answers = correct_answers
        attempt.wrong_answers = wrong_answers
        attempt.set_answers_data(answers)
        attempt.set_detailed_results({'questions': question_results})
        
        # Calculate time taken if start time is available
        if attempt.started_at:
            time_taken = (attempt.completed_at - attempt.started_at).total_seconds()
            attempt.time_taken = int(time_taken)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Practice test submitted successfully',
            'attempt_id': attempt.id,
            'score': score,
            'total_marks': total_marks,
            'percentage': percentage,
            'correct_answers': correct_answers,
            'wrong_answers': wrong_answers,
            'question_results': question_results
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to submit practice test: {str(e)}'}), 500


@ugc_net_practice_bp.route('/practice-tests/attempts/<int:attempt_id>/results', methods=['GET'])
@jwt_required()
def get_practice_test_results(attempt_id):
    """Get detailed results for a practice test attempt"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get the practice attempt
        attempt = UGCNetPracticeAttempt.query.filter_by(
            id=attempt_id,
            user_id=user.id
        ).first()
        
        if not attempt:
            return jsonify({'error': 'Practice attempt not found'}), 404
        
        if attempt.status != 'completed':
            return jsonify({'error': 'Practice test not completed yet'}), 400
        
        # Get subject and chapter details
        subject = Subject.query.get(attempt.subject_id)
        selected_chapter_ids = json.loads(attempt.selected_chapters)
        chapters = Chapter.query.filter(Chapter.id.in_(selected_chapter_ids)).all()
        
        # Load results and questions
        detailed_results_data = attempt.get_detailed_results()
        question_results = detailed_results_data.get('questions', []) if detailed_results_data else []
        questions_data = attempt.get_questions_data()
        
        # Calculate chapter-wise performance
        chapter_performance = {}
        for chapter in chapters:
            chapter_performance[chapter.id] = {
                'name': chapter.name,
                'correct': 0,
                'total': 0,
                'percentage': 0
            }
        
        # Analyze question results
        for i, result in enumerate(question_results):
            # Find the chapter for this question
            question_data = questions_data[i] if i < len(questions_data) else None
            if question_data and 'chapter_id' in question_data:
                chapter_id = question_data['chapter_id']
                if chapter_id in chapter_performance:
                    chapter_performance[chapter_id]['total'] += 1
                    if result['is_correct']:
                        chapter_performance[chapter_id]['correct'] += 1
        
        # Calculate percentages
        for chapter_id in chapter_performance:
            perf = chapter_performance[chapter_id]
            if perf['total'] > 0:
                perf['percentage'] = round((perf['correct'] / perf['total']) * 100, 2)
        
        # Generate recommendations
        weak_chapters = [
            perf for perf in chapter_performance.values() 
            if perf['total'] > 0 and perf['percentage'] < 60
        ]
        strong_chapters = [
            perf for perf in chapter_performance.values() 
            if perf['total'] > 0 and perf['percentage'] >= 80
        ]
        
        return jsonify({
            'attempt': attempt.to_dict(),
            'subject': subject.to_dict() if subject else None,
            'chapters': [c.to_dict() for c in chapters],
            'question_results': question_results,
            'chapter_performance': list(chapter_performance.values()),
            'recommendations': {
                'weak_chapters': weak_chapters,
                'strong_chapters': strong_chapters,
                'overall_performance': 'excellent' if attempt.percentage >= 80 
                                    else 'good' if attempt.percentage >= 60 
                                    else 'needs_improvement'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get practice test results: {str(e)}'}), 500


@ugc_net_practice_bp.route('/practice-tests', methods=['GET'])
@jwt_required()
def get_practice_tests():
    """Get practice test history for the current user"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get practice attempts for user
        attempts = UGCNetPracticeAttempt.query.filter_by(
            user_id=user.id
        ).order_by(desc(UGCNetPracticeAttempt.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        attempts_data = []
        for attempt in attempts.items:
            attempt_dict = attempt.to_dict()
            
            # Add subject information
            if attempt.subject_id:
                subject = Subject.query.get(attempt.subject_id)
                attempt_dict['subject_name'] = subject.name if subject else 'Unknown'
                attempt_dict['subject_code'] = subject.subject_code if subject else None
            
            attempts_data.append(attempt_dict)
        
        return jsonify({
            'practice_attempts': attempts_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': attempts.total,
                'pages': attempts.pages,
                'has_next': attempts.has_next,
                'has_prev': attempts.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get practice tests: {str(e)}'}), 500


@ugc_net_practice_bp.route('/practice-tests/attempts/<int:attempt_id>', methods=['GET'])
@jwt_required()
def get_practice_test(attempt_id):
    """Get practice test details for taking the test"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get practice attempt
        attempt = UGCNetPracticeAttempt.query.filter_by(
            id=attempt_id,
            user_id=user.id
        ).first()
        
        if not attempt:
            return jsonify({'error': 'Practice test not found'}), 404
        
        # Get the attempt data
        attempt_dict = attempt.to_dict(include_questions=True)
        
        # Debug: Print what we're getting from to_dict
        print(f"DEBUG: attempt.to_dict(include_questions=True) returned:")
        print(f"  - questions key exists: {'questions' in attempt_dict}")
        print(f"  - questions length: {len(attempt_dict.get('questions', []))}")
        if attempt_dict.get('questions'):
            print(f"  - first question keys: {list(attempt_dict['questions'][0].keys()) if attempt_dict['questions'] else 'None'}")
        
        # Ensure questions are properly formatted
        questions = attempt_dict.get('questions', [])
        if not questions:
            print("DEBUG: No questions from to_dict, trying to get from raw data")
            # Try to get questions from raw data if to_dict failed
            questions_data = attempt.get_questions_data()
            print(f"DEBUG: Raw questions_data length: {len(questions_data) if questions_data else 0}")
            
            if questions_data:
                formatted_questions = []
                for i, q_data in enumerate(questions_data):
                    print(f"DEBUG: Processing question {i}: {type(q_data)}")
                    if isinstance(q_data, dict):
                        # Ensure the question has all required fields for frontend
                        formatted_question = {
                            'id': q_data.get('id'),
                            'question_text': q_data.get('question_text', ''),
                            'option_a': q_data.get('option_a', ''),
                            'option_b': q_data.get('option_b', ''),
                            'option_c': q_data.get('option_c', ''),
                            'option_d': q_data.get('option_d', ''),
                            'options': [
                                q_data.get('option_a', ''),
                                q_data.get('option_b', ''),
                                q_data.get('option_c', ''),
                                q_data.get('option_d', '')
                            ],
                            'marks': q_data.get('marks', 1),
                            'chapter_name': q_data.get('chapter_name', ''),
                            'difficulty': q_data.get('difficulty', 'medium')
                        }
                        formatted_questions.append(formatted_question)
                        if i == 0:  # Debug first question
                            print(f"DEBUG: Formatted first question: {formatted_question}")
                
                attempt_dict['questions'] = formatted_questions
                print(f"DEBUG: Set {len(formatted_questions)} formatted questions")
        else:
            print(f"DEBUG: Using questions from to_dict: {len(questions)}")
        
        # Return practice test data including questions
        response_data = {
            'attempt': attempt_dict,
            'subject': attempt.subject.to_dict() if attempt.subject else None
        }
        
        # Add debug info if no questions found
        if not questions and not attempt_dict.get('questions'):
            response_data['debug'] = {
                'questions_data_exists': bool(attempt.questions_data),
                'questions_data_length': len(attempt.questions_data) if attempt.questions_data else 0,
                'status': attempt.status,
                'message': 'No questions found - check if practice test was properly generated'
            }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"ERROR in get_practice_test: {str(e)}")
        return jsonify({'error': f'Failed to get practice test: {str(e)}'}), 500


@ugc_net_practice_bp.route('/practice-tests/attempts/<int:attempt_id>/debug', methods=['GET'])
@jwt_required()
def debug_practice_test_attempt(attempt_id):
    """Debug endpoint to inspect practice test attempt data"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        attempt = UGCNetPracticeAttempt.query.filter_by(
            id=attempt_id,
            user_id=user.id
        ).first()
        
        if not attempt:
            return jsonify({'error': 'Practice test attempt not found'}), 404
        
        # Get raw data for debugging
        debug_info = {
            'attempt_id': attempt.id,
            'status': attempt.status,
            'questions_data_exists': bool(attempt.questions_data),
            'questions_data_length': len(attempt.questions_data) if attempt.questions_data else 0,
            'answers_data_exists': bool(attempt.answers_data),
            'created_at': attempt.created_at.isoformat() + 'Z' if attempt.created_at else None,
            'is_completed': attempt.is_completed,
            'total_questions': attempt.total_questions,
            'score': attempt.score,
            'percentage': attempt.percentage
        }
        
        return jsonify({
            'debug_info': debug_info,
            'attempt': attempt.to_dict(include_questions=True, include_answers=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Debug failed: {str(e)}'}), 500


@ugc_net_practice_bp.route('/practice-tests/attempts/<int:attempt_id>', methods=['DELETE'])
@jwt_required()
def delete_practice_test_attempt(attempt_id):
    """Delete a specific practice test attempt"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Find the attempt
        attempt = UGCNetPracticeAttempt.query.filter_by(
            id=attempt_id,
            user_id=user.id
        ).first()
        
        if not attempt:
            return jsonify({'error': 'Practice test attempt not found'}), 404
        
        # Delete the attempt
        db.session.delete(attempt)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Practice test attempt deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
