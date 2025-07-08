from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import desc, func
from app import db, redis_client
from app.models import User, Subject, Chapter, QuestionBank, UGCNetMockTest, UGCNetMockAttempt, UGCNetPracticeAttempt
import json
import os

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))

# Dashboard Statistics
@admin_bp.route('/dashboard/test', methods=['GET'])
def test_dashboard_stats():
    """Test endpoint without authentication for debugging"""
    try:
        # Basic counts using new models
        total_users = User.query.filter_by(is_admin=False).count()
        total_subjects = Subject.query.filter_by(is_active=True).count()
        total_questions = QuestionBank.query.count()
        total_mock_tests = UGCNetMockTest.query.filter_by(is_active=True).count()
        total_mock_attempts = UGCNetMockAttempt.query.filter_by(is_completed=True).count()
        total_practice_attempts = UGCNetPracticeAttempt.query.filter_by(is_completed=True).count()
        
        simple_stats = {
            'total_users': total_users,
            'total_subjects': total_subjects,
            'total_questions': total_questions,
            'total_mock_tests': total_mock_tests,
            'total_mock_attempts': total_mock_attempts,
            'total_practice_attempts': total_practice_attempts,
            'debug': 'Updated to use new UGC NET models'
        }
        
        print(f"Test endpoint returning: {simple_stats}")
        return jsonify(simple_stats), 200
        
    except Exception as e:
        print(f"Test endpoint error: {e}")
        return jsonify({'error': str(e), 'debug': 'Error in test endpoint'}), 500

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Get comprehensive dashboard statistics using new models"""
    try:
        print("=== DASHBOARD ENDPOINT CALLED ===")
        # Check cache first
        cache_key = 'admin_dashboard_stats'
        cached_stats = None
        
        # Safe Redis operation with error handling
        try:
            if redis_client:
                cached_stats = redis_client.get(cache_key)
        except Exception as redis_error:
            print(f"Redis cache error: {redis_error}")
            # Continue without cache
        
        if cached_stats:
            try:
                print("Returning cached data")
                return jsonify(json.loads(cached_stats)), 200
            except:
                print("Failed to parse cached data, regenerating...")
        
        print("Generating fresh analytics data...")
        
        # Time filters
        time_filter = request.args.get('timeFilter', '7d')
        
        # Calculate date range
        if time_filter == '24h':
            start_date = datetime.utcnow() - timedelta(hours=24)
        elif time_filter == '7d':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif time_filter == '30d':
            start_date = datetime.utcnow() - timedelta(days=30)
        elif time_filter == '90d':
            start_date = datetime.utcnow() - timedelta(days=90)
        else:
            start_date = datetime.utcnow() - timedelta(days=7)

        # Basic counts with error handling
        try:
            total_users = User.query.filter_by(is_admin=False).count()
            active_users = User.query.filter(
                User.is_admin == False,
                User.last_login >= start_date
            ).count()
            
            total_subjects = Subject.query.filter_by(is_active=True).count()
            total_chapters = Chapter.query.filter_by(is_active=True).count()
            total_questions = QuestionBank.query.count()
            total_mock_tests = UGCNetMockTest.query.filter_by(is_active=True).count()
            
            # Attempt statistics using new models
            total_mock_attempts = UGCNetMockAttempt.query.filter_by(is_completed=True).count()
            recent_mock_attempts = UGCNetMockAttempt.query.filter(
                UGCNetMockAttempt.is_completed == True,
                UGCNetMockAttempt.completed_at >= start_date
            ).count()
            
            total_practice_attempts = UGCNetPracticeAttempt.query.filter_by(is_completed=True).count()
            recent_practice_attempts = UGCNetPracticeAttempt.query.filter(
                UGCNetPracticeAttempt.is_completed == True,
                UGCNetPracticeAttempt.completed_at >= start_date
            ).count()
            
            # User management stats
            total_admins = User.query.filter_by(is_admin=True).count()
            active_users_all = User.query.filter_by(is_active=True, is_admin=False).count()
            inactive_users = User.query.filter_by(is_active=False, is_admin=False).count()
            new_users_today = User.query.filter(
                User.created_at >= datetime.utcnow().date(),
                User.is_admin == False
            ).count()
            
            print(f"Real database counts - Users: {total_users}, Subjects: {total_subjects}, Mock Tests: {total_mock_tests}, Questions: {total_questions}")
            print(f"User management stats - Admins: {total_admins}, Active: {active_users_all}, Inactive: {inactive_users}, New today: {new_users_today}")
        except Exception as e:
            print(f"Error getting basic counts: {e}")
            # Use zero values when there's no data or errors
            total_users = 0
            active_users = 0
            total_subjects = 0
            total_chapters = 0
            total_questions = 0
            total_mock_tests = 0
            total_mock_attempts = 0
            recent_mock_attempts = 0
            total_practice_attempts = 0
            recent_practice_attempts = 0
            total_admins = 0
            active_users_all = 0
            inactive_users = 0
            new_users_today = 0
        
        # Performance calculations with error handling
        average_mock_score = 0
        average_practice_score = 0
        mock_pass_rate = 0
        practice_pass_rate = 0
        
        try:
            # Mock test performance
            completed_mock_attempts = UGCNetMockAttempt.query.filter(
                UGCNetMockAttempt.is_completed == True,
                UGCNetMockAttempt.completed_at >= start_date
            ).all()
            
            if completed_mock_attempts:
                scores = [attempt.percentage for attempt in completed_mock_attempts if attempt.percentage is not None]
                if scores:
                    average_mock_score = round(sum(scores) / len(scores), 1)
                    mock_pass_rate = round((len([s for s in scores if s >= 40]) / len(scores)) * 100, 1)  # UGC NET pass rate
            
            # Practice test performance
            completed_practice_attempts = UGCNetPracticeAttempt.query.filter(
                UGCNetPracticeAttempt.is_completed == True,
                UGCNetPracticeAttempt.completed_at >= start_date
            ).all()
            
            if completed_practice_attempts:
                scores = [attempt.percentage for attempt in completed_practice_attempts if attempt.percentage is not None]
                if scores:
                    average_practice_score = round(sum(scores) / len(scores), 1)
                    practice_pass_rate = round((len([s for s in scores if s >= 60]) / len(scores)) * 100, 1)  # Practice pass rate
        except Exception as e:
            print(f"Error calculating performance: {e}")
        
        # Subject statistics with error handling
        subject_stats = []
        try:
            subjects = Subject.query.filter_by(is_active=True).all()
            
            for subject in subjects:
                try:
                    # Get attempts for this subject via mock tests
                    subject_mock_attempts = db.session.query(UGCNetMockAttempt).join(UGCNetMockTest).filter(
                        UGCNetMockTest.subject_id == subject.id,
                        UGCNetMockAttempt.is_completed == True,
                        UGCNetMockAttempt.completed_at >= start_date
                    ).all()
                    
                    # Get practice attempts for this subject
                    subject_practice_attempts = UGCNetPracticeAttempt.query.filter(
                        UGCNetPracticeAttempt.subject_id == subject.id,
                        UGCNetPracticeAttempt.is_completed == True,
                        UGCNetPracticeAttempt.completed_at >= start_date
                    ).all()
                    
                    total_subject_attempts = len(subject_mock_attempts) + len(subject_practice_attempts)
                    
                    if total_subject_attempts > 0:
                        all_scores = []
                        all_scores.extend([attempt.percentage for attempt in subject_mock_attempts if attempt.percentage is not None])
                        all_scores.extend([attempt.percentage for attempt in subject_practice_attempts if attempt.percentage is not None])
                        
                        if all_scores:
                            avg_score = round(sum(all_scores) / len(all_scores), 1)
                            subject_stats.append({
                                'subject': subject.name,
                                'attempts': total_subject_attempts,
                                'average_percentage': avg_score
                            })
                except Exception as e:
                    print(f"Error processing subject {subject.name}: {e}")
                    continue
        except Exception as e:
            print(f"Error getting subject stats: {e}")
        
        # Recent top performers with error handling
        top_performers = []
        try:
            # Get recent high-scoring mock attempts
            recent_mock_attempts = UGCNetMockAttempt.query.filter(
                UGCNetMockAttempt.is_completed == True,
                UGCNetMockAttempt.percentage >= 80
            ).order_by(desc(UGCNetMockAttempt.completed_at)).limit(5).all()
            
            # Get recent high-scoring practice attempts
            recent_practice_attempts = UGCNetPracticeAttempt.query.filter(
                UGCNetPracticeAttempt.is_completed == True,
                UGCNetPracticeAttempt.percentage >= 80
            ).order_by(desc(UGCNetPracticeAttempt.completed_at)).limit(5).all()
            
            # Combine and sort
            all_attempts = []
            for attempt in recent_mock_attempts:
                all_attempts.append({
                    'type': 'mock',
                    'attempt': attempt,
                    'completed_at': attempt.completed_at
                })
            
            for attempt in recent_practice_attempts:
                all_attempts.append({
                    'type': 'practice',
                    'attempt': attempt,
                    'completed_at': attempt.completed_at
                })
            
            # Sort by completion time and take top 10
            all_attempts.sort(key=lambda x: x['completed_at'], reverse=True)
            
            for item in all_attempts[:10]:
                try:
                    attempt = item['attempt']
                    test_title = ""
                    if item['type'] == 'mock' and attempt.mock_test:
                        test_title = attempt.mock_test.title
                    elif item['type'] == 'practice':
                        test_title = attempt.title
                    
                    top_performers.append({
                        'id': attempt.id,
                        'user_name': attempt.user.full_name if attempt.user else 'Unknown',
                        'test_title': test_title,
                        'test_type': item['type'],
                        'percentage': attempt.percentage,
                        'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None
                    })
                except Exception as e:
                    print(f"Error processing top performer: {e}")
                    continue
        except Exception as e:
            print(f"Error getting top performers: {e}")
        
        # Calculate retention rate with error handling
        retention_rate = 0
        try:
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            # Users who have made attempts in the last 30 days
            active_users_30_days = db.session.query(User).join(
                db.or_(
                    User.id == UGCNetMockAttempt.user_id,
                    User.id == UGCNetPracticeAttempt.user_id
                )
            ).filter(
                db.or_(
                    UGCNetMockAttempt.started_at >= thirty_days_ago,
                    UGCNetPracticeAttempt.started_at >= thirty_days_ago
                ),
                User.is_admin == False
            ).distinct().count()
            
            if total_users > 0:
                retention_rate = round((active_users_30_days / total_users) * 100, 1)
        except Exception as e:
            print(f"Error calculating retention rate: {e}")
        
        # Calculate daily trends for the last 7 days
        daily_trends = []
        try:
            for i in range(6, -1, -1):  # Last 7 days
                date = datetime.utcnow().date() - timedelta(days=i)
                next_date = date + timedelta(days=1)
                
                # Count mock attempts for this day
                day_mock_attempts = UGCNetMockAttempt.query.filter(
                    UGCNetMockAttempt.completed_at >= date,
                    UGCNetMockAttempt.completed_at < next_date,
                    UGCNetMockAttempt.is_completed == True
                ).count()
                
                # Count practice attempts for this day
                day_practice_attempts = UGCNetPracticeAttempt.query.filter(
                    UGCNetPracticeAttempt.completed_at >= date,
                    UGCNetPracticeAttempt.completed_at < next_date,
                    UGCNetPracticeAttempt.is_completed == True
                ).count()
                
                total_day_attempts = day_mock_attempts + day_practice_attempts
                
                # Calculate average score for this day
                day_mock_scores = [attempt.percentage for attempt in UGCNetMockAttempt.query.filter(
                    UGCNetMockAttempt.completed_at >= date,
                    UGCNetMockAttempt.completed_at < next_date,
                    UGCNetMockAttempt.is_completed == True,
                    UGCNetMockAttempt.percentage != None
                ).all()]
                
                day_practice_scores = [attempt.percentage for attempt in UGCNetPracticeAttempt.query.filter(
                    UGCNetPracticeAttempt.completed_at >= date,
                    UGCNetPracticeAttempt.completed_at < next_date,
                    UGCNetPracticeAttempt.is_completed == True,
                    UGCNetPracticeAttempt.percentage != None
                ).all()]
                
                all_day_scores = day_mock_scores + day_practice_scores
                day_avg_score = round(sum(all_day_scores) / len(all_day_scores), 1) if all_day_scores else 0
                
                daily_trends.append({
                    'date': date.strftime('%b %d'),
                    'attempts': total_day_attempts,
                    'average_score': day_avg_score
                })
        except Exception as e:
            print(f"Error calculating daily trends: {e}")
            # Provide fallback data
            for i in range(6, -1, -1):
                date = datetime.utcnow().date() - timedelta(days=i)
                daily_trends.append({
                    'date': date.strftime('%b %d'),
                    'attempts': 0,
                    'average_score': 0
                })
        
        # Combine total attempts for legacy compatibility
        total_attempts = total_mock_attempts + total_practice_attempts
        recent_attempts_count = recent_mock_attempts + recent_practice_attempts
        combined_average_score = round((average_mock_score + average_practice_score) / 2, 1) if average_mock_score > 0 or average_practice_score > 0 else 0
        
        stats = {
            'total_users': total_users,
            'total_subjects': total_subjects,
            'total_mock_tests': total_mock_tests,
            'total_questions': total_questions,
            'total_attempts': total_attempts,
            'active_users': active_users,
            'recent_attempts': recent_attempts_count,
            'today_attempts': recent_attempts_count,  # Add for compatibility
            'week_attempts': recent_attempts_count,   # Add for compatibility
            'average_score': combined_average_score,
            'pass_rate': round((mock_pass_rate + practice_pass_rate) / 2, 1) if mock_pass_rate > 0 or practice_pass_rate > 0 else 0,
            'average_time_minutes': 0,  # Would need to calculate from attempt times
            'retention_rate': retention_rate,
            # User management specific stats
            'total_admins': total_admins,
            'active_users_all': active_users_all,
            'inactive_users': inactive_users,
            'new_users_today': new_users_today,
            'subjects': subject_stats,
            'top_performers': top_performers,
            'daily_trends': daily_trends,
            # UGC NET specific stats
            'ugc_net_stats': {
                'total_mock_tests': total_mock_tests,
                'total_mock_attempts': total_mock_attempts,
                'total_practice_attempts': total_practice_attempts,
                'average_mock_score': average_mock_score,
                'average_practice_score': average_practice_score,
                'mock_pass_rate': mock_pass_rate,
                'practice_pass_rate': practice_pass_rate
            },
            # Keep nested structure for advanced components
            'stats': {
                'total_users': total_users,
                'total_subjects': total_subjects,
                'total_mock_tests': total_mock_tests,
                'total_questions': total_questions,
                'total_attempts': total_attempts,
                'active_users': active_users,
                'recent_attempts': recent_attempts_count
            },
            'performance': {
                'average_percentage': combined_average_score,
                'pass_rate': round((mock_pass_rate + practice_pass_rate) / 2, 1) if mock_pass_rate > 0 or practice_pass_rate > 0 else 0,
                'average_time_minutes': 0,
                'retention_rate': retention_rate
            },
            'engagement': {
                'total_registered': total_users,
                'active_users': active_users
            },
            # User management nested structure
            'user_management': {
                'total_users': total_users,
                'total_admins': total_admins,
                'active_users': active_users_all,
                'inactive_users': inactive_users,
                'new_users_today': new_users_today
            }
        }
        
        print(f"Generated stats: {stats}")
        print(f"Returning response with total_users: {stats['total_users']}, total_mock_tests: {stats['total_mock_tests']}")
        
        # Cache for 5 minutes with error handling
        try:
            if redis_client:
                redis_client.setex(cache_key, 300, json.dumps(stats, default=str))
        except Exception as redis_error:
            print(f"Redis cache set error: {redis_error}")
            # Continue without caching
        
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"Dashboard stats error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Subject Management
@admin_bp.route('/subjects', methods=['GET'])
@admin_required
def get_subjects():
    try:
        subjects = Subject.query.all()
        return jsonify([subject.to_dict() for subject in subjects]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subjects', methods=['POST'])
@admin_required
def create_subject():
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Subject name required'}), 400
        
        # Check if subject already exists
        if Subject.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Subject already exists'}), 400
        
        subject = Subject(
            name=data['name'],
            description=data.get('description', ''),
            subject_code=data.get('subject_code', ''),
            paper_type=data.get('paper_type', 'paper2'),
            total_marks_paper1=data.get('total_marks_paper1', 100),
            total_marks_paper2=data.get('total_marks_paper2', 100),
            exam_duration_paper1=data.get('exam_duration_paper1', 60),
            exam_duration_paper2=data.get('exam_duration_paper2', 120)
        )
        
        db.session.add(subject)
        db.session.commit()
        
        # Clear cache with error handling
        try:
            if redis_client:
                redis_client.delete('admin_dashboard_stats')
        except Exception as redis_error:
            print(f"Redis cache delete error: {redis_error}")
        
        return jsonify({
            'message': 'Subject created successfully',
            'subject': subject.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@admin_required
def update_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        data = request.get_json()
        
        if 'name' in data:
            # Check if name already exists (excluding current subject)
            existing = Subject.query.filter(Subject.name == data['name'], Subject.id != subject_id).first()
            if existing:
                return jsonify({'error': 'Subject name already exists'}), 400
            subject.name = data['name']
        
        if 'description' in data:
            subject.description = data['description']
        
        if 'is_active' in data:
            subject.is_active = data['is_active']
            
        # UGC NET specific fields
        if 'subject_code' in data:
            subject.subject_code = data['subject_code']
        if 'paper_type' in data:
            subject.paper_type = data['paper_type']
        if 'total_marks_paper1' in data:
            subject.total_marks_paper1 = data['total_marks_paper1']
        if 'total_marks_paper2' in data:
            subject.total_marks_paper2 = data['total_marks_paper2']
        if 'exam_duration_paper1' in data:
            subject.exam_duration_paper1 = data['exam_duration_paper1']
        if 'exam_duration_paper2' in data:
            subject.exam_duration_paper2 = data['exam_duration_paper2']
        
        db.session.commit()
        
        # Clear cache with error handling
        try:
            if redis_client:
                redis_client.delete('admin_dashboard_stats')
        except Exception as redis_error:
            print(f"Redis cache delete error: {redis_error}")
        
        return jsonify({
            'message': 'Subject updated successfully',
            'subject': subject.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@admin_required
def delete_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        # Check if subject has chapters
        if subject.chapters:
            return jsonify({'error': 'Cannot delete subject with existing chapters'}), 400
        
        db.session.delete(subject)
        db.session.commit()
        
        # Clear cache with error handling
        try:
            if redis_client:
                redis_client.delete('admin_dashboard_stats')
        except Exception as redis_error:
            print(f"Redis cache delete error: {redis_error}")
        
        return jsonify({'message': 'Subject deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Chapter Management
@admin_bp.route('/chapters', methods=['GET'])
@admin_required
def get_chapters():
    try:
        subject_id = request.args.get('subject_id', type=int)
        
        if subject_id:
            chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        else:
            chapters = Chapter.query.all()
        
        return jsonify([chapter.to_dict() for chapter in chapters]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/chapters', methods=['POST'])
@admin_required
def create_chapter():
    try:
        data = request.get_json()
        
        required_fields = ['name', 'subject_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify subject exists
        subject = Subject.query.get(data['subject_id'])
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        chapter = Chapter(
            name=data['name'],
            description=data.get('description', ''),
            subject_id=data['subject_id'],
            weightage_paper1=data.get('weightage_paper1', 0),
            weightage_paper2=data.get('weightage_paper2', 0),
            estimated_questions_paper1=data.get('estimated_questions_paper1', 0),
            estimated_questions_paper2=data.get('estimated_questions_paper2', 0),
            chapter_order=data.get('chapter_order', 0)
        )
        
        db.session.add(chapter)
        db.session.commit()
        
        return jsonify({
            'message': 'Chapter created successfully',
            'chapter': chapter.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Mock Test Management
@admin_bp.route('/mock-tests', methods=['GET'])
@admin_required
def get_mock_tests():
    """Get mock tests (updated for question bank compatibility)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        subject_id = request.args.get('subject_id', type=int)
        
        query = UGCNetMockTest.query
        
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        
        # Get paginated results
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        tests_data = []
        for test in pagination.items:
            test_dict = test.to_dict()
            # Add related data for better filtering
            if test.subject:
                test_dict['subject_name'] = test.subject.name
            tests_data.append(test_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'mock_tests': tests_data,
                'total_pages': pagination.pages,
                'current_page': page,
                'total_items': pagination.total,
                'per_page': per_page
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/mock-tests', methods=['POST'])
@admin_required
def create_mock_test():
    """Create mock test"""
    try:
        data = request.get_json()
        
        required_fields = ['title', 'subject_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify subject exists
        subject = Subject.query.get(data['subject_id'])
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Get current user for created_by
        current_user = get_current_user()
        
        mock_test = UGCNetMockTest(
            title=data['title'],
            description=data.get('description', ''),
            subject_id=data['subject_id'],
            paper_type=data.get('paper_type', 'paper2'),
            total_questions=data.get('total_questions', 100),
            total_marks=data.get('total_marks', 200),
            time_limit=data.get('time_limit', 180),
            previous_year_percentage=data.get('previous_year_percentage', 70.0),
            ai_generated_percentage=data.get('ai_generated_percentage', 30.0),
            easy_percentage=data.get('easy_percentage', 30.0),
            medium_percentage=data.get('medium_percentage', 50.0),
            hard_percentage=data.get('hard_percentage', 20.0),
            created_by=current_user.id
        )
        
        db.session.add(mock_test)
        db.session.commit()
        
        return jsonify({
            'message': 'Mock test created successfully',
            'test': mock_test.to_dict(),  # Updated compatibility
            'mock_test': mock_test.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Mock Test Status Management
@admin_bp.route('/mock-tests/<int:test_id>/toggle-status', methods=['PUT'])
@admin_required
def toggle_mock_test_status(test_id):
    """Toggle mock test active status (admin only)"""
    try:
        mock_test = UGCNetMockTest.query.get(test_id)
        if not mock_test:
            return jsonify({'error': 'Mock test not found'}), 404
        
        # Toggle the active status
        mock_test.is_active = not mock_test.is_active
        db.session.commit()
        
        status = 'activated' if mock_test.is_active else 'deactivated'
        
        return jsonify({
            'message': f'Mock test {status} successfully',
            'test': mock_test.to_dict(),  # Updated compatibility
            'mock_test': mock_test.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/mock-tests/<int:test_id>/status', methods=['PUT'])
@admin_required
def update_mock_test_status(test_id):
    """Update mock test status (admin only)"""
    try:
        mock_test = UGCNetMockTest.query.get(test_id)
        if not mock_test:
            return jsonify({'error': 'Mock test not found'}), 404
        
        data = request.get_json()
        if 'is_active' not in data:
            return jsonify({'error': 'is_active field required'}), 400
        
        mock_test.is_active = data['is_active']
        db.session.commit()
        
        status = 'activated' if mock_test.is_active else 'deactivated'
        
        return jsonify({
            'message': f'Mock test {status} successfully',
            'test': mock_test.to_dict(),  # Updated compatibility
            'mock_test': mock_test.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Management
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '', type=str)
        filter_type = request.args.get('filter', 'all', type=str)
        role_filter = request.args.get('role', '', type=str)
        status_filter = request.args.get('status', '', type=str)
        
        # Build the query - start with base query
        if role_filter == 'admin':
            query = User.query.filter_by(is_admin=True)
        elif role_filter == 'user':
            query = User.query.filter_by(is_admin=False)
        elif filter_type == 'admin':
            # Legacy support for single filter parameter
            query = User.query.filter_by(is_admin=True)
        elif filter_type == 'user':
            # Legacy support for single filter parameter
            query = User.query.filter_by(is_admin=False)
        else:
            # Default: exclude admin users unless specifically requested
            query = User.query.filter_by(is_admin=False)
        
        # Apply status filter
        if status_filter == 'active':
            query = query.filter_by(is_active=True)
        elif status_filter == 'inactive':
            query = query.filter_by(is_active=False)
        elif filter_type == 'active':
            # Legacy support for single filter parameter
            query = query.filter_by(is_active=True)
        elif filter_type == 'inactive':
            # Legacy support for single filter parameter
            query = query.filter_by(is_active=False)
        
        # Apply search filter
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term)
                )
            )
        
        # Order by created_at descending
        query = query.order_by(desc(User.created_at))
        
        # Paginate
        users = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users_data = []
        for user in users.items:
            user_data = user.to_dict()
            # Add activity stats using new models
            user_data['mock_attempts'] = UGCNetMockAttempt.query.filter_by(user_id=user.id).count()
            user_data['practice_attempts'] = UGCNetPracticeAttempt.query.filter_by(user_id=user.id).count()
            users_data.append(user_data)
        
        return jsonify({
            'users': users_data,
            'total': users.total,
            'pages': users.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        print(f"Error in get_users: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Update user fields
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'email' in data:
            # Check if email is already taken
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'error': 'Email already in use'}), 400
            user.email = data['email']
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        # Additional profile fields
        profile_fields = ['phone', 'bio', 'gender', 'country', 'timezone', 
                         'notification_email', 'notification_quiz_reminders', 
                         'theme_preference', 'email_verified']
        
        for field in profile_fields:
            if field in data:
                setattr(user, field, data[field])
        
        if 'date_of_birth' in data and data['date_of_birth']:
            try:
                user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/create', methods=['POST'])
@admin_required
def create_user():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already in use'}), 400
        
        # Create new user
        user = User(
            full_name=data['full_name'],
            email=data['email'],
            is_admin=data.get('is_admin', False),
            is_active=data.get('is_active', True),
            email_verified=True,  # Admin-created users are verified by default
            phone=data.get('phone'),
            bio=data.get('bio'),
            gender=data.get('gender'),
            country=data.get('country'),
            timezone=data.get('timezone', 'UTC')
        )
        user.set_password(data['password'])
        
        if data.get('date_of_birth'):
            try:
                user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent deletion of admin users
        if user.is_admin:
            return jsonify({'error': 'Cannot delete admin users'}), 400
        
        # Delete the user (cascades will handle related data)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Admin Profile Management
@admin_bp.route('/profile', methods=['GET'])
@admin_required
def get_admin_profile():
    """Get current admin's profile"""
    try:
        user = get_current_user()
        return jsonify({'admin': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/profile', methods=['PUT'])
@admin_required
def update_admin_profile():
    """Update current admin's profile"""
    try:
        user = get_current_user()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate email uniqueness if changed
        if 'email' in data and data['email'] != user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'error': 'Email already exists'}), 400
        
        # Update allowed fields (admins can update more fields)
        updatable_fields = [
            'email', 'full_name', 'phone', 'bio', 'date_of_birth', 
            'gender', 'country', 'timezone', 'notification_email',
            'notification_quiz_reminders', 'theme_preference'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'date_of_birth' and data[field]:
                    try:
                        user.date_of_birth = datetime.strptime(data[field], '%Y-%m-%d').date()
                    except ValueError:
                        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
                else:
                    setattr(user, field, data[field])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Admin profile updated successfully',
            'admin': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/profile/password', methods=['PUT'])
@admin_required
def change_admin_password():
    """Change admin's password"""
    try:
        user = get_current_user()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
            
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
            
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
            
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Enhanced User Management for Admins
@admin_bp.route('/users/<int:user_id>/profile', methods=['PUT'])
@admin_required
def update_user_profile_by_admin(user_id):
    """Update any user's profile (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate email uniqueness if changed
        if 'email' in data and data['email'] != user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'error': 'Email already exists'}), 400
        
        # Admin can update all fields including admin status
        updatable_fields = [
            'email', 'full_name', 'phone', 'bio', 'date_of_birth', 
            'gender', 'country', 'timezone', 'is_admin', 'is_active',
            'notification_email', 'notification_quiz_reminders', 'theme_preference',
            'email_verified'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'date_of_birth' and data[field]:
                    try:
                        user.date_of_birth = datetime.strptime(data[field], '%Y-%m-%d').date()
                    except ValueError:
                        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
                else:
                    setattr(user, field, data[field])
        
        # Update password if provided
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'error': 'Password must be at least 6 characters long'}), 400
            user.set_password(data['password'])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'User profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Export Data
@admin_bp.route('/export', methods=['POST'])
@admin_required
def export_data():
    try:
        data = request.get_json()
        export_type = data.get('type', 'all')  # 'users', 'mock_tests', 'attempts', 'all'
        
        # Import task dynamically to avoid circular imports
        try:
            from app.tasks.export_tasks import export_admin_data
            # Run export task synchronously for now
            result = export_admin_data(export_type)
        except ImportError:
            # Fallback if export tasks don't exist
            result = {
                'status': 'success',
                'message': 'Export functionality not implemented yet',
                'files_created': []
            }
        
        if result['status'] == 'success':
            return jsonify({
                'message': result['message'],
                'files_created': result.get('files_created', [])
            }), 200
        else:
            return jsonify({
                'message': 'Export failed',
                'error': result.get('error', 'Unknown error')
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/export/<task_id>', methods=['GET'])
@admin_required
def get_export_status(task_id):
    try:
        try:
            from app import celery_app
            task = celery_app.AsyncResult(task_id)
            
            if task.state == 'PENDING':
                response = {'state': task.state, 'status': 'Task is waiting...'}
            elif task.state == 'PROGRESS':
                response = {
                    'state': task.state,
                    'status': task.info.get('status', ''),
                    'current': task.info.get('current', 0),
                    'total': task.info.get('total', 1)
                }
            elif task.state == 'SUCCESS':
                response = {
                    'state': task.state,
                    'download_url': task.result
                }
            else:  # FAILURE
                response = {
                    'state': task.state,
                    'error': str(task.info)
                }
        except ImportError:
            # Fallback if celery is not available
            response = {
                'state': 'SUCCESS',
                'message': 'Export tasks not implemented'
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# System Settings Management
@admin_bp.route('/settings', methods=['GET'])
@admin_required
def get_system_settings():
    """Get system settings"""
    try:
        # This could be extended to include actual system settings from a settings table
        settings = {
            'app_name': 'PrepCheck UGC NET',
            'version': '2.0.0',
            'max_file_size': '5MB',
            'allowed_extensions': ['png', 'jpg', 'jpeg', 'gif', 'webp'],
            'maintenance_mode': False,
            'registration_enabled': True,
            'email_verification_required': False,
            'max_mock_test_time': 180,  # minutes
            'max_practice_test_time': 30,  # minutes
            'default_questions_per_test': 20,
            'password_min_length': 6,
            'ugc_net_pass_percentage': 40.0,
            'practice_pass_percentage': 60.0
        }
        
        return jsonify({'settings': settings}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/download/<filename>', methods=['GET'])
@admin_required
def download_export_file(filename):
    """Download exported files"""
    try:
        from app.utils.file_utils import safe_send_file, get_export_directory
        export_dir = get_export_directory()
        return safe_send_file(export_dir, filename)
    except ImportError:
        return jsonify({'error': 'File utilities not available'}), 500

# User Analytics for Admin
@admin_bp.route('/user/<int:user_id>/analytics', methods=['GET'])
@admin_required
def get_user_analytics(user_id):
    """Get analytics for any user (admin only) - Updated for UGC NET models"""
    try:
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get query parameters
        days = request.args.get('days', 30, type=int)
        subject_id = request.args.get('subject_id', type=int)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Build base query for mock attempts
        mock_attempts_query = UGCNetMockAttempt.query.filter(
            UGCNetMockAttempt.user_id == user_id,
            UGCNetMockAttempt.is_completed == True,
            UGCNetMockAttempt.completed_at >= start_date,
            UGCNetMockAttempt.completed_at <= end_date
        )
        
        # Build base query for practice attempts
        practice_attempts_query = UGCNetPracticeAttempt.query.filter(
            UGCNetPracticeAttempt.user_id == user_id,
            UGCNetPracticeAttempt.is_completed == True,
            UGCNetPracticeAttempt.completed_at >= start_date,
            UGCNetPracticeAttempt.completed_at <= end_date
        )
        
        # Add subject filter if provided
        if subject_id:
            mock_attempts_query = mock_attempts_query.join(UGCNetMockTest).filter(UGCNetMockTest.subject_id == subject_id)
            practice_attempts_query = practice_attempts_query.filter(UGCNetPracticeAttempt.subject_id == subject_id)
        
        mock_attempts = mock_attempts_query.order_by(UGCNetMockAttempt.completed_at.desc()).all()
        practice_attempts = practice_attempts_query.order_by(UGCNetPracticeAttempt.completed_at.desc()).all()
        
        # Calculate basic stats
        total_mock_attempts = len(mock_attempts)
        total_practice_attempts = len(practice_attempts)
        total_attempts = total_mock_attempts + total_practice_attempts
        
        # Calculate averages
        mock_scores = [attempt.percentage for attempt in mock_attempts if attempt.percentage is not None]
        practice_scores = [attempt.percentage for attempt in practice_attempts if attempt.percentage is not None]
        
        average_mock_score = sum(mock_scores) / len(mock_scores) if mock_scores else 0
        average_practice_score = sum(practice_scores) / len(practice_scores) if practice_scores else 0
        average_overall_score = (average_mock_score + average_practice_score) / 2 if (mock_scores or practice_scores) else 0
        
        # Calculate trends (compare to previous period)
        prev_start = start_date - timedelta(days=days)
        prev_mock_attempts = UGCNetMockAttempt.query.filter(
            UGCNetMockAttempt.user_id == user_id,
            UGCNetMockAttempt.is_completed == True,
            UGCNetMockAttempt.completed_at >= prev_start,
            UGCNetMockAttempt.completed_at < start_date
        ).all()
        
        prev_practice_attempts = UGCNetPracticeAttempt.query.filter(
            UGCNetPracticeAttempt.user_id == user_id,
            UGCNetPracticeAttempt.is_completed == True,
            UGCNetPracticeAttempt.completed_at >= prev_start,
            UGCNetPracticeAttempt.completed_at < start_date
        ).all()
        
        prev_mock_scores = [attempt.percentage for attempt in prev_mock_attempts if attempt.percentage is not None]
        prev_practice_scores = [attempt.percentage for attempt in prev_practice_attempts if attempt.percentage is not None]
        prev_average_score = (sum(prev_mock_scores + prev_practice_scores) / len(prev_mock_scores + prev_practice_scores)) if (prev_mock_scores or prev_practice_scores) else 0
        
        score_trend = average_overall_score - prev_average_score
        
        # Get recent performance by day
        daily_performance = {}
        all_attempts = []
        
        # Combine all attempts with type info
        for attempt in mock_attempts:
            all_attempts.append({
                'type': 'mock',
                'attempt': attempt,
                'date': attempt.completed_at,
                'percentage': attempt.percentage
            })
        
        for attempt in practice_attempts:
            all_attempts.append({
                'type': 'practice',
                'attempt': attempt,
                'date': attempt.completed_at,
                'percentage': attempt.percentage
            })
        
        for item in all_attempts:
            day_key = item['date'].strftime('%Y-%m-%d')
            if day_key not in daily_performance:
                daily_performance[day_key] = {'attempts': 0, 'scores': []}
            daily_performance[day_key]['attempts'] += 1
            if item['percentage'] is not None:
                daily_performance[day_key]['scores'].append(item['percentage'])
        
        # Convert to list and calculate percentages
        performance_data = []
        for day, data in sorted(daily_performance.items()):
            percentage = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
            performance_data.append({
                'date': day,
                'attempts': data['attempts'],
                'percentage': round(percentage, 2)
            })
        
        # Get subject breakdown
        subject_performance = {}
        
        # Process mock attempts
        for attempt in mock_attempts:
            if attempt.mock_test and attempt.mock_test.subject:
                subject_name = attempt.mock_test.subject.name
                
                if subject_name not in subject_performance:
                    subject_performance[subject_name] = {
                        'mock_attempts': 0, 
                        'practice_attempts': 0,
                        'mock_scores': [],
                        'practice_scores': []
                    }
                
                subject_performance[subject_name]['mock_attempts'] += 1
                if attempt.percentage is not None:
                    subject_performance[subject_name]['mock_scores'].append(attempt.percentage)
        
        # Process practice attempts
        for attempt in practice_attempts:
            if attempt.subject:
                subject_name = attempt.subject.name
                
                if subject_name not in subject_performance:
                    subject_performance[subject_name] = {
                        'mock_attempts': 0, 
                        'practice_attempts': 0,
                        'mock_scores': [],
                        'practice_scores': []
                    }
                
                subject_performance[subject_name]['practice_attempts'] += 1
                if attempt.percentage is not None:
                    subject_performance[subject_name]['practice_scores'].append(attempt.percentage)
        
        # Convert to list with percentages
        subjects_data = []
        for subject_name, data in subject_performance.items():
            all_subject_scores = data['mock_scores'] + data['practice_scores']
            total_subject_attempts = data['mock_attempts'] + data['practice_attempts']
            percentage = sum(all_subject_scores) / len(all_subject_scores) if all_subject_scores else 0
            
            subjects_data.append({
                'name': subject_name,
                'attempts': total_subject_attempts,
                'mock_attempts': data['mock_attempts'],
                'practice_attempts': data['practice_attempts'],
                'percentage': round(percentage, 2)
            })
        
        return jsonify({
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email
            },
            'summary': {
                'total_attempts': total_attempts,
                'total_mock_attempts': total_mock_attempts,
                'total_practice_attempts': total_practice_attempts,
                'average_score': round(average_overall_score, 2),
                'average_mock_score': round(average_mock_score, 2),
                'average_practice_score': round(average_practice_score, 2),
                'score_trend': round(score_trend, 2),
                'period_days': days
            },
            'daily_performance': performance_data,
            'subject_performance': subjects_data,
            'filters': {
                'subject_id': subject_id,
                'days': days
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
