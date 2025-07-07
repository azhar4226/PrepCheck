#!/usr/bin/env python3
"""Test script to verify modular UGC NET controllers can be imported"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, '/Users/apple/Desktop/PrepCheck/backend')

def test_modular_imports():
    """Test that all modular controllers can be imported"""
    try:
        # Test individual controller imports
        print("Testing individual controller imports...")
        
        from app.controllers.ugc_net.subject_controller import ugc_net_subject_bp
        print("✅ Subject controller imported successfully")
        
        from app.controllers.ugc_net.question_controller import ugc_net_question_bp
        print("✅ Question controller imported successfully")
        
        from app.controllers.ugc_net.mock_test_controller import ugc_net_mock_bp
        print("✅ Mock test controller imported successfully")
        
        from app.controllers.ugc_net.practice_test_controller import ugc_net_practice_bp
        print("✅ Practice test controller imported successfully")
        
        # Test main modular import
        print("\nTesting main modular import...")
        from app.controllers.ugc_net import register_ugc_net_blueprints
        print("✅ Main modular function imported successfully")
        
        print("\n🎉 All modular UGC NET controllers imported successfully!")
        print("📁 Controller structure:")
        print("   - subject_controller.py (subjects, chapters, statistics, admin)")
        print("   - question_controller.py (question bank management)")
        print("   - mock_test_controller.py (mock test generation and attempts)")
        print("   - practice_test_controller.py (practice tests with auto-save)")
        print("   - __init__.py (main coordinator)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

if __name__ == "__main__":
    success = test_modular_imports()
    sys.exit(0 if success else 1)
