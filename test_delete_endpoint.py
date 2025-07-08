#!/usr/bin/env python3
"""Simple test to check if delete endpoints work"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password"

def test_delete_endpoints():
    session = requests.Session()
    
    print("🔍 Testing UGC NET Delete Endpoints...")
    
    # First, try to login
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    print(f"🔐 Attempting login with {TEST_EMAIL}...")
    response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        print(f"✅ Login successful, token: {token[:50]}...")
        
        # Set authorization header
        session.headers.update({'Authorization': f'Bearer {token}'})
        
        # Test delete endpoints (with non-existent IDs, just to see the response)
        print("\n🗑️ Testing mock test delete endpoint...")
        response = session.delete(f"{BASE_URL}/api/ugc-net/mock-tests/attempts/999")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        print("\n🗑️ Testing practice test delete endpoint...")
        response = session.delete(f"{BASE_URL}/api/ugc-net/practice-tests/attempts/999")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        print("💡 You may need to create a test user first or check backend status")

if __name__ == "__main__":
    test_delete_endpoints()
