import time
import sys
import os
from django.db.models import Q
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import User, Challenge, Notification, Submission, ChallengeReport
from .auth import generate_jwt_token
from .evaluator.engine import EvaluationEngine

evaluation_engine = EvaluationEngine()


# Add ai-engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../ai-engine'))
from services.challenge_generator import AIChallengeGenerator
from services.bug_injector import BugInjector
from buggyman.ml.analytics_collector import AnalyticsCollector
from buggyman.ml.skill_profiler import SkillProfiler
from buggyman.ml.difficulty_predictor import DifficultyPredictor
from buggyman.ml.recommender import ChallengeRecommender
from buggyman.ml.adaptive_difficulty import AdaptiveDifficultyManager
from buggyman.ml.weakness_detector import WeaknessDetector
from buggyman.ml.learning_path import LearningPathGenerator
from buggyman.throttling import apply_rate_limit
from buggyman.logger import log_event, log_security_event, log_evaluator_event, log_error_event
from buggyman.backup import BackupManager


def get_authenticated_user(request):
    if request.user and request.user.is_authenticated:
        return request.user
    return None

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    lim = apply_rate_limit(request, 'auth', limit=10)
    if lim:
        return lim
    data = request.data
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=email).first()
    if not user:
        user = User.objects.filter(username=email).first()

    if user and user.check_password(password):
        token = generate_jwt_token(user)
        return Response({'token': token, 'user': user.to_dict()})
    
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    lim = apply_rate_limit(request, 'auth', limit=10)
    if lim:
        return lim
    data = request.data
    display_name = data.get('displayName', '')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    bio = data.get('bio', '')
    country = data.get('country', '')
    timezone = data.get('timezone', '')
    avatar = data.get('avatar', 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150')
    theme = data.get('theme', 'dark')
    accent_color = data.get('accentColor', 'blue')
    interests = data.get('interests', [])
    notifications_config = data.get('notificationsConfig', {})

    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    if not username:
        username = email.split('@')[0]

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username is already taken'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email is already registered'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(password)
    except ValidationError as e:
        return Response({'error': ', '.join(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

    name_parts = display_name.strip().split(' ', 1) if display_name else []
    first_name = name_parts[0] if name_parts else ''
    last_name = name_parts[1] if len(name_parts) > 1 else ''

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        display_name=display_name,
        college=data.get('college', 'State Technical University'),
        bio=bio,
        avatar=avatar,
        theme=theme,
        accent_color=accent_color,
        country=country,
        timezone=timezone,
        interests=interests,
        notifications_config=notifications_config,
        skills={'React': 75, 'Django': 65, 'NodeJS': 50, 'CSS': 70},
        activities=[{
            'id': int(time.time()),
            'text': 'Joined BuggyMan community',
            'time': 'Just now',
            'xp': 50
        }],
        badges=[{
            'name': 'First Bug Defeated',
            'desc': 'Resolved your first bug',
            'icon': '🐞',
            'date': 'Today'
        }]
    )

    token = generate_jwt_token(user)
    return Response({'token': token, 'user': user.to_dict()})

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        return Response(user.to_dict())

    if request.method == 'PUT':
        data = request.data
        if 'username' in data and data['username'] != user.username:
            if User.objects.filter(username=data['username']).exclude(id=user.id).exists():
                return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)
            user.username = data['username']
        if 'email' in data and data['email'] != user.email:
            if User.objects.filter(email=data['email']).exclude(id=user.id).exists():
                return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)
            user.email = data['email']
        if 'display_name' in data:
            user.display_name = data['display_name']
            parts = data['display_name'].strip().split(' ', 1)
            user.first_name = parts[0] if parts else ''
            user.last_name = parts[1] if len(parts) > 1 else ''
        if 'bio' in data:
            user.bio = data['bio']
        if 'college' in data:
            user.college = data['college']
        if 'avatar' in data:
            user.avatar = data['avatar']
        if 'theme' in data:
            user.theme = data['theme']
        if 'accent_color' in data:
            user.accent_color = data['accent_color']
        if 'country' in data:
            user.country = data['country']
        if 'timezone' in data:
            user.timezone = data['timezone']
        if 'interests' in data:
            user.interests = data['interests']
        if 'notifications_config' in data:
            user.notifications_config = data['notifications_config']
        if 'password' in data and data['password']:
            try:
                validate_password(data['password'], user)
            except ValidationError as e:
                return Response({'error': ', '.join(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(data['password'])
        if 'skills' in data:
            user.skills = data['skills']
        user.save()
        return Response(user.to_dict())

@api_view(['GET'])
@permission_classes([AllowAny])
def challenges_list_view(request):
    # Ensure catalog items are seeded in database if catalog challenges missing
    if not Challenge.objects.filter(title__startswith='[RE-').exists():
        for key, item in SPECIAL_CHALLENGE_CATALOG.items():
            Challenge.objects.get_or_create(
                title=f"[{key}] {item['title']}",
                defaults={
                    'description': item['description'],
                    'difficulty': item['difficulty'],
                    'technology': item['technology'],
                    'category': item['category'],
                    'time_estimate': item['time_estimate'],
                    'points': item['points'],
                    'files': item['files'],
                    'test_cases': item['test_cases'],
                    'bug_signature': item['bug_signature'],
                    'suspected_component': item['suspected_component']
                }
            )

    user = get_authenticated_user(request)
    queryset = Challenge.objects.all().order_by('id')

    status_filter = request.query_params.get('status', '').strip()
    if not is_admin_user(user):
        queryset = queryset.filter(status='published')
    elif status_filter and status_filter.lower() != 'all':
        queryset = queryset.filter(status__iexact=status_filter)

    difficulty = request.query_params.get('difficulty', '').strip()
    technology = request.query_params.get('technology', '').strip()
    category = request.query_params.get('category', '').strip()
    arena = request.query_params.get('arena', '').strip() or request.query_params.get('type', '').strip()
    search = request.query_params.get('search', '').strip() or request.query_params.get('q', '').strip()

    if difficulty and difficulty.lower() != 'all':
        queryset = queryset.filter(difficulty__iexact=difficulty)
    if technology and technology.lower() != 'all':
        queryset = queryset.filter(technology__iexact=technology)
    if category and category.lower() != 'all':
        queryset = queryset.filter(category__iexact=category)

    if arena and arena.lower() != 'all':
        arena_low = arena.lower()
        if arena_low in ('sql', 'database'):
            queryset = queryset.filter(Q(technology__iexact='SQL') | Q(title__startswith='[SQL-'))
        elif arena_low in ('frontend', 'studio', 'design'):
            queryset = queryset.filter(
                Q(technology__in=['React', 'React Router', 'Web', 'CSS', 'HTML', 'Styling', 'Controlled Components']) |
                Q(title__startswith='[RE-')
            )
        elif arena_low in ('debugging', 'backend', 'code'):
            queryset = queryset.filter(technology__in=['Python', 'Django', 'NodeJS', 'JavaScript', 'Backend', 'FastAPI'])
    elif not search:
        queryset = queryset.exclude(title__startswith='[SQL-').exclude(title__startswith='[RE-')

    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(category__icontains=search) |
            Q(technology__icontains=search)
        )

    challenges = [c.to_dict() for c in queryset]
    return Response(challenges)

SPECIAL_CHALLENGE_CATALOG = {
    # SQL LAB CHALLENGES
    'SQL-E01': {
        'title': 'Incorrect WHERE clause returns extra records',
        'description': 'A SELECT query returns all rows from the orders table because the WHERE clause filtering for completed status is missing.',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Query',
        'time_estimate': '10 mins',
        'points': 100,
        'expected_query': "SELECT * FROM orders WHERE status = 'completed';",
        'ordered_comparison': False,
        'files': [
            {
                'name': 'schema.sql',
                'content': "CREATE TABLE orders (id INT, customer_id INT, amount DECIMAL(10,2), status VARCHAR(20));\nINSERT INTO orders VALUES (1, 101, 150.00, 'completed'), (2, 102, 200.00, 'pending'), (3, 101, 50.00, 'cancelled'), (4, 103, 300.00, 'completed');"
            },
            {
                'name': 'query.sql',
                'content': "-- BUG: Missing required WHERE condition\nSELECT * FROM orders;"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Filters completed orders correctly', 'input': '', 'expected': "WHERE status = 'completed'", 'passed': False}],
        'bug_signature': 'SELECT * FROM orders;',
        'suspected_component': 'query.sql'
    },
    'SQL-E02': {
        'title': 'ORDER BY sorts incorrectly',
        'description': 'Results are sorted in the wrong order because the ORDER BY uses the wrong field or missing direction.',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Sorting',
        'time_estimate': '10 mins',
        'points': 100,
        'expected_query': "SELECT name, price FROM products ORDER BY price ASC;",
        'ordered_comparison': True,
        'files': [
            {
                'name': 'schema.sql',
                'content': "CREATE TABLE products (id INT, name VARCHAR(50), price DECIMAL(10,2), created_at TIMESTAMP);\nINSERT INTO products VALUES (1, 'Laptop', 999.99, '2026-01-01'), (2, 'Mouse', 25.00, '2026-01-02'), (3, 'Keyboard', 75.00, '2026-01-03');"
            },
            {
                'name': 'report.sql',
                'content': "-- BUG: ORDER BY uses wrong column\nSELECT name, price FROM products ORDER BY created_at;"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Orders products by price', 'input': '', 'expected': 'ORDER BY price', 'passed': False}],
        'bug_signature': 'ORDER BY created_at;',
        'suspected_component': 'report.sql'
    },
    'SQL-E03': {
        'title': 'Missing PRIMARY KEY',
        'description': 'A table has no PRIMARY KEY constraint, causing duplicate rows and unreliable joins.',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Schema',
        'time_estimate': '10 mins',
        'points': 100,
        'expected_query': "CREATE TABLE users (id INT PRIMARY KEY, username VARCHAR(50), email VARCHAR(100));",
        'ordered_comparison': False,
        'files': [
            {
                'name': 'schema.sql',
                'content': "-- BUG: users table defined without a primary key\nCREATE TABLE users (\n  username VARCHAR(50),\n  email VARCHAR(100)\n);\nINSERT INTO users VALUES ('alice', 'alice@test.com'), ('bob', 'bob@test.com');"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Defines a primary key', 'input': '', 'expected': 'PRIMARY KEY', 'passed': False}],
        'bug_signature': 'CREATE TABLE users ( username VARCHAR(50), email VARCHAR(100) );',
        'suspected_component': 'schema.sql'
    },
    'SQL-E04': {
        'title': 'Duplicate usernames allowed',
        'description': 'The users table lacks a UNIQUE constraint on username, allowing duplicate accounts.',
        'difficulty': 'Easy',
        'technology': 'SQL',
        'category': 'Constraints',
        'time_estimate': '10 mins',
        'points': 100,
        'expected_query': "CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(50) UNIQUE, email VARCHAR(100));",
        'ordered_comparison': False,
        'files': [
            {
                'name': 'schema.sql',
                'content': "-- BUG: Missing UNIQUE constraint on username\nCREATE TABLE users (\n  id INTEGER PRIMARY KEY,\n  username VARCHAR(50),\n  email VARCHAR(100)\n);\nINSERT INTO users VALUES (1, 'john_doe', 'john@test.com'), (2, 'jane_doe', 'jane@test.com');"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Username uniqueness enforced', 'input': '', 'expected': 'UNIQUE', 'passed': False}],
        'bug_signature': 'username VARCHAR(50),',
        'suspected_component': 'schema.sql'
    },
    'SQL-M01': {
        'title': 'GROUP BY omits aggregate column',
        'description': 'A report query fails because the SELECT list includes a non-aggregated column without a corresponding GROUP BY expression.',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Aggregation',
        'time_estimate': '15 mins',
        'points': 150,
        'expected_query': "SELECT region, SUM(amount) FROM sales GROUP BY region;",
        'ordered_comparison': False,
        'files': [
            {
                'name': 'schema.sql',
                'content': "CREATE TABLE sales (id INT, region VARCHAR(50), amount DECIMAL(10,2));\nINSERT INTO sales VALUES (1, 'North', 500.00), (2, 'South', 300.00), (3, 'North', 700.00);"
            },
            {
                'name': 'sales_report.sql',
                'content': "-- BUG: Missing GROUP BY column\nSELECT region, SUM(amount) FROM sales;"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Uses GROUP BY correctly', 'input': '', 'expected': 'GROUP BY region', 'passed': False}],
        'bug_signature': 'SELECT region, SUM(amount) FROM sales;',
        'suspected_component': 'sales_report.sql'
    },
    'SQL-M02': {
        'title': 'JOIN duplicates rows unexpectedly',
        'description': 'A multi-table join returns duplicate records because the join condition is too broad or the join type is incorrect.',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Joins',
        'time_estimate': '15 mins',
        'points': 150,
        'expected_query': "SELECT o.id, c.name FROM orders o JOIN customers c ON o.customer_id = c.id;",
        'ordered_comparison': False,
        'files': [
            {
                'name': 'schema.sql',
                'content': "CREATE TABLE customers (id INT PRIMARY KEY, name VARCHAR(50));\nCREATE TABLE orders (id INT PRIMARY KEY, customer_id INT, amount DECIMAL(10,2));\nINSERT INTO customers VALUES (1, 'Alice'), (2, 'Bob');\nINSERT INTO orders VALUES (101, 1, 150.00), (102, 2, 250.00);"
            },
            {
                'name': 'nested_join.sql',
                'content': "-- BUG: Join missing proper ON condition\nSELECT o.id, c.name FROM orders o JOIN customers c;"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Joins with explicit conditions', 'input': '', 'expected': 'ON o.customer_id = c.id', 'passed': False}],
        'bug_signature': 'SELECT o.id, c.name FROM orders o JOIN customers c;',
        'suspected_component': 'nested_join.sql'
    },
    'SQL-M03': {
        'title': 'HAVING used instead of WHERE',
        'description': 'A filter on aggregated results is applied in the wrong clause, so the final output is incorrect.',
        'difficulty': 'Medium',
        'technology': 'SQL',
        'category': 'Filtering',
        'time_estimate': '15 mins',
        'points': 150,
        'expected_query': "SELECT product_id, SUM(quantity) FROM orders WHERE quantity > 10 GROUP BY product_id;",
        'ordered_comparison': False,
        'files': [
            {
                'name': 'schema.sql',
                'content': "CREATE TABLE orders (id INT, product_id INT, quantity INT);\nINSERT INTO orders VALUES (1, 101, 15), (2, 102, 5), (3, 101, 20);"
            },
            {
                'name': 'aggregate.sql',
                'content': "-- BUG: HAVING should be used after aggregation\nSELECT product_id, SUM(quantity) FROM orders HAVING quantity > 10;"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Uses WHERE before aggregation', 'input': '', 'expected': 'WHERE quantity > 10', 'passed': False}],
        'bug_signature': 'HAVING quantity > 10;',
        'suspected_component': 'aggregate.sql'
    },
    'SQL-H01': {
        'title': 'Window function partitions incorrectly',
        'description': 'A ranking query uses the wrong PARTITION BY clause, causing each row to be compared against the wrong group.',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Window Functions',
        'time_estimate': '25 mins',
        'points': 250,
        'expected_query': "SELECT *, RANK() OVER (PARTITION BY department ORDER BY salary DESC) FROM employee_metrics;",
        'ordered_comparison': False,
        'files': [
            {
                'name': 'schema.sql',
                'content': "CREATE TABLE employee_metrics (id INT, name VARCHAR(50), department VARCHAR(50), salary DECIMAL(10,2));\nINSERT INTO employee_metrics VALUES (1, 'Alice', 'Eng', 90000), (2, 'Bob', 'Eng', 110000), (3, 'Charlie', 'HR', 70000);"
            },
            {
                'name': 'ranking.sql',
                'content': "-- BUG: Window function missing PARTITION BY\nSELECT *, RANK() OVER (ORDER BY salary DESC) FROM employee_metrics;"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Partitions by correct field', 'input': '', 'expected': 'PARTITION BY department', 'passed': False}],
        'bug_signature': 'RANK() OVER (ORDER BY salary DESC)',
        'suspected_component': 'ranking.sql'
    },
    'SQL-H02': {
        'title': 'Recursive CTE repeats indefinitely',
        'description': 'A recursive CTE does not include a termination condition, producing an endless recursion loop.',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'CTE',
        'time_estimate': '25 mins',
        'points': 250,
        'expected_query': "WITH RECURSIVE manager_path AS ( SELECT id, manager_id FROM org_chart WHERE manager_id IS NULL UNION ALL SELECT o.id, o.manager_id FROM org_chart o JOIN manager_path mp ON o.manager_id = mp.id ) SELECT * FROM manager_path;",
        'ordered_comparison': False,
        'files': [
            {
                'name': 'schema.sql',
                'content': "CREATE TABLE org_chart (id INT PRIMARY KEY, manager_id INT);\nINSERT INTO org_chart VALUES (1, NULL), (2, 1), (3, 2);"
            },
            {
                'name': 'hierarchy.sql',
                'content': "-- BUG: Recursive CTE missing termination condition\nWITH RECURSIVE manager_path AS (\n  SELECT id, manager_id FROM org_chart\n  UNION ALL\n  SELECT o.id, o.manager_id FROM org_chart o JOIN manager_path mp ON o.manager_id = mp.id\n)\nSELECT * FROM manager_path;"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Adds termination condition', 'input': '', 'expected': 'WHERE manager_id IS NULL', 'passed': False}],
        'bug_signature': 'SELECT id, manager_id FROM org_chart UNION ALL',
        'suspected_component': 'hierarchy.sql'
    },
    'SQL-H03': {
        'title': 'Index hint prevents plan reuse',
        'description': 'A query uses the wrong index hint and performs a full table scan even though a better index exists.',
        'difficulty': 'Hard',
        'technology': 'SQL',
        'category': 'Performance',
        'time_estimate': '25 mins',
        'points': 250,
        'expected_query': "SELECT * FROM events FORCE INDEX (idx_event_date) WHERE event_date > '2026-01-01';",
        'ordered_comparison': False,
        'files': [
            {
                'name': 'schema.sql',
                'content': "CREATE TABLE events (id INT, event_name VARCHAR(50), event_date DATE);\nINSERT INTO events VALUES (1, 'Login', '2026-01-02'), (2, 'Purchase', '2026-01-03');"
            },
            {
                'name': 'query.sql',
                'content': "-- BUG: Wrong index hint forces an inefficient scan\nSELECT * FROM events FORCE INDEX (idx_old_date) WHERE event_date > '2026-01-01';"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Uses correct index hint', 'input': '', 'expected': 'FORCE INDEX (idx_event_date)', 'passed': False}],
        'bug_signature': 'FORCE INDEX (idx_old_date)',
        'suspected_component': 'query.sql'
    },

    # FRONTEND STUDIO / REACT / CSS CHALLENGES
    'RE-E01': {
        'title': 'Counter state doesn\'t update',
        'description': 'A React counter component fails to re-render because state is mutated directly rather than updated immutably.',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'State',
        'time_estimate': '10 mins',
        'points': 100,
        'files': [
            {
                'name': 'Counter.jsx',
                'content': "import React, { useState } from 'react';\n\nexport default function Counter() {\n  const [count, setCount] = useState(0);\n\n  const increment = () => {\n    count = count + 1; // BUG: Mutating state directly\n    setCount(count);\n  };\n\n  return (\n    <div className=\"counter-card\">\n      <h2>Interactive Counter Widget</h2>\n      <p>Current count: <strong>{count}</strong></p>\n      <button onClick={increment}>Increment</button>\n    </div>\n  );\n}"
            },
            {
                'name': 'styles.css',
                'content': ".counter-card { padding: 20px; background: #1e293b; border-radius: 12px; border: 1px solid #334155; text-align: center; }\n.counter-card h2 { margin-top: 0; color: #38bdf8; }\n.counter-card button { background: #0284c7; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; }\n.counter-card button:hover { background: #0369a1; }"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Uses state setter correctly', 'input': '', 'expected': 'setCount(count + 1)', 'passed': False}],
        'bug_signature': 'count = count + 1;',
        'suspected_component': 'Counter.jsx'
    },
    'RE-E02': {
        'title': 'Form validation never displays errors',
        'description': 'A form validation handler computes errors correctly but the UI never renders them.',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'Forms',
        'time_estimate': '10 mins',
        'points': 100,
        'files': [
            {
                'name': 'SignupForm.jsx',
                'content': "import React, { useState } from 'react';\n\nexport default function SignupForm() {\n  const [errors] = useState({});\n\n  const handleSubmit = (e) => {\n    e.preventDefault();\n  };\n\n  return (\n    <form className=\"form-card\" onSubmit={handleSubmit}>\n      <h3>Account Registration</h3>\n      <input type=\"email\" placeholder=\"Enter your email\" />\n      <button type=\"submit\">Submit</button>\n    </form>\n  );\n}"
            },
            {
                'name': 'form-styles.css',
                'content': ".form-card { padding: 20px; background: #1e293b; border-radius: 12px; border: 1px solid #334155; display: flex; flex-direction: column; gap: 12px; max-width: 320px; }\n.form-card input { background: #0f172a; color: white; border: 1px solid #475569; padding: 8px 12px; border-radius: 6px; }\n.error-msg { color: #f43f5e; font-size: 12px; margin-top: 4px; }"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Renders validation messages', 'input': '', 'expected': 'errors.email', 'passed': False}],
        'bug_signature': 'const [errors] = useState({});',
        'suspected_component': 'SignupForm.jsx'
    },
    'RE-E03': {
        'title': 'Navbar links don\'t navigate',
        'description': 'React Router links appear in the navigation bar but clicks do not change routes due to a missing Link component or wrong path.',
        'difficulty': 'Easy',
        'technology': 'React Router',
        'category': 'React Router',
        'time_estimate': '10 mins',
        'points': 100,
        'files': [
            {
                'name': 'Navbar.jsx',
                'content': "import React from 'react';\n\nexport default function Navbar() {\n  return (\n    <nav className=\"nav-bar\">\n      <a href=\"/dashboard\">Dashboard</a>\n      <a href=\"/profile\">Profile</a>\n    </nav>\n  );\n}"
            },
            {
                'name': 'nav.css',
                'content': ".nav-bar { display: flex; gap: 16px; padding: 12px 20px; background: #1e293b; border-radius: 8px; }\n.nav-bar a { color: #38bdf8; text-decoration: none; font-weight: 500; }\n.nav-bar a:hover { color: #7dd3fc; }"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Uses React Router Link', 'input': '', 'expected': '<Link', 'passed': False}],
        'bug_signature': '<a href="/dashboard">',
        'suspected_component': 'Navbar.jsx'
    },
    'RE-E04': {
        'title': 'Button click handler not working',
        'description': 'A button render is fine but the onClick callback never fires due to incorrect binding or missing handler reference.',
        'difficulty': 'Easy',
        'technology': 'React',
        'category': 'Events',
        'time_estimate': '10 mins',
        'points': 100,
        'files': [
            {
                'name': 'ActionButton.jsx',
                'content': "import React from 'react';\n\nexport default function ActionButton() {\n  function handleClick() {\n    console.log('clicked');\n  }\n\n  return <button className=\"action-btn\" onClick={handleclck}>Click me</button>;\n}"
            },
            {
                'name': 'button-styles.css',
                'content': ".action-btn { background: #6366f1; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; }\n.action-btn:hover { background: #4f46e5; }"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Uses correct handler reference', 'input': '', 'expected': 'onClick={handleClick}', 'passed': False}],
        'bug_signature': 'onClick={handleclck}',
        'suspected_component': 'ActionButton.jsx'
    },
    'RE-M01': {
        'title': 'Image fails to load',
        'description': 'An image asset is referenced incorrectly, causing a broken image placeholder in the UI.',
        'difficulty': 'Medium',
        'technology': 'Web',
        'category': 'Assets',
        'time_estimate': '15 mins',
        'points': 150,
        'files': [
            {
                'name': 'Avatar.jsx',
                'content': "import React from 'react';\n\nexport default function Avatar() {\n  return <img className=\"avatar-img\" src=\"/avatars/profile.png\" alt=\"Profile\" />;\n}"
            },
            {
                'name': 'avatar-styles.css',
                'content': ".avatar-img { width: 48px; height: 48px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Loads correct image asset', 'input': '', 'expected': 'src="/assets/avatars/profile.png"', 'passed': False}],
        'bug_signature': 'src="/avatars/profile.png"',
        'suspected_component': 'Avatar.jsx'
    },
    'RE-M02': {
        'title': 'Input field doesn\'t update value',
        'description': 'A controlled input does not reflect user typing because its value prop is not linked to state correctly.',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Controlled Components',
        'time_estimate': '15 mins',
        'points': 150,
        'files': [
            {
                'name': 'SearchInput.jsx',
                'content': "import React, { useState } from 'react';\n\nexport default function SearchInput() {\n  const [search, setSearch] = useState('');\n\n  return (\n    <input className=\"search-box\" value=\"\" onChange={(e) => setSearch(e.target.value)} placeholder=\"Search...\" />\n  );\n}"
            },
            {
                'name': 'search-styles.css',
                'content': ".search-box { background: #0f172a; color: #f8fafc; border: 1px solid #334155; padding: 10px 14px; border-radius: 8px; width: 100%; max-width: 300px; }"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Uses state for input value', 'input': '', 'expected': 'value={search}', 'passed': False}],
        'bug_signature': 'value=""',
        'suspected_component': 'SearchInput.jsx'
    },
    'RE-M03': {
        'title': 'Dark mode toggle resets on refresh',
        'description': 'The theme toggle works, but the selection is not persisted, so the UI resets after page reload.',
        'difficulty': 'Medium',
        'technology': 'React',
        'category': 'Local Storage',
        'time_estimate': '15 mins',
        'points': 150,
        'files': [
            {
                'name': 'ThemeToggle.jsx',
                'content': "import React, { useState } from 'react';\n\nexport default function ThemeToggle() {\n  const [darkMode, setDarkMode] = useState(false);\n\n  const toggle = () => {\n    setDarkMode(!darkMode);\n  };\n\n  return <button className=\"theme-btn\" onClick={toggle}>{darkMode ? 'Dark Mode' : 'Light Mode'}</button>;\n}"
            },
            {
                'name': 'theme-styles.css',
                'content': ".theme-btn { padding: 8px 16px; border-radius: 6px; background: #334155; color: #f8fafc; border: none; font-weight: 500; cursor: pointer; }"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Persists theme selection', 'input': '', 'expected': 'localStorage.setItem', 'passed': False}],
        'bug_signature': 'const [darkMode, setDarkMode] = useState(false);',
        'suspected_component': 'ThemeToggle.jsx'
    },
    'RE-H01': {
        'title': 'Modal closes unexpectedly on backdrop click',
        'description': 'A modal dialog closes as soon as the overlay is clicked, breaking the expected interaction flow.',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Accessibility',
        'time_estimate': '20 mins',
        'points': 250,
        'files': [
            {
                'name': 'Modal.jsx',
                'content': "import React from 'react';\n\nexport default function Modal({ onClose }) {\n  return (\n    <div className=\"backdrop\" onClick={onClose}>\n      <div className=\"modal-content\">Modal body content</div>\n    </div>\n  );\n}"
            },
            {
                'name': 'modal-styles.css',
                'content': ".backdrop { position: fixed; inset: 0; background: rgba(15,23,42,0.8); display: flex; items-center; justify-center; }\n.modal-content { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 24px; color: white; min-width: 300px; }"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Only backdrop clicks close modal', 'input': '', 'expected': 'stopPropagation', 'passed': False}],
        'bug_signature': 'onClick={onClose}',
        'suspected_component': 'Modal.jsx'
    },
    'RE-H02': {
        'title': 'Dashboard list shows stale data after refresh',
        'description': 'A list component keeps rendering old data because the data-fetch effect is not invalidating correctly.',
        'difficulty': 'Hard',
        'technology': 'React',
        'category': 'Data Fetching',
        'time_estimate': '20 mins',
        'points': 250,
        'files': [
            {
                'name': 'DataList.jsx',
                'content': "import React, { useState, useEffect } from 'react';\n\nexport default function DataList() {\n  const [items, setItems] = useState([]);\n\n  useEffect(() => {\n    fetchData();\n  }, []);\n\n  const fetchData = async () => {\n    const response = await fetch('/api/items');\n    const data = await response.json();\n    setItems(data);\n  };\n\n  return <ul className=\"data-list\">{items.map(item => <li key={item.id}>{item.name}</li>)}</ul>;\n}"
            },
            {
                'name': 'list-styles.css',
                'content': ".data-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }\n.data-list li { background: #1e293b; padding: 10px 16px; border-radius: 6px; color: #f8fafc; border: 1px solid #334155; }"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Refreshes data on demand', 'input': '', 'expected': 'fetchData', 'passed': False}],
        'bug_signature': 'useEffect(() => {',
        'suspected_component': 'DataList.jsx'
    },
    'RE-H03': {
        'title': 'Responsive grid collapses on mobile',
        'description': 'A card layout breaks on smaller screens because the flexbox and grid breakpoint rules are not applied correctly.',
        'difficulty': 'Hard',
        'technology': 'CSS',
        'category': 'Responsive Layout',
        'time_estimate': '20 mins',
        'points': 250,
        'files': [
            {
                'name': 'CardGrid.jsx',
                'content': "import React from 'react';\n\nexport default function CardGrid() {\n  return (\n    <div className=\"cards\">\n      <div className=\"card\">Card 1</div>\n      <div className=\"card\">Card 2</div>\n      <div className=\"card\">Card 3</div>\n      <div className=\"card\">Card 4</div>\n    </div>\n  );\n}"
            },
            {
                'name': 'grid.css',
                'content': "/* BUG: Missing mobile breakpoint styles */\n.cards {\n  display: grid;\n  grid-template-columns: repeat(4, minmax(0, 1fr));\n  gap: 1rem;\n}\n.card { background: #1e293b; padding: 16px; border-radius: 8px; color: white; border: 1px solid #334155; text-align: center; }\n\n@media (max-width: 768px) {\n  .cards {\n    grid-template-columns: repeat(4, minmax(0, 1fr));\n  }\n}"
            }
        ],
        'test_cases': [{'id': 1, 'name': 'Uses responsive columns for mobile', 'input': '', 'expected': 'grid-template-columns: repeat(1, minmax(0, 1fr))', 'passed': False}],
        'bug_signature': 'grid-template-columns: repeat(4, minmax(0, 1fr));',
        'suspected_component': 'grid.css'
    }
}

def get_challenge_or_none(pk):
    pk_str = str(pk).strip()
    
    # 1. Direct PK lookup if integer
    if pk_str.isdigit():
        try:
            return Challenge.objects.get(pk=int(pk_str))
        except Challenge.DoesNotExist:
            pass

    # 2. Look up by string ID matching title or category
    chal = Challenge.objects.filter(title__icontains=pk_str).first()
    if chal:
        return chal

    # 3. Look up in catalog if string ID (like SQL-E01, RE-E01)
    catalog_item = SPECIAL_CHALLENGE_CATALOG.get(pk_str)
    if catalog_item:
        chal = Challenge.objects.create(
            title=f"[{pk_str}] {catalog_item['title']}",
            description=catalog_item['description'],
            difficulty=catalog_item['difficulty'],
            technology=catalog_item['technology'],
            category=catalog_item['category'],
            time_estimate=catalog_item['time_estimate'],
            points=catalog_item['points'],
            files=catalog_item['files'],
            test_cases=catalog_item['test_cases'],
            bug_signature=catalog_item['bug_signature'],
            suspected_component=catalog_item['suspected_component']
        )
        return chal

    # 4. Fallback to first challenge in DB if any exist
    return Challenge.objects.first()

@api_view(['GET'])
@permission_classes([AllowAny])
def challenge_detail_view(request, pk):
    challenge = get_challenge_or_none(pk)
    if challenge:
        data = challenge.to_dict() if hasattr(challenge, 'to_dict') else challenge
        user = get_authenticated_user(request)
        if user and isinstance(challenge, Challenge):
            data['predictedDifficulty'] = DifficultyPredictor.predict_difficulty(user, challenge)
        return Response(data)
    return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def predict_challenge_difficulty_view(request, pk):
    challenge = get_challenge_or_none(pk)
    if not challenge:
        return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)

    user = get_authenticated_user(request)
    if not isinstance(challenge, Challenge):
        c_dict = challenge if isinstance(challenge, dict) else {}
        dummy_chal = Challenge(
            id=pk,
            title=c_dict.get('title', pk),
            description=c_dict.get('description', ''),
            difficulty=c_dict.get('difficulty', 'Easy'),
            technology=c_dict.get('technology', 'React'),
            category=c_dict.get('category', 'General')
        )
        prediction = DifficultyPredictor.predict_difficulty(user, dummy_chal)
    else:
        prediction = DifficultyPredictor.predict_difficulty(user, challenge)

    return Response(prediction, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def run_challenge_view(request, pk):
    lim = apply_rate_limit(request, 'code_execution', limit=30)
    if lim:
        return lim
    challenge = get_challenge_or_none(pk)
    if not challenge:
        return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)

    code = request.data.get('code', '')
    files = request.data.get('files', None)

    eval_res = evaluation_engine.evaluate(challenge, files=files, code=code)

    return Response({
        'success': eval_res['success'],
        'score': eval_res['score'],
        'testsPassed': eval_res['tests_passed'],
        'tests_passed': eval_res['tests_passed'],
        'testsTotal': eval_res['tests_total'],
        'tests_total': eval_res['tests_total'],
        'testCases': eval_res['test_results'],
        'test_results': eval_res['test_results'],
        'stdout': eval_res['stdout'],
        'stderr': eval_res['stderr'],
        'executionTime': eval_res['execution_time'],
        'execution_time': eval_res['execution_time'],
        'timedOut': eval_res['timed_out'],
        'error': eval_res['error'],
        'bugSignatureDetected': eval_res['bug_signature_detected'],
        'aiSummary': eval_res['ai_summary']
    })

import datetime
from django.utils import timezone

def update_user_streak(user):
    today = datetime.date.today()
    if not user.last_active_date:
        user.streak = 1
        user.last_active_date = today
    elif user.last_active_date == today:
        pass
    elif user.last_active_date == today - datetime.timedelta(days=1):
        user.streak += 1
        user.last_active_date = today
    else:
        user.streak = 1
        user.last_active_date = today

def check_and_unlock_badges(user):
    existing_badge_names = {b.get('name') for b in (user.badges or []) if isinstance(b, dict)}
    unlocked = []

    badge_rules = [
        {'name': 'First Bug Defeated', 'desc': 'Resolved your first bug', 'icon': '🐞', 'cond': user.challenges_solved >= 1},
        {'name': 'Five Bugs Squashed', 'desc': 'Resolved 5 debugging challenges', 'icon': '🔥', 'cond': user.challenges_solved >= 5},
        {'name': 'Ten Bugs Squashed', 'desc': 'Resolved 10 debugging challenges', 'icon': '⚡', 'cond': user.challenges_solved >= 10},
        {'name': 'Streak Master', 'desc': 'Maintained a 5-day debugging streak', 'icon': '🏆', 'cond': user.streak >= 5},
        {'name': 'Centurion', 'desc': 'Earned over 500 XP', 'icon': '💎', 'cond': user.total_score >= 500},
        {'name': 'Master Debugger', 'desc': 'Earned over 1000 XP', 'icon': '👑', 'cond': user.total_score >= 1000},
    ]

    current_badges = list(user.badges or [])
    for rule in badge_rules:
        if rule['cond'] and rule['name'] not in existing_badge_names:
            badge_obj = {
                'name': rule['name'],
                'desc': rule['desc'],
                'icon': rule['icon'],
                'date': timezone.now().strftime('%b %d, %Y')
            }
            current_badges.append(badge_obj)
            unlocked.append(rule['name'])

            Notification.objects.create(
                user=user,
                title=f"Achievement Unlocked: {rule['name']}",
                message=f'You unlocked the "{rule["name"]}" badge ({rule["desc"]})! Keep squashing bugs.',
                type='achievement',
                time='Just now'
            )

    if unlocked:
        user.badges = current_badges

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_challenge_view(request, pk):
    lim = apply_rate_limit(request, 'code_execution', limit=30)
    if lim:
        return lim
    challenge = get_challenge_or_none(pk)
    if not challenge:
        return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)

    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    code = request.data.get('code', '')
    files = request.data.get('files', None)

    existing_subs = Submission.objects.filter(user=user, challenge=challenge)
    attempt_number = existing_subs.count() + 1
    already_solved = existing_subs.filter(success=True).exists()

    eval_res = evaluation_engine.evaluate(challenge, files=files, code=code)
    is_success = eval_res['success']
    awarded_score = 0

    if is_success:
        if not already_solved:
            awarded_score = eval_res['score']
            user.challenges_solved += 1
            user.total_score += awarded_score

            # Execute Gamification Pipeline
            update_user_streak(user)
            check_and_unlock_badges(user)

            current_activities = user.activities or []
            current_activities.insert(0, {
                'id': int(time.time() * 1000),
                'type': 'challenge_completed',
                'text': f'Squashed bug in "{challenge.title}"',
                'time': 'Just now',
                'xp': awarded_score
            })
            user.activities = current_activities
            user.save()
            summary = eval_res['ai_summary']
        else:
            awarded_score = 0
            summary = 'Already solved previously. Solution verified without additional XP.'
    else:
        awarded_score = 0
        summary = eval_res['ai_summary']

    sub_record = Submission.objects.create(
        user=user,
        challenge=challenge,
        submitted_code=code,
        submitted_files=files or [],
        success=is_success,
        score=awarded_score if is_success else 0,
        test_results=eval_res['test_results'],
        execution_time=eval_res['execution_time'],
        attempt_number=attempt_number,
        stdout=eval_res['stdout'],
        stderr=eval_res['stderr'],
        ai_summary=summary
    )

    # Record learning analytics data for Phase 4 ML tracking
    hints_used_input = request.data.get('hintsUsed') or request.data.get('hints_used') or 0
    AnalyticsCollector.record_submission(sub_record, hints_used=hints_used_input)
    SkillProfiler.update_user_skills(user)

    time_mins = int(eval_res['execution_time'] // 60)
    time_secs = int(eval_res['execution_time'] % 60)

    return Response({
        'submissionId': sub_record.id,
        'submission_id': sub_record.id,
        'success': is_success,
        'score': awarded_score if is_success else 0,
        'testsPassed': eval_res['tests_passed'],
        'tests_passed': eval_res['tests_passed'],
        'testsTotal': eval_res['tests_total'],
        'tests_total': eval_res['tests_total'],
        'attemptNumber': attempt_number,
        'alreadySolved': already_solved,
        'timeTaken': f"{time_mins}m {time_secs:02d}s",
        'bugsFixed': 1 if is_success else 0,
        'remainingIssues': 0 if is_success else max(0, eval_res['tests_total'] - eval_res['tests_passed']),
        'testCases': eval_res['test_results'],
        'test_results': eval_res['test_results'],
        'stdout': eval_res['stdout'],
        'stderr': eval_res['stderr'],
        'executionTime': eval_res['execution_time'],
        'execution_time': eval_res['execution_time'],
        'timedOut': eval_res['timed_out'],
        'error': eval_res['error'],
        'bugSignatureDetected': eval_res['bug_signature_detected'],
        'aiSummary': summary
    })

from buggyman.ai import ai_service

@api_view(['POST'])
@permission_classes([AllowAny])
def hint_challenge_view(request, pk):
    lim = apply_rate_limit(request, 'ai_request', limit=15)
    if lim:
        return lim
    challenge = get_challenge_or_none(pk)
    if not challenge:
        return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)

    user_code = request.data.get('code', '')
    submitted_files = request.data.get('files', [])
    previous_hints = request.data.get('previousHints', []) or request.data.get('previous_hints', [])
    test_results = request.data.get('testResults', []) or request.data.get('test_results', [])
    requested_level = request.data.get('level') or (len(previous_hints) + 1)
    requested_level = min(3, max(1, int(requested_level)))

    starter_code = ""
    if challenge.files:
        starter_code = "\n".join([f.get('content', '') for f in challenge.files if isinstance(f, dict)])

    context = {
        'title': challenge.title,
        'description': challenge.description,
        'technology': challenge.technology,
        'category': challenge.category,
        'suspected_component': challenge.suspected_component,
        'starter_code': starter_code,
        'user_code': user_code,
        'previous_hints': previous_hints,
        'test_results': test_results,
        'level': requested_level
    }

    result = ai_service.generate_hint(context)

    return Response({
        'hint': result.get('hint'),
        'hintNumber': requested_level,
        'level': requested_level,
        'provider': result.get('provider'),
        'isFallback': result.get('isFallback', False),
        'error': result.get('fallbackReason')
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def feedback_challenge_view(request, pk):
    lim = apply_rate_limit(request, 'ai_request', limit=15)
    if lim:
        return lim
    challenge = get_challenge_or_none(pk)
    if not challenge:
        return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)

    user_code = request.data.get('code', '')
    submitted_files = request.data.get('files', [])
    test_results = request.data.get('testResults', []) or request.data.get('test_results', [])
    stdout = request.data.get('stdout', '')
    stderr = request.data.get('stderr', '')
    error = request.data.get('error', '')

    starter_code = ""
    if challenge.files:
        starter_code = "\n".join([f.get('content', '') for f in challenge.files if isinstance(f, dict)])

    user = get_authenticated_user(request)
    weakness_data = WeaknessDetector.detect_weaknesses(user) if user else {}

    context = {
        'title': challenge.title,
        'description': challenge.description,
        'technology': challenge.technology,
        'category': challenge.category,
        'suspected_component': challenge.suspected_component,
        'starter_code': starter_code,
        'user_code': user_code,
        'test_results': test_results,
        'stdout': stdout,
        'stderr': stderr,
        'error': error,
        'user_weaknesses': weakness_data.get('topWeaknesses', [])
    }

    result = ai_service.generate_feedback(context)

    return Response({
        'whatIsWrong': result.get('whatIsWrong'),
        'whyItIsWrong': result.get('whyItIsWrong'),
        'conceptToUnderstand': result.get('conceptToUnderstand'),
        'suggestedDirection': result.get('suggestedDirection'),
        'provider': result.get('provider'),
        'isFallback': result.get('isFallback', False),
        'error': result.get('fallbackReason')
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def explain_solution_view(request, pk):
    challenge = get_challenge_or_none(pk)
    if not challenge:
        return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)

    submitted_code = request.data.get('submittedCode', '') or request.data.get('code', '')
    submitted_files = request.data.get('files', [])

    starter_code = ""
    if challenge.files:
        starter_code = "\n".join([f.get('content', '') for f in challenge.files if isinstance(f, dict)])

    context = {
        'title': challenge.title,
        'description': challenge.description,
        'technology': challenge.technology,
        'category': challenge.category,
        'suspected_component': challenge.suspected_component,
        'starter_code': starter_code,
        'submitted_code': submitted_code
    }

    result = ai_service.generate_explanation(context)

    return Response({
        'whatTheBugWas': result.get('whatTheBugWas'),
        'whyItHappened': result.get('whyItHappened'),
        'whyFixWorks': result.get('whyFixWorks'),
        'keyConcept': result.get('keyConcept'),
        'alternativeApproaches': result.get('alternativeApproaches'),
        'provider': result.get('provider'),
        'isFallback': result.get('isFallback', False),
        'error': result.get('fallbackReason')
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_submissions_list_view(request):
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    queryset = Submission.objects.filter(user=user).select_related('challenge').order_by('-created_at')
    challenge_id = request.query_params.get('challenge')
    if challenge_id:
        queryset = queryset.filter(challenge_id=challenge_id)
        
    return Response([s.to_dict() for s in queryset])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def submission_detail_view(request, pk):
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        sub = Submission.objects.get(pk=pk, user=user)
        return Response(sub.to_dict())
    except Submission.DoesNotExist:
        return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def challenge_submissions_view(request, pk):
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    challenge = get_challenge_or_none(pk)
    if not challenge:
        return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)

    submissions = Submission.objects.filter(user=user, challenge=challenge).order_by('-created_at')
    return Response({
        'challengeId': str(challenge.id),
        'totalAttempts': submissions.count(),
        'solved': submissions.filter(success=True).exists(),
        'submissions': [s.to_dict() for s in submissions]
    })



@api_view(['GET'])
@permission_classes([AllowAny])
def analytics_view(request):
    user = get_authenticated_user(request)
    if user:
        total_solved = user.challenges_solved
        total_attempts = Submission.objects.filter(user=user).count()
        successful_attempts = Submission.objects.filter(user=user, success=True).count()
        accuracy = int(round((successful_attempts / total_attempts) * 100)) if total_attempts > 0 else 100

        solved_subs = Submission.objects.filter(user=user, success=True).select_related('challenge')
        easy_count = len({s.challenge_id for s in solved_subs if s.challenge and s.challenge.difficulty.lower() == 'easy'})
        medium_count = len({s.challenge_id for s in solved_subs if s.challenge and s.challenge.difficulty.lower() == 'medium'})
        hard_count = len({s.challenge_id for s in solved_subs if s.challenge and s.challenge.difficulty.lower() == 'hard'})

        return Response({
            'totalSolved': total_solved,
            'totalAttempts': total_attempts,
            'accuracy': accuracy,
            'streak': user.streak,
            'totalScore': user.total_score,
            'timeTrend': [
                { 'name': 'Mon', 'mins': 15 },
                { 'name': 'Tue', 'mins': 22 },
                { 'name': 'Wed', 'mins': 12 },
                { 'name': 'Thu', 'mins': 30 },
                { 'name': 'Fri', 'mins': 18 },
                { 'name': 'Sat', 'mins': 25 },
                { 'name': 'Sun', 'mins': 8 }
            ],
            'bugStats': [
                { 'name': 'State Management', 'count': max(1, easy_count) },
                { 'name': 'Styling & CSS', 'count': max(1, medium_count) },
                { 'name': 'APIs', 'count': max(1, hard_count) },
                { 'name': 'Async Logic', 'count': 2 }
            ],
            'difficultyProgression': [
                { 'name': 'Easy', 'completed': easy_count },
                { 'name': 'Medium', 'completed': medium_count },
                { 'name': 'Hard', 'completed': hard_count }
            ]
        })

    return Response({
        'totalSolved': 12,
        'totalAttempts': 15,
        'accuracy': 78,
        'streak': 5,
        'totalScore': 780,
        'timeTrend': [
            { 'name': 'Mon', 'mins': 15 },
            { 'name': 'Tue', 'mins': 22 },
            { 'name': 'Wed', 'mins': 12 },
            { 'name': 'Thu', 'mins': 30 },
            { 'name': 'Fri', 'mins': 18 },
            { 'name': 'Sat', 'mins': 25 },
            { 'name': 'Sun', 'mins': 8 }
        ],
        'bugStats': [
            { 'name': 'State Management', 'count': 5 },
            { 'name': 'Styling & CSS', 'count': 3 },
            { 'name': 'APIs', 'count': 2 },
            { 'name': 'Async Logic', 'count': 2 }
        ],
        'difficultyProgression': [
            { 'name': 'Easy', 'completed': 8 },
            { 'name': 'Medium', 'completed': 3 },
            { 'name': 'Hard', 'completed': 1 }
        ]
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard_view(request):
    college = request.query_params.get('college', '').strip()
    cache_key = f"leaderboard:{college.lower() if college else 'global'}"

    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data, status=status.HTTP_200_OK)

    queryset = User.objects.all().only(
        'id', 'username', 'first_name', 'last_name', 'display_name',
        'college', 'avatar', 'total_score', 'challenges_solved', 'streak', 'badges'
    )
    if college and college.lower() != 'all':
        queryset = queryset.filter(college__iexact=college)
        
    users = queryset.order_by('-total_score', '-challenges_solved', '-streak', 'id')[:50]
    
    leaderboard = []
    current_rank = 1
    for i, u in enumerate(users):
        if i > 0:
            prev = users[i - 1]
            if (u.total_score, u.challenges_solved, u.streak) != (prev.total_score, prev.challenges_solved, prev.streak):
                current_rank = i + 1

        d = u.to_dict()
        leaderboard.append({
            'rank': current_rank,
            'id': u.id,
            'name': d['name'],
            'username': u.username,
            'score': u.total_score,
            'streak': u.streak,
            'solved': u.challenges_solved,
            'college': u.college or 'State Technical University',
            'avatar': u.avatar,
            'badgesCount': len(u.badges or [])
        })

    cache.set(cache_key, leaderboard, timeout=30)
    return Response(leaderboard, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications_view(request):
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    return Response([n.to_dict() for n in notifications])

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read_view(request, pk):
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        n = Notification.objects.get(pk=pk, user=user)
        n.read = True
        n.save()
        return Response({'success': True})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    return Response({'success': True})

def is_admin_user(user):
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser or getattr(user, 'role', 'user') == 'admin'))

@api_view(['GET'])
@permission_classes([AllowAny])
def admin_stats_view(request):
    user = get_authenticated_user(request)
    if not is_admin_user(user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    total_users = User.objects.count()
    total_challenges = Challenge.objects.count()
    challenges = [c.to_dict() for c in Challenge.objects.all()]
    users_list = []
    for u in User.objects.all():
        d = u.to_dict()
        users_list.append({
            'id': u.id,
            'name': d['name'],
            'email': u.email,
            'role': d['role'],
            'solved': u.challenges_solved
        })
    return Response({
        'totalUsers': total_users,
        'totalChallenges': total_challenges,
        'activeUsers': max(total_users, 42),
        'aiUsageCount': 289,
        'challenges': challenges,
        'users': users_list
    })

@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def admin_manage_users_view(request, pk=None):
    user = get_authenticated_user(request)
    if not is_admin_user(user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        if pk:
            target_user = User.objects.filter(pk=pk).first()
            if not target_user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response(target_user.to_dict())
        users = [u.to_dict() for u in User.objects.all()]
        return Response(users)

    if request.method == 'PUT':
        target_user = User.objects.filter(pk=pk).first()
        if not target_user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        if 'role' in data:
            new_role = data['role']
            target_user.role = new_role
            if new_role == 'admin':
                target_user.is_staff = True
            target_user.save()

        return Response(target_user.to_dict())

@api_view(['POST', 'PUT'])
@permission_classes([AllowAny])
def admin_create_challenge_view(request, pk=None):
    user = get_authenticated_user(request)
    if not is_admin_user(user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    target_status = data.get('status', 'published').lower()

    if request.method == 'PUT' or pk:
        challenge = Challenge.objects.filter(pk=pk).first()
        if not challenge:
            return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)

        if target_status == 'published':
            t_title = data.get('title', challenge.title)
            t_desc = data.get('description', challenge.description)
            t_files = data.get('files', challenge.files)
            t_tests = data.get('testCases') or data.get('test_cases') or challenge.test_cases
            if not t_title or not t_desc or not t_files or not t_tests:
                return Response({'error': 'Cannot publish incomplete or invalid challenge. Title, description, files, and test cases are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'title' in data: challenge.title = data['title']
        if 'description' in data: challenge.description = data['description']
        if 'status' in data: challenge.status = data['status']
        if 'difficulty' in data: challenge.difficulty = data['difficulty']
        if 'technology' in data: challenge.technology = data['technology']
        if 'category' in data: challenge.category = data['category']
        if 'points' in data: challenge.points = int(data['points'])
        if 'testCases' in data or 'test_cases' in data: challenge.test_cases = data.get('testCases') or data.get('test_cases')
        if 'files' in data: challenge.files = data['files']
        challenge.save()
        return Response(challenge.to_dict(), status=status.HTTP_200_OK)

    if target_status == 'published':
        t_title = data.get('title', '')
        t_desc = data.get('description', '')
        t_files = data.get('files', [])
        t_tests = data.get('testCases') or data.get('test_cases', [])
        if not t_title or not t_desc or not t_files or not t_tests:
            return Response({'error': 'Cannot publish incomplete or invalid challenge. Title, description, files, and test cases are required.'}, status=status.HTTP_400_BAD_REQUEST)

    challenge = Challenge.objects.create(
        title=data.get('title', 'Untitled Challenge'),
        description=data.get('description', ''),
        status=data.get('status', 'published'),
        difficulty=data.get('difficulty', 'Easy'),
        technology=data.get('technology', 'React'),
        category=data.get('category', 'General'),
        time_estimate=data.get('timeEstimate', '15 mins'),
        points=int(data.get('points', 100)),
        files=data.get('files', [{'name': 'index.js', 'content': '// Bug here'}]),
        test_cases=data.get('testCases', [{'id': 1, 'name': 'Runs without crash', 'input': '', 'expected': '', 'passed': False}]),
        bug_signature=data.get('bugSignature', ''),
        suspected_component=data.get('suspectedComponent', ''),
        ai_suggestions=data.get('aiSuggestions', ['Check variable declarations'])
    )
    return Response(challenge.to_dict(), status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_challenge_view(request):
    data = request.data
    difficulty = data.get('difficulty', 'Easy')
    technology = data.get('technology', 'React')
    category = data.get('category', 'Debugging')

    c_data = AIChallengeGenerator.generate_challenge(
        difficulty=difficulty,
        technology=technology,
        category=category
    )

    test_cases = c_data.get('testCases') or c_data.get('test_cases') or []
    bug_signature = c_data.get('bugSignature') or c_data.get('bug_signature') or ''
    suspected_component = c_data.get('suspectedComponent') or c_data.get('suspected_component') or ''
    ai_suggestions = c_data.get('aiSuggestions') or c_data.get('ai_suggestions') or []
    time_estimate = c_data.get('timeEstimate') or c_data.get('time_estimate') or '15 mins'

    challenge = Challenge.objects.create(
        title=c_data.get('title', 'AI Debugging Challenge'),
        description=c_data.get('description', ''),
        difficulty=c_data.get('difficulty', difficulty),
        technology=c_data.get('technology', technology),
        category=c_data.get('category', category),
        time_estimate=time_estimate,
        points=c_data.get('points', 100 if difficulty == 'Easy' else 150 if difficulty == 'Medium' else 300),
        files=c_data.get('files', []),
        test_cases=test_cases,
        bug_signature=bug_signature,
        suspected_component=suspected_component,
        ai_suggestions=ai_suggestions
    )

    # Validate generated draft through BuggyMan Evaluation Engine
    solution_code = c_data.get('solutionCode', '')
    starter_files = c_data.get('files', [])

    starter_res = evaluation_engine.evaluate(challenge, files=starter_files)
    starter_failed = not starter_res.get('success', False)

    solution_res = evaluation_engine.evaluate(challenge, files=starter_files, code=solution_code) if solution_code else {'success': True}
    solution_passed = solution_res.get('success', True)

    resp_dict = challenge.to_dict()
    resp_dict['solutionCode'] = solution_code
    resp_dict['evaluationValidated'] = True
    resp_dict['starterCodeFailed'] = starter_failed
    resp_dict['solutionCodePassed'] = solution_passed
    resp_dict['evaluationSummary'] = {
        'starterCodeResults': starter_res,
        'solutionCodeResults': solution_res
    }

    return Response(resp_dict, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_request_view(request):
    import random
    from django.utils import timezone
    import datetime
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.filter(email=email).first()
    if not user:
        return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
    otp = str(random.randint(100000, 999999))
    user.otp_code = otp
    user.otp_expiry = timezone.now() + datetime.timedelta(minutes=10)
    user.save()
    
    # In sandbox mode, we return the OTP code directly in response so front-end can display/auto-fill it for verification.
    print(f"OTP code for {email} is: {otp}")
    return Response({
        'message': 'Verification code sent successfully. Check your email (or developer console).',
        'otp': otp  # Return it directly for easy local testing
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_reset_view(request):
    from django.utils import timezone
    email = request.data.get('email')
    otp = request.data.get('otp')
    new_password = request.data.get('password')
    
    if not email or not otp or not new_password:
        return Response({'error': 'Email, OTP, and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
    user = User.objects.filter(email=email).first()
    if not user:
        return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
    if not user.otp_code or user.otp_code != otp:
        return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        
    if user.otp_expiry < timezone.now():
        return Response({'error': 'Verification code has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return Response({'error': ', '.join(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.otp_code = ''
    user.otp_expiry = None
    user.save()
    
    return Response({'message': 'Password has been reset successfully.'})

@api_view(['POST'])
@permission_classes([AllowAny])
def inject_bug_view(request):
    code = request.data.get('code', '')
    bug_type = request.data.get('bugType', 'logic') or request.data.get('type', 'logic')
    technology = request.data.get('technology', 'React')

    if not code:
        return Response({'error': 'Valid code string is required for bug injection'}, status=status.HTTP_400_BAD_REQUEST)

    result = BugInjector.inject_bug(code=code, bug_type=bug_type, technology=technology)

    # Validate that injected buggy code fails evaluation
    dummy_challenge = Challenge(
        title='Bug Injection Test',
        description=result.get('intendedBug', 'Injected bug verification'),
        technology=technology,
        files=[{'name': 'main.py' if technology.lower() == 'python' else 'query.sql' if technology.lower() == 'sql' else 'Component.jsx', 'content': result.get('buggyCode', code)}],
        test_cases=result.get('testCases', [])
    )

    eval_res = evaluation_engine.evaluate(dummy_challenge, code=result.get('buggyCode', code))
    buggy_failed = not eval_res.get('success', False)

    result['evaluationValidated'] = True
    result['buggyCodeFailed'] = buggy_failed
    result['evaluationResults'] = eval_res

    return Response(result, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def analytics_ai_insights_view(request):
    user = get_authenticated_user(request)
    username = user.username if user else 'Developer'

    submissions = Submission.objects.filter(user=user) if user else Submission.objects.none()
    total_submissions = submissions.count()
    solved_submissions = submissions.filter(success=True)
    solved_count = solved_submissions.count()

    accuracy_rate = round((solved_count / total_submissions * 100), 1) if total_submissions > 0 else 85.0

    tech_counts = {}
    failed_cats = []
    for sub in submissions:
        if sub.challenge:
            t = sub.challenge.technology
            tech_counts[t] = tech_counts.get(t, 0) + 1
            if not sub.success and sub.challenge.category not in failed_cats:
                failed_cats.append(sub.challenge.category)

    top_technologies = sorted(tech_counts.keys(), key=lambda k: tech_counts[k], reverse=True)[:3]

    context = {
        'username': username,
        'total_submissions': total_submissions or 12,
        'solved_count': solved_count or 10,
        'accuracy_rate': accuracy_rate,
        'top_technologies': top_technologies or ['React', 'SQL'],
        'failed_categories': failed_cats or ['State Management', 'Filtering']
    }

    result = ai_service.generate_personalized_feedback(context)

    return Response({
        'debuggingStrengths': result.get('debuggingStrengths', []),
        'areasNeedingImprovement': result.get('areasNeedingImprovement', []),
        'recommendedFocus': result.get('recommendedFocus', ''),
        'learningStyleInsight': result.get('learningStyleInsight', ''),
        'recommendedChallengeIds': result.get('recommendedChallengeIds', []),
        'provider': result.get('provider'),
        'isFallback': result.get('isFallback', False)
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def learning_analytics_data_view(request):
    user = get_authenticated_user(request)
    if not user:
        return Response({
            'userId': None,
            'username': 'Guest',
            'totalSubmissions': 0,
            'solvedCount': 0,
            'successRate': 0.0,
            'avgExecutionTime': 0.0,
            'hintsUsedTotal': 0,
            'errorTypesSummary': {},
            'technologyPerformance': {},
            'categoryPerformance': {},
            'difficultyPerformance': {'Easy': {'solved': 0, 'attempts': 0}, 'Medium': {'solved': 0, 'attempts': 0}, 'Hard': {'solved': 0, 'attempts': 0}},
            'completionHistory': []
        })

    data = AnalyticsCollector.get_user_analytics_data(user)
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def user_skill_matrix_view(request):
    user = get_authenticated_user(request)
    if not user:
        return Response({
            'userId': None,
            'username': 'Guest',
            'overallProficiency': 0,
            'proficiencyLevel': 'Novice',
            'technologySkills': {'React': 0, 'SQL': 0, 'Python': 0, 'JavaScript': 0, 'HTML/CSS': 0},
            'categorySkills': {},
            'totalSolved': 0,
            'totalSubmissions': 0
        })

    matrix = SkillProfiler.calculate_skill_matrix(user)
    return Response(matrix, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def recommend_challenges_view(request):
    user = get_authenticated_user(request)
    limit = int(request.query_params.get('limit', 5))
    recommendations = ChallengeRecommender.get_recommendations(user, limit=limit)
    return Response(recommendations, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def adaptive_difficulty_state_view(request):
    user = get_authenticated_user(request)
    state = AdaptiveDifficultyManager.get_user_adaptive_state(user)
    return Response(state, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def user_weaknesses_view(request):
    user = get_authenticated_user(request)
    weaknesses = WeaknessDetector.detect_weaknesses(user)
    return Response(weaknesses, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def user_learning_path_view(request):
    user = get_authenticated_user(request)
    path_data = LearningPathGenerator.generate_learning_path(user)
    return Response(path_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_challenge_report_view(request, pk):
    challenge = get_challenge_or_none(pk)
    if not challenge:
        return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)

    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    report_type = request.data.get('reportType', 'broken_challenge') or request.data.get('type', 'broken_challenge')
    description = request.data.get('description', '').strip()
    submission_id = request.data.get('submissionId')

    if not description:
        return Response({'error': 'Report description is required.'}, status=status.HTTP_400_BAD_REQUEST)

    submission = None
    if submission_id:
        submission = Submission.objects.filter(pk=submission_id, user=user).first()

    report = ChallengeReport.objects.create(
        user=user,
        challenge=challenge if isinstance(challenge, Challenge) else Challenge.objects.first(),
        submission=submission,
        report_type=report_type,
        description=description,
        status='open'
    )

    Notification.objects.create(
        user=user,
        title='Report Submitted',
        message=f'Your report regarding "{challenge.title if hasattr(challenge, "title") else pk}" has been received.',
        type='system',
        time='Just now'
    )

    return Response(report.to_dict(), status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def admin_manage_reports_view(request, pk=None):
    user = get_authenticated_user(request)
    if not is_admin_user(user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        if pk:
            rep = ChallengeReport.objects.filter(pk=pk).first()
            if not rep:
                return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response(rep.to_dict())

        status_param = request.query_params.get('status', '').strip()
        queryset = ChallengeReport.objects.all().order_by('-created_at')
        if status_param and status_param.lower() != 'all':
            queryset = queryset.filter(status__iexact=status_param)

        return Response([r.to_dict() for r in queryset], status=status.HTTP_200_OK)

    if request.method == 'PUT':
        rep = ChallengeReport.objects.filter(pk=pk).first()
        if not rep:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        if 'status' in data:
            rep.status = data['status']
        if 'adminNotes' in data or 'admin_notes' in data:
            rep.admin_notes = data.get('adminNotes') or data.get('admin_notes', '')

        rep.save()

        if data.get('disableChallenge') and rep.challenge:
            rep.challenge.status = 'archived'
            rep.challenge.save()

        return Response(rep.to_dict(), status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_view(request):
    """
    Health check endpoint for platform observability and monitoring (Phase 5 Task 7).
    """
    db_status = "connected"
    try:
        User.objects.count()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    cache_status = "operational"
    try:
        cache.set('_health_check', 'ok', timeout=5)
        if cache.get('_health_check') != 'ok':
            cache_status = "degraded"
    except Exception as e:
        cache_status = f"unhealthy: {str(e)}"

    is_healthy = (db_status == "connected" and "unhealthy" not in cache_status)
    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    payload = {
        'status': 'healthy' if is_healthy else 'degraded',
        'database': db_status,
        'evaluator': 'ready',
        'cache': cache_status,
        'version': '1.0.0',
        'timestamp': timezone.now().isoformat()
    }

    log_event('info', 'HEALTH_CHECK', 'Health check ping evaluated', payload)
    return Response(payload, status=status_code)

@api_view(['GET'])
@permission_classes([AllowAny])
def admin_backup_export_view(request):
    user = get_authenticated_user(request)
    if not is_admin_user(user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    backup_data = BackupManager.export_full_backup()
    log_security_event('BACKUP_EXPORT', f'Full system backup exported by admin {user.username}', backup_data.get('counts'))
    return Response(backup_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_backup_verify_view(request):
    user = get_authenticated_user(request)
    if not is_admin_user(user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    payload = request.data
    is_valid, msg = BackupManager.verify_backup_integrity(payload)
    if not is_valid:
        return Response({'valid': False, 'error': msg}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'valid': True, 'message': msg, 'counts': payload.get('counts')}, status=status.HTTP_200_OK)


