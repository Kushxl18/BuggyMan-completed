"""
BuggyMan Regression Test Suite: Evaluator Strictness & False Positive Prevention
Validates that:
1. Buggy starter code fails appropriate tests across all 3 arenas.
2. Correct reference implementations pass.
3. Intentionally wrong code (e.g. constant return, SELECT 1;, empty code) fails.
4. Syntax errors & runtime exceptions fail cleanly with detailed error messages.
5. Empty test suites are never treated as successful.
6. Bug signature presence blocks passing even if outputs look clean.
"""

import os
import sys
import unittest

# Configure Django environment
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from buggyman.models import Challenge
from buggyman.evaluator.engine import EvaluationEngine
from buggyman.data.solutions_120 import get_all_120_solutions


class TestEvaluatorStrictness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = EvaluationEngine()
        cls.solutions = get_all_120_solutions()

    def test_starter_code_fails_code_arena(self):
        """Buggy starter code in Code Arena MUST fail evaluation."""
        sample_ids = [1, 5, 10, 18, 25, 36, 42, 50]
        for cid in sample_ids:
            challenge = Challenge.objects.get(id=cid)
            result = self.engine.evaluate(challenge, files=challenge.files)
            self.assertFalse(
                result['success'],
                f"Challenge {cid} ('{challenge.title}') starter code falsely PASSED!"
            )
            self.assertGreater(
                result['tests_total'],
                result['tests_passed'],
                f"Challenge {cid} reported all tests passed on untouched starter code."
            )

    def test_starter_code_fails_sql_lab(self):
        """Buggy starter code in SQL Lab MUST fail evaluation."""
        sample_ids = [51, 55, 60, 65, 70, 75, 80, 85]
        for cid in sample_ids:
            challenge = Challenge.objects.get(id=cid)
            result = self.engine.evaluate(challenge, files=challenge.files)
            self.assertFalse(
                result['success'],
                f"SQL Challenge {cid} ('{challenge.title}') starter code falsely PASSED!"
            )

    def test_starter_code_fails_frontend_studio(self):
        """Buggy starter code in Frontend Studio MUST fail evaluation."""
        sample_ids = [86, 90, 95, 100, 105, 110, 115, 120]
        for cid in sample_ids:
            challenge = Challenge.objects.get(id=cid)
            result = self.engine.evaluate(challenge, files=challenge.files)
            self.assertFalse(
                result['success'],
                f"Frontend Challenge {cid} ('{challenge.title}') starter code falsely PASSED!"
            )

    def test_reference_solutions_pass(self):
        """Verified reference implementations MUST pass all test cases."""
        sample_ids = [1, 10, 18, 25, 42, 51, 60, 70, 80, 86, 95, 105, 120]
        for cid in sample_ids:
            challenge = Challenge.objects.get(id=cid)
            sol_files = self.solutions.get(cid)
            self.assertIsNotNone(sol_files, f"Missing reference solution for Challenge {cid}")
            result = self.engine.evaluate(challenge, files=sol_files)
            self.assertTrue(
                result['success'],
                f"Reference solution for Challenge {cid} ('{challenge.title}') failed! "
                f"Errors: {result.get('error')}, Tests: {result.get('test_results')}"
            )
            self.assertEqual(result['tests_passed'], result['tests_total'])

    def test_sql_dummy_queries_fail(self):
        """Submitting dummy SQL like SELECT 1; MUST NOT pass any SQL challenge."""
        sql_challenges = Challenge.objects.filter(id__gte=51, id__lte=85)[:10]
        for c in sql_challenges:
            result = self.engine.evaluate(c, code="SELECT 1;")
            self.assertFalse(
                result['success'],
                f"SQL Challenge {c.id} ('{c.title}') falsely passed 'SELECT 1;'!"
            )
            self.assertEqual(result['score'], 0)

    def test_python_dummy_functions_fail(self):
        """Submitting dummy code like def dummy(): return None MUST fail Code Arena."""
        code_challenges = Challenge.objects.filter(id__gte=1, id__lte=50)[:10]
        for c in code_challenges:
            result = self.engine.evaluate(c, code="def dummy(): return None")
            self.assertFalse(
                result['success'],
                f"Code Challenge {c.id} ('{c.title}') falsely passed dummy function!"
            )
            self.assertEqual(result['score'], 0)

    def test_frontend_dummy_components_fail(self):
        """Submitting dummy component MUST fail Frontend Studio."""
        fe_challenges = Challenge.objects.filter(id__gte=86, id__lte=120)[:10]
        for c in fe_challenges:
            result = self.engine.evaluate(c, code="export default function Dummy() { return null; }")
            self.assertFalse(
                result['success'],
                f"Frontend Challenge {c.id} ('{c.title}') falsely passed dummy component!"
            )
            self.assertEqual(result['score'], 0)

    def test_syntax_errors_fail_cleanly(self):
        """Syntax errors must produce exit_code=1, success=False, and clear error output."""
        c1 = Challenge.objects.get(id=1)
        res_py = self.engine.evaluate(c1, code="def broken_syntax(:\n  return")
        self.assertFalse(res_py['success'])
        self.assertIn("SyntaxError", (res_py.get('stderr') or '') + (res_py.get('error') or '') + str(res_py.get('test_results')))

        c51 = Challenge.objects.get(id=51)
        res_sql = self.engine.evaluate(c51, code="SELEC * FORM invalid table;;;")
        self.assertFalse(res_sql['success'])
        self.assertIn("SQLite Error", (res_sql.get('stderr') or '') + (res_sql.get('error') or '') + str(res_sql.get('test_results')))

    def test_empty_test_suite_rejected(self):
        """A challenge with zero test cases must NOT be marked successful."""
        mock_challenge = {
            'id': 9999,
            'title': 'Empty Tests Mock',
            'technology': 'Python',
            'test_cases': [],
            'files': [{'name': 'main.py', 'content': 'x = 1'}],
            'bug_signature': ''
        }
        res = self.engine.evaluate(mock_challenge, code="x = 1")
        self.assertFalse(res['success'], "Challenge with 0 test cases must not succeed.")
        self.assertEqual(res['score'], 0)

    def test_bug_signature_blocks_success(self):
        """If user code contains the intentional bug signature, it must fail."""
        c1 = Challenge.objects.get(id=1)
        # Modify code to pass logical conditions but keep the exact buggy line
        buggy_code = c1.files[0]['content']
        res = self.engine.evaluate(c1, code=buggy_code)
        self.assertFalse(res['success'])
        self.assertTrue(res['bug_signature_detected'])


if __name__ == '__main__':
    unittest.main()
