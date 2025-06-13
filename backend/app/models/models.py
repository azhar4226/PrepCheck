from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

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
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_answer:
            data['correct_option'] = self.correct_option
            data['explanation'] = self.explanation
            
        return data

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
            'score': self.score,
            'total_marks': self.total_marks,
            'percentage': round((self.score / self.total_marks) * 100, 2) if self.total_marks > 0 else 0,
            'time_taken': self.time_taken,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_completed': self.is_completed
        }
