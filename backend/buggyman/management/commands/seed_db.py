from django.core.management.base import BaseCommand
from django.core.management import call_command
from buggyman.models import User, Challenge, Notification, Submission

class Command(BaseCommand):
    help = 'Seed database with initial challenges, users, and notifications'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # 1. Database Users: Real accounts created via user registration only
        self.stdout.write('Users: Only genuine user registrations are maintained.')

        # 3. Seed 120 Challenges Bank
        call_command('seed_120_challenges', replace=True)

        # 4. Seed BugBytes Packages
        from buggyman.models import BugBytesPackage
        packages_data = [
            {
                'name': 'Starter Pack',
                'bugbytes': 5,
                'price_inr': 10.00,
                'is_best_value': False,
                'order_priority': 1,
                'mission_title': 'Starter Money-Back Mission',
                'mission_days': 7,
                'mission_challenge_count': 5,
                'mission_difficulty': 'Medium',
                'reward_amount_inr': 10.00,
            },
            {
                'name': 'Pro Debugger Pack',
                'bugbytes': 15,
                'price_inr': 25.00,
                'is_best_value': False,
                'order_priority': 2,
                'mission_title': 'Pro Money-Back Mission',
                'mission_days': 7,
                'mission_challenge_count': 5,
                'mission_difficulty': 'Hard',
                'reward_amount_inr': 25.00,
            },
            {
                'name': 'Master Pack',
                'bugbytes': 30,
                'price_inr': 45.00,
                'is_best_value': False,
                'order_priority': 3,
                'mission_title': 'Master Money-Back Mission',
                'mission_days': 14,
                'mission_challenge_count': 8,
                'mission_difficulty': 'Medium or Hard',
                'reward_amount_inr': 45.00,
            },
            {
                'name': 'Elite Engineer Pack',
                'bugbytes': 75,
                'price_inr': 99.00,
                'is_best_value': True,
                'order_priority': 4,
                'mission_title': 'Elite Money-Back Mission',
                'mission_days': 14,
                'mission_challenge_count': 10,
                'mission_difficulty': 'Hard',
                'reward_amount_inr': 99.00,
            },
        ]

        for pkg in packages_data:
            BugBytesPackage.objects.update_or_create(
                bugbytes=pkg['bugbytes'],
                defaults=pkg
            )
        self.stdout.write('Seeded BugBytes Store Packages.')
        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
