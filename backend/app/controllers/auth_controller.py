from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import User
from app.utils.timezone_utils import get_ist_now

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'data': {},
                'message': 'Invalid or missing JSON in request.'
            }), 400
        # Validate required fields
        required_fields = ['email', 'password', 'full_name']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'status': 'error',
                'data': {},
                'message': f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'status': 'error',
                'data': {},
                'message': 'Email already registered.'
            }), 400
        # Validate subject_id if provided
        subject_id = data.get('subject_id')
        if subject_id:
            from app.models.models import Subject
            subject = Subject.query.get(subject_id)
            if not subject or not subject.is_active:
                return jsonify({
                    'status': 'error',
                    'data': {},
                    'message': 'Invalid subject selected.'
                }), 400
        # Create new user
        user = User(
            email=data['email'],
            full_name=data['full_name'],
            subject_id=subject_id,
            is_admin=False
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'status': 'success',
            'data': {
                'access_token': access_token,
                'user': user.to_dict()
            },
            'message': 'User registered successfully.'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'data': {},
            'message': 'Registration failed. Please try again.'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.check_password(data['password']) and user.is_active:
            # Update last login
            user.last_login = get_ist_now()
            db.session.commit()
                 # Create access token
            access_token = create_access_token(identity=str(user.id))
            
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


