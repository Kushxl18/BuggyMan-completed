"""
AI Providers Abstraction for BuggyMan
"""
import os
import json
import urllib.request
import urllib.error
import re
from abc import ABC, abstractmethod

class BaseAIProvider(ABC):
    @abstractmethod
    def generate_hint(self, context: dict, prompt: str) -> dict:
        pass

    @abstractmethod
    def generate_feedback(self, context: dict, prompt: str) -> dict:
        pass

    @abstractmethod
    def generate_explanation(self, context: dict, prompt: str) -> dict:
        pass

    @abstractmethod
    def generate_personalized_feedback(self, context: dict, prompt: str) -> dict:
        pass

class GeminiAIProvider(BaseAIProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY', '')

    def generate_hint(self, context: dict, prompt: str) -> dict:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 300
            }
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')

        with urllib.request.urlopen(req, timeout=8.0) as resp:
            body = resp.read().decode('utf-8')
            res_json = json.loads(body)
            candidates = res_json.get('candidates', [])
            if candidates:
                parts = candidates[0].get('content', {}).get('parts', [])
                if parts:
                    hint_text = parts[0].get('text', '').strip()
                    return {
                        'hint': hint_text,
                        'provider': 'gemini',
                        'isFallback': False
                    }

        raise RuntimeError("Gemini API returned an empty or invalid response structure.")

    def generate_feedback(self, context: dict, prompt: str) -> dict:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
                "maxOutputTokens": 500
            }
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')

        with urllib.request.urlopen(req, timeout=8.0) as resp:
            body = resp.read().decode('utf-8')
            res_json = json.loads(body)
            candidates = res_json.get('candidates', [])
            if candidates:
                parts = candidates[0].get('content', {}).get('parts', [])
                if parts:
                    raw_text = parts[0].get('text', '').strip()
                    parsed = json.loads(raw_text)
                    return {
                        'whatIsWrong': parsed.get('whatIsWrong', 'Issue detected in solution logic.'),
                        'whyItIsWrong': parsed.get('whyItIsWrong', 'The code does not satisfy challenge requirements.'),
                        'conceptToUnderstand': parsed.get('conceptToUnderstand', 'Core Programming Principles'),
                        'suggestedDirection': parsed.get('suggestedDirection', 'Review requirements and test case outputs.'),
                        'provider': 'gemini',
                        'isFallback': False
                    }

        raise RuntimeError("Gemini API returned an invalid feedback response.")

    def generate_explanation(self, context: dict, prompt: str) -> dict:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json",
                "maxOutputTokens": 600
            }
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')

        with urllib.request.urlopen(req, timeout=8.0) as resp:
            body = resp.read().decode('utf-8')
            res_json = json.loads(body)
            candidates = res_json.get('candidates', [])
            if candidates:
                parts = candidates[0].get('content', {}).get('parts', [])
                if parts:
                    raw_text = parts[0].get('text', '').strip()
                    parsed = json.loads(raw_text)
                    return {
                        'whatTheBugWas': parsed.get('whatTheBugWas', 'Bug detected in original code.'),
                        'whyItHappened': parsed.get('whyItHappened', 'Logic flaw in initial starter code.'),
                        'whyFixWorks': parsed.get('whyFixWorks', 'Your solution resolves the issue.'),
                        'keyConcept': parsed.get('keyConcept', 'Programming Design Patterns'),
                        'alternativeApproaches': parsed.get('alternativeApproaches', 'Functional or declarative patterns.'),
                        'provider': 'gemini',
                        'isFallback': False
                    }

        raise RuntimeError("Gemini API returned an invalid explanation response.")

    def generate_personalized_feedback(self, context: dict, prompt: str) -> dict:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json",
                "maxOutputTokens": 600
            }
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')

        with urllib.request.urlopen(req, timeout=8.0) as resp:
            body = resp.read().decode('utf-8')
            res_json = json.loads(body)
            candidates = res_json.get('candidates', [])
            if candidates:
                parts = candidates[0].get('content', {}).get('parts', [])
                if parts:
                    raw_text = parts[0].get('text', '').strip()
                    parsed = json.loads(raw_text)
                    return {
                        'debuggingStrengths': parsed.get('debuggingStrengths', ['Quick bug identification']),
                        'areasNeedingImprovement': parsed.get('areasNeedingImprovement', ['Complex state transitions']),
                        'recommendedFocus': parsed.get('recommendedFocus', 'Practice state management and query optimization.'),
                        'learningStyleInsight': parsed.get('learningStyleInsight', 'Consistent problem solving workflow.'),
                        'recommendedChallengeIds': parsed.get('recommendedChallengeIds', ['RE-E01', 'SQL-E01']),
                        'provider': 'gemini',
                        'isFallback': False
                    }

        raise RuntimeError("Gemini API returned an invalid personalized feedback response.")

