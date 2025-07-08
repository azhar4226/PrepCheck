#!/usr/bin/env python3
"""
Test script to verify the delete functionality works with backend API
"""

import requests
import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

BASE_URL = "http://localhost:8000"

def test_delete_endpoints():
    """Test that the delete endpoints exist and respond correctly"""
    
    print("🔍 Testing DELETE endpoints for test attempts...")
    
    # Test endpoints without auth (should return 401 or 422)
    endpoints = [
        "/api/ugc-net/mock-tests/attempts/1",
        "/api/ugc-net/practice-tests/attempts/1"
    ]
    
    for endpoint in endpoints:
        print(f"\n📍 Testing endpoint: {endpoint}")
        
        # Test OPTIONS request first
        try:
            response = requests.options(f"{BASE_URL}{endpoint}")
            print(f"   OPTIONS status: {response.status_code}")
            print(f"   Allowed methods: {response.headers.get('Allow', 'Not specified')}")
        except Exception as e:
            print(f"   OPTIONS error: {e}")
        
        # Test DELETE request (should fail with auth error)
        try:
            response = requests.delete(f"{BASE_URL}{endpoint}")
            print(f"   DELETE status: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ Endpoint exists but requires authentication (expected)")
            elif response.status_code == 422:
                print("   ✅ Endpoint exists but requires JWT token (expected)")
            else:
                print(f"   ⚠️  Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ DELETE error: {e}")

def test_with_mock_auth():
    """Test with a mock authorization header"""
    print("\n🔍 Testing with mock authorization header...")
    
    headers = {
        "Authorization": "Bearer mock_token",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        "/api/ugc-net/mock-tests/attempts/999",
        "/api/ugc-net/practice-tests/attempts/999"
    ]
    
    for endpoint in endpoints:
        print(f"\n📍 Testing endpoint with auth: {endpoint}")
        try:
            response = requests.delete(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"   DELETE status: {response.status_code}")
            if response.status_code == 404:
                print("   ✅ Endpoint accessible but attempt not found (expected for ID 999)")
            elif response.status_code == 422:
                print("   ✅ JWT validation failed (expected with mock token)")
            else:
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ DELETE error: {e}")

if __name__ == "__main__":
    print("🚀 Testing UGC NET delete functionality...")
    test_delete_endpoints()
    test_with_mock_auth()
    print("\n✅ Test completed!")
