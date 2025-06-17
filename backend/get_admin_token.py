#!/usr/bin/env python3
"""Generate admin login token for testing"""

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
    # Get admin user
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        # Create JWT token
        token = create_access_token(identity=str(admin.id))
        print(f"Admin user: {admin.full_name} ({admin.email})")
        print(f"JWT Token: {token}")
        print(f"\nTest command:")
        print(f'curl -X GET http://localhost:8000/api/admin/dashboard -H "Authorization: Bearer {token}" | jq')
    else:
        print("No admin user found")
