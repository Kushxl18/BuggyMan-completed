import os
import re
import json
import shutil
import sqlite3
from abc import ABC, abstractmethod
from .sandboxes import SubprocessSandboxRunner


class BaseRuntimeAdapter(ABC):
    def __init__(self, sandbox_runner=None):
        self.sandbox_runner = sandbox_runner or SubprocessSandboxRunner()

    @abstractmethod
    def evaluate(self, challenge, files, test_cases, timeout=5.0):
        pass


class PythonRuntimeAdapter(BaseRuntimeAdapter):
    """
    Runtime adapter for Python code execution.
    Creates a driver script that executes user code and runs challenge test cases.
    """
    def evaluate(self, challenge, files, test_cases, timeout=5.0):
        # 1. Identify primary Python file
        py_files = [f for f in files if (f.get('name') or '').endswith('.py')]
        primary_file = py_files[0] if py_files else (files[0] if files else {'name': 'main.py', 'content': ''})
        primary_filename = primary_file.get('name', 'main.py')

        c_dict = challenge if isinstance(challenge, dict) else (challenge.to_dict() if hasattr(challenge, 'to_dict') else {})
        bug_sig = c_dict.get('bug_signature') or c_dict.get('bugSignature') or ""

        # 2. Build test runner harness script
        test_harness_code = self._build_python_harness(primary_filename, test_cases, bug_sig)
        
        all_files = list(files)
        all_files.append({
            'name': '_runner.py',
            'content': test_harness_code
        })

        # 3. Execute via Python isolated mode (-I -B)
        python_bin = shutil.which("python") or shutil.which("python3") or "python"
        command = [python_bin, "-I", "-B", "_runner.py"]

        sandbox_result = self.sandbox_runner.run(all_files, command, timeout=timeout)
        
        # 4. Parse harness results
        return self._parse_sandbox_output(sandbox_result, test_cases)

    def _build_python_harness(self, primary_filename, test_cases, bug_signature=""):
        raw_json = json.dumps(test_cases or [])
        bug_sig_json = json.dumps(bug_signature or "")

        return f"""import sys
import re
import ast
import json
import traceback

test_results = []
test_cases = json.loads({repr(raw_json)})
bug_signature = json.loads({repr(bug_sig_json)})

# Import or execute target module
user_globals = {{}}
code_content = ""
try:
    with open('{primary_filename}', 'r', encoding='utf-8') as f:
        code_content = f.read()
    exec(compile(code_content, '{primary_filename}', 'exec'), user_globals)
except SyntaxError as se:
    print(f"SYNTAX_ERROR: {{se}}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"RUNTIME_ERROR: {{e}}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

clean_code_lines = [
    l for l in code_content.splitlines()
    if "buggy signature" not in l.lower() and "fix bug in" not in l.lower()
]
clean_code = "\\n".join(clean_code_lines)
has_bug = False
if bug_signature and bug_signature.strip():
    norm_bug = re.sub(r'\\s+', ' ', bug_signature).strip().lower()
    norm_code = re.sub(r'\\s+', ' ', clean_code).strip().lower()
    if norm_bug in norm_code:
        has_bug = True

for tc in test_cases:
    tc_id = tc.get('id')
    tc_name = tc.get('name', f'Test {{tc_id}}')
    expected = str(tc.get('expected', '')).strip()
    inp = tc.get('input', '')
    
    passed = False
    actual_out = ""
    err_msg = None
    try:
        if has_bug:
            passed = False
            actual_out = f"Bug signature still detected in code: '{{bug_signature}}'"
            err_msg = actual_out
        elif inp and inp.strip():
            try:
                if "\\n" in inp.strip():
                    lines = inp.strip().split("\\n")
                    exec("\\n".join(lines[:-1]), user_globals)
                    res = eval(lines[-1].strip(), user_globals)
                else:
                    res = eval(inp.strip(), user_globals)
                actual_out = str(res).strip()
                if actual_out == expected:
                    passed = True
                else:
                    try:
                        exp_obj = ast.literal_eval(expected)
                        res_obj = ast.literal_eval(actual_out)
                        passed = (exp_obj == res_obj)
                    except Exception:
                        passed = False
            except Exception as eval_err:
                fn_name = inp.strip()
                if fn_name in user_globals and callable(user_globals[fn_name]):
                    try:
                        res = user_globals[fn_name]()
                        actual_out = str(res).strip()
                        if actual_out == expected:
                            passed = True
                        else:
                            try:
                                exp_obj = ast.literal_eval(expected)
                                res_obj = ast.literal_eval(actual_out)
                                passed = (exp_obj == res_obj)
                            except Exception:
                                passed = False
                    except Exception as fn_err:
                        passed = False
                        err_msg = str(fn_err)
                        actual_out = f"Error: {{fn_err}}"
                else:
                    passed = False
                    err_msg = str(eval_err)
                    actual_out = f"Error: {{eval_err}}"
        else:
            passed = False
            actual_out = "No test input provided for test case"
            err_msg = actual_out

    except Exception as ex:
        passed = False
        err_msg = str(ex)
        actual_out = f"Error: {{ex}}"

    test_results.append({{
        'id': tc_id,
        'name': tc_name,
        'passed': passed,
        'input': inp,
        'expected': expected,
        'actual': actual_out,
        'error': err_msg,
        'hidden': bool(tc.get('hidden', False))
    }})

print("---BUGGYMAN_TEST_RESULTS---")
print(json.dumps(test_results))
"""

    def _parse_sandbox_output(self, sandbox_result, default_test_cases):
        stdout = sandbox_result.stdout
        stderr = sandbox_result.stderr
        
        parsed_tests = []
        clean_stdout = stdout

        if "---BUGGYMAN_TEST_RESULTS---" in stdout:
            parts = stdout.split("---BUGGYMAN_TEST_RESULTS---")
            clean_stdout = parts[0].strip()
            try:
                parsed_tests = json.loads(parts[1].strip())
            except Exception:
                parsed_tests = []

        if not parsed_tests and default_test_cases:
            # If harness failed or didn't output valid JSON, mark tests as failed
            for tc in default_test_cases:
                parsed_tests.append({
                    'id': tc.get('id'),
                    'name': tc.get('name', 'Execution Test'),
                    'passed': False,
                    'input': tc.get('input', ''),
                    'expected': tc.get('expected', ''),
                    'actual': stderr or "Execution failed before tests completed",
                    'error': stderr or "Test runner failed"
                })

        return {
            'exit_code': sandbox_result.exit_code,
            'stdout': clean_stdout,
            'stderr': stderr,
            'timed_out': sandbox_result.timed_out,
            'error': sandbox_result.error,
            'execution_time': sandbox_result.execution_time,
            'test_results': parsed_tests
        }


