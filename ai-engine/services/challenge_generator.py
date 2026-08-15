import os
import json
import random
import requests

PROMPTS_TEMPLATES = {
    'React': {
        'Easy': [
            {
                'title': 'Fix Uncontrolled Component Warning',
                'description': 'Input value initializes as undefined causing React to throw an uncontrolled to controlled input warning.',
                'category': 'Form Controls',
                'time_estimate': '10 mins',
                'points': 100,
                'files': [{
                    'name': 'InputForm.jsx',
                    'content': "import React, { useState } from 'react';\n\nexport default function InputForm() {\n  // BUG: initial value is undefined!\n  const [text, setText] = useState();\n\n  return (\n    <input \n      value={text}\n      onChange={(e) => setText(e.target.value)}\n      className=\"p-2 border rounded\"\n    />\n  );\n}"
                }],
                'test_cases': [
                    {'id': 1, 'name': 'Input starts with empty string', 'input': '', 'expected': 'value=""', 'passed': False}
                ],
                'bug_signature': 'const [text, setText] = useState();',
                'suspected_component': 'useState initialization in InputForm.jsx',
                'ai_suggestions': [
                    "React inputs require initial state to not be undefined. Pass `useState('')` instead."
                ]
            },
            {
                'title': 'Fix Infinite Re-render Loop',
                'description': 'Calling setState directly inside component body causes infinite re-render loops.',
                'category': 'State & Lifecycle',
                'time_estimate': '10 mins',
                'points': 100,
                'files': [{
                    'name': 'CounterBadge.jsx',
                    'content': "import React, { useState } from 'react';\n\nexport default function CounterBadge({ initialCount }) {\n  const [count, setCount] = useState(0);\n\n  // BUG: Direct state mutation during render!\n  if (count < initialCount) {\n    setCount(initialCount);\n  }\n\n  return <span className=\"badge\">Count: {count}</span>;\n}"
                }],
                'test_cases': [
                    {'id': 1, 'name': 'Render without crashing', 'input': 'initialCount=5', 'expected': 'Count: 5', 'passed': False}
                ],
                'bug_signature': 'if (count < initialCount) {\n    setCount(initialCount);\n  }',
                'suspected_component': 'Direct setCount call in render phase',
                'ai_suggestions': [
                    "Move state updates inside `useEffect` or compute derived state directly during render without calling `setCount`."
                ]
            }
        ],
        'Medium': [
            {
                'title': 'Fix Stale Closure in setInterval Hook',
                'description': 'The timer hook reads a stale count value because interval callback captures original closure.',
                'category': 'Hooks & Closures',
                'time_estimate': '15 mins',
                'points': 150,
                'files': [{
                    'name': 'useTimer.js',
                    'content': "import { useState, useEffect } from 'react';\n\nexport default function useTimer() {\n  const [seconds, setSeconds] = useState(0);\n\n  useEffect(() => {\n    const timer = setInterval(() => {\n      // BUG: Stale state reference in interval closure!\n      setSeconds(seconds + 1);\n    }, 1000);\n    return () => clearInterval(timer);\n  }, []);\n\n  return seconds;\n}"
                }],
                'test_cases': [
                    {'id': 1, 'name': 'Timer increments correctly past 1s', 'input': 'wait 3s', 'expected': 'seconds: 3', 'passed': False}
                ],
                'bug_signature': 'setSeconds(seconds + 1);',
                'suspected_component': 'setSeconds in useTimer.js',
                'ai_suggestions': [
                    "Use functional state updater: `setSeconds(prev => prev + 1)` to avoid reading stale variables from closure scope."
                ]
            }
        ],
        'Hard': [
            {
                'title': 'Fix React Context Re-render Thrashing',
                'description': 'Passing an unmemoized object literal into Context Provider causes all consumers to re-render on every parent tick.',
                'category': 'Performance Optimization',
                'time_estimate': '25 mins',
                'points': 300,
                'files': [{
                    'name': 'UserContextProvider.jsx',
                    'content': "import React, { useState, createContext } from 'react';\n\nexport className = 'UserContext';\nexport const UserContext = createContext();\n\nexport default function UserContextProvider({ children }) {\n  const [user, setUser] = useState({ name: 'Alex' });\n  const [theme, setTheme] = useState('dark');\n\n  // BUG: Creating new object reference on every render!\n  const contextValue = { user, setUser, theme, setTheme };\n\n  return (\n    <UserContext.Provider value={contextValue}>\n      {children}\n    </UserContext.Provider>\n  );\n}"
                }],
                'test_cases': [
                    {'id': 1, 'name': 'Memoized context value', 'input': 'parent state update', 'expected': 'reference stable', 'passed': False}
                ],
                'bug_signature': 'const contextValue = { user, setUser, theme, setTheme };',
                'suspected_component': 'contextValue definition in UserContextProvider.jsx',
                'ai_suggestions': [
                    "Wrap `contextValue` in `useMemo(() => ({ user, setUser, theme, setTheme }), [user, theme])`."
                ]
            }
        ]
    },
    'Django': {
        'Easy': [
            {
                'title': 'Fix Missing Related Name in ForeignKey',
                'description': 'Reverse relationship query crashes because related_name is missing or colliding.',
                'category': 'ORM Models',
                'time_estimate': '10 mins',
                'points': 100,
                'files': [{
                    'name': 'models.py',
                    'content': "from django.db import models\nfrom django.contrib.auth import get_user_model\n\nUser = get_user_model()\n\nclass Post(models.Model):\n    title = models.CharField(max_length=200)\n    # BUG: Duplicate related_name causes clash!\n    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')\n    editor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')\n"
                }],
                'test_cases': [
                    {'id': 1, 'name': 'Django check passes without clashes', 'input': 'manage.py check', 'expected': '0 errors', 'passed': False}
                ],
                'bug_signature': "editor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')",
                'suspected_component': 'editor ForeignKey in models.py',
                'ai_suggestions': [
                    "Give unique related names for `author` and `editor`, e.g. `related_name='authored_posts'` and `related_name='edited_posts'`."
                ]
            }
        ],
        'Medium': [
            {
                'title': 'Fix N+1 Query Problem in Django View',
                'description': 'Listing posts triggers N+1 database queries when accessing author information.',
                'category': 'Database Optimization',
                'time_estimate': '15 mins',
                'points': 150,
                'files': [{
                    'name': 'views.py',
                    'content': "from rest_framework.decorators import api_view\nfrom rest_framework.response import Response\nfrom .models import Post\nfrom .serializers import PostSerializer\n\n@api_view(['GET'])\ndef list_posts(request):\n    # BUG: missing select_related for author!\n    posts = Post.objects.all()\n    serializer = PostSerializer(posts, many=True)\n    return Response(serializer.data)"
                }],
                'test_cases': [
                    {'id': 1, 'name': 'Query count remains under 2 queries', 'input': 'GET /posts', 'expected': '1 query', 'passed': False}
                ],
                'bug_signature': 'posts = Post.objects.all()',
                'suspected_component': 'Post.objects.all() in list_posts',
                'ai_suggestions': [
                    "Use `Post.objects.select_related('author').all()` to join author fields in a single SQL query."
                ]
            }
        ],
        'Hard': [
            {
                'title': 'Fix Race Condition in Inventory Decrement',
                'description': 'Concurrent purchase requests lead to negative stock levels due to un-isolated database reads and writes.',
                'category': 'Concurrency & Transactions',
                'time_estimate': '25 mins',
                'points': 300,
                'files': [{
                    'name': 'views.py',
                    'content': "from rest_framework.decorators import api_view\nfrom rest_framework.response import Response\nfrom django.db.models import F\nfrom .models import Product\n\n@api_view(['POST'])\ndef purchase_product(request, pk):\n    # BUG: Race condition on quantity update!\n    product = Product.objects.get(pk=pk)\n    if product.stock > 0:\n        product.stock = product.stock - 1\n        product.save()\n        return Response({'status': 'success'})\n    return Response({'error': 'Out of stock'}, status=400)"
                }],
                'test_cases': [
                    {'id': 1, 'name': 'Atomic update under high concurrency', 'input': '10 concurrent posts', 'expected': 'stock >= 0', 'passed': False}
                ],
                'bug_signature': 'product.stock = product.stock - 1\n        product.save()',
                'suspected_component': 'stock assignment in purchase_product',
                'ai_suggestions': [
                    "Use F expressions or select_for_update(): `Product.objects.filter(pk=pk, stock__gt=0).update(stock=F('stock') - 1)`."
                ]
            }
        ]
    }
}

