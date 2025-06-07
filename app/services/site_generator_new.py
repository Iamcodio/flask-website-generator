import os
import shutil
from datetime import datetime
import re

class SiteGenerator:
    def __init__(self, business_data):
        self.business_data = business_data
        self.site_id = business_data.get('id', 'demo')
        
    def generate_site(self):
        """Generate a complete static site from business data"""
        # Create site directory
        site_dir = f"generated_sites/{self.site_id}"
        os.makedirs(site_dir, exist_ok=True)
        
        # Generate HTML
        html_content = self._generate_html()
        
        # Generate CSS with custom colors
        css_content = self._generate_css()
        
        # Write files
        with open(f"{site_dir}/index.html", "w", encoding='utf-8') as f:
            f.write(html_content)
            
        with open(f"{site_dir}/styles.css", "w", encoding='utf-8') as f:
            f.write(css_content)
            
        # Copy placeholder images
        self._copy_placeholder_images(site_dir)
        
        return {
            'site_url': f"/generated_sites/{self.site_id}/index.html",
            'files': ['index.html', 'styles.css'],
            'directory': site_dir
        }
    
    def _generate_html(self):
        """Generate semantic HTML with BEM naming convention"""
        business = self.business_data
        
        # Parse services and values
        services_list = self._parse_list(business.get('services', ''))
        values_list = self._parse_list(business.get('values', ''))
        
        # Generate sections
        header_html = self._generate_header()
        hero_html = self._generate_hero()
        features_html = self._generate_features(values_list)
        about_html = self._generate_about()
        services_html = self._generate_services(services_list)
        testimonials_html = self._generate_testimonials()
        team_html = self._generate_team() if business.get('owner_name') else ''
        contact_html = self._generate_contact()
        footer_html = self._generate_footer()
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{business.get('business_name', 'Business')} - {self._get_industry_tagline()}</title>
    <meta name="description" content="{business.get('mission_statement', 'Professional services for your needs')}">
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700&family=Open+Sans:wght@400;500;600&display=swap" rel="stylesheet">
    
    <!-- Stylesheet -->
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    {header_html}
    
    <main>
        {hero_html}
        {features_html}
        {about_html}
        {services_html}
        {testimonials_html}
        {team_html}
        {contact_html}
    </main>
    
    {footer_html}
    
    <script>
        // Mobile menu toggle
        const toggle = document.querySelector('.nav__toggle');
        const nav = document.querySelector('.nav__list');
        
        toggle?.addEventListener('click', () => {{
            nav.classList.toggle('nav__list--active');
            toggle.setAttribute('aria-expanded', 
                toggle.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'
            );
        }});
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                    // Close mobile menu if open
                    nav.classList.remove('nav__list--active');
                }}
            }});
        }});
    </script>
