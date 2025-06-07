from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify, send_file
import os
from datetime import datetime
import uuid
import shutil
import zipfile
import tempfile
from werkzeug.utils import secure_filename
from site_generator import SiteGenerator
from supabase_client import create_user_and_business, get_supabase_client
from auth import TokenAuth

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Initialize authentication
supabase_client = get_supabase_client()
auth = TokenAuth(app, supabase_client)

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

# Capture route moved below to integrate with authentication

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

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with email token authentication"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            return render_template('login.html', 
                                 message='Please enter your email address', 
                                 message_type='error')
        
        # Generate login token
        token = auth.generate_token(email)
        login_url = url_for('verify_login', token=token, _external=True)
        
        # Send login email (or print for dev)
        if auth.send_login_email(email, login_url):
            return render_template('login.html', 
                                 message=f'🚀 Magic link sent to {email}! Check your email and click the link to log in.',
                                 message_type='success')
        else:
            return render_template('login.html', 
                                 message='Error sending login email. Please try again.',
                                 message_type='error')
    
    return render_template('login.html')

@app.route('/verify/<token>')
def verify_login(token):
    """Verify login token and log user in"""
    email = auth.verify_token(token, max_age=3600)  # 1 hour expiry
    
    if not email:
        flash('Invalid or expired login link. Please try again.', 'error')
        return redirect(url_for('login'))
    
    # Create or get user
    user = auth.create_or_get_user(email)
    if not user:
        flash('Error creating user account. Please try again.', 'error')
        return redirect(url_for('login'))
    
    # Log user in
    session['user_id'] = user['id']
    session['user_email'] = user['email']
    session['logged_in'] = True
    
    flash(f'Welcome to SiteGen, {email}! 🎉', 'success')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """User dashboard - requires login"""
    if not session.get('logged_in'):
        flash('Please log in to access your dashboard.', 'error')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    user_email = session.get('user_email')
    
    # Get user data
    user = {'id': user_id, 'email': user_email, 'created_at': '', 'last_login': ''}
    
    # Get user's sites
    sites = auth.get_user_sites(user_id)
    
    return render_template('dashboard.html', user=user, sites=sites)

@app.route('/logout')
def logout():
    """Log user out"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

# Helper function to check if user is logged in
def is_logged_in():
    return session.get('logged_in', False)

def store_email_lead(email, site_id, consent_download=True, consent_marketing=False):
    """Store email lead for marketing list with GDPR consent"""
    try:
        # Get business data from session for context
        business_data = session.get('business_data', {})
        business_name = business_data.get('business_name', 'Unknown')
        industry = business_data.get('industry', 'Unknown')
        
        lead_data = {
            'email': email,
            'site_id': site_id,
            'business_name': business_name,
            'industry': industry,
            'captured_at': datetime.now().isoformat(),
            'status': 'free_download',
            'consent_download': consent_download,
            'consent_marketing': consent_marketing,
            'consent_date': datetime.now().isoformat()
        }
        
        # Store in Supabase (or file in dev mode)
        if hasattr(auth, 'supabase') and auth.supabase:
            try:
                auth.supabase.table('email_leads').insert(lead_data).execute()
                print(f"✅ Email lead stored in Supabase: {email}")
            except Exception as e:
                print(f"⚠️ Supabase storage failed, using file backup: {e}")
                store_email_to_file(lead_data)
        else:
            # Development mode - store in local file
            store_email_to_file(lead_data)
            
    except Exception as e:
        print(f"Error storing email lead: {e}")

def store_email_to_file(lead_data):
    """Store email lead to local CSV file for development"""
    import csv
    import os
    
    filename = 'email_leads.csv'
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['email', 'site_id', 'business_name', 'industry', 'captured_at', 'status', 'consent_download', 'consent_marketing', 'consent_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(lead_data)
    
    print(f"📝 Email lead stored to {filename}: {lead_data['email']} (Marketing consent: {lead_data.get('consent_marketing', False)})")

# Admin route to view collected emails
@app.route('/admin/leads')
def view_leads():
    """View collected email leads"""
    try:
        import csv
        import os
        
        leads = []
        filename = 'email_leads.csv'
        
        if os.path.exists(filename):
            with open(filename, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                leads = list(reader)
        
        return render_template('leads.html', leads=leads)
    except Exception as e:
        return f"Error reading leads: {e}"

@app.route('/admin/leads/export')
def export_leads():
    """Export leads as CSV download"""
    import os
    filename = 'email_leads.csv'
    if os.path.exists(filename):
        return send_file(filename, as_attachment=True, download_name='sitegen_leads.csv')
    else:
        flash('No leads file found.', 'error')
        return redirect(url_for('view_leads'))

# Test Download Route (for development)
@app.route('/test-download/<site_id>')
def test_download(site_id):
    """Direct download for testing - bypasses email"""
    return download_site_files(site_id, 'test@example.com')

# Download Routes
@app.route('/email-download', methods=['POST'])
def email_download():
    """Handle email download request for free tier"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        site_id = data.get('site_id')
        consent_download = data.get('consent_download', False)
        consent_marketing = data.get('consent_marketing', False)
        
        if not email or not site_id:
            return jsonify({'success': False, 'message': 'Email and site ID required'})
        
        if not consent_download:
            return jsonify({'success': False, 'message': 'Download consent is required'})
        
        print(f"📧 EMAIL CAPTURED: {email} for site {site_id}")
        print(f"🔒 CONSENT - Download: {consent_download}, Marketing: {consent_marketing}")
        
        # Store email in database/file for lead collection
        store_email_lead(email, site_id, consent_download, consent_marketing)
        
        # Generate download token
        download_token = auth.generate_token(f"{email}:{site_id}")
        download_url = url_for('download_with_token', token=download_token, _external=True)
        
        # Send email with download link (or print in dev mode)
        if auth.send_download_email(email, download_url, site_id):
            return jsonify({'success': True, 'message': 'Download link sent successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send email'})
            
    except Exception as e:
        print(f"Error in email download: {e}")
        return jsonify({'success': False, 'message': 'Server error'})

