"""
Lead capture and GDPR compliance utilities
"""

import csv
import os
from datetime import datetime
from flask import session, current_app

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
            
    except Exception as e:
        print(f"Error storing email lead: {e}")

def store_email_to_file(lead_data):
    """Store email lead to local CSV file for development"""
    filename = '.dev/email_leads.csv'
    file_exists = os.path.isfile(filename)
    
    # Ensure .dev directory exists
    os.makedirs('.dev', exist_ok=True)
    
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['email', 'site_id', 'business_name', 'industry', 'captured_at', 'status', 'consent_download', 'consent_marketing', 'consent_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(lead_data)
    
    print(f"📝 Email lead stored to {filename}: {lead_data['email']} (Marketing consent: {lead_data.get('consent_marketing', False)})")