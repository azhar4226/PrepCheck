from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Quiz, Question, Chapter
from app.services.ai_service import AIService
import json

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
        try:
            quiz_data = ai_service.generate_quiz(
                topic=data['topic'],
                difficulty=data['difficulty'],
                num_questions=data['num_questions'],
                additional_context=data.get('context', '')
            )
        except Exception as e:
            return jsonify({'error': f'AI generation failed: {str(e)}'}), 500
        
        # Create quiz (draft mode)
        quiz = Quiz(
            title=f"AI Generated: {data['topic']}",
            description=quiz_data.get('description', ''),
            chapter_id=data['chapter_id'],
            time_limit=data.get('time_limit', 60),
            is_ai_generated=True,
            is_active=False  # Start as draft
        )
        
        db.session.add(quiz)
        db.session.flush()  # Get quiz ID
        
        # Create questions
        questions_created = []
        for q_data in quiz_data['questions']:
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
                
                db.session.add(question)
                questions_created.append(question)
                
            except Exception as e:
                # Skip invalid questions
                continue
        
        if not questions_created:
            db.session.rollback()
            return jsonify({'error': 'No valid questions were generated'}), 400
        
        db.session.commit()
        
        # Update quiz total marks
        quiz.update_total_marks()
        
        return jsonify({
            'message': 'Quiz generated successfully',
            'quiz': quiz.to_dict(),
            'questions': [q.to_dict(include_answer=True) for q in questions_created],
            'ai_metadata': {
                'generation_timestamp': quiz_data.get('timestamp'),
                'model_used': quiz_data.get('model', 'Gemini'),
                'confidence_score': quiz_data.get('confidence', 0.8)
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
        
        return jsonify({
            'quiz_id': quiz.id,
            'quiz_title': quiz.title,
            'verification_results': verification_results,
            'summary': {
                'total_questions': len(verification_results),
                'valid_questions': len(valid_questions),
                'validity_score': round(validity_score * 100, 2),
                'needs_review': validity_score < 0.8
            }
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
