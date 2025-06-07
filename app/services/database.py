import os
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Development mode - mock Supabase client
DEVELOPMENT_MODE = not (url and key)

if not DEVELOPMENT_MODE:
    from supabase import create_client, Client
else:
    print("🔧 Running in development mode - Supabase disabled")
    # Mock Supabase client for development
    class MockTable:
        def select(self, *args):
            return self
        def eq(self, *args):
            return self
        def insert(self, *args):
            return self
        def update(self, *args):
            return self
        def order(self, *args):
            return self
        def execute(self):
            return type('MockResponse', (), {'data': []})()
    
    class MockClient:
        def table(self, name):
            return MockTable()

def get_supabase_client():
    """Initialize and return Supabase client"""
    if DEVELOPMENT_MODE:
        return MockClient()
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    return create_client(url, key)

def create_user_and_business(email: str, business_data: dict):
    """Create user account and store business data"""
    supabase = get_supabase_client()
    
    try:
        # Sign up user
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": "temp-password-123!"  # Will be changed via email
        })
        
        if auth_response.user:
            # Store business data
            business_response = supabase.table('businesses').insert({
                'user_id': auth_response.user.id,
                'business_name': business_data['business_name'],
                'industry': business_data['industry'],
                'email': business_data['email'],
                'phone': business_data.get('phone'),
                'address': business_data.get('address'),
                'mission_statement': business_data.get('mission_statement'),
                'values': business_data.get('values'),
                'goals': business_data.get('goals'),
                'services': business_data.get('services'),
                'owner_name': business_data.get('owner_name'),
                'years_experience': business_data.get('years_experience'),
                'site_generated': False
            }).execute()
            
            return {
                'success': True,
                'user_id': auth_response.user.id,
                'business_id': business_response.data[0]['id'] if business_response.data else None
            }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_business_data(business_id: str):
    """Retrieve business data by ID"""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table('businesses').select("*").eq('id', business_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error retrieving business data: {e}")
        return None

def mark_site_generated(business_id: str, site_url: str):
    """Mark business site as generated and store URL"""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table('businesses').update({
            'site_generated': True,
            'site_url': site_url,
            'generated_at': 'now()'
        }).eq('id', business_id).execute()
        
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error marking site as generated: {e}")
        return None