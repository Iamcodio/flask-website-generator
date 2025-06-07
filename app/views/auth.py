"""
Authentication and download routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import os
import tempfile
import zipfile
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with email token authentication"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            return render_template('login.html', 
                                 message='Please enter your email address', 
                                 message_type='error')
        
        from flask import current_app
        
        # Generate login token
        token = current_app.auth.generate_token(email)
        login_url = url_for('auth.verify_login', token=token, _external=True)
        
        # Send login email (or print for dev)
        if current_app.auth.send_login_email(email, login_url):
            return render_template('login.html', 
                                 message=f'🚀 Magic link sent to {email}! Check your email and click the link to log in.',
                                 message_type='success')
        else:
            return render_template('login.html', 
                                 message='Error sending login email. Please try again.',
                                 message_type='error')
    
    return render_template('login.html')

@auth_bp.route('/verify/<token>')
def verify_login(token):
    """Verify login token and log user in"""
    from flask import current_app
    
    email = current_app.auth.verify_token(token, max_age=3600)  # 1 hour expiry
    
    if not email:
        flash('Invalid or expired login link. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
    # Create or get user
    user = current_app.auth.create_or_get_user(email)
    if not user:
        flash('Error creating user account. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
    # Log user in
    session['user_id'] = user['id']
    session['user_email'] = user['email']
    session['logged_in'] = True
    
    flash(f'Welcome to SiteGen, {email}! 🎉', 'success')
    return redirect(url_for('auth.dashboard'))

@auth_bp.route('/dashboard')
def dashboard():
    """User dashboard - requires login"""
    if not session.get('logged_in'):
        flash('Please log in to access your dashboard.', 'error')
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    user_email = session.get('user_email')
    
    # Get user data
    user = {'id': user_id, 'email': user_email, 'created_at': '', 'last_login': ''}
    
    from flask import current_app
    # Get user's sites
    sites = current_app.auth.get_user_sites(user_id)
    
    return render_template('dashboard.html', user=user, sites=sites)

@auth_bp.route('/logout')
def logout():
    """Log user out"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/email-download', methods=['POST'])
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
        from app.utils.lead_capture import store_email_lead
        store_email_lead(email, site_id, consent_download, consent_marketing)
        
        from flask import current_app
        
        # Generate download token
        download_token = current_app.auth.generate_token(f"{email}:{site_id}")
        download_url = url_for('auth.download_with_token', token=download_token, _external=True)
        
        # Send email with download link (or print in dev mode)
        if current_app.auth.send_download_email(email, download_url, site_id):
            return jsonify({'success': True, 'message': 'Download link sent successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send email'})
            
    except Exception as e:
        print(f"Error in email download: {e}")
        return jsonify({'success': False, 'message': 'Server error'})

@auth_bp.route('/download/<site_id>')
def download_site_direct(site_id):
    """Direct download for logged-in users"""
    if not session.get('logged_in'):
        flash('Please log in to download your sites.', 'error')
        return redirect(url_for('auth.login'))
    
    from app.utils.file_helpers import download_site_files
    return download_site_files(site_id)

@auth_bp.route('/download/token/<token>')
def download_with_token(token):
    """Download with email token for free tier"""
    from flask import current_app
    
    # Verify token (contains email:site_id)
    token_data = current_app.auth.verify_token(token, max_age=3600)  # 1 hour expiry
    if not token_data or ':' not in token_data:
        flash('Invalid or expired download link.', 'error')
        return redirect(url_for('main.index'))
    
    email, site_id = token_data.split(':', 1)
    from app.utils.file_helpers import download_site_files
    return download_site_files(site_id, email)

@auth_bp.route('/test-download/<site_id>')
def test_download(site_id):
    """Direct download for testing - bypasses email"""
    from app.utils.file_helpers import download_site_files
    return download_site_files(site_id, 'test@example.com')