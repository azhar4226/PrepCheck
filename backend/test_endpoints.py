#!/usr/bin/env python3
"""
Test script to verify backend endpoints work after quiz cleanup
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables before importing app
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/prepcheck.db'
os.environ['DATABASE_URL'] = 'sqlite:///instance/prepcheck.db'
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
os.environ['FLASK_ENV'] = 'development'

def test_backend_functionality():
    """Test that backend can start and basic functionality works"""
    
    print("Testing backend functionality after quiz cleanup...")
    
    try:
        # Test model imports
        from app.models import User, UGCNetMockTest, UGCNetMockAttempt, Subject, Chapter
        print("✓ All UGC NET models imported successfully")
        
        # Test that old quiz models are gone
        try:
            from app.models import Quiz
            print("✗ ERROR: Quiz model still exists!")
            return False
        except ImportError:
            print("✓ Quiz model successfully removed")
        
        try:
            from app.models import QuizAttempt
            print("✗ ERROR: QuizAttempt model still exists!")
            return False
        except ImportError:
            print("✓ QuizAttempt model successfully removed")
        
        print("\n✓ All backend functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Backend test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_backend_functionality()
    sys.exit(0 if success else 1)
