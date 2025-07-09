"""
Admin Profile Service
Handles admin profile management and self-service operations
"""
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from app import db
from app.models import User


class AdminProfileService:
    """Service for admin profile operations"""
    
    def __init__(self):
        pass
    
    def get_admin_profile(self, user_id):
        """Get admin profile by user ID"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('User not found')
            
            if not user.is_admin:
                raise ValueError('User is not an admin')
            
            return user.to_dict()
        except Exception as e:
            raise Exception(f"Error fetching admin profile: {str(e)}")
    
    def update_admin_profile(self, user_id, data):
        """Update admin profile"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('User not found')
            
            if not user.is_admin:
                raise ValueError('User is not an admin')
            
            # Validate email uniqueness if changed
            if 'email' in data and data['email'] != user.email:
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user:
                    raise ValueError('Email already exists')
            
            # Update allowed fields (admins can update more fields)
            updatable_fields = [
                'email', 'full_name', 'phone', 'bio', 'date_of_birth', 
                'gender', 'country', 'timezone', 'notification_email',
                'notification_quiz_reminders', 'theme_preference'
            ]
            
            for field in updatable_fields:
                if field in data:
                    if field == 'date_of_birth' and data[field]:
                        try:
                            user.date_of_birth = datetime.strptime(data[field], '%Y-%m-%d').date()
                        except ValueError:
                            raise ValueError('Invalid date format. Use YYYY-MM-DD')
                    else:
                        setattr(user, field, data[field])
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return user.to_dict()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error updating admin profile: {str(e)}")
    
    def change_admin_password(self, user_id, current_password, new_password):
        """Change admin password"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('User not found')
            
            if not user.is_admin:
                raise ValueError('User is not an admin')
            
            if not current_password or not new_password:
                raise ValueError('Current password and new password are required')
            
            if not user.check_password(current_password):
                raise ValueError('Current password is incorrect')
            
            if len(new_password) < 6:
                raise ValueError('New password must be at least 6 characters long')
            
            user.set_password(new_password)
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error changing admin password: {str(e)}")
    
    def upload_profile_picture(self, user_id, file):
        """Upload profile picture for admin"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('User not found')
            
            if not user.is_admin:
                raise ValueError('User is not an admin')
            
            if not file.filename:
                raise ValueError('No file selected')
            
            # Check file size (max 5MB)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            max_size = 5 * 1024 * 1024  # 5MB
            if file_size > max_size:
                raise ValueError('File too large. Maximum size is 5MB')
            
            # Check file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            if not file_extension or file_extension not in allowed_extensions:
                raise ValueError('Invalid file type. Only PNG, JPG, JPEG, GIF, and WEBP are allowed')
            
            # Delete old profile picture if exists
            if user.profile_picture_url:
                old_filename = user.profile_picture_url.split('/')[-1]
                old_file_path = os.path.join(current_app.root_path, '..', 'uploads', 'profile_pictures', old_filename)
                try:
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                except Exception as e:
                    print(f"Warning: Could not delete old profile picture: {e}")
            
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{user.id}_{uuid.uuid4().hex}.{file_extension}"
            
            # Ensure upload folder exists
            upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'profile_pictures')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # Verify file was saved successfully
            if not os.path.exists(file_path):
                raise ValueError('Failed to save file')
            
            # Update user profile with proper URL
            user.profile_picture_url = f"/uploads/profile_pictures/{unique_filename}"
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'message': 'Profile picture uploaded successfully',
                'profile_picture_url': user.profile_picture_url,
                'user': user.to_dict()  # Include updated user data
            }
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error uploading profile picture: {str(e)}")
    
    def remove_profile_picture(self, user_id):
        """Remove profile picture for admin"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('User not found')
            
            if not user.is_admin:
                raise ValueError('User is not an admin')
            
            if not user.profile_picture_url:
                raise ValueError('No profile picture to remove')
            
            # Delete the file
            filename = user.profile_picture_url.split('/')[-1]
            file_path = os.path.join(current_app.root_path, '..', 'uploads', 'profile_pictures', filename)
            
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not delete profile picture file: {e}")
            
            # Update user profile
            user.profile_picture_url = None
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'message': 'Profile picture removed successfully',
                'user': user.to_dict()  # Include updated user data
            }
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error removing profile picture: {str(e)}")
