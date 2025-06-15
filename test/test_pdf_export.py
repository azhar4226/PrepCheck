#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/apple/Desktop/PrepCheck/backend')

# Set environment
os.environ['FLASK_ENV'] = 'development'

from app.tasks.export_tasks import export_admin_data

# Test PDF generation
print("Testing PDF generation...")
result = export_admin_data('analytics')
print(f"Result: {result}")
