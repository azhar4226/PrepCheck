from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.utils.timezone_utils import current_ist_timestamp, get_ist_isoformat
import json
from typing import Dict, Optional

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    
    # Profile fields
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    profile_picture_url = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))  # male, female, other
    country = db.Column(db.String(50))
    timezone = db.Column(db.String(50), default='Asia/Kolkata')
    
    # Preferences
    notification_email = db.Column(db.Boolean, default=True)
    notification_quiz_reminders = db.Column(db.Boolean, default=True)
    theme_preference = db.Column(db.String(20), default='light')  # light, dark, auto
    
    # System fields
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(255))
    password_reset_token = db.Column(db.String(255))
    password_reset_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=current_ist_timestamp)
    updated_at = db.Column(db.DateTime, default=current_ist_timestamp, onupdate=current_ist_timestamp)
    last_login = db.Column(db.DateTime)
    
    # User's registered subject for UGC NET preparation
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    registered_subject = db.relationship('Subject', backref='registered_users', lazy=True)
    
    # Relationships - Updated to use UGC NET models only
    ugc_net_mock_attempts = db.relationship('UGCNetMockAttempt', backref='attempt_user', lazy=True, cascade='all, delete-orphan')
    ugc_net_practice_attempts = db.relationship('UGCNetPracticeAttempt', backref='attempt_user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'bio': self.bio,
            'profile_picture_url': self.profile_picture_url,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'country': self.country,
            'timezone': self.timezone,
            'notification_email': self.notification_email,
            'notification_quiz_reminders': self.notification_quiz_reminders,
            'theme_preference': self.theme_preference,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': get_ist_isoformat(self.created_at),
            'updated_at': get_ist_isoformat(self.updated_at),
            'last_login': get_ist_isoformat(self.last_login),
            'subject_id': self.subject_id,
            'registered_subject': self.registered_subject.to_dict() if self.registered_subject else None
        }
        
        if include_sensitive:
            data.update({
                'email_verification_token': self.email_verification_token,
                'password_reset_token': self.password_reset_token,
                'password_reset_expires': self.password_reset_expires.isoformat() if self.password_reset_expires else None
            })
            
        return data

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=current_ist_timestamp)
    
    # UGC NET specific fields
    subject_code = db.Column(db.String(10))  # UGC NET subject code
    paper_type = db.Column(db.String(20), default='paper2')  # 'paper1' or 'paper2'

    # Relationships
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        # Dynamically set total_marks and exam_duration based on paper_type
        total_marks = 200 if self.paper_type == 'paper2' else 100
        exam_duration = 120 if self.paper_type == 'paper2' else 60
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': get_ist_isoformat(self.created_at),
            'chapters_count': Chapter.query.filter_by(subject_id=self.id).count(),
            'subject_code': self.subject_code,
            'paper_type': self.paper_type,
            'total_marks': total_marks,
            'exam_duration': exam_duration
        }

class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=current_ist_timestamp)
    
    # UGC NET specific fields
    weightage = db.Column(db.Integer, default=0)  # Weightage for the chapter (0-100)
    estimated_questions = db.Column(db.Integer, default=0)  # Expected questions in the chapter
    chapter_order = db.Column(db.Integer, default=0)  # Order in syllabus

    # Relationships - Updated to use QuestionBank instead of Quiz
    # Note: backref relationships are defined in child models to avoid conflicts
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'questions_count': QuestionBank.query.filter_by(chapter_id=self.id).count(),
            'weightage': self.weightage,
            'estimated_questions': self.estimated_questions,
            'chapter_order': self.chapter_order
        }

class StudyMaterial(db.Model):
    __tablename__ = 'study_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # For text-based materials
    material_type = db.Column(db.String(20), nullable=False)  # document, video, audio, link, text
    file_path = db.Column(db.String(500))  # For uploaded files
    url = db.Column(db.String(500))  # For external links
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=current_ist_timestamp)
    updated_at = db.Column(db.DateTime, default=current_ist_timestamp, onupdate=current_ist_timestamp)
    
    # Relationships
    chapter = db.relationship('Chapter', backref='materials')
    creator = db.relationship('User', backref='study_materials')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'material_type': self.material_type,
            'file_path': self.file_path,
            'url': self.url,
            'chapter_id': self.chapter_id,
            'created_by': self.created_by,
            'is_active': self.is_active,
            'created_at': get_ist_isoformat(self.created_at),
            'updated_at': get_ist_isoformat(self.updated_at)
        }

