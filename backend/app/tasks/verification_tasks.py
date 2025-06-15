from flask import Flask
from app import create_app, db
from app.models.models import Quiz, Question
from app.services.ai_service import AIService
from datetime import datetime
import json
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_and_store_quiz_task(quiz_id, verification_config=None):
    """
    Background task to verify AI-generated quiz questions and store only verified ones
    
    Args:
        quiz_id: ID of the quiz to verify
        verification_config: Dict with verification settings
    
    Returns:
        Dict with verification results
    """
    
    # Default configuration
    config = {
        'min_confidence': 0.7,
        'max_retry_attempts': 3,
        'fallback_strategy': 'skip',  # 'skip', 'manual_review', 'use_anyway'
        'notify_admin': True
    }
    
    if verification_config:
        config.update(verification_config)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Get quiz and questions
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                raise Exception(f"Quiz {quiz_id} not found")
            
            questions = Question.query.filter_by(quiz_id=quiz_id).all()
            total_questions = len(questions)
            
            if not questions:
                return {'status': 'error', 'message': 'No questions found for verification'}
            
            # Initialize AI service
            ai_service = AIService()
            verification_results = []
            verified_count = 0
            failed_count = 0
            
            for i, question in enumerate(questions):
                try:
                    # Verify the question
                    verification_result = ai_service.verify_question_comprehensive(
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
                    
                    # Process verification result
                    confidence = verification_result.get('confidence', 0.0)
                    is_valid = verification_result.get('is_valid', False) and confidence >= config['min_confidence']
                    
                    # Update question with verification results
                    question.verification_confidence = confidence
                    question.verification_attempts = getattr(question, 'verification_attempts', 0) + 1
                    question.verified_at = datetime.utcnow()
                    question.set_verification_metadata(verification_result)
                    
                    if is_valid:
                        question.verification_status = 'verified'
                        question.is_verified = True
                        verified_count += 1
                        logger.info(f"Question {question.id} verified successfully (confidence: {confidence:.2f})")
                    else:
                        question.verification_status = 'failed'
                        question.is_verified = False
                        failed_count += 1
                        logger.warning(f"Question {question.id} failed verification (confidence: {confidence:.2f})")
                    
                    verification_results.append({
                        'question_id': question.id,
                        'status': question.verification_status,
                        'confidence': confidence,
                        'is_valid': is_valid
                    })
                    
                except Exception as e:
                    logger.error(f"Error verifying question {question.id}: {str(e)}")
                    question.verification_status = 'error'
                    question.is_verified = False
                    question.set_verification_metadata({'error': str(e)})
                    failed_count += 1
                    
                    verification_results.append({
                        'question_id': question.id,
                        'status': 'error',
                        'error': str(e)
                    })
            
            # Save all changes
            db.session.commit()
            
            # Calculate success rate
            success_rate = (verified_count / total_questions) * 100 if total_questions > 0 else 0
            
            logger.info(f"Verification completed for quiz {quiz_id}: {verified_count}/{total_questions} verified ({success_rate:.1f}%)")
            
            return {
                'status': 'success',
                'quiz_id': quiz_id,
                'total_questions': total_questions,
                'verified_count': verified_count,
                'failed_count': failed_count,
                'success_rate': success_rate,
                'verification_results': verification_results
            }
            
        except Exception as e:
            logger.error(f"Fatal error in verify_and_store_quiz_task: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

def verify_single_question_task(question_id, verification_config=None):
    """
    Verify a single question
    
    Args:
        question_id: ID of the question to verify
        verification_config: Dict with verification settings
        
    Returns:
        Dict with verification result
    """
    
    # Default configuration
    config = {
        'min_confidence': 0.7,
        'max_retry_attempts': 3
    }
    
    if verification_config:
        config.update(verification_config)
    
    app = create_app()
    
    with app.app_context():
        try:
            question = Question.query.get(question_id)
            if not question:
                return {'status': 'error', 'message': 'Question not found'}
            
            # Initialize AI service
            ai_service = AIService()
            
            # Verify the question
            verification_result = ai_service.verify_question_comprehensive(
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
            
            # Process result
            confidence = verification_result.get('confidence', 0.0)
            is_valid = verification_result.get('is_valid', False) and confidence >= config['min_confidence']
            
            # Update question
            question.verification_confidence = confidence
            question.verification_attempts = getattr(question, 'verification_attempts', 0) + 1
            question.verified_at = datetime.utcnow()
            question.set_verification_metadata(verification_result)
            
            if is_valid:
                question.verification_status = 'verified'
                question.is_verified = True
            else:
                question.verification_status = 'failed'
                question.is_verified = False
            
            db.session.commit()
            
            return {
                'status': 'success',
                'question_id': question_id,
                'verification_status': question.verification_status,
                'confidence': confidence,
                'is_valid': is_valid
            }
            
        except Exception as e:
            logger.error(f"Error in verify_single_question_task: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
