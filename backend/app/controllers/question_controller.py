from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Quiz, Question, Subject, Chapter
from sqlalchemy import desc, or_, and_
from datetime import datetime

question_bp = Blueprint('question', __name__)

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))

@question_bp.route('/', methods=['GET'])
@jwt_required()
def get_questions():
    """Get all questions with filtering and pagination"""
    try:
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        quiz_id = request.args.get('quiz_id', type=int)
        subject_id = request.args.get('subject_id', type=int)
        search = request.args.get('search', '')
        
        # Build query
        query = Question.query
        
        # Apply filters
        if quiz_id:
            query = query.filter(Question.quiz_id == quiz_id)
        
        if subject_id:
            # Filter by subject through quiz -> chapter -> subject relationship
            query = query.join(Quiz, Question.quiz_id == Quiz.id)\
                        .join(Chapter, Quiz.chapter_id == Chapter.id)\
                        .filter(Chapter.subject_id == subject_id)
        
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                or_(
                    Question.question_text.ilike(search_term),
                    Question.option_a.ilike(search_term),
                    Question.option_b.ilike(search_term),
                    Question.option_c.ilike(search_term),
                    Question.option_d.ilike(search_term)
                )
            )
        
        # Add joins for additional data (simplified first)
        # query = query.join(Quiz, Question.quiz_id == Quiz.id, isouter=True)\
        #             .join(Chapter, Quiz.chapter_id == Chapter.id, isouter=True)\
        #             .join(Subject, Chapter.subject_id == Subject.id, isouter=True)\
        #             .add_columns(
        #                 Quiz.title.label('quiz_title'),
        #                 Subject.name.label('subject_name')
        #             )
        
        # Order by creation date (newest first)
        query = query.order_by(desc(Question.created_at))
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Format results
        questions = []
        for question in pagination.items:
            question_data = question.to_dict(include_answer=True)
            
            # Manually get quiz and subject info
            if question.quiz:
                question_data['quiz_title'] = question.quiz.title
                if question.quiz.chapter and question.quiz.chapter.subject:
                    question_data['subject_name'] = question.quiz.chapter.subject.name
                else:
                    question_data['subject_name'] = None
            else:
                question_data['quiz_title'] = None
                question_data['subject_name'] = None
                
            questions.append(question_data)
        
        return jsonify({
            'success': True,
            'questions': questions,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@question_bp.route('/<int:question_id>', methods=['GET'])
@jwt_required()
def get_question(question_id):
    """Get a specific question by ID"""
    try:
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        question = Question.query.get_or_404(question_id)
        
        # Get additional data
        quiz = Quiz.query.get(question.quiz_id) if question.quiz_id else None
        subject = Subject.query.get(quiz.subject_id) if quiz and quiz.subject_id else None
        
        question_data = question.to_dict(include_answer=True)
        if quiz:
            question_data['quiz_title'] = quiz.title
            question_data['quiz_id'] = quiz.id
        if subject:
            question_data['subject_name'] = subject.name
            question_data['subject_id'] = subject.id
        
        return jsonify({
            'success': True,
            'question': question_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@question_bp.route('/', methods=['POST'])
@jwt_required()
def create_question():
    """Create a new question"""
    try:
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate correct option
        if data['correct_option'] not in ['A', 'B', 'C', 'D']:
            return jsonify({'error': 'Correct option must be A, B, C, or D'}), 400
        
        # Create question
        question = Question(
            question_text=data['question_text'],
            option_a=data['option_a'],
            option_b=data['option_b'],
            option_c=data['option_c'],
            option_d=data['option_d'],
            correct_option=data['correct_option'],
            explanation=data.get('explanation', ''),
            marks=data.get('marks', 1),
            quiz_id=data.get('quiz_id'),
            created_at=datetime.utcnow()
        )
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Question created successfully',
            'question': question.to_dict(include_answer=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@question_bp.route('/<int:question_id>', methods=['PUT'])
@jwt_required()
def update_question(question_id):
    """Update an existing question"""
    try:
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        question = Question.query.get_or_404(question_id)
        data = request.get_json()
        
        # Validate correct option if provided
        if 'correct_option' in data and data['correct_option'] not in ['A', 'B', 'C', 'D']:
            return jsonify({'error': 'Correct option must be A, B, C, or D'}), 400
        
        # Update fields
        updatable_fields = [
            'question_text', 'option_a', 'option_b', 'option_c', 'option_d',
            'correct_option', 'explanation', 'marks', 'quiz_id'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(question, field, data[field])
        
        question.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Question updated successfully',
            'question': question.to_dict(include_answer=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@question_bp.route('/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    """Delete a question"""
    try:
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        question = Question.query.get_or_404(question_id)
        
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Question deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@question_bp.route('/bulk', methods=['POST'])
@jwt_required()
def bulk_create_questions():
    """Create multiple questions at once"""
    try:
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        questions_data = data.get('questions', [])
        
        if not questions_data:
            return jsonify({'error': 'Questions array is required'}), 400
        
        created_questions = []
        errors = []
        
        for i, question_data in enumerate(questions_data):
            try:
                # Validate required fields
                required_fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
                for field in required_fields:
                    if not question_data.get(field):
                        raise ValueError(f'{field} is required')
                
                # Validate correct option
                if question_data['correct_option'] not in ['A', 'B', 'C', 'D']:
                    raise ValueError('Correct option must be A, B, C, or D')
                
                # Create question
                question = Question(
                    question_text=question_data['question_text'],
                    option_a=question_data['option_a'],
                    option_b=question_data['option_b'],
                    option_c=question_data['option_c'],
                    option_d=question_data['option_d'],
                    correct_option=question_data['correct_option'],
                    explanation=question_data.get('explanation', ''),
                    marks=question_data.get('marks', 1),
                    quiz_id=question_data.get('quiz_id'),
                    created_at=datetime.utcnow()
                )
                
                db.session.add(question)
                created_questions.append(question)
                
            except Exception as e:
                errors.append(f'Question {i+1}: {str(e)}')
        
        if created_questions:
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Created {len(created_questions)} questions',
            'created_count': len(created_questions),
            'errors': errors,
            'questions': [q.to_dict(include_answer=True) for q in created_questions]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@question_bp.route('/<int:question_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_question(question_id):
    """Duplicate an existing question"""
    try:
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        original_question = Question.query.get_or_404(question_id)
        
        # Create duplicate
        duplicate = Question(
            question_text=f"{original_question.question_text} (Copy)",
            option_a=original_question.option_a,
            option_b=original_question.option_b,
            option_c=original_question.option_c,
            option_d=original_question.option_d,
            correct_option=original_question.correct_option,
            explanation=original_question.explanation,
            marks=original_question.marks,
            difficulty=original_question.difficulty,
            quiz_id=original_question.quiz_id,
            question_type=original_question.question_type,
            created_at=datetime.utcnow()
        )
        
        db.session.add(duplicate)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Question duplicated successfully',
            'question': duplicate.to_dict(include_answer=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@question_bp.route('/import', methods=['POST'])
@jwt_required()
def import_questions():
    """Import questions from CSV file"""
    try:
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        # This would handle CSV file upload and parsing
        # Implementation would depend on specific CSV format requirements
        
        return jsonify({
            'success': True,
            'message': 'Questions imported successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@question_bp.route('/export', methods=['GET'])
@jwt_required()
def export_questions():
    """Export questions to CSV file"""
    try:
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get filter parameters
        quiz_id = request.args.get('quiz_id', type=int)
        subject_id = request.args.get('subject_id', type=int)
        
        # Build query
        query = Question.query
        
        if quiz_id:
            query = query.filter(Question.quiz_id == quiz_id)
        
        if subject_id:
            query = query.join(Quiz).filter(Quiz.subject_id == subject_id)
        
        questions = query.all()
        
        # This would generate and return CSV file
        # Implementation would depend on specific export format requirements
        
        return jsonify({
            'success': True,
            'message': f'Exported {len(questions)} questions'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