class QuestionBank(db.Model):
    """Enhanced question bank for UGC NET preparation"""
    __tablename__ = 'question_bank'
    
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # A, B, C, or D
    explanation = db.Column(db.Text)
    marks = db.Column(db.Integer, default=1)
    
    # UGC NET specific fields
    paper_type = db.Column(db.String(20), default='paper2')  # 'paper1', 'paper2'
    year = db.Column(db.Integer)  # Question year (2019, 2020, etc.)
    session = db.Column(db.String(20))  # 'june', 'december'
    question_type = db.Column(db.String(20), default='practice')  # 'previous_year', 'ai_generated', 'practice'
    
    # Question bank specific fields
    topic = db.Column(db.String(200), nullable=False)  # Topic/subject area
    difficulty = db.Column(db.String(20), nullable=False)  # easy, medium, hard
    weightage = db.Column(db.Integer, default=5)  # Difficulty weightage out of 10
    source = db.Column(db.String(50), default='ai_generated')  # ai_generated, manual, imported, previous_year
    tags = db.Column(db.Text)  # JSON array of tags for categorization
    
    # Performance analytics
    avg_solve_time = db.Column(db.Integer)  # Average time to solve in seconds
    success_rate = db.Column(db.Float, default=0.0)  # Success percentage (0-100)
    attempt_count = db.Column(db.Integer, default=0)  # Total attempts across all users
    
    # Verification fields
    is_verified = db.Column(db.Boolean, default=False)
    verification_method = db.Column(db.String(50))  # gemini, manual, peer_review
    verification_confidence = db.Column(db.Float)
    verification_notes = db.Column(db.Text)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_at = db.Column(db.DateTime)
    
    # Metadata
    usage_count = db.Column(db.Integer, default=0)  # How many times used in quizzes
    last_used = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=current_ist_timestamp)
    updated_at = db.Column(db.DateTime, default=current_ist_timestamp, onupdate=current_ist_timestamp)
    
    # Content hash for deduplication
    content_hash = db.Column(db.String(64), unique=True, nullable=False)
    
    # Relationships
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'))
    chapter = db.relationship('Chapter', backref='questions')
    verifier = db.relationship('User', foreign_keys=[verified_by])
    
    def __repr__(self):
        return f'<QuestionBank {self.id}: {self.topic}>'
    
    def to_dict(self, include_answer=False):
        data = {
            'id': self.id,
            'question_text': self.question_text,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'option_d': self.option_d,
            'marks': self.marks,
            'paper_type': self.paper_type,
            'year': self.year,
            'session': self.session,
            'question_type': self.question_type,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'weightage': self.weightage,
            'source': self.source,
            'tags': json.loads(self.tags) if self.tags else [],
            'avg_solve_time': self.avg_solve_time,
            'success_rate': self.success_rate,
            'attempt_count': self.attempt_count,
            'is_verified': self.is_verified,
            'verification_method': self.verification_method,
            'verification_confidence': self.verification_confidence,
            'verification_notes': self.verification_notes,
            'usage_count': self.usage_count,
            'last_used': get_ist_isoformat(self.last_used),
            'created_at': get_ist_isoformat(self.created_at),
            'updated_at': get_ist_isoformat(self.updated_at),
            'chapter_id': self.chapter_id
        }
        
        if include_answer:
            data['correct_option'] = self.correct_option
            data['explanation'] = self.explanation
            
        return data
    
    def update_performance_stats(self):
        """Update performance statistics based on question attempts"""
        # This would calculate avg_solve_time and success_rate from QuestionPerformance
        # Implementation would depend on your analytics requirements
        pass
    
    def increment_usage(self):
        """Increment usage count and update last used timestamp"""
        self.usage_count = (self.usage_count or 0) + 1
        self.last_used = current_ist_timestamp()
    
    def get_performance_stats(self):
        """Get performance statistics for this question"""
        return {
            'total_attempts': self.attempt_count or 0,
            'success_rate': self.success_rate or 0.0,
            'average_time': self.avg_solve_time or 0,
            'difficulty_rating': self.difficulty,
            'usage_count': self.usage_count or 0,
            'last_used': get_ist_isoformat(self.last_used)
        }
    
    def get_usage_trends(self, days=30):
        """Get usage trends over specified days - simplified version"""
        # Simplified implementation since we don't have detailed QuestionPerformance data
        return []

