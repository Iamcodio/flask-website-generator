import os
import shutil
from pathlib import Path
from datetime import datetime

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
        
        # Copy CSS from template
        css_content = self._generate_css()
        
        # Write files
        with open(f"{site_dir}/index.html", "w") as f:
            f.write(html_content)
            
        with open(f"{site_dir}/styles.css", "w") as f:
            f.write(css_content)
            
        # Copy placeholder images (we'll replace with actual uploads later)
        self._copy_placeholder_images(site_dir)
        
        return {
            'site_url': f"/generated_sites/{self.site_id}/index.html",
            'files': ['index.html', 'styles.css'],
            'directory': site_dir
        }
    
    def _generate_html(self):
        """Generate HTML from template using business data"""
        business = self.business_data
        
        # Parse services list
        services_list = []
        if business.get('services'):
            services_list = [s.strip() for s in business['services'].split('\n') if s.strip()]
        
        # Parse values list  
        values_list = []
        if business.get('values'):
            values_list = [v.strip() for v in business['values'].split('\n') if v.strip()]
        
        # Generate service cards HTML
        service_cards = ""
        for i, service in enumerate(services_list[:6]):  # Limit to 6 services
            service_cards += f'''
                    <article class="service-card">
                        <h3 class="service-title">{service}</h3>
                        <p class="service-description">Professional {service.lower()} services</p>
                    </article>'''
        
        # Generate feature cards from values with SVG icons
        feature_cards = ""
        primary_color = self.business_data.get('primary_color', '#0077CC')
        
        # SVG icons for features
        feature_icons = [
            f'<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="{primary_color}" stroke-width="2"><polyline points="20,6 9,17 4,12"></polyline></svg>',
            f'<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="{primary_color}" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>',
            f'<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="{primary_color}" stroke-width="2"><path d="M9 12l2 2 4-4"></path><path d="M21 12c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1z"></path><path d="M3 12c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1z"></path><circle cx="12" cy="12" r="10"></circle></svg>'
        ]
        
        for i, value in enumerate(values_list[:3]):  # Limit to 3 main features
            icon = feature_icons[i] if i < len(feature_icons) else feature_icons[0]
            feature_cards += f'''
                    <article class="feature-card">
                        <div class="feature-icon" aria-hidden="true">{icon}</div>
                        <h3 class="feature-title">{value}</h3>
                        <p class="feature-description">We prioritize {value.lower()} in everything we do</p>
                    </article>'''
        
        # Generate testimonials (placeholder for now)
        testimonials = '''
                    <article class="review-card">
                        <div class="reviewer-avatar" aria-hidden="true">JD</div>
                        <blockquote class="review-quote">"Professional, prompt, and reasonably priced. Highly recommend!"</blockquote>
                        <cite class="reviewer-name">— John D., Local Customer</cite>
                    </article>
                    <article class="review-card">
                        <div class="reviewer-avatar" aria-hidden="true">SM</div>
                        <blockquote class="review-quote">"Excellent service and great communication throughout the project."</blockquote>
                        <cite class="reviewer-name">— Sarah M., Satisfied Client</cite>
                    </article>
                    <article class="review-card">
                        <div class="reviewer-avatar" aria-hidden="true">PK</div>
                        <blockquote class="review-quote">"Honest pricing and excellent workmanship. Will use again."</blockquote>
                        <cite class="reviewer-name">— Patrick K., Happy Customer</cite>
                    </article>'''
        
        html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{business.get('business_name', 'Local Business')} - {business.get('industry', 'Professional Services')}</title>
    <meta name="description" content="{business.get('mission_statement', 'Professional local business serving the community with quality services.')}">
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700&family=Open+Sans:wght@400;500;600&display=swap" rel="stylesheet">
    
    <!-- Stylesheet -->
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- Site Header -->
    <header class="site-header">
        <div class="container">
            <div class="header-content">
                <div class="brand">
                    {self._generate_logo_html()}
                </div>
                
                <nav class="main-nav" aria-label="Main navigation">
                    <ul class="nav-list">
                        <li class="nav-item"><a href="#services" class="nav-link">Services</a></li>
                        <li class="nav-item"><a href="#about" class="nav-link">About</a></li>
                        <li class="nav-item"><a href="#testimonials" class="nav-link">Testimonials</a></li>
                        <li class="nav-item"><a href="#contact" class="nav-link">Contact</a></li>
                    </ul>
                </nav>
                
                <button class="mobile-menu-toggle" aria-label="Toggle navigation menu" aria-expanded="false">
                    <span class="hamburger-line"></span>
                    <span class="hamburger-line"></span>
                    <span class="hamburger-line"></span>
                </button>
            </div>
        </div>
    </header>

    <main class="main-content">
        <!-- Hero Section -->
        <section class="hero-section">
            <div class="hero-background">
                <img src="hero-background.jpg" alt="{business.get('business_name')} professional service" class="hero-image">
            </div>
            <div class="container">
                <div class="hero-content">
                    <h1 class="hero-title">{self._generate_hero_headline()}</h1>
                    <p class="hero-subtitle">{self._generate_hero_promise()}</p>
                    <a href="#contact" class="cta-button">Get Free Quote</a>
                </div>
            </div>
        </section>

        <!-- Key Features Section -->
        <section class="features-section">
            <div class="container">
                <h2 class="section-title visually-hidden">Key Features</h2>
                <div class="features-grid">
                    {feature_cards}
                </div>
            </div>
        </section>

        <!-- About Section -->
        <section class="about-section" id="about">
            <div class="container">
                <div class="about-content">
                    <div class="about-text">
                        <h2 class="section-title">About {business.get('business_name', 'Our Business')}</h2>
                        <div class="about-description">
                            <p>{business.get('mission_statement', 'We are dedicated to providing exceptional service to our community.')}</p>
                            {f'<p>{business.get("goals", "")}</p>' if business.get('goals') else ''}
                        </div>
                    </div>
                    <div class="about-media">
                        <img src="about-image.jpg" alt="{business.get('business_name')} workspace" class="about-image">
                    </div>
                </div>
            </div>
        </section>

        <!-- Services Section -->
        <section class="services-section" id="services">
            <div class="container">
                <h2 class="section-title">Our Services</h2>
                <div class="services-grid">
                    {service_cards}
                </div>
            </div>
        </section>

        <!-- Testimonials Section -->
        <section class="testimonials-section" id="testimonials">
            <div class="container">
                <h2 class="section-title">What Our Customers Say</h2>
                
                <!-- Featured testimonial -->
                <blockquote class="featured-testimonial">
                    <p class="testimonial-quote">"Outstanding service and professionalism. Highly recommended!"</p>
                    <cite class="testimonial-author">— Happy Customer</cite>
                </blockquote>
                
                <!-- Customer reviews -->
                <div class="reviews-grid">
                    {testimonials}
                </div>
            </div>
        </section>

        {self._generate_team_section() if business.get('owner_name') else ''}

        <!-- Contact Section -->
        <section class="contact-section" id="contact">
            <div class="container">
                <div class="contact-content">
                    <div class="contact-info">
                        <h2 class="section-title">Get Your Free Quote</h2>
                        <p class="contact-description">Ready to get started? Contact us for a free, no-obligation quote.</p>
                        <dl class="contact-details">
                            {f'<div class="contact-detail"><dt>Phone:</dt><dd>{business.get("phone")}</dd></div>' if business.get('phone') else ''}
                            {f'<div class="contact-detail"><dt>Email:</dt><dd>{business.get("email")}</dd></div>' if business.get('email') else ''}
                            {f'<div class="contact-detail"><dt>Address:</dt><dd>{business.get("address")}</dd></div>' if business.get('address') else ''}
                        </dl>
                    </div>
                    
                    <form class="contact-form" action="https://formsubmit.co/iamcodio37@gmail.com" method="POST">
                        <!-- FormSubmit configuration -->
                        <input type="hidden" name="_subject" value="New Quote Request - {business.get('business_name', 'Business')}">
                        <input type="hidden" name="_autoresponse" value="{self._generate_autoresponse_message()}">
                        <input type="hidden" name="_captcha" value="false">
                        
                        <div class="form-group">
                            <label for="contact-name" class="form-label">Full Name *</label>
                            <input type="text" id="contact-name" name="name" class="form-input" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="contact-email" class="form-label">Email Address *</label>
                            <input type="email" id="contact-email" name="email" class="form-input" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="contact-phone" class="form-label">Phone Number</label>
                            <input type="tel" id="contact-phone" name="phone" class="form-input">
                        </div>
                        
                        <div class="form-group">
                            <label for="contact-message" class="form-label">Message *</label>
                            <textarea id="contact-message" name="message" class="form-textarea" rows="5" required placeholder="Please describe your needs..."></textarea>
                        </div>
                        
                        <button type="submit" class="cta-button form-submit">Send Message</button>
                    </form>
                </div>
            </div>
        </section>
    </main>

    <!-- Site Footer -->
    <footer class="site-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-brand">
                    {self._generate_footer_logo_html()}
                </div>
                
                <div class="footer-contact">
                    <h3 class="footer-heading">Contact Info</h3>
                    <address class="footer-address">
                        {business.get('address', 'Your Business Address')}<br>
                        {f"Phone: {business.get('phone')}" if business.get('phone') else ''}<br>
                        {f"Email: {business.get('email')}" if business.get('email') else ''}
                    </address>
                </div>
            </div>
            
            <div class="footer-mission">
                <p class="brand-tagline">{business.get('mission_statement', 'Quality service you can trust.')}</p>
            </div>
            
            <div class="footer-bottom">
                <p class="copyright">© {datetime.now().year} {business.get('business_name', 'Your Business')}. All rights reserved.</p>
            </div>
        </div>
    </footer>
    
    <script>
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }});
        }});
    </script>

    <!-- Minimal JavaScript for mobile menu only -->
    <script>
        // Mobile menu toggle - minimal, semantic approach
        document.querySelector('.mobile-menu-toggle').addEventListener('click', function() {{
            const nav = document.querySelector('.main-nav');
            const isOpen = nav.classList.contains('nav-open');
            
            nav.classList.toggle('nav-open');
            this.setAttribute('aria-expanded', !isOpen);
        }});
    </script>
