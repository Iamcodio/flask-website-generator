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
    """Handle email submission for free download"""
    try:
        site_id = request.form.get('site_id')
        email = request.form.get('email')
        consent_download = request.form.get('consent_download')
        consent_marketing = request.form.get('consent_marketing')
        
        print(f"📧 EMAIL-DOWNLOAD REQUEST:")
        print(f"   Email: {email}")
        print(f"   Site ID: {site_id}")
        print(f"   Consent Download: {consent_download}")
        print(f"   Consent Marketing: {consent_marketing}")
        
        if not site_id or not email or not consent_download:
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        # Always capture lead first (even if download fails)
        print(f"📧 About to capture lead: {email} for site {site_id}")
        from app.utils.lead_capture import capture_lead
        try:
            # Try to get business data from session
            business_data = session.get('business_data', {})
            business_name = business_data.get('business_name')
            industry = business_data.get('industry')
            print(f"📊 Found business data in session: {business_name}, {industry}")
            
            capture_lead(email, site_id, consent_marketing == 'on', 
                        business_name=business_name, industry=industry)
            print(f"✅ Lead captured: {email} for site {site_id}")
        except Exception as e:
            print(f"⚠️ Lead capture error: {e}")
            import traceback
            traceback.print_exc()
        
        # Generate download token
        from flask import current_app
        try:
            token = current_app.auth.generate_token(f"{email}:{site_id}")
            download_url = url_for('auth.download_with_token', token=token, _external=True)
        except Exception as e:
            print(f"❌ Error generating download token: {e}")
            return jsonify({
                'success': False, 
                'message': 'Error generating download link. Your information has been saved and we will contact you.',
                'admin_leads': '/admin/leads'
            })
        
        # In production, send email. In dev, return link directly
        if current_app.config.get('MAIL_SERVER'):
            # Send email with download link
            try:
                from app.services.auth import send_download_email
                send_download_email(email, download_url, site_id)
                return jsonify({
                    'success': True, 
                    'message': 'Check your email for the download link!'
                })
            except Exception as e:
                print(f"❌ Email send error: {e}")
                return jsonify({
                    'success': False,
                    'message': 'Failed to send email. Your information has been saved.',
                    'download_url': download_url,  # Still provide download link
                    'admin_leads': '/admin/leads'
                })
        
        # Dev mode: return link directly
        return jsonify({
            'success': True,
            'message': 'Download link ready!',
            'download_url': download_url
        })
        
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