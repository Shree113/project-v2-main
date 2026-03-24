#!/usr/bin/env bash
# exit on error
set -o errexit

# [C2/H6] Change to backend directory since script is run from project root
cd backend

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# [C2/H6] Robust superuser creation with fallback to hardcoded defaults
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
u = '${DJANGO_SUPERUSER_USERNAME:-admin}';
e = '${DJANGO_SUPERUSER_EMAIL:-admin@example.com}';
p = '${DJANGO_SUPERUSER_PASSWORD:-admin123}';
if not User.objects.filter(username=u).exists():
    User.objects.create_superuser(u, e, p)
    print(f'Superuser {u} created successfully.')
else:
    print(f'Superuser {u} already exists.')
"