#!/usr/bin/env python3
"""
Celery worker script for PrepCheck
Run with: python celery_worker.py
"""

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import after loading env vars
from app import create_app, init_celery

# Create Flask app and initialize Celery
app = create_app()
celery = init_celery(app)

if __name__ == '__main__':
    # Start Celery worker
    celery.start()
