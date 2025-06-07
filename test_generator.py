#!/usr/bin/env python3

from site_generator import SiteGenerator
import json

# Test data (like BluePipe example)
test_business_data = {
    'id': 'bluepipe-demo',
    'business_name': 'BluePipe Plumbing & Heating',
    'industry': 'plumbing',
    'email': 'david@bluepipe.ie',
    'phone': '021 123 4567',
    'address': '123 Main Street, Cork, Ireland',
    'mission_statement': 'For over a decade, BluePipe Plumbing & Heating has been the trusted choice for homeowners and small businesses throughout the region.',
    'values': '''24/7 Emergency Service
Licensed Professionals  
Upfront Pricing
Quality Workmanship''',
    'goals': 'Expand service area, build long-term customer relationships, become the most trusted plumber in Cork.',
    'services': '''Emergency Plumbing Repairs
Boiler Installation and Maintenance
Bathroom Renovations
Leak Detection and Repair
Drain Cleaning Services
Water Pressure Solutions''',
    'owner_name': 'David Ryan',
    'years_experience': '15'
}

def main():
    print("🚀 Testing Site Generator...")
    
    # Generate site
    generator = SiteGenerator(test_business_data)
    result = generator.generate_site()
    
    print(f"✅ Site generated successfully!")
    print(f"📁 Directory: {result['directory']}")
    print(f"📄 Files: {result['files']}")
    print(f"🌐 URL: {result['site_url']}")
    
    # Show generated HTML snippet
    try:
        with open(f"{result['directory']}/index.html", 'r') as f:
            html_content = f.read()
            print(f"\n📝 Generated HTML preview (first 500 chars):")
            print(html_content[:500] + "...")
            
        print(f"\n🎉 Test completed! Check {result['directory']} for generated files.")
            
    except Exception as e:
        print(f"❌ Error reading generated file: {e}")

if __name__ == "__main__":
    main()