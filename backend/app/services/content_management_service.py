"""
Content Management Service
Handles subjects, chapters, and mock tests management
"""
from app import db, redis_client
from app.models import Subject, Chapter, UGCNetMockTest


class ContentManagementService:
    """Service for content management operations"""
    
    def __init__(self):
        pass
    
    def clear_cache(self):
        """Clear relevant caches"""
        try:
            if redis_client:
                redis_client.delete('admin_dashboard_stats')
        except Exception as redis_error:
            print(f"Redis cache delete error: {redis_error}")
    
    # Subject Management
    def get_all_subjects(self):
        """Get all subjects"""
        try:
            subjects = Subject.query.all()
            return [subject.to_dict() for subject in subjects]
        except Exception as e:
            raise Exception(f"Error fetching subjects: {str(e)}")
    
    def create_subject(self, data):
        """Create a new subject"""
        try:
            if not data or 'name' not in data:
                raise ValueError('Subject name required')
            
            # Check if subject already exists
            if Subject.query.filter_by(name=data['name']).first():
                raise ValueError('Subject already exists')
            
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
            self.clear_cache()
            
            return subject.to_dict()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error creating subject: {str(e)}")
    
    def update_subject(self, subject_id, data):
        """Update an existing subject"""
        try:
            subject = Subject.query.get(subject_id)
            if not subject:
                raise ValueError('Subject not found')
            
            if 'name' in data:
                # Check if name already exists (excluding current subject)
                existing = Subject.query.filter(Subject.name == data['name'], Subject.id != subject_id).first()
                if existing:
                    raise ValueError('Subject name already exists')
                subject.name = data['name']
            
            # Update other fields
            updatable_fields = [
                'description', 'is_active', 'subject_code', 'paper_type',
                'total_marks_paper1', 'total_marks_paper2', 
                'exam_duration_paper1', 'exam_duration_paper2'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(subject, field, data[field])
            
            db.session.commit()
            self.clear_cache()
            
            return subject.to_dict()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error updating subject: {str(e)}")
    
    def delete_subject(self, subject_id):
        """Delete a subject"""
        try:
            subject = Subject.query.get(subject_id)
            if not subject:
                raise ValueError('Subject not found')
            
            # Check if subject has chapters
            if subject.chapters:
                raise ValueError('Cannot delete subject with existing chapters')
            
            db.session.delete(subject)
            db.session.commit()
            self.clear_cache()
            
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error deleting subject: {str(e)}")
    
    # Chapter Management
    def get_chapters(self, subject_id=None):
        """Get chapters, optionally filtered by subject"""
        try:
            if subject_id:
                chapters = Chapter.query.filter_by(subject_id=subject_id).all()
            else:
                chapters = Chapter.query.all()
            
            return [chapter.to_dict() for chapter in chapters]
        except Exception as e:
            raise Exception(f"Error fetching chapters: {str(e)}")
    
    def create_chapter(self, data):
        """Create a new chapter"""
        try:
            required_fields = ['name', 'subject_id']
            if not all(field in data for field in required_fields):
                raise ValueError('Missing required fields')
            
            # Verify subject exists
            subject = Subject.query.get(data['subject_id'])
            if not subject:
                raise ValueError('Subject not found')
            
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
            
            return chapter.to_dict()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error creating chapter: {str(e)}")
    
    # Mock Test Management
    def get_mock_tests(self, page=1, per_page=10, subject_id=None):
        """Get mock tests with pagination"""
        try:
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
            
            return {
                'mock_tests': tests_data,
                'total_pages': pagination.pages,
                'current_page': page,
                'total_items': pagination.total,
                'per_page': per_page
            }
        except Exception as e:
            raise Exception(f"Error fetching mock tests: {str(e)}")
    
    def create_mock_test(self, data, created_by_user_id):
        """Create a new mock test"""
        try:
            required_fields = ['title', 'subject_id']
            if not all(field in data for field in required_fields):
                raise ValueError('Missing required fields')
            
            # Verify subject exists
            subject = Subject.query.get(data['subject_id'])
            if not subject:
                raise ValueError('Subject not found')
            
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
                created_by=created_by_user_id
            )
            
            db.session.add(mock_test)
            db.session.commit()
            
            return mock_test.to_dict()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error creating mock test: {str(e)}")
    
    def update_mock_test_status(self, test_id, is_active=None):
        """Update mock test status"""
        try:
            mock_test = UGCNetMockTest.query.get(test_id)
            if not mock_test:
                raise ValueError('Mock test not found')
            
            if is_active is not None:
                mock_test.is_active = is_active
            else:
                # Toggle the active status
                mock_test.is_active = not mock_test.is_active
            
            db.session.commit()
            
            return mock_test.to_dict()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error updating mock test status: {str(e)}")
