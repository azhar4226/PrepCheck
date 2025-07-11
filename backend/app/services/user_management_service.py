"""
User Management Service
Handles user CRUD operations and management
"""
from datetime import datetime
from sqlalchemy import desc, or_
from app import db
from app.models import User, UGCNetMockAttempt, UGCNetPracticeAttempt
from app.utils.timezone_utils import get_ist_now


class UserManagementService:
    """
    Service for user management operations
    
    Note: This service enforces IST (Asia/Kolkata) timezone for all users.
    Timezone is not configurable and all timestamps are in IST.
    """
    
    def __init__(self):
        pass
    
    def get_users(self, page=1, per_page=20, search='', filter_type='all', role_filter='', status_filter=''):
        """Get users with filtering and pagination"""
        try:
            # Start with base query
            query = User.query
            
            # Apply role filter
            if role_filter == 'admin':
                query = query.filter_by(is_admin=True)
            elif role_filter == 'user':
                query = query.filter_by(is_admin=False)
            elif filter_type == 'all':
                # When filter_type is 'all', don't filter by role
                pass
            else:
                # Default: exclude admin users unless specifically requested
                query = query.filter_by(is_admin=False)
            
            # Apply status filter
            if status_filter == 'active':
                query = query.filter_by(is_active=True)
            elif status_filter == 'inactive':
                query = query.filter_by(is_active=False)
            
            # Apply search filter
            if search:
                search_term = f'%{search}%'
                query = query.filter(
                    or_(
                        User.full_name.ilike(search_term),
                        User.email.ilike(search_term)
                    )
                )
            
            # Order by created_at descending
            query = query.order_by(desc(User.created_at))
            
            # Paginate
            users = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            users_data = []
            for user in users.items:
                user_data = user.to_dict()
                # Add activity stats
                user_data['mock_attempts'] = UGCNetMockAttempt.query.filter_by(user_id=user.id).count()
                user_data['practice_attempts'] = UGCNetPracticeAttempt.query.filter_by(user_id=user.id).count()
                users_data.append(user_data)
            
            return {
                'users': users_data,
                'total': users.total,
                'pages': users.pages,
                'current_page': page,
                'per_page': per_page
            }
        except Exception as e:
            raise Exception(f"Error fetching users: {str(e)}")
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('User not found')
            return user
        except Exception as e:
            raise Exception(f"Error fetching user: {str(e)}")
    
    def update_user(self, user_id, data):
        """Update user information"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('User not found')
            
            # Update basic fields
            if 'full_name' in data:
                user.full_name = data['full_name']
            
            if 'email' in data:
                # Check if email is already taken
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user and existing_user.id != user.id:
                    raise ValueError('Email already in use')
                user.email = data['email']
            
            if 'is_admin' in data:
                user.is_admin = data['is_admin']
            
            if 'is_active' in data:
                user.is_active = data['is_active']
            
            if 'password' in data and data['password']:
                user.set_password(data['password'])
            
            # Additional profile fields
            profile_fields = [
                'phone', 'bio', 'gender', 'country', 
                'notification_email', 'notification_quiz_reminders', 
                'theme_preference', 'email_verified'
            ]
            
            for field in profile_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            if 'date_of_birth' in data and data['date_of_birth']:
                try:
                    user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError('Invalid date format. Use YYYY-MM-DD')
            
            user.updated_at = get_ist_now()
            db.session.commit()
            
            return user.to_dict()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error updating user: {str(e)}")
    
    def create_user(self, data):
        """Create a new user"""
        try:
            # Validate required fields
            required_fields = ['full_name', 'email', 'password']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValueError(f'{field} is required')
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                raise ValueError('Email already in use')
            
            # Create new user
            user = User(
                full_name=data['full_name'],
                email=data['email'],
                is_admin=data.get('is_admin', False),
                is_active=data.get('is_active', True),
                email_verified=True,  # Admin-created users are verified by default
                phone=data.get('phone'),
                bio=data.get('bio'),
                gender=data.get('gender'),
                country=data.get('country'),
                timezone='Asia/Kolkata'  # IST is the only supported timezone
            )
            user.set_password(data['password'])
            
            if data.get('date_of_birth'):
                try:
                    user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError('Invalid date format. Use YYYY-MM-DD')
            
            db.session.add(user)
            db.session.commit()
            
            return user.to_dict()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error creating user: {str(e)}")
    
    def delete_user(self, user_id):
        """Delete a user"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('User not found')
            
            # Prevent deletion of admin users
            if user.is_admin:
                raise ValueError('Cannot delete admin users')
            
            # Delete the user (cascades will handle related data)
            db.session.delete(user)
            db.session.commit()
            
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error deleting user: {str(e)}")
    
    def update_user_profile_by_admin(self, user_id, data):
        """Update any user's profile (admin only)"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError('User not found')
            
            # Validate email uniqueness if changed
            if 'email' in data and data['email'] != user.email:
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user:
                    raise ValueError('Email already exists')
            
            # Admin can update all fields including admin status
            updatable_fields = [
                'email', 'full_name', 'phone', 'bio', 'date_of_birth', 
                'gender', 'country', 'is_admin', 'is_active',
                'notification_email', 'notification_quiz_reminders', 'theme_preference',
                'email_verified'
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
            
            # Update password if provided
            if 'password' in data and data['password']:
                if len(data['password']) < 6:
                    raise ValueError('Password must be at least 6 characters long')
                user.set_password(data['password'])
            
            user.updated_at = get_ist_now()
            db.session.commit()
            
            return user.to_dict()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error updating user profile: {str(e)}")
    
    def get_user_statistics(self):
        """Get user statistics for dashboard"""
        try:
            stats = {
                'total_users': User.query.filter_by(is_admin=False).count(),
                'total_admins': User.query.filter_by(is_admin=True).count(),
                'active_users': User.query.filter_by(is_active=True, is_admin=False).count(),
                'inactive_users': User.query.filter_by(is_active=False, is_admin=False).count(),
                'new_users_today': User.query.filter(
                    User.created_at >= get_ist_now().date(),
                    User.is_admin == False
                ).count()
            }
            return stats
        except Exception as e:
            raise Exception(f"Error getting user statistics: {str(e)}")
