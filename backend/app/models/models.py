from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
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
    timezone = db.Column(db.String(50), default='UTC')
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        from sqlalchemy.orm import selectinload
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'chapters_count': Chapter.query.filter_by(subject_id=self.id).count()
        }

class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'quizzes_count': Quiz.query.filter_by(chapter_id=self.id).count()
        }

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    time_limit = db.Column(db.Integer, default=60)  # minutes
    total_marks = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    is_ai_generated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True, cascade='all, delete-orphan')
    
    def update_total_marks(self):
        questions = Question.query.filter_by(quiz_id=self.id).all()
        self.total_marks = sum(q.marks for q in questions)
        db.session.commit()
    
    def to_dict(self):
        questions_count = Question.query.filter_by(quiz_id=self.id).count()
        
        # Map is_active to status for frontend compatibility
        if self.is_active:
            status = 'active'
        else:
            status = 'inactive'
            
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'chapter_id': self.chapter_id,
            'chapter_name': self.chapter.name if self.chapter else None,
            'subject_name': self.chapter.subject.name if self.chapter and self.chapter.subject else None,
            'subject_id': self.chapter.subject_id if self.chapter else None,
            'difficulty': self.difficulty,
            'time_limit': self.time_limit,
            'total_marks': self.total_marks,
            'is_active': self.is_active,
            'status': status,
            'is_ai_generated': self.is_ai_generated,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'questions_count': questions_count,
            'total_questions': questions_count
        }

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # A, B, C, or D
    explanation = db.Column(db.Text)
    marks = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # AI Verification fields
    is_verified = db.Column(db.Boolean, default=False)
    verification_confidence = db.Column(db.Float)
    verification_attempts = db.Column(db.Integer, default=0)
    verification_status = db.Column(db.String(20), default='pending')  # pending, verified, failed, manual_review
    verification_metadata = db.Column(db.Text)  # JSON string for verification details
    verified_at = db.Column(db.DateTime)
    
    def to_dict(self, include_answer=False):
        data = {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_text': self.question_text,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'option_d': self.option_d,
            'marks': self.marks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_verified': self.is_verified,
            'verification_status': self.verification_status,
            'verification_confidence': self.verification_confidence
        }
        
        if include_answer:
            data['correct_option'] = self.correct_option
            data['explanation'] = self.explanation
            
        return data
    
    def set_verification_metadata(self, metadata_dict):
        """Store verification metadata as JSON"""
        self.verification_metadata = json.dumps(metadata_dict)
    
    def get_verification_metadata(self):
        """Retrieve verification metadata as dict"""
        return json.loads(self.verification_metadata) if self.verification_metadata else {}
    
    def mark_verified(self, confidence, metadata=None):
        """Mark question as verified"""
        self.is_verified = True
        self.verification_status = 'verified'
        self.verification_confidence = confidence
        self.verified_at = datetime.utcnow()
        if metadata:
            self.set_verification_metadata(metadata)
    
    def mark_failed_verification(self, metadata=None):
        """Mark question as failed verification"""
        self.verification_status = 'failed'
        if metadata:
            self.set_verification_metadata(metadata)
    
    def get_options_dict(self):
        """Get options as dictionary for verification"""
        return {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d
        }

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    total_marks = db.Column(db.Integer, default=0)
    time_taken = db.Column(db.Integer)  # in seconds
    answers = db.Column(db.Text)  # JSON string of user answers
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)
    
    def set_answers(self, answers_dict):
        self.answers = json.dumps(answers_dict)
    
    def get_answers(self):
        return json.loads(self.answers) if self.answers else {}
    
    def calculate_score(self):
        if not self.is_completed:
            return 0
            
        user_answers = self.get_answers()
        score = 0
        
        for question in self.quiz.questions:
            question_id = str(question.id)
            if question_id in user_answers:
                if user_answers[question_id].upper() == question.correct_option:
                    score += question.marks
        
        self.score = score
        self.total_marks = self.quiz.total_marks
        db.session.commit()
        return score
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'quiz_title': self.quiz.title if self.quiz else None,
            'subject_name': self.quiz.chapter.subject.name if self.quiz and self.quiz.chapter and self.quiz.chapter.subject else None,
            'score': self.score,
            'total_marks': self.total_marks,
            'percentage': round((self.score / self.total_marks) * 100, 2) if self.total_marks > 0 else 0,
            'time_taken': self.time_taken,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_completed': self.is_completed
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chapter = db.relationship('Chapter', backref='study_materials')
    creator = db.relationship('User', backref='created_study_materials')
    
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class QuestionPerformance(db.Model):
    """Track performance analytics for each question attempt"""
    __tablename__ = 'question_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    question_bank_id = db.Column(db.Integer, db.ForeignKey('question_bank.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'))
    
    # Answer data
    selected_option = db.Column(db.String(1), nullable=False)  # A, B, C, or D
    is_correct = db.Column(db.Boolean, nullable=False)
    time_taken = db.Column(db.Integer)  # Time in seconds
    
    # Context
    difficulty_at_time = db.Column(db.String(20))  # Difficulty when answered
    topic_at_time = db.Column(db.String(200))  # Topic when answered
    
    # Timestamps
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question_bank = db.relationship('QuestionBank', backref='performance_history')
    user = db.relationship('User', backref='question_performances')
    quiz_attempt = db.relationship('QuizAttempt', backref='question_performances')
    
    def __repr__(self):
        return f'<QuestionPerformance {self.id}: Q{self.question_bank_id} U{self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_bank_id': self.question_bank_id,
            'user_id': self.user_id,
            'quiz_attempt_id': self.quiz_attempt_id,
            'selected_option': self.selected_option,
            'is_correct': self.is_correct,
            'time_taken': self.time_taken,
            'difficulty_at_time': self.difficulty_at_time,
            'topic_at_time': self.topic_at_time,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None
        }
    
    @classmethod
    def get_question_stats(cls, question_bank_id: int) -> Dict:
        """Get performance statistics for a specific question"""
        from sqlalchemy import func
        
        performances = cls.query.filter_by(question_bank_id=question_bank_id)
        total_attempts = performances.count()
        
        if total_attempts == 0:
            return {
                'total_attempts': 0,
                'success_rate': 0,
                'average_time': 0,
                'difficulty_perception': 'unknown'
            }
        
        correct_attempts = performances.filter_by(is_correct=True).count()
        success_rate = (correct_attempts / total_attempts) * 100
        
        # Average time taken
        avg_time_result = performances.with_entities(func.avg(cls.time_taken)).scalar()
        average_time = int(avg_time_result) if avg_time_result else 0
        
        # Difficulty perception based on success rate
        if success_rate >= 80:
            difficulty_perception = 'easy'
        elif success_rate >= 60:
            difficulty_perception = 'medium'
        else:
            difficulty_perception = 'hard'
        
        return {
            'total_attempts': total_attempts,
            'success_rate': round(success_rate, 2),
            'average_time': average_time,
            'difficulty_perception': difficulty_perception
        }
    
    @classmethod
    def get_user_performance(cls, user_id: int, question_bank_id: Optional[int] = None) -> Dict:
        """Get performance statistics for a user, optionally for a specific question"""
        query = cls.query.filter_by(user_id=user_id)
        
        if question_bank_id:
            query = query.filter_by(question_bank_id=question_bank_id)
        
        performances = query.all()
        total_attempts = len(performances)
        
        if total_attempts == 0:
            return {
                'total_attempts': 0,
                'success_rate': 0,
                'average_time': 0,
                'strong_topics': [],
                'weak_topics': []
            }
        
        correct_attempts = len([p for p in performances if p.is_correct])
        success_rate = (correct_attempts / total_attempts) * 100
        
        # Average time
        times = [p.time_taken for p in performances if p.time_taken is not None]
        average_time = sum(times) // len(times) if times else 0
        
        # Topic analysis
        topic_stats = {}
        for perf in performances:
            topic = perf.topic_at_time or 'Unknown'
            if topic not in topic_stats:
                topic_stats[topic] = {'correct': 0, 'total': 0}
            topic_stats[topic]['total'] += 1
            if perf.is_correct:
                topic_stats[topic]['correct'] += 1
        
        # Calculate topic success rates
        topic_rates = {}
        for topic, stats in topic_stats.items():
            topic_rates[topic] = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
        
        # Identify strong and weak topics
        strong_topics = [topic for topic, rate in topic_rates.items() if rate >= 75 and topic_stats[topic]['total'] >= 3]
        weak_topics = [topic for topic, rate in topic_rates.items() if rate <= 50 and topic_stats[topic]['total'] >= 3]
        
        return {
            'total_attempts': total_attempts,
            'success_rate': round(success_rate, 2),
            'average_time': average_time,
            'strong_topics': strong_topics[:5],  # Top 5
            'weak_topics': weak_topics[:5]  # Bottom 5
        }

