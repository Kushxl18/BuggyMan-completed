import os
import time
from .sandboxes import SubprocessSandboxRunner
from .runtimes import (
    PythonRuntimeAdapter,
    NodeRuntimeAdapter,
    StaticCodeRuntimeAdapter,
    SQLRuntimeAdapter,
    UnsupportedRuntimeAdapter
)


class EvaluationEngine:
    """
    Central Evaluation Engine for BuggyMan challenges.
    
    Architecture Flow:
    User Workspace -> Files -> Validation -> Runtime Resolution -> Isolated Sandbox -> Test Execution -> Output Capture -> Result Formatting & Backend Scoring
    """

    def __init__(self, sandbox_runner=None):
        self.sandbox_runner = sandbox_runner or SubprocessSandboxRunner()
        self.python_adapter = PythonRuntimeAdapter(self.sandbox_runner)
        self.node_adapter = NodeRuntimeAdapter(self.sandbox_runner)
        self.static_adapter = StaticCodeRuntimeAdapter(self.sandbox_runner)
        self.sql_adapter = SQLRuntimeAdapter(self.sandbox_runner)
        self.unsupported_adapter = UnsupportedRuntimeAdapter(self.sandbox_runner)

    def resolve_adapter(self, technology, files):
        tech_lower = (technology or '').lower().strip()
        
        # 1. Match explicit technology names
        if tech_lower in ['python', 'django', 'backend', 'fastapi', 'flask']:
            return self.python_adapter
        
        if tech_lower in ['javascript', 'js', 'typescript', 'ts', 'nodejs', 'node', 'express', 'react', 'react router', 'react-router']:
            return self.node_adapter
        
        if tech_lower in ['css', 'html', 'styling', 'frontend design']:
            return self.static_adapter
        
        if tech_lower in ['sql', 'sqlite', 'postgresql', 'database']:
            return self.sql_adapter

        # 2. Check file extensions if technology is generic or unspecified
        extensions = {os.path.splitext(f.get('name', ''))[1].lower() for f in (files or [])}

        if '.py' in extensions:
            return self.python_adapter
        if any(ext in extensions for ext in ['.js', '.jsx', '.ts', '.tsx']):
            return self.node_adapter
        if any(ext in extensions for ext in ['.css', '.html']):
            return self.static_adapter
        if '.sql' in extensions:
            return self.sql_adapter
        
        return self.unsupported_adapter

    def evaluate(self, challenge, files=None, code=None, timeout=5.0):
        start_time = time.time()

        # 1. Normalize challenge dictionary / model
        if hasattr(challenge, 'to_dict'):
            c_dict = challenge.to_dict()
            points = challenge.points
            technology = challenge.technology
            test_cases = challenge.test_cases or []
            bug_signature = challenge.bug_signature or ''
        elif isinstance(challenge, dict):
            c_dict = challenge
            points = challenge.get('points', 100)
            technology = challenge.get('technology', 'React')
            test_cases = challenge.get('testCases') or challenge.get('test_cases') or []
            bug_signature = challenge.get('bugSignature') or challenge.get('bug_signature') or ''
        else:
            c_dict = {}
            points = 100
            technology = 'Unknown'
            test_cases = []
            bug_signature = ''

        # 2. Normalize workspace files
        chal_files = c_dict.get('files') or []
        norm_files = []

        if files and isinstance(files, list):
            for f in files:
                if isinstance(f, dict):
                    norm_files.append({
                        'name': f.get('name') or f.get('filename') or 'main.js',
                        'content': f.get('content') or ''
                    })
                elif isinstance(f, str):
                    norm_files.append({'name': 'main.txt', 'content': f})

            user_filenames = {f['name'].lower() for f in norm_files}
            for cf in chal_files:
                cf_name = cf.get('name', '')
                if cf_name.lower() in ('schema.sql', 'setup.sql', 'seed.sql') and cf_name.lower() not in user_filenames:
                    norm_files.insert(0, cf)

        elif code and isinstance(code, str):
            tech_low = (technology or '').lower().strip()
            if tech_low in ['python', 'django', 'backend', 'fastapi', 'flask']:
                ext = '.py'
            elif tech_low in ['sql', 'sqlite', 'postgresql', 'database']:
                ext = '.sql'
            elif tech_low in ['css']:
                ext = '.css'
            elif tech_low in ['javascript', 'nodejs', 'node', 'express', 'react']:
                ext = '.js'
            else:
                ext = '.txt'

            suspected = getattr(challenge, 'suspected_component', None) or (challenge.get('suspected_component') if isinstance(challenge, dict) else None)
            user_filename = suspected if suspected else ('query.sql' if ext == '.sql' else f'main{ext}')
            norm_files = [{'name': user_filename, 'content': code}]

            # Only insert schema.sql if chal_files has secondary query files
            has_secondary_sql = any(f.get('name', '').lower() not in ('schema.sql', 'setup.sql', 'seed.sql') for f in chal_files)
            if has_secondary_sql:
                for cf in chal_files:
                    cf_name = cf.get('name', '')
                    if cf_name.lower() in ('schema.sql', 'setup.sql', 'seed.sql'):
                        norm_files.insert(0, cf)
        else:
            norm_files = list(chal_files)

        # 3. Select appropriate runtime adapter
        adapter = self.resolve_adapter(technology, norm_files)

        # 4. Execute evaluation through adapter and sandbox runner
        res = adapter.evaluate(challenge, norm_files, test_cases, timeout=timeout)

        # 5. Process test results & backend score calculation
        test_results = res.get('test_results', [])
        tests_total = len(test_results)
        tests_passed = len([t for t in test_results if t.get('passed')])

        timed_out = res.get('timed_out', False)
        exit_code = res.get('exit_code', -1)
        error = res.get('error')

        primary_code = "\n".join([f.get('content', '') for f in norm_files])
        bug_signature_detected = (bug_signature.strip() in primary_code) if bug_signature.strip() else False

        if tests_total > 0:
            success = (tests_passed == tests_total) and not timed_out and (exit_code == 0) and not bug_signature_detected and not error
            score = int(round((tests_passed / tests_total) * points)) if success else 0
        else:
            success = (exit_code == 0) and not timed_out and not error and not bug_signature_detected
            score = points if success else 0

        # Generate summary message
        if timed_out:
            ai_summary = f"Execution timed out ({timeout}s limit exceeded). Check for infinite loops or heavy operations."
        elif error and not success:
            ai_summary = f"Execution encountered an error: {error}"
        elif success:
            ai_summary = f"Excellent fix! All {tests_passed}/{tests_total or 1} tests passed successfully."
        else:
            ai_summary = f"Evaluation completed: {tests_passed}/{tests_total} tests passed. Check the output panel for details."

        total_elapsed = time.time() - start_time

        return {
            "success": success,
            "score": score,
            "tests_passed": tests_passed,
            "tests_total": tests_total,
            "test_results": test_results,
            "stdout": res.get('stdout', ''),
            "stderr": res.get('stderr', ''),
            "execution_time": round(total_elapsed, 4),
            "timed_out": timed_out,
            "error": error,
            "bug_signature_detected": bug_signature_detected,
            "ai_summary": ai_summary
        }
