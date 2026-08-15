import os
import sys
import django

sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if __name__ == '__main__':
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    email = os.environ.get('ADMIN_EMAIL', 'admin@buggyman.com')
    password = os.environ.get('ADMIN_PASSWORD', 'admin123')

    if not User.objects.filter(username=username).exists():
        admin_user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Admin',
            last_name='User'
        )
        print(f"Superuser '{username}' created successfully.")
    else:
        print(f"User '{username}' already exists.")
