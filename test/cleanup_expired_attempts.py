#!/usr/bin/env python3
"""
Script to clean up expired 'in_progress' attempts that should be marked as completed
"""

import os
import sys
from datetime import datetime, timedelta

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
load_dotenv()

from backend.app import create_app, db
from backend.app.models import UGCNetMockAttempt, UGCNetMockTest

def cleanup_expired_attempts():
    """Clean up expired attempts that are still marked as in_progress"""
    app = create_app()
    
    with app.app_context():
        # Find all in_progress attempts
        in_progress_attempts = UGCNetMockAttempt.query.filter_by(status='in_progress').all()
        
        cleaned_count = 0
        for attempt in in_progress_attempts:
            # Get the mock test to check time limit
            mock_test = UGCNetMockTest.query.get(attempt.mock_test_id)
            if not mock_test:
                continue
                
            # Calculate if the attempt has expired
            if attempt.start_time:
                time_limit_minutes = mock_test.time_limit
                expiry_time = attempt.start_time + timedelta(minutes=time_limit_minutes)
                
                if datetime.utcnow() > expiry_time:
                    # Mark as completed with 0 score
                    attempt.status = 'completed'
                    attempt.end_time = expiry_time
                    attempt.score = 0.0
                    attempt.percentage = 0.0
                    attempt.correct_answers = 0
                    attempt.total_questions = mock_test.total_questions
                    
                    print(f"Cleaned up expired attempt {attempt.id} for test {attempt.mock_test_id}")
                    cleaned_count += 1
        
        if cleaned_count > 0:
            db.session.commit()
            print(f"Successfully cleaned up {cleaned_count} expired attempts")
        else:
            print("No expired attempts found")

if __name__ == '__main__':
    cleanup_expired_attempts()
