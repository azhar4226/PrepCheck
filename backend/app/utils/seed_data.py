from app import db
from app.models import User
from werkzeug.security import generate_password_hash
import os

def seed_admin_user():
    """Create default admin user if it doesn't exist"""
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@prepcheck.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # Check if admin already exists
    admin_user = User.query.filter_by(email=admin_email, is_admin=True).first()
    
    if not admin_user:
        admin_user = User(
            email=admin_email,
            full_name='System Administrator',
            is_admin=True,
            is_active=True
        )
        admin_user.set_password(admin_password)
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"✅ Admin user created: {admin_email}")
    else:
        print(f"ℹ️  Admin user already exists: {admin_email}")

def seed_sample_data():
    """Create sample subjects, chapters, and quizzes for testing"""
    from app.models import Subject, Chapter, Quiz, Question
    
    # Create sample subject
    subject = Subject.query.filter_by(name='Mathematics').first()
    if not subject:
        subject = Subject(
            name='Mathematics',
            description='Basic mathematics concepts and problem solving'
        )
        db.session.add(subject)
        db.session.flush()
    
    # Create sample chapter
    chapter = Chapter.query.filter_by(name='Algebra', subject_id=subject.id).first()
    if not chapter:
        chapter = Chapter(
            name='Algebra',
            description='Linear equations, quadratic equations, and polynomials',
            subject_id=subject.id
        )
        db.session.add(chapter)
        db.session.flush()
    
    # Create sample quiz
    quiz = Quiz.query.filter_by(title='Basic Algebra Quiz', chapter_id=chapter.id).first()
    if not quiz:
        quiz = Quiz(
            title='Basic Algebra Quiz',
            description='Test your knowledge of basic algebraic concepts',
            chapter_id=chapter.id,
            time_limit=30
        )
        db.session.add(quiz)
        db.session.flush()
        
        # Create sample questions
        sample_questions = [
            {
                'question_text': 'What is the value of x in the equation 2x + 5 = 15?',
                'option_a': 'x = 3',
                'option_b': 'x = 5',
                'option_c': 'x = 7',
                'option_d': 'x = 10',
                'correct_option': 'B',
                'explanation': '2x + 5 = 15, so 2x = 10, therefore x = 5'
            },
            {
                'question_text': 'Solve for y: 3y - 7 = 14',
                'option_a': 'y = 5',
                'option_b': 'y = 6',
                'option_c': 'y = 7',
                'option_d': 'y = 8',
                'correct_option': 'C',
                'explanation': '3y - 7 = 14, so 3y = 21, therefore y = 7'
            },
            {
                'question_text': 'What is the product of (x + 3)(x - 2)?',
                'option_a': 'x² + x - 6',
                'option_b': 'x² - x + 6',
                'option_c': 'x² + x + 6',
                'option_d': 'x² - x - 6',
                'correct_option': 'A',
                'explanation': '(x + 3)(x - 2) = x² - 2x + 3x - 6 = x² + x - 6'
            }
        ]
        
        for q_data in sample_questions:
            question = Question(
                quiz_id=quiz.id,
                question_text=q_data['question_text'],
                option_a=q_data['option_a'],
                option_b=q_data['option_b'],
                option_c=q_data['option_c'],
                option_d=q_data['option_d'],
                correct_option=q_data['correct_option'],
                explanation=q_data['explanation'],
                marks=1
            )
            db.session.add(question)
        
        quiz.update_total_marks()
    
    db.session.commit()
    print("✅ Sample data created successfully")
