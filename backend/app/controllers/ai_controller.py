from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Quiz, Question, Chapter, QuestionBank
from app.services.ai_service import AIService
from app.services.question_bank_service import QuestionBankService
# from app.tasks.verification_tasks import verify_and_store_quiz_task, verify_single_question_task
from datetime import datetime
import json
import time

ai_bp = Blueprint('ai', __name__)

def admin_required():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    return user and user.is_admin

@ai_bp.route('/generate-quiz', methods=['POST'])
@jwt_required()
def generate_quiz():
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        required_fields = ['chapter_id', 'topic', 'difficulty', 'num_questions']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify chapter exists
        chapter = Chapter.query.get(data['chapter_id'])
        if not chapter:
            return jsonify({'error': 'Chapter not found'}), 404
        
        # Initialize AI service
        ai_service = AIService()
        
        # Generate quiz content
        print(f"🚀 Starting quiz generation for: {data['topic']} ({data['difficulty']}, {data['num_questions']} questions)")
        start_time = time.time()
        
        try:
            quiz_data = ai_service.generate_quiz(
                topic=data['topic'],
                difficulty=data['difficulty'],
                num_questions=data['num_questions'],
                additional_context=data.get('context', '')
            )
            generation_time = time.time() - start_time
            print(f"⚡ Quiz generation completed in {generation_time:.2f}s")
        except Exception as e:
            print(f"❌ Quiz generation failed: {str(e)}")
            return jsonify({'error': f'AI generation failed: {str(e)}'}), 500
        
        # Create quiz (draft mode) - OPTIMIZED
        print("💾 Creating quiz in database...")
        db_start = time.time()
        
        quiz = Quiz(
            title=f"AI Generated: {data['topic']}",
            description=quiz_data.get('description', ''),
            chapter_id=data['chapter_id'],
            time_limit=data.get('time_limit', 60),
            is_ai_generated=True,
            is_active=True  # Make active immediately for user access
        )
        
        db.session.add(quiz)
        db.session.flush()  # Get quiz ID without full commit
        
        # Batch create questions for better performance
        questions_to_add = []
        valid_questions = []
        
        for i, q_data in enumerate(quiz_data['questions']):
            try:
                question = Question(
                    quiz_id=quiz.id,
                    question_text=q_data['question'],
                    option_a=q_data['options']['A'],
                    option_b=q_data['options']['B'],
                    option_c=q_data['options']['C'],
                    option_d=q_data['options']['D'],
                    correct_option=q_data['correct_answer'],
                    explanation=q_data.get('explanation', ''),
                    marks=q_data.get('marks', 1)
                )
                
                questions_to_add.append(question)
                valid_questions.append(q_data)
                
            except Exception as e:
                print(f"⚠️ Skipping invalid question {i+1}: {str(e)}")
                continue
        
        if not questions_to_add:
            db.session.rollback()
            return jsonify({'error': 'No valid questions were generated'}), 400
        
        # Batch add all questions
        db.session.add_all(questions_to_add)
        
        # Commit everything at once
        try:
            db.session.commit()
            db_time = time.time() - db_start
            print(f"✅ Database operations completed in {db_time:.2f}s")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Database error: {str(e)}")
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        
        # Update quiz total marks efficiently
        quiz.total_marks = len(questions_to_add)  # Since each question is 1 mark
        db.session.commit()
        
        # Start background verification process
        verification_config = {
            'min_confidence': data.get('verification_threshold', 0.7),
            'max_retry_attempts': data.get('max_retry_attempts', 3),
            'fallback_strategy': data.get('fallback_strategy', 'skip'),
            'notify_admin': True
        }
        
        # verification_task = verify_and_store_quiz_task.delay(quiz.id, verification_config)
        
        total_time = time.time() - start_time
        print(f"🎉 Quiz generation completed in {total_time:.2f}s total")
        
        # Prepare quiz data with questions in frontend-expected format
        quiz_data_response = quiz.to_dict()
        
        # Transform questions to match frontend expectations
        frontend_questions = []
        for q in questions_to_add:
            q_dict = q.to_dict(include_answer=True)
            frontend_question = {
                'question': q_dict['question_text'],
                'options': {
                    'A': q_dict['option_a'],
                    'B': q_dict['option_b'], 
                    'C': q_dict['option_c'],
                    'D': q_dict['option_d']
                },
                'correct_answer': q_dict['correct_option'],
                'explanation': q_dict.get('explanation', ''),
                'marks': q_dict.get('marks', 1)
            }
            frontend_questions.append(frontend_question)
        
        quiz_data_response['questions'] = frontend_questions
        
        # Store questions in question bank for future reuse
        print("🏦 Storing questions in question bank...")
        question_bank_start = time.time()
        
        # Prepare tags for categorization
        tags = [data['topic'], f"quiz_{quiz.id}"]
        if data.get('context'):
            tags.append('contextual')
        
        try:
            # Store all valid questions in the question bank
            question_bank_result = QuestionBankService.bulk_store_ai_questions(
                questions_data=valid_questions,
                topic=data['topic'],
                difficulty=data['difficulty'],
                chapter_id=data['chapter_id'],
                tags=tags
            )
            
            question_bank_time = time.time() - question_bank_start
            print(f"🏦 Question bank storage completed in {question_bank_time:.2f}s")
            print(f"   - New questions: {question_bank_result['new_questions']}")
            print(f"   - Duplicates: {question_bank_result['duplicate_questions']}")
            print(f"   - Failed: {question_bank_result['failed_questions']}")
            
        except Exception as e:
            # Don't fail the entire request if question bank storage fails
            print(f"⚠️ Question bank storage failed: {str(e)}")
            question_bank_result = {
                'error': str(e),
                'new_questions': 0,
                'duplicate_questions': 0,
                'failed_questions': len(valid_questions)
            }
        
        return jsonify({
            'message': 'Quiz generated successfully',  # (verification temporarily disabled)
            'quiz': quiz_data_response,
            # 'verification_task_id': verification_task.id,
            'verification_status': 'disabled',  # temporarily disabled
            'ai_metadata': {
                'generation_timestamp': quiz_data.get('timestamp'),
                'model_used': quiz_data.get('model', 'Gemini'),
                'confidence_score': quiz_data.get('confidence', 0.8),
                'generation_time': total_time,
                'questions_count': len(questions_to_add)
            },
            'question_bank': {
                'storage_status': 'success' if 'error' not in question_bank_result else 'failed',
                'new_questions_stored': question_bank_result.get('new_questions', 0),
                'duplicate_questions_found': question_bank_result.get('duplicate_questions', 0),
                'failed_questions': question_bank_result.get('failed_questions', 0),
                'total_processed': question_bank_result.get('total_questions', len(valid_questions)),
                'error': question_bank_result.get('error')
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/verify-answers', methods=['POST'])
@jwt_required()
def verify_answers():
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        if 'quiz_id' not in data:
            return jsonify({'error': 'Quiz ID required'}), 400
        
        quiz = Quiz.query.get(data['quiz_id'])
        if not quiz or not quiz.is_ai_generated:
            return jsonify({'error': 'AI-generated quiz not found'}), 404
        
        # Initialize AI service
        ai_service = AIService()
        
        # Get all questions for verification
        questions = Question.query.filter_by(quiz_id=quiz.id).all()
        
        verification_results = []
        
        for question in questions:
            try:
                # Verify each question and answer
                verification = ai_service.verify_question_answer(
                    question=question.question_text,
                    options={
                        'A': question.option_a,
                        'B': question.option_b,
                        'C': question.option_c,
                        'D': question.option_d
                    },
                    correct_answer=question.correct_option,
                    explanation=question.explanation
                )
                
                verification_results.append({
                    'question_id': question.id,
                    'question_text': question.question_text,
                    'is_valid': verification['is_valid'],
                    'confidence': verification['confidence'],
                    'suggested_corrections': verification.get('corrections', []),
                    'ai_explanation': verification.get('explanation', '')
                })
                
            except Exception as e:
                verification_results.append({
                    'question_id': question.id,
                    'question_text': question.question_text,
                    'is_valid': False,
                    'error': str(e)
                })
        
        # Calculate overall validity score
        valid_questions = [r for r in verification_results if r.get('is_valid', False)]
        validity_score = len(valid_questions) / len(verification_results) if verification_results else 0
        
        # Update question bank with verification results
        print("🔍 Updating question bank with verification results...")
        question_bank_updates = {
            'verified_questions': 0,
            'failed_verifications': 0,
            'errors': []
        }
        
        current_user_id = get_jwt_identity()
        
        for result in verification_results:
            try:
                # Find corresponding question bank entry
                question = Question.query.get(result['question_id'])
                if question:
                    # Find in question bank by content
                    question_bank_entry = QuestionBankService.check_duplicate(
                        question.question_text,
                        {
                            'A': question.option_a,
                            'B': question.option_b,
                            'C': question.option_c,
                            'D': question.option_d
                        },
                        question.correct_option
                    )
                    
                    if question_bank_entry:
                        if result['is_valid']:
                            # Update question bank with verification
                            QuestionBankService.verify_question(
                                question_bank_id=question_bank_entry.id,
                                verification_method='gemini',
                                confidence=result['confidence'],
                                verified_by_user_id=int(current_user_id),
                                notes=result.get('ai_explanation', '')
                            )
                            question_bank_updates['verified_questions'] += 1
                        else:
                            # Mark as failed verification
                            question_bank_entry.verification_status = 'failed'
                            question_bank_entry.verification_notes = result.get('error', 'Failed AI verification')
                            db.session.commit()
                            question_bank_updates['failed_verifications'] += 1
                            
            except Exception as e:
                question_bank_updates['errors'].append({
                    'question_id': result['question_id'],
                    'error': str(e)
                })
        
        print(f"✅ Question bank updated - Verified: {question_bank_updates['verified_questions']}, Failed: {question_bank_updates['failed_verifications']}")
        
        return jsonify({
            'quiz_id': quiz.id,
            'quiz_title': quiz.title,
            'verification_results': verification_results,
            'summary': {
                'total_questions': len(verification_results),
                'valid_questions': len(valid_questions),
                'validity_score': round(validity_score * 100, 2),
                'needs_review': validity_score < 0.8
            },
            'question_bank_updates': question_bank_updates
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/publish-quiz', methods=['POST'])
@jwt_required()
def publish_ai_quiz():
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        if 'quiz_id' not in data:
            return jsonify({'error': 'Quiz ID required'}), 400
        
        quiz = Quiz.query.get(data['quiz_id'])
        if not quiz or not quiz.is_ai_generated:
            return jsonify({'error': 'AI-generated quiz not found'}), 404
        
        # Apply any final edits from admin
        if 'title' in data:
            quiz.title = data['title']
        
        if 'description' in data:
            quiz.description = data['description']
        
        if 'time_limit' in data:
            quiz.time_limit = data['time_limit']
        
        # Update questions if provided
        if 'question_updates' in data:
            for update in data['question_updates']:
                question = Question.query.get(update['question_id'])
                if question and question.quiz_id == quiz.id:
                    if 'question_text' in update:
                        question.question_text = update['question_text']
                    if 'options' in update:
                        question.option_a = update['options'].get('A', question.option_a)
                        question.option_b = update['options'].get('B', question.option_b)
                        question.option_c = update['options'].get('C', question.option_c)
                        question.option_d = update['options'].get('D', question.option_d)
                    if 'correct_option' in update:
                        question.correct_option = update['correct_option']
                    if 'explanation' in update:
                        question.explanation = update['explanation']
        
        # Activate the quiz
        quiz.is_active = True
        
        db.session.commit()
        
        # Update total marks
        quiz.update_total_marks()
        
        return jsonify({
            'message': 'AI-generated quiz published successfully',
            'quiz': quiz.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/quiz-suggestions', methods=['POST'])
@jwt_required()
def get_quiz_suggestions():
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        if 'subject' not in data:
            return jsonify({'error': 'Subject required'}), 400
        
        # Initialize AI service
        ai_service = AIService()
        
        try:
            suggestions = ai_service.suggest_quiz_topics(
                subject=data['subject'],
                difficulty_levels=data.get('difficulty_levels', ['easy', 'medium', 'hard']),
                num_suggestions=data.get('num_suggestions', 10)
            )
            
            return jsonify({
                'subject': data['subject'],
                'suggestions': suggestions
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'AI suggestion failed: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/verification-status/<task_id>', methods=['GET'])
@jwt_required()
def get_verification_status(task_id):
    """Get the status of a verification task"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        from celery.result import AsyncResult
        
        task = AsyncResult(task_id)
        
        response = {
            'task_id': task_id,
            'status': task.status,
            'ready': task.ready(),
            'successful': task.successful() if task.ready() else None
        }
        
        if task.ready():
            if task.successful():
                response['result'] = task.result
            else:
                response['error'] = str(task.info)
        else:
            # Task is still running, get progress info
            response['info'] = task.info
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/quiz-verification-summary/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz_verification_summary(quiz_id):
    """Get verification summary for a quiz"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        summary = {
            'quiz_id': quiz_id,
            'quiz_title': quiz.title,
            'total_questions': len(questions),
            'verified_count': sum(1 for q in questions if q.is_verified),
            'failed_count': sum(1 for q in questions if q.verification_status == 'failed'),
            'pending_count': sum(1 for q in questions if q.verification_status == 'pending'),
            'manual_review_count': sum(1 for q in questions if q.verification_status == 'manual_review'),
            'average_confidence': 0,
            'is_quiz_active': quiz.is_active,
            'questions': []
        }
        
        # Calculate average confidence for verified questions
        verified_questions = [q for q in questions if q.is_verified and q.verification_confidence]
        if verified_questions:
            summary['average_confidence'] = sum(q.verification_confidence for q in verified_questions) / len(verified_questions)
        
        # Add question details
        for question in questions:
            question_data = {
                'id': question.id,
                'question_text': question.question_text[:100] + '...' if len(question.question_text) > 100 else question.question_text,
                'is_verified': question.is_verified,
                'verification_status': question.verification_status,
                'verification_confidence': question.verification_confidence,
                'verification_attempts': question.verification_attempts,
                'verified_at': question.verified_at.isoformat() if question.verified_at else None
            }
            summary['questions'].append(question_data)
        
        return jsonify(summary), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/retry-verification', methods=['POST'])
@jwt_required()
def retry_verification():
    """Retry verification for failed questions or entire quiz"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        if 'quiz_id' in data:
            # Retry entire quiz
            quiz_id = data['quiz_id']
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                return jsonify({'error': 'Quiz not found'}), 404
            
            # Reset failed questions to pending
            failed_questions = Question.query.filter_by(
                quiz_id=quiz_id, 
                verification_status='failed'
            ).all()
            
            for question in failed_questions:
                question.verification_status = 'pending'
                question.verification_attempts = 0
            
            db.session.commit()
            
            # Start verification task
            verification_config = {
                'min_confidence': data.get('verification_threshold', 0.7),
                'max_retry_attempts': data.get('max_retry_attempts', 3),
                'fallback_strategy': data.get('fallback_strategy', 'skip')
            }
            
            # verification_task = verify_and_store_quiz_task.delay(quiz_id, verification_config)
            
            return jsonify({
                'message': f'Retry verification would start for {len(failed_questions)} failed questions (currently disabled)',
                # 'task_id': verification_task.id,
                'failed_questions_count': len(failed_questions)
            }), 200
            
        elif 'question_id' in data:
            # Retry single question
            question_id = data['question_id']
            question = Question.query.get(question_id)
            if not question:
                return jsonify({'error': 'Question not found'}), 404
            
            # Reset question status
            question.verification_status = 'pending'
            question.verification_attempts = 0
            db.session.commit()
            
            # Start single question verification
            verification_config = {
                'min_confidence': data.get('verification_threshold', 0.7),
                'max_retry_attempts': data.get('max_retry_attempts', 3)
            }
            
            # verification_task = verify_single_question_task.delay(question_id, verification_config)
            
            return jsonify({
                'message': 'Single question verification would start (currently disabled)',
                # 'task_id': verification_task.id,
                'question_id': question_id
            }), 200
        
        else:
            return jsonify({'error': 'Either quiz_id or question_id is required'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/manual-approve-question', methods=['POST'])
@jwt_required()
def manual_approve_question():
    """Manually approve a question that failed verification"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        if 'question_id' not in data:
            return jsonify({'error': 'Question ID required'}), 400
        
        question = Question.query.get(data['question_id'])
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        # Get admin user for metadata
        admin_user = User.query.get(get_jwt_identity())
        
        # Manually approve the question
        question.is_verified = True
        question.verification_status = 'manually_approved'
        question.verification_confidence = 0.8  # Default confidence for manual approval
        question.verified_at = datetime.utcnow()
        
        # Add manual approval metadata
        metadata = question.get_verification_metadata()
        metadata.update({
            'manual_approval': True,
            'approved_by': admin_user.email,
            'approved_at': datetime.utcnow().isoformat(),
            'approval_reason': data.get('reason', 'Manual approval by admin')
        })
        question.set_verification_metadata(metadata)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Question manually approved',
            'question': question.to_dict(include_answer=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/verification-config', methods=['GET', 'POST'])
@jwt_required()
def verification_config():
    """Get or update default verification configuration"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        if request.method == 'GET':
            # Return current configuration (could be stored in database or config file)
            default_config = {
                'min_confidence': 0.7,
                'max_retry_attempts': 3,
                'fallback_strategy': 'skip',  # 'skip', 'manual_review', 'use_anyway'
                'auto_verification': True,
                'notification_settings': {
                    'notify_on_completion': True,
                    'notify_on_failures': True
                }
            }
            return jsonify(default_config), 200
        
        elif request.method == 'POST':
            # Update configuration (in a real app, this would be stored in database)
            config = request.get_json()
            
            # Validate configuration
            valid_strategies = ['skip', 'manual_review', 'use_anyway']
            if config.get('fallback_strategy') not in valid_strategies:
                return jsonify({'error': 'Invalid fallback strategy'}), 400
            
            if not (0.1 <= config.get('min_confidence', 0.7) <= 1.0):
                return jsonify({'error': 'Confidence threshold must be between 0.1 and 1.0'}), 400
            
            # In a real implementation, save to database or config file
            return jsonify({
                'message': 'Configuration updated successfully',
                'config': config
            }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/verification-stats', methods=['GET'])
@jwt_required()
def get_verification_stats():
    """Get overall verification statistics"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get all AI-generated quizzes
        ai_quizzes = Quiz.query.filter_by(is_ai_generated=True).all()
        ai_quiz_ids = [quiz.id for quiz in ai_quizzes]
        
        if not ai_quiz_ids:
            # No AI quizzes found
            return jsonify({
                'total_ai_questions': 0,
                'verified_count': 0,
                'pending_count': 0,
                'failed_count': 0,
                'manually_approved_count': 0,
                'success_rate': 0,
                'average_confidence': 0,
                'total_ai_quizzes': 0,
                'active_ai_quizzes': 0,
                'verification_enabled': True
            }), 200
        
        # Get all questions from AI quizzes
        ai_questions = Question.query.filter(Question.quiz_id.in_(ai_quiz_ids)).all()
        
        # Calculate statistics
        total_ai_questions = len(ai_questions)
        verified_count = len([q for q in ai_questions if q.is_verified])
        pending_count = len([q for q in ai_questions if q.verification_status == 'pending'])
        failed_count = len([q for q in ai_questions if q.verification_status == 'failed'])
        manually_approved_count = len([q for q in ai_questions if q.verification_status == 'manually_approved'])
        
        # Calculate average confidence for verified questions
        verified_questions = [q for q in ai_questions if q.is_verified and q.verification_confidence]
        avg_confidence = sum(q.verification_confidence for q in verified_questions) / len(verified_questions) if verified_questions else 0
        
        # Calculate quiz statistics
        total_ai_quizzes = len(ai_quizzes)
        active_ai_quizzes = len([q for q in ai_quizzes if q.is_active])
        
        # Calculate success rate
        success_rate = (verified_count / total_ai_questions * 100) if total_ai_questions > 0 else 0
        
        return jsonify({
            'total_ai_questions': total_ai_questions,
            'verified_count': verified_count,
            'pending_count': pending_count,
            'failed_count': failed_count,
            'manually_approved_count': manually_approved_count,
            'success_rate': round(success_rate, 2),
            'average_confidence': round(avg_confidence, 3) if avg_confidence else 0,
            'total_ai_quizzes': total_ai_quizzes,
            'active_ai_quizzes': active_ai_quizzes,
            'verification_enabled': True
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
