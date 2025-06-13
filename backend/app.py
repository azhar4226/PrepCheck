from dotenv import load_dotenv
import os

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app, init_celery

app = create_app()
celery = init_celery(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
