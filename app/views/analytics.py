"""
Analytics routes using Redis data
"""
from flask import Blueprint, render_template, jsonify
from app.services.redis_service import redis_service, cache_response
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
@cache_response(ttl=60)  # Cache for 1 minute
def dashboard():
    """Analytics dashboard"""
    # Get site generation stats
    stats = get_generation_stats()
    return render_template('analytics.html', stats=stats)

@analytics_bp.route('/api/stats')
@cache_response(ttl=60)
def api_stats():
    """API endpoint for analytics data"""
    stats = get_generation_stats()
    return jsonify(stats)

def get_generation_stats():
    """Get site generation statistics from Redis"""
    if not redis_service.is_enabled():
        return {
            'total_generations': 0,
            'by_industry': {},
            'today': 0,
            'this_week': 0
        }
    
    # This is a simplified version - in production you'd use Redis SCAN
    # to get all analytics keys and aggregate them
    industries = ['plumbing', 'electrical', 'landscaping', 'automotive', 'professional_services']
    today = datetime.now().strftime("%Y%m%d")
    
    stats = {
        'total_generations': 0,
        'by_industry': {},
        'today': 0,
        'this_week': 0
    }
    
    # Get today's stats by industry
    for industry in industries:
        key = f"analytics:generation:{industry}:{today}"
        count = redis_service.cache_get(key) or 0
        stats['by_industry'][industry] = count
        stats['today'] += count
    
    # Get weekly stats (simplified)
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
        for industry in industries:
            key = f"analytics:generation:{industry}:{date}"
            count = redis_service.cache_get(key) or 0
            stats['this_week'] += count
    
    stats['total_generations'] = stats['this_week']  # Simplified
    
    return stats