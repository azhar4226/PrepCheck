#!/usr/bin/env python3
"""
Add NEW sample questions to Computer Science chapters for testing (modified to avoid duplicates)
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_EMAIL = "admin@prepcheck.com"
ADMIN_PASSWORD = "admin123"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"Authentication failed: {response.text}")
        return None

def add_new_questions():
    """Add new unique questions to Computer Science chapters"""
    
    token = get_auth_token()
    if not token:
        print("❌ Failed to authenticate")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # NEW sample questions with different content to avoid hash collision
    sample_questions = [
        # Chapter 1: Discrete Mathematics
        {
            "question_text": "In a complete graph with 5 vertices, how many edges are there?",
            "option_a": "5",
            "option_b": "10",
            "option_c": "15",
            "option_d": "20",
            "correct_option": "B",
            "explanation": "A complete graph with n vertices has n(n-1)/2 edges. For n=5: 5×4/2 = 10 edges.",
            "topic": "Graph Theory Basics",
            "difficulty": "easy",
            "chapter_id": 1,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 5
        },
        # Chapter 2: System Architecture
        {
            "question_text": "Which memory hierarchy level is typically the fastest?",
            "option_a": "Main Memory",
            "option_b": "Cache Memory",
            "option_c": "Secondary Storage",
            "option_d": "Virtual Memory",
            "correct_option": "B",
            "explanation": "Cache memory is the fastest memory in the hierarchy, closer to the CPU than main memory.",
            "topic": "Memory Hierarchy",
            "difficulty": "easy",
            "chapter_id": 2,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 5
        },
        # Chapter 3: Programming
        {
            "question_text": "What is the worst-case time complexity of Quick Sort?",
            "option_a": "O(n)",
            "option_b": "O(n log n)",
            "option_c": "O(n²)",
            "option_d": "O(2ⁿ)",
            "correct_option": "C",
            "explanation": "Quick Sort has O(n²) worst-case time complexity when the pivot is always the smallest or largest element.",
            "topic": "Sorting Complexity",
            "difficulty": "medium",
            "chapter_id": 3,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 5
        },
        # Chapter 4: Database
        {
            "question_text": "What does ACID stand for in database systems?",
            "option_a": "Atomicity, Consistency, Isolation, Durability",
            "option_b": "Accuracy, Completeness, Integrity, Dependability",
            "option_c": "Authorization, Confidentiality, Integrity, Data",
            "option_d": "Association, Clustering, Indexing, Distribution",
            "correct_option": "A",
            "explanation": "ACID represents the four key properties that guarantee database transactions are processed reliably.",
            "topic": "Database Transactions",
            "difficulty": "easy",
            "chapter_id": 4,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 5
        },
        # Chapter 5: Networks
        {
            "question_text": "What is the default port number for HTTP?",
            "option_a": "21",
            "option_b": "23",
            "option_c": "80",
            "option_d": "443",
            "correct_option": "C",
            "explanation": "HTTP uses port 80 by default, while HTTPS uses port 443.",
            "topic": "Network Protocols",
            "difficulty": "easy",
            "chapter_id": 5,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 4
        }
    ]
    
    print(f"🚀 Adding {len(sample_questions)} NEW questions to Computer Science chapters...")
    
    success_count = 0
    for i, question in enumerate(sample_questions):
        response = requests.post(
            f"{BASE_URL}/ugc-net/question-bank/add",
            json=question,
            headers=headers
        )
        
        if response.status_code == 201:
            data = response.json()
            question_id = data.get('question', {}).get('id')
            print(f"✅ Added question {i+1} to chapter {question['chapter_id']} (ID: {question_id})")
            success_count += 1
        else:
            print(f"❌ Failed to add question {i+1}: {response.text}")
    
    print(f"\n📊 Successfully added {success_count} out of {len(sample_questions)} questions")
    return success_count

if __name__ == "__main__":
    add_new_questions()
