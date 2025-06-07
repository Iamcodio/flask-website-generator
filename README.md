# SiteGen MVP - AI Website Builder for Local Businesses

A 3-day MVP that generates professional websites for local businesses using AI and modern web technologies.

## 🚀 Features

- **Business Info Capture**: Simple form to collect business details
- **AI Site Generation**: Automatically generates HTML/CSS sites from business data
- **Live Preview**: Instant preview of generated websites
- **Mobile Responsive**: Modern, mobile-first design
- **Professional Templates**: Based on proven local business designs

## 📋 Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Docker + nginx
- **Template Engine**: Jinja2

## 🏗️ Project Structure

```
flask-app/
├── app.py                 # Main Flask application
├── site_generator.py      # Website generation logic
├── supabase_client.py     # Database integration
├── templates/             # Flask templates
│   ├── base.html
│   ├── index.html
│   ├── capture.html
│   └── preview.html
├── bluepipe/              # Example business template
│   ├── index.html
│   └── styles.css
├── generated_sites/       # Generated websites
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container setup
├── docker-compose.yml    # Multi-service deployment
├── nginx.conf           # Web server config
└── deploy.sh            # Deployment script
```

## 🛠️ Local Development

1. **Clone and setup**:
   ```bash
   cd flask-app
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the app**:
   ```bash
   python app.py
   ```

3. **Test site generation**:
   ```bash
   python test_generator.py
   ```

4. **Access the app**:
   - Main app: http://localhost:5000
   - Create site: http://localhost:5000/capture

## 🚢 Production Deployment

### Digital Ocean / VPS Deployment

1. **Server setup**:
   ```bash
   # Install Docker & Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo apt install docker-compose
   ```

2. **Deploy**:
   ```bash
   git clone <your-repo>
   cd flask-app
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Configure environment**:
   ```bash
   # Create .env file
   echo "SUPABASE_URL=your-url" > .env
   echo "SUPABASE_KEY=your-key" >> .env
   ```

### Environment Variables

- `SECRET_KEY`: Flask secret key
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key

## 📊 Database Schema (Supabase)

```sql
-- Users table (handled by Supabase Auth)

-- Businesses table
CREATE TABLE businesses (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid REFERENCES auth.users(id),
  business_name text NOT NULL,
  industry text,
  email text,
  phone text,
  address text,
  mission_statement text,
  values text,
  goals text,
  services text,
  owner_name text,
  years_experience integer,
  site_generated boolean DEFAULT false,
  site_url text,
  created_at timestamp DEFAULT now(),
  generated_at timestamp
);
```

## 🎯 MVP Scope (3 Days)

### Day 1: Core Foundation ✅
- [x] Flask app structure
- [x] Business info capture form
- [x] Basic site generation
- [x] Template system

### Day 2: Integration ✅
- [x] Site generator using real template
- [x] Preview functionality
- [x] File serving
- [x] Supabase integration setup

### Day 3: Deployment 🏗️
- [x] Docker containerization
- [x] nginx configuration
- [x] Deployment scripts
- [ ] Production testing

## 🚀 Usage Flow

1. **Landing Page**: User sees value proposition
2. **Business Form**: User fills out business details
3. **Site Generation**: System generates HTML/CSS automatically
4. **Preview**: User sees generated website in iframe
5. **Deploy**: User can deploy to production (future feature)

## 🔮 Future Features

- Email verification and user accounts
- Custom domain setup
- Site editing interface
- Payment integration
- AI-generated content improvements
- Image upload and optimization
- SEO optimization tools
- Analytics dashboard

## 📈 Success Metrics

- ✅ Site generation < 30 seconds
- ✅ Mobile-responsive output
- ✅ Professional template quality
- 🎯 User completion rate > 80%
- 🎯 Generated sites load < 3 seconds

## 🤝 Contributing

This is an MVP built in 3 days. For production use:
1. Add proper error handling
2. Implement user authentication
3. Add input validation
4. Set up monitoring
5. Add automated tests
6. Implement proper logging

## 📄 License

MIT License - Built for rapid prototyping and learning.
