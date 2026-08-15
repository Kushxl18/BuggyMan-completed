import os
import json
import requests

class BugInjector:
    @staticmethod
    def inject_bug(code: str, bug_type: str = 'logic', technology: str = 'React') -> dict:
        """
        Injects realistic software bugs (syntax, logic, state, boundary, performance)
        into valid working code snippets.
        """
        tech_lower = (technology or 'React').lower()
        bug_type_lower = (bug_type or 'logic').lower()

        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            try:
                prompt = f"""You are an expert AI software testing and bug injection engine.
Take this valid working {technology} code and inject a realistic '{bug_type_lower}' bug.

Original Working Code:
```
{code}
```

Return JSON ONLY matching this exact schema:
{{
  "originalCode": {json.dumps(code)},
  "buggyCode": "code snippet containing injected bug",
  "bugType": "{bug_type_lower}",
  "intendedBug": "clear description of the injected bug",
  "suspectedComponent": "component or line identifier where bug was injected",
  "bugSignature": "exact line of code containing injected bug",
  "testCases": [
    {{"id": 1, "name": "verification test case", "input": "test input", "expected": "expected behavior", "passed": false}}
  ]
}}"""
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                headers = {'Content-Type': 'application/json'}
                body = {'contents': [{'parts': [{'text': prompt}]}]}
                res = requests.post(url, json=body, headers=headers, timeout=10)
                if res.status_code == 200:
                    text_resp = res.json()['candidates'][0]['content']['parts'][0]['text']
                    if '```json' in text_resp:
                        text_resp = text_resp.split('```json')[1].split('```')[0].strip()
                    elif '```' in text_resp:
                        text_resp = text_resp.split('```')[1].split('```')[0].strip()
                    parsed = json.loads(text_resp)
                    return parsed
            except Exception as e:
                print(f"Gemini bug injection failed, falling back to dynamic injector: {e}")

        # Dynamic fallback pattern injector
        buggy_code = code
        intended_bug = f"Injected {bug_type_lower} bug in {technology} code"
        suspected_comp = "main logic component"
        bug_sig = ""

        if 'react' in tech_lower or 'js' in tech_lower or 'javascript' in tech_lower:
            if 'state_mutation' in bug_type_lower or 'state' in bug_type_lower:
                if 'setCount(prev => prev + 1)' in code:
                    buggy_code = code.replace('setCount(prev => prev + 1)', 'count = count + 1;')
                    bug_sig = 'count = count + 1;'
                    intended_bug = 'Replaced immutable state setter with direct variable assignment count = count + 1'
                elif 'useState(' in code:
                    buggy_code = code.replace("useState('')", "useState()").replace("useState(0)", "useState()")
                    bug_sig = "useState()"
                    intended_bug = 'Omitted initial state argument causing uncontrolled component warnings'
                else:
                    buggy_code = code + "\n// BUG: Direct mutation\nstate.value = 'mutated';"
                    bug_sig = "state.value = 'mutated';"
                    intended_bug = 'Direct state object property mutation'
            elif 'boundary' in bug_type_lower:
                buggy_code = code.replace('<', '<=').replace('>', '>=')
                bug_sig = '<='
                intended_bug = 'Off-by-one boundary comparison error'
            elif 'syntax' in bug_type_lower:
                buggy_code = code.replace(';', '').replace('}', '')
                bug_sig = 'Unmatched closing bracket'
                intended_bug = 'Syntax error: missing closing brace'
            else: # logic
                buggy_code = code.replace('+', '-').replace('==', '!=')
                bug_sig = 'Operator substitution'
                intended_bug = 'Inverted comparison or arithmetic logic operator'

        elif 'sql' in tech_lower:
            if 'WHERE' in code:
                buggy_code = code.replace("WHERE status = 'completed'", "").replace("WHERE", "-- WHERE")
                bug_sig = "Omitted WHERE filter"
                intended_bug = 'Removed WHERE filtering clause, returning unwanted table records'
            else:
                buggy_code = code.replace("SELECT", "SELECT DISTINCT")
                bug_sig = "SELECT DISTINCT"
                intended_bug = 'Incorrect column aggregation clause'

        else: # Python / General
            if 'boundary' in bug_type_lower:
                buggy_code = code.replace('range(len(', 'range(len(' + ' + 1')
                bug_sig = 'range boundary'
                intended_bug = 'Index error: range upper bound exceeds list length'
            elif 'syntax' in bug_type_lower:
                buggy_code = code.replace(':', '')
                bug_sig = 'Missing colon'
                intended_bug = 'Syntax error: missing colon at end of statement'
            else:
                buggy_code = code.replace('==', '!=')
                bug_sig = '=='
                intended_bug = 'Inverted conditional check'

        return {
            'originalCode': code,
            'buggyCode': buggy_code,
            'bugType': bug_type_lower,
            'intendedBug': intended_bug,
            'suspectedComponent': suspected_comp,
            'bugSignature': bug_sig or buggy_code[:40],
            'testCases': [
                {'id': 1, 'name': f'Verifies fix for {intended_bug[:30]}', 'input': 'Run evaluation', 'expected': 'Clean execution without bugs', 'passed': False}
            ]
        }
