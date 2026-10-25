import unittest
import json
import os
import sys

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from django.test import RequestFactory
from buggyman.models import User, FeatureChallenge, FeatureSubmission, BugBytesTransaction
from buggyman.views import (
    feature_challenges_list_view,
    feature_challenge_detail_view,
    run_feature_challenge_view,
    submit_feature_challenge_view,
    feature_challenge_hint_view,
    feature_codebase_assistant_view,
    feature_challenge_submissions_view
)
from buggyman.evaluator.feature_engine import feature_evaluator

class FeatureArenaBackendTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()
        cls.user, _ = User.objects.get_or_create(
            username='feature_qa_user',
            defaults={
                'email': 'feature_qa@buggyman.test',
                'bugbytes_balance': 100,
                'total_score': 0,
                'challenges_solved': 0
            }
        )
        cls.challenge = FeatureChallenge.objects.first()

    def setUp(self):
        self.user.bugbytes_balance = 100
        self.user.total_score = 0
        self.user.challenges_solved = 0
        self.user.save()
        FeatureSubmission.objects.filter(user=self.user).delete()

    def test_01_feature_challenges_list(self):
        request = self.factory.get('/api/feature-challenges')
        response = feature_challenges_list_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)
        item = response.data[0]
        self.assertIn('title', item)
        self.assertIn('difficulty', item)
        self.assertIn('technology', item)
        self.assertIn('requirements', item)

    def test_02_feature_challenge_detail(self):
        request = self.factory.get(f'/api/feature-challenges/{self.challenge.id}')
        response = feature_challenge_detail_view(request, pk=str(self.challenge.id))
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['title'], self.challenge.title)
        self.assertIn('files', data)
        self.assertIn('publicTests', data)
        self.assertIn('scoringConfig', data)

    def test_03_evaluator_path_traversal_sanitization(self):
        malicious_files = [
            {'name': '../../etc/passwd', 'content': 'evil'},
            {'name': 'C:\\Windows\\system32\\cmd.exe', 'content': 'evil'},
            {'name': 'app/valid.py', 'content': 'print("safe")'}
        ]
        cleaned = feature_evaluator.validate_files(malicious_files)
        names = [f['name'] for f in cleaned]
        self.assertNotIn('../../etc/passwd', names)
        self.assertNotIn('C:\\Windows\\system32\\cmd.exe', names)
        self.assertIn('app/valid.py', names)

    def test_04_run_feature_challenge(self):
        # Run tests against initial files
        request = self.factory.post(
            f'/api/feature-challenges/{self.challenge.id}/run',
            data=json.dumps({'files': self.challenge.initial_files}),
            content_type='application/json'
        )
        response = run_feature_challenge_view(request, pk=str(self.challenge.id))
        self.assertEqual(response.status_code, 200)
        res = response.data
        self.assertIn('score', res)
        self.assertIn('score_breakdown', res)
        self.assertIn('test_results', res)
        self.assertIn('execution_time', res)

    def test_05_submit_feature_challenge_and_xp_award(self):
        # Create an authorized request with user header
        request = self.factory.post(
            f'/api/feature-challenges/{self.challenge.id}/submit',
            data=json.dumps({'files': self.challenge.initial_files}),
            content_type='application/json'
        )
        # Mock authenticated user
        request.user = self.user
        setattr(request, '_dont_enforce_csrf_checks', True)

        initial_xp = self.user.total_score
        initial_bb = self.user.bugbytes_balance

        # We inject mock authorization for the view
        from buggyman.auth import generate_jwt_token
        token = generate_jwt_token(self.user)
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        response = submit_feature_challenge_view(request, pk=str(self.challenge.id))
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn('submission', data)
        self.assertIn('scoreBreakdown', data)
        self.assertIn('aiReview', data)

        # Refresh user from DB
        self.user.refresh_from_db()
        self.assertGreaterEqual(self.user.total_score, initial_xp)

    def test_06_prevent_duplicate_rewards(self):
        # Create an already-successful submission
        FeatureSubmission.objects.create(
            user=self.user,
            challenge=self.challenge,
            submitted_files=self.challenge.initial_files,
            success=True,
            score=100
        )
        self.user.total_score = 150
        self.user.challenges_solved = 1
        self.user.save()

        from buggyman.auth import generate_jwt_token
        token = generate_jwt_token(self.user)

        request = self.factory.post(
            f'/api/feature-challenges/{self.challenge.id}/submit',
            data=json.dumps({'files': self.challenge.initial_files}),
            content_type='application/json'
        )
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        response = submit_feature_challenge_view(request, pk=str(self.challenge.id))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('alreadySolved'))
        self.assertEqual(response.data.get('xpAwarded'), 0)
        self.assertEqual(response.data.get('bugbytesAwarded'), 0)

    def test_07_unlock_progressive_hint(self):
        from buggyman.auth import generate_jwt_token
        token = generate_jwt_token(self.user)

        request = self.factory.post(
            f'/api/feature-challenges/{self.challenge.id}/hint',
            data=json.dumps({'level': 1}),
            content_type='application/json'
        )
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        initial_bb = self.user.bugbytes_balance
        response = feature_challenge_hint_view(request, pk=str(self.challenge.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn('hint', response.data)
        self.assertEqual(response.data['hint']['level'], 1)

        self.user.refresh_from_db()
        self.assertLess(self.user.bugbytes_balance, initial_bb)

    def test_08_codebase_assistant(self):
        request = self.factory.post(
            f'/api/feature-challenges/{self.challenge.id}/ai-assistant',
            data=json.dumps({
                'prompt': 'How should I structure the rate limiter timestamps?',
                'files': self.challenge.initial_files
            }),
            content_type='application/json'
        )
        response = feature_codebase_assistant_view(request, pk=str(self.challenge.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn('reply', response.data)
        self.assertIn('timestamp', response.data)

if __name__ == '__main__':
    unittest.main()
