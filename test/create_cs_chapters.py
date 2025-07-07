#!/usr/bin/env python3
"""
Script to create UGC NET Computer Science chapters via API
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MDI1MzgyMCwianRpIjoiYjEzNWU2YjYtNjFmNC00NDlkLThmNTctOTAzYTIxYTM1YzhkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NTAyNTM4MjAsImV4cCI6MTc1MDM0MDIyMH0.mEWDvAQNehy0BB_alEEdGgTaMIKJEXa0v47sCkAr5HY"

def create_chapters_for_subject(subject_id, token):
    """Create all chapters for Computer Science subject"""
    
    chapters_data = [
        {
            "name": "Programming and Data Structures",
            "weightage_paper2": 10,
            "description": "Programming fundamentals, Arrays, Linked Lists, Stacks, Queues, Trees, Graphs",
            "chapter_order": 2,
            "estimated_questions_paper2": 5
        },
        {
            "name": "Computer Organization and Architecture", 
            "weightage_paper2": 8,
            "description": "Machine instructions, CPU architecture, Memory organization, I/O systems",
            "chapter_order": 3,
            "estimated_questions_paper2": 4
        },
        {
            "name": "Theory of Computation",
            "weightage_paper2": 8,
            "description": "Finite Automata, Context-free grammars, Turing machines, Computability",
            "chapter_order": 4,
            "estimated_questions_paper2": 4
        },
        {
            "name": "Compiler Design",
            "weightage_paper2": 6,
            "description": "Lexical analysis, Syntax analysis, Semantic analysis, Code generation",
            "chapter_order": 5,
            "estimated_questions_paper2": 3
        },
        {
            "name": "Operating System",
            "weightage_paper2": 8,
            "description": "Process management, Memory management, File systems, I/O management",
            "chapter_order": 6,
            "estimated_questions_paper2": 4
        },
        {
            "name": "Database Management System",
            "weightage_paper2": 8,
            "description": "ER model, Relational model, SQL, Normalization, Transaction management",
            "chapter_order": 7,
            "estimated_questions_paper2": 4
        },
        {
            "name": "Computer Networks",
            "weightage_paper2": 8,
            "description": "Network protocols, OSI model, TCP/IP, Routing, Network security",
            "chapter_order": 8,
            "estimated_questions_paper2": 4
        },
        {
            "name": "Web Technology",
            "weightage_paper2": 6,
            "description": "HTML, CSS, JavaScript, Web servers, Web protocols",
            "chapter_order": 9,
            "estimated_questions_paper2": 3
        }
    ]
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    created_chapters = []
    for chapter_data in chapters_data:
        response = requests.post(
            f"{BASE_URL}/ugc-net/admin/subjects/{subject_id}/chapters",
            json=chapter_data,
            headers=headers
        )
        
        if response.status_code == 201:
            result = response.json()
            created_chapters.append(result['chapter'])
            print(f"✅ Created chapter: {chapter_data['name']} (ID: {result['chapter']['id']})")
        else:
            print(f"❌ Failed to create chapter {chapter_data['name']}: {response.text}")
    
    return created_chapters

def main():
    """Main function to create chapters"""
    
    # Subject already exists with ID 1, so just create chapters
    subject_id = 1
    
    print(f"Creating chapters for subject ID: {subject_id}")
    chapters = create_chapters_for_subject(subject_id, ADMIN_TOKEN)
    
    if chapters:
        print(f"\n✅ Successfully created {len(chapters)} chapters!")
        print("\nChapter Summary:")
        total_weightage = 0
        for chapter in chapters:
            print(f"- {chapter['name']} (ID: {chapter['id']}, Weightage: {chapter['weightage_paper2']})")
            total_weightage += chapter['weightage_paper2']
        
        print(f"\nTotal weightage: {total_weightage}%")
    else:
        print("❌ No chapters were created")

if __name__ == "__main__":
    main()
