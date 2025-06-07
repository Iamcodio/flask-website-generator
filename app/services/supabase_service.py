"""
Supabase database service for production
"""
import os
from supabase import create_client, Client
from typing import Optional, Dict, List
from datetime import datetime
import uuid

class SupabaseService:
    def __init__(self):
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')
        
        if url and key:
            self.client: Client = create_client(url, key)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            
    def is_enabled(self):
        """Check if Supabase is configured and enabled"""
        return self.enabled
    
    # User Management
    def create_user(self, email: str, full_name: Optional[str] = None) -> Optional[Dict]:
        """Create a new user profile"""
        if not self.enabled:
            return None
            
        try:
            # Note: User should be created through Supabase Auth first
            # This creates the profile in our custom users table
            data = {
                'email': email,
                'full_name': full_name,
                'role': 'user'
            }
            
            result = self.client.table('users').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating user profile: {e}")
            return None
    
    # Site Management
    def create_site(self, user_id: str, business_data: Dict) -> Optional[Dict]:
        """Create a new site"""
        if not self.enabled:
            return None
            
        try:
            data = {
                'user_id': user_id,
                'business_name': business_data.get('business_name'),
                'industry': business_data.get('industry'),
                'business_data': business_data,
                'site_url': f"/sites/{business_data.get('id', str(uuid.uuid4()))}"
            }
            
            result = self.client.table('sites').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating site: {e}")
            return None
    
    def get_user_sites(self, user_id: str) -> List[Dict]:
        """Get all sites for a user"""
        if not self.enabled:
            return []
            
        try:
            result = self.client.table('sites')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting user sites: {e}")
            return []
    
    def get_site(self, site_id: str) -> Optional[Dict]:
        """Get a single site by ID"""
        if not self.enabled:
            return None
            
        try:
            result = self.client.table('sites')\
                .select('*')\
                .eq('id', site_id)\
                .single()\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error getting site: {e}")
            return None
    
    # Lead Management
    def store_email_lead(self, email: str, site_id: str, 
                        consent_download: bool = True, 
                        consent_marketing: bool = False,
                        business_name: Optional[str] = None,
                        industry: Optional[str] = None) -> Optional[Dict]:
        """Store an email lead"""
        if not self.enabled:
            return None
            
        try:
            data = {
                'email': email,
                'site_id': site_id,
                'business_name': business_name,
                'industry': industry,
                'consent_download': consent_download,
                'consent_marketing': consent_marketing,
                'consent_date': datetime.now().isoformat(),
                'status': 'free_download'
            }
            
            # Use upsert to handle duplicates
            result = self.client.table('email_leads')\
                .upsert(data, on_conflict='site_id,email')\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error storing email lead: {e}")
            return None
    
    def get_site_leads(self, site_id: str) -> List[Dict]:
        """Get all leads for a site"""
        if not self.enabled:
            return []
            
        try:
            result = self.client.table('email_leads')\
                .select('*')\
                .eq('site_id', site_id)\
                .order('captured_at', desc=True)\
                .execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting site leads: {e}")
            return []
    
    def get_all_user_leads(self, user_id: str) -> List[Dict]:
        """Get all leads for all sites owned by a user"""
        if not self.enabled:
            return []
            
        try:
            # First get user's sites
            sites = self.get_user_sites(user_id)
            site_ids = [site['id'] for site in sites]
            
            if not site_ids:
                return []
            
            # Then get leads for those sites
            result = self.client.table('email_leads')\
                .select('*, sites!inner(business_name)')\
                .in_('site_id', site_ids)\
                .order('captured_at', desc=True)\
                .execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting user leads: {e}")
            return []
    
    # Subscription Management
    def get_user_subscription(self, user_id: str) -> Optional[Dict]:
        """Get active subscription for a user"""
        if not self.enabled:
            return None
            
        try:
            result = self.client.table('subscriptions')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('status', 'active')\
                .single()\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error getting subscription: {e}")
            return None
    
    def create_subscription(self, user_id: str, plan: str = 'free') -> Optional[Dict]:
        """Create a new subscription"""
        if not self.enabled:
            return None
            
        try:
            data = {
                'user_id': user_id,
                'plan': plan,
                'status': 'active',
                'features': self._get_plan_features(plan)
            }
            
            result = self.client.table('subscriptions').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating subscription: {e}")
            return None
    
    def _get_plan_features(self, plan: str) -> Dict:
        """Get features for a subscription plan"""
        features = {
            'free': {
                'sites_limit': 1,
                'leads_limit': 100,
                'custom_domain': False,
                'analytics': False,
                'cms': False
            },
            'starter': {
                'sites_limit': 3,
                'leads_limit': 1000,
                'custom_domain': True,
                'analytics': True,
                'cms': False
            },
            'pro': {
                'sites_limit': 10,
                'leads_limit': 10000,
                'custom_domain': True,
                'analytics': True,
                'cms': True
            },
            'enterprise': {
                'sites_limit': -1,  # Unlimited
                'leads_limit': -1,  # Unlimited
                'custom_domain': True,
                'analytics': True,
                'cms': True
            }
        }
        return features.get(plan, features['free'])

# Global instance
supabase_service = SupabaseService()