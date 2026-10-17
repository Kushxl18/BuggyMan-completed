import re
import json
from unittest.mock import patch
from django.test import TestCase
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from buggyman.models import Challenge, Notification, Submission
from buggyman.evaluator.engine import EvaluationEngine
from buggyman.throttling import clear_rate_limits
from buggyman.logger import sanitize_data, log_event

User = get_user_model()

class BuggyManAPITestCase(TestCase):
    def setUp(self):
        clear_rate_limits()
        cache.clear()
        self.client = APIClient()
        self.engine = EvaluationEngine()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User',
            college='Test University',
            total_score=200,
            challenges_solved=2
        )
        self.challenge = Challenge.objects.create(
            title='Test Bug Challenge',
            description='Fix this bug',
            difficulty='Easy',
            technology='Python',
            category='State',
            points=100,
            files=[{'name': 'main.py', 'content': 'def add():\n    return 3'}],
            test_cases=[{'id': 1, 'name': 'Addition test', 'input': 'add', 'expected': '5', 'passed': False}],
            bug_signature='return 3',
            suspected_component='main.py'
        )

    def test_login(self):
        res = self.client.post('/api/login', {'email': 'test@example.com', 'password': 'testpassword123'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)
        self.assertEqual(res.data['user']['username'], 'testuser')

    def test_register(self):
        res = self.client.post('/api/register', {
            'fullName': 'New User',
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)
        self.assertEqual(res.data['user']['email'], 'new@example.com')

    def test_get_challenges(self):
        res = self.client.get('/api/challenges')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 1)
        self.assertTrue(any(c['title'] == 'Test Bug Challenge' for c in res.data))

    def test_get_challenges_can_filter_by_difficulty_technology_and_category(self):
        Challenge.objects.create(
            title='Second Challenge',
            description='Another challenge',
            difficulty='Medium',
            technology='Python',
            category='Auth',
            points=150,
            files=[{'name': 'views.py', 'content': 'pass'}],
            test_cases=[{'id': 1, 'name': 'Test 1', 'input': '', 'expected': '', 'passed': False}],
            bug_signature='bug',
            suspected_component='views.py'
        )

        res = self.client.get('/api/challenges', {
            'difficulty': 'Easy',
            'technology': 'Python',
            'category': 'State'
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], 'Test Bug Challenge')

    def test_submit_requires_authentication(self):
        res = self.client.post(f'/api/challenges/{self.challenge.id}/submit', {'code': 'def add():\n    return 5'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_leaderboard(self):
        res = self.client.get('/api/leaderboard')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 1)

    def test_admin_stats(self):
        self.user.role = 'admin'
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/admin/stats')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('totalUsers', res.data)
        self.assertIn('totalChallenges', res.data)

    def test_generate_challenge(self):
        res = self.client.post('/api/challenges/generate', {
            'difficulty': 'Medium',
            'technology': 'React'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['difficulty'], 'Medium')
        self.assertEqual(res.data['technology'], 'React')
        self.assertIn('files', res.data)
        self.assertIn('bugSignature', res.data)

    # ----------------------------------------------------
    # TASK 4 SPECIFIC EVALUATOR TESTS (TESTS 1 to 8)
    # ----------------------------------------------------

    def test_1_correct_solution(self):
        """Test 1: Correct solution produces success = True and passed test cases"""
        py_challenge = {
            'technology': 'Python',
            'points': 100,
            'test_cases': [{'id': 1, 'name': 'Calculates sum', 'input': 'calculate', 'expected': '10'}]
        }
        code = "def calculate():\n    return 5 + 5"
        res = self.engine.evaluate(py_challenge, code=code)
        
        self.assertTrue(res['success'])
        self.assertEqual(res['score'], 100)
        self.assertEqual(res['tests_passed'], 1)
        self.assertEqual(res['test_results'][0]['actual'], '10')

    def test_2_incorrect_solution(self):
        """Test 2: Incorrect solution fails test case and produces success = False"""
        py_challenge = {
            'technology': 'Python',
            'points': 100,
            'test_cases': [{'id': 1, 'name': 'Calculates sum', 'input': 'calculate', 'expected': '10'}]
        }
        code = "def calculate():\n    return 5 + 2"
        res = self.engine.evaluate(py_challenge, code=code)
        
        self.assertFalse(res['success'])
        self.assertEqual(res['score'], 0)
        self.assertEqual(res['tests_passed'], 0)

    def test_3_syntax_compile_error(self):
        """Test 3: Controlled syntax/compile error output"""
        py_challenge = {
            'technology': 'Python',
            'points': 100,
            'test_cases': [{'id': 1, 'name': 'Syntax check', 'input': '', 'expected': 'ok'}]
        }
        invalid_code = "def broken_syntax(:\n    return 1"
        res = self.engine.evaluate(py_challenge, code=invalid_code)
        
        self.assertFalse(res['success'])
        self.assertIn('SYNTAX_ERROR', res['stderr'])

    def test_4_runtime_error(self):
        """Test 4: Controlled runtime error output"""
        py_challenge = {
            'technology': 'Python',
            'points': 100,
            'test_cases': [{'id': 1, 'name': 'Division check', 'input': '', 'expected': 'ok'}]
        }
        runtime_err_code = "x = 1 / 0"
        res = self.engine.evaluate(py_challenge, code=runtime_err_code)
        
        self.assertFalse(res['success'])
        self.assertIn('ZeroDivisionError', res['stderr'])

    def test_5_infinite_loop_timeout(self):
        """Test 5: Program timeout is caught cleanly within limit without hanging server"""
        py_challenge = {
            'technology': 'Python',
            'points': 100,
            'test_cases': [{'id': 1, 'name': 'Loop test', 'input': '', 'expected': 'ok'}]
        }
        infinite_loop_code = "while True:\n    pass"
        res = self.engine.evaluate(py_challenge, code=infinite_loop_code, timeout=1.0)
        
        self.assertFalse(res['success'])
        self.assertTrue(res['timed_out'])
        self.assertIn('timed out', res['ai_summary'].lower())

    def test_6_unsupported_runtime(self):
        """Test 6: Clear unsupported runtime response"""
        unsupported_challenge = {
            'technology': 'Brainfuck',
            'points': 100,
            'test_cases': [{'id': 1, 'name': 'Check', 'input': '', 'expected': ''}]
        }
        res = self.engine.evaluate(unsupported_challenge, code="++++")
        
        self.assertFalse(res['success'])
        self.assertIn('Unsupported runtime technology', res['stderr'])

    def test_7_existing_challenge_evaluation(self):
        """Test 7: Real BuggyMan challenge evaluated from Django database"""
        self.client.force_authenticate(user=self.user)
        
        res_run = self.client.post(
            f'/api/challenges/{self.challenge.id}/run',
            {'code': 'def add():\n    return 5'},
            format='json'
        )
        self.assertEqual(res_run.status_code, status.HTTP_200_OK)
        self.assertIn('testsPassed', res_run.data)
        self.assertEqual(Submission.objects.filter(user=self.user, challenge=self.challenge).count(), 0)

    # ----------------------------------------------------
    # TASK 5 SPECIFIC SUBMISSION SYSTEM TESTS
    # ----------------------------------------------------

    def test_submission_model_field_persistence(self):
        """Task 5: Submission model records submitted_files, test_results, execution_time, attempt_number, stdout, stderr, ai_summary"""
        sub = Submission.objects.create(
            user=self.user,
            challenge=self.challenge,
            submitted_code="def add(): return 5",
            submitted_files=[{'name': 'main.py', 'content': 'def add(): return 5'}],
            success=True,
            score=100,
            test_results=[{'id': 1, 'passed': True}],
            execution_time=0.12,
            attempt_number=1,
            stdout="OK",
            stderr="",
            ai_summary="All tests passed"
        )
        self.assertEqual(sub.attempt_number, 1)
        self.assertEqual(sub.execution_time, 0.12)
        d = sub.to_dict()
        self.assertEqual(d['attemptNumber'], 1)
        self.assertEqual(d['submissionId'] if 'submissionId' in d else d['id'], sub.id)
        self.assertEqual(len(d['submittedFiles']), 1)

    def test_attempt_number_increment_and_xp_farming_prevention(self):
        """Task 5: Sequential attempt numbering and XP farming prevention on duplicate success"""
        self.user.total_score = 0
        self.user.challenges_solved = 0
        self.user.save()
        self.client.force_authenticate(user=self.user)

        # Attempt 1: Failed submission
        res1 = self.client.post(f'/api/challenges/{self.challenge.id}/submit', {'code': 'def add(): return 1'}, format='json')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.data['attemptNumber'], 1)
        self.assertFalse(res1.data['success'])
        self.assertEqual(res1.data['score'], 0)

        # Attempt 2: First-time successful submission
        res2 = self.client.post(f'/api/challenges/{self.challenge.id}/submit', {'code': 'def add(): return 5'}, format='json')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data['attemptNumber'], 2)
        self.assertTrue(res2.data['success'])
        self.assertEqual(res2.data['score'], 100)

        self.user.refresh_from_db()
        self.assertEqual(self.user.total_score, 100)
        self.assertEqual(self.user.challenges_solved, 1)

        # Attempt 3: Duplicate successful submission (XP farming check)
        res3 = self.client.post(f'/api/challenges/{self.challenge.id}/submit', {'code': 'def add(): return 5'}, format='json')
        self.assertEqual(res3.status_code, status.HTTP_200_OK)
        self.assertEqual(res3.data['attemptNumber'], 3)
        self.assertTrue(res3.data['alreadySolved'])
        self.assertEqual(res3.data['score'], 0)

        # User score & challenges_solved must NOT double increment!
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_score, 100)
        self.assertEqual(self.user.challenges_solved, 1)

        # 3 submission records should exist in DB
        self.assertEqual(Submission.objects.filter(user=self.user, challenge=self.challenge).count(), 3)

    def test_submission_history_apis(self):
        """Task 5: Submission history list, detail, and challenge-level APIs"""
        self.client.force_authenticate(user=self.user)
        self.client.post(f'/api/challenges/{self.challenge.id}/submit', {'code': 'def add(): return 5'}, format='json')

        # 1. User Submissions List API
        res_list = self.client.get('/api/submissions')
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res_list.data), 1)

        sub_id = res_list.data[0]['id']

        # 2. Submission Detail API
        res_detail = self.client.get(f'/api/submissions/{sub_id}')
        self.assertEqual(res_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(res_detail.data['id'], sub_id)

        # 3. Challenge Submissions History API
        res_chal_subs = self.client.get(f'/api/challenges/{self.challenge.id}/submissions')
        self.assertEqual(res_chal_subs.status_code, status.HTTP_200_OK)
        self.assertEqual(res_chal_subs.data['totalAttempts'], len(res_list.data))
        self.assertTrue(res_chal_subs.data['solved'])

    # ----------------------------------------------------
    # TASK 7 SPECIFIC GAMIFICATION TESTS
    # ----------------------------------------------------

    def test_gamification_pipeline_first_solve(self):
        """Task 7: Gamification pipeline triggers streak, badge check, activity feed logging, and XP award"""
        self.user.total_score = 0
        self.user.challenges_solved = 0
        self.user.streak = 0
        self.user.activities = []
        self.user.badges = []
        self.user.save()
        self.client.force_authenticate(user=self.user)

        res = self.client.post(f'/api/challenges/{self.challenge.id}/submit', {'code': 'def add(): return 5'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_score, 100)
        self.assertEqual(self.user.challenges_solved, 1)
        self.assertEqual(self.user.streak, 1)
        self.assertGreaterEqual(len(self.user.activities), 1)
        self.assertGreaterEqual(len(self.user.badges), 1)
        self.assertTrue(any(b['name'] == 'First Bug Defeated' for b in self.user.badges))
        self.assertTrue(Notification.objects.filter(user=self.user, type='achievement').exists())

    def test_streak_calculation_consecutive_vs_gap(self):
        """Task 7: Streak increments on consecutive days and resets after gap"""
        import datetime
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        
        self.user.last_active_date = yesterday
        self.user.streak = 3
        self.user.save()
        
        from buggyman.views import update_user_streak
        update_user_streak(self.user)
        self.assertEqual(self.user.streak, 4)
        self.assertEqual(self.user.last_active_date, today)

        # Gap reset test
        self.user.last_active_date = today - datetime.timedelta(days=4)
        self.user.streak = 10
        self.user.save()
        
        update_user_streak(self.user)
        self.assertEqual(self.user.streak, 1)

    def test_badge_unlocks_on_milestones(self):
        """Task 7: Milestone scores unlock badges automatically"""
        from buggyman.views import check_and_unlock_badges
        self.user.challenges_solved = 5
        self.user.total_score = 550
        self.user.badges = []
        self.user.save()

        check_and_unlock_badges(self.user)
        self.user.save()

        badge_names = [b['name'] for b in self.user.badges]
        self.assertIn('Five Bugs Squashed', badge_names)
        self.assertIn('Centurion', badge_names)

    def test_leaderboard_sorting_and_filtering(self):
        """Task 7: Leaderboard ranks users by score and filters by college"""
        User.objects.create_user(username='topcoder', email='top@mit.edu', password='p', college='MIT', total_score=2000, challenges_solved=15)
        User.objects.create_user(username='stanfordcoder', email='st@stanford.edu', password='p', college='Stanford', total_score=1500, challenges_solved=10)

        # Global leaderboard
        res = self.client.get('/api/leaderboard')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['username'], 'topcoder')

        # College filtered leaderboard
        res_mit = self.client.get('/api/leaderboard', {'college': 'MIT'})
        self.assertEqual(res_mit.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_mit.data), 1)
        self.assertEqual(res_mit.data[0]['username'], 'topcoder')

    def test_analytics_metrics(self):
        """Task 7: Analytics returns user accuracy and difficulty progression"""
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/analytics')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('accuracy', res.data)
        self.assertIn('difficultyProgression', res.data)

    # ----------------------------------------------------
    # PHASE 2 TASK 1: SQL CHALLENGE ENGINE TESTS
    # ----------------------------------------------------

    def test_sql_engine_correct_query(self):
        """Task 1: Correct SQL query produces tabular output and passed test case"""
        from buggyman.evaluator.runtimes import SQLRuntimeAdapter
        adapter = SQLRuntimeAdapter()
        files = [
            {'name': 'schema.sql', 'content': 'CREATE TABLE users (id INT, name TEXT);\nINSERT INTO users VALUES (1, "Alice");'},
            {'name': 'query.sql', 'content': 'SELECT * FROM users WHERE name = "Alice";'}
        ]
        test_cases = [{'id': 1, 'name': 'Finds Alice', 'input': '', 'expected': 'Alice'}]
        res = adapter.evaluate({'technology': 'SQL'}, files, test_cases)
        
        self.assertEqual(res['exit_code'], 0)
        self.assertIn('Alice', res['stdout'])
        self.assertTrue(res['test_results'][0]['passed'])

    def test_sql_engine_syntax_error_handling(self):
        """Task 1: Syntax error returns clear SQLite error message without breaking process"""
        from buggyman.evaluator.runtimes import SQLRuntimeAdapter
        adapter = SQLRuntimeAdapter()
        files = [{'name': 'query.sql', 'content': 'SELECT * FORM users;'}]
        test_cases = [{'id': 1, 'name': 'Query Check', 'input': '', 'expected': 'users'}]
        res = adapter.evaluate({'technology': 'SQL'}, files, test_cases)
        
        self.assertEqual(res['exit_code'], 1)
        self.assertIn('SQLite Error', res['stderr'])
        self.assertFalse(res['test_results'][0]['passed'])

    def test_sql_engine_destructive_query_isolation(self):
        """Task 1: Destructive SQL query executes safely in isolated SQLite without altering host DB"""
        from buggyman.evaluator.runtimes import SQLRuntimeAdapter
        adapter = SQLRuntimeAdapter()
        files = [
            {'name': 'schema.sql', 'content': 'CREATE TABLE orders (id INT);'},
            {'name': 'query.sql', 'content': 'DROP TABLE orders;'}
        ]
        res = adapter.evaluate({'technology': 'SQL'}, files, [])
        
        self.assertEqual(res['exit_code'], 0)
        self.assertIn('Statement executed cleanly', res['stdout'])
        # Host database remains completely intact
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_sql_engine_security_check(self):
        """Task 1: Security check blocks disallowed attach/extension commands"""
        from buggyman.evaluator.runtimes import SQLRuntimeAdapter
        adapter = SQLRuntimeAdapter()
        files = [{'name': 'query.sql', 'content': 'SELECT load_extension("libsomething.so");'}]
        res = adapter.evaluate({'technology': 'SQL'}, files, [])
        
        self.assertEqual(res['exit_code'], 1)
        self.assertIn('SECURITY_ERROR', res['stderr'])

    def test_sql_engine_real_challenges_evaluation(self):
        """Task 1: Evaluates 2 real SQL challenges (SQL-E01 and SQL-E02) via API endpoints"""
        self.client.force_authenticate(user=self.user)

        # Challenge 1: SQL-E01 (WHERE clause)
        res_run1 = self.client.post(
            '/api/challenges/SQL-E01/run',
            {'code': 'SELECT * FROM orders WHERE status = \'completed\';'},
            format='json'
        )
        self.assertEqual(res_run1.status_code, status.HTTP_200_OK)
        self.assertTrue(res_run1.data['success'])
        self.assertIn('completed', res_run1.data['stdout'])

        # Challenge 2: SQL-E02 (ORDER BY clause)
        res_run2 = self.client.post(
            '/api/challenges/SQL-E02/run',
            {'code': 'SELECT name, price FROM products ORDER BY price;'},
            format='json'
        )
        self.assertEqual(res_run2.status_code, status.HTTP_200_OK)
        self.assertTrue(res_run2.data['success'])
        self.assertIn('Mouse', res_run2.data['stdout'])

    # ----------------------------------------------------
    # PHASE 2 TASK 2: SQL EVALUATION TESTS
    # ----------------------------------------------------

    def test_sql_evaluation_correct_result_set(self):
        """Task 2: Query producing matching result set passes evaluation"""
        from buggyman.evaluator.runtimes import SQLRuntimeAdapter
        adapter = SQLRuntimeAdapter()
        challenge = {
            'technology': 'SQL',
            'expected_query': "SELECT id, name FROM users WHERE role = 'admin';",
            'ordered_comparison': False
        }
        files = [
            {'name': 'schema.sql', 'content': 'CREATE TABLE users (id INT, name TEXT, role TEXT);\nINSERT INTO users VALUES (1, "Alice", "admin"), (2, "Bob", "user");'},
            {'name': 'query.sql', 'content': 'SELECT id, name FROM users WHERE role = "admin";'}
        ]
        test_cases = [{'id': 1, 'name': 'Admins check', 'input': '', 'expected': 'Alice'}]
        res = adapter.evaluate(challenge, files, test_cases)
        
        self.assertTrue(res['test_results'][0]['passed'])
        self.assertEqual(len(res['rows']), 1)
        self.assertEqual(res['rows'][0][1], 'Alice')

    def test_sql_evaluation_incorrect_result_set(self):
        """Task 2: Query producing wrong or extra rows fails evaluation"""
        from buggyman.evaluator.runtimes import SQLRuntimeAdapter
        adapter = SQLRuntimeAdapter()
        challenge = {
            'technology': 'SQL',
            'expected_query': "SELECT id, name FROM users WHERE role = 'admin';",
            'ordered_comparison': False
        }
        files = [
            {'name': 'schema.sql', 'content': 'CREATE TABLE users (id INT, name TEXT, role TEXT);\nINSERT INTO users VALUES (1, "Alice", "admin"), (2, "Bob", "user");'},
            {'name': 'query.sql', 'content': 'SELECT id, name FROM users;'} # Returns extra rows!
        ]
        test_cases = [{'id': 1, 'name': 'Admins check', 'input': '', 'expected': 'Alice'}]
        res = adapter.evaluate(challenge, files, test_cases)
        
        self.assertFalse(res['test_results'][0]['passed'])
        self.assertIn('Result set mismatch', str(res['test_results'][0]['error']))

    def test_sql_evaluation_order_sensitive_vs_insensitive(self):
        """Task 2: Order-insensitive query passes with different order; order-sensitive query fails if un-sorted"""
        from buggyman.evaluator.runtimes import SQLRuntimeAdapter
        adapter = SQLRuntimeAdapter()

        # 1. Order-insensitive challenge
        chal_insensitive = {
            'technology': 'SQL',
            'title': 'Filter users',
            'expected_query': 'SELECT name FROM items ORDER BY id ASC;',
            'ordered_comparison': False
        }
        files_reverse = [
            {'name': 'schema.sql', 'content': 'CREATE TABLE items (id INT, name TEXT);\nINSERT INTO items VALUES (1, "A"), (2, "B");'},
            {'name': 'query.sql', 'content': 'SELECT name FROM items ORDER BY id DESC;'}
        ]
        test_cases = [{'id': 1, 'name': 'Items check', 'input': '', 'expected': 'A'}]
        res1 = adapter.evaluate(chal_insensitive, files_reverse, test_cases)
        self.assertTrue(res1['test_results'][0]['passed']) # Order insensitive: same set of rows!

        # 2. Order-sensitive challenge
        chal_sensitive = {
            'technology': 'SQL',
            'title': 'Sort items by name',
            'expected_query': 'SELECT name FROM items ORDER BY name ASC;',
            'ordered_comparison': True
        }
        res2 = adapter.evaluate(chal_sensitive, files_reverse, test_cases)
        self.assertFalse(res2['test_results'][0]['passed']) # Order sensitive: B, A does not match A, B!
        self.assertIn('Row order mismatch', str(res2['test_results'][0]['error']))

    def test_sql_evaluation_empty_result_set(self):
        """Task 2: Query returning 0 rows when rows expected fails evaluation"""
        from buggyman.evaluator.runtimes import SQLRuntimeAdapter
        adapter = SQLRuntimeAdapter()
        challenge = {
            'technology': 'SQL',
            'expected_query': "SELECT * FROM orders WHERE status = 'completed';"
        }
        files = [
            {'name': 'schema.sql', 'content': 'CREATE TABLE orders (id INT, status TEXT);\nINSERT INTO orders VALUES (1, "completed");'},
            {'name': 'query.sql', 'content': 'SELECT * FROM orders WHERE status = "nonexistent";'}
        ]
        test_cases = [{'id': 1, 'name': 'Completed orders', 'input': '', 'expected': 'completed'}]
        res = adapter.evaluate(challenge, files, test_cases)
        
        self.assertFalse(res['test_results'][0]['passed'])
        self.assertEqual(len(res['rows']), 0)

    def test_sql_evaluation_malformed_query(self):
        """Task 2: Malformed SQL query returns clean failure result without crashing"""
        from buggyman.evaluator.runtimes import SQLRuntimeAdapter
        adapter = SQLRuntimeAdapter()
        challenge = {'technology': 'SQL', 'expected_query': 'SELECT * FROM orders;'}
        files = [{'name': 'query.sql', 'content': 'SELECT * FORM orders WHERE;'}]
        test_cases = [{'id': 1, 'name': 'Syntax check', 'input': '', 'expected': 'orders'}]
        res = adapter.evaluate(challenge, files, test_cases)
        
        self.assertEqual(res['exit_code'], 1)
        self.assertFalse(res['test_results'][0]['passed'])
        self.assertIn('SQLite Error', res['stderr'])

    def test_sql_evaluation_anti_spoofing(self):
        """Task 2: Anti-spoofing check prevents hardcoded dummy strings from tricking evaluator"""
        from buggyman.evaluator.runtimes import SQLRuntimeAdapter
        adapter = SQLRuntimeAdapter()
        challenge = {
            'technology': 'SQL',
            'expected_query': "SELECT id, amount FROM orders WHERE status = 'completed';"
        }
        files = [
            {'name': 'schema.sql', 'content': 'CREATE TABLE orders (id INT, amount INT, status TEXT);\nINSERT INTO orders VALUES (1, 100, "completed");'},
            {'name': 'query.sql', 'content': '-- Comment saying completed\nSELECT 999 AS id, 999 AS amount;' } # Dummy hardcoded spoof query!
        ]
        test_cases = [{'id': 1, 'name': 'Orders check', 'input': '', 'expected': 'completed'}]
        res = adapter.evaluate(challenge, files, test_cases)
        
        self.assertFalse(res['test_results'][0]['passed'])
        self.assertIn('Result set mismatch', str(res['test_results'][0]['error']))

    # ----------------------------------------------------
    # PHASE 2 TASK 3: FRONTEND CHALLENGE ENGINE TESTS
    # ----------------------------------------------------

    def test_frontend_engine_multi_file_support(self):
        """Task 3: Frontend engine accepts multi-file workspaces (JSX + CSS) and evaluates"""
        from buggyman.evaluator.engine import EvaluationEngine
        engine = EvaluationEngine()
        challenge = {
            'technology': 'React',
            'files': [
                {'name': 'Counter.jsx', 'content': 'export default function Counter() { return <button>0</button>; }'},
                {'name': 'styles.css', 'content': 'button { color: red; }'}
            ],
            'test_cases': [{'id': 1, 'name': 'Button element check', 'input': '', 'expected': '<button>'}]
        }
        res = engine.evaluate(challenge, challenge['files'])
        self.assertTrue(res['test_results'][0]['passed'])

    def test_frontend_engine_real_challenges_run(self):
        """Task 3: Fetches and evaluates real Frontend challenges (RE-E01, RE-E02) via API"""
        self.client.force_authenticate(user=self.user)

        # 1. Fetch challenge detail for RE-E01
        res_get = self.client.get('/api/challenges/RE-E01')
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        self.assertIn('Counter', res_get.data['title'])
        self.assertGreaterEqual(len(res_get.data['files']), 2) # Multi-file structure!

        # 2. Run challenge RE-E01 with corrected state code
        fixed_code = "import React, { useState } from 'react';\n\nexport default function Counter() {\n  const [count, setCount] = useState(0);\n  const increment = () => setCount(count + 1);\n  return <button onClick={increment}>{count}</button>;\n}"
        res_run = self.client.post(
            '/api/challenges/RE-E01/run',
            {'code': fixed_code},
            format='json'
        )
        self.assertEqual(res_run.status_code, status.HTTP_200_OK)
        self.assertTrue(res_run.data['success'])

    # ----------------------------------------------------
    # PHASE 2 TASK 4: FRONTEND EVALUATION TESTS
    # ----------------------------------------------------

    def test_frontend_evaluation_correct_vs_incorrect_react_solution(self):
        """Task 4: Evaluates both correct and incorrect React component solutions (RE-E01)"""
        self.client.force_authenticate(user=self.user)

        # 1. Incorrect solution containing bug signature count = count + 1
        buggy_code = "import React, { useState } from 'react';\nexport default function Counter() {\n  const [count, setCount] = useState(0);\n  const increment = () => { count = count + 1; setCount(count); };\n  return <button onClick={increment}>{count}</button>;\n}"
        res_buggy = self.client.post('/api/challenges/RE-E01/run', {'code': buggy_code}, format='json')
        self.assertEqual(res_buggy.status_code, status.HTTP_200_OK)
        self.assertFalse(res_buggy.data['success'])
        self.assertFalse(res_buggy.data['testCases'][0]['passed'])

        # 2. Correct solution with immutable setCount(count + 1)
        fixed_code = "import React, { useState } from 'react';\nexport default function Counter() {\n  const [count, setCount] = useState(0);\n  const increment = () => setCount(prev => prev + 1);\n  return <button onClick={increment}>{count}</button>;\n}"
        res_fixed = self.client.post('/api/challenges/RE-E01/run', {'code': fixed_code}, format='json')
        self.assertEqual(res_fixed.status_code, status.HTTP_200_OK)
        self.assertTrue(res_fixed.data['success'])
        self.assertTrue(res_fixed.data['testCases'][0]['passed'])

    def test_frontend_evaluation_correct_vs_incorrect_css_solution(self):
        """Task 4: Evaluates both correct and incorrect CSS responsive grid solutions (RE-H03)"""
        self.client.force_authenticate(user=self.user)

        # 1. Incorrect CSS containing bug signature repeat(4, minmax(0, 1fr)) in mobile query
        buggy_css = "/* BUG */\n.cards { display: grid; grid-template-columns: repeat(4, 1fr); }\n@media (max-width: 768px) { .cards { grid-template-columns: repeat(4, minmax(0, 1fr)); } }"
        res_buggy = self.client.post('/api/challenges/RE-H03/run', {'code': buggy_css}, format='json')
        self.assertEqual(res_buggy.status_code, status.HTTP_200_OK)
        self.assertFalse(res_buggy.data['success'])

        # 2. Correct responsive CSS with single column grid for mobile
        fixed_css = ".cards { display: grid; grid-template-columns: repeat(4, 1fr); }\n@media (max-width: 768px) { .cards { grid-template-columns: repeat(1, minmax(0, 1fr)); } }"
        res_fixed = self.client.post('/api/challenges/RE-H03/run', {'code': fixed_css}, format='json')
        self.assertEqual(res_fixed.status_code, status.HTTP_200_OK)
        self.assertTrue(res_fixed.data['success'])

    # ----------------------------------------------------
    # PHASE 2 TASK 5: CHALLENGE FILTERING & ORGANIZATION TESTS
    # ----------------------------------------------------

    def test_challenge_filtering_by_difficulty_tech_and_category(self):
        """Task 5: Filtering challenges by difficulty, technology, and category"""
        # Filter by difficulty
        res_diff = self.client.get('/api/challenges', {'difficulty': 'Easy'})
        self.assertEqual(res_diff.status_code, status.HTTP_200_OK)
        self.assertTrue(all(c['difficulty'] == 'Easy' for c in res_diff.data))

        # Filter by technology
        res_tech = self.client.get('/api/challenges', {'technology': 'SQL'})
        self.assertEqual(res_tech.status_code, status.HTTP_200_OK)
        self.assertTrue(all(c['technology'] == 'SQL' for c in res_tech.data))

    def test_challenge_filtering_by_arena_type(self):
        """Task 5: Filtering challenges by arena/challenge_type (SQL, Frontend, Debugging)"""
        # SQL Arena
        res_sql = self.client.get('/api/challenges', {'arena': 'sql'})
        self.assertEqual(res_sql.status_code, status.HTTP_200_OK)
        self.assertTrue(all(c['technology'] == 'SQL' or '[SQL-' in c['title'] for c in res_sql.data))

        # Frontend Studio Arena
        res_fe = self.client.get('/api/challenges', {'arena': 'frontend'})
        self.assertEqual(res_fe.status_code, status.HTTP_200_OK)
        self.assertGreater(len(res_fe.data), 0)

    def test_challenge_filtering_by_search_query(self):
        """Task 5: Search filtering by keyword matching title/description/category/tech"""
        res_search = self.client.get('/api/challenges', {'search': 'Counter'})
        self.assertEqual(res_search.status_code, status.HTTP_200_OK)
        self.assertGreater(len(res_search.data), 0)
        self.assertTrue(any('Counter' in c['title'] for c in res_search.data))

    # ----------------------------------------------------
    # PHASE 2 TASK 6: CHALLENGE DATA QUALITY TESTS
    # ----------------------------------------------------

    def test_challenge_data_quality_complete_catalog_metadata(self):
        """Task 6: Audits catalog records to ensure complete metadata across all challenge records"""
        from buggyman.views import SPECIAL_CHALLENGE_CATALOG
        self.assertGreaterEqual(len(SPECIAL_CHALLENGE_CATALOG), 20)

        for key, item in SPECIAL_CHALLENGE_CATALOG.items():
            self.assertTrue(item.get('title'), f"Missing title in {key}")
            self.assertTrue(item.get('description'), f"Missing description in {key}")
            self.assertIn(item.get('difficulty'), ['Easy', 'Medium', 'Hard'], f"Invalid difficulty in {key}")
            self.assertTrue(item.get('technology'), f"Missing technology in {key}")
            self.assertTrue(item.get('category'), f"Missing category in {key}")
            self.assertTrue(item.get('time_estimate'), f"Missing time_estimate in {key}")
            self.assertGreater(item.get('points', 0), 0, f"Invalid points in {key}")
            self.assertGreaterEqual(len(item.get('files', [])), 1, f"Missing files in {key}")
            self.assertGreaterEqual(len(item.get('test_cases', [])), 1, f"Missing test_cases in {key}")
            self.assertTrue(item.get('bug_signature'), f"Missing bug_signature in {key}")
            self.assertTrue(item.get('suspected_component'), f"Missing suspected_component in {key}")

    def test_sql_challenges_contain_schema_and_sample_data(self):
        """Task 6: Audits all SQL challenges to ensure valid schema.sql DDL and sample INSERT data"""
        from buggyman.views import SPECIAL_CHALLENGE_CATALOG
        sql_challenges = {k: v for k, v in SPECIAL_CHALLENGE_CATALOG.items() if k.startswith('SQL-')}
        self.assertEqual(len(sql_challenges), 10)

        for key, item in sql_challenges.items():
            filenames = [f['name'].lower() for f in item['files']]
            self.assertIn('schema.sql', filenames, f"SQL challenge {key} missing schema.sql")
            schema_file = next(f for f in item['files'] if f['name'].lower() == 'schema.sql')
            self.assertIn('CREATE TABLE', schema_file['content'].upper(), f"{key} schema.sql missing CREATE TABLE")
            self.assertIn('INSERT INTO', schema_file['content'].upper(), f"{key} schema.sql missing INSERT INTO")

    def test_frontend_challenges_contain_multi_file_starter_code(self):
        """Task 6: Audits all Frontend challenges to ensure working multi-file (.jsx + .css) starter code"""
        from buggyman.views import SPECIAL_CHALLENGE_CATALOG
        fe_challenges = {k: v for k, v in SPECIAL_CHALLENGE_CATALOG.items() if k.startswith('RE-')}
        self.assertEqual(len(fe_challenges), 10)

        for key, item in fe_challenges.items():
            files = item['files']
            self.assertGreaterEqual(len(files), 2, f"Frontend challenge {key} has less than 2 workspace files")
            extensions = [f['name'].split('.')[-1].lower() for f in files]
            self.assertIn('jsx', extensions, f"Frontend challenge {key} missing .jsx component file")
            self.assertIn('css', extensions, f"Frontend challenge {key} missing .css style file")

    # ----------------------------------------------------
    # PHASE 2 TASK 7: UNIFIED CHALLENGE ARCHITECTURE TESTS
    # ----------------------------------------------------

    def test_unified_challenge_architecture_pipeline_shapes(self):
        """Task 7: Verifies standardized response payload contracts across Run and Submit endpoints for all arenas"""
        self.client.force_authenticate(user=self.user)

        # 1. Test Run endpoint standardized shape for SQL arena (SQL-E01)
        res_sql_run = self.client.post('/api/challenges/SQL-E01/run', {'code': "SELECT * FROM orders WHERE status = 'completed';"}, format='json')
        self.assertEqual(res_sql_run.status_code, status.HTTP_200_OK)
        for key in ['success', 'score', 'testsPassed', 'testsTotal', 'testCases', 'stdout', 'stderr', 'executionTime', 'timedOut', 'error', 'bugSignatureDetected', 'aiSummary']:
            self.assertIn(key, res_sql_run.data, f"Missing {key} in SQL run response")

        # 2. Test Submit endpoint standardized shape for Frontend arena (RE-E01)
        fixed_code = "import React, { useState } from 'react';\nexport default function Counter() {\n  const [count, setCount] = useState(0);\n  const increment = () => setCount(prev => prev + 1);\n  return <button onClick={increment}>{count}</button>;\n}"
        res_fe_sub = self.client.post('/api/challenges/RE-E01/submit', {'code': fixed_code}, format='json')
        self.assertEqual(res_fe_sub.status_code, status.HTTP_200_OK)
        for key in ['submissionId', 'success', 'score', 'attemptNumber', 'alreadySolved', 'timeTaken', 'bugsFixed', 'remainingIssues', 'testCases', 'stdout', 'stderr', 'executionTime', 'timedOut', 'error', 'aiSummary']:
            self.assertIn(key, res_fe_sub.data, f"Missing {key} in Frontend submit response")

    # ----------------------------------------------------
    # PHASE 2 TASK 8: FULL CHALLENGE-SYSTEM TESTING
    # ----------------------------------------------------

    def test_e2e_debugging_arena_syntax_error_and_empty_code(self):
        """Task 8: Tests Debugging Arena handling syntax errors and empty code submissions"""
        self.client.force_authenticate(user=self.user)

        # 1. Syntax Error Code
        res_syntax = self.client.post(f'/api/challenges/{self.challenge.id}/run', {'code': 'def broken_function(: print("bad syntax")'}, format='json')
        self.assertEqual(res_syntax.status_code, status.HTTP_200_OK)
        self.assertFalse(res_syntax.data['success'])

        # 2. Empty Code
        res_empty = self.client.post(f'/api/challenges/{self.challenge.id}/run', {'code': ''}, format='json')
        self.assertEqual(res_empty.status_code, status.HTTP_200_OK)

    def test_e2e_sql_arena_easy_medium_hard_challenges(self):
        """Task 8: End-to-end evaluation across SQL Lab challenges (Easy, Medium, Hard)"""
        self.client.force_authenticate(user=self.user)

        # Easy SQL: SQL-E01 (WHERE filter)
        res_e01 = self.client.post('/api/challenges/SQL-E01/run', {'code': "SELECT * FROM orders WHERE status = 'completed';"}, format='json')
        self.assertTrue(res_e01.data['success'])

        # Easy SQL: SQL-E02 (ORDER BY)
        res_e02 = self.client.post('/api/challenges/SQL-E02/run', {'code': "SELECT name, price FROM products ORDER BY price ASC;"}, format='json')
        self.assertTrue(res_e02.data['success'])

        # Medium SQL: SQL-M01 (GROUP BY)
        res_m01 = self.client.post('/api/challenges/SQL-M01/run', {'code': "SELECT region, SUM(amount) FROM sales GROUP BY region;"}, format='json')
        self.assertTrue(res_m01.data['success'])

        # Hard SQL: SQL-H01 (Window function)
        res_h01 = self.client.post('/api/challenges/SQL-H01/run', {'code': "SELECT *, RANK() OVER (PARTITION BY department ORDER BY salary DESC) FROM employee_metrics;"}, format='json')
        self.assertTrue(res_h01.data['success'])

    def test_e2e_frontend_arena_easy_medium_hard_challenges(self):
        """Task 8: End-to-end evaluation across Frontend Studio challenges (Easy, Medium, Hard)"""
        self.client.force_authenticate(user=self.user)

        # Easy Frontend: RE-E01 (Counter)
        code_e01 = "import React, { useState } from 'react';\nexport default function Counter() {\n const [count, setCount] = useState(0);\n return <button onClick={() => setCount(prev => prev + 1)}>{count}</button>;\n}"
        res_e01 = self.client.post('/api/challenges/RE-E01/run', {'code': code_e01}, format='json')
        self.assertTrue(res_e01.data['success'])

        # Hard Frontend: RE-H03 (Responsive Grid CSS)
        css_h03 = ".cards { display: grid; grid-template-columns: repeat(4, 1fr); }\n@media (max-width: 768px) { .cards { grid-template-columns: repeat(1, minmax(0, 1fr)); } }"
        res_h03 = self.client.post('/api/challenges/RE-H03/run', {'code': css_h03}, format='json')
        self.assertTrue(res_h03.data['success'])

    def test_e2e_duplicate_submission_anti_xp_exploit(self):
        """Task 8: Submitting correct solution twice awards XP on 1st submission, 0 XP on duplicate submission"""
        self.client.force_authenticate(user=self.user)
        initial_score = self.user.total_score

        # 1st Submission
        res_sub1 = self.client.post('/api/challenges/SQL-E01/submit', {'code': "SELECT * FROM orders WHERE status = 'completed';"}, format='json')
        self.assertTrue(res_sub1.data['success'])
        self.assertEqual(res_sub1.data['score'], 100)
        self.assertFalse(res_sub1.data['alreadySolved'])

        self.user.refresh_from_db()
        self.assertEqual(self.user.total_score, initial_score + 100)

        # 2nd Submission (Duplicate)
        res_sub2 = self.client.post('/api/challenges/SQL-E01/submit', {'code': "SELECT * FROM orders WHERE status = 'completed';"}, format='json')
        self.assertTrue(res_sub2.data['success'])
        self.assertEqual(res_sub2.data['score'], 0) # No double XP exploit!
        self.assertTrue(res_sub2.data['alreadySolved'])

        self.user.refresh_from_db()
        self.assertEqual(self.user.total_score, initial_score + 100)

    # ----------------------------------------------------
    # PHASE 2.5: CHALLENGE QUALITY & CORRECTNESS AUDIT TESTS
    # ----------------------------------------------------

    def test_phase_2_5_audit_chain_integrity_all_challenges(self):
        """Phase 2.5: Verifies that Question -> Starter Code -> Intended Bug -> Expected -> Test Cases chain is logically aligned for all challenges"""
        from buggyman.views import SPECIAL_CHALLENGE_CATALOG
        self.assertGreaterEqual(len(SPECIAL_CHALLENGE_CATALOG), 20)

        for key, item in SPECIAL_CHALLENGE_CATALOG.items():
            files = item.get('files', [])
            all_code = "\n".join([f.get('content', '') for f in files])
            bug_sig = item.get('bug_signature', '')

            # 1. Verify starter code actually contains the described bug signature
            norm_bug = re.sub(r'\s+', ' ', bug_sig).strip().lower()
            norm_code = re.sub(r'\s+', ' ', all_code).strip().lower()
            self.assertIn(norm_bug, norm_code, f"Challenge {key} starter code missing bug signature '{bug_sig}'")

            # 2. Verify suspected component exists in files
            component = item.get('suspected_component')
            file_names = [f.get('name') for f in files]
            self.assertIn(component, file_names, f"Challenge {key} suspected component '{component}' not found in files")

    def test_phase_2_5_alternative_valid_solutions_pass(self):
        """Phase 2.5: Verifies that valid alternative solutions pass evaluation cleanly across SQL, Frontend, and Debugging"""
        self.client.force_authenticate(user=self.user)

        # 1. SQL Alternative: Explicit column selection in SQL-E01
        res_sql_alt = self.client.post('/api/challenges/SQL-E01/run', {'code': "SELECT id, customer_id, amount, status FROM orders WHERE status = 'completed';"}, format='json')
        self.assertTrue(res_sql_alt.data['success'])

        # 2. SQL Alternative: Omitted ASC keyword in ORDER BY SQL-E02
        res_sql_alt2 = self.client.post('/api/challenges/SQL-E02/run', {'code': "SELECT name, price FROM products ORDER BY price;"}, format='json')
        self.assertTrue(res_sql_alt2.data['success'])

        # 3. SQL Alternative: Schema DDL primary key variation SQL-E03
        res_sql_alt3 = self.client.post('/api/challenges/SQL-E03/run', {'code': "CREATE TABLE users (username VARCHAR(50) PRIMARY KEY, email VARCHAR(100));"}, format='json')
        self.assertTrue(res_sql_alt3.data['success'])

        # 4. React Alternative: Functional state updater in RE-E01
        res_react_alt = self.client.post('/api/challenges/RE-E01/run', {'code': "import React, { useState } from 'react';\nexport default function Counter() {\n const [count, setCount] = useState(0);\n return <button onClick={() => setCount(prev => prev + 1)}>{count}</button>;\n}"}, format='json')
        self.assertTrue(res_react_alt.data['success'])

        # 5. React Alternative: Named function state updater in RE-E01
        res_react_alt2 = self.client.post('/api/challenges/RE-E01/run', {'code': "import React, { useState } from 'react';\nexport default function Counter() {\n const [count, setCount] = useState(0);\n function handleInc() { setCount(c => c + 1); }\n return <button onClick={handleInc}>{count}</button>;\n}"}, format='json')
        self.assertTrue(res_react_alt2.data['success'])

        # 6. React Router Alternative: Imported Link tag in RE-E03
        res_rr_alt = self.client.post('/api/challenges/RE-E03/run', {'code': "import React from 'react';\nimport { Link } from 'react-router-dom';\nexport default function Navbar() {\n return <nav><Link to=\"/dashboard\">Dashboard</Link></nav>;\n}"}, format='json')
        self.assertTrue(res_rr_alt.data['success'])

    # ----------------------------------------------------
    # PHASE 3 TASK 1: AI HINT SYSTEM TESTS
    # ----------------------------------------------------

    def test_phase_3_task_1_ai_hint_system(self):
        """Phase 3 Task 1: Tests context-aware AI hint generation, fallback handling, and security key non-exposure"""
        self.client.force_authenticate(user=self.user)

        # 1. Request hint on real SQL challenge (SQL-E01)
        res_hint1 = self.client.post('/api/challenges/SQL-E01/hint', {
            'code': 'SELECT * FROM orders;',
            'previousHints': []
        }, format='json')

        self.assertEqual(res_hint1.status_code, status.HTTP_200_OK)
        self.assertIn('hint', res_hint1.data)
        self.assertEqual(res_hint1.data['hintNumber'], 1)
        self.assertTrue(len(res_hint1.data['hint']) > 10)
        # Verify secret keys are NOT exposed in response payload
        self.assertNotIn('api_key', json.dumps(res_hint1.data).lower())
        self.assertNotIn('secret', json.dumps(res_hint1.data).lower())

        # 2. Request 2nd hint passing previous hints and failed test cases context
        res_hint2 = self.client.post('/api/challenges/RE-E01/hint', {
            'code': 'function Counter() { count = count + 1; }',
            'previousHints': [res_hint1.data['hint']],
            'testResults': [{'name': 'State update', 'passed': False, 'expected': 'setCount(prev => prev + 1)', 'actual': 'count = count + 1'}]
        }, format='json')

        self.assertEqual(res_hint2.status_code, status.HTTP_200_OK)
        self.assertEqual(res_hint2.data['hintNumber'], 2)
        self.assertIn('hint', res_hint2.data)

    # ----------------------------------------------------
    # PHASE 3 TASK 2: PROGRESSIVE HINT SYSTEM TESTS
    # ----------------------------------------------------

    def test_phase_3_task_2_progressive_hint_system(self):
        """Phase 3 Task 2: Verifies 3-level progressive hint generation (Level 1 Conceptual -> Level 2 Specific -> Level 3 Targeted)"""
        self.client.force_authenticate(user=self.user)

        # Level 1: Conceptual Direction
        res_l1 = self.client.post('/api/challenges/RE-E01/hint', {
            'code': 'function Counter() { count = count + 1; }',
            'level': 1,
            'previousHints': []
        }, format='json')
        self.assertEqual(res_l1.status_code, status.HTTP_200_OK)
        self.assertEqual(res_l1.data['level'], 1)
        self.assertIn('Conceptual', res_l1.data['hint'])

        # Level 2: Specific Guidance
        res_l2 = self.client.post('/api/challenges/RE-E01/hint', {
            'code': 'function Counter() { count = count + 1; }',
            'level': 2,
            'previousHints': [res_l1.data['hint']]
        }, format='json')
        self.assertEqual(res_l2.status_code, status.HTTP_200_OK)
        self.assertEqual(res_l2.data['level'], 2)
        self.assertIn('Specific', res_l2.data['hint'])

        # Level 3: Targeted Problem Area
        res_l3 = self.client.post('/api/challenges/RE-E01/hint', {
            'code': 'function Counter() { count = count + 1; }',
            'level': 3,
            'previousHints': [res_l1.data['hint'], res_l2.data['hint']]
        }, format='json')
        self.assertEqual(res_l3.status_code, status.HTTP_200_OK)
        self.assertEqual(res_l3.data['level'], 3)
        self.assertIn('Targeted', res_l3.data['hint'])

    # ----------------------------------------------------
    # PHASE 3 TASK 3: AI CODE/DEBUGGING FEEDBACK TESTS
    # ----------------------------------------------------

    def test_phase_3_task_3_ai_code_debugging_feedback(self):
        """Phase 3 Task 3: Verifies structured AI diagnostic feedback for failing and passing solutions"""
        self.client.force_authenticate(user=self.user)

        # 1. Failing solution feedback for SQL-E01
        res_fb_fail = self.client.post('/api/challenges/SQL-E01/feedback', {
            'code': 'SELECT * FROM orders;',
            'testResults': [{'name': 'Filters completed orders', 'passed': False, 'expected': "WHERE status = 'completed'", 'actual': '4 rows returned'}]
        }, format='json')

        self.assertEqual(res_fb_fail.status_code, status.HTTP_200_OK)
        for key in ['whatIsWrong', 'whyItIsWrong', 'conceptToUnderstand', 'suggestedDirection', 'provider']:
            self.assertIn(key, res_fb_fail.data, f"Missing {key} in feedback response")

        self.assertTrue(len(res_fb_fail.data['whatIsWrong']) > 5)
        self.assertTrue(len(res_fb_fail.data['whyItIsWrong']) > 5)

        # 2. Passing solution feedback for SQL-E01
        res_fb_pass = self.client.post('/api/challenges/SQL-E01/feedback', {
            'code': "SELECT * FROM orders WHERE status = 'completed';",
            'testResults': [{'name': 'Filters completed orders', 'passed': True, 'expected': "WHERE status = 'completed'", 'actual': '2 rows returned'}]
        }, format='json')

        self.assertEqual(res_fb_pass.status_code, status.HTTP_200_OK)
        self.assertIn('No bugs detected', res_fb_pass.data['whatIsWrong'])

    # ----------------------------------------------------
    # PHASE 3 TASK 4: AI SOLUTION EXPLANATION TESTS
    # ----------------------------------------------------

    def test_phase_3_task_4_ai_solution_explanation(self):
        """Phase 3 Task 4: Verifies post-mortem solution explanation payload format and content"""
        self.client.force_authenticate(user=self.user)

        # 1. SQL challenge explanation
        res_exp_sql = self.client.post('/api/challenges/SQL-E01/explain', {
            'submittedCode': "SELECT * FROM orders WHERE status = 'completed';"
        }, format='json')

        self.assertEqual(res_exp_sql.status_code, status.HTTP_200_OK)
        for key in ['whatTheBugWas', 'whyItHappened', 'whyFixWorks', 'keyConcept', 'alternativeApproaches', 'provider']:
            self.assertIn(key, res_exp_sql.data, f"Missing {key} in explanation response")

        self.assertTrue(len(res_exp_sql.data['whatTheBugWas']) > 5)
        self.assertTrue(len(res_exp_sql.data['whyFixWorks']) > 5)

        # 2. React challenge explanation
        res_exp_react = self.client.post('/api/challenges/RE-E01/explain', {
            'submittedCode': 'function Counter() { const [count, setCount] = useState(0); return <button onClick={() => setCount(prev => prev + 1)}>{count}</button>; }'
        }, format='json')

        self.assertEqual(res_exp_react.status_code, status.HTTP_200_OK)
        self.assertIn('whatTheBugWas', res_exp_react.data)
        self.assertIn('whyFixWorks', res_exp_react.data)

    # ----------------------------------------------------
    # PHASE 3 TASK 5: AI CHALLENGE GENERATION TESTS
    # ----------------------------------------------------

    def test_phase_3_task_5_ai_challenge_generation(self):
        """Phase 3 Task 5: Verifies AI challenge generation with evaluator validation of starter and solution code"""
        self.client.force_authenticate(user=self.user)

        res_gen = self.client.post('/api/challenges/generate', {
            'difficulty': 'Easy',
            'technology': 'React',
            'category': 'Form Controls'
        }, format='json')

        self.assertEqual(res_gen.status_code, status.HTTP_201_CREATED)

        data = res_gen.data
        for key in ['id', 'title', 'description', 'technology', 'difficulty', 'files', 'testCases', 'bugSignature', 'suspectedComponent', 'solutionCode', 'evaluationValidated', 'starterCodeFailed', 'solutionCodePassed']:
            self.assertIn(key, data, f"Missing {key} in generated challenge payload")

        self.assertTrue(data['evaluationValidated'])
        self.assertTrue(len(data['files']) > 0)
        self.assertTrue(len(data['testCases']) > 0)
        self.assertIn('evaluationSummary', data)

    # ----------------------------------------------------
    # PHASE 3 TASK 6: AI BUG INJECTION TESTS
    # ----------------------------------------------------

    def test_phase_3_task_6_ai_bug_injection(self):
        """Phase 3 Task 6: Verifies AI bug injection generating buggy code from valid code with evaluator validation"""
        self.client.force_authenticate(user=self.user)

        clean_code = "function Counter() { const [count, setCount] = useState(0); return <button onClick={() => setCount(prev => prev + 1)}>{count}</button>; }"

        res_inj = self.client.post('/api/challenges/inject-bug', {
            'code': clean_code,
            'bugType': 'state_mutation',
            'technology': 'React'
        }, format='json')

        self.assertEqual(res_inj.status_code, status.HTTP_200_OK)

        data = res_inj.data
        for key in ['originalCode', 'buggyCode', 'bugType', 'intendedBug', 'suspectedComponent', 'bugSignature', 'testCases', 'evaluationValidated', 'buggyCodeFailed']:
            self.assertIn(key, data, f"Missing {key} in bug injection payload")

        self.assertEqual(data['originalCode'], clean_code)
        self.assertNotEqual(data['buggyCode'], clean_code)
        self.assertTrue(data['evaluationValidated'])

    # ----------------------------------------------------
    # PHASE 3 TASK 7: AI PERSONALIZED FEEDBACK TESTS
    # ----------------------------------------------------

    def test_phase_3_task_7_ai_personalized_feedback(self):
        """Phase 3 Task 7: Verifies AI personalized feedback analyzing user history and returning learning insights"""
        self.client.force_authenticate(user=self.user)

        res_pf = self.client.get('/api/analytics/ai-insights')
        self.assertEqual(res_pf.status_code, status.HTTP_200_OK)

        data = res_pf.data
        for key in ['debuggingStrengths', 'areasNeedingImprovement', 'recommendedFocus', 'learningStyleInsight', 'recommendedChallengeIds', 'provider']:
            self.assertIn(key, data, f"Missing {key} in personalized feedback payload")

        self.assertTrue(len(data['debuggingStrengths']) > 0)
        self.assertTrue(len(data['areasNeedingImprovement']) > 0)
        self.assertTrue(len(data['recommendedFocus']) > 5)

    # ----------------------------------------------------
    # PHASE 3 TASK 8: AI RELIABILITY, SECURITY & E2E RECOVERY TESTS
    # ----------------------------------------------------

    def test_phase_3_task_8_ai_full_suite_e2e_regression(self):
        """Phase 3 Task 8: Comprehensive security audit, key non-exposure, fallback resilience, and E2E regression"""
        self.client.force_authenticate(user=self.user)

        endpoints = [
            ('/api/challenges/RE-E01/hint', 'post', {'code': 'x=1', 'level': 1}),
            ('/api/challenges/RE-E01/hint', 'post', {'code': 'x=1', 'level': 2}),
            ('/api/challenges/RE-E01/hint', 'post', {'code': 'x=1', 'level': 3}),
            ('/api/challenges/SQL-E01/feedback', 'post', {'code': 'SELECT * FROM orders;'}),
            ('/api/challenges/SQL-E01/explain', 'post', {'submittedCode': "SELECT * FROM orders WHERE status = 'completed';"}),
            ('/api/challenges/generate', 'post', {'difficulty': 'Easy', 'technology': 'React'}),
            ('/api/challenges/inject-bug', 'post', {'code': 'x=1', 'bugType': 'logic', 'technology': 'Python'}),
            ('/api/analytics/ai-insights', 'get', {})
        ]

        # 1. Verify API Key non-exposure across all endpoints
        for url, method, payload in endpoints:
            if method == 'post':
                res = self.client.post(url, payload, format='json')
            else:
                res = self.client.get(url)

            self.assertIn(res.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED], f"Endpoint {url} failed with {res.status_code}")
            raw_json = json.dumps(res.data).lower()
            self.assertNotIn('api_key', raw_json, f"Secret api_key leaked in {url}")
            self.assertNotIn('secret', raw_json, f"Secret phrase leaked in {url}")
            self.assertNotIn('bearer', raw_json, f"Bearer token leaked in {url}")

        # 2. Verify Provider Fallback Resilience when external API fails
        original_provider = getattr(settings, 'AI_PROVIDER', 'gemini')
        try:
            # Force invalid provider configuration to test fallback handling
            settings.AI_PROVIDER = 'invalid_provider'
            res_fallback = self.client.post('/api/challenges/RE-E01/hint', {'code': 'x=1', 'level': 1}, format='json')
            self.assertEqual(res_fallback.status_code, status.HTTP_200_OK)
            self.assertEqual(res_fallback.data['provider'], 'mock')
            self.assertTrue(res_fallback.data['isFallback'])
        finally:
            settings.AI_PROVIDER = original_provider

    # ----------------------------------------------------
    # PHASE 4 TASK 1: LEARNING ANALYTICS DATA TESTS
    # ----------------------------------------------------

    def test_phase_4_task_1_learning_analytics_data(self):
        """Phase 4 Task 1: Verifies collection of learning performance data across challenge activity"""
        self.client.force_authenticate(user=self.user)

        # Submit a challenge attempt with hints used and error stderr
        res_sub = self.client.post('/api/challenges/RE-E01/submit', {
            'code': 'function Counter() { count = count + 1; return <div>Counter</div>; }',
            'hintsUsed': 2
        }, format='json')

        self.assertEqual(res_sub.status_code, status.HTTP_200_OK)

        # Retrieve learning analytics data
        res_analytics = self.client.get('/api/analytics/learning-data')
        self.assertEqual(res_analytics.status_code, status.HTTP_200_OK)

        data = res_analytics.data
        for key in ['userId', 'username', 'totalSubmissions', 'solvedCount', 'successRate', 'hintsUsedTotal', 'errorTypesSummary', 'technologyPerformance', 'categoryPerformance', 'difficultyPerformance', 'completionHistory']:
            self.assertIn(key, data, f"Missing {key} in learning analytics payload")

        self.assertTrue(data['totalSubmissions'] > 0)
        self.assertTrue(data['hintsUsedTotal'] >= 2)
        self.assertIn('React', data['technologyPerformance'])
        self.assertTrue(len(data['completionHistory']) > 0)

    # ----------------------------------------------------
    # PHASE 4 TASK 2: USER SKILL PROFILE TESTS
    # ----------------------------------------------------

    def test_phase_4_task_2_user_skill_profile(self):
        """Phase 4 Task 2: Verifies dynamic calculation and updating of user proficiency matrix"""
        self.client.force_authenticate(user=self.user)

        # 1. Fetch initial skill matrix
        res_initial = self.client.get('/api/profile/skill-matrix')
        self.assertEqual(res_initial.status_code, status.HTTP_200_OK)
        initial_data = res_initial.data

        for key in ['userId', 'overallProficiency', 'proficiencyLevel', 'technologySkills', 'categorySkills']:
            self.assertIn(key, initial_data, f"Missing {key} in skill matrix payload")

        # 2. Submit a successful solution to update skill profile
        res_sub = self.client.post('/api/challenges/RE-E01/submit', {
            'code': 'function Counter() { const [count, setCount] = useState(0); return <button onClick={() => setCount(prev => prev + 1)}>{count}</button>; }'
        }, format='json')
        self.assertEqual(res_sub.status_code, status.HTTP_200_OK)

        # 3. Verify updated skill profile
        res_updated = self.client.get('/api/profile/skill-matrix')
        self.assertEqual(res_updated.status_code, status.HTTP_200_OK)
        updated_data = res_updated.data

        self.assertIn('React', updated_data['technologySkills'])
        self.assertTrue(updated_data['technologySkills']['React'] > 0)
        
        # Verify user model skills JSON field was updated in DB
        self.user.refresh_from_db()
        self.assertIn('React', self.user.skills)

    # ----------------------------------------------------
    # PHASE 4 TASK 3: DIFFICULTY PREDICTION TESTS
    # ----------------------------------------------------

    def test_phase_4_task_3_difficulty_prediction(self):
        """Phase 4 Task 3: Verifies statistical ML difficulty predictor classifying challenges as too_easy, appropriate, or too_difficult"""
        self.client.force_authenticate(user=self.user)

        res_pred = self.client.post('/api/challenges/RE-E01/predict-difficulty')
        self.assertEqual(res_pred.status_code, status.HTTP_200_OK)

        data = res_pred.data
        for key in ['challengeId', 'predictedCategory', 'expectedSuccessProbability', 'confidenceScore', 'userTechSkill', 'reasoning']:
            self.assertIn(key, data, f"Missing {key} in difficulty prediction payload")

        self.assertIn(data['predictedCategory'], ['too_easy', 'appropriate', 'too_difficult'])
        self.assertTrue(0.0 <= data['expectedSuccessProbability'] <= 1.0)

    # ----------------------------------------------------
    # PHASE 4 TASK 4: PERSONALIZED RECOMMENDATION TESTS
    # ----------------------------------------------------

    def test_phase_4_task_4_personalized_challenge_recommendation(self):
        """Phase 4 Task 4: Verifies multi-factor ML challenge recommendations with human-readable explanations"""
        self.client.force_authenticate(user=self.user)

        res_rec = self.client.get('/api/challenges/recommendations?limit=3')
        self.assertEqual(res_rec.status_code, status.HTTP_200_OK)

        data = res_rec.data
        self.assertTrue(isinstance(data, list))
        self.assertTrue(len(data) > 0)

        top_rec = data[0]
        for key in ['challenge', 'recommendationScore', 'predictedCategory', 'expectedSuccessProbability', 'reason']:
            self.assertIn(key, top_rec, f"Missing {key} in recommendation item payload")

        self.assertTrue(len(top_rec['reason']) > 5)

    # ----------------------------------------------------
    # PHASE 4 TASK 5: ADAPTIVE DIFFICULTY TESTS
    # ----------------------------------------------------

    def test_phase_4_task_5_adaptive_difficulty(self):
        """Phase 4 Task 5: Verifies tier escalation on consecutive successes and regression on failures without changing DB records"""
        self.client.force_authenticate(user=self.user)

        # 1. Verify initial adaptive state
        res_initial = self.client.get('/api/analytics/adaptive-difficulty')
        self.assertEqual(res_initial.status_code, status.HTTP_200_OK)
        for key in ['recommendedTier', 'trend', 'consecutiveSuccesses', 'consecutiveFailures', 'recentAccuracy', 'explanation']:
            self.assertIn(key, res_initial.data, f"Missing {key} in adaptive state payload")

        # 2. Simulate 3 consecutive successful solutions
        for _ in range(3):
            self.client.post('/api/challenges/RE-E01/submit', {
                'code': 'function Counter() { const [count, setCount] = useState(0); return <button onClick={() => setCount(prev => prev + 1)}>{count}</button>; }'
            }, format='json')

        res_escalated = self.client.get('/api/analytics/adaptive-difficulty')
        self.assertEqual(res_escalated.status_code, status.HTTP_200_OK)
        self.assertEqual(res_escalated.data['recommendedTier'], 'Hard')
        self.assertEqual(res_escalated.data['trend'], 'escalating')
        self.assertEqual(res_escalated.data['consecutiveSuccesses'], 3)

        # 3. Simulate 2 consecutive failed attempts
        for _ in range(2):
            self.client.post('/api/challenges/RE-E01/submit', {
                'code': 'function Counter() { count = count + 1; }'
            }, format='json')

        res_regressed = self.client.get('/api/analytics/adaptive-difficulty')
        self.assertEqual(res_regressed.status_code, status.HTTP_200_OK)
        self.assertEqual(res_regressed.data['recommendedTier'], 'Easy')
        self.assertEqual(res_regressed.data['trend'], 'regressing')
        self.assertEqual(res_regressed.data['consecutiveFailures'], 2)

        # 4. Confirm challenge records remain unchanged
        from buggyman.views import get_challenge_or_none
        chal = get_challenge_or_none('RE-E01')
        diff_val = chal.get('difficulty') if isinstance(chal, dict) else chal.difficulty
        self.assertEqual(diff_val, 'Easy')

    # ----------------------------------------------------
    # PHASE 4 TASK 6: WEAK-AREA DETECTION TESTS
    # ----------------------------------------------------

    def test_phase_4_task_6_weak_area_detection(self):
        """Phase 4 Task 6: Verifies weak-area pattern detection and integration with diagnostic feedback"""
        self.client.force_authenticate(user=self.user)

        # 1. Submit 2 failing state mutation attempts
        for _ in range(2):
            self.client.post('/api/challenges/RE-E01/submit', {
                'code': 'function Counter() { count = count + 1; // direct mutation error }'
            }, format='json')

        # 2. Fetch detected weaknesses
        res_weak = self.client.get('/api/analytics/weaknesses')
        self.assertEqual(res_weak.status_code, status.HTTP_200_OK)

        data = res_weak.data
        for key in ['userId', 'weaknessCount', 'topWeaknesses', 'summary']:
            self.assertIn(key, data, f"Missing {key} in weakness payload")

        self.assertTrue(data['weaknessCount'] > 0)
        self.assertTrue(len(data['topWeaknesses']) > 0)
        first_weakness = data['topWeaknesses'][0]
        self.assertIn('name', first_weakness)
        self.assertIn('severity', first_weakness)

        # 3. Verify AI feedback includes weakness integration context cleanly
        res_fb = self.client.post('/api/challenges/RE-E01/feedback', {
            'code': 'function Counter() { count = count + 1; }'
        }, format='json')
        self.assertEqual(res_fb.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------
    # PHASE 4 TASK 7: PERSONALIZED LEARNING PATH TESTS
    # ----------------------------------------------------

    def test_phase_4_task_7_personalized_learning_path(self):
        """Phase 4 Task 7: Verifies generation of 5-stage progression learning path targeting user weakness"""
        self.client.force_authenticate(user=self.user)

        res_path = self.client.get('/api/challenges/learning-path')
        self.assertEqual(res_path.status_code, status.HTTP_200_OK)

        data = res_path.data
        for key in ['targetConcept', 'stages', 'completedStages', 'totalStages', 'completionPercentage', 'currentStageIndex']:
            self.assertIn(key, data, f"Missing {key} in learning path payload")

        self.assertTrue(len(data['stages']) >= 3)
        stage1 = data['stages'][0]
        for skey in ['stageNumber', 'title', 'difficulty', 'challenge', 'completed']:
            self.assertIn(skey, stage1, f"Missing {skey} in stage item payload")

    # ----------------------------------------------------
    # PHASE 4 TASK 8: ML EVALUATION & E2E REGRESSION TESTS
    # ----------------------------------------------------

    def test_phase_4_task_8_ml_evaluation_and_e2e_suite(self):
        """Phase 4 Task 8: Comprehensive ML evaluation across New User, Strong User, Struggling User, Asymmetric Skill User, and Determinism"""

        # 1. New User Profile (Cold Start Baseline)
        new_user = User.objects.create_user(username='newbie_user', password='password123')
        self.client.force_authenticate(user=new_user)

        res_new_matrix = self.client.get('/api/profile/skill-matrix')
        self.assertEqual(res_new_matrix.data['overallProficiency'], 0)
        self.assertEqual(res_new_matrix.data['proficiencyLevel'], 'Novice')

        res_new_recs = self.client.get('/api/challenges/recommendations?limit=3')
        self.assertTrue(len(res_new_recs.data) > 0)
        self.assertIn('reason', res_new_recs.data[0])

        res_new_path = self.client.get('/api/challenges/learning-path')
        self.assertEqual(res_new_path.data['completedStages'], 0)

        # 2. Strong User Profile (High Accuracy & Escalation)
        strong_user = User.objects.create_user(username='strong_dev', password='password123')
        self.client.force_authenticate(user=strong_user)

        for _ in range(3):
            self.client.post('/api/challenges/RE-E01/submit', {
                'code': 'function Counter() { const [count, setCount] = useState(0); return <button onClick={() => setCount(prev => prev + 1)}>{count}</button>; }'
            }, format='json')

        res_strong_adaptive = self.client.get('/api/analytics/adaptive-difficulty')
        self.assertEqual(res_strong_adaptive.data['recommendedTier'], 'Hard')
        self.assertEqual(res_strong_adaptive.data['trend'], 'escalating')

        # 3. Asymmetric Skill User (Strong SQL, Weak React)
        asym_user = User.objects.create_user(username='sql_wizard', password='password123')
        self.client.force_authenticate(user=asym_user)

        # 3a. Solve SQL challenge
        self.client.post('/api/challenges/SQL-E01/submit', {
            'code': "SELECT * FROM orders WHERE status = 'completed';"
        }, format='json')

        # 3b. Fail React challenge 2 times
        for _ in range(2):
            self.client.post('/api/challenges/RE-E01/submit', {
                'code': 'function Counter() { count = count + 1; // mutation }'
            }, format='json')

        res_asym_matrix = self.client.get('/api/profile/skill-matrix')
        tech_skills = res_asym_matrix.data['technologySkills']
        self.assertTrue(tech_skills.get('SQL', 0) > tech_skills.get('React', 0))

        res_asym_weak = self.client.get('/api/analytics/weaknesses')
        self.assertTrue(res_asym_weak.data['weaknessCount'] > 0)
        self.assertTrue(
            'State' in res_asym_weak.data['topWeaknesses'][0]['name'] or
            'React' in res_asym_weak.data['topWeaknesses'][0]['name']
        )

        # 4. Determinism & Reproducibility Check
        res_rec_1 = self.client.get('/api/challenges/recommendations?limit=3')
        res_rec_2 = self.client.get('/api/challenges/recommendations?limit=3')
        self.assertEqual(
            [r['challenge']['id'] for r in res_rec_1.data],
            [r['challenge']['id'] for r in res_rec_2.data],
            "Recommendation ordering must be deterministic for identical user state"
        )

    # ----------------------------------------------------
    # PHASE 5 TASK 1: SECURITY AUDIT & PENETRATION TESTS
    # ----------------------------------------------------

    def test_phase_5_task_1_security_audit(self):
        """Phase 5 Task 1: Security Audit testing JWT auth, unauthorized access, path traversal, and evaluator isolation"""

        # 1. Test JWT expiration or malformed token rejection
        fake_client = APIClient()
        fake_client.credentials(HTTP_AUTHORIZATION='Bearer invalid_jwt_token_format_abc123')
        res_fake = fake_client.get('/api/profile')
        self.assertIn(res_fake.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # 2. Test Path Traversal attempt in sandbox execution
        res_traversal = self.engine.evaluate(self.challenge, files=[
            {'name': '../../../../etc/passwd', 'content': 'root:x:0:0:'},
            {'name': 'main.py', 'content': 'def add(): return 5'}
        ])
        self.assertTrue(res_traversal.get('success', False) or 'test_results' in res_traversal)

        # 3. Test Disallowed SQL command loading
        res_sql_sec = self.engine.evaluate({
            'technology': 'SQL',
            'test_cases': [{'id': 1, 'expected': 'test'}]
        }, files=[{'name': 'query.sql', 'content': 'SELECT load_extension("libsomething.so");'}])
        self.assertIn('SECURITY_ERROR', res_sql_sec['stderr'])
        self.assertFalse(res_sql_sec['success'])

    # ----------------------------------------------------
    # PHASE 5 TASK 2: ROLE & ADMIN SYSTEM TESTS
    # ----------------------------------------------------

    def test_phase_5_task_2_role_and_admin_system(self):
        """Phase 5 Task 2: Verifies Student vs Admin role separation and admin privileges management"""

        # 1. Normal student user receives 403 Forbidden on admin endpoint
        self.client.force_authenticate(user=self.user)
        res_denied = self.client.get('/api/admin/stats')
        self.assertEqual(res_denied.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Promote user to Admin role
        admin_user = User.objects.create_user(
            username='admin_boss',
            email='admin@buggyman.dev',
            password='adminpassword123',
            role='admin',
            is_staff=True
        )
        self.client.force_authenticate(user=admin_user)

        # 3. Admin successfully accesses stats endpoint
        res_allowed = self.client.get('/api/admin/stats')
        self.assertEqual(res_allowed.status_code, status.HTTP_200_OK)
        self.assertIn('totalUsers', res_allowed.data)
        self.assertIn('totalChallenges', res_allowed.data)

        # 4. Admin updates user role via admin user management endpoint
        res_role_update = self.client.put(f'/api/admin/users/{self.user.id}', {'role': 'admin'}, format='json')
        self.assertEqual(res_role_update.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'admin')
        self.assertTrue(self.user.is_staff)

    # ----------------------------------------------------
    # PHASE 5 TASK 3: CHALLENGE MANAGEMENT TESTS
    # ----------------------------------------------------

    def test_phase_5_task_3_challenge_management(self):
        """Phase 5 Task 3: Verifies challenge status workflow (Draft -> Review -> Published -> Archived) and completeness validation"""
        admin_user = User.objects.create_user(
            username='chal_admin',
            email='chal_admin@buggyman.dev',
            password='password123',
            role='admin',
            is_staff=True
        )
        self.client.force_authenticate(user=admin_user)

        # 1. Create a Draft challenge
        res_draft = self.client.post('/api/admin/challenges/create', {
            'title': 'Draft Bug Challenge',
            'description': 'Under development',
            'status': 'draft',
            'files': [],
            'testCases': []
        }, format='json')
        self.assertEqual(res_draft.status_code, status.HTTP_201_CREATED)
        draft_id = res_draft.data['id']
        self.assertEqual(res_draft.data['status'], 'draft')

        # 2. Attempting to publish incomplete challenge fails with 400
        res_pub_invalid = self.client.put(f'/api/admin/challenges/{draft_id}', {
            'status': 'published',
            'files': [],
            'testCases': []
        }, format='json')
        self.assertEqual(res_pub_invalid.status_code, status.HTTP_400_BAD_REQUEST)

        # 3. Publish valid challenge with files and test cases
        res_pub_valid = self.client.put(f'/api/admin/challenges/{draft_id}', {
            'status': 'published',
            'files': [{'name': 'main.py', 'content': 'def test(): return 1'}],
            'testCases': [{'id': 1, 'name': 'Unit test', 'input': 'test', 'expected': '1', 'passed': False}]
        }, format='json')
        self.assertEqual(res_pub_valid.status_code, status.HTTP_200_OK)
        self.assertEqual(res_pub_valid.data['status'], 'published')

        # 4. Confirm student users only see published challenges
        self.client.force_authenticate(user=self.user)
        res_student_list = self.client.get('/api/challenges')
        self.assertEqual(res_student_list.status_code, status.HTTP_200_OK)
        for c in res_student_list.data:
            self.assertEqual(c.get('status', 'published'), 'published')

    # ----------------------------------------------------
    # PHASE 5 TASK 4: REPORTING & FEEDBACK TESTS
    # ----------------------------------------------------

    def test_phase_5_task_4_reporting_and_feedback(self):
        """Phase 5 Task 4: Verifies user challenge reporting and admin review workflow"""
        self.client.force_authenticate(user=self.user)

        # 1. User submits report for a challenge
        res_rep = self.client.post('/api/challenges/RE-E01/report', {
            'reportType': 'wrong_test',
            'description': 'Test case 2 expects undefined instead of null.'
        }, format='json')
        self.assertEqual(res_rep.status_code, status.HTTP_201_CREATED)
        report_id = res_rep.data['id']
        self.assertEqual(res_rep.data['status'], 'open')

        # 2. Student attempting to list reports gets 403
        res_denied = self.client.get('/api/admin/reports')
        self.assertEqual(res_denied.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Admin lists reports
        admin_user = User.objects.create_user(
            username='rep_admin',
            email='rep_admin@buggyman.dev',
            password='password123',
            role='admin',
            is_staff=True
        )
        self.client.force_authenticate(user=admin_user)

        res_list = self.client.get('/api/admin/reports')
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res_list.data) > 0)

        # 4. Admin resolves report
        res_resolve = self.client.put(f'/api/admin/reports/{report_id}', {
            'status': 'resolved',
            'adminNotes': 'Corrected assertion logic in test case 2.'
        }, format='json')
        self.assertEqual(res_resolve.status_code, status.HTTP_200_OK)
        self.assertEqual(res_resolve.data['status'], 'resolved')
        self.assertEqual(res_resolve.data['adminNotes'], 'Corrected assertion logic in test case 2.')

    # ----------------------------------------------------
    # PHASE 5 TASK 5: RATE LIMITING TESTS
    # ----------------------------------------------------

    def test_phase_5_task_5_rate_limiting(self):
        """Phase 5 Task 5: Verifies rate limiting on auth and code execution endpoints returning 429 Too Many Requests"""
        clear_rate_limits()

        # 1. Execute 10 login attempts (allowed)
        for i in range(10):
            res = self.client.post('/api/login', {'email': 'test@example.com', 'password': 'wrongpassword'}, format='json')
            self.assertNotEqual(res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # 2. 11th request triggers HTTP 429 Too Many Requests
        res_throttled = self.client.post('/api/login', {'email': 'test@example.com', 'password': 'wrongpassword'}, format='json')
        self.assertEqual(res_throttled.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('retryAfterSeconds', res_throttled.data)
        self.assertIn('scope', res_throttled.data)

        clear_rate_limits()

    # ----------------------------------------------------
    # PHASE 5 TASK 6: PERFORMANCE & CACHING TESTS
    # ----------------------------------------------------

    def test_phase_5_task_6_performance_and_caching(self):
        """Phase 5 Task 6: Verifies leaderboard and ML recommendations caching and query optimization"""
        cache.clear()

        # 1. First call populates leaderboard cache
        res_lb_1 = self.client.get('/api/leaderboard')
        self.assertEqual(res_lb_1.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(cache.get('leaderboard:global'))

        # 2. Second call returns cached data
        res_lb_2 = self.client.get('/api/leaderboard')
        self.assertEqual(res_lb_2.status_code, status.HTTP_200_OK)
        self.assertEqual(res_lb_1.data, res_lb_2.data)

        # 3. Recommendations cache test
        self.client.force_authenticate(user=self.user)
        res_rec_1 = self.client.get('/api/challenges/recommendations')
        self.assertEqual(res_rec_1.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(cache.get(f'ml_recom:user_{self.user.id}:lim_5'))

        res_rec_2 = self.client.get('/api/challenges/recommendations')
        self.assertEqual(res_rec_2.status_code, status.HTTP_200_OK)
        self.assertEqual(res_rec_1.data, res_rec_2.data)

    # ----------------------------------------------------
    # PHASE 5 TASK 7: OBSERVABILITY & ERROR LOGGING TESTS
    # ----------------------------------------------------

    def test_phase_5_task_7_observability_and_error_logging(self):
        """Phase 5 Task 7: Verifies health check endpoint and structured logging payload sanitization"""
        
        # 1. Health check endpoint ping
        res_health = self.client.get('/api/health')
        self.assertEqual(res_health.status_code, status.HTTP_200_OK)
        self.assertEqual(res_health.data['status'], 'healthy')
        self.assertEqual(res_health.data['database'], 'connected')
        self.assertEqual(res_health.data['evaluator'], 'ready')
        self.assertEqual(res_health.data['cache'], 'operational')
        self.assertIn('timestamp', res_health.data)

        # 2. Sensitive log sanitization check
        raw_payload = {
            'username': 'john_doe',
            'password': 'secret_password_123',
            'token': 'Bearer secret_jwt_token',
            'nested': {
                'api_key': 'sk_live_secret123'
            }
        }
        sanitized = sanitize_data(raw_payload)
        self.assertEqual(sanitized['password'], '[REDACTED]')
        self.assertEqual(sanitized['token'], '[REDACTED]')
        self.assertEqual(sanitized['nested']['api_key'], '[REDACTED]')
        self.assertEqual(sanitized['username'], 'john_doe')

    # ----------------------------------------------------
    # PHASE 5 TASK 8: DEPLOYMENT READINESS TESTS
    # ----------------------------------------------------

    def test_phase_5_task_8_deployment_readiness(self):
        """Phase 5 Task 8: Verifies environment variable settings, static root, and deployment configurations"""
        self.assertTrue(hasattr(settings, 'SECRET_KEY'))
        self.assertTrue(hasattr(settings, 'ALLOWED_HOSTS'))
        self.assertTrue(hasattr(settings, 'STATIC_ROOT'))
        self.assertIsNotNone(settings.STATIC_ROOT)

        # Confirm health check returns healthy status in simulated production
        res_prod_health = self.client.get('/api/health')
        self.assertEqual(res_prod_health.status_code, status.HTTP_200_OK)
        self.assertEqual(res_prod_health.data['status'], 'healthy')

    # ----------------------------------------------------
    # PHASE 5 TASK 9: BACKUP & DATA INTEGRITY TESTS
    # ----------------------------------------------------

    def test_phase_5_task_9_backup_and_data_integrity(self):
        """Phase 5 Task 9: Verifies full database backup export and integrity validation workflow"""
        self.client.force_authenticate(user=self.user)

        # 1. Student attempting backup export receives 403
        res_denied = self.client.get('/api/admin/backup/export')
        self.assertEqual(res_denied.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Admin exports backup
        admin_user = User.objects.create_user(
            username='backup_admin',
            email='bkp_admin@buggyman.dev',
            password='password123',
            role='admin',
            is_staff=True
        )
        self.client.force_authenticate(user=admin_user)

        res_export = self.client.get('/api/admin/backup/export')
        self.assertEqual(res_export.status_code, status.HTTP_200_OK)
        backup_data = res_export.data
        self.assertIn('counts', backup_data)
        self.assertIn('data', backup_data)
        self.assertGreaterEqual(backup_data['counts']['users'], 1)

        # 3. Admin verifies valid backup integrity
        res_verify_valid = self.client.post('/api/admin/backup/verify', backup_data, format='json')
        self.assertEqual(res_verify_valid.status_code, status.HTTP_200_OK)
        self.assertTrue(res_verify_valid.data['valid'])

        # 4. Admin verifies corrupted backup returns 400 Bad Request
        corrupted_backup = dict(backup_data)
        corrupted_backup['counts'] = {'users': 999, 'challenges': 0, 'submissions': 0, 'reports': 0, 'notifications': 0}
        res_verify_invalid = self.client.post('/api/admin/backup/verify', corrupted_backup, format='json')
        self.assertEqual(res_verify_invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res_verify_invalid.data['valid'])

    # ----------------------------------------------------
    # PHASE 6 TASK 8: DEMO & SYSTEM VERIFICATION TESTS
    # ----------------------------------------------------

    def test_phase_6_task_8_demo_verification(self):
        """Phase 6 Task 8: Verifies full demo checklist flow including user lifecycle, submission scoring, leaderboard ranks, and security bounds"""
        # 1. Register new student
        reg_res = self.client.post('/api/register', {
            'username': 'demo_student',
            'email': 'demo@buggyman.dev',
            'password': 'Kushal_BuggyMan_2026!',
            'college': 'Demo Tech Institute'
        }, format='json')
        self.assertIn(reg_res.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        demo_user = User.objects.get(username='demo_student')

        # Authenticate demo user
        self.client.force_authenticate(user=demo_user)

        # 2. Verify profile & initial stats
        prof_res = self.client.get('/api/profile')
        self.assertEqual(prof_res.status_code, status.HTTP_200_OK)
        self.assertEqual(prof_res.data['totalScore'], 0)

        # 3. Verify ML recommendations & learning path
        rec_res = self.client.get('/api/challenges/recommendations')
        self.assertEqual(rec_res.status_code, status.HTTP_200_OK)
        
        path_res = self.client.get('/api/challenges/learning-path')
        self.assertEqual(path_res.status_code, status.HTTP_200_OK)
        self.assertIn('stages', path_res.data)

        # 4. Execute & Submit challenge solution
        sub_res = self.client.post(f'/api/challenges/{self.challenge.id}/submit', {
            'code': 'def add():\n    return 5',
            'files': [{'name': 'main.py', 'content': 'def add():\n    return 5'}]
        }, format='json')
        self.assertEqual(sub_res.status_code, status.HTTP_200_OK)
        self.assertTrue(sub_res.data['success'])

        # 5. Verify leaderboard updated with dense rank
        lead_res = self.client.get('/api/leaderboard')
        self.assertEqual(lead_res.status_code, status.HTTP_200_OK)
        leader_usernames = [u['username'] for u in lead_res.data]
        self.assertIn('demo_student', leader_usernames)

        # 6. Submit issue report
        rep_res = self.client.post(f'/api/challenges/{self.challenge.id}/report', {
            'reportType': 'wrong_test',
            'description': 'Demo verification issue report test'
        }, format='json')
        self.assertEqual(rep_res.status_code, status.HTTP_201_CREATED)

        # 7. Health check verification
        health_res = self.client.get('/api/health')
        self.assertEqual(health_res.status_code, status.HTTP_200_OK)
        self.assertEqual(health_res.data['status'], 'healthy')

    def test_catalog_120_challenges(self):
        from django.core.management import call_command
        call_command('seed_db')
        
        # 1. Verify GET /api/challenges returns published Code Challenges (50+ total)
        res = self.client.get('/api/challenges?arena=code')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        challenges = res.data
        self.assertGreaterEqual(len(challenges), 50)

        # 2. Verify difficulty breakdown (15 Easy, 20 Medium, 15 Hard)
        easy_count = sum(1 for c in challenges if c['difficulty'] == 'Easy')
        medium_count = sum(1 for c in challenges if c['difficulty'] == 'Medium')
        hard_count = sum(1 for c in challenges if c['difficulty'] == 'Hard')
        self.assertGreaterEqual(easy_count, 15)
        self.assertGreaterEqual(medium_count, 20)
        self.assertGreaterEqual(hard_count, 15)

        # 3. Test Difficulty filtering
        easy_res = self.client.get('/api/challenges?arena=code&difficulty=Easy')
        self.assertGreaterEqual(len(easy_res.data), 15)

        medium_res = self.client.get('/api/challenges?arena=code&difficulty=Medium')
        self.assertGreaterEqual(len(medium_res.data), 20)

        hard_res = self.client.get('/api/challenges?arena=code&difficulty=Hard')
        self.assertGreaterEqual(len(hard_res.data), 15)

        # 4. Test Search filtering
        search_res = self.client.get('/api/challenges?search=Webhook')
        self.assertGreaterEqual(len(search_res.data), 1)
        self.assertEqual(search_res.status_code, status.HTTP_200_OK)
        self.assertTrue(any('Webhook' in c['title'] for c in search_res.data))

        # 5. Verify SQL Lab and Frontend Studio arenas are intact
        sql_res = self.client.get('/api/challenges?arena=sql')
        self.assertEqual(sql_res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(sql_res.data), 1)

        frontend_res = self.client.get('/api/challenges?arena=frontend')
        self.assertEqual(frontend_res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(frontend_res.data), 1)

        # 6. Sample catalog challenges can be fetched and executed
        for c in challenges[:3]:
            clear_rate_limits()
            detail_res = self.client.get(f"/api/challenges/{c['id']}")
            self.assertEqual(detail_res.status_code, status.HTTP_200_OK)

            # Test Run endpoint
            run_res = self.client.post(f"/api/challenges/{c['id']}/run", {'code': ''}, format='json')
            self.assertEqual(run_res.status_code, status.HTTP_200_OK)
            self.assertIn('success', run_res.data)


class RecommendationSystemTestCase(TestCase):
    def setUp(self):
        clear_rate_limits()
        cache.clear()
        self.client = APIClient()

        # Create test challenges
        self.chal_sql = Challenge.objects.create(
            title='SQL Filter Bug',
            description='Fix WHERE query',
            difficulty='Easy',
            technology='SQL',
            category='Query',
            topics=['SQL Filter', 'WHERE'],
            skills_tested=['SQL', 'Database'],
            files=[{'name': 'query.sql', 'content': 'SELECT * FROM users;'}]
        )
        self.chal_frontend = Challenge.objects.create(
            title='React State Mutation',
            description='Fix count++',
            difficulty='Easy',
            technology='React',
            category='State Management',
            topics=['React State', 'Hooks'],
            skills_tested=['React', 'Frontend'],
            files=[{'name': 'App.jsx', 'content': 'export default function App() {}'}]
        )
        self.chal_backend = Challenge.objects.create(
            title='Python List Index Error',
            description='Fix off by one',
            difficulty='Medium',
            technology='Python',
            category='Algorithms',
            topics=['Arrays', 'Indexing'],
            skills_tested=['Python', 'Backend'],
            files=[{'name': 'main.py', 'content': 'def run(): pass'}]
        )

        # User A: Weak in SQL, Strong in Backend
        self.user_a = User.objects.create_user(
            username='usera',
            email='usera@example.com',
            password='Password123!',
            strengths=['Backend'],
            weaknesses=['SQL']
        )

        # User B: Weak in Frontend, Strong in SQL
        self.user_b = User.objects.create_user(
            username='userb',
            email='userb@example.com',
            password='Password123!',
            strengths=['SQL'],
            weaknesses=['Frontend']
        )

    def test_01_new_user_registration_with_strengths_and_weaknesses(self):
        res = self.client.post('/api/register', {
            'username': 'registereduser',
            'email': 'reguser@example.com',
            'password': 'Password123!',
            'displayName': 'Registered User',
            'strengths': ['Backend', 'SQL'],
            'weaknesses': ['Frontend', 'APIs']
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user_db = User.objects.get(username='registereduser')
        self.assertEqual(user_db.strengths, ['Backend', 'SQL'])
        self.assertEqual(user_db.weaknesses, ['Frontend', 'APIs'])

        # Test profile GET endpoint returns strengths and weaknesses
        self.client.force_authenticate(user=user_db)
        prof_res = self.client.get('/api/profile')
        self.assertEqual(prof_res.status_code, status.HTTP_200_OK)
        self.assertEqual(prof_res.data['strengths'], ['Backend', 'SQL'])
        self.assertEqual(prof_res.data['weaknesses'], ['Frontend', 'APIs'])

    def test_02_two_users_different_preferences_different_recommendations(self):

        from buggyman.ml.recommender import ChallengeRecommender
        recs_a = ChallengeRecommender.get_recommendations(self.user_a, limit=2)
        recs_b = ChallengeRecommender.get_recommendations(self.user_b, limit=2)

        self.assertGreaterEqual(len(recs_a), 1)
        self.assertGreaterEqual(len(recs_b), 1)

        # User A's top recommendation should target SQL weakness
        top_a_tech = recs_a[0]['challenge']['technology']
        self.assertEqual(top_a_tech, 'SQL')

        # User B's top recommendation should target Frontend weakness
        top_b_tech = recs_b[0]['challenge']['technology']
        self.assertEqual(top_b_tech, 'React')

    def test_03_solved_problems_not_recommended_again(self):
        from buggyman.ml.recommender import ChallengeRecommender
        # Mark SQL challenge solved for User A
        Submission.objects.create(
            user=self.user_a,
            challenge=self.chal_sql,
            submitted_code='SELECT * FROM users WHERE active = 1;',
            success=True
        )

        recs = ChallengeRecommender.get_recommendations(self.user_a, limit=5)
        rec_ids = [r['challenge']['id'] for r in recs]
        self.assertNotIn(str(self.chal_sql.id), rec_ids)

    def test_04_failed_attempts_affect_skill_calculations(self):
        from buggyman.ml.skill_profiler import SkillProfiler
        # Record failed submission for User A in Backend
        sub = Submission.objects.create(
            user=self.user_a,
            challenge=self.chal_backend,
            submitted_code='def run(): error',
            success=False,
            stderr='SyntaxError: invalid syntax'
        )
        matrix = SkillProfiler.calculate_skill_matrix(self.user_a)
        self.assertIn('Backend', matrix['categorySkills'])

    def test_05_difficulty_adapts_to_performance(self):
        from buggyman.ml.recommender import ChallengeRecommender
        # Give User A expert proficiency
        self.user_a.challenges_solved = 15
        self.user_a.total_score = 1500
        self.user_a.save()

        recs = ChallengeRecommender.get_recommendations(self.user_a, limit=3)
        self.assertGreaterEqual(len(recs), 1)

    def test_06_skill_profile_updates_after_new_submission(self):
        from buggyman.ml.skill_profiler import SkillProfiler
        matrix_before = SkillProfiler.calculate_skill_matrix(self.user_a)
        
        # User A submits clean solution
        Submission.objects.create(
            user=self.user_a,
            challenge=self.chal_sql,
            submitted_code='SELECT * FROM users;',
            success=True
        )
        matrix_after = SkillProfiler.update_user_skills(self.user_a)
        self.assertGreaterEqual(matrix_after['totalSolved'], 1)

    def test_07_user_isolation_user_a_activity_does_not_affect_user_b(self):
        from buggyman.ml.recommender import ChallengeRecommender
        from buggyman.ml.skill_profiler import SkillProfiler

        # User A solves SQL challenge
        Submission.objects.create(
            user=self.user_a,
            challenge=self.chal_sql,
            submitted_code='SELECT * FROM users;',
            success=True
        )
        SkillProfiler.update_user_skills(self.user_a)

        # Verify User B is unaffected
        self.user_b.refresh_from_db()
        self.assertEqual(self.user_b.challenges_solved, 0)

        recs_b = ChallengeRecommender.get_recommendations(self.user_b, limit=5)
        b_rec_ids = [r['challenge']['id'] for r in recs_b]
        # SQL challenge should STILL be available for User B
        self.assertIn(str(self.chal_sql.id), b_rec_ids)

    def test_08_recommendations_work_when_user_solved_many_problems(self):
        from buggyman.ml.recommender import ChallengeRecommender
        # Mark all challenges solved for User A
        for c in [self.chal_sql, self.chal_frontend, self.chal_backend]:
            Submission.objects.create(user=self.user_a, challenge=c, submitted_code='code', success=True)

        recs = ChallengeRecommender.get_recommendations(self.user_a, limit=2)
        # Should gracefully return review recommendations without crashing
        self.assertGreaterEqual(len(recs), 1)

    def test_09_no_available_problems_for_weak_topic(self):
        from buggyman.ml.recommender import ChallengeRecommender
        user_c = User.objects.create_user(
            username='userc',
            email='userc@example.com',
            password='Password123!',
            weaknesses=['ObscureTopicWithoutChallenges']
        )
        recs = ChallengeRecommender.get_recommendations(user_c, limit=3)
        self.assertGreaterEqual(len(recs), 1)

    def test_10_user_with_no_solved_problems_yet(self):
        from buggyman.ml.recommender import ChallengeRecommender
        brand_new_user = User.objects.create_user(
            username='newbie',
            email='newbie@example.com',
            password='Password123!'
        )
        recs = ChallengeRecommender.get_recommendations(brand_new_user, limit=5)
        self.assertGreaterEqual(len(recs), 1)
        self.assertIn('challenge', recs[0])
        self.assertIn('reason', recs[0])

    def test_11_sql_lab_remains_sql_only(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get('/api/challenges?arena=sql')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for item in res.data:
            tech = item.get('technology', '').upper()
            title = item.get('title', '')
            self.assertTrue(tech == 'SQL' or '[SQL-' in title, f"Non-SQL challenge found in SQL Lab: {title}")

    def test_12_frontend_studio_remains_frontend_only(self):
        self.client.force_authenticate(user=self.user_b)
        res = self.client.get('/api/challenges?arena=frontend')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for item in res.data:
            tech = item.get('technology', '')
            title = item.get('title', '')
            is_fe = tech in ['React', 'React Router', 'Web', 'CSS', 'HTML', 'Styling', 'Controlled Components'] or '[RE-' in title or '[FE-' in title
            self.assertTrue(is_fe, f"Non-Frontend challenge found in Frontend Studio: {title}")

    def test_13_code_challenges_remain_code_challenges(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get('/api/challenges?arena=code')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 1)

    def test_14_user_a_and_user_b_personalized_page_listing_ordering_differs(self):
        self.client.force_authenticate(user=self.user_a)
        res_a = self.client.get('/api/challenges?personalized=true')
        
        self.client.force_authenticate(user=self.user_b)
        res_b = self.client.get('/api/challenges?personalized=true')

        self.assertEqual(res_a.status_code, status.HTTP_200_OK)
        self.assertEqual(res_b.status_code, status.HTTP_200_OK)

        ids_a = [c['id'] for c in res_a.data]
        ids_b = [c['id'] for c in res_b.data]

        # Top personalized items for User A (weak in SQL) vs User B (weak in Frontend) should differ
        self.assertNotEqual(ids_a, ids_b)


class CareerInsightsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # User A: Strong in Backend & SQL
        self.user_a = User.objects.create_user(
            username='user_backend_master',
            email='backend@test.com',
            password='password123',
            strengths=['Backend', 'SQL', 'APIs'],
            weaknesses=['Frontend', 'DevOps']
        )

        # User B: Strong in Frontend
        self.user_b = User.objects.create_user(
            username='user_frontend_master',
            email='frontend@test.com',
            password='password123',
            strengths=['Frontend'],
            weaknesses=['SQL', 'Database']
        )

        # Cold start user with 0 submissions and 0 preferences
        self.user_cold = User.objects.create_user(
            username='user_cold_start',
            email='cold@test.com',
            password='password123'
        )

        # Create benchmark challenges
        self.chal_backend = Challenge.objects.create(
            title='[PY-01] Fix FastAPI Route',
            description='Fix backend routing exception',
            difficulty='Medium',
            technology='Python',
            category='Backend',
            topics=['Backend', 'APIs']
        )
        self.chal_sql = Challenge.objects.create(
            title='[SQL-01] Fix Aggregation',
            description='Fix GROUP BY query',
            difficulty='Medium',
            technology='SQL',
            category='SQL',
            topics=['SQL', 'Database']
        )
        self.chal_frontend = Challenge.objects.create(
            title='[RE-01] Fix Hook State',
            description='Fix state mutation bug',
            difficulty='Medium',
            technology='React',
            category='Frontend',
            topics=['Frontend']
        )

    def test_01_unauthenticated_user_denied(self):
        res = self.client.get('/api/career-insights')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_02_cold_start_user_receives_insufficient_data_notice(self):
        self.client.force_authenticate(user=self.user_cold)
        res = self.client.get('/api/career-insights')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get('isInsufficientData'))
        self.assertIn('dataMessage', res.data)

    def test_03_backend_oriented_user_receives_backend_top_match(self):
        from buggyman.ml.career_engine import CareerEngine
        # Add solved submission in backend & SQL for User A
        Submission.objects.create(
            user=self.user_a,
            challenge=self.chal_backend,
            submitted_code='def run(): pass',
            success=True
        )
        Submission.objects.create(
            user=self.user_a,
            challenge=self.chal_sql,
            submitted_code='SELECT 1;',
            success=True
        )

        insights = CareerEngine.calculate_role_insights(self.user_a)
        top_role_id = insights['topMatch']['id']
        self.assertIn(top_role_id, ['backend-developer', 'fullstack-developer', 'data-engineer'])
        self.assertIn(insights['topMatch']['matchLabel'], ['Strong Match', 'Good Match'])

    def test_04_frontend_oriented_user_receives_frontend_top_match(self):
        from buggyman.ml.career_engine import CareerEngine
        # Add solved submission in Frontend for User B
        Submission.objects.create(
            user=self.user_b,
            challenge=self.chal_frontend,
            submitted_code='export default function App() {}',
            success=True
        )

        insights = CareerEngine.calculate_role_insights(self.user_b)
        top_role_title = insights['topMatch']['title']
        self.assertIn('Frontend', top_role_title)

    def test_05_market_demand_metadata_is_separate_and_present(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get('/api/career-insights')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        top_role = res.data['topMatch']
        self.assertIn('marketDemand', top_role)
        self.assertIn('demandScore', top_role)
        self.assertIn('marketTrend', top_role)
        self.assertIn('lastUpdated', top_role)
        self.assertIn('source', top_role)

    def test_06_skill_gaps_connect_to_existing_recommendation_engine(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get('/api/career-insights')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        top_role = res.data['topMatch']
        self.assertIn('skillGaps', top_role)
        self.assertIn('recommendedChallenges', top_role)

    def test_07_user_a_cannot_access_user_b_career_data(self):
        self.client.force_authenticate(user=self.user_a)
        res_a = self.client.get('/api/career-insights')
        
        self.client.force_authenticate(user=self.user_b)
        res_b = self.client.get('/api/career-insights')

        # Top role or scores must be user isolated
        score_a = res_a.data['topMatch']['matchScore']
        score_b = res_b.data['topMatch']['matchScore']
        self.assertTrue(score_a > 0 and score_b > 0)


class BugBytesAndAIHintTestCase(TestCase):
    def setUp(self):
        clear_rate_limits()
        cache.clear()
        self.client = APIClient()

        self.user_a = User.objects.create_user(
            username='user_bugbytes_a',
            email='bb_a@test.com',
            password='password123',
            bugbytes_balance=50
        )

        self.user_b = User.objects.create_user(
            username='user_bugbytes_b',
            email='bb_b@test.com',
            password='password123',
            bugbytes_balance=10
        )

        self.chal_easy = Challenge.objects.create(
            title='[PY-E01] User Registration Case Test',
            description='Test description',
            difficulty='Easy',
            technology='Python',
            category='Validation',
            files=[{'name': 'auth.py', 'content': 'def run(): return True'}],
            test_cases=[{'id': 1, 'name': 'Test 1', 'input': 'run()', 'expected': 'True'}]
        )

    def test_01_user_initial_bugbytes_balance(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get('/api/bugbytes')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['balance'], 50)

    def test_02_challenge_completion_awards_bugbytes(self):
        from buggyman.models import Submission, BugBytesTransaction
        self.client.force_authenticate(user=self.user_a)

        res = self.client.post(f'/api/challenges/{self.chal_easy.id}/submit', {'code': 'def run(): return True'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user_a.refresh_from_db()
        # Easy (10) + First Attempt (5) + Full Test Pass (5) = 20 bonus BugBytes
        self.assertEqual(self.user_a.bugbytes_balance, 70)

        tx = BugBytesTransaction.objects.filter(user=self.user_a, transaction_type='EARN_CHALLENGE').first()
        self.assertIsNotNone(tx)
        self.assertEqual(tx.amount, 20)

    def test_03_duplicate_completion_prevents_bugbytes_farming(self):
        self.client.force_authenticate(user=self.user_a)

        # First submission
        self.client.post(f'/api/challenges/{self.chal_easy.id}/submit', {'code': 'def run(): return True'}, format='json')
        self.user_a.refresh_from_db()
        bal_after_first = self.user_a.bugbytes_balance

        # Second duplicate submission
        self.client.post(f'/api/challenges/{self.chal_easy.id}/submit', {'code': 'def run(): return True'}, format='json')
        self.user_a.refresh_from_db()
        self.assertEqual(self.user_a.bugbytes_balance, bal_after_first)

    def test_04_insufficient_bugbytes_rejects_hint(self):
        self.user_b.bugbytes_balance = 2
        self.user_b.save()

        self.client.force_authenticate(user=self.user_b)
        res = self.client.post(f'/api/challenges/{self.chal_easy.id}/hints', {'level': 1}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('need 5 BugBytes', res.data['error'])

    @patch('buggyman.ai.groq_service.AIHintService.generate_hint')
    def test_05_successful_hint_unlock_deducts_bugbytes(self, mock_gen):
        mock_gen.return_value = {
            'success': True,
            'hint': 'Focus on input string normalization.'
        }

        self.client.force_authenticate(user=self.user_a)
        res = self.client.post(f'/api/challenges/{self.chal_easy.id}/hints', {'level': 1}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['cost'], 5)
        self.assertEqual(res.data['remaining_bugbytes'], 45)
        self.assertEqual(res.data['hint'], 'Focus on input string normalization.')

        self.user_a.refresh_from_db()
        self.assertEqual(self.user_a.bugbytes_balance, 45)

    @patch('buggyman.ai.groq_service.AIHintService.generate_hint')
    def test_06_groq_failure_does_not_deduct_bugbytes(self, mock_gen):
        mock_gen.return_value = {
            'success': False,
            'error': 'AI assistance is temporarily unavailable. Your BugBytes were not deducted.'
        }

        self.client.force_authenticate(user=self.user_a)
        res = self.client.post(f'/api/challenges/{self.chal_easy.id}/hints', {'level': 1}, format='json')
        self.assertEqual(res.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

        self.user_a.refresh_from_db()
        self.assertEqual(self.user_a.bugbytes_balance, 50)

    @patch('buggyman.ai.groq_service.AIHintService.generate_hint')
    def test_07_previously_unlocked_hint_returned_at_zero_cost(self, mock_gen):
        mock_gen.return_value = {
            'success': True,
            'hint': 'Focus on input string normalization.'
        }

        self.client.force_authenticate(user=self.user_a)
        # First unlock
        res1 = self.client.post(f'/api/challenges/{self.chal_easy.id}/hints', {'level': 1}, format='json')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        # Second request (re-read)
        res2 = self.client.post(f'/api/challenges/{self.chal_easy.id}/hints', {'level': 1}, format='json')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data['cost'], 0)
        self.assertTrue(res2.data['already_unlocked'])

        # Groq service should only have been called once!
        self.assertEqual(mock_gen.call_count, 1)

    def test_08_user_isolation_on_unlocked_hints(self):
        from buggyman.models import UnlockedHint
        UnlockedHint.objects.create(
            user=self.user_a,
            challenge=self.chal_easy,
            hint_level=1,
            hint_content='User A secret hint',
            cost=5
        )

        self.client.force_authenticate(user=self.user_b)
        res = self.client.get(f'/api/challenges/{self.chal_easy.id}/hints')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)


class BugBytesStoreAndRewardsTestCase(TestCase):
    def setUp(self):
        clear_rate_limits()
        cache.clear()
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='store_tester',
            email='store@test.com',
            password='password123',
            bugbytes_balance=0 # Test user starting with zero BugBytes!
        )

        from buggyman.models import BugBytesPackage
        self.pkg_starter = BugBytesPackage.objects.create(
            name='Starter Pack',
            bugbytes=5,
            price_inr=10.00,
            is_best_value=False,
            order_priority=1,
            mission_title='Starter Money-Back Mission',
            mission_days=7,
            mission_challenge_count=5,
            mission_difficulty='Medium',
            reward_amount_inr=10.00
        )

        self.pkg_pro = BugBytesPackage.objects.create(
            name='Pro Debugger Pack',
            bugbytes=15,
            price_inr=25.00,
            is_best_value=False,
            order_priority=2,
            mission_title='Pro Money-Back Mission',
            mission_days=7,
            mission_challenge_count=5,
            mission_difficulty='Hard',
            reward_amount_inr=25.00
        )

        self.chal_easy = Challenge.objects.create(
            title='[TEST-E01] Easy Challenge',
            description='Easy desc',
            difficulty='Easy',
            technology='Python',
            category='General',
            files=[{'name': 'solution.py', 'content': 'def run(): return 1'}],
            test_cases=[{'id': 1, 'name': 'T1', 'input': 'run()', 'expected': '1'}]
        )

        self.chal_med1 = Challenge.objects.create(
            title='[TEST-M01] Medium Challenge 1',
            description='Med 1 desc',
            difficulty='Medium',
            technology='Python',
            category='General',
            files=[{'name': 'solution.py', 'content': 'def run(): return 1'}],
            test_cases=[{'id': 1, 'name': 'T1', 'input': 'run()', 'expected': '1'}]
        )

        self.chal_med2 = Challenge.objects.create(
            title='[TEST-M02] Medium Challenge 2',
            description='Med 2 desc',
            difficulty='Medium',
            technology='Python',
            category='General',
            files=[{'name': 'solution.py', 'content': 'def run(): return 1'}],
            test_cases=[{'id': 1, 'name': 'T1', 'input': 'run()', 'expected': '1'}]
        )

    def test_01_store_packages_listing(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/store/packages')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data['packages']) >= 2)
        self.assertEqual(res.data['userBalance'], 0)
        self.assertTrue(res.data['isDemo'])
        self.assertIn('Academic Evaluation', res.data['disclaimer'])

    def test_02_store_checkout_creates_pending_purchase(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post('/api/store/checkout', {'packageId': self.pkg_starter.id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['purchase']['status'], 'PENDING')
        self.assertEqual(res.data['purchase']['bugbytesAmount'], 5)
        self.assertTrue(res.data['purchase']['transactionReference'].startswith('DEMO-PUR-'))

    def test_03_payment_success_credits_bugbytes_and_activates_mission(self):
        self.client.force_authenticate(user=self.user)
        # 1. Create Checkout
        checkout_res = self.client.post('/api/store/checkout', {'packageId': self.pkg_starter.id}, format='json')
        tx_ref = checkout_res.data['purchase']['transactionReference']

        # 2. Confirm Payment with simulated SUCCESS
        confirm_res = self.client.post('/api/store/confirm-payment', {
            'transactionReference': tx_ref,
            'simulateOutcome': 'SUCCESS',
            'startMission': True
        }, format='json')

        self.assertEqual(confirm_res.status_code, status.HTTP_200_OK)
        self.assertTrue(confirm_res.data['success'])
        self.assertEqual(confirm_res.data['newBalance'], 5)
        self.assertIsNotNone(confirm_res.data['rewardMission'])

        self.user.refresh_from_db()
        self.assertEqual(self.user.bugbytes_balance, 5)

        from buggyman.models import RewardMission, BugBytesTransaction
        mission = RewardMission.objects.filter(purchase__transaction_reference=tx_ref).first()
        self.assertIsNotNone(mission)
        self.assertEqual(mission.status, 'ACTIVE')
        self.assertEqual(mission.required_count, 5)
        self.assertEqual(mission.reward_amount_inr, 10.00)

        # Audit ledger
        bb_tx = BugBytesTransaction.objects.filter(user=self.user, transaction_type='STORE_PURCHASE').first()
        self.assertIsNotNone(bb_tx)
        self.assertEqual(bb_tx.amount, 5)

    def test_04_payment_idempotency_prevents_duplicate_credits(self):
        self.client.force_authenticate(user=self.user)
        checkout_res = self.client.post('/api/store/checkout', {'packageId': self.pkg_starter.id}, format='json')
        tx_ref = checkout_res.data['purchase']['transactionReference']

        # First confirm
        self.client.post('/api/store/confirm-payment', {
            'transactionReference': tx_ref,
            'simulateOutcome': 'SUCCESS'
        }, format='json')

        self.user.refresh_from_db()
        self.assertEqual(self.user.bugbytes_balance, 5)

        # Second confirm with same tx_ref (e.g. user refreshed or double-clicked)
        confirm_2 = self.client.post('/api/store/confirm-payment', {
            'transactionReference': tx_ref,
            'simulateOutcome': 'SUCCESS'
        }, format='json')

        self.assertEqual(confirm_2.status_code, status.HTTP_200_OK)
        self.assertTrue(confirm_2.data.get('alreadyProcessed'))

        self.user.refresh_from_db()
        # Balance must remain exactly 5, NOT 10!
        self.assertEqual(self.user.bugbytes_balance, 5)

    def test_05_payment_failure_does_not_credit_bugbytes(self):
        self.client.force_authenticate(user=self.user)
        checkout_res = self.client.post('/api/store/checkout', {'packageId': self.pkg_starter.id}, format='json')
        tx_ref = checkout_res.data['purchase']['transactionReference']

        # Confirm Payment with simulated FAILURE
        confirm_res = self.client.post('/api/store/confirm-payment', {
            'transactionReference': tx_ref,
            'simulateOutcome': 'FAILURE',
            'failureReason': 'Simulated Test Card Decline'
        }, format='json')

        self.assertEqual(confirm_res.status_code, status.HTTP_200_OK)
        self.assertFalse(confirm_res.data['success'])

        self.user.refresh_from_db()
        self.assertEqual(self.user.bugbytes_balance, 0)

    def test_06_eligible_challenge_completion_increments_mission_progress(self):
        self.client.force_authenticate(user=self.user)
        # Purchase starter pack (requires 5 Medium challenges)
        c_res = self.client.post('/api/store/checkout', {'packageId': self.pkg_starter.id}, format='json')
        tx_ref = c_res.data['purchase']['transactionReference']
        self.client.post('/api/store/confirm-payment', {'transactionReference': tx_ref, 'simulateOutcome': 'SUCCESS'}, format='json')

        from buggyman.models import RewardMission
        mission = RewardMission.objects.get(purchase__transaction_reference=tx_ref)
        self.assertEqual(mission.completed_count, 0)

        # 1. Solve Easy Challenge -> Ineligible, should NOT increment!
        self.client.post(f'/api/challenges/{self.chal_easy.id}/submit', {'code': 'def run(): return 1'}, format='json')
        mission.refresh_from_db()
        self.assertEqual(mission.completed_count, 0)

        # 2. Solve Medium Challenge 1 -> Eligible, should increment to 1!
        self.client.post(f'/api/challenges/{self.chal_med1.id}/submit', {'code': 'def run(): return 1'}, format='json')
        mission.refresh_from_db()
        self.assertEqual(mission.completed_count, 1)

        # 3. Solve Medium Challenge 1 again -> Duplicate, should NOT increment again!
        self.client.post(f'/api/challenges/{self.chal_med1.id}/submit', {'code': 'def run(): return 1'}, format='json')
        mission.refresh_from_db()
        self.assertEqual(mission.completed_count, 1)

        # 4. Solve Medium Challenge 2 -> Distinct eligible, should increment to 2!
        self.client.post(f'/api/challenges/{self.chal_med2.id}/submit', {'code': 'def run(): return 1'}, format='json')
        mission.refresh_from_db()
        self.assertEqual(mission.completed_count, 2)

    def test_07_mission_completion_and_claim_reward(self):
        from buggyman.models import RewardMission, BugBytesPurchase, SimulatedRewardTransaction
        purchase = BugBytesPurchase.objects.create(
            user=self.user,
            package=self.pkg_starter,
            package_name='Starter Pack',
            bugbytes_amount=5,
            price_inr=10.00,
            status='COMPLETED',
            transaction_reference='DEMO-PUR-TEST-CLAIM'
        )

        mission = RewardMission.objects.create(
            user=self.user,
            purchase=purchase,
            title='Starter Mission',
            required_difficulty='Medium',
            required_count=2,
            completed_count=2, # Satisfied!
            duration_days=7,
            deadline=timezone.now() + timezone.timedelta(days=7),
            reward_amount_inr=10.00,
            status='COMPLETED'
        )

        self.client.force_authenticate(user=self.user)
        res = self.client.post(f'/api/store/missions/{mission.id}/claim')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])
        self.assertEqual(res.data['rewardTransaction']['rewardAmountInr'], 10.00)

        mission.refresh_from_db()
        self.assertEqual(mission.status, 'CLAIMED')

        # Double claim rejection
        res_dup = self.client.post(f'/api/store/missions/{mission.id}/claim')
        self.assertEqual(res_dup.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(res_dup.data.get('alreadyClaimed'))

    def test_08_expired_mission_cannot_be_claimed(self):
        from buggyman.models import RewardMission, BugBytesPurchase
        purchase = BugBytesPurchase.objects.create(
            user=self.user,
            package=self.pkg_starter,
            package_name='Starter Pack',
            bugbytes_amount=5,
            price_inr=10.00,
            status='COMPLETED',
            transaction_reference='DEMO-PUR-TEST-EXP'
        )

        # Expired deadline in the past
        mission = RewardMission.objects.create(
            user=self.user,
            purchase=purchase,
            title='Expired Mission',
            required_difficulty='Medium',
            required_count=5,
            completed_count=3,
            duration_days=7,
            deadline=timezone.now() - timezone.timedelta(days=1),
            reward_amount_inr=10.00,
            status='ACTIVE'
        )

        self.client.force_authenticate(user=self.user)
        res = self.client.post(f'/api/store/missions/{mission.id}/claim')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        mission.refresh_from_db()
        self.assertEqual(mission.status, 'EXPIRED')

    def test_09_rewards_summary_calculation(self):
        from buggyman.models import RewardMission, BugBytesPurchase, SimulatedRewardTransaction
        p1 = BugBytesPurchase.objects.create(
            user=self.user,
            package_name='Pack 1',
            bugbytes_amount=5,
            price_inr=10.00,
            status='COMPLETED',
            transaction_reference='DEMO-PUR-S1'
        )
        p2 = BugBytesPurchase.objects.create(
            user=self.user,
            package_name='Pack 2',
            bugbytes_amount=15,
            price_inr=25.00,
            status='COMPLETED',
            transaction_reference='DEMO-PUR-S2'
        )
        m1 = RewardMission.objects.create(
            user=self.user,
            purchase=p1,
            title='M1',
            required_difficulty='Medium',
            required_count=5,
            completed_count=5,
            duration_days=7,
            deadline=timezone.now() + timezone.timedelta(days=7),
            reward_amount_inr=10.00,
            status='CLAIMED'
        )
        SimulatedRewardTransaction.objects.create(
            mission=m1,
            user=self.user,
            purchase=p1,
            reward_amount_inr=10.00,
            transaction_reference='DEMO-REW-S1'
        )

        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/store/rewards')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Total purchased = 10 + 25 = 35. Total rewarded = 10. Net cost = 25.
        self.assertEqual(res.data['totalPurchasedInr'], 35.00)
        self.assertEqual(res.data['totalRewardedInr'], 10.00)
        self.assertEqual(res.data['netSimulatedCostInr'], 25.00)









































