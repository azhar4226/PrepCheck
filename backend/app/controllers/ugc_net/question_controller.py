"""UGC NET Question Bank Management Controller"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import User, Subject, Chapter, QuestionBank
import json

ugc_net_question_bp = Blueprint('ugc_net_question', __name__)


def get_current_user():
    """Get current user from JWT token"""
    try:
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except:
        return None


@ugc_net_question_bp.route('/question-bank/add', methods=['POST'])
@jwt_required()
def add_question():
    """Add a new question to the UGC NET question bank"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['question_text', 'options', 'correct_answer', 'chapter_id', 'difficulty_level']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate chapter exists
        chapter = Chapter.query.get(data['chapter_id'])
        if not chapter:
            return jsonify({'error': 'Chapter not found'}), 404
        
        # Validate options format
        if not isinstance(data['options'], list) or len(data['options']) != 4:
            return jsonify({'error': 'Options must be a list of 4 items'}), 400
        
        # Validate correct answer
        if data['correct_answer'] not in ['A', 'B', 'C', 'D']:
            return jsonify({'error': 'Correct answer must be A, B, C, or D'}), 400
        
        # Validate difficulty level
        if data['difficulty_level'] not in ['easy', 'medium', 'hard']:
            return jsonify({'error': 'Difficulty level must be easy, medium, or hard'}), 400
        
        # Generate content hash for deduplication
        import hashlib
        content = f"{data['question_text']}{data['options']}{data['correct_answer']}"
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Create new question
        question = QuestionBank(
            question_text=data['question_text'],
            option_a=data['options'][0],
            option_b=data['options'][1],
            option_c=data['options'][2],
            option_d=data['options'][3],
            correct_option=data['correct_answer'],
            explanation=data.get('explanation', ''),
            difficulty=data['difficulty_level'],  # Changed from difficulty_level to difficulty
            topic=data.get('topic', 'General'),  # Add default topic
            chapter_id=data['chapter_id'],
            created_by=current_user.id,
            created_at=datetime.utcnow(),
            source='manual',
            is_verified=True,
            verification_method='manual',
            verified_by=current_user.id,
            verified_at=datetime.utcnow(),
            content_hash=content_hash
        )
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({
            'message': 'Question added successfully',
            'question_id': question.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add question: {str(e)}'}), 500


@ugc_net_question_bp.route('/question-bank/bulk-import', methods=['POST'])
@jwt_required()
def bulk_import_questions():
    """Bulk import questions from JSON file"""
    try:
        current_user = get_current_user()
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        if not data or 'questions' not in data:
            return jsonify({'error': 'Questions data not provided'}), 400
        
        questions_data = data['questions']
        if not isinstance(questions_data, list):
            return jsonify({'error': 'Questions must be a list'}), 400
        
        imported_count = 0
        errors = []
        
        for i, question_data in enumerate(questions_data):
            try:
                # Validate required fields
                required_fields = ['question_text', 'options', 'correct_answer', 'chapter_id', 'difficulty_level']
                for field in required_fields:
                    if field not in question_data:
                        errors.append(f'Question {i+1}: Missing required field: {field}')
                        continue
                
                # Validate chapter exists
                chapter = Chapter.query.get(question_data['chapter_id'])
                if not chapter:
                    errors.append(f'Question {i+1}: Chapter not found')
                    continue
                
                # Validate options format
                if not isinstance(question_data['options'], list) or len(question_data['options']) != 4:
                    errors.append(f'Question {i+1}: Options must be a list of 4 items')
                    continue
                
                # Validate correct answer
                if question_data['correct_answer'] not in ['A', 'B', 'C', 'D']:
                    errors.append(f'Question {i+1}: Correct answer must be A, B, C, or D')
                    continue
                
                # Validate difficulty level
                if question_data['difficulty_level'] not in ['easy', 'medium', 'hard']:
                    errors.append(f'Question {i+1}: Difficulty level must be easy, medium, or hard')
                    continue
                
                # Generate content hash
                import hashlib
                content = f"{question_data['question_text']}{question_data['options']}{question_data['correct_answer']}"
                content_hash = hashlib.sha256(content.encode()).hexdigest()
                
                # Create question
                question = QuestionBank(
                    question_text=question_data['question_text'],
                    option_a=question_data['options'][0],
                    option_b=question_data['options'][1],
                    option_c=question_data['options'][2],
                    option_d=question_data['options'][3],
                    correct_option=question_data['correct_answer'],
                    explanation=question_data.get('explanation', ''),
                    difficulty=question_data['difficulty_level'],
                    topic=question_data.get('topic', 'General'),
                    chapter_id=question_data['chapter_id'],
                    created_by=current_user.id,
                    created_at=datetime.utcnow(),
                    source='manual',
                    is_verified=True,
                    verification_method='manual',
                    verified_by=current_user.id,
                    verified_at=datetime.utcnow(),
                    content_hash=content_hash
                )
                
                db.session.add(question)
                imported_count += 1
                
            except Exception as e:
                errors.append(f'Question {i+1}: {str(e)}')
        
        if imported_count > 0:
            db.session.commit()
        
        return jsonify({
            'message': f'Bulk import completed. {imported_count} questions imported.',
            'imported_count': imported_count,
            'total_processed': len(questions_data),
            'errors': errors
        }), 200 if imported_count > 0 else 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to import questions: {str(e)}'}), 500
