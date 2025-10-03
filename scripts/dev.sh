#!/bin/bash

# Development script for Django Skeleton
# Usage: ./scripts/dev.sh [uv|docker]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

case "${1:-uv}" in
    "uv")
        echo "🚀 Starting local development with uv (SQLite)..."
        cp .env.example .env
        echo "✅ Environment configured for SQLite"
        echo "📦 Installing dependencies..."
        uv sync
        echo "🗄️ Running migrations..."
        uv run python manage.py migrate
        echo "👤 Creating superuser (if not exists)..."
        echo "from accounts.models import User; user, created = User.objects.get_or_create(email='admin@example.com', defaults={'first_name': 'Admin', 'last_name': 'User', 'is_staff': True, 'is_superuser': True}); user.set_password('admin123'); user.save()" | uv run python manage.py shell || true
        echo "🌐 Starting development server..."
        echo "📍 Access: http://localhost:8000"
        echo "🔑 Admin: admin@example.com / admin123"
        uv run python manage.py runserver
        ;;
    "docker")
        echo "🐳 Starting Docker development (PostgreSQL)..."
        cp .env.docker .env
        echo "✅ Environment configured for PostgreSQL"
        echo "🏗️ Building and starting containers..."
        docker-compose up --build
        ;;
    *)
        echo "❌ Invalid option. Use: ./scripts/dev.sh [uv|docker]"
        echo "   uv     - Local development with SQLite"
        echo "   docker - Docker development with PostgreSQL"
        exit 1
        ;;
esac