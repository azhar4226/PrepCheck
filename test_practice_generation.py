#!/usr/bin/env python3
"""Test script to debug practice test question generation"""

import sys
import os
import json

# Add the backend directory to Python path
sys.path.insert(0, '/Users/apple/Desktop/PrepCheck/backend')

def test_practice_test_generation():
    """Test practice test generation and see what's happening with questions"""
    try:
        # Import required modules
        from app.services.ugc_net_paper_generator import UGCNetPaperGenerator
        from app.models.models import Subject, Chapter, QuestionBank
        
        print("Testing practice test generation...")
        
        # Mock configuration
        config = {
            'subject_id': 1,  # Assuming there's a subject with ID 1
            'paper_type': 'paper2',
            'practice_type': 'chapter_wise',
            'total_questions': 10,
            'chapter_ids': [1, 2],  # Assuming there are chapters with IDs 1 and 2
            'difficulty_distribution': {
                'easy': 30,
                'medium': 50,
                'hard': 20
            },
            'source_distribution': {
                'previous_year': 70,
                'ai_generated': 30
            }
        }
        
        print(f"Config: {json.dumps(config, indent=2)}")
        
        # Generate practice test
        generator = UGCNetPaperGenerator()
        result = generator.generate_practice_test(config)
        
        print(f"Generation result success: {result.get('success', False)}")
        
        if not result.get('success', False):
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
        
        # Check the practice test data
        practice_test_data = result.get('practice_test', {})
        questions = practice_test_data.get('questions', [])
        
        print(f"Generated questions count: {len(questions)}")
        
        if questions:
            print("First question sample:")
            first_question = questions[0]
            print(f"  ID: {first_question.get('id', 'N/A')}")
            print(f"  Text: {first_question.get('question_text', 'N/A')[:100]}...")
            print(f"  Options: {first_question.get('options', 'N/A')}")
            print(f"  Chapter: {first_question.get('chapter_name', 'N/A')}")
        else:
            print("❌ No questions generated!")
            
        print(f"Statistics: {result.get('statistics', {})}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_practice_test_generation()
    sys.exit(0 if success else 1)