class UGCNetMockTest(db.Model):
    """UGC NET Mock Test Configuration with weightage system"""
    __tablename__ = 'ugc_net_mock_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    # UGC NET specific configuration
    paper_type = db.Column(db.String(20), nullable=False)  # 'paper1', 'paper2'
    total_questions = db.Column(db.Integer, default=100)  # Standard UGC NET question count
    total_marks = db.Column(db.Integer, default=200)  # Standard UGC NET marks
    time_limit = db.Column(db.Integer, default=180)  # 3 hours in minutes
    
    # Question distribution
    previous_year_percentage = db.Column(db.Float, default=70.0)  # 70% previous year questions
    ai_generated_percentage = db.Column(db.Float, default=30.0)   # 30% AI generated questions
    
    # Difficulty distribution
    easy_percentage = db.Column(db.Float, default=30.0)
    medium_percentage = db.Column(db.Float, default=50.0)
    hard_percentage = db.Column(db.Float, default=20.0)
    
    # Configuration JSON for chapter weightages
    weightage_config = db.Column(db.Text)  # JSON string with chapter weightages
    
    # Status and metadata
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=current_ist_timestamp)
    updated_at = db.Column(db.DateTime, default=current_ist_timestamp, onupdate=current_ist_timestamp)
    
    # Relationships
    subject = db.relationship('Subject', backref='ugc_net_mock_tests')
    creator = db.relationship('User', backref='created_mock_tests')
    
    def set_weightage_config(self, config_dict):
        """Store weightage configuration as JSON"""
        self.weightage_config = json.dumps(config_dict)
    
    def get_weightage_config(self):
        """Retrieve weightage configuration as dict"""
        return json.loads(self.weightage_config) if self.weightage_config else {}
    
    def to_dict(self, include_questions=False):
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'paper_type': self.paper_type,
            'total_questions': self.total_questions,
            'total_marks': self.total_marks,
            'time_limit': self.time_limit,
            'previous_year_percentage': self.previous_year_percentage,
            'ai_generated_percentage': self.ai_generated_percentage,
            'easy_percentage': self.easy_percentage,
            'medium_percentage': self.medium_percentage,
            'hard_percentage': self.hard_percentage,
            'weightage_config': self.get_weightage_config(),
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': get_ist_isoformat(self.created_at),
            'updated_at': get_ist_isoformat(self.updated_at)
        }
        
        # Note: In the current implementation, questions are generated dynamically
        # and not stored with the mock test, so include_questions has no effect
        if include_questions:
            result['note'] = 'Questions are generated dynamically when attempts are started'
        
        return result

