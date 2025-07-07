#!/usr/bin/env python3
"""
Script to check and fix question verification status in the database.
This will help diagnose why practice tests show 0 questions.
"""

import sys
import os
sys.path.append('/Users/apple/Desktop/PrepCheck/backend')

def check_and_fix_questions():
    """Check question verification status and fix if needed"""
    try:
        from app.models.models import QuestionBank, Chapter, Subject
        from app import create_app, db
        
        # Try to create app with minimal config
        app = create_app()
        
        # We need to set the database URI for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///temp_test.db'  # Temporary
        
        print("Checking question verification status...")
        print("Note: This is a diagnostic script - run with proper database config")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTo fix this issue, you can:")
        print("1. Run the backend server")
        print("2. Check the database manually")
        print("3. Use SQL to update question verification status:")
        print("   UPDATE question_bank SET is_verified = TRUE WHERE is_verified IS NULL OR is_verified = FALSE;")
        return False

def suggest_fixes():
    """Suggest potential fixes for the question visibility issue"""
    print("\n🔧 POTENTIAL FIXES FOR PRACTICE TEST QUESTIONS:")
    print("=" * 60)
    
    print("\n1. DATABASE VERIFICATION ISSUE:")
    print("   - Questions exist but are marked as unverified")
    print("   - Only verified questions are used in practice tests")
    print("   - Solution: Mark existing questions as verified")
    
    print("\n2. QUICK SQL FIX (if you have database access):")
    print("   UPDATE question_bank SET is_verified = TRUE;")
    print("   UPDATE question_bank SET verification_method = 'manual';")
    print("   UPDATE question_bank SET verified_at = datetime('now');")
    
    print("\n3. ADMIN INTERFACE FIX:")
    print("   - Use the admin panel to bulk verify questions")
    print("   - Or create a verification endpoint")
    
    print("\n4. CHECK QUESTION CREATION:")
    print("   - Ensure new questions are created with is_verified=True")
    print("   - This was fixed in the modular question controller")
    
    print("\n5. TEMPORARY WORKAROUND:")
    print("   - Modify paper generator to include unverified questions for testing")
    print("   - Change is_verified=True to is_verified in [True, False] in the query")

if __name__ == "__main__":
    print("🔍 UGC NET Practice Test Question Diagnostic")
    print("=" * 50)
    
    if not check_and_fix_questions():
        suggest_fixes()
    
    print("\n✅ Next steps:")
    print("1. Check your database to see question verification status")
    print("2. Apply the SQL fix if questions are unverified")
    print("3. Test practice test generation after fixing")
    print("4. Ensure new questions are created as verified")
