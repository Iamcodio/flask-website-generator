"""
SiteGen Flask Application Package
Professional website generator with email marketing integration
"""

from flask import Flask
import os
from datetime import datetime

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    
    # Configure file upload
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    from app.services.database import get_supabase_client
    from app.services.auth import TokenAuth
    
    supabase_client = get_supabase_client()
    auth = TokenAuth(app, supabase_client)
    
    # Store in app context for access in views
    app.supabase_client = supabase_client
    app.auth = auth
    
    # Register blueprints
    from app.views.main import main_bp
    from app.views.auth import auth_bp
    from app.views.admin import admin_bp
    from app.views.analytics import analytics_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(analytics_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for Docker and monitoring"""
        from flask import jsonify
        from app.services.redis_service import redis_service
        from app.services.supabase_service import supabase_service
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'app': 'running',
                'redis': 'connected' if redis_service.is_enabled() else 'disconnected',
                'supabase': 'connected' if supabase_service.is_enabled() else 'disconnected'
            }
        }
        
        # Check if all critical services are running
        if not all(v == 'connected' or v == 'running' for v in health_status['services'].values()):
            health_status['status'] = 'degraded'
            
        return jsonify(health_status)
    
    # Error handlers
    @app.errorhandler(413)
    def too_large(e):
        from flask import flash, redirect, url_for
        flash('File is too large. Please upload images smaller than 16MB.', 'error')
        return redirect(url_for('main.capture_business_info'))
    
    return app