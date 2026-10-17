from django.core.management.base import BaseCommand
from django.core.management import call_command
from buggyman.models import User, Challenge, Notification, Submission

class Command(BaseCommand):
    help = 'Seed database with initial challenges, users, and notifications'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # 1. Create Default User (Jane Doe)
        user, created = User.objects.get_or_create(
            username='janedoe',
            defaults={
                'email': 'jane.doe@college.edu',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'college': 'State Technical University',
                'bio': 'Aspiring Full Stack Engineer. Lover of logic puzzles and debugging challenge marathons.',
                'avatar': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150',
                'total_score': 780,
                'challenges_solved': 12,
                'streak': 5,
                'skills': {
                    'React': 80,
                    'Django': 60,
                    'NodeJS': 45,
                    'CSS': 70
                },
                'activities': [
                    { 'id': 1, 'text': 'Completed "Fix React State Updates"', 'time': '2 hours ago', 'xp': 100 },
                    { 'id': 2, 'text': 'Unlocked "Bug Squasher" Badge', 'time': '1 day ago', 'xp': 50 },
                    { 'id': 3, 'text': 'Solved "Express Middlewares" challenge', 'time': '3 days ago', 'xp': 200 }
                ],
                'badges': [
                    { 'name': 'First Bug Defeated', 'desc': 'Resolved your first bug', 'icon': '🐞', 'date': 'Jul 01, 2026' },
                    { 'name': 'Five Day Streak', 'desc': 'Debugged 5 days in a row', 'icon': '🔥', 'date': 'Jul 05, 2026' },
                    { 'name': 'AI Explorer', 'desc': 'Used AI hints 10 times', 'icon': '🤖', 'date': 'Jul 08, 2026' }
                ]
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write('Created user: janedoe (password: password123)')

        # 2. Create Leaderboard Competitors
        leaderboard_users = [
            {'username': 'alexrivera', 'email': 'alex@mit.edu', 'first_name': 'Alex', 'last_name': 'Rivera', 'score': 1450, 'solved': 22, 'streak': 12, 'college': 'MIT'},
            {'username': 'samchen', 'email': 'sam@stanford.edu', 'first_name': 'Sam', 'last_name': 'Chen', 'score': 1220, 'solved': 18, 'streak': 8, 'college': 'Stanford'},
            {'username': 'devonsmith', 'email': 'devon@gatech.edu', 'first_name': 'Devon', 'last_name': 'Smith', 'score': 650, 'solved': 9, 'streak': 3, 'college': 'Georgia Tech'},
            {'username': 'liwei', 'email': 'li@caltech.edu', 'first_name': 'Li', 'last_name': 'Wei', 'score': 580, 'solved': 7, 'streak': 2, 'college': 'Caltech'},
        ]

        for lu in leaderboard_users:
            u, c = User.objects.get_or_create(
                username=lu['username'],
                defaults={
                    'email': lu['email'],
                    'first_name': lu['first_name'],
                    'last_name': lu['last_name'],
                    'college': lu['college'],
                    'total_score': lu['score'],
                    'challenges_solved': lu['solved'],
                    'streak': lu['streak']
                }
            )
            if c:
                u.set_password('password123')
                u.save()

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
