"""
Database migration utility for PrepCheck application
"""
from app import db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    try:
        result = db.session.execute(text(f"PRAGMA table_info({table_name})"))
        columns = [row[1] for row in result.fetchall()]  # Column names are in index 1
        return column_name in columns
    except Exception as e:
        logger.error(f"Error checking column {column_name} in {table_name}: {e}")
        return False

def add_column_if_not_exists(table_name, column_name, column_definition):
    """Add a column to a table if it doesn't exist"""
    try:
        if not check_column_exists(table_name, column_name):
            logger.info(f"Adding column {column_name} to {table_name}")
            db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"))
            db.session.commit()
            return True
        else:
            logger.info(f"Column {column_name} already exists in {table_name}")
            return False
    except Exception as e:
        logger.error(f"Error adding column {column_name} to {table_name}: {e}")
        db.session.rollback()
        return False

def apply_migrations():
    """Apply all pending migrations"""
    logger.info("Starting database migrations...")
    
    # Migration 001: Add profile fields to users table
    try:
        # Add profile fields
        add_column_if_not_exists('users', 'phone', 'VARCHAR(20)')
        add_column_if_not_exists('users', 'bio', 'TEXT')
        add_column_if_not_exists('users', 'profile_picture_url', 'VARCHAR(255)')
        add_column_if_not_exists('users', 'date_of_birth', 'DATE')
        add_column_if_not_exists('users', 'gender', 'VARCHAR(10)')
        add_column_if_not_exists('users', 'country', 'VARCHAR(50)')
        add_column_if_not_exists('users', 'timezone', 'VARCHAR(50) DEFAULT "UTC"')
        add_column_if_not_exists('users', 'notification_email', 'BOOLEAN DEFAULT 1')
        add_column_if_not_exists('users', 'notification_quiz_reminders', 'BOOLEAN DEFAULT 1')
        add_column_if_not_exists('users', 'theme_preference', 'VARCHAR(20) DEFAULT "light"')
        add_column_if_not_exists('users', 'email_verified', 'BOOLEAN DEFAULT 0')
        add_column_if_not_exists('users', 'email_verification_token', 'VARCHAR(255)')
        add_column_if_not_exists('users', 'password_reset_token', 'VARCHAR(255)')
        add_column_if_not_exists('users', 'password_reset_expires', 'DATETIME')
        add_column_if_not_exists('users', 'updated_at', 'DATETIME')
        
        logger.info("Migration 001 completed successfully")
        
    except Exception as e:
        logger.error(f"Error in migration 001: {e}")
        db.session.rollback()
        raise
    
    logger.info("All migrations applied successfully")