class NodeRuntimeAdapter(BaseRuntimeAdapter):
    """
    Runtime adapter for JavaScript / Node.js execution.
    Executes JS code via `node` executable in sandbox environment.
    """
    def evaluate(self, challenge, files, test_cases, timeout=5.0):
        js_files = [f for f in files if (f.get('name') or '').endswith(('.js', '.jsx', '.ts', '.tsx'))]
        primary_file = js_files[0] if js_files else (files[0] if files else {'name': 'index.js', 'content': ''})
        primary_filename = primary_file.get('name', 'index.js')
        user_code = primary_file.get('content', '')

        node_bin = shutil.which("node")
        if not node_bin:
            # Fallback to static code structure adapter if Node is not available
            static_adapter = StaticCodeRuntimeAdapter(self.sandbox_runner)
            return static_adapter.evaluate(challenge, files, test_cases, timeout)

        runner_js = self._build_node_harness(primary_filename, user_code, test_cases, challenge)
        all_files = list(files)
        all_files.append({
            'name': '_runner.js',
            'content': runner_js
        })

        command = [node_bin, "--no-addons", "_runner.js"]
        sandbox_result = self.sandbox_runner.run(all_files, command, timeout=timeout)
        
        return self._parse_sandbox_output(sandbox_result, test_cases, user_code)

    def _build_node_harness(self, primary_filename, user_code, test_cases, challenge=None):
        test_cases_json = json.dumps(test_cases or [])
        c_dict = challenge if isinstance(challenge, dict) else (challenge.to_dict() if hasattr(challenge, 'to_dict') else {}) if challenge else {}
        bug_sig = c_dict.get('bug_signature') or c_dict.get('bugSignature') or ""
        bug_sig_json = json.dumps(bug_sig or "")

        return f"""
const fs = require('fs');
const path = require('path');

const testCases = {test_cases_json};
const bugSignature = {bug_sig_json};
const testResults = [];

let userExports = {{}};

try {{
    const code = fs.readFileSync('{primary_filename}', 'utf8');

    // Syntax validation for missing import keywords
    const codeLines = code.split('\\n');
    for (const l of codeLines) {{
        const trimmed = l.trim();
        if (trimmed.includes('from ') && (trimmed.endsWith("';") || trimmed.endsWith('";') || trimmed.endsWith("'") || trimmed.endsWith('"'))) {{
            if (!trimmed.startsWith('import ') && !trimmed.startsWith('//') && !trimmed.startsWith('/*')) {{
                console.error("SYNTAX_ERROR: Missing 'import' keyword before module statement");
                process.exit(1);
            }}
        }}
    }}

    try {{
        const cleanCode = code
            .replace(/import\\s+.*?from\\s+['"].*?['"];?/g, '')
            .replace(/export\\s+default\\s+/g, '')
            .replace(/export\\s+/g, '');
        const mod = {{ exports: {{}} }};
        const fn = new Function('module', 'exports', 'require', '__filename', '__dirname', cleanCode);
        fn(mod, mod.exports, require, '{primary_filename}', __dirname);
        userExports = mod.exports;

        // Verify component runtime execution with sample fixture props
        const sampleBugs = [{{ id: 1, title: 'Sample Bug' }}];
        const compFn = (userExports && userExports.default) || (userExports && userExports.BugSearch) || (typeof userExports === 'function' ? userExports : null);
        if (typeof compFn === 'function') {{
            compFn({{ bugs: sampleBugs, query: '' }});
        }}
    }} catch (e) {{
        if (e.message && e.message.includes("is not defined")) {{
            console.error("RUNTIME_ERROR: " + e.message);
            process.exit(1);
        }}
        userExports = {{ _rawCode: code }};
    }}
}} catch (err) {{
    console.error("LOAD_ERROR: " + err.message);
    process.exit(1);
}}

const userCodeStr = fs.readFileSync('{primary_filename}', 'utf8');
const strippedUserCode = userCodeStr.split('\\n')
    .filter(line => !line.toLowerCase().includes('buggy signature') && !line.toLowerCase().includes('fix bug in'))
    .join('\\n');
const codeNoComments = strippedUserCode
    .replace(/\\/\\*[\\s\\S]*?\\*\\//g, '')
    .split('\\n')
    .map(line => {{
        const idx = line.indexOf('//');
        return idx !== -1 ? line.substring(0, idx) : line;
    }})
    .join('\\n');
const normCleanCode = codeNoComments.toLowerCase().replace(/\\s+/g, ' ');
const normBugSig = bugSignature.toLowerCase().replace(/\\s+/g, ' ').trim();
const hasBug = Boolean(normBugSig && normCleanCode.includes(normBugSig));

for (const tc of testCases) {{
    const tcId = tc.id;
    const tcName = tc.name || `Test ${{tcId}}`;
    const expected = (tc.expected || '').trim();
    const input = (tc.input || '').trim();

    let passed = false;
    let actual = '';
    let error = null;

    const normExpected = expected.toLowerCase().replace(/\\s+/g, ' ');

    try {{
        if (hasBug) {{
            passed = false;
            actual = `Bug signature still detected: '${{bugSignature}}'`;
            error = actual;
        }} else if (input && input.trim()) {{
            try {{
                const evalFn = new Function('exports', 'require', input);
                const evalRes = evalFn(userExports, require);
                const evalStr = String(evalRes !== undefined ? evalRes : '').trim();
                if (evalStr === expected) {{
                    passed = true;
                    actual = evalStr;
                }} else {{
                    passed = false;
                    actual = evalStr;
                    error = `Expected '${{expected}}', got '${{evalStr}}'`;
                }}
            }} catch (evalErr) {{
                passed = false;
                error = evalErr.message;
                actual = `Error: ${{evalErr.message}}`;
            }}
        }} else if (expected && (codeNoComments.includes(expected) || normCleanCode.includes(normExpected))) {{
            passed = true;
            actual = expected;
        }} else {{
            passed = false;
            actual = `Code did not satisfy expected assertion '${{expected}}'`;
            error = actual;
        }}
    }} catch (e) {{
        passed = false;
        error = e.message;
        actual = `Error: ${{e.message}}`;
    }}

    testResults.push({{
        id: tcId,
        name: tcName,
        passed: passed,
        input: input,
        expected: expected,
        actual: actual,
        error: error,
        hidden: Boolean(tc.hidden)
    }});
}}

console.log("---BUGGYMAN_TEST_RESULTS---");
console.log(JSON.stringify(testResults));
"""

    def _parse_sandbox_output(self, sandbox_result, default_test_cases, user_code=""):
        stdout = sandbox_result.stdout
        stderr = sandbox_result.stderr
        
        parsed_tests = []
        clean_stdout = stdout

        if "---BUGGYMAN_TEST_RESULTS---" in stdout:
            parts = stdout.split("---BUGGYMAN_TEST_RESULTS---")
            clean_stdout = parts[0].strip()
            try:
                parsed_tests = json.loads(parts[1].strip())
            except Exception:
                parsed_tests = []

        if sandbox_result.exit_code != 0 or stderr:
            # If process exited non-zero or produced stderr, force failure
            for tc in (default_test_cases or []):
                parsed_tests.append({
                    'id': tc.get('id'),
                    'name': tc.get('name', 'JS Execution Test'),
                    'passed': False,
                    'input': tc.get('input', ''),
                    'expected': str(tc.get('expected', '')),
                    'actual': stderr or "Execution / Syntax error in code",
                    'error': stderr or "Execution failed"
                })
        elif not parsed_tests and default_test_cases:
            for tc in default_test_cases:
                exp = str(tc.get('expected', '')).strip()
                parsed_tests.append({
                    'id': tc.get('id'),
                    'name': tc.get('name', 'JS Execution Test'),
                    'passed': False,
                    'input': tc.get('input', ''),
                    'expected': exp,
                    'actual': stderr or "Execution failed before tests completed",
                    'error': stderr or "Execution failed"
                })

        return {
            'exit_code': sandbox_result.exit_code,
            'stdout': clean_stdout,
            'stderr': stderr,
            'timed_out': sandbox_result.timed_out,
            'error': sandbox_result.error or (stderr if sandbox_result.exit_code != 0 else None),
            'execution_time': sandbox_result.execution_time,
            'test_results': parsed_tests
        }