class QuestionBank(db.Model):
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
    
    # Question bank specific fields
    topic = db.Column(db.String(200), nullable=False)  # Topic/subject area
    difficulty = db.Column(db.String(20), nullable=False)  # easy, medium, hard
    source = db.Column(db.String(50), default='ai_generated')  # ai_generated, manual, imported
    tags = db.Column(db.Text)  # JSON array of tags for categorization
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Content hash for deduplication
    content_hash = db.Column(db.String(64), unique=True, nullable=False)
    
    # Relationships
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'))
    chapter = db.relationship('Chapter', backref='question_bank_questions')
    verified_by_user = db.relationship('User', backref='verified_questions')
    
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
            'topic': self.topic,
            'difficulty': self.difficulty,
            'source': self.source,
            'tags': json.loads(self.tags) if self.tags else [],
            'is_verified': self.is_verified,
            'verification_method': self.verification_method,
            'verification_confidence': self.verification_confidence,
            'verification_notes': self.verification_notes,
            'usage_count': self.usage_count,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'chapter_id': self.chapter_id
        }
        
        if include_answer:
            data['correct_option'] = self.correct_option
            data['explanation'] = self.explanation
            
        return data
    
    def set_tags(self, tags_list):
        """Set tags as JSON array"""
        self.tags = json.dumps(tags_list) if tags_list else None
    
    def get_tags(self):
        """Get tags as list"""
        return json.loads(self.tags) if self.tags else []
    
    def generate_content_hash(self):
        """Generate hash for deduplication based on question content"""
        import hashlib
        content = f"{self.question_text}{self.option_a}{self.option_b}{self.option_c}{self.option_d}{self.correct_option}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def mark_verified(self, method, confidence, verified_by_user_id, notes=None):
        """Mark question as verified"""
        self.is_verified = True
        self.verification_method = method
        self.verification_confidence = confidence
        self.verified_by = verified_by_user_id
        self.verification_notes = notes
        self.verified_at = datetime.utcnow()
    
    def increment_usage(self):
        """Increment usage count and update last used timestamp"""
        self.usage_count += 1
        self.last_used = datetime.utcnow()
    
    @classmethod
    def find_duplicates(cls, question_text, options):
        """Find potential duplicate questions based on content hash"""
        import hashlib
        content = f"{question_text}{options['A']}{options['B']}{options['C']}{options['D']}"
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        return cls.query.filter_by(content_hash=content_hash).first()
    
    @classmethod
    def search_by_topic_and_difficulty(cls, topic=None, difficulty=None, verified_only=True, limit=None):
        """Search question bank by topic and difficulty"""
        query = cls.query
        
        if verified_only:
            query = query.filter_by(is_verified=True)
        if topic:
            query = query.filter(cls.topic.ilike(f'%{topic}%'))
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
            
        query = query.order_by(cls.usage_count.asc(), cls.created_at.desc())
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def get_performance_stats(self):
        """Get performance statistics for this question"""
        from sqlalchemy import func
        
        # Import here to avoid any potential circular import issues
        performances = db.session.query(QuestionPerformance).filter_by(question_bank_id=self.id)
        
        total_attempts = performances.count()
        if total_attempts == 0:
            return {
                'total_attempts': 0,
                'success_rate': 0,
                'average_time': 0,
                'difficulty_rating': self.difficulty
            }
        
        correct_attempts = performances.filter_by(is_correct=True).count()
        success_rate = (correct_attempts / total_attempts) * 100
        
        # Average time taken
        avg_time_result = performances.with_entities(func.avg(QuestionPerformance.time_taken)).scalar()
        average_time = int(avg_time_result) if avg_time_result else 0
        
        return {
            'total_attempts': total_attempts,
            'success_rate': round(success_rate, 2),
            'average_time': average_time,
            'difficulty_rating': self.difficulty,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }
    
    def needs_review(self, min_attempts=10, min_success_rate=60):
        """Check if question needs review based on performance"""
        stats = self.get_performance_stats()
        return (stats['total_attempts'] >= min_attempts and 
                stats['success_rate'] < min_success_rate)
    
    def get_usage_trends(self, days=30):
        """Get usage trends over specified days"""
        from sqlalchemy import func, and_
        from datetime import timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        daily_usage = db.session.query(
            func.date(QuestionPerformance.answered_at).label('date'),
            func.count(QuestionPerformance.id).label('count')
        ).filter(
            and_(
                QuestionPerformance.question_bank_id == self.id,
                QuestionPerformance.answered_at >= start_date,
                QuestionPerformance.answered_at <= end_date
            )
        ).group_by(func.date(QuestionPerformance.answered_at)).all()
        
        return [{'date': str(usage.date), 'count': usage.count} for usage in daily_usage]


