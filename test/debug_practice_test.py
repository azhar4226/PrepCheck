#!/usr/bin/env python3

import os
import sys
import sqlite3
import json

# Set up the path
sys.path.append('/Users/apple/Desktop/PrepCheck/backend')

def check_practice_test_data():
    """Check practice test data directly from database"""
    db_path = '/Users/apple/Desktop/PrepCheck/backend/instance/prepcheck.db'
    
    if not os.path.exists(db_path):
        print(f"Database file not found at: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ugc_net_practice_attempts'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("UGC NET practice attempts table does not exist!")
            return
        
        # Get all practice attempts
        cursor.execute("SELECT id, status, total_questions, questions_data FROM ugc_net_practice_attempts")
        attempts = cursor.fetchall()
        
        print(f"Found {len(attempts)} practice attempts:")
        
        for attempt_id, status, total_questions, questions_data in attempts:
            print(f"\nAttempt ID: {attempt_id}")
            print(f"  Status: {status}")
            print(f"  Total Questions: {total_questions}")
            print(f"  Questions Data Length: {len(questions_data) if questions_data else 0}")
            
            if questions_data:
                try:
                    parsed_questions = json.loads(questions_data)
                    print(f"  Parsed Questions Count: {len(parsed_questions)}")
                    
                    if parsed_questions:
                        first_question = parsed_questions[0]
                        print(f"  First Question Keys: {list(first_question.keys())}")
                        print(f"  First Question ID: {first_question.get('id', 'NO_ID')}")
                        print(f"  First Question Text: {first_question.get('question_text', 'NO_TEXT')[:100]}...")
                        print(f"  First Question Options: A={bool(first_question.get('option_a'))}, B={bool(first_question.get('option_b'))}")
                except json.JSONDecodeError as e:
                    print(f"  ERROR: Could not parse questions data: {e}")
                    print(f"  Raw data sample: {questions_data[:200]}...")
            else:
                print("  No questions data!")
        
        # Check for attempt ID 6 specifically
        cursor.execute("SELECT * FROM ugc_net_practice_attempts WHERE id=6")
        attempt_6 = cursor.fetchone()
        
        if attempt_6:
            print(f"\n=== ATTEMPT 6 DETAILS ===")
            print(f"All fields: {attempt_6}")
        else:
            print(f"\n=== ATTEMPT 6 NOT FOUND ===")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    check_practice_test_data()
