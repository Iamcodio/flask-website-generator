"""
File handling utilities for uploads and downloads
"""

import os
import tempfile
import zipfile
from flask import current_app, send_file, flash, redirect, url_for, session
from werkzeug.utils import secure_filename

# File upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, business_id, file_type):
    """Save uploaded file and return filename"""
    if file and allowed_file(file.filename):
        # Create business-specific directory
        business_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], business_id)
        os.makedirs(business_dir, exist_ok=True)
        
        # Generate secure filename with type prefix
        filename = secure_filename(file.filename)
        extension = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{file_type}.{extension}"
        
        file_path = os.path.join(business_dir, new_filename)
        file.save(file_path)
        return new_filename
    return None

def download_site_files(site_id, email=None):
    """Generate and serve ZIP file with website files"""
    try:
        site_dir = f'generated_sites/{site_id}'
        
        if not os.path.exists(site_dir):
            flash('Website files not found.', 'error')
            return redirect(url_for('main.index'))
        
        # Create temporary ZIP file
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f'website-{site_id}.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(site_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Add file to ZIP with relative path
                    arcname = os.path.relpath(file_path, site_dir)
                    zipf.write(file_path, arcname)
        
        # Get business name for filename
        business_name = 'website'
        try:
            if session.get('business_data'):
                business_name = session['business_data'].get('business_name', 'website')
                business_name = ''.join(c for c in business_name if c.isalnum() or c in (' ', '-', '_')).strip()
                business_name = business_name.replace(' ', '-').lower()
        except:
            pass
        
        filename = f'{business_name}-website.zip'
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        print(f"Error creating download: {e}")
        flash('Error creating download. Please try again.', 'error')
        return redirect(url_for('main.index'))