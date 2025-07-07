#!/usr/bin/env python3

"""
Debug script to check qualification status calculation in UGC NET test attempts
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app import create_app, db
    from app.models import UGCNetMockAttempt, User, UGCNetMockTest
    from sqlalchemy import desc
    
    app = create_app()
    with app.app_context():
        print("🔍 Debugging UGC NET Qualification Status")
        print("=" * 50)
        
        # Get all completed attempts
        attempts = UGCNetMockAttempt.query.filter_by(status='completed').order_by(desc(UGCNetMockAttempt.id)).limit(10).all()
        
        if not attempts:
            print("❌ No completed attempts found")
        else:
            print(f"✅ Found {len(attempts)} completed attempts")
            print()
            
            for i, attempt in enumerate(attempts):
                user = User.query.get(attempt.user_id)
                mock_test = UGCNetMockTest.query.get(attempt.mock_test_id)
                
                print(f"Attempt #{i+1} (ID: {attempt.id})")
                print(f"  User: {user.email if user else 'Unknown'}")
                print(f"  Test: {mock_test.title if mock_test else 'Unknown'}")
                print(f"  Score: {attempt.score}/{attempt.total_marks}")
                print(f"  Percentage: {attempt.percentage}%")
                print(f"  Qualification Status: {attempt.qualification_status}")
                
                # Check if qualification status should be updated
                expected_status = 'not_qualified'
                if attempt.percentage >= 60:
                    expected_status = 'qualified'
                elif attempt.percentage >= 40:
                    expected_status = 'borderline'
                
                if attempt.qualification_status != expected_status:
                    print(f"  ⚠️  MISMATCH: Expected '{expected_status}', got '{attempt.qualification_status}'")
                    
                    # Update the qualification status
                    attempt.qualification_status = expected_status
                    print(f"  ✅ Updated to '{expected_status}'")
                else:
                    print(f"  ✅ Status is correct")
                
                print()
            
            # Commit any changes
            db.session.commit()
            print("💾 Database updated")
            
        # Also check for any in_progress attempts that might be hanging
        hanging_attempts = UGCNetMockAttempt.query.filter_by(status='in_progress').all()
        if hanging_attempts:
            print(f"\n⚠️  Found {len(hanging_attempts)} hanging 'in_progress' attempts")
            for attempt in hanging_attempts:
                print(f"  - Attempt {attempt.id} started at {attempt.start_time}")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the PrepCheck directory and dependencies are installed")
except Exception as e:
    print(f"❌ Error: {e}")
