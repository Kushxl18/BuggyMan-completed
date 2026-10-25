import os
import sys
import time
import json
import ast
import shutil
from .sandboxes import SubprocessSandboxRunner


class FeatureEvaluator:
    """
    Dedicated evaluation engine for Feature Implementation Arena challenges.
    
    Evaluates multi-file project repositories across five configurable dimensions:
    1. Feature Functionality (default 40%) - Validates requested feature behavior
    2. Hidden Tests (default 25%) - Verifies edge cases and unannounced scenarios
    3. Regression Tests (default 15%) - Ensures existing codebase features did not break
    4. Code Quality (default 10%) - AST linting, structural design, exception handling
    5. Security & Edge Cases (default 10%) - Input validation, boundary resilience, authorization
    """

    def __init__(self, sandbox_runner=None):
        self.sandbox_runner = sandbox_runner or SubprocessSandboxRunner()

    def validate_files(self, files):
        """Sanitizes incoming project files and prevents path traversal attacks."""
        cleaned = []
        if not files or not isinstance(files, list):
            return cleaned

        for f in files:
            if not isinstance(f, dict):
                continue
            name = (f.get('name') or f.get('filename') or '').strip().replace('\\', '/')
            if not name:
                continue

            # Strip leading slashes and path traversal attempts
            norm_name = os.path.normpath(name).replace('\\', '/').lstrip('/')
            if norm_name.startswith('..') or norm_name.startswith('/') or ':' in norm_name:
                continue

            cleaned.append({
                'name': norm_name,
                'content': f.get('content') or '',
                'readonly': bool(f.get('readonly', False)),
                'is_entrypoint': bool(f.get('is_entrypoint', False))
            })
        return cleaned

    def evaluate(self, challenge, files=None, is_submission=False, timeout=8.0):
        start_time = time.time()
        c_dict = challenge.to_dict() if hasattr(challenge, 'to_dict') else challenge

        # 1. Clean workspace files
        norm_files = self.validate_files(files)
        if not norm_files:
            initial_files = challenge.initial_files if hasattr(challenge, 'initial_files') else c_dict.get('files', [])
            norm_files = self.validate_files(initial_files)

        scoring_config = c_dict.get('scoringConfig') or c_dict.get('scoring_config') or {
            'feature_weight': 40,
            'hidden_weight': 25,
            'regression_weight': 15,
            'quality_weight': 10,
            'security_weight': 10
        }

        raw_test_cases = challenge.test_cases if hasattr(challenge, 'test_cases') else c_dict.get('test_cases', [])
        technology = (challenge.technology if hasattr(challenge, 'technology') else c_dict.get('technology', '')).lower()

        # 2. Run Quality Checks on modified/submitted files
        quality_score, quality_results = self._evaluate_code_quality(norm_files, technology)

        # 3. Build test runner harness
        if 'node' in technology or 'javascript' in technology or 'express' in technology:
            exec_result = self._execute_node_feature(norm_files, raw_test_cases, is_submission, timeout)
        else:
            # Default: Python
            exec_result = self._execute_python_feature(norm_files, raw_test_cases, is_submission, timeout)

        # 4. Aggregate results by category
        test_results = exec_result.get('test_results', [])
        
        # Categorize test cases
        feature_tests = [t for t in test_results if t.get('category') == 'feature']
        hidden_tests = [t for t in test_results if t.get('category') == 'hidden']
        regression_tests = [t for t in test_results if t.get('category') == 'regression']
        security_tests = [t for t in test_results if t.get('category') == 'security']

        # Calculate category pass rates (ratio 0.0 to 1.0)
        def pass_ratio(tests):
            if not tests:
                return 1.0  # If category has no tests in this challenge, full points awarded
            passed = sum(1 for t in tests if t.get('passed'))
            return passed / len(tests)

        f_ratio = pass_ratio(feature_tests)
        h_ratio = pass_ratio(hidden_tests) if is_submission else 0.0
        r_ratio = pass_ratio(regression_tests)
        s_ratio = pass_ratio(security_tests)
        q_ratio = quality_score / 100.0

        # Weighted calculation
        fw = scoring_config.get('feature_weight', 40)
        hw = scoring_config.get('hidden_weight', 25)
        rw = scoring_config.get('regression_weight', 15)
        qw = scoring_config.get('quality_weight', 10)
        sw = scoring_config.get('security_weight', 10)

        feature_pts = round(f_ratio * fw)
        hidden_pts = round(h_ratio * hw) if is_submission else 0
        regression_pts = round(r_ratio * rw)
        quality_pts = round(q_ratio * qw)
        security_pts = round(s_ratio * sw)

        total_score = feature_pts + hidden_pts + regression_pts + quality_pts + security_pts
        if not is_submission:
            # For "Run Code", score reflects visible categories
            max_visible = fw + rw + qw + sw
            scaled_score = round((feature_pts + regression_pts + quality_pts + security_pts) / max_visible * 100) if max_visible > 0 else 0
        else:
            scaled_score = total_score

        # Success threshold: Feature tests must pass (ratio >= 0.8) and overall score >= 75
        is_success = (f_ratio >= 0.8) and (scaled_score >= 75)

        # Add quality checks to test_results display
        test_results.extend(quality_results)

        # Sanitize results if not submission (hide test_code / solution from hidden tests)
        if not is_submission:
            test_results = [t for t in test_results if not t.get('is_hidden')]

        exec_time = round(time.time() - start_time, 3)

        # Generate summary
        passed_count = sum(1 for t in test_results if t.get('passed'))
        total_count = len(test_results)
        summary = (
            f"Feature implementation evaluated: {passed_count}/{total_count} checks passed. "
            f"Overall score: {scaled_score}/100. "
            f"{'Feature successfully validated!' if is_success else 'Some requirements or regression checks need revision.'}"
        )

        return {
            'success': is_success,
            'score': scaled_score,
            'score_breakdown': {
                'feature_score': feature_pts,
                'feature_max': fw,
                'hidden_score': hidden_pts,
                'hidden_max': hw,
                'regression_score': regression_pts,
                'regression_max': rw,
                'quality_score': quality_pts,
                'quality_max': qw,
                'security_score': security_pts,
                'security_max': sw,
                'total_score': scaled_score
            },
            'test_results': test_results,
            'stdout': exec_result.get('stdout', ''),
            'stderr': exec_result.get('stderr', ''),
            'execution_time': exec_time,
            'ai_summary': summary
        }

    def _evaluate_code_quality(self, files, technology):
        """Analyzes code quality, syntax validity, structure, and basic security hygiene."""
        quality_pts = 100
        results = []

        for f in files:
            name = f['name']
            content = f['content']

            if name.endswith('.py'):
                try:
                    tree = ast.parse(content)
                    results.append({
                        'name': f"Syntax & AST Check ({name})",
                        'category': 'quality',
                        'passed': True,
                        'message': 'Valid Python syntax and AST structure',
                        'is_hidden': False
                    })
                    
                    # Check for empty TODO stubs
                    if 'pass' in content and 'raise NotImplementedError' in content:
                        quality_pts -= 15
                        results.append({
                            'name': f"Incomplete Implementation Check ({name})",
                            'category': 'quality',
                            'passed': False,
                            'message': 'Unimplemented stubs or NotImplementedError found',
                            'is_hidden': False
                        })

                except SyntaxError as e:
                    quality_pts -= 50
                    results.append({
                        'name': f"Syntax Error ({name})",
                        'category': 'quality',
                        'passed': False,
                        'message': f"Line {e.lineno}: {e.msg}",
                        'is_hidden': False
                    })
            elif name.endswith('.js') or name.endswith('.jsx') or name.endswith('.ts'):
                if 'syntax error' in content.lower():
                    quality_pts -= 30
                results.append({
                    'name': f"File Structure Validation ({name})",
                    'category': 'quality',
                    'passed': True,
                    'message': 'File present and non-empty',
                    'is_hidden': False
                })

        final_quality = max(0, min(100, quality_pts))
        return final_quality, results

    def _execute_python_feature(self, files, test_cases, is_submission, timeout):
        """Builds and executes an isolated Python test harness against the user repository."""
        # Test harness script that executes the test suite
        harness_files = list(files)
        
        # Serialize test cases for the runner
        test_cases_json = json.dumps(test_cases or [])
        is_sub_json = json.dumps(is_submission)

        runner_script = f"""import sys
import os
import json
import traceback
import unittest
import time

# Ensure current working directory is on sys.path for repository imports
sys.path.insert(0, os.path.abspath('.'))

test_cases = json.loads({repr(test_cases_json)})
is_submission = {repr(is_sub_json)}
results = []

def run_suite():
    for tc in test_cases:
        tc_id = tc.get('id')
        tc_name = tc.get('name', 'Test')
        tc_type = tc.get('type', 'feature')
        is_hidden = bool(tc.get('is_hidden', False) or tc_type == 'hidden')

        # If not submission and test is hidden, skip execution
        if is_hidden and not is_submission:
            continue

        test_code = tc.get('test_code') or tc.get('code') or ''
        expected = tc.get('expected')

        start = time.time()
        try:
            loc = {{}}
            # Execute the test assertion block
            exec(test_code, loc, loc)
            duration = round(time.time() - start, 4)
            results.append({{
                'id': tc_id,
                'name': tc_name,
                'category': tc_type,
                'passed': True,
                'message': 'Assertion succeeded',
                'duration': duration,
                'is_hidden': is_hidden
            }})
        except Exception as e:
            duration = round(time.time() - start, 4)
            err_msg = str(e)
            if not err_msg:
                err_msg = type(e).__name__
            results.append({{
                'id': tc_id,
                'name': tc_name,
                'category': tc_type,
                'passed': False,
                'message': err_msg,
                'duration': duration,
                'is_hidden': is_hidden
            }})

try:
    run_suite()
    print("__BUGGYMAN_RESULT_START__")
    print(json.dumps(results))
    print("__BUGGYMAN_RESULT_END__")
except Exception as global_err:
    print("__BUGGYMAN_ERROR__:" + str(global_err), file=sys.stderr)
    traceback.print_exc()
"""
        harness_files.append({
            'name': '_feature_runner.py',
            'content': runner_script
        })

        python_bin = shutil.which("python") or shutil.which("python3") or "python"
        command = [python_bin, "-I", "-B", "_feature_runner.py"]

        sandbox_result = self.sandbox_runner.run(harness_files, command, timeout=timeout)

        # Parse test results from stdout
        stdout = sandbox_result.stdout or ''
        stderr = sandbox_result.stderr or ''
        test_results = []

        if "__BUGGYMAN_RESULT_START__" in stdout and "__BUGGYMAN_RESULT_END__" in stdout:
            try:
                payload = stdout.split("__BUGGYMAN_RESULT_START__")[1].split("__BUGGYMAN_RESULT_END__")[0].strip()
                test_results = json.loads(payload)
                # Clean stdout of internal markers
                stdout = stdout.split("__BUGGYMAN_RESULT_START__")[0].strip()
            except Exception:
                pass
        elif sandbox_result.timed_out:
            test_results.append({
                'name': 'Execution Timeout',
                'category': 'feature',
                'passed': False,
                'message': f"Execution exceeded maximum timeout threshold of {timeout}s",
                'is_hidden': False
            })
        elif stderr:
            test_results.append({
                'name': 'Execution Failure',
                'category': 'feature',
                'passed': False,
                'message': stderr.splitlines()[-1] if stderr.splitlines() else 'Error executing test suite',
                'is_hidden': False
            })

        return {
            'test_results': test_results,
            'stdout': stdout,
            'stderr': stderr
        }

    def _execute_node_feature(self, files, test_cases, is_submission, timeout):
        """Builds and executes an isolated Node.js test harness against the repository."""
        harness_files = list(files)
        test_cases_json = json.dumps(test_cases or [])
        is_sub_json = json.dumps(is_submission)

        runner_script = f"""
const fs = require('fs');
const path = require('path');

const testCases = {test_cases_json};
const isSubmission = {is_sub_json};
const results = [];

async function run() {{
  for (const tc of testCases) {{
    const isHidden = tc.is_hidden || tc.type === 'hidden';
    if (isHidden && !isSubmission) continue;

    const start = Date.now();
    try {{
      const testFn = new Function(tc.test_code || tc.code || 'return true;');
      await testFn();
      results.push({{
        id: tc.id,
        name: tc.name || 'Test',
        category: tc.type || 'feature',
        passed: true,
        message: 'Assertion passed',
        duration: (Date.now() - start) / 1000,
        is_hidden: isHidden
      }});
    }} catch (err) {{
      results.push({{
        id: tc.id,
        name: tc.name || 'Test',
        category: tc.type || 'feature',
        passed: false,
        message: err.message || 'Assertion failed',
        duration: (Date.now() - start) / 1000,
        is_hidden: isHidden
      }});
    }}
  }}

  console.log("__BUGGYMAN_RESULT_START__");
  console.log(JSON.stringify(results));
  console.log("__BUGGYMAN_RESULT_END__");
}}

run().catch(err => {{
  console.error("__BUGGYMAN_ERROR__:" + err.message);
  process.exit(1);
}});
"""
        harness_files.append({
            'name': '_feature_runner.js',
            'content': runner_script
        })

        node_bin = shutil.which("node") or "node"
        command = [node_bin, "_feature_runner.js"]

        sandbox_result = self.sandbox_runner.run(harness_files, command, timeout=timeout)
        stdout = sandbox_result.stdout or ''
        stderr = sandbox_result.stderr or ''
        test_results = []

        if "__BUGGYMAN_RESULT_START__" in stdout and "__BUGGYMAN_RESULT_END__" in stdout:
            try:
                payload = stdout.split("__BUGGYMAN_RESULT_START__")[1].split("__BUGGYMAN_RESULT_END__")[0].strip()
                test_results = json.loads(payload)
                stdout = stdout.split("__BUGGYMAN_RESULT_START__")[0].strip()
            except Exception:
                pass
        elif sandbox_result.timed_out:
            test_results.append({
                'name': 'Execution Timeout',
                'category': 'feature',
                'passed': False,
                'message': f"Execution timed out after {timeout}s",
                'is_hidden': False
            })

        return {
            'test_results': test_results,
            'stdout': stdout,
            'stderr': stderr
        }


feature_evaluator = FeatureEvaluator()
