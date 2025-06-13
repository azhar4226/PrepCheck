#!/usr/bin/env python3
"""
Celery app module for PrepCheck
This module creates and exports the celery app for use with celery CLI
"""

from dotenv import load_dotenv
import os

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app, init_celery

# Create Flask app and initialize Celery
flask_app = create_app()
celery = init_celery(flask_app)

# Export the celery app
app = celery