@app.route('/download/<site_id>')
def download_site_direct(site_id):
    """Direct download for logged-in users"""
    if not is_logged_in():
        flash('Please log in to download your sites.', 'error')
        return redirect(url_for('login'))
    
    return download_site_files(site_id)

@app.route('/download/token/<token>')
def download_with_token(token):
    """Download with email token for free tier"""
    # Verify token (contains email:site_id)
    token_data = auth.verify_token(token, max_age=3600)  # 1 hour expiry
    if not token_data or ':' not in token_data:
        flash('Invalid or expired download link.', 'error')
        return redirect(url_for('index'))
    
    email, site_id = token_data.split(':', 1)
    return download_site_files(site_id, email)

def download_site_files(site_id, email=None):
    """Generate and serve ZIP file with website files"""
    try:
        site_dir = f'generated_sites/{site_id}'
        
        if not os.path.exists(site_dir):
            flash('Website files not found.', 'error')
            return redirect(url_for('index'))
        
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
        return redirect(url_for('index'))

# Update capture route to save to user account if logged in
@app.route('/capture', methods=['GET', 'POST'])
def capture_business_info():
    """Capture business information and generate site"""
    if request.method == 'POST':
        print("🔍 Form submission received")
        print(f"🔍 Form data: {dict(request.form)}")
        print(f"🔍 Files: {list(request.files.keys())}")
        
        # Handle CSV upload
        if 'csv_upload' in request.files:
            csv_file = request.files['csv_upload']
            if csv_file.filename and csv_file.filename.endswith('.csv'):
                # Let JavaScript handle CSV parsing on the frontend
                pass
        
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
            return redirect(url_for('capture_business_info'))
        
        # Generate the site
        generator = SiteGenerator(business_data)
        site_result = generator.generate_site()
        
        # Store in session for preview access
        session['business_data'] = business_data
        session['site_result'] = site_result
        
        # Save to user account if logged in
        if is_logged_in():
            user_id = session.get('user_id')
            site_data = {
                'site_id': business_data['id'],
                'business_name': business_data.get('business_name'),
                'site_url': site_result['site_url'],
                **business_data
            }
            auth.save_user_site(user_id, site_data)
        
        return redirect(url_for('preview_site'))
    
    return render_template('capture.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)