#!/usr/bin/env python3
"""
Comprehensive test of UGC NET weightage system with different configurations
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MDI1MzgyMCwianRpIjoiYjEzNWU2YjYtNjFmNC00NDlkLThmNTctOTAzYTIxYTM1YzhkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NTAyNTM4MjAsImV4cCI6MTc1MDM0MDIyMH0.mEWDvAQNehy0BB_alEEdGgTaMIKJEXa0v47sCkAr5HY"

def test_weightage_system():
    """Test the weightage-based question generation system"""
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}", "Content-Type": "application/json"}
    
    print("🧪 Testing UGC NET Weightage System...")
    
    # Test 1: Generate mock test with custom weightage config
    print("\n1️⃣ Testing Custom Weightage Configuration...")
    
    mock_test_data = {
        "title": "Weightage Test - Programming Heavy",
        "description": "Test with emphasis on Programming and Data Structures",
        "subject_id": 1,
        "total_questions": 5,
        "time_limit": 60,
        "paper_type": "paper2",
        "weightage_config": {
            "2": 40,  # Programming and Data Structures - 40%
            "3": 20,  # Computer Organization - 20%
            "4": 15,  # Theory of Computation - 15%
            "5": 10,  # Compiler Design - 10%
            "6": 10,  # Operating System - 10%
            "7": 5    # Database - 5%
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/ugc-net/mock-tests/generate",
        json=mock_test_data,
        headers=headers
    )
    
    if response.status_code == 201:
        test_data = response.json()
        test_id = test_data['mock_test']['id']
        print(f"   ✅ Custom weightage test created (ID: {test_id})")
        print(f"   📊 Questions generated: {test_data['statistics']['total_questions']}")
        print(f"   🎯 Chapter distribution: {test_data['statistics']['chapter_wise_distribution']}")
    else:
        print(f"   ❌ Failed to create test: {response.text}")
        return
    
    # Test 2: Start attempt and check question distribution
    print("\n2️⃣ Testing Question Distribution...")
    
    response = requests.post(f"{BASE_URL}/ugc-net/mock-tests/{test_id}/attempt", headers=headers)
    
    if response.status_code == 201:
        attempt_data = response.json()
        attempt = attempt_data['attempt']
        questions = attempt['questions']
        
        print(f"   ✅ Attempt started (ID: {attempt['id']})")
        print(f"   ❓ Total questions: {len(questions)}")
        
        # Analyze question distribution by chapter
        chapter_counts = {}
        for question in questions:
            chapter_id = question.get('chapter_id')
            chapter_name = question.get('chapter_name', f'Chapter {chapter_id}')
            chapter_counts[chapter_name] = chapter_counts.get(chapter_name, 0) + 1
        
        print("   📈 Actual distribution:")
        for chapter, count in chapter_counts.items():
            percentage = (count / len(questions)) * 100
            print(f"      • {chapter}: {count} questions ({percentage:.1f}%)")
            
        attempt_id = attempt['id']
    else:
        print(f"   ❌ Failed to start attempt: {response.text}")
        return
    
    # Test 3: Test different difficulty distributions
    print("\n3️⃣ Testing Difficulty Distribution...")
    
    difficulty_test_data = {
        "title": "Difficulty Test - Hard Focus",
        "description": "Test with emphasis on hard questions",
        "subject_id": 1,
        "total_questions": 4,
        "time_limit": 45,
        "paper_type": "paper2",
        "easy_percentage": 20,
        "medium_percentage": 30,
        "hard_percentage": 50
    }
    
    response = requests.post(
        f"{BASE_URL}/ugc-net/mock-tests/generate",
        json=difficulty_test_data,
        headers=headers
    )
    
    if response.status_code == 201:
        test_data = response.json()
        print(f"   ✅ Difficulty test created (ID: {test_data['mock_test']['id']})")
        print(f"   🎯 Target distribution: Easy 20%, Medium 30%, Hard 50%")
        print(f"   📊 Actual distribution: {test_data['statistics']['difficulty_distribution']}")
    else:
        print(f"   ❌ Failed to create difficulty test: {response.text}")
    
    # Test 4: Get comprehensive statistics
    print("\n4️⃣ Testing Statistics...")
    
    response = requests.get(f"{BASE_URL}/ugc-net/statistics", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        overall = stats.get('overall', {})
        print(f"   ✅ Statistics retrieved")
        print(f"   📚 Total questions in database: {overall.get('total_questions', 0)}")
        print(f"   📂 Subjects: {overall.get('total_subjects', 0)}")
        print(f"   📖 Chapters: {overall.get('total_chapters', 0)}")
        print(f"   ✅ Verified questions: {overall.get('verified_questions', 0)} ({overall.get('verification_rate', 0)}%)")
        
        if 'difficulty_distribution' in stats:
            print(f"   🎯 Difficulty distribution: {stats['difficulty_distribution']}")
        
        if 'subject_wise' in stats:
            print("   📈 Subject-wise distribution:")
            for subject in stats['subject_wise']:
                print(f"      • {subject['subject_name']}: {subject['question_count']} questions")
    else:
        print(f"   ❌ Failed to get statistics: {response.text}")
    
    print("\n🎉 Weightage System Test Complete!")

if __name__ == "__main__":
    test_weightage_system()