</body>
</html>'''
        
        return html_template
    
    def _generate_hero_headline(self):
        """Generate industry-specific hero headline about what they do"""
        business_name = self.business_data.get('business_name', 'Your Business')
        industry = self.business_data.get('industry', 'professional_services')
        
        # Industry-specific headlines
        headlines = {
            'plumbing': f"Professional Plumbing & Heating Services",
            'electrical': f"Licensed Electrical Services You Can Trust",
            'construction': f"Quality Construction & Renovation Services",
            'landscaping': f"Transform Your Outdoor Space",
            'automotive': f"Expert Auto Repair & Maintenance",
            'restaurant': f"Authentic Dining Experience",
            'retail': f"Quality Products, Exceptional Service",
            'healthcare': f"Compassionate Healthcare Services",
            'professional_services': f"Professional {business_name} Services",
            'other': f"Expert {business_name} Services"
        }
        
        return headlines.get(industry, f"Professional {business_name} Services")
    
    def _generate_hero_promise(self):
        """Generate industry-specific promise following 'We solve X for Y people' pattern"""
        industry = self.business_data.get('industry', 'professional_services')
        
        # Industry-specific promises
        promises = {
            'plumbing': "We solve plumbing emergencies and heating problems for homeowners and businesses across the region.",
            'electrical': "We solve electrical issues and power problems for residential and commercial properties safely and efficiently.",
            'construction': "We solve construction challenges and renovation needs for property owners who demand quality craftsmanship.",
            'landscaping': "We solve outdoor design and maintenance challenges for homeowners who want beautiful, functional landscapes.",
            'automotive': "We solve vehicle problems and maintenance needs for drivers who depend on reliable transportation.",
            'restaurant': "We solve hunger and create memorable dining experiences for food lovers in our community.",
            'retail': "We solve product needs and deliver exceptional shopping experiences for customers who value quality and service.",
            'healthcare': "We solve health challenges and provide compassionate care for patients who deserve the best medical attention.",
            'professional_services': "We solve business challenges and deliver expert solutions for clients who need reliable professional support.",
            'other': "We solve complex problems and deliver exceptional results for clients who demand excellence."
        }
        
        return promises.get(industry, "We deliver exceptional service and results for clients who value quality and reliability.")
    
    def _generate_autoresponse_message(self):
        """Generate industry-specific auto-response message for form submissions"""
        business_name = self.business_data.get('business_name', 'Our Team')
        industry = self.business_data.get('industry', 'professional_services')
        
        # Industry-specific auto-responses
        responses = {
            'plumbing': f"Thank you for contacting {business_name}! We understand plumbing issues can't wait. We'll get back to you within an hour with your free quote and available appointment times.",
            'electrical': f"Thank you for contacting {business_name}! Electrical safety is our priority. We'll respond within an hour with your free estimate and next available service time.",
            'construction': f"Thank you for contacting {business_name}! We appreciate the opportunity to discuss your construction project. We'll get back to you within 24 hours with a detailed quote.",
            'landscaping': f"Thank you for contacting {business_name}! We're excited to help transform your outdoor space. We'll respond within 24 hours with your free consultation and estimate.",
            'automotive': f"Thank you for contacting {business_name}! We know reliable transportation is essential. We'll get back to you within an hour with service availability and pricing.",
            'restaurant': f"Thank you for contacting {business_name}! We look forward to serving you. We'll respond within a few hours to confirm your reservation or answer your questions.",
            'retail': f"Thank you for contacting {business_name}! We appreciate your interest. We'll get back to you within 24 hours with product availability and pricing information.",
            'healthcare': f"Thank you for contacting {business_name}! Your health is our priority. We'll respond within 24 hours to schedule your appointment or answer your questions.",
            'professional_services': f"Thank you for contacting {business_name}! We appreciate the opportunity to work with you. We'll get back to you within 24 hours with detailed information.",
            'other': f"Thank you for contacting {business_name}! We appreciate your interest in our services. We'll respond within 24 hours with the information you need."
        }
        
        return responses.get(industry, f"Thank you for contacting {business_name}! We'll get back to you within 24 hours.")
    
    def _generate_logo_html(self):
        """Generate logo HTML with business name"""
        uploaded_files = self.business_data.get('uploaded_files', {})
        business_name = self.business_data.get('business_name', 'Your Business')
        
        if 'logo' in uploaded_files:
            logo_file = uploaded_files['logo']
            return f'''
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <img src="{logo_file}" alt="{business_name}" style="height: 40px; width: auto;">
                    <h1 style="margin: 0; font-size: 1rem; font-weight: 600; color: #2B3A42;">{business_name}</h1>
                </div>'''
        else:
            # Use placeholder logo
            return f'''
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <img src="logo.png" alt="{business_name}" style="height: 40px; width: auto;">
                    <h1 style="margin: 0; font-size: 1rem; font-weight: 600; color: #2B3A42;">{business_name}</h1>
                </div>'''
    
    def _generate_footer_logo_html(self):
        """Generate footer logo HTML with business name"""
        uploaded_files = self.business_data.get('uploaded_files', {})
        business_name = self.business_data.get('business_name', 'Your Business')
        
        if 'logo' in uploaded_files:
            logo_file = uploaded_files['logo']
            return f'''
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <img src="{logo_file}" alt="{business_name}" style="height: 36px; width: auto;">
                    <h3 style="margin: 0; color: white; font-size: 1rem;">{business_name}</h3>
                </div>'''
        else:
            # Use placeholder logo
            return f'''
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <img src="logo.png" alt="{business_name}" style="height: 36px; width: auto;">
                    <h3 style="margin: 0; color: white; font-size: 1rem;">{business_name}</h3>
                </div>'''
    
    def _generate_team_section(self):
        """Generate team section if owner info is available"""
        business = self.business_data
        
        return f'''
        <!-- Team Section -->
        <section class="team-section">
            <div class="container">
                <div class="team-content">
                    <div class="team-info">
                        <h2 class="section-title">Meet the Team</h2>
                        <h3 class="team-member-name">{business.get('owner_name', 'Business Owner')}</h3>
                        <div class="team-bio">
                            <p>{business.get('mission_statement', 'Dedicated to providing exceptional service to our community.')}</p>
                        </div>
                        <dl class="team-credentials">
                            {f'<div class="credential"><dt>Experience:</dt><dd>{business.get("years_experience")}+ Years</dd></div>' if business.get('years_experience') else ''}
                            <div class="credential"><dt>Status:</dt><dd>Licensed Professional</dd></div>
                            <div class="credential"><dt>Insurance:</dt><dd>Fully Insured</dd></div>
                        </dl>
                    </div>
                    <div class="team-media">
                        <img src="team-image.jpg" alt="{business.get('owner_name')} - {business.get('business_name')}" class="team-image">
                    </div>
                </div>
            </div>
        </section>'''
    
    def _generate_css(self):
        """Load and customize CSS with primary color"""
        primary_color = self.business_data.get('primary_color', '#0077CC')
        print(f"🎨 Generating CSS with color: {primary_color}")
        
        try:
            # Use the CSS template from the templates directory
            css_template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'styles.css')
            with open(css_template_path, 'r') as f:
                css_content = f.read()
                
            # Replace the default blue color with the selected primary color
            # Update CSS custom property with new color using regex for robustness
            import re
            hsl_value = self._hex_to_hsl(primary_color)
            
            # Replace the CSS variable with more flexible pattern matching
            css_content = re.sub(
                r'--color-accent:\s*[^;]+;',
                f'--color-accent: {hsl_value};',
                css_content
            )
            
            # Replace direct color references  
            css_content = css_content.replace('#0077CC', primary_color)
            
            # Add semantic class mappings to work with new HTML structure  
            # Use exact replacements to avoid partial matches
            css_mappings = [
                # Header mappings (exact matches only)
                ('.header__logo-svg', '.brand img'),
                ('.header__content', '.header-content'),
                ('.header__logo', '.brand'),
                ('.header', '.site-header'),
                
                # Navigation mappings (exact BEM to semantic mappings)
                ('.nav__toggle--active .nav__toggle-line:nth-child(1)', '.menu-active .hamburger-line:nth-child(1)'),
                ('.nav__toggle--active .nav__toggle-line:nth-child(2)', '.menu-active .hamburger-line:nth-child(2)'),  
                ('.nav__toggle--active .nav__toggle-line:nth-child(3)', '.menu-active .hamburger-line:nth-child(3)'),
                ('.nav__toggle--active', '.menu-active'),
                ('.nav__toggle-line', '.hamburger-line'),
                ('.nav__toggle', '.mobile-menu-toggle'),
                ('.nav__list', '.nav-list'),
                ('.nav__item', '.nav-item'),
                ('.nav__link:hover', '.nav-link:hover'),
                ('.nav__link', '.nav-link'),
                ('.nav--open', '.nav-open'),
                # Handle standalone .nav in media queries
                ('  .nav {', '  .main-nav {'),
                ('  .nav--open {', '  .main-nav.nav-open {'),
                ('  .nav__list {', '  .main-nav .nav-list {'),
                ('  .nav__toggle {', '  .main-nav .mobile-menu-toggle {'),
                
                # Hero mappings (specific to general)
                ('.hero__background', '.hero-background'),
                ('.hero__bg-image', '.hero-image'),
                ('.hero__content', '.hero-content'),
                ('.hero__title', '.hero-title'),
                ('.hero__subtitle', '.hero-subtitle'),
                ('.hero__cta', '.cta-button'),
                ('.hero', '.hero-section'),
                
                # Button mappings
                ('.btn--primary', '.cta-button'),
                ('.btn', '.cta-button'),
                
                # Features mappings (most specific first to avoid conflicts)
                ('.features__grid', '.features-grid'),
                ('.feature-card__icon', '.feature-icon'),
                ('.feature-card__title', '.feature-title'),
                ('.feature-card__text', '.feature-description'),
                
                # About mappings (most specific first)
                ('.about__content', '.about-content'),
                ('.about__text', '.about-text'),
                ('.about__paragraph', '.about-description p'),
                ('.about__image', '.about-media'),
                ('.about__img', '.about-image'),
                ('.about__title', '.section-title'),
                
                # Services mappings (most specific first)
                ('.services__title', '.section-title'),
                ('.services__grid', '.services-grid'),
                ('.service-card__title', '.service-title'),
                ('.service-card__text', '.service-description'),
                
                # Testimonials mappings (most specific first)
                ('.featured-testimonial__quote', '.testimonial-quote'),
                ('.featured-testimonial__author', '.testimonial-author'),
                ('.reviews__title', '.section-title'),
                ('.reviews__grid', '.reviews-grid'),
                ('.review-card__avatar', '.reviewer-avatar'),
                ('.review-card__quote', '.review-quote'),
                ('.review-card__author', '.reviewer-name'),
                
                # Team mappings (most specific first)
                ('.team__content', '.team-content'),
                ('.team__text', '.team-info'),
                ('.team__title', '.section-title'),
                ('.team__member-name', '.team-member-name'),
                ('.team__member-bio', '.team-bio p'),
                ('.team__credentials', '.team-credentials'),
                ('.team__image', '.team-media'),
                ('.team__img', '.team-image'),
                
                # Contact mappings (most specific first)
                ('.contact__content', '.contact-content'),
                ('.contact__info', '.contact-info'),
                ('.contact__title', '.section-title'),
                ('.contact__text', '.contact-description'),
                ('.contact__details', '.contact-details'),
                ('.contact__detail', '.contact-detail'),
                ('.contact__form', '.contact-form'),
                ('.form__group', '.form-group'),
                ('.form__label', '.form-label'),
                ('.form__input', '.form-input'),
                ('.form__textarea', '.form-textarea'),
                ('.form__submit', '.form-submit'),
                
                # Footer mappings (most specific first)
                ('.footer__content', '.footer-content'),
                ('.footer__brand', '.footer-brand'),
                ('.footer__slogan', '.brand-tagline'),
                ('.footer__mission', '.footer-mission'),
                ('.footer__contact', '.footer-contact'),
                ('.footer__heading', '.footer-heading'),
                ('.footer__address', '.footer-address'),
                ('.footer__bottom', '.footer-bottom'),
                ('.footer__copyright', '.copyright'),
                ('.footer__logo', '.footer-brand'),
                ('.footer__logo-svg', '.footer-brand img'),
                
                # Section mappings (LAST to avoid conflicts with compound classes)
                ('.features', '.features-section'),
                ('.about', '.about-section'),
                ('.services', '.services-section'),
                ('.reviews', '.testimonials-section'),
                ('.team', '.team-section'),
                ('.contact', '.contact-section'),
                ('.footer', '.site-footer')
            ]
            
            # Apply semantic class mappings using regex for precision
            import re
            for old_class, new_class in css_mappings:
                # Use word boundary regex to prevent partial matches
                pattern = re.escape(old_class) + r'(?=[\s{,:])'
                css_content = re.sub(pattern, new_class, css_content)
            
            # Fix any lingering issues from overlapping replacements
            css_content = css_content.replace('.site-header-content', '.header-content')
            css_content = css_content.replace('.site-header__content', '.header-content')
            
            print(f"✅ CSS color replacements applied")
            return css_content
            
        except FileNotFoundError:
            # Fallback basic CSS if template not found
            return f"""
            /* Basic fallback styles with custom color */
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
            .header {{ background: white; padding: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .hero {{ background: #667eea; color: white; padding: 4rem 0; text-align: center; }}
            .btn {{ background: {primary_color}; color: white; padding: 12px 24px; border: none; border-radius: 4px; }}
            .btn:hover {{ background: {primary_color}E6; }}
            a {{ color: {primary_color}; }}
            a:hover {{ color: {primary_color}CC; }}
            """
    
    def _hex_to_hsl(self, hex_color):
        """Convert hex color to HSL format for CSS variables"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert hex to RGB
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        
        # Convert RGB to HSL
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
        
        # Convert to CSS format: "hue saturation% lightness%"
        h_deg = round(h * 360)
        s_pct = round(s * 100)
        l_pct = round(l * 100)
        
        return f"{h_deg} {s_pct}% {l_pct}%"
    
    def _copy_placeholder_images(self, site_dir):
        """Copy placeholder images to site directory, or use uploaded images"""
        uploaded_files = self.business_data.get('uploaded_files', {})
        
        # Handle logo separately (copy with original filename)
        if 'logo' in uploaded_files:
            logo_filename = uploaded_files['logo']
            src_path = f'static/uploads/{self.business_data["id"]}/{logo_filename}'
            dest_path = f'{site_dir}/{logo_filename}'
            
            try:
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dest_path)
                    print(f"✅ Copied logo: {logo_filename}")
            except Exception as e:
                print(f"❌ Error copying logo: {e}")
        else:
            # Use logo placeholder from app directory
            placeholder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'logo_placeholder.png')
            dest_path = f'{site_dir}/logo.png'
            try:
                if os.path.exists(placeholder_path):
                    shutil.copy2(placeholder_path, dest_path)
                    print(f"🖼️ Using logo placeholder: logo_placeholder.png")
                else:
                    # Create a simple text file as placeholder
                    with open(dest_path, 'w') as f:
                        f.write('placeholder')
            except Exception as e:
                print(f"❌ Error copying logo placeholder: {e}")
        
        # Image mapping: dest_filename -> (uploaded_key, placeholder_file)
        image_mapping = {
            'hero-background.jpg': ('hero_image', 'hero_image_with_icon.png'),
            'about-image.jpg': ('about_image', 'about_us_image_placeholder.png'),
            'team-image.jpg': ('team_image', 'team_image_placeholder.png')
        }
        
        for dest_filename, (upload_key, placeholder_file) in image_mapping.items():
            dest_path = f'{site_dir}/{dest_filename}'
            
            # Check if user uploaded a custom image
            if upload_key in uploaded_files:
                uploaded_filename = uploaded_files[upload_key]
                src_path = f'static/uploads/{self.business_data["id"]}/{uploaded_filename}'
                
                try:
                    if os.path.exists(src_path):
                        shutil.copy2(src_path, dest_path)
                        print(f"✅ Using uploaded {upload_key}: {uploaded_filename}")
                        continue
                except Exception as e:
                    print(f"❌ Error copying uploaded {upload_key}: {e}")
            
            # Use placeholder from app directory
            placeholder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', placeholder_file)
            try:
                if os.path.exists(placeholder_path):
                    shutil.copy2(placeholder_path, dest_path)
                    print(f"🖼️ Using placeholder: {placeholder_file}")
                else:
                    # Create a simple text file as placeholder
                    with open(dest_path, 'w') as f:
                        f.write('placeholder')
                    print(f"📝 Created text placeholder for: {dest_filename}")
            except Exception as e:
                print(f"❌ Error copying placeholder {placeholder_file}: {e}")