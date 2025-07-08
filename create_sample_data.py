#!/usr/bin/env python3
"""Create some sample test attempts for demonstrating the history functionality"""

import os
import sys
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from app.models.models import User, Subject, Chapter, UGCNetMockTest, UGCNetMockAttempt, db
import random

def create_sample_data():
    app = create_app()
    
    with app.app_context():
        # Find or create a test user
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            from werkzeug.security import generate_password_hash
            user = User(
                email='test@example.com',
                full_name='Test User',
                password_hash=generate_password_hash('password'),
                is_admin=False,
                is_verified=True
            )
            db.session.add(user)
            db.session.commit()
            print("Created test user: test@example.com / password")

        # Find or create a subject
        subject = Subject.query.filter_by(name='Computer Science').first()
        if not subject:
            subject = Subject(
                name='Computer Science',
                description='Computer Science for UGC NET'
            )
            db.session.add(subject)
            db.session.commit()

        # Find or create a mock test
        mock_test = UGCNetMockTest.query.filter_by(title='Sample Mock Test').first()
        if not mock_test:
            mock_test = UGCNetMockTest(
                title='Sample Mock Test',
                subject_id=subject.id,
                total_questions=50,
                time_limit=180,  # 3 hours
                is_active=True,
                weightage_config={'easy': 20, 'medium': 20, 'hard': 10}
            )
            db.session.add(mock_test)
            db.session.commit()

        # Create sample attempts with different dates and scores
        sample_attempts = [
            {'score': 85, 'days_ago': 1},
            {'score': 72, 'days_ago': 3},
            {'score': 68, 'days_ago': 7},
            {'score': 91, 'days_ago': 14},
        ]

        for attempt_data in sample_attempts:
            # Check if attempt already exists for this date
            attempt_date = datetime.now() - timedelta(days=attempt_data['days_ago'])
            existing = UGCNetMockAttempt.query.filter_by(
                user_id=user.id,
                mock_test_id=mock_test.id
            ).filter(
                UGCNetMockAttempt.created_at >= attempt_date.date(),
                UGCNetMockAttempt.created_at < (attempt_date + timedelta(days=1)).date()
            ).first()

            if not existing:
                attempt = UGCNetMockAttempt(
                    user_id=user.id,
                    mock_test_id=mock_test.id,
                    total_questions=mock_test.total_questions,
                    correct_answers=int(mock_test.total_questions * attempt_data['score'] / 100),
                    incorrect_answers=mock_test.total_questions - int(mock_test.total_questions * attempt_data['score'] / 100),
                    unanswered=0,
                    score_percentage=attempt_data['score'],
                    time_taken=random.randint(120, 170),  # Random time between 2-2.8 hours
                    is_completed=True,
                    created_at=attempt_date,
                    updated_at=attempt_date
                )
                db.session.add(attempt)

        db.session.commit()
        print(f"Created sample test attempts for user {user.email}")
        print("You can now login with test@example.com / password to see test history")

if __name__ == '__main__':
    create_sample_data()
