"""
BuggyMan Security & Anti-Leakage Test Suite
Validates that:
1. Challenge serialization (to_dict / DRF Serializer) NEVER leaks:
   - bugSignature
   - aiSuggestions
   - Hidden test case inputs, expected values, or assertions
   - Solution-specific SQL clauses or code syntax
2. EvaluationEngine and runtime adapters NEVER leak:
   - Expected SQL result tables
   - Internal test assertions
   - Solution conditions in actual/error fields
3. Test case results return clean format:
   - 'Test Case 1', 'Test Case 2'
   - Total passed / total tests
   - Non-revealing debugging hints on failure
4. Both passing and failing runs across all 3 arenas behave properly.
"""

import os
import sys
import unittest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from buggyman.models import Challenge
from buggyman.evaluator.engine import EvaluationEngine
from buggyman.serializers import ChallengeSerializer
from buggyman.data.solutions_120 import get_all_120_solutions


class TestLeakageAndSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = EvaluationEngine()
        cls.solutions = get_all_120_solutions()

    def test_challenge_to_dict_no_bug_signature(self):
        """to_dict() must never expose bugSignature or aiSuggestions to clients."""
        for cid in [1, 51, 86]:
            challenge = Challenge.objects.get(id=cid)
            data = challenge.to_dict()
            self.assertEqual(data.get('bugSignature'), '', f"Challenge {cid} leaked bugSignature")
            self.assertEqual(data.get('bug_signature'), '', f"Challenge {cid} leaked bug_signature")
            self.assertEqual(data.get('aiSuggestions'), [], f"Challenge {cid} leaked aiSuggestions")
            self.assertEqual(data.get('ai_suggestions'), [], f"Challenge {cid} leaked ai_suggestions")

    def test_challenge_to_dict_hides_hidden_tests(self):
        """to_dict() must completely strip hidden tests from client testCases."""
        for cid in [1, 51, 86]:
            challenge = Challenge.objects.get(id=cid)
            data = challenge.to_dict()
            client_cases = data.get('testCases', [])
            
            # Client cases should only have visible tests
            for tc in client_cases:
                self.assertFalse(tc.get('hidden', False), f"Challenge {cid} leaked hidden test in to_dict: {tc}")
                # Ensure generic non-revealing expected description
                expected = tc.get('expected', '')
                self.assertNotIn('opt_out', expected)
                self.assertNotIn('SELECT', expected)
                self.assertNotIn('WHERE', expected)

    def test_challenge_serializer_no_leakage(self):
        """DRF ChallengeSerializer must serialize without leaking secrets."""
        for cid in [1, 51, 86]:
            challenge = Challenge.objects.get(id=cid)
            serializer = ChallengeSerializer(challenge)
            data = serializer.data
            self.assertEqual(data.get('bugSignature'), '')
            self.assertEqual(data.get('aiSuggestions'), [])
            for tc in data.get('testCases', []):
                self.assertFalse(tc.get('hidden', False))

    def test_evaluator_results_sanitization(self):
        """EvaluationEngine.evaluate() must never send expected or actual solutions."""
        # Test on SQL challenge 51 (WHERE clause bug)
        challenge = Challenge.objects.get(id=51)
        # Run buggy starter code
        res = self.engine.evaluate(challenge, files=challenge.files)
        self.assertFalse(res['success'])
        
        test_results = res['test_results']
        self.assertGreater(len(test_results), 0)
        for tr in test_results:
            self.assertIn('Test Case', tr['name'])
            self.assertIsNone(tr['expected'], "Evaluator leaked expected output table/assertion")
            self.assertIsNone(tr['actual'], "Evaluator leaked actual internal output")
            if tr['hidden']:
                self.assertEqual(tr['input'], '', "Evaluator leaked hidden test input")

    def test_evaluator_sql_failure_hints_non_revealing(self):
        """SQL test failures must provide concise debugging hints without leaking tables or answers."""
        challenge = Challenge.objects.get(id=51)
        res = self.engine.evaluate(challenge, files=challenge.files)
        
        for tr in res['test_results']:
            if not tr['passed']:
                err = tr.get('error') or tr.get('hint') or ''
                self.assertNotIn('+---', err, "ASCII table leaked in failure error/hint")
                self.assertNotIn('opt_out = 0', err, "Solution condition leaked in failure hint")
                self.assertTrue("null" in err.lower() or "filter" in err.lower(), f"Unexpected hint: {err}")

    def test_correct_solution_passes_cleanly(self):
        """Valid reference solution must still pass all tests cleanly."""
        for cid in [1, 51, 86]:
            challenge = Challenge.objects.get(id=cid)
            sol_files = self.solutions.get(cid)
            self.assertIsNotNone(sol_files, f"No reference solution for challenge {cid}")
            res = self.engine.evaluate(challenge, files=sol_files)
            self.assertTrue(res['success'], f"Reference solution for challenge {cid} failed to pass")
            self.assertEqual(res['tests_passed'], res['tests_total'])


if __name__ == '__main__':
    unittest.main()
