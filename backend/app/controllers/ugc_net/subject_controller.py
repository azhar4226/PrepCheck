"""UGC NET Subject and Chapter Management Controller"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import desc, func
from app import db
from app.models import User, Subject, Chapter, QuestionBank, UGCNetPracticeAttempt, UGCNetMockAttempt, UGCNetMockTest, UGCNetMockTest
from app.utils.seed_subjects_and_chapters import get_subject_weightage_info
from app.utils.timezone_utils import get_ist_now
from app.services.user_metrics_service import UserMetricsService
from app.services.ai_study_recommendation_service import AIStudyRecommendationService
import json

ugc_net_subject_bp = Blueprint('ugc_net_subject', __name__)


def get_current_user():
    """Get current user from JWT token"""
    try:
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except:
        return None


@ugc_net_subject_bp.route('/subjects', methods=['GET'])
def get_ugc_net_subjects():
    """Get all UGC NET subjects with their details"""
    try:
        subjects = Subject.query.filter(Subject.subject_code.isnot(None)).all()
        subjects_data = []
        
        for subject in subjects:
            subject_dict = subject.to_dict()
            # Add weightage information
            try:
                weightage_info = get_subject_weightage_info(subject.id)
                subject_dict['weightage_info'] = weightage_info
            except:
                subject_dict['weightage_info'] = {'chapters': []}
            subjects_data.append(subject_dict)
        
        return jsonify({
            'subjects': subjects_data,
            'total': len(subjects_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch subjects: {str(e)}'}), 500


@ugc_net_subject_bp.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
@jwt_required()
def get_subject_chapters(subject_id):
    """Get all chapters for a specific subject with question counts"""
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
            
        paper_type = request.args.get('paper_type', 'paper2')
        chapters = Chapter.query.filter_by(subject_id=subject_id).order_by(Chapter.chapter_order).all()
        chapters_data = []
        
        for chapter in chapters:
            chapter_dict = chapter.to_dict()
            
            # Add weightage based on paper type
            if paper_type == 'paper1':
                chapter_dict['weightage'] = getattr(chapter, 'weightage_paper1', 0)
                chapter_dict['estimated_questions'] = getattr(chapter, 'estimated_questions_paper1', 0)
            else:
                chapter_dict['weightage'] = getattr(chapter, 'weightage_paper2', 0)
                chapter_dict['estimated_questions'] = getattr(chapter, 'estimated_questions_paper2', 0)
            
            # Add question bank statistics (count both total and verified questions)
            total_questions = QuestionBank.query.filter_by(chapter_id=chapter.id).count()
            verified_questions = QuestionBank.query.filter_by(
                chapter_id=chapter.id, is_verified=True
            ).count()
            
            chapter_dict['total_questions_in_bank'] = total_questions
            chapter_dict['verified_questions'] = verified_questions
            chapter_dict['question_count'] = verified_questions  # For practice test setup
            
            chapters_data.append(chapter_dict)
        
        return jsonify({
            'subject': subject.to_dict(),
            'chapters': chapters_data,
            'total_chapters': len(chapters_data),
            'paper_type': paper_type
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch chapters: {str(e)}'}), 500


@ugc_net_subject_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_ugc_net_statistics():
    """Get comprehensive UGC NET statistics"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Basic counts
        total_subjects = Subject.query.filter(Subject.subject_code.isnot(None)).count()
        total_chapters = Chapter.query.join(Subject).filter(Subject.subject_code.isnot(None)).count()
        total_questions = QuestionBank.query.join(Chapter, QuestionBank.chapter_id == Chapter.id).join(Subject, Chapter.subject_id == Subject.id).filter(Subject.subject_code.isnot(None)).count()
        
        # Subject-wise question distribution
        subject_stats = db.session.query(
            Subject.id,
            Subject.name,
            func.count(QuestionBank.id).label('question_count')
        ).join(Chapter, Subject.id == Chapter.subject_id).join(QuestionBank, Chapter.id == QuestionBank.chapter_id).filter(
            Subject.subject_code.isnot(None)
        ).group_by(Subject.id, Subject.name).all()
        
        subject_distribution = [
            {
                'subject_id': stat.id,
                'subject_name': stat.name,
                'question_count': stat.question_count
            }
            for stat in subject_stats
        ]
        
        # Chapter-wise statistics for subjects with questions
        chapter_stats = db.session.query(
            Chapter.id,
            Chapter.name,
            Chapter.subject_id,
            Subject.name.label('subject_name'),
            func.count(QuestionBank.id).label('question_count')
        ).join(Subject, Chapter.subject_id == Subject.id).join(QuestionBank, Chapter.id == QuestionBank.chapter_id).filter(
            Subject.subject_code.isnot(None)
        ).group_by(
            Chapter.id, Chapter.name, Chapter.subject_id, Subject.name
        ).all()
        
        chapter_distribution = [
            {
                'chapter_id': stat.id,
                'chapter_name': stat.name,
                'subject_id': stat.subject_id,
                'subject_name': stat.subject_name,
                'question_count': stat.question_count
            }
            for stat in chapter_stats
        ]
         # Get subjects with insufficient questions (less than 50)
        subjects_needing_questions = [
            stat for stat in subject_distribution
            if stat['question_count'] < 50
        ]
        
        # User-specific statistics
        user_practice_attempts = UGCNetPracticeAttempt.query.filter_by(user_id=current_user.id).count()
        user_mock_attempts = UGCNetMockAttempt.query.filter_by(user_id=current_user.id).count()
        total_user_attempts = user_practice_attempts + user_mock_attempts
        
        # Get all completed attempts for the user
        completed_practice_attempts = UGCNetPracticeAttempt.query.filter_by(
            user_id=current_user.id, is_completed=True
        ).filter(
            UGCNetPracticeAttempt.percentage != None
        ).all()
        
        completed_mock_attempts = UGCNetMockAttempt.query.filter_by(
            user_id=current_user.id, is_completed=True
        ).filter(
            UGCNetMockAttempt.percentage != None
        ).all()
        
        # Calculate comprehensive statistics with percentage validation
        practice_scores = [min(max(attempt.percentage, 0), 100) for attempt in completed_practice_attempts if attempt.percentage is not None]
        mock_scores = [min(max(attempt.percentage, 0), 100) for attempt in completed_mock_attempts if attempt.percentage is not None]
        all_scores = practice_scores + mock_scores
        
        # Calculate averages and best scores (ensure they don't exceed 100%)
        avg_score = min(sum(all_scores) / len(all_scores), 100) if all_scores else 0
        best_score = min(max(all_scores), 100) if all_scores else 0
        
        # Calculate qualified attempts (>=40%)
        qualified_practice = len([score for score in practice_scores if score >= 40])
        qualified_mock = len([score for score in mock_scores if score >= 40])
        total_qualified = qualified_practice + qualified_mock
        
        # Calculate qualification rate
        completed_attempts = len(all_scores)
        qualification_rate = (total_qualified / completed_attempts * 100) if completed_attempts > 0 else 0

        return jsonify({
            'overview': {
                'total_subjects': total_subjects,
                'total_chapters': total_chapters,
                'total_questions': total_questions,
                'subjects_needing_questions': len(subjects_needing_questions)
            },
            'user_stats': {
                'total_attempts': total_user_attempts,
                'completed_attempts': completed_attempts,
                'practice_attempts': user_practice_attempts,
                'mock_attempts': user_mock_attempts,
                'average_score': round(avg_score, 1),
                'best_score': round(best_score, 1),
                'qualified_attempts': total_qualified,
                'qualification_rate': round(qualification_rate, 1)
            },
            'subject_distribution': subject_distribution,
            'chapter_distribution': chapter_distribution,
            'subjects_needing_questions': subjects_needing_questions
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch statistics: {str(e)}'}), 500


@ugc_net_subject_bp.route('/admin/subjects', methods=['POST'])
@jwt_required()
def create_subject():
    """Create a new subject (Admin only)"""
    try:
        current_user = get_current_user()
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['name', 'subject_code']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if subject already exists
        existing_subject = Subject.query.filter_by(subject_code=data['subject_code']).first()
        if existing_subject:
            return jsonify({'error': 'Subject with this code already exists'}), 400
        
        subject = Subject(
            name=data['name'],
            subject_code=data['subject_code'],
            description=data.get('description', ''),
            created_at=get_ist_now()
        )
        
        db.session.add(subject)
        db.session.commit()
        
        return jsonify({
            'message': 'Subject created successfully',
            'subject': subject.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create subject: {str(e)}'}), 500


@ugc_net_subject_bp.route('/admin/subjects/<int:subject_id>/chapters', methods=['POST'])
@jwt_required()
def create_chapter(subject_id):
    """Create a new chapter for a subject (Admin only)"""
    try:
        current_user = get_current_user()
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        chapter = Chapter(
            name=data['name'],
            subject_id=subject_id,
            description=data.get('description', ''),
            created_at=datetime.utcnow()
        )
        
        db.session.add(chapter)
        db.session.commit()
        
        return jsonify({
            'message': 'Chapter created successfully',
            'chapter': chapter.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create chapter: {str(e)}'}), 500


@ugc_net_subject_bp.route('/admin/questions/verify-all', methods=['POST'])
@jwt_required()
def bulk_verify_questions():
    """Bulk verify all unverified questions (Admin only)"""
    try:
        current_user = get_current_user()
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get all unverified questions
        unverified_questions = QuestionBank.query.filter_by(is_verified=False).all()
        
        if not unverified_questions:
            return jsonify({
                'message': 'No unverified questions found',
                'verified_count': 0
            }), 200
        
        # Update all unverified questions
        verified_count = 0
        for question in unverified_questions:
            question.is_verified = True
            question.verification_method = 'admin_bulk'
            question.verified_by = current_user.id
            question.verified_at = datetime.utcnow()
            verified_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully verified {verified_count} questions',
            'verified_count': verified_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to verify questions: {str(e)}'}), 500


@ugc_net_subject_bp.route('/admin/questions/status', methods=['GET'])
@jwt_required()
def get_question_verification_status():
    """Get question verification status overview (Admin only)"""
    try:
        current_user = get_current_user()
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get verification statistics
        total_questions = QuestionBank.query.count()
        verified_questions = QuestionBank.query.filter_by(is_verified=True).count()
        unverified_questions = QuestionBank.query.filter_by(is_verified=False).count()
        
        # Get chapter-wise breakdown
        chapter_stats = db.session.query(
            Chapter.id,
            Chapter.name,
            Subject.name.label('subject_name'),
            func.count(QuestionBank.id).label('total_questions'),
            func.sum(func.case([(QuestionBank.is_verified == True, 1)], else_=0)).label('verified_questions')
        ).join(Subject).outerjoin(QuestionBank).group_by(
            Chapter.id, Chapter.name, Subject.name
        ).all()
        
        chapter_breakdown = []
        for stat in chapter_stats:
            chapter_breakdown.append({
                'chapter_id': stat.id,
                'chapter_name': stat.name,
                'subject_name': stat.subject_name,
                'total_questions': stat.total_questions or 0,
                'verified_questions': stat.verified_questions or 0,
                'unverified_questions': (stat.total_questions or 0) - (stat.verified_questions or 0)
            })
        
        return jsonify({
            'overview': {
                'total_questions': total_questions,
                'verified_questions': verified_questions,
                'unverified_questions': unverified_questions,
                'verification_percentage': (verified_questions / total_questions * 100) if total_questions > 0 else 0
            },
            'chapter_breakdown': chapter_breakdown
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get verification status: {str(e)}'}), 500


@ugc_net_subject_bp.route('/analytics/export', methods=['POST'])
@jwt_required()
def export_user_analytics():
    """Export user's UGC NET analytics with timeline support"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        timeline = data.get('timeline', 'all')  # 'all', 'last_30_days', 'last_3_months', 'last_6_months'
        
        # Calculate date range based on timeline
        end_date = datetime.utcnow()
        if timeline == 'last_30_days':
            start_date = end_date - timedelta(days=30)
        elif timeline == 'last_3_months':
            start_date = end_date - timedelta(days=90)
        elif timeline == 'last_6_months':
            start_date = end_date - timedelta(days=180)
        else:
            start_date = None  # All time
        
        # Get user's test history
        mock_attempts_query = UGCNetMockAttempt.query.filter_by(user_id=user.id)
        practice_attempts_query = UGCNetPracticeAttempt.query.filter_by(user_id=user.id)
        
        if start_date:
            mock_attempts_query = mock_attempts_query.filter(UGCNetMockAttempt.created_at >= start_date)
            practice_attempts_query = practice_attempts_query.filter(UGCNetPracticeAttempt.created_at >= start_date)
        
        mock_attempts = mock_attempts_query.order_by(desc(UGCNetMockAttempt.created_at)).all()
        practice_attempts = practice_attempts_query.order_by(desc(UGCNetPracticeAttempt.created_at)).all()
        
        # Prepare analytics data
        analytics_data = {
            'user_info': {
                'name': user.full_name,
                'email': user.email,
                'registered_subject': user.registered_subject.name if user.registered_subject else 'Not specified',
                'registration_date': user.created_at.isoformat(),
                'total_login_days': 'N/A'  # Would need tracking for accurate count
            },
            'export_info': {
                'generated_at': get_ist_now().isoformat(),
                'timeline': timeline,
                'date_range': {
                    'start': start_date.isoformat() if start_date else 'All time',
                    'end': end_date.isoformat()
                }
            },
            'summary_statistics': {
                'total_mock_attempts': len(mock_attempts),
                'total_practice_attempts': len(practice_attempts),
                'completed_mock_attempts': len([a for a in mock_attempts if a.is_completed]),
                'completed_practice_attempts': len([a for a in practice_attempts if a.is_completed]),
            },
            'performance_metrics': {},
            'mock_test_history': [],
            'practice_test_history': []
        }
        
        # Calculate performance metrics
        completed_mock = [a for a in mock_attempts if a.is_completed and a.percentage is not None]
        completed_practice = [a for a in practice_attempts if a.is_completed and a.percentage is not None]
        
        if completed_mock:
            mock_scores = [a.percentage for a in completed_mock]
            analytics_data['performance_metrics']['mock_tests'] = {
                'average_score': round(sum(mock_scores) / len(mock_scores), 2),
                'best_score': max(mock_scores),
                'worst_score': min(mock_scores),
                'pass_rate': round((len([s for s in mock_scores if s >= 40]) / len(mock_scores)) * 100, 2)
            }
        
        if completed_practice:
            practice_scores = [a.percentage for a in completed_practice]
            analytics_data['performance_metrics']['practice_tests'] = {
                'average_score': round(sum(practice_scores) / len(practice_scores), 2),
                'best_score': max(practice_scores),
                'worst_score': min(practice_scores),
                'pass_rate': round((len([s for s in practice_scores if s >= 60]) / len(practice_scores)) * 100, 2)
            }
        
        # Add detailed test history
        for attempt in mock_attempts:
            analytics_data['mock_test_history'].append({
                'test_name': attempt.test.title if attempt.test else 'Unknown Test',
                'date_taken': attempt.created_at.isoformat(),
                'completed': attempt.is_completed,
                'score_percentage': attempt.percentage,
                'time_taken_minutes': attempt.time_taken,
                'total_questions': attempt.total_questions,
                'correct_answers': attempt.correct_answers,
                'status': 'Completed' if attempt.is_completed else 'Incomplete'
            })
        
        for attempt in practice_attempts:
            analytics_data['practice_test_history'].append({
                'chapter_name': attempt.chapter.name if attempt.chapter else 'Unknown Chapter',
                'subject_name': attempt.chapter.subject.name if attempt.chapter and attempt.chapter.subject else 'Unknown Subject',
                'date_taken': attempt.created_at.isoformat(),
                'completed': attempt.is_completed,
                'score_percentage': attempt.percentage,
                'time_taken_minutes': attempt.time_taken,
                'total_questions': attempt.total_questions,
                'correct_answers': attempt.correct_answers,
                'status': 'Completed' if attempt.is_completed else 'Incomplete'
            })
        
        return jsonify({
            'success': True,
            'data': analytics_data,
            'message': 'Analytics data exported successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to export analytics: {str(e)}'
        }), 500


@ugc_net_subject_bp.route('/user/subject', methods=['GET'])
@jwt_required()
def get_user_registered_subject():
    """Get the user's registered subject with chapters and study materials"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.subject_id or not user.registered_subject:
            return jsonify({
                'error': 'No subject registered',
                'message': 'Please update your profile to select a subject for UGC NET preparation'
            }), 404
        
        subject = user.registered_subject
        subject_data = subject.to_dict()
        
        # Get chapters for the subject
        chapters = Chapter.query.filter_by(subject_id=subject.id).order_by(Chapter.name).all()
        subject_data['chapters'] = [chapter.to_dict() for chapter in chapters]
        
        # Get user's performance for this subject
        mock_attempts = UGCNetMockAttempt.query.join(UGCNetMockTest).filter(
            UGCNetMockAttempt.user_id == user.id,
            UGCNetMockTest.subject_id == subject.id
        ).all()
        
        practice_attempts = UGCNetPracticeAttempt.query.join(Chapter).filter(
            UGCNetPracticeAttempt.user_id == user.id,
            Chapter.subject_id == subject.id
        ).all()
        
        # Calculate subject-specific performance
        completed_mock = [a for a in mock_attempts if a.is_completed and a.percentage is not None]
        completed_practice = [a for a in practice_attempts if a.is_completed and a.percentage is not None]
        
        performance_data = {
            'total_mock_attempts': len(mock_attempts),
            'total_practice_attempts': len(practice_attempts),
            'completed_mock_attempts': len(completed_mock),
            'completed_practice_attempts': len(completed_practice),
            'average_mock_score': 0,
            'average_practice_score': 0,
            'best_score': 0,
            'recent_activity': []
        }
        
        if completed_mock:
            mock_scores = [a.percentage for a in completed_mock]
            performance_data['average_mock_score'] = round(sum(mock_scores) / len(mock_scores), 1)
            performance_data['best_score'] = max(performance_data['best_score'], max(mock_scores))
        
        if completed_practice:
            practice_scores = [a.percentage for a in completed_practice]
            performance_data['average_practice_score'] = round(sum(practice_scores) / len(practice_scores), 1)
            performance_data['best_score'] = max(performance_data['best_score'], max(practice_scores))
        
        # Get recent activity (last 5 attempts)
        all_attempts = []
        for attempt in mock_attempts:
            all_attempts.append({
                'type': 'mock',
                'name': attempt.test.title if attempt.test else 'Unknown Test',
                'date': attempt.created_at,
                'score': attempt.percentage,
                'completed': attempt.is_completed
            })
        
        for attempt in practice_attempts:
            all_attempts.append({
                'type': 'practice',
                'name': attempt.chapter.name if attempt.chapter else 'Unknown Chapter',
                'date': attempt.created_at,
                'score': attempt.percentage,
                'completed': attempt.is_completed
            })
        
        # Sort by date and take last 5
        all_attempts.sort(key=lambda x: x['date'], reverse=True)
        performance_data['recent_activity'] = all_attempts[:5]
        
        # Recommended study materials
        study_materials = {
            'syllabus': f'UGC NET {subject.name} Syllabus',
            'previous_papers': f'Previous Year Papers - {subject.name}',
            'reference_books': [
                f'{subject.name} - Comprehensive Guide',
                f'UGC NET {subject.name} - Practice Sets',
                f'{subject.name} - Solved Papers Collection'
            ],
            'online_resources': [
                f'{subject.name} Video Lectures',
                f'Interactive {subject.name} Tests',
                f'{subject.name} Study Notes'
            ]
        }
        
        return jsonify({
            'subject': subject_data,
            'performance': performance_data,
            'study_materials': study_materials,
            'message': f'Showing content for {subject.name}'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch user subject: {str(e)}'}), 500


@ugc_net_subject_bp.route('/incomplete-tests', methods=['GET'])
@jwt_required()
def get_incomplete_tests():
    """Get all incomplete tests (both practice and mock) for the current user"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404

        # Get incomplete practice attempts
        incomplete_practice = UGCNetPracticeAttempt.query.filter_by(
            user_id=current_user.id, 
            is_completed=False
        ).order_by(desc(UGCNetPracticeAttempt.created_at)).all()

        # Get incomplete mock attempts
        incomplete_mock = UGCNetMockAttempt.query.filter_by(
            user_id=current_user.id, 
            is_completed=False
        ).order_by(desc(UGCNetMockAttempt.created_at)).all()

        print(f"[DEBUG] Incomplete practice attempts for user {current_user.id}: {len(incomplete_practice)}")
        print(f"[DEBUG] Incomplete mock attempts for user {current_user.id}: {len(incomplete_mock)}")

        practice_tests = []
        for attempt in incomplete_practice:
            practice_tests.append({
                'id': attempt.id,
                'type': 'practice',
                'title': f"Practice Test - {attempt.subject.name if attempt.subject else 'Unknown'}",
                'subject_name': attempt.subject.name if attempt.subject else 'Unknown',
                'paper_type': attempt.paper_type or 'paper2',
                'total_questions': attempt.total_questions,
                'answered_questions': len(json.loads(attempt.answers_data or '{}')),
                'time_limit': attempt.time_limit,
                'created_at': attempt.created_at.isoformat(),
                'progress_percentage': (len(json.loads(attempt.answers_data or '{}')) / attempt.total_questions * 100) if attempt.total_questions > 0 else 0
            })

        mock_tests = []
        for attempt in incomplete_mock:
            mock_tests.append({
                'id': attempt.id,
                'type': 'mock',
                'title': attempt.mock_test.title if attempt.mock_test else 'Mock Test',
                'subject_name': attempt.mock_test.subject.name if attempt.mock_test and attempt.mock_test.subject else 'Unknown',
                'paper_type': 'paper1+paper2',
                'total_questions': attempt.total_questions,
                'answered_questions': len(json.loads(attempt.answers_data or '{}')),
                'time_limit': attempt.time_limit,
                'created_at': attempt.created_at.isoformat(),
                'progress_percentage': (len(json.loads(attempt.answers_data or '{}')) / attempt.total_questions * 100) if attempt.total_questions > 0 else 0
            })

        return jsonify({
            'success': True,
            'data': {
                'practice_tests': practice_tests,
                'mock_tests': mock_tests,
                'total_incomplete': len(practice_tests) + len(mock_tests)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch incomplete tests: {str(e)}'
        }), 500


@ugc_net_subject_bp.route('/ai/recommendations', methods=['GET'])
@jwt_required()
def get_ai_study_recommendations():
    """Get AI-generated study recommendations for the current user"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        max_recommendations = request.args.get('max_recommendations', 5, type=int)
        
        # Generate recommendations
        ai_service = AIStudyRecommendationService()
        recommendations = ai_service.generate_study_recommendations(
            current_user.id, 
            max_recommendations=max_recommendations
        )
        
        return jsonify({
            'recommendations': recommendations,
            'total': len(recommendations),
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate recommendations: {str(e)}'}), 500


@ugc_net_subject_bp.route('/ai/study-plan', methods=['GET'])
@jwt_required()
def get_ai_study_plan():
    """Get AI-generated personalized study plan for the current user"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        plan_duration_weeks = request.args.get('weeks', 12, type=int)
        
        # Validate duration (4-20 weeks)
        if plan_duration_weeks < 4 or plan_duration_weeks > 20:
            return jsonify({'error': 'Plan duration must be between 4 and 20 weeks'}), 400
        
        # Generate study plan
        ai_service = AIStudyRecommendationService()
        study_plan = ai_service.generate_study_plan(
            current_user.id,
            plan_duration_weeks=plan_duration_weeks
        )
        
        return jsonify(study_plan), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate study plan: {str(e)}'}), 500


@ugc_net_subject_bp.route('/metrics/comprehensive', methods=['GET'])
@jwt_required()
def get_comprehensive_user_metrics():
    """Get comprehensive user metrics for analysis"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        
        # Validate days parameter
        if days < 7 or days > 365:
            return jsonify({'error': 'Days parameter must be between 7 and 365'}), 400
        
        # Get comprehensive metrics
        metrics_service = UserMetricsService()
        metrics = metrics_service.get_comprehensive_user_metrics(current_user.id, days=days)
        
        return jsonify(metrics), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch comprehensive metrics: {str(e)}'}), 500
