"""
Lead capture and GDPR compliance utilities
"""

import csv
import os
from datetime import datetime
from flask import session, current_app

def store_email_lead(email, site_id, consent_download=True, consent_marketing=False, business_name=None, industry=None):
    """Store email lead for marketing list with GDPR consent"""
    try:
        # Try to get business data from session if not provided
        if business_name is None or industry is None:
            try:
                business_data = session.get('business_data', {})
                if business_name is None:
                    business_name = business_data.get('business_name', 'Unknown')
                if industry is None:
                    industry = business_data.get('industry', 'Unknown')
            except RuntimeError:
                # We're outside request context, use defaults
                if business_name is None:
                    business_name = 'Unknown'
                if industry is None:
                    industry = 'Unknown'
        
        print(f"📧 Storing lead: {email} for site {site_id}")
        print(f"📊 Business: {business_name} | Industry: {industry}")
        
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
        try:
            if hasattr(current_app, 'supabase_client') and current_app.supabase_client:
                try:
                    current_app.supabase_client.table('email_leads').insert(lead_data).execute()
                    print(f"✅ Email lead stored in Supabase: {email}")
                except Exception as e:
                    print(f"⚠️ Supabase storage failed, using file backup: {e}")
                    store_email_to_file(lead_data)
            else:
                # Development mode - store in local file
                store_email_to_file(lead_data)
        except RuntimeError:
            # We're outside application context, just use file storage
            print(f"📝 Outside app context, using file storage")
            store_email_to_file(lead_data)
            
    except Exception as e:
        print(f"❌ Error storing email lead: {e}")
        import traceback
        traceback.print_exc()

def store_email_to_file(lead_data):
    """Store email lead to local CSV file for development"""
    # Use absolute path to ensure it works regardless of working directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    dev_dir = os.path.join(base_dir, '.dev')
    filename = os.path.join(dev_dir, 'email_leads.csv')
    
    print(f"📁 Using email leads file: {filename}")
    
    # Ensure .dev directory exists
    os.makedirs(dev_dir, exist_ok=True)
    
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['email', 'site_id', 'business_name', 'industry', 'captured_at', 'status', 'consent_download', 'consent_marketing', 'consent_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(lead_data)
    
    print(f"📝 Email lead stored to {filename}: {lead_data['email']} (Marketing consent: {lead_data.get('consent_marketing', False)})")
    print(f"✅ Lead data written: {lead_data}")

def capture_lead(email, site_id, consent_marketing=False, business_name=None, industry=None):
    """Wrapper function for capturing leads - always captures with download consent"""
    print(f"🎯 capture_lead called with: email={email}, site_id={site_id}, consent_marketing={consent_marketing}")
    result = store_email_lead(email, site_id, consent_download=True, consent_marketing=consent_marketing, 
                            business_name=business_name, industry=industry)
    print(f"✅ capture_lead result: {result}")
    return result

def get_all_leads():
    """Get all captured leads from CSV file"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(base_dir, '.dev', 'email_leads.csv')
    leads = []
    
    if os.path.isfile(filename):
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                leads.append(row)
    
    return leads