class AIChallengeGenerator:
    @staticmethod
    def generate_challenge(difficulty='Easy', technology='React', category=None):
        """
        Generates a new challenge using Gemini API if key is present,
        or uses dynamic AI challenge template pool.
        """
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            try:
                prompt = f"""Generate a realistic software bug coding challenge for {technology} at {difficulty} difficulty level.
Return JSON ONLY with this exact schema:
{{
  "title": "short title",
  "description": "detailed problem statement",
  "difficulty": "{difficulty}",
  "technology": "{technology}",
  "category": "{category or 'General'}",
  "timeEstimate": "15 mins",
  "points": {100 if difficulty == 'Easy' else 150 if difficulty == 'Medium' else 300},
  "files": [{{"name": "filename", "content": "source code with bug"}}],
  "testCases": [{{"id": 1, "name": "test case name", "input": "", "expected": "", "passed": false}}],
  "bugSignature": "exact line of code containing the bug",
  "suspectedComponent": "component name",
  "solutionCode": "fixed working code solving the bug",
  "aiSuggestions": ["hint 1", "hint 2"]
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
                print(f"Gemini API call failed, falling back to dynamic generator: {e}")

        # Fallback to rich dynamic template pool
        tech_pool = PROMPTS_TEMPLATES.get(technology, PROMPTS_TEMPLATES['React'])
        diff_pool = tech_pool.get(difficulty, tech_pool['Easy'])
        template = random.choice(diff_pool)
        
        random_id = random.randint(100, 999)
        challenge = dict(template)
        challenge['title'] = f"{challenge['title']} #{random_id}"
        challenge['testCases'] = challenge.get('testCases') or challenge.get('test_cases') or []
        challenge['test_cases'] = challenge['testCases']
        challenge['bugSignature'] = challenge.get('bugSignature') or challenge.get('bug_signature') or ''
        challenge['bug_signature'] = challenge['bugSignature']
        challenge['suspectedComponent'] = challenge.get('suspectedComponent') or challenge.get('suspected_component') or ''
        challenge['suspected_component'] = challenge['suspectedComponent']
        challenge['aiSuggestions'] = challenge.get('aiSuggestions') or challenge.get('ai_suggestions') or []
        challenge['ai_suggestions'] = challenge['aiSuggestions']
        challenge['timeEstimate'] = challenge.get('timeEstimate') or challenge.get('time_estimate') or '15 mins'

        # Provide default solutionCode if missing
        if 'solution_code' in challenge:
            challenge['solutionCode'] = challenge['solution_code']
        elif 'files' in challenge and challenge['files']:
            starter = challenge['files'][0].get('content', '')
            challenge['solutionCode'] = starter.replace("useState();", "useState('');").replace("setSeconds(seconds + 1);", "setSeconds(prev => prev + 1);")
        else:
            challenge['solutionCode'] = "SELECT * FROM orders WHERE status = 'completed';"

        return challenge
