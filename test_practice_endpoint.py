#!/usr/bin/env python3
"""Test the practice test endpoint data structure"""

import sys
import os
import requests
import json

# Simple test without authentication - let's check what structure the DB has
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    from backend.app import create_app
    from backend.app.models.models import UGCNetPracticeAttempt
    
    app = create_app()
    
    with app.app_context():
        # Get a practice attempt
        attempt = UGCNetPracticeAttempt.query.filter_by(id=6).first()
        
        if attempt:
            print("Found attempt 6:")
            print(f"  - Status: {attempt.status}")
            print(f"  - Title: {attempt.title}")
            print(f"  - Total questions: {attempt.total_questions}")
            
            # Check raw questions data
            questions_data = attempt.get_questions_data()
            print(f"  - Questions data length: {len(questions_data) if questions_data else 0}")
            
            if questions_data:
                print(f"  - First question sample:")
                first_q = questions_data[0]
                print(f"    - ID: {first_q.get('id')}")
                print(f"    - Question text: {first_q.get('question_text', '')[:50]}...")
                print(f"    - Option A: {first_q.get('option_a', '')[:30]}...")
                print(f"    - All keys: {list(first_q.keys())}")
            
            # Test to_dict method
            print("\n" + "="*50)
            print("Testing to_dict(include_questions=True):")
            attempt_dict = attempt.to_dict(include_questions=True)
            print(f"  - 'questions' key exists: {'questions' in attempt_dict}")
            
            if 'questions' in attempt_dict:
                questions = attempt_dict['questions']
                print(f"  - Questions length: {len(questions)}")
                if questions:
                    print(f"  - First question from to_dict:")
                    first_q_dict = questions[0]
                    print(f"    - ID: {first_q_dict.get('id')}")
                    print(f"    - Question text: {first_q_dict.get('question_text', '')[:50]}...")
                    print(f"    - All keys: {list(first_q_dict.keys())}")
        else:
            print("No attempt found with ID 6")
            
            # List available attempts
            attempts = UGCNetPracticeAttempt.query.all()
            print(f"Available attempts: {[a.id for a in attempts]}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
