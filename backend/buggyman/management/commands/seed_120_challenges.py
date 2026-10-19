from django.core.management.base import BaseCommand
from django.db import connection
from buggyman.models import Challenge
from buggyman.data import get_all_120_challenges

class Command(BaseCommand):
    help = 'Seed database with 120 high-quality real-world software engineering challenges'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Delete existing challenges before seeding',
        )

    def handle(self, *args, **options):
        self.stdout.write('Seeding 120 Real-World Software Engineering Challenges...')

        if options['replace']:
            self.stdout.write('Clearing existing challenges...')
            Challenge.objects.all().delete()

        # 1. Purge legacy duplicates beyond 120 to preserve exact count of 120
        purged = Challenge.objects.filter(id__gt=120).delete()
        if purged[0] > 0:
            self.stdout.write(self.style.WARNING(f'Purged {purged[0]} legacy challenges with id > 120'))

        # 2. Load all 120 real-world challenges
        challenges_data = get_all_120_challenges()
        self.stdout.write(f'Loaded {len(challenges_data)} challenges from buggyman.data')

        # 3. Upsert all 120 challenges to DB (preserves user progress, auth, and submissions)
        upserted_count = 0
        for cdict in challenges_data:
            Challenge.objects.update_or_create(
                id=cdict['id'],
                defaults=cdict
            )
            upserted_count += 1

        # 4. Reset and align PostgreSQL auto-increment sequence to avoid duplicate key conflicts
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT setval(
                        pg_get_serial_sequence('buggyman_challenge', 'id'),
                        COALESCE((SELECT MAX(id) FROM buggyman_challenge), 1),
                        true
                    );
                """)

        total_db_count = Challenge.objects.count()
        easy_count = Challenge.objects.filter(difficulty='Easy').count()
        med_count = Challenge.objects.filter(difficulty='Medium').count()
        hard_count = Challenge.objects.filter(difficulty='Hard').count()

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded {upserted_count} challenges!\n'
            f'Total in DB: {total_db_count} (Easy: {easy_count}, Medium: {med_count}, Hard: {hard_count})'
        ))
