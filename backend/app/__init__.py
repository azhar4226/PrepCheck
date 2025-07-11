from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate
from celery import Celery
import redis
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))

from config.config import config

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
migrate = Migrate()
redis_client = None  # Will be initialized in create_app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Enable CORS with specific configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })
    
    # Initialize Redis
    global redis_client
    redis_client = redis.from_url(app.config['REDIS_URL'])
    
    # Register blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.user_controller import user_bp
    from app.controllers.analytics_controller import analytics_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.ugc_net import register_ugc_net_blueprints
    from app.controllers.notifications_controller import notifications_bp

    # Register blueprints with v1 prefix
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(user_bp, url_prefix='/api/v1/users')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(notifications_bp, url_prefix='/api/v1/notifications')

    # Register UGC NET modular blueprints with the app
    register_ugc_net_blueprints(app)
    
    # Serve uploaded files
    from flask import send_from_directory
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        uploads_path = os.path.join(app.root_path, '..', 'uploads')
        return send_from_directory(uploads_path, filename)
    
    # Create tables and apply migrations
    with app.app_context():
        db.create_all()
        
        # Apply database migrations if needed
        try:
            from app.utils.migrate import apply_migrations
            apply_migrations()
        except Exception as e:
            print(f"Migration error (this is normal for new databases): {e}")
        
        from app.utils.seed_data import seed_admin_user, seed_sample_data
        seed_admin_user()
        seed_sample_data()
    
    return app

celery_app = None

def init_celery(app):
    global celery_app
    celery_app = make_celery(app)
    return celery_app