class OpenAIAIProvider(BaseAIProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY', '')

    def generate_hint(self, context: dict, prompt: str) -> dict:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.api_key}"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are BuggyMan AI, an expert debugging mentor."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4,
            "max_tokens": 300
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')

        with urllib.request.urlopen(req, timeout=8.0) as resp:
            body = resp.read().decode('utf-8')
            res_json = json.loads(body)
            choices = res_json.get('choices', [])
            if choices:
                hint_text = choices[0].get('message', {}).get('content', '').strip()
                return {
                    'hint': hint_text,
                    'provider': 'openai',
                    'isFallback': False
                }

        raise RuntimeError("OpenAI API returned an empty or invalid response structure.")

    def generate_feedback(self, context: dict, prompt: str) -> dict:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.api_key}"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are BuggyMan AI. Return JSON only."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
            "max_tokens": 500
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')

        with urllib.request.urlopen(req, timeout=8.0) as resp:
            body = resp.read().decode('utf-8')
            res_json = json.loads(body)
            choices = res_json.get('choices', [])
            if choices:
                raw_text = choices[0].get('message', {}).get('content', '').strip()
                parsed = json.loads(raw_text)
                return {
                    'whatIsWrong': parsed.get('whatIsWrong', 'Issue detected in solution logic.'),
                    'whyItIsWrong': parsed.get('whyItIsWrong', 'The code does not satisfy challenge requirements.'),
                    'conceptToUnderstand': parsed.get('conceptToUnderstand', 'Core Programming Principles'),
                    'suggestedDirection': parsed.get('suggestedDirection', 'Review requirements and test case outputs.'),
                    'provider': 'openai',
                    'isFallback': False
                }

        raise RuntimeError("OpenAI API returned an invalid feedback response.")

    def generate_explanation(self, context: dict, prompt: str) -> dict:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.api_key}"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are BuggyMan AI. Return JSON only."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
            "max_tokens": 600
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')

        with urllib.request.urlopen(req, timeout=8.0) as resp:
            body = resp.read().decode('utf-8')
            res_json = json.loads(body)
            choices = res_json.get('choices', [])
            if choices:
                raw_text = choices[0].get('message', {}).get('content', '').strip()
                parsed = json.loads(raw_text)
                return {
                    'whatTheBugWas': parsed.get('whatTheBugWas', 'Bug detected in original code.'),
                    'whyItHappened': parsed.get('whyItHappened', 'Logic flaw in initial starter code.'),
                    'whyFixWorks': parsed.get('whyFixWorks', 'Your solution resolves the issue.'),
                    'keyConcept': parsed.get('keyConcept', 'Programming Design Patterns'),
                    'alternativeApproaches': parsed.get('alternativeApproaches', 'Functional or declarative patterns.'),
                    'provider': 'openai',
                    'isFallback': False
                }

        raise RuntimeError("OpenAI API returned an invalid explanation response.")

    def generate_personalized_feedback(self, context: dict, prompt: str) -> dict:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.api_key}"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are BuggyMan AI. Return JSON only."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
            "max_tokens": 600
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')

        with urllib.request.urlopen(req, timeout=8.0) as resp:
            body = resp.read().decode('utf-8')
            res_json = json.loads(body)
            choices = res_json.get('choices', [])
            if choices:
                raw_text = choices[0].get('message', {}).get('content', '').strip()
                parsed = json.loads(raw_text)
                return {
                    'debuggingStrengths': parsed.get('debuggingStrengths', ['Quick bug identification']),
                    'areasNeedingImprovement': parsed.get('areasNeedingImprovement', ['Complex state transitions']),
                    'recommendedFocus': parsed.get('recommendedFocus', 'Practice state management and query optimization.'),
                    'learningStyleInsight': parsed.get('learningStyleInsight', 'Consistent problem solving workflow.'),
                    'recommendedChallengeIds': parsed.get('recommendedChallengeIds', ['RE-E01', 'SQL-E01']),
                    'provider': 'openai',
                    'isFallback': False
                }

        raise RuntimeError("OpenAI API returned an invalid personalized feedback response.")

