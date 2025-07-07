"""UGC NET Subject and Chapter Management Controller"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import desc, func
from app import db
from app.models import User, Subject, Chapter, QuestionBank, UGCNetPracticeAttempt, UGCNetMockAttempt
from app.utils.ugc_net_seed_data import get_subject_weightage_info
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
@jwt_required()
def get_ugc_net_subjects():
    """Get all UGC NET subjects with their details"""
    try:
        subjects = Subject.query.filter(Subject.subject_code.isnot(None)).all()
        subjects_data = []
        
        for subject in subjects:
            subject_dict = subject.to_dict()
            # Add weightage information
            try:
                weightage_info = get_subject_weightage_info(subject.id, 'paper2')
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
        
        # User's recent practice scores
        recent_practice_attempts = UGCNetPracticeAttempt.query.filter_by(
            user_id=current_user.id
        ).filter(
            UGCNetPracticeAttempt.score != None
        ).order_by(desc(UGCNetPracticeAttempt.created_at)).limit(5).all()
        
        # User's recent mock scores
        recent_mock_attempts = UGCNetMockAttempt.query.filter_by(
            user_id=current_user.id
        ).filter(
            UGCNetMockAttempt.score != None
        ).order_by(desc(UGCNetMockAttempt.created_at)).limit(5).all()
        
        # Calculate average scores
        practice_scores = [attempt.score for attempt in recent_practice_attempts]
        mock_scores = [attempt.score for attempt in recent_mock_attempts]
        all_scores = practice_scores + mock_scores
        
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        best_score = max(all_scores) if all_scores else 0

        return jsonify({
            'overview': {
                'total_subjects': total_subjects,
                'total_chapters': total_chapters,
                'total_questions': total_questions,
                'subjects_needing_questions': len(subjects_needing_questions)
            },
            'user_stats': {
                'total_attempts': total_user_attempts,
                'practice_attempts': user_practice_attempts,
                'mock_attempts': user_mock_attempts,
                'average_score': round(avg_score, 1),
                'best_score': round(best_score, 1)
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
            created_at=datetime.utcnow()
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