class StaticCodeRuntimeAdapter(BaseRuntimeAdapter):
    """
    Adapter for CSS/HTML, React, and Frontend structure analysis.
    Evaluates DOM elements, CSS rules, React hooks, event bindings, and bug signatures safely.
    """
    def _validate_js_syntax(self, code):
        if not code or not code.strip():
            return "Code file is empty."

        # Syntax check for missing import keyword (e.g. `React, { useState } from 'react';`)
        for line in code.splitlines():
            l_clean = line.strip()
            if 'from ' in l_clean and (l_clean.endswith("';") or l_clean.endswith('";') or l_clean.endswith("'") or l_clean.endswith('"')):
                if not l_clean.startswith('import ') and not l_clean.startswith('//') and not l_clean.startswith('/*'):
                    return "Missing 'import' keyword before module statement"
        stack = []
        pairs = {')': '(', '}': '{', ']': '['}
        in_str = None
        esc = False

        for char in code:
            if esc:
                esc = False
                continue
            if char == '\\' and in_str:
                esc = True
                continue
            if char in ('"', "'", '`'):
                if not in_str:
                    in_str = char
                elif in_str == char:
                    in_str = None
                continue
            if in_str:
                continue
            if char in ('(', '{', '['):
                stack.append(char)
            elif char in (')', '}', ']'):
                if not stack or stack[-1] != pairs[char]:
                    return f"Unmatched closing '{char}' in code"
                stack.pop()

        if in_str:
            return f"Unterminated string literal ({in_str})"
        if stack:
            return f"Unclosed token '{stack[-1]}' in code"

        if re.search(r'const\s+\w+\s*=\s*;', code) or re.search(r'let\s+\w+\s*=\s*;', code):
            return "Invalid assignment syntax (empty expression after =)"

        # Reference check for callback parameter mismatch (e.g. `bug => (r.title ...)` where `r` is undeclared)
        cb_matches = re.finditer(r'\.(filter|map|forEach|find|some|every)\s*\(\s*([A-Za-z0-9_]+)\s*=>\s*([^;\}]+)', code)
        for m in cb_matches:
            param_name = m.group(2)
            body_text = m.group(3)
            prop_accesses = re.findall(r'\b([A-Za-z0-9_]+)\.[A-Za-z0-9_]+', body_text)
            for obj_name in prop_accesses:
                if obj_name not in [param_name, 'Math', 'Object', 'Array', 'JSON', 'String', 'Number', 'Boolean', 'console', 'e', 'event', 'props', 'query', 'bugs', 'items']:
                    if not re.search(rf'\b(const|let|var|function|import)\s+{obj_name}\b', code):
                        return f"ReferenceError: '{obj_name}' is not defined (did you mean '{param_name}'?)"

        return None

    def evaluate(self, challenge, files, test_cases, timeout=5.0):
        all_code = "\n".join([f.get('content', '') for f in files])
        c_dict = challenge if isinstance(challenge, dict) else (challenge.to_dict() if hasattr(challenge, 'to_dict') else {})
        bug_sig = c_dict.get('bug_signature') or c_dict.get('bugSignature') or ""

        parsed_tests = []
        has_bug = False

        # 0. Check syntax errors and empty code
        syntax_err = self._validate_js_syntax(all_code)
        if syntax_err:
            for tc in (test_cases or []):
                parsed_tests.append({
                    'id': tc.get('id'),
                    'name': tc.get('name', 'Syntax Check'),
                    'passed': False,
                    'input': tc.get('input', ''),
                    'expected': str(tc.get('expected', '')),
                    'actual': f"Syntax Error: {syntax_err}",
                    'error': syntax_err
                })
            return {
                'exit_code': 1,
                'stdout': '',
                'stderr': f"SyntaxError: {syntax_err}",
                'timed_out': False,
                'error': f"SyntaxError: {syntax_err}",
                'execution_time': 0.005,
                'test_results': parsed_tests
            }

        # 1. Bug signature detection check (strip template header comments)
        clean_code_lines = [
            l for l in all_code.splitlines()
            if "buggy signature" not in l.lower() and "fix bug in" not in l.lower()
        ]
        clean_code_for_sig = "\n".join(clean_code_lines)
        if bug_sig and bug_sig.strip():
            norm_bug = re.sub(r'\s+', ' ', bug_sig).strip().lower()
            norm_code_sig = re.sub(r'\s+', ' ', clean_code_for_sig).strip().lower()
            if norm_bug in norm_code_sig:
                has_bug = True

        # Strip all single-line and multi-line comments for pattern verification
        clean_code_no_comments = re.sub(r'/\*[\s\S]*?\*/', '', clean_code_for_sig)
        clean_code_no_comments = "\n".join([
            l[:l.index('//')] if '//' in l else l
            for l in clean_code_no_comments.splitlines()
        ])
        norm_code = re.sub(r'\s+', ' ', clean_code_no_comments).lower()

        # 2. Evaluate test cases against AST, CSS, DOM and code patterns
        for tc in (test_cases or []):
            tc_id = tc.get('id')
            tc_name = tc.get('name', f'Frontend Check {tc_id}')
            expected = str(tc.get('expected', '')).strip()

            passed = False
            actual = ""

            if has_bug:
                passed = False
                actual = f"Bug signature still detected in code: '{bug_sig}'"
            elif not expected:
                passed = False
                actual = "No verification criteria defined"
            else:
                norm_expected = re.sub(r'\s+', ' ', expected).lower()

                # Flexible AST / JSX / DOM / CSS pattern matching
                if norm_expected in norm_code or expected in clean_code_no_comments:
                    passed = True
                    actual = expected
                else:
                    passed = False
                    actual = f"Failed verification check. Expected: '{expected}'"

            parsed_tests.append({
                'id': tc_id,
                'name': tc_name,
                'passed': passed,
                'input': tc.get('input', ''),
                'expected': expected,
                'actual': actual,
                'error': None if passed else actual,
                'hidden': bool(tc.get('hidden', False))
            })

        all_passed = all(t['passed'] for t in parsed_tests) and not has_bug
        return {
            'exit_code': 0 if all_passed else 1,
            'stdout': 'Frontend AST & DOM evaluation completed successfully.' if all_passed else 'Verification checks failed.',
            'stderr': '' if all_passed else ('Bug signature detected in code.' if has_bug else 'One or more frontend verification checks failed.'),
            'timed_out': False,
            'error': None if all_passed else ('Bug signature detected' if has_bug else 'Verification failure'),
            'execution_time': 0.005,
            'test_results': parsed_tests
        }


