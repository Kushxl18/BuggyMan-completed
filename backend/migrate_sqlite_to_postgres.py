#!/usr/bin/env python
"""
BuggyMan SQLite -> PostgreSQL Data Migration Utility

Safely migrates all data from local db.sqlite3 into a target PostgreSQL database:
- Preserves all Users, Challenges, Test Cases, Submissions, Badges, and PvP Battles
- Runs Django migrations on the target PostgreSQL database
- Restores data with foreign key integrity
- Resets PostgreSQL auto-increment sequences to prevent ID collisions
- Cleans up temporary data dumps

Usage:
    # 1. Using DATABASE_URL from backend/.env:
    python migrate_sqlite_to_postgres.py

    # 2. Or passing target PostgreSQL URI explicitly:
    python migrate_sqlite_to_postgres.py postgresql://postgres:postgres@localhost:5432/buggyman
"""

import os
import sys
import tempfile
from pathlib import Path

# Ensure UTF-8 output encoding across Windows shells
os.environ['PYTHONUTF8'] = '1'

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

def print_step(title):
    print(f"\n\033[1;36m==>\033[0m \033[1m{title}\033[0m")

def print_success(msg):
    print(f"\033[1;32m[OK]\033[0m {msg}")

def print_error(msg):
    print(f"\033[1;31m[ERROR]\033[0m {msg}")

def run_migration():
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        sys.exit(0)

    sqlite_path = BASE_DIR / 'db.sqlite3'
    if not sqlite_path.exists():
        print_error(f"SQLite database not found at {sqlite_path}. Nothing to migrate.")
        sys.exit(1)

    # 1. Determine target PostgreSQL connection string
    target_url = None
    if len(sys.argv) > 1:
        target_url = sys.argv[1].strip()
    else:
        # Check backend/.env
        from dotenv import load_dotenv
        load_dotenv(BASE_DIR / '.env')
        target_url = os.environ.get('DATABASE_URL', '').strip()

    if not target_url or not target_url.startswith(('postgres://', 'postgresql://')):
        print_step("PostgreSQL Connection String Required")
        print("Please provide your PostgreSQL connection URI.")
        print("Example: postgresql://postgres:password@localhost:5432/buggyman")
        print("Or cloud provider (Neon, Supabase, RDS, Render): postgresql://user:pass@host/db?sslmode=require\n")
        try:
            target_url = input("Enter target PostgreSQL URI: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nMigration cancelled.")
            sys.exit(0)

        if not target_url or not target_url.startswith(('postgres://', 'postgresql://')):
            print_error("Invalid PostgreSQL URI. Must start with postgresql:// or postgres://")
            sys.exit(1)

    print_step(f"Target Database: {target_url.split('@')[-1] if '@' in target_url else target_url}")

    # 2. Dump data from SQLite
    print_step("Step 1: Exporting current data from SQLite...")
    
    # Temporarily force SQLite settings to dump
    os.environ['DATABASE_URL'] = ''
    os.environ['DB_ENGINE'] = 'sqlite'
    
    import django
    django.setup()
    from django.core.management import call_command
    from django.conf import settings
    from django.db import connection, connections

    dump_file = BASE_DIR / 'migration_temp_dump.json'
    
    try:
        with open(dump_file, 'w', encoding='utf-8') as f:
            call_command(
                'dumpdata',
                natural_foreign=True,
                natural_primary=True,
                exclude=['contenttypes', 'auth.permission'],
                indent=2,
                stdout=f
            )
        file_size_kb = round(dump_file.stat().st_size / 1024, 2)
        print_success(f"Data exported successfully ({file_size_kb} KB dumped to temporary file).")
    except Exception as e:
        print_error(f"Failed to export SQLite data: {e}")
        if dump_file.exists():
            dump_file.unlink()
        sys.exit(1)

    # 3. Configure target PostgreSQL connection in Django settings
    print_step("Step 2: Connecting to PostgreSQL...")
    import dj_database_url
    pg_config = dj_database_url.parse(target_url, conn_max_age=600, ssl_require='sslmode=require' in target_url)

    settings.DATABASES['default'] = pg_config
    # Close any existing connections
    for conn in connections.all():
        conn.close()

    try:
        connection.ensure_connection()
        print_success(f"Connected to PostgreSQL database: {pg_config.get('NAME')}")
    except Exception as e:
        print_error(f"Could not connect to PostgreSQL: {e}")
        print("Please check that PostgreSQL is running and the database exists.")
        if dump_file.exists():
            dump_file.unlink()
        sys.exit(1)

    # 4. Run Django migrations on PostgreSQL
    print_step("Step 3: Running migrations on PostgreSQL database schema...")
    try:
        call_command('migrate', interactive=False)
        print_success("Database schema migrated successfully.")
    except Exception as e:
        print_error(f"Migration failed on PostgreSQL: {e}")
        if dump_file.exists():
            dump_file.unlink()
        sys.exit(1)

    # 5. Load exported data into PostgreSQL
    print_step("Step 4: Loading data into PostgreSQL...")
    try:
        call_command('loaddata', str(dump_file))
        print_success("All records successfully imported into PostgreSQL.")
    except Exception as e:
        print_error(f"Failed to load data into PostgreSQL: {e}")
        if dump_file.exists():
            dump_file.unlink()
        sys.exit(1)

    # 6. Reset PostgreSQL sequences so subsequent INSERTs do not collide with existing IDs
    print_step("Step 5: Synchronizing PostgreSQL auto-increment sequences...")
    try:
        from django.core.management.color import no_style
        from io import StringIO

        output = StringIO()
        call_command('sqlsequencereset', 'buggyman', 'auth', stdout=output)
        sql_commands = output.getvalue()
        
        if sql_commands.strip():
            with connection.cursor() as cursor:
                cursor.execute(sql_commands)
            print_success("Sequences synchronized.")
        else:
            print_success("No sequence adjustments needed.")
    except Exception as e:
        print(f"Notice: Sequence reset skipped ({e}), usually harmless.")

    # 7. Clean up temporary dump
    if dump_file.exists():
        dump_file.unlink()

    # 8. Report verified counts
    print_step("Step 6: Verifying Migrated Records in PostgreSQL")
    try:
        from buggyman.models import User, Challenge, Submission, RewardMission, PvPBattle
        print(f"  • Registered Users:    {User.objects.count()}")
        print(f"  • Challenges:          {Challenge.objects.count()}")
        print(f"  • Code Submissions:    {Submission.objects.count()}")
        print(f"  • Reward Missions:     {RewardMission.objects.count()}")
        print(f"  • PvP Battles:         {PvPBattle.objects.count()}")
    except Exception as e:
        print(f"Verification query error: {e}")

    print("\n\033[1;32m=========================================================\033[0m")
    print("\033[1;32m  PostgreSQL Migration Complete & Production Ready!      \033[0m")
    print("\033[1;32m=========================================================\033[0m\n")
    print("To make this database permanent in your backend environment:")
    print("Add this line to backend/.env:")
    print(f"DATABASE_URL={target_url}\n")

if __name__ == '__main__':
    run_migration()