</body>
</html>'''

    def _generate_header(self):
        """Generate header with navigation"""
        business_name = self.business_data.get('business_name', 'Business')
        
        return f'''
    <header class="header">
        <div class="container">
            <div class="header__content">
                <a href="/" class="header__brand">
                    <img src="logo.png" alt="{business_name} logo" class="header__logo">
                    <span class="header__name">{business_name}</span>
                </a>
                
                <nav class="nav" aria-label="Main navigation">
                    <ul class="nav__list">
                        <li class="nav__item"><a href="#services" class="nav__link">Services</a></li>
                        <li class="nav__item"><a href="#about" class="nav__link">About</a></li>
                        <li class="nav__item"><a href="#testimonials" class="nav__link">Reviews</a></li>
                        <li class="nav__item"><a href="#contact" class="nav__link">Contact</a></li>
                    </ul>
                    
                    <button class="nav__toggle" aria-label="Toggle menu" aria-expanded="false">
                        <span class="nav__toggle-line"></span>
                        <span class="nav__toggle-line"></span>
                        <span class="nav__toggle-line"></span>
                    </button>
                </nav>
            </div>
        </div>
    </header>'''

    def _generate_hero(self):
        """Generate hero section with industry-specific content"""
        headline = self._get_industry_headline()
        promise = self._get_industry_promise()
        
        return f'''
    <section class="hero">
        <div class="hero__background">
            <img src="hero-background.jpg" alt="Professional service background" class="hero__image">
        </div>
        <div class="container">
            <div class="hero__content">
                <h1 class="hero__title">{headline}</h1>
                <p class="hero__subtitle">{promise}</p>
                <a href="#contact" class="button button--primary">Get Free Quote</a>
            </div>
        </div>
    </section>'''

    def _generate_features(self, values_list):
        """Generate features section from business values"""
        if not values_list:
            values_list = ['Quality Service', 'Professional Team', 'Customer Satisfaction']
        
        feature_cards = []
        icons = [
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>',
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87L7 21l1.18-6.86L2 9.27l6.91-1.01L12 2z"/></svg>',
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>'
        ]
        
        for i, value in enumerate(values_list[:3]):
            icon = icons[i % len(icons)]
            feature_cards.append(f'''
                <article class="feature-card">
                    <div class="feature-card__icon">{icon}</div>
                    <h3 class="feature-card__title">{value}</h3>
                    <p class="feature-card__description">We prioritize {value.lower()} in everything we do</p>
                </article>''')
        
        return f'''
    <section class="features">
        <div class="container">
            <h2 class="visually-hidden">Our Core Values</h2>
            <div class="features__grid">
                {"".join(feature_cards)}
            </div>
        </div>
    </section>'''

    def _generate_about(self):
        """Generate about section"""
        business = self.business_data
        mission = business.get('mission_statement', 'Providing quality services to our community')
        goals = business.get('goals', '')
        
        return f'''
    <section class="about" id="about">
        <div class="container">
            <div class="about__content">
                <div class="about__text">
                    <h2 class="about__title">About {business.get('business_name', 'Us')}</h2>
                    <div class="about__description">
                        <p>{mission}</p>
                        {f'<p>{goals}</p>' if goals else ''}
                        <p>We take pride in delivering exceptional service and building lasting relationships with our clients.</p>
                    </div>
                    <a href="#contact" class="button button--secondary">Learn More</a>
                </div>
                <div class="about__media">
                    <img src="about-image.jpg" alt="About our company" class="about__image">
                </div>
            </div>
        </div>
    </section>'''

    def _generate_services(self, services_list):
        """Generate services section"""
        if not services_list:
            services_list = self._get_default_services()
        
        service_cards = []
        for service in services_list[:6]:  # Limit to 6 services
            service_cards.append(f'''
                <article class="service-card">
                    <h3 class="service-card__title">{service}</h3>
                    <p class="service-card__description">Professional {service.lower()} services tailored to your needs.</p>
                    <ul class="service-card__features">
                        <li class="service-card__feature">Licensed & Insured</li>
                        <li class="service-card__feature">Free Estimates</li>
                        <li class="service-card__feature">Quality Guaranteed</li>
                    </ul>
                </article>''')
        
        return f'''
    <section class="services" id="services">
        <div class="container">
            <h2 class="services__title">Our Services</h2>
            <div class="services__grid">
                {"".join(service_cards)}
            </div>
        </div>
    </section>'''

    def _generate_testimonials(self):
        """Generate testimonials section"""
        business_name = self.business_data.get('business_name', 'they')
        
        testimonials = self._get_industry_testimonials()
        
        featured = testimonials[0]
        cards = []
        
        for testimonial in testimonials[1:4]:
            initials = ''.join([word[0].upper() for word in testimonial['author'].split()[:2]])
            cards.append(f'''
                <article class="testimonial-card">
                    <p class="testimonial-card__content">"{testimonial['text']}"</p>
                    <footer class="testimonial-card__footer">
                        <div class="testimonial-card__avatar">{initials}</div>
                        <div>
                            <p class="testimonial-card__author">{testimonial['author']}</p>
                            <p class="testimonial-card__rating">★★★★★</p>
                        </div>
                    </footer>
                </article>''')
        
        return f'''
    <section class="testimonials" id="testimonials">
        <div class="container">
            <h2 class="testimonials__title">What Our Clients Say</h2>
            
            <div class="testimonials__featured">
                <blockquote class="testimonials__quote">
                    "{featured['text']}"
                </blockquote>
                <p class="testimonials__author">— {featured['author']}</p>
            </div>
            
            <div class="testimonials__grid">
                {"".join(cards)}
            </div>
        </div>
    </section>'''

    def _generate_team(self):
        """Generate team section if owner info available"""
        business = self.business_data
        owner_name = business.get('owner_name')
        
        if not owner_name:
            return ''
            
        return f'''
    <section class="team" id="team">
        <div class="container">
            <h2 class="team__title">Meet the Team</h2>
            <div class="team__content">
                <div class="team__info">
                    <h3 class="team__member-name">{owner_name}</h3>
                    <p class="team__member-role">Founder & Lead Professional</p>
                    <div class="team__bio">
                        <p>With {business.get('years_experience', '10+')} years of experience in the industry, 
                        {owner_name} brings expertise and dedication to every project.</p>
                        <p>{business.get('mission_statement', 'Committed to excellence and customer satisfaction.')}</p>
                    </div>
                    <div class="team__credentials">
                        <span class="credential">Licensed Professional</span>
                        <span class="credential">{business.get('years_experience', '10+')} Years Experience</span>
                        <span class="credential">Fully Insured</span>
                    </div>
                </div>
                <div class="team__media">
                    <img src="team-image.jpg" alt="{owner_name}" class="team__image">
                </div>
            </div>
        </div>
    </section>'''

    def _generate_contact(self):
        """Generate contact section with form"""
        business = self.business_data
        email = business.get('email', 'contact@business.com')
        phone = business.get('phone', '(555) 123-4567')
        address = business.get('address', 'Your City, State')
        
        # Use FormSubmit.co for form handling - always send to admin email
        form_action = "https://formsubmit.co/iamcodio37@gmail.com"
        
        return f'''
    <section class="contact" id="contact">
        <div class="container">
            <h2 class="contact__title">Get In Touch</h2>
            <div class="contact__content">
                <div class="contact__info">
                    <h3>Ready to Get Started?</h3>
                    <p class="contact__description">
                        Contact us today for a free consultation and quote. 
                        We're here to help with all your needs.
                    </p>
                    
                    <div class="contact__details">
                        <div class="contact__item">
                            <div class="contact__icon">📞</div>
                            <div class="contact__text">
                                <strong>Phone</strong><br>
                                {phone}
                            </div>
                        </div>
                        <div class="contact__item">
                            <div class="contact__icon">✉️</div>
                            <div class="contact__text">
                                <strong>Email</strong><br>
                                {email}
                            </div>
                        </div>
                        <div class="contact__item">
                            <div class="contact__icon">📍</div>
                            <div class="contact__text">
                                <strong>Location</strong><br>
                                {address}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="contact__form-wrapper">
                    <form action="{form_action}" method="POST" class="form">
                        <input type="hidden" name="_subject" value="New inquiry from website">
                        <input type="hidden" name="_captcha" value="false">
                        <input type="hidden" name="_template" value="table">
                        
                        <div class="form__group">
                            <label for="name" class="form__label">Your Name</label>
                            <input type="text" id="name" name="name" required class="form__input">
                        </div>
                        
                        <div class="form__group">
                            <label for="email" class="form__label">Email Address</label>
                            <input type="email" id="email" name="email" required class="form__input">
                        </div>
                        
                        <div class="form__group">
                            <label for="phone" class="form__label">Phone Number</label>
                            <input type="tel" id="phone" name="phone" class="form__input">
                        </div>
                        
                        <div class="form__group">
                            <label for="message" class="form__label">Message</label>
                            <textarea id="message" name="message" required class="form__textarea" 
                                placeholder="Tell us about your project..."></textarea>
                        </div>
                        
                        <button type="submit" class="button button--primary form__button">
                            Send Message
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </section>'''

    def _generate_footer(self):
        """Generate footer section"""
        business = self.business_data
        business_name = business.get('business_name', 'Business')
        year = datetime.now().year
        
        return f'''
    <footer class="footer">
        <div class="container">
            <div class="footer__content">
                <div class="footer__brand">
                    <a href="/" class="footer__logo">
                        <img src="logo.png" alt="{business_name}" class="footer__logo-image">
                        <span class="footer__name">{business_name}</span>
                    </a>
                    <p class="footer__tagline">
                        {business.get('mission_statement', 'Quality service you can trust')}
                    </p>
                </div>
                
                <div class="footer__section">
                    <h3 class="footer__heading">Quick Links</h3>
                    <ul class="footer__list">
                        <li><a href="#services" class="footer__link">Services</a></li>
                        <li><a href="#about" class="footer__link">About Us</a></li>
                        <li><a href="#testimonials" class="footer__link">Reviews</a></li>
                        <li><a href="#contact" class="footer__link">Contact</a></li>
                    </ul>
                </div>
                
                <div class="footer__section">
                    <h3 class="footer__heading">Contact Info</h3>
                    <div class="footer__contact">
                        <p>{business.get('phone', '(555) 123-4567')}</p>
                        <p>{business.get('email', 'info@business.com')}</p>
                        <p>{business.get('address', 'Your City, State')}</p>
                    </div>
                </div>
            </div>
            
            <div class="footer__bottom">
                <p class="footer__copyright">
                    © {year} {business_name}. All rights reserved.
                </p>
            </div>
        </div>
    </footer>'''

    def _generate_css(self):
        """Load and customize CSS template"""
        primary_color = self.business_data.get('primary_color', '#0077CC')
        
        # Load the bluepipe CSS template
        css_template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'templates', 
            'bluepipe_styles.css'
        )
        
        try:
            with open(css_template_path, 'r') as f:
                css_content = f.read()
                
            # Convert hex to HSL
            hsl_value = self._hex_to_hsl(primary_color)
            
            # Replace the accent color
            css_content = css_content.replace(
                '--color-accent: 215 85% 45%;',
                f'--color-accent: {hsl_value};'
            )
            
            # Calculate darker version
            hsl_parts = hsl_value.split()
            if len(hsl_parts) == 3:
                h = hsl_parts[0]
                s = hsl_parts[1]
                l = int(hsl_parts[2].rstrip('%'))
                l_dark = max(l - 10, 20)  # Darken by 10%, min 20%
                
                css_content = css_content.replace(
                    '--color-accent-dark: 215 85% 35%;',
                    f'--color-accent-dark: {h} {s} {l_dark}%;'
                )
            
            return css_content
            
        except FileNotFoundError:
            # Fallback - this shouldn't happen
            return self._get_fallback_css()

    def _hex_to_hsl(self, hex_color):
        """Convert hex color to HSL format"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        
        # Find min/max
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Lightness
        l = (max_val + min_val) / 2
        
        if diff == 0:
            h = s = 0  # achromatic
        else:
            # Saturation
            s = diff / (2 - max_val - min_val) if l > 0.5 else diff / (max_val + min_val)
            
            # Hue
            if max_val == r:
                h = (g - b) / diff + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / diff + 2
            else:
                h = (r - g) / diff + 4
            h /= 6
        
        # Convert to CSS format
        h_deg = round(h * 360)
        s_pct = round(s * 100)
        l_pct = round(l * 100)
        
        return f"{h_deg} {s_pct}% {l_pct}%"

    def _copy_placeholder_images(self, site_dir):
        """Copy placeholder images to site directory"""
        uploaded_files = self.business_data.get('uploaded_files', {})
        
        # Image mapping
        image_files = {
            'logo.png': ('logo', 'logo_placeholder.png'),
            'hero-background.jpg': ('hero_image', 'hero_image_with_icon.png'),
            'about-image.jpg': ('about_image', 'about_us_image_placeholder.png'),
            'team-image.jpg': ('team_image', 'team_image_placeholder.png')
        }
        
        for dest_name, (upload_key, placeholder_name) in image_files.items():
            dest_path = os.path.join(site_dir, dest_name)
            
            # Check for uploaded file first
            if upload_key in uploaded_files:
                src_path = os.path.join(
                    'app', 'static', 'uploads', 
                    self.business_data['id'], 
                    uploaded_files[upload_key]
                )
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dest_path)
                    continue
            
            # Use placeholder
            placeholder_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'static', 'images', placeholder_name
            )
            
            if os.path.exists(placeholder_path):
                shutil.copy2(placeholder_path, dest_path)
            else:
                # Create simple placeholder
                with open(dest_path, 'w') as f:
                    f.write('placeholder')

    # Helper methods for content generation
    def _parse_list(self, text):
        """Parse multi-line text into list"""
        if not text:
            return []
        return [line.strip() for line in text.split('\n') if line.strip()]

    def _get_industry_tagline(self):
        """Get industry-specific tagline"""
        industry = self.business_data.get('industry', 'professional_services')
        taglines = {
            'plumbing': 'Expert Plumbing Solutions',
            'electrical': 'Reliable Electrical Services',
            'construction': 'Quality Construction & Renovation',
            'landscaping': 'Beautiful Outdoor Spaces',
            'automotive': 'Professional Auto Services',
            'cleaning': 'Spotless Cleaning Solutions',
            'retail': 'Your Local Shopping Destination',
            'healthcare': 'Caring Healthcare Services',
            'professional_services': 'Professional Excellence'
        }
        return taglines.get(industry, 'Professional Services')

    def _get_industry_headline(self):
        """Get industry-specific hero headline"""
        industry = self.business_data.get('industry', 'professional_services')
        headlines = {
            'plumbing': 'Expert Plumbing Services You Can Trust',
            'electrical': 'Professional Electrical Solutions',
            'construction': 'Building Your Dreams, One Project at a Time',
            'landscaping': 'Transform Your Outdoor Space',
            'automotive': 'Keep Your Vehicle Running Smoothly',
            'cleaning': 'A Cleaner Space, A Better Life',
            'retail': 'Quality Products, Exceptional Service',
            'healthcare': 'Your Health, Our Priority',
            'professional_services': 'Excellence in Every Detail'
        }
        return headlines.get(industry, 'Quality Service You Can Trust')

    def _get_industry_promise(self):
        """Get industry-specific value proposition"""
        industry = self.business_data.get('industry', 'professional_services')
        promises = {
            'plumbing': 'Fast, reliable plumbing repairs and installations. Available 24/7 for emergencies.',
            'electrical': 'Safe, code-compliant electrical work by licensed professionals.',
            'construction': 'From concept to completion, we deliver quality construction on time and on budget.',
            'landscaping': 'Creating beautiful, sustainable outdoor environments that enhance your property.',
            'automotive': 'Honest service, fair prices, and expert technicians you can count on.',
            'cleaning': 'Professional cleaning services that give you more time for what matters.',
            'retail': 'Find everything you need with friendly service and competitive prices.',
            'healthcare': 'Compassionate care and modern treatments for your health and wellness.',
            'professional_services': 'Dedicated professionals committed to your success.'
        }
        return promises.get(industry, 'Quality service and exceptional results you can count on.')

    def _get_default_services(self):
        """Get default services based on industry"""
        industry = self.business_data.get('industry', 'professional_services')
        services = {
            'plumbing': [
                'Emergency Plumbing Repairs',
                'Drain Cleaning',
                'Water Heater Installation',
                'Leak Detection & Repair',
                'Bathroom Remodeling',
                'Pipe Replacement'
            ],
            'electrical': [
                'Electrical Repairs',
                'Panel Upgrades',
                'Lighting Installation',
                'Outlet & Switch Replacement',
                'Safety Inspections',
                'Emergency Services'
            ],
            'landscaping': [
                'Lawn Care & Maintenance',
                'Garden Design',
                'Tree & Shrub Care',
                'Hardscape Installation',
                'Irrigation Systems',
                'Seasonal Cleanup'
            ],
            'construction': [
                'New Construction',
                'Renovations',
                'Kitchen Remodeling',
                'Bathroom Remodeling',
                'Additions',
                'General Contracting'
            ]
        }
        return services.get(industry, [
            'Consultation Services',
            'Project Management',
            'Custom Solutions',
            'Maintenance & Support',
            'Training & Education',
            'Emergency Response'
        ])

    def _get_industry_testimonials(self):
        """Get industry-specific testimonials"""
        business_name = self.business_data.get('business_name', 'they')
        industry = self.business_data.get('industry', 'professional_services')
        
        testimonial_sets = {
            'plumbing': [
                {
                    'text': f'{business_name} saved the day! Our pipe burst at 2 AM and they were here within an hour. Professional, courteous, and fair pricing. Highly recommend!',
                    'author': 'Sarah Johnson'
                },
                {
                    'text': 'Fast service and honest pricing. They fixed our water heater and explained everything clearly.',
                    'author': 'Mike Chen'
                },
                {
                    'text': 'Best plumber in town! They renovated our entire bathroom and the results are amazing.',
                    'author': 'Emily Davis'
                },
                {
                    'text': 'Reliable and professional. They always arrive on time and get the job done right.',
                    'author': 'Robert Williams'
                }
            ],
            'electrical': [
                {
                    'text': f'Had {business_name} upgrade our electrical panel. They were professional, clean, and completed the work ahead of schedule. Very impressed!',
                    'author': 'David Martinez'
                },
                {
                    'text': 'Excellent work on our home rewiring project. Safety-focused and detail-oriented.',
                    'author': 'Lisa Anderson'
                },
                {
                    'text': 'They installed our EV charger perfectly. Great communication throughout the project.',
                    'author': 'James Wilson'
                },
                {
                    'text': 'Fair pricing and quality work. They fixed issues other electricians missed.',
                    'author': 'Maria Garcia'
                }
            ],
            'landscaping': [
                {
                    'text': f'{business_name} transformed our backyard into an oasis! Their design vision and attention to detail exceeded our expectations.',
                    'author': 'Jennifer Brown'
                },
                {
                    'text': 'Our lawn has never looked better. They truly care about their work and it shows.',
                    'author': 'Tom Phillips'
                },
                {
                    'text': 'Professional team that delivers on their promises. Our garden is now the envy of the neighborhood.',
                    'author': 'Susan Lee'
                },
                {
                    'text': 'Reliable weekly maintenance and beautiful seasonal plantings. Highly recommend!',
                    'author': 'Mark Thompson'
                }
            ]
        }
        
        # Default testimonials
        default = [
            {
                'text': f'Working with {business_name} was a fantastic experience. Professional, reliable, and the results speak for themselves. I couldn\'t be happier!',
                'author': 'Alex Morgan'
            },
            {
                'text': 'Excellent service from start to finish. They listened to our needs and delivered beyond expectations.',
                'author': 'Chris Taylor'
            },
            {
                'text': 'Professional, punctual, and fair pricing. I\'ve found my go-to service provider!',
                'author': 'Pat Johnson'
            },
            {
                'text': 'The team was courteous, efficient, and did outstanding work. Highly recommended!',
                'author': 'Jordan Smith'
            }
        ]
        
        return testimonial_sets.get(industry, default)

    def _get_fallback_css(self):
        """Fallback CSS if template not found"""
        return '''/* Fallback CSS */
body { font-family: sans-serif; line-height: 1.6; margin: 0; padding: 0; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.header { background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 1rem 0; }
.hero { background: #f5f5f5; padding: 4rem 0; text-align: center; }
.button { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; }
section { padding: 3rem 0; }
h1, h2, h3 { color: #333; }
.footer { background: #333; color: white; padding: 2rem 0; margin-top: 4rem; }
'''