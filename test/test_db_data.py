#!/usr/bin/env python3
"""Quick script to check database data"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app
from app.models.models import User, Subject, Quiz, QuizAttempt

app = create_app()

with app.app_context():
    print("=== Database Data Check ===")
    
    # Check users
    total_users = User.query.count()
    admin_users = User.query.filter_by(is_admin=True).count()
    regular_users = User.query.filter_by(is_admin=False).count()
    
    print(f"Users:")
    print(f"  Total: {total_users}")
    print(f"  Admins: {admin_users}")
    print(f"  Regular: {regular_users}")
    
    # Check subjects
    total_subjects = Subject.query.count()
    active_subjects = Subject.query.filter_by(is_active=True).count()
    
    print(f"\nSubjects:")
    print(f"  Total: {total_subjects}")
    print(f"  Active: {active_subjects}")
    
    # Check quizzes
    total_quizzes = Quiz.query.count()
    active_quizzes = Quiz.query.filter_by(is_active=True).count()
    
    print(f"\nQuizzes:")
    print(f"  Total: {total_quizzes}")
    print(f"  Active: {active_quizzes}")
    
    # Check quiz attempts
    total_attempts = QuizAttempt.query.count()
    completed_attempts = QuizAttempt.query.filter_by(is_completed=True).count()
    
    print(f"\nQuiz Attempts:")
    print(f"  Total: {total_attempts}")
    print(f"  Completed: {completed_attempts}")
    
    # List some users if they exist
    if total_users > 0:
        print(f"\nFirst few users:")
        users = User.query.limit(5).all()
        for user in users:
            print(f"  - {user.full_name} ({user.email}) - Admin: {user.is_admin}")
    
    # List some subjects if they exist
    if total_subjects > 0:
        print(f"\nSubjects:")
        subjects = Subject.query.limit(5).all()
        for subject in subjects:
            print(f"  - {subject.name} - Active: {subject.is_active}")
