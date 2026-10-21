import os
import sys
import unittest
import json
import sqlite3

# Set up Django environment so we can import models and evaluator directly
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

import django
django.setup()

from buggyman.evaluator.engine import EvaluationEngine
from buggyman.models import Challenge, User


class EvaluatorDeepDiveTest(unittest.TestCase):
    """
    Phase 4: Critical Debugging and Evaluation Tests
    Verifies that correct submissions pass and incorrect/syntax/logic/edge-case
    submissions fail across Code, SQL, and Frontend arenas.
    """

    @classmethod
    def setUpClass(cls):
        cls.engine = EvaluationEngine()

    # =========================================================================
    # ARENA 1: CODE CHALLENGES (Python & JavaScript / Backend)
    # =========================================================================

    def test_01_code_challenge_known_correct_submission_passes(self):
        """Verify known-correct Python code passes all test cases with 100% score."""
        challenge = {
            "title": "API Pagination Boundary Bug",
            "technology": "Python",
            "points": 100,
            "bug_signature": "return items[start:end]",
            "test_cases": [
                {"id": 1, "name": "Basic Pagination", "input": "paginate([1,2,3,4,5], page=1, page_size=2)", "expected": "[1, 2]", "hidden": False},
                {"id": 2, "name": "Last Page Partial", "input": "paginate([1,2,3,4,5], page=3, page_size=2)", "expected": "[5]", "hidden": False},
                {"id": 3, "name": "Page Beyond Range Edge Case", "input": "paginate([1,2,3], page=5, page_size=2)", "expected": "[]", "hidden": True}
            ]
        }

        correct_code = """
def paginate(items, page, page_size):
    if page < 1 or page_size < 1:
        return []
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    return items[start_idx:end_idx]
"""
        result = self.engine.evaluate(challenge, code=correct_code)

        self.assertTrue(result["success"], "Known correct code must pass")
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["tests_passed"], 3)
        self.assertEqual(result["tests_total"], 3)
        self.assertFalse(result["bug_signature_detected"])

    def test_02_code_challenge_syntax_error_fails(self):
        """Verify code containing syntax errors fails and produces informative error."""
        challenge = {
            "title": "Syntax Error Test",
            "technology": "Python",
            "points": 100,
            "test_cases": [
                {"id": 1, "name": "Syntax Test", "input": "foo()", "expected": "1", "hidden": False}
            ]
        }

        broken_syntax_code = """
def foo(
    return 1 # missing closing parenthesis and invalid syntax
"""
        result = self.engine.evaluate(challenge, code=broken_syntax_code)

        self.assertFalse(result["success"], "Syntax error must NOT pass")
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["tests_passed"], 0)
        # Check that error is captured
        has_error = result.get("error") is not None or any(t.get("error") for t in result["test_results"])
        self.assertTrue(has_error, "Error details must be present")

    def test_03_code_challenge_incorrect_logic_fails(self):
        """Verify code with wrong business logic fails test assertions."""
        challenge = {
            "title": "Reverse Words Logic",
            "technology": "Python",
            "points": 100,
            "test_cases": [
                {"id": 1, "name": "Reverse Sentence", "input": "reverse_words('hello world')", "expected": "'world hello'", "hidden": False}
            ]
        }

        wrong_logic_code = """
def reverse_words(s):
    # Inverted logic: reversing characters instead of words
    return s[::-1]
"""
        result = self.engine.evaluate(challenge, code=wrong_logic_code)

        self.assertFalse(result["success"], "Incorrect logic must fail")
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["tests_passed"], 0)

    def test_04_code_challenge_passes_sample_fails_hidden_edge_case(self):
        """Verify code that handles samples but fails edge case is rejected."""
        challenge = {
            "title": "Division Safeguard",
            "technology": "Python",
            "points": 100,
            "test_cases": [
                {"id": 1, "name": "Standard Division", "input": "safe_divide(10, 2)", "expected": "5.0", "hidden": False},
                {"id": 2, "name": "Hidden Zero Division Edge Case", "input": "safe_divide(10, 0)", "expected": "None", "hidden": True}
            ]
        }

        naive_code = """
def safe_divide(a, b):
    # Fails when b is 0
    return float(a / b)
"""
        result = self.engine.evaluate(challenge, code=naive_code)

        self.assertFalse(result["success"], "Failing edge cases must reject submission")
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["tests_passed"], 1)
        self.assertEqual(result["tests_total"], 2)

    def test_05_code_challenge_unaltered_bug_signature_rejected(self):
        """Verify submitting code retaining original bug signature is rejected."""
        challenge = {
            "title": "Signature Anti-Cheat Test",
            "technology": "Python",
            "points": 100,
            "bug_signature": "CRITICAL_BUG_TOKEN_999",
            "test_cases": [
                {"id": 1, "name": "Stub Test", "input": "check()", "expected": "True", "hidden": False}
            ]
        }

        cheated_code = """
# CRITICAL_BUG_TOKEN_999
def check():
    return True
"""
        result = self.engine.evaluate(challenge, code=cheated_code)

        self.assertFalse(result["success"], "Unaltered bug signature must be flagged and rejected")
        self.assertTrue(result["bug_signature_detected"])

    # =========================================================================
    # ARENA 2: SQL LAB
    # =========================================================================

    def test_06_sql_lab_known_correct_query_passes(self):
        """Verify known-correct SQL query against schema produces matching rows."""
        challenge = {
            "title": "Active Employees Report",
            "technology": "SQL",
            "points": 100,
            "expected_query": "SELECT name, salary FROM employees WHERE status = 'active' ORDER BY salary DESC;",
            "ordered_comparison": True,
            "files": [
                {
                    "name": "schema.sql",
                    "content": """
                    CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, salary INTEGER, status TEXT);
                    INSERT INTO employees VALUES (1, 'Alice', 90000, 'active');
                    INSERT INTO employees VALUES (2, 'Bob', 80000, 'inactive');
                    INSERT INTO employees VALUES (3, 'Charlie', 95000, 'active');
                    """
                }
            ],
            "test_cases": [
                {"id": 1, "name": "Returns active employees ordered by salary DESC", "hidden": False}
            ]
        }

        correct_sql = "SELECT name, salary FROM employees WHERE status = 'active' ORDER BY salary DESC;"
        result = self.engine.evaluate(challenge, code=correct_sql)

        self.assertTrue(result["success"], "Valid SQL query must pass")
        self.assertEqual(result["tests_passed"], 1)
        self.assertIn("Charlie", result["stdout"])

    def test_07_sql_lab_missing_filter_fails(self):
        """Verify SQL query omitting WHERE condition returns incorrect rows and fails."""
        challenge = {
            "title": "Active Employees Filter Test",
            "technology": "SQL",
            "points": 100,
            "expected_query": "SELECT name FROM employees WHERE status = 'active';",
            "files": [
                {
                    "name": "schema.sql",
                    "content": """
                    CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, status TEXT);
                    INSERT INTO employees VALUES (1, 'Alice', 'active');
                    INSERT INTO employees VALUES (2, 'Bob', 'inactive');
                    """
                }
            ],
            "test_cases": [
                {"id": 1, "name": "Filters by active status", "hidden": False}
            ]
        }

        # Omits WHERE status = 'active'
        wrong_sql = "SELECT name FROM employees;"
        result = self.engine.evaluate(challenge, code=wrong_sql)

        self.assertFalse(result["success"], "Unfiltered query must fail")
        self.assertEqual(result["tests_passed"], 0)

    def test_08_sql_lab_null_handling_edge_case(self):
        """Verify SQL query failing to account for NULL handling is rejected."""
        challenge = {
            "title": "High Earners Excluding Bonus",
            "technology": "SQL",
            "points": 100,
            "expected_query": "SELECT name FROM sales WHERE COALESCE(bonus, 0) > 500;",
            "files": [
                {
                    "name": "schema.sql",
                    "content": """
                    CREATE TABLE sales (id INTEGER PRIMARY KEY, name TEXT, bonus INTEGER);
                    INSERT INTO sales VALUES (1, 'Alice', 1000);
                    INSERT INTO sales VALUES (2, 'Bob', NULL);
                    INSERT INTO sales VALUES (3, 'Charlie', 200);
                    """
                }
            ],
            "test_cases": [
                {"id": 1, "name": "Handles NULL bonus correctly", "hidden": False}
            ]
        }

        # Incorrect query fails on NULL comparison
        failing_sql = "SELECT name FROM sales WHERE bonus > 500 OR bonus IS NULL;"
        result = self.engine.evaluate(challenge, code=failing_sql)

        self.assertFalse(result["success"], "Incorrect NULL handling query must fail")

    def test_09_sql_lab_syntax_error_fails(self):
        """Verify malformed SQL statements fail gracefully with operational error."""
        challenge = {
            "title": "SQL Syntax Test",
            "technology": "SQL",
            "points": 100,
            "expected_query": "SELECT 1;",
            "files": [],
            "test_cases": [{"id": 1, "name": "Basic SQL", "hidden": False}]
        }

        broken_sql = "SELEKT * FORM non_existent_table WHERE ;"
        result = self.engine.evaluate(challenge, code=broken_sql)

        self.assertFalse(result["success"])
        self.assertEqual(result["score"], 0)

    # =========================================================================
    # ARENA 3: FRONTEND STUDIO (CSS / HTML / React Static Code)
    # =========================================================================

    def test_10_frontend_studio_correct_styling_passes(self):
        """Verify correct CSS flexbox centering implementation passes."""
        challenge = {
            "title": "Center Hero Card Layout",
            "technology": "CSS",
            "points": 100,
            "test_cases": [
                {"id": 1, "name": "Display flexbox applied", "expected": "display: flex", "hidden": False},
                {"id": 2, "name": "Centered horizontally", "expected": "justify-content: center", "hidden": False},
                {"id": 3, "name": "Centered vertically", "expected": "align-items: center", "hidden": True}
            ]
        }

        correct_css = """
.hero-card {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}
"""
        result = self.engine.evaluate(challenge, code=correct_css)

        self.assertTrue(result["success"], "Valid CSS must pass all 3 tests")
        self.assertEqual(result["tests_passed"], 3)
        self.assertEqual(result["score"], 100)

    def test_11_frontend_studio_missing_property_fails(self):
        """Verify CSS missing critical layout rule fails."""
        challenge = {
            "title": "Center Hero Card Layout",
            "technology": "CSS",
            "points": 100,
            "test_cases": [
                {"id": 1, "name": "Display flexbox applied", "expected": "display: flex", "hidden": False},
                {"id": 2, "name": "Centered vertically", "expected": "align-items: center", "hidden": False}
            ]
        }

        incomplete_css = """
.hero-card {
    display: flex;
    /* Missing align-items: center */
    padding: 20px;
}
"""
        result = self.engine.evaluate(challenge, code=incomplete_css)

        self.assertFalse(result["success"], "Incomplete CSS must fail")
        self.assertEqual(result["tests_passed"], 1)
        self.assertEqual(result["tests_total"], 2)
        self.assertEqual(result["score"], 0)

    def test_12_frontend_studio_empty_code_fails(self):
        """Verify submitting empty code is rejected immediately."""
        challenge = {
            "title": "Empty Submission Check",
            "technology": "CSS",
            "points": 100,
            "test_cases": [
                {"id": 1, "name": "Rule Check", "expected": "display: grid", "hidden": False}
            ]
        }

        result = self.engine.evaluate(challenge, code="")

        self.assertFalse(result["success"])
        self.assertEqual(result["score"], 0)


if __name__ == "__main__":
    unittest.main()
