"""
Redis caching and rate limiting service using Upstash
"""
import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify
import redis

class RedisService:
    def __init__(self):
        # Try Upstash first, then local Redis
        self.upstash_url = os.environ.get('UPSTASH_REDIS_REST_URL')
        self.upstash_token = os.environ.get('UPSTASH_REDIS_REST_TOKEN')
        self.redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        
        self.client = None
        self.is_upstash = False
        
        try:
            if self.upstash_url and self.upstash_token:
                # Use Upstash REST API
                self.is_upstash = True
                print("🔴 Using Upstash Redis")
            else:
                # Use standard Redis
                self.client = redis.from_url(self.redis_url)
                self.client.ping()
                print("🔴 Using local Redis")
        except Exception as e:
            print(f"⚠️ Redis not available: {e}")
            self.client = None
    
    def is_enabled(self):
        """Check if Redis is available"""
        return self.client is not None or self.is_upstash
    
    def _make_key(self, prefix: str, *args) -> str:
        """Create a consistent key format"""
        parts = [prefix] + [str(arg) for arg in args]
        return ":".join(parts)
    
    # Caching Methods
    def cache_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set a value in cache with TTL (in seconds)"""
        if not self.is_enabled():
            return False
        
        try:
            if self.is_upstash:
                # Use Upstash REST API via MCP
                from app.services.upstash_mcp import upstash_run_command
                serialized = json.dumps(value)
                return upstash_run_command(['SET', key, serialized, 'EX', str(ttl)])
            else:
                serialized = json.dumps(value)
                return self.client.setex(key, ttl, serialized)
        except Exception as e:
            print(f"❌ Cache set error: {e}")
            return False
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        if not self.is_enabled():
            return None
        
        try:
            if self.is_upstash:
                from app.services.upstash_mcp import upstash_run_command
                result = upstash_run_command(['GET', key])
                if result:
                    return json.loads(result)
            else:
                result = self.client.get(key)
                if result:
                    return json.loads(result)
        except Exception as e:
            print(f"❌ Cache get error: {e}")
        return None
    
    def cache_delete(self, key: str) -> bool:
        """Delete a key from cache"""
        if not self.is_enabled():
            return False
        
        try:
            if self.is_upstash:
                from app.services.upstash_mcp import upstash_run_command
                return upstash_run_command(['DEL', key]) > 0
            else:
                return self.client.delete(key) > 0
        except Exception as e:
            print(f"❌ Cache delete error: {e}")
            return False
    
    # Site Caching
    def cache_generated_site(self, site_id: str, html_content: str, ttl: int = 86400):
        """Cache generated site HTML (24 hour default)"""
        key = self._make_key("site", site_id, "html")
        return self.cache_set(key, html_content, ttl)
    
    def get_cached_site(self, site_id: str) -> Optional[str]:
        """Get cached site HTML"""
        key = self._make_key("site", site_id, "html")
        return self.cache_get(key)
    
    def cache_site_preview(self, business_data_hash: str, preview_data: Dict, ttl: int = 3600):
        """Cache site preview data (1 hour default)"""
        key = self._make_key("preview", business_data_hash)
        return self.cache_set(key, preview_data, ttl)
    
    def get_cached_preview(self, business_data: Dict) -> Optional[Dict]:
        """Get cached preview data"""
        # Create hash of business data for cache key
        data_str = json.dumps(business_data, sort_keys=True)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()
        
        key = self._make_key("preview", data_hash)
        return self.cache_get(key)
    
    # Rate Limiting
    def check_rate_limit(self, identifier: str, limit: int = 60, window: int = 60) -> tuple[bool, int]:
        """
        Check if rate limit is exceeded
        Returns: (is_allowed, remaining_requests)
        """
        if not self.is_enabled():
            return True, limit
        
        key = self._make_key("rate", identifier, datetime.now().strftime("%Y%m%d%H%M"))
        
        try:
            if self.is_upstash:
                from app.services.upstash_mcp import upstash_run_command
                # Increment counter
                current = upstash_run_command(['INCR', key])
                if current == 1:
                    # Set expiration on first request
                    upstash_run_command(['EXPIRE', key, str(window)])
            else:
                pipe = self.client.pipeline()
                pipe.incr(key)
                pipe.expire(key, window)
                current = pipe.execute()[0]
            
            remaining = max(0, limit - current)
            return current <= limit, remaining
        except Exception as e:
            print(f"❌ Rate limit check error: {e}")
            return True, limit
    
    # Session Storage
    def store_session_data(self, session_id: str, data: Dict, ttl: int = 7200):
        """Store session data (2 hour default)"""
        key = self._make_key("session", session_id)
        return self.cache_set(key, data, ttl)
    
    def get_session_data(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        key = self._make_key("session", session_id)
        return self.cache_get(key)
    
    # Lead Deduplication
    def check_lead_duplicate(self, email: str, site_id: str) -> bool:
        """Check if lead was recently captured (prevent duplicates)"""
        key = self._make_key("lead_check", site_id, email)
        
        if not self.is_enabled():
            return False
        
        try:
            if self.is_upstash:
                from app.services.upstash_mcp import upstash_run_command
                # Set if not exists, with 1 hour TTL
                result = upstash_run_command(['SET', key, '1', 'NX', 'EX', '3600'])
                return result is None  # None means key already existed
            else:
                # Set if not exists, with 1 hour TTL
                return not self.client.set(key, 1, nx=True, ex=3600)
        except Exception as e:
            print(f"❌ Lead duplicate check error: {e}")
            return False
    
    # Analytics Tracking
    def track_site_generation(self, industry: str):
        """Track site generation by industry"""
        if not self.is_enabled():
            return
        
        key = self._make_key("analytics", "generation", industry, datetime.now().strftime("%Y%m%d"))
        
        try:
            if self.is_upstash:
                from app.services.upstash_mcp import upstash_run_command
                upstash_run_command(['INCR', key])
            else:
                self.client.incr(key)
        except Exception as e:
            print(f"❌ Analytics tracking error: {e}")

# Decorators for Flask routes
def cache_response(ttl: int = 300):
    """Cache Flask response decorator"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            redis_service = RedisService()
            if not redis_service.is_enabled():
                return f(*args, **kwargs)
            
            # Create cache key from route + args
            cache_key = f"response:{request.path}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached = redis_service.cache_get(cache_key)
            if cached:
                return cached
            
            # Generate response
            response = f(*args, **kwargs)
            
            # Cache it
            redis_service.cache_set(cache_key, response, ttl)
            
            return response
        return wrapper
    return decorator

def rate_limit(limit: int = 60, window: int = 60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            redis_service = RedisService()
            
            # Use IP address or user ID as identifier
            identifier = request.remote_addr
            if hasattr(request, 'user_id'):
                identifier = f"user:{request.user_id}"
            
            allowed, remaining = redis_service.check_rate_limit(identifier, limit, window)
            
            if not allowed:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': window
                }), 429
            
            # Add rate limit headers
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(limit)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                response.headers['X-RateLimit-Reset'] = str(int(datetime.now().timestamp()) + window)
            
            return response
        return wrapper
    return decorator

# Global instance
redis_service = RedisService()