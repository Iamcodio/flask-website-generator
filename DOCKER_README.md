# Docker Setup for Flask Website Generator

This Docker setup provides both development and production environments that closely mirror each other.

## Quick Start

### Development Environment
```bash
# Copy environment variables
cp .env.docker .env

# Start development environment
make dev

# Or manually:
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

Access:
- App: http://localhost
- Mailhog (email testing): http://localhost:8025
- Adminer (database UI): http://localhost:8080

### Production Environment
```bash
# Copy and configure production environment
cp .env.production .env
# Edit .env with your production values

# Start production environment
make prod

# Or manually:
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Architecture

### Services

1. **Web (Flask App)**
   - Development: Hot reload enabled, debug mode
   - Production: Gunicorn with 4 workers, optimized for performance
   - Both use the same Supabase database with different schemas

2. **Nginx**
   - Reverse proxy and static file serving
   - Development: Simple configuration with no caching
   - Production: Advanced configuration with caching, compression, and security headers

3. **Redis**
   - Local Redis for caching (development)
   - Falls back to Upstash Redis in production
   - Session storage and rate limiting

4. **PostgreSQL** (Development only)
   - Local database for testing without affecting Supabase
   - Mirrors Supabase schema structure

5. **Mailhog** (Development only)
   - Captures all emails sent by the application
   - Web UI to view sent emails

6. **Monitoring** (Production only)
   - Prometheus for metrics collection
   - Grafana for visualization

## Database Configuration

### Using Supabase (Recommended)
The application uses the same Supabase project for both environments:
- Development: Uses `development` schema
- Production: Uses `public` schema

### Using Local PostgreSQL (Development)
If you prefer local development:
1. Uncomment the `db` service in `docker-compose.dev.yml`
2. Update `DATABASE_URL` in `.env` to use local PostgreSQL
3. Run migrations: `make migrate`

## Common Commands

```bash
# View logs
make logs                    # All services
make logs SERVICE=web       # Specific service

# Access containers
make shell                  # Web container shell
make db-shell              # PostgreSQL shell (dev only)
make redis-cli             # Redis CLI

# Manage services
make restart SERVICE=web    # Restart a service
make down                  # Stop all services
make clean                 # Remove all containers and volumes

# Run commands
make exec SERVICE=web CMD='flask routes'  # List routes
make exec SERVICE=web CMD='pytest'        # Run tests
```

## Environment Variables

### Required
- `SECRET_KEY`: Flask secret key for sessions
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Supabase anonymous key
- `UPSTASH_REDIS_REST_URL`: Upstash Redis URL
- `UPSTASH_REDIS_REST_TOKEN`: Upstash Redis token

### Optional
- `DATABASE_URL`: PostgreSQL connection string (if not using Supabase)
- `REDIS_URL`: Redis connection string (if not using Upstash)
- `MAIL_*`: Email configuration

## SSL/HTTPS Setup (Production)

1. Obtain SSL certificates (e.g., Let's Encrypt)
2. Place certificates in `nginx/certs/`
3. Update `nginx/sites-enabled/flask-app.conf` to enable HTTPS
4. Update `APP_URL` in `.env` to use HTTPS

## Deployment Checklist

- [ ] Generate secure `SECRET_KEY`
- [ ] Configure production Supabase credentials
- [ ] Set up production Redis (Upstash or self-hosted)
- [ ] Configure email service (SendGrid, AWS SES, etc.)
- [ ] Set up domain and SSL certificates
- [ ] Configure monitoring (optional)
- [ ] Set up backups for uploaded files
- [ ] Review and adjust rate limits
- [ ] Test health check endpoint: `/health`

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs web

# Rebuild image
make build ENV=dev
```

### Database connection issues
```bash
# Check if Supabase is accessible
curl https://your-project.supabase.co/rest/v1/

# Test local PostgreSQL
make db-shell
\l  # List databases
```

### Permission issues
```bash
# Fix file permissions
docker exec flask_app_dev chown -R flaskuser:flaskuser /app
```

### Redis connection issues
```bash
# Check Redis connectivity
make redis-cli
PING  # Should return PONG
```

## Performance Tuning

### Production Optimizations
1. Adjust Gunicorn workers based on CPU cores
2. Configure Nginx caching for static assets
3. Enable CDN for generated sites
4. Use Redis for session storage
5. Enable Gzip compression

### Monitoring
- Access Grafana: http://localhost:3000 (admin/admin)
- View Prometheus metrics: http://localhost:9090
- Application metrics endpoint: `/metrics` (if enabled)