from app import db
from app.models import User
from werkzeug.security import generate_password_hash
import os

def seed_admin_user():
    """Create default admin user if it doesn't exist"""
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@prepcheck.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # Check if admin already exists
    admin_user = User.query.filter_by(email=admin_email, is_admin=True).first()
    
    if not admin_user:
        admin_user = User(
            email=admin_email,
            full_name='System Administrator',
            is_admin=True,
            is_active=True
        )
        admin_user.set_password(admin_password)
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"✅ Admin user created: {admin_email}")
    else:
        print(f"ℹ️  Admin user already exists: {admin_email}")

def seed_sample_data():
    """Create sample subjects and chapters for testing"""
    from app.models import Subject, Chapter
    from app.utils.ugc_net_seed_data import seed_ugc_net_subjects
    
    # First, seed UGC NET subjects (contains comprehensive data including subjects and chapters)
    try:
        seed_ugc_net_subjects()
        print("✅ UGC NET subjects and chapters created successfully")
    except Exception as e:
        print(f"Note: UGC NET subjects may already exist: {str(e)}")
    
    db.session.commit()
    print("✅ Sample data created successfully")