class UGCNetMockAttempt(db.Model):
    """UGC NET Mock Test Attempts with detailed analytics"""
    __tablename__ = 'ugc_net_mock_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mock_test_id = db.Column(db.Integer, db.ForeignKey('ugc_net_mock_tests.id'), nullable=False)
    
    # Attempt status and timing
    status = db.Column(db.String(20), default='in_progress')  # 'in_progress', 'completed', 'abandoned'
    start_time = db.Column(db.DateTime, default=current_ist_timestamp)
    end_time = db.Column(db.DateTime)
    time_limit = db.Column(db.Integer, default=180)  # Time limit in minutes
    created_at = db.Column(db.DateTime, default=current_ist_timestamp)
    
    # Basic attempt data
    score = db.Column(db.Float, default=0.0)  # Changed to Float for percentage scores
    total_marks = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Float, default=0.0)
    time_taken = db.Column(db.Integer)  # in seconds
    
    # Answer data
    answers_data = db.Column(db.Text)  # JSON string of user answers
    detailed_results = db.Column(db.Text)  # JSON string with detailed question-wise results
    analytics = db.Column(db.Text)  # JSON string with performance analytics
    
    # UGC NET specific analytics
    paper1_score = db.Column(db.Integer, default=0)  # If applicable
    paper2_score = db.Column(db.Integer, default=0)
    qualification_status = db.Column(db.String(20))  # 'qualified', 'not_qualified', 'borderline'
    predicted_rank = db.Column(db.Integer)  # Predicted rank based on performance
    
    # Chapter-wise performance (JSON)
    chapter_wise_performance = db.Column(db.Text)  # JSON string with chapter scores
    
    # Question-wise data (legacy fields for backward compatibility)
    answers = db.Column(db.Text)  # JSON string of user answers
    question_ids = db.Column(db.Text)  # JSON array of question IDs used in this attempt
    
    # Time tracking (legacy fields for backward compatibility)
    started_at = db.Column(db.DateTime, default=current_ist_timestamp)
    completed_at = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)
    
    # Analysis data
    strengths = db.Column(db.Text)  # JSON array of strength areas
    weaknesses = db.Column(db.Text)  # JSON array of weakness areas
    recommendations = db.Column(db.Text)  # JSON array of study recommendations
    
    # Relationships
    mock_test = db.relationship('UGCNetMockTest', backref='attempts')
    
    def set_answers(self, answers_dict):
        self.answers = json.dumps(answers_dict)
    
    def get_answers(self):
        return json.loads(self.answers) if self.answers else {}
    
    def set_question_ids(self, question_ids_list):
        self.question_ids = json.dumps(question_ids_list)
    
    def get_question_ids(self):
        return json.loads(self.question_ids) if self.question_ids else []
    
    def set_chapter_wise_performance(self, performance_dict):
        self.chapter_wise_performance = json.dumps(performance_dict)
    
    def get_chapter_wise_performance(self):
        return json.loads(self.chapter_wise_performance) if self.chapter_wise_performance else {}
    
    def set_strengths(self, strengths_list):
        self.strengths = json.dumps(strengths_list)
    
    def get_strengths(self):
        return json.loads(self.strengths) if self.strengths else []
    
    def set_weaknesses(self, weaknesses_list):
        self.weaknesses = json.dumps(weaknesses_list)
    
    def get_weaknesses(self):
        return json.loads(self.weaknesses) if self.weaknesses else []
    
    def set_recommendations(self, recommendations_list):
        self.recommendations = json.dumps(recommendations_list)
    
    def get_recommendations(self):
        return json.loads(self.recommendations) if self.recommendations else []
    
    def calculate_ugc_net_score(self):
        """Calculate UGC NET specific scoring and qualification status"""
        if not self.is_completed:
            return 0
            
        # Basic score calculation
        user_answers = self.get_answers()
        question_ids = self.get_question_ids()
        
        score = 0
        chapter_scores = {}
        
        for q_id in question_ids:
            question = QuestionBank.query.get(q_id)
            if question and str(q_id) in user_answers:
                if user_answers[str(q_id)].upper() == question.correct_option:
                    score += question.marks
                    
                    # Track chapter-wise performance
                    chapter_name = question.chapter.name if question.chapter else 'General'
                    if chapter_name not in chapter_scores:
                        chapter_scores[chapter_name] = {'correct': 0, 'total': 0}
                    chapter_scores[chapter_name]['correct'] += 1
                
                # Always count total
                chapter_name = question.chapter.name if question.chapter else 'General'
                if chapter_name not in chapter_scores:
                    chapter_scores[chapter_name] = {'correct': 0, 'total': 0}
                chapter_scores[chapter_name]['total'] += 1
        
        self.score = score
        self.percentage = round((score / self.total_marks) * 100, 2) if self.total_marks > 0 else 0
        self.set_chapter_wise_performance(chapter_scores)
        
        # Determine qualification status (simplified logic)
        if self.percentage >= 40:  # UGC NET qualification threshold
            self.qualification_status = 'qualified'
        elif self.percentage >= 35:
            self.qualification_status = 'borderline'
        else:
            self.qualification_status = 'not_qualified'
        
        db.session.commit()
        return score
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'mock_test_id': self.mock_test_id,
            'mock_test_title': self.mock_test.title if self.mock_test else None,
            'status': self.status,
            'start_time': get_ist_isoformat(self.start_time),
            'end_time': get_ist_isoformat(self.end_time),
            'time_limit': self.time_limit,
            'created_at': get_ist_isoformat(self.created_at),
            'score': self.score,
            'total_marks': self.total_marks,
            'correct_answers': self.correct_answers,
            'total_questions': self.total_questions,
            'percentage': self.percentage,
            'time_taken': self.time_taken,
            'paper1_score': self.paper1_score,
            'paper2_score': self.paper2_score,
            'qualification_status': self.qualification_status,
            'predicted_rank': self.predicted_rank,
            'chapter_wise_performance': self.get_chapter_wise_performance(),
            'started_at': self.started_at.isoformat() + 'Z' if self.started_at else None,
            'completed_at': self.completed_at.isoformat() + 'Z' if self.completed_at else None,
            'is_completed': self.is_completed,
            'strengths': self.get_strengths(),
            'weaknesses': self.get_weaknesses(),
            'recommendations': self.get_recommendations(),
            'analytics': json.loads(self.analytics) if self.analytics else {}
        }

