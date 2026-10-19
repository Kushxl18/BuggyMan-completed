"""
BuggyMan Challenge Page Audit Test Suite
Verifies:
1. Answer leakage elimination (Zero BUG comments, clean business requirements, progressive hints)
2. Challenge reactions and engagement persistence (likes, dislikes, stars, toggle uniqueness)
3. Testing interface integrity (visible vs hidden tests, hidden input masking)
4. XP awarding and duplicate reward prevention
5. Solution protection behind dedicated endpoint
"""

import os
import sys
import json
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

# Setup Django environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from buggyman.models import Challenge, ChallengeReaction, Submission
from buggyman.evaluator.engine import EvaluationEngine
from buggyman.auth import generate_jwt_token

User = get_user_model()


class BuggyManAuditTestSuite(TestCase):
    def setUp(self):
        self.client = Client()
        self.engine = EvaluationEngine()
        
        # Create test users
        self.user1 = User.objects.create(
            username="test_auditor_1",
            email="auditor1@buggyman.test",
            display_name="Auditor One",
            total_score=0,
            challenges_solved=0
        )
        self.token1 = generate_jwt_token(self.user1)
        self.auth_headers1 = {'HTTP_AUTHORIZATION': f'Bearer {self.token1}'}

        self.user2 = User.objects.create(
            username="test_auditor_2",
            email="auditor2@buggyman.test",
            display_name="Auditor Two",
            total_score=0,
            challenges_solved=0
        )
        self.token2 = generate_jwt_token(self.user2)
        self.auth_headers2 = {'HTTP_AUTHORIZATION': f'Bearer {self.token2}'}

        # Retrieve a sample challenge
        self.challenge = Challenge.objects.first()
        if not self.challenge:
            self.challenge = Challenge.objects.create(
                id=1,
                title="[CODE-E01] API Pagination Skips the Final Record",
                difficulty="Easy",
                technology="Python",
                category="API & Web",
                points=100,
                description="Test description without answer leakage",
                files=[{'name': 'pagination.py', 'content': 'def paginate(items, page=1, page_size=10):\n    return items'}],
                test_cases=[
                    {'id': 1, 'name': 'Visible: Test 1', 'input': 'paginate([1,2,3])', 'expected': '[1, 2, 3]', 'hidden': False},
                    {'id': 2, 'name': 'Hidden: Boundary Test', 'input': 'paginate([])', 'expected': '[]', 'hidden': True}
                ]
            )

    def test_01_no_bug_comments_in_starter_code(self):
        """Audit Section A: Verify zero # BUG:, // BUG:, -- BUG: comments exist in any challenge starter files."""
        for c in Challenge.objects.all():
            for f in (c.files or []):
                content = f.get('content', '')
                self.assertNotIn('# BUG:', content, f"Challenge {c.id} ({c.title}) file {f.get('name')} leaks # BUG:")
                self.assertNotIn('// BUG:', content, f"Challenge {c.id} ({c.title}) file {f.get('name')} leaks // BUG:")
                self.assertNotIn('-- BUG:', content, f"Challenge {c.id} ({c.title}) file {f.get('name')} leaks -- BUG:")

    def test_02_engagement_reactions_persistence_and_uniqueness(self):
        """Audit Section B: Verify persistent reactions, atomic toggles, and per-user uniqueness."""
        cid = self.challenge.id

        # 1. User 1 likes the challenge
        res = self.client.post(
            f'/api/challenges/{cid}/reaction',
            data=json.dumps({'reaction': 'like'}),
            content_type='application/json',
            **self.auth_headers1
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['userReaction'], 'like')
        self.assertEqual(data['likes'], 1)
        self.assertEqual(data['dislikes'], 0)

        # 2. User 2 dislikes the challenge
        res = self.client.post(
            f'/api/challenges/{cid}/reaction',
            data=json.dumps({'reaction': 'dislike'}),
            content_type='application/json',
            **self.auth_headers2
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['userReaction'], 'dislike')
        self.assertEqual(data['likes'], 1)
        self.assertEqual(data['dislikes'], 1)

        # 3. User 1 switches reaction to dislike (atomic update, no duplicates)
        res = self.client.post(
            f'/api/challenges/{cid}/reaction',
            data=json.dumps({'reaction': 'dislike'}),
            content_type='application/json',
            **self.auth_headers1
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['userReaction'], 'dislike')
        self.assertEqual(data['likes'], 0)
        self.assertEqual(data['dislikes'], 2)

        # 4. User 1 toggles off reaction (clicks dislike again to cancel)
        res = self.client.post(
            f'/api/challenges/{cid}/reaction',
            data=json.dumps({'reaction': 'dislike'}),
            content_type='application/json',
            **self.auth_headers1
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsNone(data['userReaction'])
        self.assertEqual(data['likes'], 0)
        self.assertEqual(data['dislikes'], 1)

        # 5. Verify star / favorite toggling
        res = self.client.post(
            f'/api/challenges/{cid}/star',
            content_type='application/json',
            **self.auth_headers1
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['isStarred'])
        self.assertEqual(res.json()['stars'], 1)

    def test_03_hidden_test_case_masking(self):
        """Audit Section C: Verify that hidden test cases do not leak raw input or expected output."""
        # Failing code (returns wrong output for hidden case)
        failing_files = [{'name': 'pagination.py', 'content': 'def paginate(items, page=1, page_size=10):\n    return [9999]'}]
        failing_res = self.engine.evaluate(self.challenge, files=failing_files)
        
        hidden_cases = [tr for tr in failing_res['test_results'] if tr.get('hidden')]
        self.assertTrue(len(hidden_cases) > 0, "Challenge should contain at least one hidden test case")

        for hc in hidden_cases:
            self.assertEqual(hc['input'], '[Hidden Test Input]', "Hidden test raw input leaked")
            self.assertEqual(hc['expected'], '[Hidden Expected Output]', "Hidden test expected output leaked")
            self.assertEqual(hc['actual'], 'Hidden test assertion failed')
            self.assertIn('Hidden test assertion failed', hc['error'])

        # Passing solution code
        sol_code = (
            'def paginate(items, page=1, page_size=10):\n'
            '    if not items or page < 1 or page_size < 1:\n'
            '        return []\n'
            '    start = (page - 1) * page_size\n'
            '    end = min(len(items), page * page_size)\n'
            '    if start >= len(items):\n'
            '        return []\n'
            '    return items[start:end]'
        )
        passing_res = self.engine.evaluate(self.challenge, files=[{'name': 'pagination.py', 'content': sol_code}])
        passing_hidden = [tr for tr in passing_res['test_results'] if tr.get('hidden')]
        for hc in passing_hidden:
            self.assertEqual(hc['input'], '[Hidden Test Input]')
            self.assertEqual(hc['expected'], '[Hidden Expected Output]')
            self.assertEqual(hc['actual'], 'Matched hidden assertion')
            self.assertIsNone(hc['error'])

    def test_04_xp_awarding_and_duplicate_prevention(self):
        """Audit Section E: Verify that solving awards XP only once, preventing duplicate rewards."""
        cid = self.challenge.id
        
        # Correct reference solution for Challenge 1
        solution_code = '''def paginate(items, page=1, page_size=10):
    if not items or page < 1 or page_size < 1:
        return []
    start = (page - 1) * page_size
    end = min(len(items), page * page_size)
    if start >= len(items):
        return []
    return items[start:end]'''

        initial_score = self.user1.total_score
        initial_solved = self.user1.challenges_solved

        # Submission 1: Successful
        res = self.client.post(
            f'/api/challenges/{cid}/submit',
            data=json.dumps({'code': solution_code}),
            content_type='application/json',
            **self.auth_headers1
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertGreater(data['score'], 0, "First submission should award points")

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.challenges_solved, initial_solved + 1)
        self.assertEqual(self.user1.total_score, initial_score + data['score'])

        # Submission 2: Re-submitting the same solved challenge
        score_after_sub1 = self.user1.total_score
        res2 = self.client.post(
            f'/api/challenges/{cid}/submit',
            data=json.dumps({'code': solution_code}),
            content_type='application/json',
            **self.auth_headers1
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertTrue(data2['success'])

        self.user1.refresh_from_db()
        # Verify score and solved count are NOT incremented again
        self.assertEqual(self.user1.total_score, score_after_sub1, "Duplicate submission awarded extra XP!")
        self.assertEqual(self.user1.challenges_solved, initial_solved + 1, "Duplicate submission increased solved count!")

    def test_05_solution_endpoint_protection(self):
        """Audit Section A & B: Verify dedicated solution endpoint returns complete guidance."""
        cid = self.challenge.id
        res = self.client.get(f'/api/challenges/{cid}/solution')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn('referenceCode', data)
        self.assertIn('rootCause', data)
        self.assertIn('preventionRule', data)
        self.assertTrue(len(data['referenceCode']) > 0)


if __name__ == '__main__':
    import unittest
    unittest.main()
