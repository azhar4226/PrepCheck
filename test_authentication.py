#!/usr/bin/env python3
"""
Test authentication with the provided credentials
"""
import requests
import json
import sys

# Backend URL
BASE_URL = "http://localhost:8000"

def test_login():
    """Test login with student credentials"""
    login_url = f"{BASE_URL}/api/auth/login"
    
    credentials = {
        "email": "student1@test.com",
        "password": "Student123"
    }
    
    print("🔍 Testing login with student credentials...")
    print(f"URL: {login_url}")
    print(f"Credentials: {credentials}")
    
    try:
        response = requests.post(login_url, json=credentials)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Extract the token
            token = data.get('access_token') or data.get('token')
            if token:
                print(f"🔑 Token (first 50 chars): {token[:50]}...")
                
                # Test the statistics endpoint with this token
                print("\n🔍 Testing statistics endpoint with token...")
                test_statistics(token)
            else:
                print("⚠️ No token found in response")
                
        else:
            print("❌ Login failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during login: {e}")

def test_statistics(token):
    """Test the statistics endpoint with the token"""
    stats_url = f"{BASE_URL}/api/ugc-net/statistics"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(stats_url, headers=headers)
        print(f"Statistics Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Statistics endpoint works!")
            print(f"Statistics: {json.dumps(data, indent=2)}")
        else:
            print("❌ Statistics endpoint failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error fetching statistics: {e}")

if __name__ == "__main__":
    test_login()