class UGCNetPracticeAttempt(db.Model):
    """UGC NET Practice Test Attempts for focused chapter-wise practice"""
    __tablename__ = 'ugc_net_practice_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    # Practice configuration
    title = db.Column(db.String(200), nullable=False)
    paper_type = db.Column(db.String(20), default='paper2')  # 'paper1', 'paper2'
    practice_type = db.Column(db.String(30), default='chapter_wise')  # 'chapter_wise', 'mixed', 'revision'
    selected_chapters = db.Column(db.Text)  # JSON array of chapter IDs
    
    # Question configuration
    total_questions = db.Column(db.Integer, default=20)
    difficulty_easy = db.Column(db.Integer, default=30)  # Percentage
    difficulty_medium = db.Column(db.Integer, default=50)  # Percentage
    difficulty_hard = db.Column(db.Integer, default=20)  # Percentage
    
    # Source distribution
    previous_year_percentage = db.Column(db.Float, default=70.0)
    ai_generated_percentage = db.Column(db.Float, default=30.0)
    
    # Attempt status and timing
    status = db.Column(db.String(20), default='generated')  # 'generated', 'in_progress', 'completed', 'abandoned'
    time_limit = db.Column(db.Integer, default=30)  # Time limit in minutes
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    time_taken = db.Column(db.Integer)  # in seconds
    
    # Results
    score = db.Column(db.Float, default=0.0)
    total_marks = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Float, default=0.0)
    
    # Data storage
    questions_data = db.Column(db.Text)  # JSON array of question IDs used
    answers_data = db.Column(db.Text)  # JSON object of user answers
    detailed_results = db.Column(db.Text)  # JSON with question-wise results
    
    # Chapter-wise performance
    chapter_wise_performance = db.Column(db.Text)  # JSON with chapter scores
    
    # Analytics and feedback
    strengths = db.Column(db.Text)  # JSON array of strength areas
    weaknesses = db.Column(db.Text)  # JSON array of weakness areas
    recommendations = db.Column(db.Text)  # JSON array of study recommendations
    
    # Metadata
    created_at = db.Column(db.DateTime, default=current_ist_timestamp)
    updated_at = db.Column(db.DateTime, default=current_ist_timestamp, onupdate=current_ist_timestamp)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)
    
    # Relationships
    subject = db.relationship('Subject', backref='practice_attempts')
    
    def set_selected_chapters(self, chapter_ids_list):
        """Store selected chapter IDs as JSON"""
        self.selected_chapters = json.dumps(chapter_ids_list)
    
    def get_selected_chapters(self):
        """Retrieve selected chapter IDs as list"""
        return json.loads(self.selected_chapters) if self.selected_chapters else []
    
    def set_questions_data(self, questions_list):
        """Store questions data as JSON"""
        self.questions_data = json.dumps(questions_list)
    
    def get_questions_data(self):
        """Retrieve questions data as list"""
        return json.loads(self.questions_data) if self.questions_data else []
    
    def set_answers_data(self, answers_dict):
        """Store user answers as JSON"""
        self.answers_data = json.dumps(answers_dict)
    
    def get_answers_data(self):
        """Retrieve user answers as dict"""
        return json.loads(self.answers_data) if self.answers_data else {}
    
    def set_detailed_results(self, results_dict):
        """Store detailed results as JSON"""
        self.detailed_results = json.dumps(results_dict)
    
    def get_detailed_results(self):
        """Retrieve detailed results as dict"""
        return json.loads(self.detailed_results) if self.detailed_results else {}
    
    def set_chapter_wise_performance(self, performance_dict):
        """Store chapter-wise performance as JSON"""
        self.chapter_wise_performance = json.dumps(performance_dict)
    
    def get_chapter_wise_performance(self):
        """Retrieve chapter-wise performance as dict"""
        return json.loads(self.chapter_wise_performance) if self.chapter_wise_performance else {}
    
    def set_strengths(self, strengths_list):
        """Store strengths as JSON"""
        self.strengths = json.dumps(strengths_list)
    
    def get_strengths(self):
        """Retrieve strengths as list"""
        return json.loads(self.strengths) if self.strengths else []
    
    def set_weaknesses(self, weaknesses_list):
        """Store weaknesses as JSON"""
        self.weaknesses = json.dumps(weaknesses_list)
    
    def get_weaknesses(self):
        """Retrieve weaknesses as list"""
        return json.loads(self.weaknesses) if self.weaknesses else []
    
    def set_recommendations(self, recommendations_list):
        """Store recommendations as JSON"""
        self.recommendations = json.dumps(recommendations_list)
    
    def get_recommendations(self):
        """Retrieve recommendations as list"""
        return json.loads(self.recommendations) if self.recommendations else []
    
    def calculate_practice_score(self):
        """Calculate practice test score and analytics"""
        if not self.is_completed or not self.questions_data or not self.answers_data:
            return 0
            
        questions_data = self.get_questions_data()
        user_answers = self.get_answers_data()
        
        correct_count = 0
        total_marks = 0
        chapter_performance = {}
        detailed_results = []
        
        for question_data in questions_data:
            question_id = question_data['id']
            total_marks += question_data.get('marks', 1)
            
            # Check if answer is correct
            is_correct = False
            if str(question_id) in user_answers:
                user_answer = user_answers[str(question_id)].upper()
                correct_answer = question_data.get('correct_option', '').upper()
                is_correct = user_answer == correct_answer
                
                if is_correct:
                    correct_count += 1
            
            # Track chapter-wise performance
            chapter_name = question_data.get('chapter_name', 'General')
            if chapter_name not in chapter_performance:
                chapter_performance[chapter_name] = {'correct': 0, 'total': 0}
            
            chapter_performance[chapter_name]['total'] += 1
            if is_correct:
                chapter_performance[chapter_name]['correct'] += 1
            
            # Store detailed result
            detailed_results.append({
                'question_id': question_id,
                'is_correct': is_correct,
                'user_answer': user_answers.get(str(question_id), ''),
                'correct_answer': question_data.get('correct_option', ''),
                'marks': question_data.get('marks', 1),
                'chapter': chapter_name,
                'difficulty': question_data.get('difficulty', 'medium')
            })
        
        # Update attempt data
        self.correct_answers = correct_count
        self.total_marks = total_marks
        self.score = correct_count  # For practice tests, score = correct answers
        self.percentage = round((correct_count / len(questions_data)) * 100, 2) if questions_data else 0
        
        # Store analysis data
        self.set_detailed_results({'questions': detailed_results})
        self.set_chapter_wise_performance(chapter_performance)
        
        # Generate strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for chapter, perf in chapter_performance.items():
            chapter_percentage = (perf['correct'] / perf['total']) * 100 if perf['total'] > 0 else 0
            if chapter_percentage >= 70:
                strengths.append(chapter)
            elif chapter_percentage < 50:
                weaknesses.append(chapter)
        
        self.set_strengths(strengths)
        self.set_weaknesses(weaknesses)
        
        # Generate recommendations
        recommendations = []
        if weaknesses:
            recommendations.append(f"Focus more on: {', '.join(weaknesses)}")
        if self.percentage < 60:
            recommendations.append("Consider reviewing the basics and practicing more questions")
        if self.percentage >= 80:
            recommendations.append("Great performance! Try harder difficulty levels")
        
        self.set_recommendations(recommendations)
        
        db.session.commit()
        return self.score
    
    def to_dict(self, include_questions=False, include_answers=False):
        """Convert to dictionary for API responses"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'title': self.title,
            'paper_type': self.paper_type,
            'practice_type': self.practice_type,
            'selected_chapters': self.get_selected_chapters(),
            'total_questions': self.total_questions,
            'difficulty_easy': self.difficulty_easy,
            'difficulty_medium': self.difficulty_medium,
            'difficulty_hard': self.difficulty_hard,
            'previous_year_percentage': self.previous_year_percentage,
            'ai_generated_percentage': self.ai_generated_percentage,
            'status': self.status,
            'time_limit': self.time_limit,
            'start_time': get_ist_isoformat(self.start_time),
            'end_time': get_ist_isoformat(self.end_time),
            'time_taken': self.time_taken,
            'score': self.score,
            'total_marks': self.total_marks,
            'correct_answers': self.correct_answers,
            'percentage': self.percentage,
            'chapter_wise_performance': self.get_chapter_wise_performance(),
            'strengths': self.get_strengths(),
            'weaknesses': self.get_weaknesses(),
            'recommendations': self.get_recommendations(),
            'created_at': get_ist_isoformat(self.created_at),
            'updated_at': get_ist_isoformat(self.updated_at),
            'started_at': get_ist_isoformat(self.started_at),
            'completed_at': get_ist_isoformat(self.completed_at),
            'is_completed': self.is_completed
        }
        
        if include_questions:
            result['questions'] = self.get_questions_data()
        
        if include_answers:
            result['answers'] = self.get_answers_data()
            result['detailed_results'] = self.get_detailed_results()
        
        return result

class UserStudySession(db.Model):
    """Track detailed user study sessions for AI analysis"""
    __tablename__ = 'user_study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_type = db.Column(db.String(50), nullable=False)  # 'practice', 'mock', 'study', 'revision'
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    chapter_ids = db.Column(db.JSON, nullable=True)  # List of chapter IDs studied
    
    # Session details
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    
    # Performance metrics
    questions_attempted = db.Column(db.Integer, default=0)
    questions_correct = db.Column(db.Integer, default=0)
    accuracy_percentage = db.Column(db.Float, nullable=True)
    average_time_per_question = db.Column(db.Float, nullable=True)  # in seconds
    
    # Learning insights
    difficulty_level = db.Column(db.String(20), nullable=True)  # 'easy', 'medium', 'hard'
    topics_mastered = db.Column(db.JSON, nullable=True)  # List of topic IDs where user scored >80%
    topics_struggling = db.Column(db.JSON, nullable=True)  # List of topic IDs where user scored <50%
    
    # Engagement metrics
    focus_score = db.Column(db.Float, nullable=True)  # Based on time patterns (1-100)
    completion_rate = db.Column(db.Float, nullable=True)  # Percentage of session completed
    
    # Metadata
    device_type = db.Column(db.String(50), nullable=True)  # 'mobile', 'desktop', 'tablet'
    created_at = db.Column(db.DateTime, default=current_ist_timestamp)
    updated_at = db.Column(db.DateTime, default=current_ist_timestamp, onupdate=current_ist_timestamp)
    
    # Relationships
    user = db.relationship('User', backref='study_sessions')
    subject = db.relationship('Subject', backref='study_sessions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_type': self.session_type,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'chapter_ids': self.chapter_ids,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'questions_attempted': self.questions_attempted,
            'questions_correct': self.questions_correct,
            'accuracy_percentage': self.accuracy_percentage,
            'average_time_per_question': self.average_time_per_question,
            'difficulty_level': self.difficulty_level,
            'topics_mastered': self.topics_mastered,
            'topics_struggling': self.topics_struggling,
            'focus_score': self.focus_score,
            'completion_rate': self.completion_rate,
            'device_type': self.device_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserLearningMetrics(db.Model):
    """Store aggregated learning metrics for AI recommendations"""
    __tablename__ = 'user_learning_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Overall performance
    total_study_hours = db.Column(db.Float, default=0.0)
    total_questions_attempted = db.Column(db.Integer, default=0)
    total_questions_correct = db.Column(db.Integer, default=0)
    overall_accuracy = db.Column(db.Float, default=0.0)
    
    # Learning patterns
    preferred_study_time = db.Column(db.String(20), nullable=True)  # 'morning', 'afternoon', 'evening', 'night'
    average_session_duration = db.Column(db.Float, default=0.0)  # in minutes
    study_consistency_score = db.Column(db.Float, default=0.0)  # 1-100 based on regular study pattern
    
    # Strength and weakness analysis
    strong_subjects = db.Column(db.JSON, nullable=True)  # List of subject IDs with >70% accuracy
    weak_subjects = db.Column(db.JSON, nullable=True)  # List of subject IDs with <50% accuracy
    strong_chapters = db.Column(db.JSON, nullable=True)  # List of chapter IDs with >70% accuracy
    weak_chapters = db.Column(db.JSON, nullable=True)  # List of chapter IDs with <50% accuracy
    
    # Progress tracking
    improvement_trend = db.Column(db.Float, default=0.0)  # +/- percentage change over last 30 days
    plateau_warning = db.Column(db.Boolean, default=False)  # True if no improvement for 2+ weeks
    last_significant_improvement = db.Column(db.DateTime, nullable=True)
    
    # AI insights
    learning_style = db.Column(db.String(50), nullable=True)  # 'visual', 'auditory', 'kinesthetic', 'mixed'
    recommended_daily_hours = db.Column(db.Float, default=2.0)
    estimated_readiness_percentage = db.Column(db.Float, default=0.0)  # Overall exam readiness (1-100)
    
    # Metadata
    last_calculated = db.Column(db.DateTime, default=current_ist_timestamp)
    calculation_version = db.Column(db.String(10), default='1.0')  # For tracking algorithm updates
    
    # Relationships
    user = db.relationship('User', backref='learning_metrics')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_study_hours': self.total_study_hours,
            'total_questions_attempted': self.total_questions_attempted,
            'total_questions_correct': self.total_questions_correct,
            'overall_accuracy': self.overall_accuracy,
            'preferred_study_time': self.preferred_study_time,
            'average_session_duration': self.average_session_duration,
            'study_consistency_score': self.study_consistency_score,
            'strong_subjects': self.strong_subjects,
            'weak_subjects': self.weak_subjects,
            'strong_chapters': self.strong_chapters,
            'weak_chapters': self.weak_chapters,
            'improvement_trend': self.improvement_trend,
            'plateau_warning': self.plateau_warning,
            'last_significant_improvement': self.last_significant_improvement.isoformat() if self.last_significant_improvement else None,
            'learning_style': self.learning_style,
            'recommended_daily_hours': self.recommended_daily_hours,
            'estimated_readiness_percentage': self.estimated_readiness_percentage,
            'last_calculated': self.last_calculated.isoformat() if self.last_calculated else None,
            'calculation_version': self.calculation_version
        }

# TestAttempt and QuestionResponse models removed as they are redundant
# Their functionality is covered by UGCNetMockAttempt and UGCNetPracticeAttempt models