class MockAIProvider(BaseAIProvider):
    """
    Intelligent development fallback provider that generates context-aware progressive hints and diagnostic feedback.
    """
    def generate_hint(self, context: dict, prompt: str) -> dict:
        title = context.get('title', 'Challenge')
        tech = context.get('technology', 'Code')
        suspected = context.get('suspected_component', '')
        user_code = context.get('user_code', '')
        starter_code = context.get('starter_code', '')
        test_results = context.get('test_results', [])
        prev_hints = context.get('previous_hints', [])

        hint_level = context.get('level', len(prev_hints) + 1)
        hint_level = min(3, max(1, hint_level))

        # Level 1: Conceptual Direction
        if hint_level == 1:
            if tech.lower() == 'sql':
                hint_text = "Conceptual Direction: SQL queries filter dataset rows using relational criteria and organize output using clause order (WHERE -> GROUP BY -> HAVING -> ORDER BY). Ensure your query applies filtering before or during aggregation as intended."
            elif tech.lower() in ['react', 'react router', 'javascript']:
                hint_text = "Conceptual Direction: React components render based on state immutability and component prop bindings. Direct variable mutation bypasses React's virtual DOM reconciliation loop."
            elif tech.lower() == 'css':
                hint_text = "Conceptual Direction: Responsive web design relies on CSS media queries overriding grid or flex layout column structures at specific screen width breakpoints."
            else:
                hint_text = f"Conceptual Direction: Focus on algorithmic flow and contract expectations in {suspected or 'main.py'}. Verify function return signatures."

        # Level 2: Specific Guidance
        elif hint_level == 2:
            if tech.lower() == 'sql':
                if 'where' not in user_code.lower() and 'select' in user_code.lower():
                    hint_text = "Specific Guidance: Your query is missing a WHERE clause. Add a WHERE filter matching the requested record status."
                elif 'group by' not in user_code.lower() and 'sum(' in user_code.lower():
                    hint_text = "Specific Guidance: Using aggregate function SUM() requires a GROUP BY clause for all non-aggregated select columns."
                else:
                    hint_text = "Specific Guidance: Review table join conditions and ORDER BY column selection against schema constraints."
            elif tech.lower() in ['react', 'react router', 'javascript']:
                if 'count = count + 1' in user_code:
                    hint_text = "Specific Guidance: Instead of reassigning the state variable directly, call the state setter function provided by useState."
                elif '<a href=' in user_code and 'router' in tech.lower():
                    hint_text = "Specific Guidance: Replace standard HTML <a> elements with React Router's <Link to='...'> component."
                elif 'value=""' in user_code:
                    hint_text = "Specific Guidance: The input value prop is static. Bind it to your state variable so the input reflects user typing."
                else:
                    hint_text = f"Specific Guidance: Inspect event handler binding and state setter logic in {suspected or 'component'}."
            elif tech.lower() == 'css':
                hint_text = f"Specific Guidance: Look closely at your `@media (max-width: 768px)` block in {suspected or 'stylesheet'}. Ensure grid-template-columns changes from 4 columns to 1 column."
            else:
                if test_results:
                    failed = [t for t in test_results if not t.get('passed')]
                    if failed:
                        f = failed[0]
                        hint_text = f"Specific Guidance: Test '{f.get('name')}' failed. Compare expected '{f.get('expected')}' against actual '{f.get('actual')}'."
                    else:
                        hint_text = f"Specific Guidance: Check parameter handling in {suspected or 'main.py'}."
                else:
                    hint_text = f"Specific Guidance: Check function return logic in {suspected or 'main.py'}."

        # Level 3: Point toward Exact Problematic Area
        else:
            if tech.lower() == 'sql':
                hint_text = f"Targeted Area: Look at line 1 in {suspected or 'query.sql'}. The query expression near '{user_code[:30]}...' needs the filter condition applied."
            elif tech.lower() in ['react', 'react router', 'javascript']:
                if 'count = count + 1' in user_code:
                    hint_text = f"Targeted Area: Look inside the click handler function in {suspected or 'Counter.jsx'}. Replace direct assignment `count = count + 1;` with state updater `setCount(prev => prev + 1);`."
                elif '<a href=' in user_code:
                    hint_text = f"Targeted Area: Look at `<a href=\"/dashboard\">` in {suspected or 'Navbar.jsx'}. Replace `<a>` with `<Link to=\"/dashboard\">`."
                else:
                    hint_text = f"Targeted Area: Look at state setter invocation inside {suspected or 'component'}."
            elif tech.lower() == 'css':
                hint_text = f"Targeted Area: Look inside `@media (max-width: 768px)` in {suspected or 'grid.css'}. Change `repeat(4, ...)` to `repeat(1, minmax(0, 1fr))`."
            else:
                hint_text = f"Targeted Area: Inspect the return statement in {suspected or 'main.py'}."

        return {
            'hint': hint_text,
            'level': hint_level,
            'provider': 'mock',
            'isFallback': True
        }

    def generate_feedback(self, context: dict, prompt: str) -> dict:
        tech = context.get('technology', 'Code')
        category = context.get('category', 'Logic')
        user_code = context.get('user_code', '')
        test_results = context.get('test_results', [])
        suspected = context.get('suspected_component', '')

        failed_tests = [t for t in (test_results or []) if not t.get('passed')]
        all_passed = (len(test_results) > 0 and len(failed_tests) == 0)

        if all_passed:
            return {
                'whatIsWrong': 'No bugs detected! Your code passes all verification tests cleanly.',
                'whyItIsWrong': 'The implementation correctly satisfies the requirements and test expectations.',
                'conceptToUnderstand': f'Mastery of {tech} {category}',
                'suggestedDirection': 'Great job! Proceed to the next challenge or explore alternative solution patterns.',
                'provider': 'mock',
                'isFallback': True
            }

        # Analyze failing logic
        if tech.lower() == 'sql':
            what = "The SQL query returns incorrect rows or violates query constraints."
            why = "The query lacks the required WHERE clause filter, returning extra records from the table."
            concept = "SQL Relational Predicates & Data Filtering"
            direction = "Add a WHERE clause specifying the required condition (e.g., status = 'completed')."
        elif tech.lower() in ['react', 'react router', 'javascript']:
            if 'count = count + 1' in user_code:
                what = "Direct React state mutation detected (`count = count + 1`)."
                why = "Reassigning state variables directly does not trigger React component re-renders."
                concept = "React State Immutability & Virtual DOM Reconciliation"
                direction = "Use the state setter function `setCount(prev => prev + 1)` instead of direct assignment."
            elif '<a href=' in user_code:
                what = "Standard HTML <a> tag used for internal routing."
                why = "Standard <a> tags cause browser reloads instead of SPA route transitions."
                concept = "Single Page Application (SPA) Client Routing"
                direction = "Import and use React Router's `<Link to='...'>` component."
            else:
                what = f"Component interaction in {suspected or 'component'} failed verification."
                why = "The UI state or event handler did not produce the expected DOM behavior."
                concept = "React Event Handling & Controlled Inputs"
                direction = "Verify click event bindings and state setter function calls."
        elif tech.lower() == 'css':
            what = "Responsive layout rules failed for mobile screen widths."
            why = "The grid layout columns remained hardcoded to 4 columns inside the max-width media query."
            concept = "CSS Media Queries & Fluid Grid Layouts"
            direction = "Change `grid-template-columns: repeat(4, ...)` to `repeat(1, minmax(0, 1fr))` inside `@media (max-width: 768px)`."
        else:
            what = f"Logic error in {suspected or 'main.py'}."
            why = "Function return values do not match test case assertions."
            concept = "Functional Return Contracts"
            direction = "Check conditional logic and return statement calculations."

        return {
            'whatIsWrong': what,
            'whyItIsWrong': why,
            'conceptToUnderstand': concept,
            'suggestedDirection': direction,
            'provider': 'mock',
            'isFallback': True
        }

    def generate_explanation(self, context: dict, prompt: str) -> dict:
        tech = context.get('technology', 'Code')
        category = context.get('category', 'Logic')
        suspected = context.get('suspected_component', '')

        if tech.lower() == 'sql':
            bug = "The original query omitted required filtering or grouping predicates."
            happened = "Without filtering, relational database engines evaluate queries over the complete table, returning unwanted records."
            fix = "Adding explicit WHERE or GROUP BY constraints limits query evaluation to the matching dataset."
            concept = "Relational Query Evaluation & Index Optimization"
            alt = "Using Common Table Expressions (CTEs) or database views for complex subquery logic."
        elif tech.lower() in ['react', 'react router', 'javascript']:
            bug = "The component directly mutated local state or used standard HTML <a> elements."
            happened = "Direct mutation skips React's virtual DOM reconciliation queue, leading to stale UI renders."
            fix = "Using immutable state setters or React Router <Link> tags queues React state transitions cleanly."
            concept = "React Immutability & Declarative UI Rendering"
            alt = "Using useReducer or custom hook abstractions for multi-step state management."
        elif tech.lower() == 'css':
            bug = "The grid layout columns were hardcoded across desktop and mobile breakpoints."
            happened = "Failing to adapt grid-template-columns causes multi-column grid overflow on narrow screen width viewports."
            fix = "Overriding grid columns to single column inside `@media (max-width: 768px)` ensures mobile responsiveness."
            concept = "CSS Media Queries & Fluid Responsive Design"
            alt = "Using CSS Flexbox wrap (`flex-wrap: wrap`) or `auto-fit` minmax grid templates."
        else:
            bug = f"Function logic in {suspected or 'main.py'} returned incorrect values."
            happened = "The original control flow failed to handle boundary edge case parameters."
            fix = "Your updated control flow evaluates arguments correctly and returns expected contracts."
            concept = f"{tech} Function Contracts & Logic Design"
            alt = "Using pattern matching, guard clauses, or unit test assertion guards."

        return {
            'whatTheBugWas': bug,
            'whyItHappened': happened,
            'whyFixWorks': fix,
            'keyConcept': concept,
            'alternativeApproaches': alt,
            'provider': 'mock',
            'isFallback': True
        }

    def generate_personalized_feedback(self, context: dict, prompt: str) -> dict:
        accuracy = context.get('accuracy_rate', 0)
        solved = context.get('solved_count', 0)

        strengths = [
            "Quick diagnosis of fundamental syntax and query logic",
            "Consistent execution velocity across Easy and Medium arenas"
        ]

        growth = [
            "React component state immutability patterns (`useState` functional updaters)",
            "Complex SQL joins and GROUP BY aggregate filters"
        ]

        rec_focus = "Focus on React State & Lifecycle and SQL Aggregation challenges to eliminate state mutation and query syntax errors."
        style = f"Demonstrates solid problem-solving flow with {accuracy}% accuracy across {solved} solved challenges. Benefits from structured hint progression on multi-file React component bugs."
        rec_ids = ["RE-E01", "SQL-E01", "RE-M01"]

        return {
            'debuggingStrengths': strengths,
            'areasNeedingImprovement': growth,
            'recommendedFocus': rec_focus,
            'learningStyleInsight': style,
            'recommendedChallengeIds': rec_ids,
            'provider': 'mock',
            'isFallback': True
        }
