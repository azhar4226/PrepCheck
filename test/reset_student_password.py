#!/usr/bin/env python3
"""Reset student password"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app
from app.models.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Find student user
    student = User.query.filter_by(email="student1@test.com").first()
    if student:
        # Reset password
        student.password_hash = generate_password_hash("password123")
        
        from app import db
        db.session.commit()
        
        print(f"✓ Reset password for {student.email}")
        print(f"New password: password123")
    else:
        print("Student user not found")
