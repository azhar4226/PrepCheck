"""
Question Bank Controller for managing question bank operations
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, QuestionBank
from app.services.question_bank_service import QuestionBankService
from datetime import datetime

question_bank_bp = Blueprint('question_bank', __name__)

def admin_required():
    """Check if current user is admin"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    return user and user.is_admin

@question_bank_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_question_bank_stats():
    """Get question bank statistics"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        stats = QuestionBankService.get_question_bank_stats()
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@question_bank_bp.route('/search', methods=['GET'])
@jwt_required()
def search_question_bank():
    """Search questions in the question bank"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get query parameters
        topic = request.args.get('topic')
        difficulty = request.args.get('difficulty')
        verified_only = request.args.get('verified_only', 'true').lower() == 'true'
        chapter_id = request.args.get('chapter_id', type=int)
        tags = request.args.getlist('tags')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Search questions
        questions = QuestionBankService.search_questions(
            topic=topic,
            difficulty=difficulty,
            verified_only=verified_only,
            chapter_id=chapter_id,
            tags=tags if tags else None,
            limit=limit,
            offset=offset
        )
        
        # Convert to dict format
        questions_data = [q.to_dict() for q in questions]
        
        return jsonify({
            'questions': questions_data,
            'count': len(questions_data),
            'filters': {
                'topic': topic,
                'difficulty': difficulty,
                'verified_only': verified_only,
                'chapter_id': chapter_id,
                'tags': tags,
                'limit': limit,
                'offset': offset
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@question_bank_bp.route('/questions/<int:question_id>', methods=['GET'])
@jwt_required()
def get_question_bank_question(question_id):
    """Get a specific question from the question bank"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        question = QuestionBank.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        return jsonify(question.to_dict(include_answer=True)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@question_bank_bp.route('/questions/<int:question_id>/verify', methods=['POST'])
@jwt_required()
def verify_question_bank_question(question_id):
    """Manually verify a question in the question bank"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        verification_method = data.get('verification_method', 'manual')
        confidence = data.get('confidence', 1.0)
        notes = data.get('notes', '')
        
        current_user_id = get_jwt_identity()
        
        success = QuestionBankService.verify_question(
            question_bank_id=question_id,
            verification_method=verification_method,
            confidence=confidence,
            verified_by_user_id=int(current_user_id),
            notes=notes
        )
        
        if success:
            return jsonify({
                'message': 'Question verified successfully',
                'question_id': question_id
            }), 200
        else:
            return jsonify({'error': 'Question not found or verification failed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@question_bank_bp.route('/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
def update_question_bank_question(question_id):
    """Update a question in the question bank"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        question = QuestionBank.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'question_text' in data:
            question.question_text = data['question_text']
        if 'option_a' in data:
            question.option_a = data['option_a']
        if 'option_b' in data:
            question.option_b = data['option_b']
        if 'option_c' in data:
            question.option_c = data['option_c']
        if 'option_d' in data:
            question.option_d = data['option_d']
        if 'correct_option' in data:
            question.correct_option = data['correct_option']
        if 'explanation' in data:
            question.explanation = data['explanation']
        if 'topic' in data:
            question.topic = data['topic']
        if 'difficulty' in data:
            question.difficulty = data['difficulty']
        if 'tags' in data:
            question.set_tags(data['tags'])
        
        # Regenerate content hash after changes
        question.content_hash = question.generate_content_hash()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Question updated successfully',
            'question': question.to_dict(include_answer=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@question_bank_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question_bank_question(question_id):
    """Delete a question from the question bank"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        question = QuestionBank.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({
            'message': 'Question deleted successfully',
            'question_id': question_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@question_bank_bp.route('/questions', methods=['POST'])
@jwt_required()
def create_question_bank_question():
    """Manually create a question in the question bank"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'topic', 'difficulty']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check for duplicates
        existing_question = QuestionBankService.check_duplicate(
            data['question_text'],
            {
                'A': data['option_a'],
                'B': data['option_b'],
                'C': data['option_c'],
                'D': data['option_d']
            },
            data['correct_option']
        )
        
        if existing_question:
            return jsonify({
                'error': 'Question already exists in the question bank',
                'existing_question_id': existing_question.id
            }), 409
        
        # Create new question
        question = QuestionBank(
            question_text=data['question_text'],
            option_a=data['option_a'],
            option_b=data['option_b'],
            option_c=data['option_c'],
            option_d=data['option_d'],
            correct_option=data['correct_option'],
            explanation=data.get('explanation', ''),
            marks=data.get('marks', 1),
            topic=data['topic'],
            difficulty=data['difficulty'].lower(),
            source='manual',
            chapter_id=data.get('chapter_id'),
            content_hash=QuestionBankService.generate_content_hash(
                data['question_text'],
                {
                    'A': data['option_a'],
                    'B': data['option_b'],
                    'C': data['option_c'],
                    'D': data['option_d']
                },
                data['correct_option']
            )
        )
        
        # Set tags if provided
        if 'tags' in data:
            question.set_tags(data['tags'])
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({
            'message': 'Question created successfully',
            'question': question.to_dict(include_answer=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@question_bank_bp.route('/questions/for-quiz', methods=['POST'])
@jwt_required()
def get_questions_for_quiz():
    """Get questions from question bank for creating a new quiz"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['topic', 'difficulty', 'num_questions']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get questions from question bank
        questions = QuestionBankService.get_questions_for_quiz(
            topic=data['topic'],
            difficulty=data['difficulty'],
            num_questions=data['num_questions'],
            chapter_id=data.get('chapter_id'),
            exclude_recent_usage_hours=data.get('exclude_recent_usage_hours', 24)
        )
        
        # Convert to dict format and update usage
        questions_data = []
        for question in questions:
            question.increment_usage()
            questions_data.append(question.to_dict(include_answer=True))
        
        db.session.commit()
        
        return jsonify({
            'questions': questions_data,
            'count': len(questions_data),
            'requested': data['num_questions'],
            'fulfilled': len(questions_data) == data['num_questions']
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@question_bank_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_question_bank_analytics():
    """Get detailed analytics for question bank"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get query parameters for filtering
        days = request.args.get('days', 30, type=int)
        topic = request.args.get('topic')
        difficulty = request.args.get('difficulty')
        
        analytics = QuestionBankService.get_detailed_analytics(
            days=days,
            topic=topic,
            difficulty=difficulty
        )
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@question_bank_bp.route('/analytics/performance/<int:question_id>', methods=['GET'])
@jwt_required()
def get_question_performance_analytics(question_id):
    """Get performance analytics for a specific question"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        question = QuestionBank.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        analytics = QuestionBankService.get_question_performance_analytics(question_id)
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@question_bank_bp.route('/analytics/trends', methods=['GET'])
@jwt_required()
def get_question_bank_trends():
    """Get usage trends for question bank"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        days = request.args.get('days', 30, type=int)
        trends = QuestionBankService.get_usage_trends(days=days)
        
        return jsonify(trends), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@question_bank_bp.route('/analytics/recommendations', methods=['GET'])
@jwt_required()
def get_question_bank_recommendations():
    """Get AI-driven recommendations for question bank improvements"""
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        recommendations = QuestionBankService.get_improvement_recommendations()
        
        return jsonify(recommendations), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
