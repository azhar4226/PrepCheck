#!/usr/bin/env python3
"""
UGC NET API Test Script
Tests all the new UGC NET endpoints for functionality
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_EMAIL = "admin@prepcheck.com"
ADMIN_PASSWORD = "admin123"

class UGCNetAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
    
    def log_test(self, test_name, success, message="", data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'data': data
        })
        print(f"{status} {test_name}: {message}")
    
    def authenticate(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                json={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}',
                    'Content-Type': 'application/json'
                })
                self.log_test("Authentication", True, "Successfully authenticated as admin")
                return True
            else:
                self.log_test("Authentication", False, f"Failed to authenticate: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_get_subjects(self):
        """Test getting UGC NET subjects"""
        try:
            response = self.session.get(f"{BASE_URL}/ugc-net/subjects")
            
            if response.status_code == 200:
                data = response.json()
                subjects = data.get('subjects', [])
                self.log_test(
                    "Get UGC NET Subjects", 
                    True, 
                    f"Retrieved {len(subjects)} subjects", 
                    {'subject_count': len(subjects)}
                )
                return subjects
            else:
                self.log_test("Get UGC NET Subjects", False, f"Failed: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Get UGC NET Subjects", False, f"Error: {str(e)}")
            return []
    
    def test_get_subject_chapters(self, subject_id):
        """Test getting chapters for a subject"""
        try:
            response = self.session.get(
                f"{BASE_URL}/ugc-net/subjects/{subject_id}/chapters",
                params={'paper_type': 'paper2'}
            )
            
            if response.status_code == 200:
                data = response.json()
                chapters = data.get('chapters', [])
                self.log_test(
                    "Get Subject Chapters", 
                    True, 
                    f"Retrieved {len(chapters)} chapters for subject {subject_id}", 
                    {'chapter_count': len(chapters)}
                )
                return chapters
            else:
                self.log_test("Get Subject Chapters", False, f"Failed: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Get Subject Chapters", False, f"Error: {str(e)}")
            return []
    
    def test_add_question(self, chapter_id):
        """Test adding a question to the question bank"""
        try:
            question_data = {
                "question_text": "What is the primary function of the CPU in a computer system?",
                "option_a": "To store data permanently",
                "option_b": "To execute instructions and perform calculations",
                "option_c": "To provide network connectivity",
                "option_d": "To display output to the user",
                "correct_option": "B",
                "explanation": "The CPU (Central Processing Unit) is responsible for executing instructions and performing calculations.",
                "topic": "Computer Architecture",
                "difficulty": "easy",
                "chapter_id": chapter_id,
                "paper_type": "paper2",
                "year": 2024,
                "session": "December",
                "source": "manual",
                "marks": 1,
                "weightage": 5,
                "tags": ["cpu", "computer-architecture", "basics"]
            }
            
            response = self.session.post(
                f"{BASE_URL}/ugc-net/question-bank/add",
                json=question_data
            )
            
            if response.status_code == 201:
                data = response.json()
                question = data.get('question', {})
                self.log_test(
                    "Add Question to Bank", 
                    True, 
                    f"Successfully added question with ID {question.get('id')}", 
                    {'question_id': question.get('id')}
                )
                return question
            else:
                self.log_test("Add Question to Bank", False, f"Failed: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Add Question to Bank", False, f"Error: {str(e)}")
            return None
    
    def test_get_statistics(self):
        """Test getting question bank statistics"""
        try:
            response = self.session.get(f"{BASE_URL}/ugc-net/statistics")
            
            if response.status_code == 200:
                data = response.json()
                overall = data.get('overall', {})
                self.log_test(
                    "Get Statistics", 
                    True, 
                    f"Retrieved statistics: {overall.get('total_questions', 0)} total questions", 
                    data
                )
                return data
            else:
                self.log_test("Get Statistics", False, f"Failed: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Get Statistics", False, f"Error: {str(e)}")
            return None
    
    def test_generate_mock_test(self, subject_id):
        """Test generating a mock test"""
        try:
            config = {
                "title": "Test Mock Paper - Computer Science",
                "description": "Generated test mock paper for Computer Science",
                "subject_id": subject_id,
                "paper_type": "paper2",
                "total_questions": 5,  # Small number for testing
                "time_limit": 30,  # 30 minutes
                "difficulty_distribution": {
                    "easy": 40,
                    "medium": 40,
                    "hard": 20
                },
                "source_distribution": {
                    "previous_year": 50,
                    "ai_generated": 30,
                    "manual": 20
                }
            }
            
            response = self.session.post(
                f"{BASE_URL}/ugc-net/mock-tests/generate",
                json=config
            )
            
            if response.status_code == 201:
                data = response.json()
                mock_test = data.get('mock_test', {})
                self.log_test(
                    "Generate Mock Test", 
                    True, 
                    f"Successfully generated mock test with ID {mock_test.get('id')}", 
                    {'mock_test_id': mock_test.get('id')}
                )
                return mock_test
            else:
                self.log_test("Generate Mock Test", False, f"Failed: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Generate Mock Test", False, f"Error: {str(e)}")
            return None
    
    def test_get_mock_tests(self):
        """Test getting available mock tests"""
        try:
            response = self.session.get(f"{BASE_URL}/ugc-net/mock-tests")
            
            if response.status_code == 200:
                data = response.json()
                mock_tests = data.get('mock_tests', [])
                self.log_test(
                    "Get Mock Tests", 
                    True, 
                    f"Retrieved {len(mock_tests)} mock tests", 
                    {'mock_test_count': len(mock_tests)}
                )
                return mock_tests
            else:
                self.log_test("Get Mock Tests", False, f"Failed: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Get Mock Tests", False, f"Error: {str(e)}")
            return []
    
    def test_start_mock_test_attempt(self, test_id):
        """Test starting a mock test attempt"""
        try:
            response = self.session.post(f"{BASE_URL}/ugc-net/mock-tests/{test_id}/attempt")
            
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                attempt = data.get('attempt', {})
                self.log_test(
                    "Start Mock Test Attempt", 
                    True, 
                    f"Started attempt with ID {attempt.get('id')}", 
                    {'attempt_id': attempt.get('id')}
                )
                return attempt
            else:
                self.log_test("Start Mock Test Attempt", False, f"Failed: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Start Mock Test Attempt", False, f"Error: {str(e)}")
            return None
    
    def test_bulk_import(self, chapter_id):
        """Test bulk import of questions"""
        try:
            questions_data = [
                {
                    "question_text": "What is the binary representation of decimal 10?",
                    "option_a": "1010",
                    "option_b": "1100",
                    "option_c": "1001",
                    "option_d": "1110",
                    "correct_option": "A",
                    "explanation": "10 in decimal equals 1010 in binary (8+2=10).",
                    "topic": "Number Systems",
                    "difficulty": "medium",
                    "chapter_id": chapter_id,
                    "paper_type": "paper2",
                    "source": "bulk_import",
                    "marks": 1,
                    "weightage": 5
                },
                {
                    "question_text": "Which of the following is NOT a programming paradigm?",
                    "option_a": "Object-oriented",
                    "option_b": "Functional",
                    "option_c": "Procedural",
                    "option_d": "Sequential",
                    "correct_option": "D",
                    "explanation": "Sequential is not a programming paradigm; it's a processing order.",
                    "topic": "Programming Concepts",
                    "difficulty": "easy",
                    "chapter_id": chapter_id,
                    "paper_type": "paper2",
                    "source": "bulk_import",
                    "marks": 1,
                    "weightage": 4
                }
            ]
            
            response = self.session.post(
                f"{BASE_URL}/ugc-net/question-bank/bulk-import",
                json={"questions": questions_data}
            )
            
            if response.status_code == 200:
                data = response.json()
                imported_count = data.get('imported_count', 0)
                self.log_test(
                    "Bulk Import Questions", 
                    True, 
                    f"Successfully imported {imported_count} questions", 
                    data
                )
                return data
            else:
                self.log_test("Bulk Import Questions", False, f"Failed: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Bulk Import Questions", False, f"Error: {str(e)}")
            return None
    
    def run_all_tests(self):
        """Run all UGC NET API tests"""
        print("🚀 Starting UGC NET API Tests...\n")
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Step 2: Get subjects
        subjects = self.test_get_subjects()
        if not subjects:
            print("❌ No subjects found. Cannot proceed with chapter/question tests.")
            return
        
        # Use first Paper 2 subject for testing (skip Paper 1 subjects)
        test_subject = None
        for subject in subjects:
            if subject.get('paper_type') == 'paper2' and subject.get('weightage_info', {}).get('chapters'):
                test_subject = subject
                break
        
        if not test_subject:
            print("❌ No Paper 2 subjects found with chapters. Cannot proceed with mock test generation.")
            test_subject = subjects[0]  # Use first subject for other tests
        
        subject_id = test_subject['id']
        
        # Step 3: Get chapters for the subject
        chapters = self.test_get_subject_chapters(subject_id)
        if not chapters:
            print("❌ No chapters found. Cannot proceed with question tests.")
            return
        
        # Use first chapter for testing
        test_chapter = chapters[0]
        chapter_id = test_chapter['id']
        
        # Step 4: Add a test question
        self.test_add_question(chapter_id)
        
        # Step 5: Test bulk import
        self.test_bulk_import(chapter_id)
        
        # Step 6: Get statistics
        self.test_get_statistics()
        
        # Step 7: Generate mock test (might fail if insufficient questions)
        mock_test = self.test_generate_mock_test(subject_id)
        
        # Step 8: Get mock tests
        mock_tests = self.test_get_mock_tests()
        
        # Step 9: Start mock test attempt (if we have mock tests)
        if mock_tests:
            test_mock = mock_tests[0]
            self.test_start_mock_test_attempt(test_mock['id'])
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test']}: {result['message']}")
        
        print("\n" + "="*60)


def main():
    """Main function to run the tests"""
    tester = UGCNetAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