class SQLRuntimeAdapter(BaseRuntimeAdapter):
    """
    Adapter for SQL challenges executing in an isolated in-memory SQLite instance.
    Runs schema DDL/sample data setup first, then executes user queries safely,
    returning structured tabular output and SQL error messages.
    """
    def evaluate(self, challenge, files, test_cases, timeout=5.0):
        # 1. Separate schema/setup files from user query files
        schema_files = [f for f in files if (f.get('name') or '').lower() in ('schema.sql', 'setup.sql', 'seed.sql')]
        query_files = [f for f in files if f not in schema_files and (f.get('name') or '').endswith('.sql')]

        if query_files:
            setup_code = "\n".join([f.get('content', '') for f in schema_files]) if schema_files else ""
            user_query_file = query_files[0]
        else:
            setup_code = ""
            user_query_file = schema_files[0] if schema_files else (files[0] if files else {'name': 'query.sql', 'content': ''})

        user_code = user_query_file.get('content', '')

        # Security check: disallow SQLite extension loading or unsafe PRAGMA statements
        forbidden = [r'\bload_extension\b', r'\battach\s+database\b']
        for pat in forbidden:
            if re.search(pat, user_code, re.IGNORECASE):
                err = "SECURITY_ERROR: Disallowed SQL command or extension invocation."
                return self._build_error_response(err, test_cases)

        stdout_lines = []
        stderr = ""
        last_columns = []
        last_rows = []
        parsed_tests = []
        start_time = os.times().user + os.times().system

        try:
            conn = sqlite3.connect(":memory:")
            cursor = conn.cursor()

            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON;")

            # 2. Execute schema setup statements
            if setup_code and setup_code.strip():
                for stmt in setup_code.split(";"):
                    s = stmt.strip()
                    if s:
                        cursor.execute(s)
                conn.commit()

            # 3. Execute user SQL statements
            user_stmts = [s.strip() for s in user_code.split(";") if s.strip()]
            
            if not user_stmts:
                stdout_lines.append("Empty query submitted.")

            for stmt in user_stmts:
                cursor.execute(stmt)
                if cursor.description:
                    # SELECT query or returning statement
                    cols = [d[0] for d in cursor.description]
                    rows = cursor.fetchall()
                    last_columns = cols
                    last_rows = rows
                    table_str = self._format_table(cols, rows)
                    stdout_lines.append(table_str)
                else:
                    # DML / DDL statement
                    affected = cursor.rowcount
                    stdout_lines.append(f"Statement executed cleanly. ({affected} row{'s' if affected != 1 else ''} affected)")

            conn.commit()
            stdout = "\n\n".join(stdout_lines)

            # 4. Evaluate query result set against expected query result set
            expected_query = challenge.get('expected_query') if isinstance(challenge, dict) else getattr(challenge, 'expected_query', None)
            ordered_comparison = challenge.get('ordered_comparison') if isinstance(challenge, dict) else getattr(challenge, 'ordered_comparison', False)

            if not expected_query:
                chal_id = challenge.get('id') if isinstance(challenge, dict) else getattr(challenge, 'id', None)
                chal_title = str(challenge.get('title') if isinstance(challenge, dict) else getattr(challenge, 'title', ''))
                try:
                    from buggyman.data.sql_challenges import get_sql_challenges
                    for sc in get_sql_challenges():
                        if (chal_id is not None and str(sc.get('id')) == str(chal_id)) or \
                           (sc.get('title') and sc.get('title') == chal_title) or \
                           (sc.get('title') and chal_title and (sc.get('title') in chal_title or chal_title in sc.get('title'))):
                            expected_query = sc.get('expected_query')
                            if sc.get('ordered_comparison'):
                                ordered_comparison = True
                            break
                except Exception:
                    pass

            if not expected_query:
                chal_id = str(challenge.get('id') if isinstance(challenge, dict) else getattr(challenge, 'id', '')).upper()
                chal_title = str(challenge.get('title') if isinstance(challenge, dict) else getattr(challenge, 'title', '')).upper()
                from buggyman.views import SPECIAL_CHALLENGE_CATALOG
                for cat_key, cat_item in SPECIAL_CHALLENGE_CATALOG.items():
                    if cat_key in chal_id or cat_key in chal_title or f"[{cat_key}]" in chal_title:
                        expected_query = cat_item.get('expected_query')
                        if cat_item.get('ordered_comparison'):
                            ordered_comparison = True
                        break

            if not ordered_comparison:
                chal_title = str(challenge.get('title') if isinstance(challenge, dict) else getattr(challenge, 'title', '')).lower()
                if 'order' in chal_title or 'sort' in chal_title or 'rank' in chal_title or 'top-' in chal_title:
                    ordered_comparison = True

            expected_columns = []
            expected_rows = []
            expected_table_str = ""

            if expected_query:
                try:
                    exp_conn = sqlite3.connect(":memory:")
                    exp_conn.execute("PRAGMA foreign_keys = ON;")
                    if setup_code and setup_code.strip():
                        for stmt in setup_code.split(";"):
                            s = stmt.strip()
                            if s:
                                exp_conn.execute(s)
                        exp_conn.commit()
                    exp_cursor = exp_conn.cursor()
                    for eq_stmt in expected_query.split(";"):
                        eq_clean = eq_stmt.strip()
                        if eq_clean:
                            exp_cursor.execute(eq_clean)
                            if exp_cursor.description:
                                expected_columns = [d[0] for d in exp_cursor.description]
                                expected_rows = exp_cursor.fetchall()
                                expected_table_str = self._format_table(expected_columns, expected_rows)
                    exp_conn.close()
                except Exception:
                    pass

            c_dict = challenge if isinstance(challenge, dict) else (challenge.to_dict() if hasattr(challenge, 'to_dict') else {})
            bug_sig = c_dict.get('bug_signature') or c_dict.get('bugSignature') or ""
            clean_code_lines = [
                l for l in user_code.splitlines()
                if "buggy signature" not in l.lower() and "fix bug in" not in l.lower()
            ]
            clean_code = "\n".join(clean_code_lines)
            has_bug = False
            if bug_sig and bug_sig.strip():
                norm_bug = re.sub(r'\s+', ' ', bug_sig).strip().lower()
                norm_code = re.sub(r'\s+', ' ', clean_code).strip().lower()
                if norm_bug in norm_code:
                    has_bug = True

            for tc in (test_cases or []):
                tc_id = tc.get('id')
                tc_name = tc.get('name', f'SQL Result Check {tc_id}')
                expected_str = str(tc.get('expected', '')).strip()

                passed = False
                actual_output = ""
                err_detail = None

                if has_bug:
                    passed = False
                    actual_output = f"Bug signature still detected in query: '{bug_sig}'"
                    err_detail = actual_output
                elif expected_rows or expected_columns:
                    cols_ok = True
                    if expected_columns and last_columns:
                        cols_ok = ([c.lower() for c in last_columns] == [c.lower() for c in expected_columns])
                    else:
                        cols_ok = False

                    if ordered_comparison:
                        rows_ok = (last_rows == expected_rows)
                    else:
                        try:
                            sorted_actual = sorted([tuple(r) for r in last_rows])
                            sorted_expected = sorted([tuple(r) for r in expected_rows])
                            rows_ok = (sorted_actual == sorted_expected)
                        except Exception:
                            rows_ok = (set(tuple(r) for r in last_rows) == set(tuple(r) for r in expected_rows))

                    passed = cols_ok and rows_ok
                    actual_output = stdout if passed else f"Returned {len(last_rows)} rows (Expected {len(expected_rows)} matching rows)."
                    if not passed:
                        if not cols_ok:
                            err_detail = f"Column schema mismatch. Expected columns: {expected_columns}, Got: {last_columns}"
                        elif not rows_ok and ordered_comparison:
                            err_detail = f"Row order mismatch. Expected:\n{expected_table_str}\nGot:\n{stdout}"
                        elif not rows_ok:
                            err_detail = f"Result set mismatch. Expected rows:\n{expected_table_str}\nGot:\n{stdout}"
                else:
                    if expected_str:
                        norm_expected = re.sub(r'\s+', ' ', expected_str).strip().lower()
                        norm_stdout = re.sub(r'\s+', ' ', stdout).strip().lower()
                        if norm_expected in norm_stdout:
                            passed = True
                            actual_output = expected_str
                        else:
                            passed = False
                            actual_output = f"Result did not satisfy assertion: '{expected_str}'"
                            err_detail = actual_output
                    else:
                        passed = False
                        actual_output = "No valid assertion criteria found for SQL verification."
                        err_detail = actual_output

                parsed_tests.append({
                    'id': tc_id,
                    'name': tc_name,
                    'passed': passed,
                    'input': tc.get('input', ''),
                    'expected': expected_table_str or expected_str,
                    'actual': actual_output,
                    'error': err_detail,
                    'hidden': bool(tc.get('hidden', False))
                })

            conn.close()
            exec_duration = round(max(0.005, (os.times().user + os.times().system) - start_time), 3)

            all_passed = all(t['passed'] for t in parsed_tests) and not has_bug
            return {
                'exit_code': 0 if all_passed else 1,
                'stdout': stdout,
                'stderr': '' if all_passed else ('Bug signature detected in query.' if has_bug else 'SQL test failed.'),
                'timed_out': False,
                'error': None if all_passed else ('Bug signature detected' if has_bug else 'Query result verification failed'),
                'execution_time': exec_duration,
                'test_results': parsed_tests,
                'columns': last_columns,
                'rows': [list(r) for r in last_rows]
            }

        except sqlite3.Error as e:
            stderr = f"SQLite Error: {str(e)}"
            for tc in (test_cases or []):
                parsed_tests.append({
                    'id': tc.get('id'),
                    'name': tc.get('name', 'SQL Query'),
                    'passed': False,
                    'input': tc.get('input', ''),
                    'expected': str(tc.get('expected', '')),
                    'actual': f"SQL Error: {str(e)}",
                    'error': str(e)
                })

            return {
                'exit_code': 1,
                'stdout': "\n\n".join(stdout_lines),
                'stderr': stderr,
                'timed_out': False,
                'error': stderr,
                'execution_time': 0.01,
                'test_results': parsed_tests
            }

    def _format_table(self, headers, rows):
        if not headers:
            return "Query executed successfully. (0 columns)"
        if not rows:
            return f"Columns: {', '.join(headers)}\n(0 rows returned)"
        
        col_widths = [len(str(h)) for h in headers]
        for row in rows:
            for i, val in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(val if val is not None else 'NULL')))
        
        divider = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
        header_line = "| " + " | ".join([str(h).ljust(col_widths[i]) for i, h in enumerate(headers)]) + " |"
        
        lines = [divider, header_line, divider]
        for row in rows:
            row_str = "| " + " | ".join([str(val if val is not None else 'NULL').ljust(col_widths[i]) for i, val in enumerate(row)]) + " |"
            lines.append(row_str)
        lines.append(divider)
        lines.append(f"({len(rows)} row{'s' if len(rows) != 1 else ''} returned)")
        return "\n".join(lines)

    def _build_error_response(self, error_msg, test_cases):
        parsed_tests = []
        for tc in (test_cases or []):
            parsed_tests.append({
                'id': tc.get('id'),
                'name': tc.get('name', 'SQL Check'),
                'passed': False,
                'input': tc.get('input', ''),
                'expected': tc.get('expected', ''),
                'actual': error_msg,
                'error': error_msg
            })
        return {
            'exit_code': 1,
            'stdout': '',
            'stderr': error_msg,
            'timed_out': False,
            'error': error_msg,
            'execution_time': 0.0,
            'test_results': parsed_tests
        }


class UnsupportedRuntimeAdapter(BaseRuntimeAdapter):
    """
    Fallback for unsupported or unknown runtime technologies.
    """
    def evaluate(self, challenge, files, test_cases, timeout=5.0):
        tech = challenge.get('technology') if isinstance(challenge, dict) else getattr(challenge, 'technology', 'Unknown')
        error_msg = f"Unsupported runtime technology: '{tech}'. Execution engine supports Python, JavaScript/NodeJS, CSS, HTML, and SQL."
        
        parsed_tests = []
        for tc in (test_cases or []):
            parsed_tests.append({
                'id': tc.get('id'),
                'name': tc.get('name', 'Runtime Check'),
                'passed': False,
                'input': tc.get('input', ''),
                'expected': tc.get('expected', ''),
                'actual': error_msg,
                'error': error_msg
            })

        return {
            'exit_code': 1,
            'stdout': '',
            'stderr': error_msg,
            'timed_out': False,
            'error': error_msg,
            'execution_time': 0.0,
            'test_results': parsed_tests
        }
