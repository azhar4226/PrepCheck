# This file helps with Python imports in the backend
import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Add the app directory to Python path  
app_dir = os.path.join(backend_dir, 'app')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
