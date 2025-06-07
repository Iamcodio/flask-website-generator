"""
Main application routes - website generation and preview
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify, send_file
import os
import uuid
import tempfile
import zipfile
from datetime import datetime
from werkzeug.utils import secure_filename

from app.services.site_generator import SiteGenerator
from app.utils.file_helpers import allowed_file, save_uploaded_file

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/capture', methods=['GET', 'POST'])
def capture_business_info():
    """Capture business information and generate site"""
    if request.method == 'POST':
        print("🔍 Form submission received")
        print(f"🔍 Form data: {dict(request.form)}")
        print(f"🔍 Files: {list(request.files.keys())}")
        
        # Get form data
        business_data = {
            'id': str(uuid.uuid4()),
            'business_name': request.form.get('business_name'),
            'industry': request.form.get('industry'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'owner_name': request.form.get('owner_name'),
            'years_experience': request.form.get('years_experience'),
            'business_story': request.form.get('business_story'),
            'mission_statement': request.form.get('mission_statement'),
            'values': request.form.get('values'),
            'goals': request.form.get('goals'),
            'services': request.form.get('services'),
            'primary_color': request.form.get('primary_color', '#0077CC'),
            'created_at': datetime.now().isoformat()
        }
        
        # Handle custom industry
        industry = request.form.get('industry')
        if industry == 'custom':
            industry = request.form.get('custom_industry', 'other')
        business_data['industry'] = industry
        
        # Handle uploaded files
        uploaded_files = {}
        file_types = ['logo', 'hero_image', 'about_image', 'team_image']
        
        for file_type in file_types:
            if file_type in request.files:
                file = request.files[file_type]
                if file and file.filename and allowed_file(file.filename):
                    filename = save_uploaded_file(file, business_data['id'], file_type)
                    if filename:
                        uploaded_files[file_type] = filename
        
        business_data['uploaded_files'] = uploaded_files
        
        # Validate required fields
        required_fields = ['business_name', 'industry', 'email']
        missing_fields = [field for field in required_fields if not business_data.get(field)]
        
        if missing_fields:
            flash(f'Please fill out required fields: {", ".join(missing_fields)}', 'error')
            return redirect(url_for('main.capture_business_info'))
        
        # Generate the site
        generator = SiteGenerator(business_data)
        site_result = generator.generate_site()
        
        # Store in session for preview access
        session['business_data'] = business_data
        session['site_result'] = site_result
        
        # Save to user account if logged in
        from flask import current_app
        if session.get('logged_in'):
            user_id = session.get('user_id')
            site_data = {
                'site_id': business_data['id'],
                'business_name': business_data.get('business_name'),
                'site_url': site_result['site_url'],
                **business_data
            }
            current_app.auth.save_user_site(user_id, site_data)
        
        return redirect(url_for('main.preview_site'))
    
    return render_template('capture.html')

@main_bp.route('/preview')
def preview_site():
    business_data = session.get('business_data')
    site_result = session.get('site_result')
    
    if not business_data or not site_result:
        flash('Please fill out your business information first.', 'error')
        return redirect(url_for('main.capture_business_info'))
    
    return render_template('preview.html', business=business_data, site=site_result)

@main_bp.route('/generated_sites/<site_id>/<filename>')
def serve_generated_site(site_id, filename):
    """Serve generated site files"""
    return send_from_directory(f'generated_sites/{site_id}', filename)

@main_bp.route('/uploads/<business_id>/<filename>')
def serve_uploaded_file(business_id, filename):
    """Serve uploaded user files"""
    return send_from_directory(f'static/uploads/{business_id}', filename)