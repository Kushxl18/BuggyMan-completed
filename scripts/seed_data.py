import os
import sys
import django

sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command

if __name__ == '__main__':
    print("Seeding database via scripts/seed_data.py...")
    call_command('seed_db')
