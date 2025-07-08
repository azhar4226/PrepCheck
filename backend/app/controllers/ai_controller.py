from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Chapter, QuestionBank, UGCNetMockAttempt, UGCNetPracticeAttempt
from app.services.ai_service import AIService
from app.services.question_bank_service import QuestionBankService
from datetime import datetime
import json
import time

ai_bp = Blueprint('ai', __name__)

def admin_required():
    """Check if the current user is an admin"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    return user and user.is_admin

# ========================================
# ADMIN TASK 1: AI-POWERED QUESTION GENERATION
# ========================================

@ai_bp.route('/generate-questions', methods=['POST'])
@jwt_required()
def generate_questions():
    """
    Admin Task 1: Generate AI-powered questions with options and answers
    
    This endpoint allows admins to generate questions using AI, which are then
    stored in the QuestionBank for use in UGC NET tests.
    """
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['chapter_id', 'topic', 'difficulty', 'num_questions']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields: chapter_id, topic, difficulty, num_questions'}), 400
        
        # Verify chapter exists
        chapter = Chapter.query.get(data['chapter_id'])
        if not chapter:
            return jsonify({'error': 'Chapter not found'}), 404
        
        # Validate difficulty level
        if data['difficulty'] not in ['easy', 'medium', 'hard']:
            return jsonify({'error': 'Difficulty must be one of: easy, medium, hard'}), 400
        
        # Validate number of questions
        if not isinstance(data['num_questions'], int) or data['num_questions'] < 1 or data['num_questions'] > 20:
            return jsonify({'error': 'Number of questions must be between 1 and 20'}), 400
        
        print(f"🚀 Admin generating {data['num_questions']} questions for: {data['topic']} ({data['difficulty']})")
        start_time = time.time()
        
        # Initialize AI service
        ai_service = AIService()
        
        try:
            # Generate questions using AI
            questions_data = ai_service.generate_test_questions(
                topic=data['topic'],
                difficulty=data['difficulty'],
                num_questions=data['num_questions'],
                additional_context=data.get('context', '')
            )
            
            generation_time = time.time() - start_time
            print(f"⚡ Question generation completed in {generation_time:.2f}s")
            
        except Exception as e:
            print(f"❌ AI generation failed: {str(e)}")
            return jsonify({'error': f'AI generation failed: {str(e)}'}), 500
        
        # Store questions in QuestionBank
        print("💾 Storing questions in QuestionBank...")
        db_start = time.time()
        
        questions_added = []
        failed_questions = []
        
        # Prepare metadata tags
        tags = [data['topic'], 'ai_generated', f"difficulty_{data['difficulty']}"]
        if data.get('context'):
            tags.append('contextual')
        
        for i, q_data in enumerate(questions_data['questions']):
            try:
                # Store each question in QuestionBank
                question_bank_entry, is_new = QuestionBankService.store_ai_question(
                    question_data=q_data,
                    topic=data['topic'],
                    difficulty=data['difficulty'],
                    chapter_id=data['chapter_id'],
                    tags=tags
                )
                
                questions_added.append(question_bank_entry)
                
            except Exception as e:
                print(f"⚠️ Failed to store question {i+1}: {str(e)}")
                failed_questions.append({
                    'index': i + 1,
                    'question': q_data.get('question', 'Unknown'),
                    'error': str(e)
                })
        
        if not questions_added:
            return jsonify({'error': 'No questions were successfully generated and stored'}), 400
        
        db_time = time.time() - db_start
        total_time = time.time() - start_time
        
        print(f"✅ Generated {len(questions_added)} questions in {total_time:.2f}s")
        
        # Format response for frontend
        generated_questions = []
        for q in questions_added:
            q_dict = q.to_dict(include_answer=True)
            generated_questions.append({
                'id': q_dict['id'],
                'question': q_dict['question_text'],
                'options': {
                    'A': q_dict['option_a'],
                    'B': q_dict['option_b'],
                    'C': q_dict['option_c'],
                    'D': q_dict['option_d']
                },
                'correct_answer': q_dict['correct_option'],
                'explanation': q_dict.get('explanation', ''),
                'marks': q_dict.get('marks', 1),
                'topic': q_dict['topic'],
                'difficulty': q_dict['difficulty'],
                'chapter_id': q_dict['chapter_id']
            })
        
        return jsonify({
            'message': f'Successfully generated {len(questions_added)} questions',
            'questions': generated_questions,
            'generation_summary': {
                'total_requested': data['num_questions'],
                'successfully_generated': len(questions_added),
                'failed_count': len(failed_questions),
                'generation_time_seconds': round(generation_time, 2),
                'storage_time_seconds': round(db_time, 2),
                'total_time_seconds': round(total_time, 2)
            },
            'metadata': {
                'topic': data['topic'],
                'difficulty': data['difficulty'],
                'chapter_id': data['chapter_id'],
                'generated_at': datetime.utcnow().isoformat(),
                'generated_by': get_jwt_identity()
            },
            'failed_questions': failed_questions if failed_questions else None
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Question generation endpoint failed: {str(e)}")
        return jsonify({'error': f'Question generation failed: {str(e)}'}), 500

# ========================================
# ADMIN TASK 2: AI-POWERED QUESTION VALIDATION
# ========================================

@ai_bp.route('/validate-questions', methods=['POST'])
@jwt_required()
def validate_questions():
    """
    Admin Task 2: Validate AI-generated questions and answers
    
    This endpoint allows admins to validate questions in the QuestionBank
    using AI to ensure accuracy and quality.
    """
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        if 'question_ids' not in data or not isinstance(data['question_ids'], list):
            return jsonify({'error': 'question_ids must be provided as a list'}), 400
        
        if len(data['question_ids']) == 0:
            return jsonify({'error': 'At least one question ID must be provided'}), 400
        
        if len(data['question_ids']) > 10:
            return jsonify({'error': 'Cannot validate more than 10 questions at once'}), 400
        
        print(f"🔍 Admin validating {len(data['question_ids'])} questions")
        
        # Get questions from QuestionBank
        questions = QuestionBank.query.filter(QuestionBank.id.in_(data['question_ids'])).all()
        
        if not questions:
            return jsonify({'error': 'No questions found with the provided IDs'}), 404
        
        # Initialize AI service
        ai_service = AIService()
        
        validation_results = []
        start_time = time.time()
        
        for question in questions:
            try:
                print(f"🔍 Validating question {question.id}: {question.question_text[:50]}...")
                
                # Use AI to validate the question
                validation = ai_service.verify_question_answer(
                    question=question.question_text,
                    options={
                        'A': question.option_a,
                        'B': question.option_b,
                        'C': question.option_c,
                        'D': question.option_d
                    },
                    correct_answer=question.correct_option,
                    explanation=question.explanation or ""
                )
                
                validation_result = {
                    'question_id': question.id,
                    'question_text': question.question_text,
                    'is_valid': validation['is_valid'],
                    'confidence': validation['confidence'],
                    'validation_notes': validation.get('explanation', ''),
                    'suggested_improvements': validation.get('corrections', [])
                }
                
                # Update question if validation passed
                if validation['is_valid'] and validation['confidence'] >= 0.7:
                    question.is_verified = True
                    question.verification_method = 'ai_validated'
                    question.verification_confidence = validation['confidence']
                    question.verified_at = datetime.utcnow()
                    question.verified_by = get_jwt_identity()
                    validation_result['status'] = 'approved'
                else:
                    validation_result['status'] = 'needs_review'
                
                validation_results.append(validation_result)
                
            except Exception as e:
                print(f"❌ Validation failed for question {question.id}: {str(e)}")
                validation_results.append({
                    'question_id': question.id,
                    'question_text': question.question_text,
                    'is_valid': False,
                    'error': str(e),
                    'status': 'validation_failed'
                })
        
        # Commit changes to database
        db.session.commit()
        
        # Calculate summary statistics
        total_questions = len(validation_results)
        valid_questions = len([r for r in validation_results if r.get('is_valid', False)])
        approved_questions = len([r for r in validation_results if r.get('status') == 'approved'])
        needs_review = len([r for r in validation_results if r.get('status') == 'needs_review'])
        
        validation_time = time.time() - start_time
        
        print(f"✅ Validation completed: {approved_questions}/{total_questions} approved in {validation_time:.2f}s")
        
        return jsonify({
            'message': f'Validation completed for {total_questions} questions',
            'validation_results': validation_results,
            'summary': {
                'total_questions': total_questions,
                'valid_questions': valid_questions,
                'approved_questions': approved_questions,
                'needs_review': needs_review,
                'validation_time_seconds': round(validation_time, 2),
                'overall_validity_percentage': round((valid_questions / total_questions) * 100, 2) if total_questions > 0 else 0
            },
            'metadata': {
                'validated_at': datetime.utcnow().isoformat(),
                'validated_by': get_jwt_identity()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Question validation endpoint failed: {str(e)}")
        return jsonify({'error': f'Question validation failed: {str(e)}'}), 500

# ========================================
# USER FEATURE: AI-POWERED RECOMMENDATIONS
# ========================================

@ai_bp.route('/generate-recommendations', methods=['POST'])
@jwt_required()
def generate_recommendations():
    """
    User Feature: Generate AI-powered study recommendations
    
    This endpoint generates personalized study recommendations for users
    based on their performance in mock tests or practice tests.
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if 'attempt_id' not in data or 'attempt_type' not in data:
            return jsonify({'error': 'attempt_id and attempt_type are required'}), 400
        
        attempt_type = data['attempt_type']
        attempt_id = data['attempt_id']
        
        # Validate attempt type
        if attempt_type not in ['mock', 'practice']:
            return jsonify({'error': 'attempt_type must be either "mock" or "practice"'}), 400
        
        print(f"🧠 Generating recommendations for user {user_id}, {attempt_type} attempt {attempt_id}")
        
        # Get the test attempt based on type
        if attempt_type == 'mock':
            attempt = UGCNetMockAttempt.query.filter_by(id=attempt_id, user_id=user_id).first()
        else:  # practice
            attempt = UGCNetPracticeAttempt.query.filter_by(id=attempt_id, user_id=user_id).first()
        
        if not attempt:
            return jsonify({'error': f'No {attempt_type} attempt found with the provided ID'}), 404
        
        if not attempt.is_completed:
            return jsonify({'error': 'Recommendations can only be generated for completed attempts'}), 400
        
        # Initialize AI service
        ai_service = AIService()
        
        # Prepare performance data for AI analysis
        performance_data = {
            'overall_score': float(attempt.percentage) if attempt.percentage else 0,
            'total_questions': attempt.total_questions,
            'correct_answers': attempt.correct_answers,
            'time_taken': attempt.time_taken,
            'attempt_type': attempt_type,
            'attempt_date': attempt.created_at.isoformat() if attempt.created_at else None
        }
        
        # Add attempt-specific data
        if attempt_type == 'mock':
            performance_data.update({
                'subject_name': attempt.mock_test.subject.name if attempt.mock_test and attempt.mock_test.subject else 'UGC NET',
                'paper_type': attempt.mock_test.paper_type if attempt.mock_test else 'paper2'
            })
            
            # Get chapter-wise performance if available
            try:
                if hasattr(attempt, 'get_chapter_wise_performance'):
                    performance_data['chapter_wise_performance'] = attempt.get_chapter_wise_performance()
                if hasattr(attempt, 'get_strengths'):
                    performance_data['strengths'] = attempt.get_strengths()
                if hasattr(attempt, 'get_weaknesses'):
                    performance_data['weaknesses'] = attempt.get_weaknesses()
            except:
                pass
        else:
            performance_data.update({
                'subject_name': attempt.subject.name if attempt.subject else 'UGC NET',
                'paper_type': attempt.paper_type if hasattr(attempt, 'paper_type') else 'paper2'
            })
        
        try:
            start_time = time.time()
            
            # Generate AI recommendations
            recommendations = ai_service.generate_study_recommendations(performance_data)
            
            generation_time = time.time() - start_time
            print(f"🎯 Recommendations generated in {generation_time:.2f}s")
            
            # Store recommendations in the attempt
            recommendations_with_metadata = {
                **recommendations,
                'generated_at': datetime.utcnow().isoformat(),
                'generated_for_user': user_id,
                'based_on_attempt': attempt_id,
                'attempt_type': attempt_type
            }
            
            if attempt_type == 'mock':
                # Store in analytics field for mock attempts
                existing_analytics = json.loads(attempt.analytics) if attempt.analytics else {}
                existing_analytics['ai_recommendations'] = recommendations_with_metadata
                attempt.analytics = json.dumps(existing_analytics)
            else:
                # Store recommendations for practice attempts
                if hasattr(attempt, 'set_recommendations'):
                    attempt.set_recommendations(recommendations.get('study_plan', []))
            
            db.session.commit()
            
            return jsonify({
                'message': 'Study recommendations generated successfully',
                'recommendations': recommendations,
                'performance_summary': {
                    'overall_score': performance_data['overall_score'],
                    'total_questions': performance_data['total_questions'],
                    'correct_answers': performance_data['correct_answers'],
                    'subject': performance_data['subject_name'],
                    'paper_type': performance_data['paper_type'],
                    'attempt_type': attempt_type
                },
                'metadata': {
                    'generated_at': datetime.utcnow().isoformat(),
                    'generation_time_seconds': round(generation_time, 2),
                    'user_id': user_id,
                    'attempt_id': attempt_id,
                    'attempt_type': attempt_type
                }
            }), 200
            
        except Exception as e:
            print(f"❌ AI recommendation generation failed: {str(e)}")
            return jsonify({'error': f'Recommendation generation failed: {str(e)}'}), 500
        
    except Exception as e:
        print(f"❌ Recommendation endpoint failed: {str(e)}")
        return jsonify({'error': f'Failed to generate recommendations: {str(e)}'}), 500

