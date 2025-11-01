#!/bin/bash
set -e

echo "🔧 Running database migrations..."
python manage.py migrate --noinput

# ✅ Seed data only if not already seeded
echo "🌱 Checking if initial data needs to be seeded..."
if ! python manage.py shell -c "from accounts.models import User; exit(0 if User.objects.exists() else 1)"; then
    echo "🌱 Seeding initial data..."
    python manage.py seed || echo "⚠️ Seeding failed, skipping..."
else
    echo "✅ Initial data already seeded, skipping..."
fi

echo "🎯 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🌍 Compiling Languages..."
django-admin compilemessages || echo "⚠️ Failed to compile translations, skipping..."

echo "🚀 Starting Gunicorn server..."
exec gunicorn project.wsgi:application --bind 0.0.0.0:8080
