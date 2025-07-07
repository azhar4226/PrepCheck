#!/usr/bin/env python3
"""Create a student user for testing UGC NET functionality"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
load_dotenv()

from backend.app import create_app
from backend.app.models.models import User, db
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Check if user already exists
    existing_user = User.query.filter_by(email='student@prepcheck.com').first()
    if existing_user:
        print(f'✅ Student user already exists: {existing_user.email}')
        print(f'📧 Email: student@prepcheck.com')
        print(f'🔑 Password: password123')
    else:
        # Create a regular student user
        student_user = User(
            email='student@prepcheck.com',
            full_name='Test Student',
            password_hash=generate_password_hash('password123'),
            is_admin=False,
            is_active=True
        )
        db.session.add(student_user)
        db.session.commit()
        print(f'✅ Created student user: {student_user.email}')
        print(f'📧 Email: student@prepcheck.com')
        print(f'🔑 Password: password123')
