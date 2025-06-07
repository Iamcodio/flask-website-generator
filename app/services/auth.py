"""
Email Token Authentication Module
Simple authentication system using email verification tokens
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for
import os

# Flask-Mail imports (optional for now)
try:
    from flask_mail import Mail, Message
    MAIL_AVAILABLE = True
except ImportError:
    MAIL_AVAILABLE = False
    # Create mock classes for development
    class Mail:
        def __init__(self, app=None):
            pass
        def send(self, msg):
            pass
    
    class Message:
        def __init__(self, **kwargs):
            pass
    
    print("⚠️ Flask-Mail not available. Email sending disabled for development.")

class TokenAuth:
    def __init__(self, app=None, supabase_client=None):
        self.app = app
        self.supabase = supabase_client
        self.mail = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the authentication system with Flask app"""
        self.app = app
        
        # Secret key for token generation
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
        self.serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        
        # Configure Flask-Mail if available
        if MAIL_AVAILABLE:
            app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
            app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
            app.config['MAIL_USE_TLS'] = True
            app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
            app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
            app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@sitegen.com')
            
            self.mail = Mail(app)
        else:
            self.mail = None
    
    def generate_token(self, email):
        """Generate a secure token for email verification"""
        return self.serializer.dumps(email, salt='email-verification')
    
    def verify_token(self, token, max_age=3600):
        """Verify a token and return the email if valid"""
        try:
            email = self.serializer.loads(token, salt='email-verification', max_age=max_age)
            return email
        except:
            return None
    
    def send_login_email(self, email, login_url):
        """Send login email with magic link"""
        if not MAIL_AVAILABLE or not self.mail:
            # For development: just print the login URL
            print(f"\n🔗 LOGIN LINK FOR {email}:")
            print(f"   {login_url}")
            print("   (Email sending disabled in development mode)\n")
            return True
            
        try:
            msg = Message(
                subject='🔐 Your SiteGen Login Link',
                recipients=[email],
                html=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2563eb;">Welcome to SiteGen!</h2>
                    <p>Click the link below to log in to your account:</p>
                    <a href="{login_url}" 
                       style="display: inline-block; background: #2563eb; color: white; 
                              padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                        🚀 Log In to SiteGen
                    </a>
                    <p><small>This link will expire in 1 hour for security.</small></p>
                    <p><small>If you didn't request this, please ignore this email.</small></p>
                </div>
                '''
            )
            self.mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_download_email(self, email, download_url, site_id):
        """Send download email with website files link"""
        if not MAIL_AVAILABLE or not self.mail:
            # For development: just print the download URL
            print(f"\n📥 DOWNLOAD LINK FOR {email}:")
            print(f"   {download_url}")
            print(f"   Site ID: {site_id}")
            print("   (Email sending disabled in development mode)\n")
            return True
            
        try:
            msg = Message(
                subject='📥 Your Website Download Link - SiteGen',
                recipients=[email],
                html=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2563eb;">Your Website is Ready!</h2>
                    <p>Thank you for using SiteGen! Your website files are ready to download.</p>
                    <a href="{download_url}" 
                       style="display: inline-block; background: #2563eb; color: white; 
                              padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                        📥 Download Your Website
                    </a>
                    <p><strong>What's included:</strong></p>
                    <ul>
                        <li>Complete HTML & CSS files</li>
                        <li>All images and assets</li>
                        <li>Ready to upload to any web host</li>
                    </ul>
                    <p><small>This download link will expire in 1 hour for security.</small></p>
                    <p><small>Need hosting? Consider our $49/month hosted option with blog CMS and analytics!</small></p>
                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                    <p style="font-size: 12px; color: #666;">
                        SiteGen - Professional websites in minutes<br>
                        If you didn't request this download, please ignore this email.
                    </p>
                </div>
                '''
            )
            self.mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending download email: {e}")
            return False
    
    def create_or_get_user(self, email):
        """Create user if doesn't exist, or get existing user"""
        try:
            # Check if user exists
            response = self.supabase.table('users').select('*').eq('email', email).execute()
            
            if response.data:
                # User exists, update last_login
                user = response.data[0]
                self.supabase.table('users').update({
                    'last_login': datetime.now().isoformat()
                }).eq('id', user['id']).execute()
                return user
            else:
                # Create new user
                user_data = {
                    'email': email,
                    'created_at': datetime.now().isoformat(),
                    'last_login': datetime.now().isoformat(),
                    'is_active': True
                }
                response = self.supabase.table('users').insert(user_data).execute()
                return response.data[0]
                
        except Exception as e:
            print(f"Error creating/getting user: {e}")
            return None
    
    def get_user_sites(self, user_id):
        """Get all sites created by a user"""
        try:
            response = self.supabase.table('generated_sites').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error getting user sites: {e}")
            return []
    
    def save_user_site(self, user_id, site_data):
        """Save a generated site to the user's account"""
        try:
            site_record = {
                'user_id': user_id,
                'site_id': site_data['site_id'],
                'business_name': site_data.get('business_name', 'Untitled Site'),
                'site_url': site_data['site_url'],
                'business_data': site_data,
                'created_at': datetime.now().isoformat()
            }
            response = self.supabase.table('generated_sites').insert(site_record).execute()
            return response.data[0]
        except Exception as e:
            print(f"Error saving user site: {e}")
            return None

def init_auth_tables(supabase_client):
    """Initialize required database tables for authentication"""
    # This would typically be done via SQL migrations
    # For demo purposes, we'll assume tables exist or are created manually
    
    # Users table schema:
    # - id (uuid, primary key)
    # - email (text, unique)
    # - created_at (timestamp)
    # - last_login (timestamp)
    # - is_active (boolean)
    
    # Generated sites table schema:
    # - id (uuid, primary key)
    # - user_id (uuid, foreign key to users)
    # - site_id (text, unique)
    # - business_name (text)
    # - site_url (text)
    # - business_data (jsonb)
    # - created_at (timestamp)
    
    print("🔧 Auth tables should be created manually in Supabase dashboard")
    print("📋 Users table: id, email, created_at, last_login, is_active")
    print("📋 Generated_sites table: id, user_id, site_id, business_name, site_url, business_data, created_at")