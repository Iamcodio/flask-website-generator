#!/bin/bash

# Simple deployment script for Digital Ocean or any VPS

echo "🚀 Deploying SiteGen MVP..."

# Build and start containers
echo "📦 Building containers..."
docker-compose build

echo "🔄 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Test if app is running
if curl -f http://localhost:5000 > /dev/null 2>&1; then
    echo "✅ App is running successfully!"
    echo "🌐 Access your app at: http://localhost"
    echo "📊 Admin panel: http://localhost:5000"
else
    echo "❌ App failed to start. Check logs:"
    docker-compose logs
fi

echo "🏁 Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Set up domain DNS pointing to this server"
echo "  2. Configure SSL with certbot"
echo "  3. Set up Supabase environment variables"
echo "  4. Monitor with 'docker-compose logs -f'"