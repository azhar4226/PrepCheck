                                                    #!/usr/bin/env python3
"""
Add sample questions to Computer Science chapters for testing
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

def add_sample_questions():
    """Add sample questions to Computer Science chapters"""
    
    token = get_auth_token()
    if not token:
        print("❌ Failed to authenticate")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Sample questions for different CS chapters
    sample_questions = [
        # Chapter 1: Discrete Mathematics and Graph Theory
        {
            "question_text": "What is the maximum number of edges in a simple undirected graph with n vertices?",
            "option_a": "n",
            "option_b": "n(n-1)",
            "option_c": "n(n-1)/2",
            "option_d": "2n",
            "correct_option": "C",
            "explanation": "In a simple undirected graph, the maximum number of edges is C(n,2) = n(n-1)/2.",
            "topic": "Graph Theory",
            "difficulty": "medium",
            "chapter_id": 1,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 5
        },
        {
            "question_text": "Which of the following is NOT a property of an equivalence relation?",
            "option_a": "Reflexive",
            "option_b": "Symmetric",
            "option_c": "Transitive",
            "option_d": "Antisymmetric",
            "correct_option": "D",
            "explanation": "Equivalence relations must be reflexive, symmetric, and transitive. Antisymmetric is a property of partial orders.",
            "topic": "Relations",
            "difficulty": "easy",
            "chapter_id": 1,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 4
        },
        # Chapter 2: Computer System Architecture
        {
            "question_text": "What is the primary advantage of pipelining in CPU design?",
            "option_a": "Reduces memory usage",
            "option_b": "Increases instruction throughput",
            "option_c": "Decreases power consumption",
            "option_d": "Simplifies instruction set",
            "correct_option": "B",
            "explanation": "Pipelining allows multiple instructions to be in different stages of execution simultaneously, increasing throughput.",
            "topic": "CPU Architecture",
            "difficulty": "medium",
            "chapter_id": 2,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 5
        },
        # Chapter 3: Programming and Data Structures
        {
            "question_text": "What is the time complexity of inserting an element at the beginning of a singly linked list?",
            "option_a": "O(1)",
            "option_b": "O(log n)",
            "option_c": "O(n)",
            "option_d": "O(n log n)",
            "correct_option": "A",
            "explanation": "Inserting at the beginning of a linked list only requires updating pointers, which is O(1).",
            "topic": "Linked Lists",
            "difficulty": "easy",
            "chapter_id": 3,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 4
        },
        {
            "question_text": "Which sorting algorithm has the best average-case time complexity?",
            "option_a": "Bubble Sort",
            "option_b": "Quick Sort",
            "option_c": "Merge Sort",
            "option_d": "Insertion Sort",
            "correct_option": "C",
            "explanation": "Merge Sort has O(n log n) time complexity in all cases, while Quick Sort has O(n²) worst case.",
            "topic": "Sorting Algorithms",
            "difficulty": "medium",
            "chapter_id": 3,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 5
        },
        # Chapter 4: Database Systems
        {
            "question_text": "Which normal form eliminates transitive dependencies?",
            "option_a": "1NF",
            "option_b": "2NF",
            "option_c": "3NF",
            "option_d": "BCNF",
            "correct_option": "C",
            "explanation": "Third Normal Form (3NF) eliminates transitive dependencies between non-key attributes.",
            "topic": "Database Normalization",
            "difficulty": "medium",
            "chapter_id": 4,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 5
        },
        # Chapter 5: Computer Networks
        {
            "question_text": "Which layer of the OSI model is responsible for routing?",
            "option_a": "Physical Layer",
            "option_b": "Data Link Layer",
            "option_c": "Network Layer",
            "option_d": "Transport Layer",
            "correct_option": "C",
            "explanation": "The Network Layer (Layer 3) is responsible for routing packets between different networks.",
            "topic": "OSI Model",
            "difficulty": "easy",
            "chapter_id": 5,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 4
        },
        # Chapter 6: Operating Systems
        {
            "question_text": "What is the main purpose of virtual memory?",
            "option_a": "Increase CPU speed",
            "option_b": "Provide more physical RAM",
            "option_c": "Allow programs larger than physical memory to run",
            "option_d": "Improve network performance",
            "correct_option": "C",
            "explanation": "Virtual memory allows programs to use more memory than physically available by using disk storage as extended memory.",
            "topic": "Memory Management",
            "difficulty": "medium",
            "chapter_id": 6,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 5
        },
        # Chapter 7: Software Engineering
        {
            "question_text": "Which software development model involves iterative development with frequent releases?",
            "option_a": "Waterfall Model",
            "option_b": "Spiral Model",
            "option_c": "Agile Model",
            "option_d": "V-Model",
            "correct_option": "C",
            "explanation": "Agile methodology emphasizes iterative development with frequent releases and customer feedback.",
            "topic": "Software Development Models",
            "difficulty": "easy",
            "chapter_id": 7,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 4
        },
        # Chapter 8: Web Technologies
        {
            "question_text": "Which HTTP method is idempotent?",
            "option_a": "POST",
            "option_b": "PUT",
            "option_c": "PATCH",
            "option_d": "All of the above",
            "correct_option": "B",
            "explanation": "PUT is idempotent - making the same request multiple times has the same effect as making it once.",
            "topic": "HTTP Methods",
            "difficulty": "medium",
            "chapter_id": 8,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 5
        },
        # Chapter 9: Theory of Computation
        {
            "question_text": "Which type of grammar generates context-free languages?",
            "option_a": "Type 0",
            "option_b": "Type 1",
            "option_c": "Type 2",
            "option_d": "Type 3",
            "correct_option": "C",
            "explanation": "Type 2 grammars (context-free grammars) generate context-free languages according to Chomsky hierarchy.",
            "topic": "Formal Languages",
            "difficulty": "hard",
            "chapter_id": 9,
            "paper_type": "paper2",
            "source": "manual",
            "marks": 2,
            "weightage": 6
        }
    ]
    
    print(f"🚀 Adding {len(sample_questions)} sample questions to Computer Science chapters...")
    
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
    add_sample_questions()