# ========================================
# UTILITY ENDPOINTS
# ========================================

@ai_bp.route('/question-bank-stats', methods=['GET'])
@jwt_required()
def get_question_bank_stats():
    """Get statistics about AI-generated questions in QuestionBank"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get AI-generated questions statistics
        total_ai_questions = QuestionBank.query.filter_by(source='ai_generated').count()
        verified_questions = QuestionBank.query.filter_by(source='ai_generated', is_verified=True).count()
        pending_questions = total_ai_questions - verified_questions
        
        # Calculate verification rate
        verification_rate = (verified_questions / total_ai_questions * 100) if total_ai_questions > 0 else 0
        
        return jsonify({
            'total_ai_generated_questions': total_ai_questions,
            'verified_questions': verified_questions,
            'pending_verification': pending_questions,
            'verification_rate_percentage': round(verification_rate, 2),
            'last_updated': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get statistics: {str(e)}'}), 500

@ai_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for AI controller"""
    try:
        ai_service = AIService()
        return jsonify({
            'status': 'healthy',
            'ai_service_mode': 'mock' if ai_service.use_mock else 'real',
            'endpoints': {
                'generate_questions': 'POST /ai/generate-questions (Admin)',
                'validate_questions': 'POST /ai/validate-questions (Admin)',
                'generate_recommendations': 'POST /ai/generate-recommendations (User)',
                'question_bank_stats': 'GET /ai/question-bank-stats (Admin)'
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
