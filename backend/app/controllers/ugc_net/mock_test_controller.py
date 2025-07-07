"""UGC NET Mock Test Management Controller"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import desc
from app import db
from app.models import User, UGCNetMockTest, UGCNetMockAttempt
from app.services.ugc_net_paper_generator import UGCNetPaperGenerator
import json

ugc_net_mock_bp = Blueprint('ugc_net_mock', __name__)


def get_current_user():
    """Get current user from JWT token"""
    try:
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except:
        return None


@ugc_net_mock_bp.route('/mock-tests/generate', methods=['POST'])
@jwt_required()
def generate_mock_test():
    """Generate a new UGC NET mock test based on weightage system"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Initialize paper generator
        generator = UGCNetPaperGenerator()
        
        # Validate configuration
        validation = generator.validate_paper_config(data)
        if not validation['valid']:
            return jsonify({'error': 'Invalid configuration', 'details': validation['errors']}), 400
        
        # Generate the paper
        result = generator.generate_paper(data)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        # Create mock test record
        mock_test = UGCNetMockTest(
            title=data.get('title', f"Mock Test - {data['paper_type'].upper()}"),
            description=data.get('description', ''),
            subject_id=data['subject_id'],
            paper_type=data['paper_type'],
            total_questions=result['paper']['total_questions'],
            time_limit=data.get('time_limit', 120),  # Default 2 hours
            created_by=user.id,
            weightage_config=json.dumps(data.get('weightage_config', {}))
        )
        
        # Set difficulty distribution if provided
        if 'difficulty_distribution' in data:
            difficulty_dist = data['difficulty_distribution']
            mock_test.easy_percentage = difficulty_dist.get('easy', 30.0)
            mock_test.medium_percentage = difficulty_dist.get('medium', 50.0)
            mock_test.hard_percentage = difficulty_dist.get('hard', 20.0)
        
        # Set source distribution if provided
        if 'source_distribution' in data:
            source_dist = data['source_distribution']
            mock_test.previous_year_percentage = source_dist.get('previous_year', 70.0)
            mock_test.ai_generated_percentage = source_dist.get('ai_generated', 30.0)
        
        db.session.add(mock_test)
        db.session.commit()
        
        # Store the generated questions as a separate field or return them without storing
        mock_test_dict = mock_test.to_dict()
        mock_test_dict['generated_questions'] = [q.to_dict() for q in result['paper']['questions']]
        
        # Also convert questions in the paper for return
        paper_result = result['paper'].copy()
        paper_result['questions'] = [q.to_dict() for q in result['paper']['questions']]
        
        return jsonify({
            'message': 'Mock test generated successfully',
            'mock_test': mock_test_dict,
            'paper': paper_result,
            'statistics': result['statistics']
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ugc_net_mock_bp.route('/mock-tests', methods=['GET'])
@jwt_required()
def get_mock_tests():
    """Get all available mock tests for the user"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get query parameters
        subject_id = request.args.get('subject_id', type=int)
        paper_type = request.args.get('paper_type')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = UGCNetMockTest.query
        
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        
        if paper_type:
            query = query.filter_by(paper_type=paper_type)
        
        # Get paginated results
        mock_tests = query.order_by(desc(UGCNetMockTest.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Add attempt statistics for each test
        tests_data = []
        for test in mock_tests.items:
            test_dict = test.to_dict()
            
            # Get user's attempt statistics
            user_attempts = UGCNetMockAttempt.query.filter_by(
                mock_test_id=test.id,
                user_id=user.id
            ).all()
            
            test_dict['user_attempts'] = len(user_attempts)
            test_dict['best_score'] = max([attempt.score for attempt in user_attempts]) if user_attempts else None
            test_dict['last_attempted'] = max([attempt.created_at for attempt in user_attempts]) if user_attempts else None
            
            tests_data.append(test_dict)
        
        return jsonify({
            'mock_tests': tests_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': mock_tests.total,
                'pages': mock_tests.pages,
                'has_next': mock_tests.has_next,
                'has_prev': mock_tests.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ugc_net_mock_bp.route('/mock-tests/<int:test_id>', methods=['GET'])
@jwt_required()
def get_mock_test_details(test_id):
    """Get detailed information about a specific mock test"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        mock_test = UGCNetMockTest.query.get_or_404(test_id)
        
        # Include questions or not based on query parameter
        include_questions = request.args.get('include_questions', 'false').lower() == 'true'
        
        test_dict = mock_test.to_dict(include_questions=include_questions)
        
        # Add user's attempt history
        user_attempts = UGCNetMockAttempt.query.filter_by(
            mock_test_id=test_id,
            user_id=user.id
        ).order_by(desc(UGCNetMockAttempt.created_at)).all()
        
        test_dict['user_attempts'] = [attempt.to_dict() for attempt in user_attempts]
        
        return jsonify(test_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ugc_net_mock_bp.route('/mock-tests/<int:test_id>/attempt', methods=['POST'])
@jwt_required()
def start_mock_test_attempt(test_id):
    """Start a new attempt for a mock test"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        mock_test = UGCNetMockTest.query.get_or_404(test_id)
        
        # Check if user has an ongoing attempt
        ongoing_attempt = UGCNetMockAttempt.query.filter_by(
            mock_test_id=test_id,
            user_id=user.id,
            status='in_progress'
        ).first()
        
        if ongoing_attempt:
            # Check if the ongoing attempt has expired
            time_limit_minutes = mock_test.time_limit
            expiry_time = ongoing_attempt.start_time + timedelta(minutes=time_limit_minutes)
            
            if datetime.utcnow() > expiry_time:
                # Auto-submit the expired attempt
                ongoing_attempt.status = 'completed'
                ongoing_attempt.end_time = expiry_time
                ongoing_attempt.score = 0.0
                ongoing_attempt.percentage = 0.0
                ongoing_attempt.correct_answers = 0
                ongoing_attempt.total_questions = mock_test.total_questions
                db.session.commit()
                
                # Clear the ongoing_attempt to create a new fresh one below
                ongoing_attempt = None
            else:
                # Generate questions for the valid ongoing attempt
                generator = UGCNetPaperGenerator()
                
                # Build configuration from mock test
                config = {
                    'subject_id': mock_test.subject_id,
                    'paper_type': mock_test.paper_type,
                    'total_questions': mock_test.total_questions,
                    'difficulty_distribution': {
                        'easy': mock_test.easy_percentage,
                        'medium': mock_test.medium_percentage,
                        'hard': mock_test.hard_percentage
                    },
                    'source_distribution': {
                        'previous_year': mock_test.previous_year_percentage,
                        'ai_generated': mock_test.ai_generated_percentage,
                        'manual': 100 - mock_test.previous_year_percentage - mock_test.ai_generated_percentage
                    },
                    'weightage_config': mock_test.get_weightage_config()
                }
                
                # Generate questions
                result = generator.generate_paper(config)
                
                if result['success']:
                    ongoing_attempt_dict = ongoing_attempt.to_dict()
                    ongoing_attempt_dict['questions'] = [q.to_dict() for q in result['paper']['questions']]
                    ongoing_attempt_dict['statistics'] = result['statistics']
                else:
                    ongoing_attempt_dict = ongoing_attempt.to_dict()
                    ongoing_attempt_dict['error'] = f'Failed to generate questions: {result["error"]}'
                
                return jsonify({
                    'message': 'You have an ongoing attempt for this test',
                    'attempt': ongoing_attempt_dict
                }), 200
        
        # Create new attempt (either no ongoing attempt or the old one was expired and cleaned up)
        attempt = UGCNetMockAttempt(
            mock_test_id=test_id,
            user_id=user.id,
            status='in_progress',
            start_time=datetime.utcnow(),
            time_limit=mock_test.time_limit
        )
        
        db.session.add(attempt)
        db.session.commit()
        
        # Generate questions for this attempt using the mock test configuration
        generator = UGCNetPaperGenerator()
        
        # Build configuration from mock test
        config = {
            'subject_id': mock_test.subject_id,
            'paper_type': mock_test.paper_type,
            'total_questions': mock_test.total_questions,
            'difficulty_distribution': {
                'easy': mock_test.easy_percentage,
                'medium': mock_test.medium_percentage,
                'hard': mock_test.hard_percentage
            },
            'source_distribution': {
                'previous_year': mock_test.previous_year_percentage,
                'ai_generated': mock_test.ai_generated_percentage,
                'manual': 100 - mock_test.previous_year_percentage - mock_test.ai_generated_percentage
            },
            'weightage_config': mock_test.get_weightage_config()
        }
        
        # Generate questions
        result = generator.generate_paper(config)
        
        if not result['success']:
            db.session.delete(attempt)
            db.session.commit()
            return jsonify({'error': f'Failed to generate questions: {result["error"]}'}), 400
        
        # Return attempt details with questions
        attempt_dict = attempt.to_dict()
        attempt_dict['questions'] = [q.to_dict() for q in result['paper']['questions']]
        attempt_dict['statistics'] = result['statistics']
        
        return jsonify({
            'message': 'Mock test attempt started',
            'attempt': attempt_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ugc_net_mock_bp.route('/mock-tests/<int:test_id>/attempt/<int:attempt_id>/submit', methods=['POST'])
@jwt_required()
def submit_mock_test_attempt(test_id, attempt_id):
    """Submit answers for a mock test attempt"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        attempt = UGCNetMockAttempt.query.filter_by(
            id=attempt_id,
            mock_test_id=test_id,
            user_id=user.id
        ).first_or_404()
        
        if attempt.status != 'in_progress':
            return jsonify({'error': 'This attempt has already been submitted'}), 400
        
        data = request.get_json()
        answers = data.get('answers', {})
        
        # Get mock test
        mock_test = UGCNetMockTest.query.get(test_id)
        
        # Generate the same questions that were used in the attempt to validate answers
        generator = UGCNetPaperGenerator()
        
        # Build configuration from mock test
        config = {
            'subject_id': mock_test.subject_id,
            'paper_type': mock_test.paper_type,
            'total_questions': mock_test.total_questions,
            'difficulty_distribution': {
                'easy': mock_test.easy_percentage,
                'medium': mock_test.medium_percentage,
                'hard': mock_test.hard_percentage
            },
            'source_distribution': {
                'previous_year': mock_test.previous_year_percentage,
                'ai_generated': mock_test.ai_generated_percentage,
                'manual': 100 - mock_test.previous_year_percentage - mock_test.ai_generated_percentage
            },
            'weightage_config': mock_test.get_weightage_config()
        }
        
        # Generate questions to get the correct answers
        result = generator.generate_paper(config)
        
        # Calculate actual score
        correct_answers = 0
        total_marks = 0
        obtained_marks = 0
        
        if result['success']:
            questions = result['paper']['questions']
            
            # Create a mapping of question ID to correct answer and marks
            question_answers = {}
            question_marks = {}
            for q in questions:
                question_answers[str(q.id)] = q.correct_option if hasattr(q, 'correct_option') else 'A'  # Default fallback
                question_marks[str(q.id)] = q.marks if hasattr(q, 'marks') else 2  # Default 2 marks per question
                total_marks += question_marks[str(q.id)]
            
            # Check submitted answers
            for question_id, submitted_answer in answers.items():
                if question_id in question_answers:
                    if submitted_answer == question_answers[question_id]:
                        correct_answers += 1
                        obtained_marks += question_marks.get(question_id, 2)  # Use actual marks for this question
        else:
            # Fallback if question generation fails
            total_marks = mock_test.total_questions * 2
            correct_answers = 0
            obtained_marks = 0
        
        # Calculate percentage
        percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
        
        # Determine qualification status based on UGC NET criteria
        qualification_status = 'not_qualified'
        if percentage >= 60:
            qualification_status = 'qualified'
        elif percentage >= 40:
            qualification_status = 'borderline'
        else:
            qualification_status = 'not_qualified'
        
        # Update attempt
        attempt.status = 'completed'
        attempt.end_time = datetime.utcnow()
        attempt.answers_data = json.dumps(answers)
        attempt.score = obtained_marks
        attempt.correct_answers = correct_answers
        attempt.total_questions = mock_test.total_questions
        attempt.total_marks = total_marks
        attempt.percentage = percentage
        attempt.qualification_status = qualification_status
        
        # Calculate time taken
        time_taken_minutes = (attempt.end_time - attempt.start_time).total_seconds() / 60
        
        # Analytics
        analytics = {
            'total_time_taken': time_taken_minutes,
            'submitted_answers': len(answers),
            'completion_status': 'completed',
            'accuracy': (correct_answers / mock_test.total_questions * 100) if mock_test.total_questions > 0 else 0
        }
        
        attempt.analytics = json.dumps(analytics)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Mock test submitted successfully',
            'attempt': attempt.to_dict(),
            'results': {
                'score': attempt.score,
                'correct_answers': attempt.correct_answers,
                'total_questions': attempt.total_questions,
                'obtained_marks': attempt.score,
                'total_marks': total_marks,
                'analytics': json.loads(attempt.analytics)
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ugc_net_mock_bp.route('/mock-tests/<int:test_id>/attempt/<int:attempt_id>/results', methods=['GET'])
@jwt_required()
def get_attempt_results(test_id, attempt_id):
    """Get detailed results for a completed mock test attempt"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        attempt = UGCNetMockAttempt.query.filter_by(
            id=attempt_id,
            mock_test_id=test_id,
            user_id=user.id
        ).first_or_404()
        
        if attempt.status != 'completed':
            return jsonify({'error': 'This attempt is not yet completed'}), 400
        
        # Get detailed results
        attempt_dict = attempt.to_dict()
        
        # Include correct answers and explanations if requested
        include_solutions = request.args.get('include_solutions', 'false').lower() == 'true'
        
        if include_solutions:
            # For now, we'll return basic attempt data
            # TODO: Implement proper question storage and retrieval for detailed solutions
            attempt_dict['note'] = 'Detailed solutions not available in current implementation'
        
        return jsonify(attempt_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ugc_net_mock_bp.route('/mock-tests/<int:test_id>/attempts', methods=['GET'])
@jwt_required()
def get_test_attempts(test_id):
    """Get all attempts for a specific mock test (for the current user)"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        mock_test = UGCNetMockTest.query.get_or_404(test_id)
        
        attempts = UGCNetMockAttempt.query.filter_by(
            mock_test_id=test_id,
            user_id=user.id
        ).order_by(desc(UGCNetMockAttempt.created_at)).all()
        
        attempts_data = [attempt.to_dict() for attempt in attempts]
        
        return jsonify({
            'mock_test': mock_test.to_dict(),
            'attempts': attempts_data,
            'total_attempts': len(attempts)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
