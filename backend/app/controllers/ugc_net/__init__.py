"""
UGC NET Modular Controller - Main Entry Point

This is the main controller that imports and registers all UGC NET sub-controllers.
This modular approach breaks down the large ugc_net_controller.py into manageable pieces:

1. subject_controller.py - Subject and chapter management
2. question_controller.py - Question bank management  
3. mock_test_controller.py - Mock test generation and management
4. practice_test_controller.py - Practice test management

All routes are preserved with the same endpoints to maintain backward compatibility.
"""

from flask import Blueprint
from .subject_controller import ugc_net_subject_bp
from .question_controller import ugc_net_question_bp
from .mock_test_controller import ugc_net_mock_bp
from .practice_test_controller import ugc_net_practice_bp

# Create the main blueprint
ugc_net_modular_bp = Blueprint('ugc_net_modular', __name__)

def register_ugc_net_blueprints(app):
    """Register all UGC NET modular blueprints with the Flask app"""
    
    # Register individual blueprints with appropriate URL prefixes
    app.register_blueprint(ugc_net_subject_bp, url_prefix='/api/ugc-net')
    app.register_blueprint(ugc_net_question_bp, url_prefix='/api/ugc-net')
    app.register_blueprint(ugc_net_mock_bp, url_prefix='/api/ugc-net')
    app.register_blueprint(ugc_net_practice_bp, url_prefix='/api/ugc-net')
    
    return True

# For backward compatibility, also create a combined blueprint that includes all routes
def create_combined_blueprint():
    """Create a combined blueprint that includes all UGC NET routes for easier registration"""
    combined_bp = Blueprint('ugc_net_combined', __name__)
    
    # Import all route functions and register them with the combined blueprint
    from .subject_controller import (
        get_ugc_net_subjects, get_subject_chapters, get_ugc_net_statistics,
        create_subject, create_chapter, get_user_registered_subject, export_user_analytics
    )
    from .question_controller import add_question, bulk_import_questions
    from .mock_test_controller import (
        generate_mock_test, get_mock_tests, get_mock_test_details,
        start_mock_test_attempt, submit_mock_test_attempt, 
        get_attempt_results, get_test_attempts
    )
    from .practice_test_controller import (
        generate_practice_test, auto_save_answers, submit_practice_test,
        get_practice_test_results, get_practice_tests, get_practice_test
    )
    
    # Register all routes with the combined blueprint
    # Subject routes
    combined_bp.add_url_rule('/subjects', 'get_ugc_net_subjects', get_ugc_net_subjects, methods=['GET'])
    combined_bp.add_url_rule('/subjects/<int:subject_id>/chapters', 'get_subject_chapters', get_subject_chapters, methods=['GET'])
    combined_bp.add_url_rule('/statistics', 'get_ugc_net_statistics', get_ugc_net_statistics, methods=['GET'])
    combined_bp.add_url_rule('/admin/subjects', 'create_subject', create_subject, methods=['POST'])
    combined_bp.add_url_rule('/admin/subjects/<int:subject_id>/chapters', 'create_chapter', create_chapter, methods=['POST'])
    combined_bp.add_url_rule('/user/subject', 'get_user_registered_subject', get_user_registered_subject, methods=['GET'])
    combined_bp.add_url_rule('/analytics/export', 'export_user_analytics', export_user_analytics, methods=['POST'])
    
    # Question routes
    combined_bp.add_url_rule('/question-bank/add', 'add_question', add_question, methods=['POST'])
    combined_bp.add_url_rule('/question-bank/bulk-import', 'bulk_import_questions', bulk_import_questions, methods=['POST'])
    
    # Mock test routes
    combined_bp.add_url_rule('/mock-tests/generate', 'generate_mock_test', generate_mock_test, methods=['POST'])
    combined_bp.add_url_rule('/mock-tests', 'get_mock_tests', get_mock_tests, methods=['GET'])
    combined_bp.add_url_rule('/mock-tests/<int:test_id>', 'get_mock_test_details', get_mock_test_details, methods=['GET'])
    combined_bp.add_url_rule('/mock-tests/<int:test_id>/attempt', 'start_mock_test_attempt', start_mock_test_attempt, methods=['POST'])
    combined_bp.add_url_rule('/mock-tests/<int:test_id>/attempt/<int:attempt_id>/submit', 'submit_mock_test_attempt', submit_mock_test_attempt, methods=['POST'])
    combined_bp.add_url_rule('/mock-tests/<int:test_id>/attempt/<int:attempt_id>/results', 'get_attempt_results', get_attempt_results, methods=['GET'])
    combined_bp.add_url_rule('/mock-tests/<int:test_id>/attempts', 'get_test_attempts', get_test_attempts, methods=['GET'])
    
    # Practice test routes
    combined_bp.add_url_rule('/practice-tests/generate', 'generate_practice_test', generate_practice_test, methods=['POST'])
    combined_bp.add_url_rule('/practice-tests/attempts/<int:attempt_id>/answers', 'auto_save_answers', auto_save_answers, methods=['PUT'])
    combined_bp.add_url_rule('/practice-tests/attempts/<int:attempt_id>/submit', 'submit_practice_test', submit_practice_test, methods=['POST'])
    combined_bp.add_url_rule('/practice-tests/attempts/<int:attempt_id>/results', 'get_practice_test_results', get_practice_test_results, methods=['GET'])
    combined_bp.add_url_rule('/practice-tests', 'get_practice_tests', get_practice_tests, methods=['GET'])
    combined_bp.add_url_rule('/practice-tests/attempts/<int:attempt_id>', 'get_practice_test', get_practice_test, methods=['GET'])
    
    return combined_bp
