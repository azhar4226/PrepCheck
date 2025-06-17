"""
Utility functions for file operations, downloads, and exports
"""
import os
from flask import send_from_directory, abort, jsonify


def validate_filename(filename):
    """
    Validate filename to prevent directory traversal attacks
    
    Args:
        filename (str): The filename to validate
        
    Returns:
        bool: True if filename is safe, False otherwise
    """
    if not filename:
        return False
    
    # Check for directory traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
        
    return True


def get_mimetype_by_extension(filename):
    """
    Determine MIME type based on file extension
    
    Args:
        filename (str): The filename
        
    Returns:
        str: MIME type string
    """
    if filename.endswith('.pdf'):
        return 'application/pdf'
    elif filename.endswith('.csv'):
        return 'text/csv'
    elif filename.endswith('.json'):
        return 'application/json'
    elif filename.endswith('.xlsx'):
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif filename.endswith('.zip'):
        return 'application/zip'
    else:
        return 'application/octet-stream'


def safe_send_file(export_dir, filename, access_check_func=None):
    """
    Safely send a file with validation and security checks
    
    Args:
        export_dir (str): The directory containing the file
        filename (str): The filename to send
        access_check_func (callable): Optional function to check access permissions
        
    Returns:
        Flask response or tuple with error
    """
    try:
        # Validate filename
        if not validate_filename(filename):
            abort(400)
        
        # Check access permissions if function provided
        if access_check_func and not access_check_func(filename):
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if file exists
        file_path = os.path.join(export_dir, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Get MIME type
        mimetype = get_mimetype_by_extension(filename)
        
        return send_from_directory(
            export_dir,
            filename,
            as_attachment=True,
            mimetype=mimetype
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_export_directory():
    """
    Get the standard export directory path
    
    Returns:
        str: Export directory path
    """
    return os.path.join(os.getcwd(), 'exports')
