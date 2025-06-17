from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, StudyMaterial, Subject, Chapter
from sqlalchemy import desc, or_, and_
from datetime import datetime
import os
from werkzeug.utils import secure_filename

study_material_bp = Blueprint('study_material', __name__)

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'md', 'html', 'ppt', 'pptx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@study_material_bp.route('/', methods=['GET'])
@jwt_required()
def get_study_materials():
    """Get all study materials with filtering and pagination"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        subject_id = request.args.get('subject_id', type=int)
        chapter_id = request.args.get('chapter_id', type=int)
        material_type = request.args.get('material_type')
        search = request.args.get('search', '')
        
        # Build query
        query = StudyMaterial.query
        
        # Apply filters
        if subject_id:
            query = query.join(Chapter, StudyMaterial.chapter_id == Chapter.id)\
                        .filter(Chapter.subject_id == subject_id)
        
        if chapter_id:
            query = query.filter(StudyMaterial.chapter_id == chapter_id)
        
        if material_type:
            query = query.filter(StudyMaterial.material_type == material_type)
        
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                or_(
                    StudyMaterial.title.ilike(search_term),
                    StudyMaterial.description.ilike(search_term),
                    StudyMaterial.content.ilike(search_term)
                )
            )
        
        # Add ordering
        query = query.order_by(desc(StudyMaterial.created_at))
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format results with additional data
        materials = []
        for material in pagination.items:
            material_data = material.to_dict()
            
            # Add chapter and subject information
            if material.chapter:
                material_data['chapter_name'] = material.chapter.name
                if material.chapter.subject:
                    material_data['subject_name'] = material.chapter.subject.name
                    material_data['subject_id'] = material.chapter.subject.id
                else:
                    material_data['subject_name'] = None
                    material_data['subject_id'] = None
            else:
                material_data['chapter_name'] = None
                material_data['subject_name'] = None
                material_data['subject_id'] = None
            
            materials.append(material_data)
        
        return jsonify({
            'success': True,
            'materials': materials,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@study_material_bp.route('/<int:material_id>', methods=['GET'])
@jwt_required()
def get_study_material(material_id):
    """Get a specific study material by ID"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        material = StudyMaterial.query.get_or_404(material_id)
        
        material_data = material.to_dict()
        
        # Add additional data
        if material.chapter:
            material_data['chapter_name'] = material.chapter.name
            if material.chapter.subject:
                material_data['subject_name'] = material.chapter.subject.name
                material_data['subject_id'] = material.chapter.subject.id
        
        return jsonify({
            'success': True,
            'material': material_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@study_material_bp.route('/', methods=['POST'])
@jwt_required()
def create_study_material():
    """Create a new study material"""
    try:
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'material_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate material type
        valid_types = ['document', 'video', 'audio', 'link', 'text']
        if data['material_type'] not in valid_types:
            return jsonify({'error': f'Material type must be one of: {", ".join(valid_types)}'}), 400
        
        # Create study material
        material = StudyMaterial(
            title=data['title'],
            description=data.get('description', ''),
            content=data.get('content', ''),
            material_type=data['material_type'],
            file_path=data.get('file_path'),
            url=data.get('url'),
            chapter_id=data.get('chapter_id'),
            created_by=user.id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(material)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Study material created successfully',
            'material': material.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@study_material_bp.route('/<int:material_id>', methods=['PUT'])
@jwt_required()
def update_study_material(material_id):
    """Update an existing study material"""
    try:
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        material = StudyMaterial.query.get_or_404(material_id)
        data = request.get_json()
        
        # Validate material type if provided
        if 'material_type' in data:
            valid_types = ['document', 'video', 'audio', 'link', 'text']
            if data['material_type'] not in valid_types:
                return jsonify({'error': f'Material type must be one of: {", ".join(valid_types)}'}), 400
        
        # Update fields
        updatable_fields = [
            'title', 'description', 'content', 'material_type',
            'file_path', 'url', 'chapter_id'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(material, field, data[field])
        
        material.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Study material updated successfully',
            'material': material.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@study_material_bp.route('/<int:material_id>', methods=['DELETE'])
@jwt_required()
def delete_study_material(material_id):
    """Delete a study material"""
    try:
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        material = StudyMaterial.query.get_or_404(material_id)
        
        # Delete associated file if exists
        if material.file_path and os.path.exists(material.file_path):
            try:
                os.remove(material.file_path)
            except OSError:
                pass  # File might be already deleted or inaccessible
        
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Study material deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@study_material_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_study_material():
    """Upload a file for study material"""
    try:
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join('uploads', 'study_materials')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Secure the filename and save
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = f"{timestamp}{filename}"
        file_path = os.path.join(upload_dir, filename)
        
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'file_path': file_path,
            'filename': filename
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
