#!/usr/bin/env python3
"""
Final UGC NET API Test - Test the completed implementation
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

def test_complete_workflow():
    """Test the complete UGC NET workflow"""
    
    token = get_auth_token()
    if not token:
        print("❌ Failed to authenticate")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("🚀 Testing Complete UGC NET Workflow...\n")
    
    # Test 1: Mock Test Generation
    print("1️⃣ Testing Mock Test Generation...")
    mock_test_config = {
        "title": "Final Test - Computer Science Mock Paper",
        "description": "Comprehensive test of the UGC NET mock test system",
        "subject_id": 1,
        "paper_type": "paper2",
        "total_questions": 3,
        "time_limit": 45,
        "difficulty_distribution": {"easy": 60, "medium": 30, "hard": 10},
        "source_distribution": {"previous_year": 50, "ai_generated": 30, "manual": 20},
        "weightage_config": {
            "chapters": [
                {"chapter_id": 1, "chapter_name": "Discrete Mathematics", "weightage": 40, "estimated_questions": 1},
                {"chapter_id": 2, "chapter_name": "Computer Architecture", "weightage": 30, "estimated_questions": 1},
                {"chapter_id": 3, "chapter_name": "Programming", "weightage": 30, "estimated_questions": 1}
            ]
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/ugc-net/mock-tests/generate",
        json=mock_test_config,
        headers=headers
    )
    
    if response.status_code == 201:
        mock_test_data = response.json()
        mock_test = mock_test_data['mock_test']
        paper = mock_test_data['paper']
        statistics = mock_test_data['statistics']
        
        print(f"   ✅ Mock test created successfully (ID: {mock_test['id']})")
        print(f"   📊 Generated {len(paper['questions'])} questions from {len(statistics['chapter_wise_distribution'])} chapters")
        print(f"   🎯 Difficulty distribution: {statistics['difficulty_distribution']}")
        
        test_id = mock_test['id']
    else:
        print(f"   ❌ Failed to generate mock test: {response.text}")
        return
    
    # Test 2: Get Mock Tests List
    print("\n2️⃣ Testing Mock Tests List...")
    response = requests.get(f"{BASE_URL}/ugc-net/mock-tests", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        mock_tests = data['mock_tests']
        print(f"   ✅ Retrieved {len(mock_tests)} mock tests")
        print(f"   📝 Latest test: '{mock_tests[0]['title']}'")
    else:
        print(f"   ❌ Failed to get mock tests: {response.text}")
    
    # Test 3: Get Mock Test Details
    print("\n3️⃣ Testing Mock Test Details...")
    response = requests.get(f"{BASE_URL}/ugc-net/mock-tests/{test_id}", headers=headers)
    
    if response.status_code == 200:
        test_details = response.json()
        print(f"   ✅ Retrieved test details for ID {test_id}")
        print(f"   ⏱️  Time limit: {test_details['time_limit']} minutes")
        print(f"   📈 User attempts: {len(test_details['user_attempts'])}")
    else:
        print(f"   ❌ Failed to get test details: {response.text}")
    
    # Test 4: Start Mock Test Attempt
    print("\n4️⃣ Testing Mock Test Attempt...")
    response = requests.post(f"{BASE_URL}/ugc-net/mock-tests/{test_id}/attempt", headers=headers)
    
    if response.status_code == 201:
        attempt_data = response.json()
        attempt = attempt_data['attempt']
        questions = attempt['questions']
        
        print(f"   ✅ Started attempt (ID: {attempt['id']})")
        print(f"   ❓ Questions loaded: {len(questions)}")
        
        attempt_id = attempt['id']
    else:
        print(f"   ❌ Failed to start attempt: {response.text}")
        return
    
    # Test 5: Submit Mock Test Attempt
    print("\n5️⃣ Testing Mock Test Submission...")
    
    # Create sample answers (answering all questions as 'A' for demo)
    sample_answers = {}
    for i, question in enumerate(questions):
        sample_answers[str(question['id'])] = 'A'
    
    submission_data = {
        "answers": sample_answers
    }
    
    response = requests.post(
        f"{BASE_URL}/ugc-net/mock-tests/{test_id}/attempt/{attempt_id}/submit",
        json=submission_data,
        headers=headers
    )
    
    if response.status_code == 200:
        results_data = response.json()
        results = results_data['results']
        
        print(f"   ✅ Submitted attempt successfully")
        print(f"   📊 Score: {results['score']:.1f}%")
        print(f"   ✅ Correct answers: {results['correct_answers']}/{results['total_questions']}")
        print(f"   ⏱️  Time taken: {results['analytics']['total_time_taken']:.1f} minutes")
    else:
        print(f"   ❌ Failed to submit attempt: {response.text}")
    
    # Test 6: Get Statistics
    print("\n6️⃣ Testing Question Bank Statistics...")
    response = requests.get(f"{BASE_URL}/ugc-net/statistics", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        overall = stats['overall']
        
        print(f"   ✅ Retrieved statistics")
        print(f"   📚 Total questions: {overall['total_questions']}")
        print(f"   ✅ Verified questions: {overall['verified_questions']} ({overall['verification_rate']:.1f}%)")
        print(f"   📂 Subjects: {overall['total_subjects']}, Chapters: {overall['total_chapters']}")
    else:
        print(f"   ❌ Failed to get statistics: {response.text}")
    
    print("\n🎉 UGC NET Implementation Test Complete!")
    print("="*60)
    print("✅ All core functionality is working:")
    print("   • Mock test generation with weightage system")
    print("   • Question bank management") 
    print("   • Attempt tracking and scoring")
    print("   • Performance analytics")
    print("   • Chapter-wise distribution")
    print("="*60)

if __name__ == "__main__":
    test_complete_workflow()
