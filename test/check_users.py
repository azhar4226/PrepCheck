#!/usr/bin/env python3
"""Check existing users and create tokens"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app
from app.models.models import User
from flask_jwt_extended import create_access_token

app = create_app()

with app.app_context():
    # Get all users
    users = User.query.all()
    print(f"Found {len(users)} users:")
    
    student_user = None
    for user in users:
        role = "Admin" if user.is_admin else "Student"
        print(f"  {user.id}: {user.full_name} ({user.email}) - {role}")
        if not user.is_admin:
            student_user = user
    
    if student_user:
        # Create JWT token for student
        token = create_access_token(identity=str(student_user.id))
        print(f"\nStudent token for {student_user.email}:")
        print(f"JWT Token: {token}")
        print(f"\nTest command:")
        print(f'curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d \'{{"email": "{student_user.email}", "password": "password123"}}\'')
    else:
        print("No student user found")
        
        # Create a student user
        print("\nCreating a student user...")
        from werkzeug.security import generate_password_hash
        
        student = User(
            email="student@test.com",
            password_hash=generate_password_hash("password123"),
            full_name="Test Student",
            is_admin=False,
            verification_status="verified"
        )
        
        from app import db
        db.session.add(student)
        db.session.commit()
        
        token = create_access_token(identity=str(student.id))
        print(f"✓ Created student user: {student.email}")
        print(f"JWT Token: {token}")
