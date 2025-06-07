from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import os
from datetime import datetime
import uuid
import shutil
from werkzeug.utils import secure_filename
from site_generator import SiteGenerator
from supabase_client import create_user_and_business

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

@app.errorhandler(413)
def too_large(e):
    flash('File is too large. Please upload images smaller than 16MB.', 'error')
    return redirect(url_for('capture_business_info'))

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, business_id, file_type):
    """Save uploaded file and return filename"""
    if file and allowed_file(file.filename):
        # Create business-specific directory
        business_dir = os.path.join(app.config['UPLOAD_FOLDER'], business_id)
        os.makedirs(business_dir, exist_ok=True)
        
        # Generate secure filename with type prefix
        filename = secure_filename(file.filename)
        extension = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{file_type}.{extension}"
        
        file_path = os.path.join(business_dir, new_filename)
        file.save(file_path)
        return new_filename
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture', methods=['GET', 'POST'])
def capture_business_info():
    if request.method == 'POST':
        business_id = str(uuid.uuid4())
        
        # Handle custom industry
        industry = request.form.get('industry')
        if industry == 'custom':
            industry = request.form.get('custom_industry', 'other')
        
        business_data = {
            'id': business_id,
            'business_name': request.form.get('business_name'),
            'industry': industry,
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'business_story': request.form.get('business_story'),
            'mission_statement': request.form.get('mission_statement'),
            'values': request.form.get('values'),
            'goals': request.form.get('goals'),
            'services': request.form.get('services'),
            'owner_name': request.form.get('owner_name'),
            'years_experience': request.form.get('years_experience'),
            'primary_color': request.form.get('primary_color', '#0077CC'),
            'created_at': datetime.now().isoformat()
        }
        
        # Handle file uploads
        uploaded_files = {}
        for file_type in ['logo', 'hero_image', 'about_image', 'team_image']:
            if file_type in request.files:
                file = request.files[file_type]
                if file.filename:
                    filename = save_uploaded_file(file, business_id, file_type)
                    if filename:
                        uploaded_files[file_type] = filename
                        flash(f'{file_type.replace("_", " ").title()} uploaded successfully!', 'success')
        
        business_data['uploaded_files'] = uploaded_files
        
        # Debug: Print selected color
        print(f"🎨 Selected primary color: {business_data['primary_color']}")
        
        # Store in session for demo (would integrate Supabase in production)
        session['business_data'] = business_data
        
        # Generate the site immediately
        generator = SiteGenerator(business_data)
        site_result = generator.generate_site()
        
        session['site_result'] = site_result
        flash('Website generated successfully!', 'success')
        return redirect(url_for('preview_site'))
    
    return render_template('capture.html')

@app.route('/preview')
def preview_site():
    business_data = session.get('business_data')
    site_result = session.get('site_result')
    
    if not business_data or not site_result:
        flash('Please fill out your business information first.', 'error')
        return redirect(url_for('capture_business_info'))
    
    return render_template('preview.html', business=business_data, site=site_result)

@app.route('/generated_sites/<site_id>/<filename>')
def serve_generated_site(site_id, filename):
    """Serve generated site files"""
    return send_from_directory(f'generated_sites/{site_id}', filename)

@app.route('/uploads/<business_id>/<filename>')
def serve_uploaded_file(business_id, filename):
    """Serve uploaded user files"""
    return send_from_directory(f'static/uploads/{business_id}', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)