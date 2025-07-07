#!/usr/bin/env python3
"""
Simple test to check qualification status via API calls
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
UGC_NET_URL = f"{BASE_URL}/ugc-net"

def main():
    print("=== Testing Qualification Status via API ===")
    
    # Test login
    login_data = {
        "email": "student1@test.com",
        "password": "password123"
    }
    
    print("1. Logging in...")
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Login successful")
    
    # Get tests
    print("\n2. Getting available tests...")
    response = requests.get(f"{UGC_NET_URL}/mock-tests", headers=headers)
    if response.status_code != 200:
        print(f"Failed to get tests: {response.text}")
        return
    
    tests = response.json().get('mock_tests', [])
    if not tests:
        print("No tests available")
        return
    
    test_id = tests[0]['id']
    print(f"✓ Using test ID: {test_id}")
    
    # Get existing attempts
    print("\n3. Checking existing attempts...")
    response = requests.get(f"{UGC_NET_URL}/mock-tests/{test_id}/attempts", headers=headers)
    if response.status_code == 200:
        attempts = response.json().get('attempts', [])
        print(f"Found {len(attempts)} existing attempts:")
        for attempt in attempts:
            status = attempt.get('status', 'unknown')
            score = attempt.get('score', 'N/A')
            percentage = attempt.get('percentage', 'N/A')
            qual_status = attempt.get('qualification_status', 'N/A')
            print(f"  Attempt {attempt['id']}: {status}, score={score}, percentage={percentage}%, qualification={qual_status}")
    
    # Start new attempt
    print(f"\n4. Starting new test attempt...")
    response = requests.post(f"{UGC_NET_URL}/mock-tests/{test_id}/start", headers=headers)
    if response.status_code != 200:
        print(f"Failed to start attempt: {response.text}")
        return
    
    attempt_data = response.json()['attempt']
    attempt_id = attempt_data['id']
    print(f"✓ Started attempt ID: {attempt_id}")
    
    # Get questions
    print("\n5. Getting test questions...")
    response = requests.get(f"{UGC_NET_URL}/mock-tests/{test_id}/attempt/{attempt_id}", headers=headers)
    if response.status_code != 200:
        print(f"Failed to get attempt: {response.text}")
        return
    
    attempt_info = response.json()['attempt']
    questions = attempt_info['questions']
    print(f"✓ Test has {len(questions)} questions")
    
    # Submit with high score (answer all correctly)
    print("\n6. Submitting test with all correct answers...")
    answers = {}
    for question in questions:
        correct_option = question.get('correct_option', 'A')
        answers[str(question['id'])] = correct_option
    
    submit_data = {"answers": answers}
    response = requests.post(f"{UGC_NET_URL}/mock-tests/{test_id}/attempt/{attempt_id}/submit", 
                           headers=headers, json=submit_data)
    
    if response.status_code != 200:
        print(f"Failed to submit test: {response.text}")
        return
    
    result = response.json()
    attempt = result.get('attempt', {})
    
    print("✓ Test submitted successfully!")
    print(f"\nRESULTS:")
    print(f"  Score: {attempt.get('score', 'N/A')}")
    print(f"  Total Marks: {attempt.get('total_marks', 'N/A')}")
    print(f"  Percentage: {attempt.get('percentage', 'N/A')}%")
    print(f"  Correct Answers: {attempt.get('correct_answers', 'N/A')} / {attempt.get('total_questions', 'N/A')}")
    print(f"  Qualification Status: {attempt.get('qualification_status', 'N/A')}")
    
    # Expected: 100% score should result in 'qualified' status
    percentage = attempt.get('percentage', 0)
    qual_status = attempt.get('qualification_status', 'unknown')
    
    print(f"\nANALYSIS:")
    if percentage >= 60 and qual_status == 'qualified':
        print("✓ Qualification status is CORRECT!")
    elif percentage >= 60 and qual_status != 'qualified':
        print(f"❌ BUG FOUND: {percentage}% should be 'qualified' but got '{qual_status}'")
    elif percentage < 60:
        print(f"⚠️  Low score ({percentage}%) - expected for testing")
    
    print(f"\nFull response:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
