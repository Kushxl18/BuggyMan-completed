import time
import datetime
import sys
import os
import requests
from django.db.models import Q, Avg, Count, Sum
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
import uuid
import random
import string
from .models import (
    User, Challenge, Notification, Submission, ChallengeReport,
    BugBytesTransaction, UnlockedHint, BugBytesPackage, BugBytesPurchase,
    RewardMission, MissionChallengeCompletion, SimulatedRewardTransaction,
    PvPBattle
)
from .auth import generate_jwt_token
from .evaluator.engine import EvaluationEngine
from .constants import (
    EASY_BUGBYTE_REWARD,
    MEDIUM_BUGBYTE_REWARD,
    HARD_BUGBYTE_REWARD,
    FIRST_ATTEMPT_BONUS,
    FULL_TEST_PASS_BONUS,
    HINT_COSTS
)
from .ai.groq_service import AIHintService

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
from buggyman.ml.career_engine import CareerEngine
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

    # Validate email format if input is provided as an email address
    if '@' in email:
        try:
            from buggyman.validators import validate_legitimate_email
            email = validate_legitimate_email(email)
        except ValidationError as e:
            return Response({'error': ', '.join(e.messages) if hasattr(e, 'messages') else str(e)}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=email).first()
    if not user:
        user = User.objects.filter(username=email).first()

    if user and user.check_password(password):
        token = generate_jwt_token(user)
        user_dict = user.to_dict()
        is_new = not bool(user.onboarding_completed or user.is_onboarded)
        return Response({'token': token, 'user': user_dict, 'isNewUser': is_new})
    
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

    try:
        from buggyman.validators import validate_legitimate_email
        email = validate_legitimate_email(email)
    except ValidationError as e:
        return Response({'error': ', '.join(e.messages) if hasattr(e, 'messages') else str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if not username:
        username = email.split('@')[0]

    otp = str(data.get('otp', '')).strip()
    from django.core.cache import cache
    sess_otp = request.session.get(f"reg_otp_{email}") if hasattr(request, 'session') else None
    session_otp_val = sess_otp.get('otp') if isinstance(sess_otp, dict) else sess_otp
    saved_otp = cache.get(f"reg_otp_{email}") or session_otp_val
    email_user = getattr(settings, 'EMAIL_HOST_USER', '')

    if email_user or otp or saved_otp:
        if not otp or not saved_otp or str(saved_otp).strip() != str(otp).strip():
            return Response({'error': 'Invalid or expired 6-digit verification code. Please check your inbox or request a new code.'}, status=status.HTTP_400_BAD_REQUEST)
        cache.delete(f"reg_otp_{email}")
        if hasattr(request, 'session'):
            try:
                request.session.pop(f"reg_otp_{email}", None)
            except Exception:
                pass

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
        college=data.get('college', ''),
        bio=bio,
        avatar=avatar,
        theme=theme,
        accent_color=accent_color,
        country=country,
        timezone=timezone,
        interests=interests,
        strengths=data.get('strengths', []),
        weaknesses=data.get('weaknesses', []),
        notifications_config=notifications_config,
        skills={},
        activities=[{
            'id': int(time.time()),
            'text': 'Joined BuggyMan community',
            'time': 'Just now',
            'xp': 0
        }],
        badges=[]
    )

    # Create initial welcome notification for the new user
    Notification.objects.create(
        user=user,
        title='Welcome to BuggyMan!',
        message='Welcome aboard! Solve your first debugging challenge to earn badges and XP.',
        type='system',
        time='Just now'
    )

    token = generate_jwt_token(user)
    user_dict = user.to_dict()
    return Response({'token': token, 'user': user_dict, 'isNewUser': True})

@api_view(['POST'])
@permission_classes([AllowAny])
def check_availability_view(request):
    data = request.data
    username = str(data.get('username', '')).strip()
    email = str(data.get('email', '')).strip()

    if username and User.objects.filter(username__iexact=username).exists():
        return Response({'available': False, 'field': 'username', 'error': 'Username is already taken'}, status=status.HTTP_400_BAD_REQUEST)

    if email:
        try:
            from buggyman.validators import validate_legitimate_email
            email = validate_legitimate_email(email)
        except ValidationError as e:
            return Response({'available': False, 'field': 'email', 'error': ', '.join(e.messages) if hasattr(e, 'messages') else str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if email and User.objects.filter(email__iexact=email).exists():
        return Response({'available': False, 'field': 'email', 'error': 'Email is already registered'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'available': True})

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
            try:
                from buggyman.validators import validate_legitimate_email
                new_email = validate_legitimate_email(data['email'])
            except ValidationError as e:
                return Response({'error': ', '.join(e.messages) if hasattr(e, 'messages') else str(e)}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)
            user.email = new_email
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
        if 'strengths' in data:
            user.strengths = data['strengths']
        if 'weaknesses' in data:
            user.weaknesses = data['weaknesses']
        if 'notifications_config' in data:
            user.notifications_config = data['notifications_config']
        if 'onboarding_completed' in data or 'onboardingCompleted' in data:
            val = data.get('onboarding_completed') if 'onboarding_completed' in data else data.get('onboardingCompleted')
            user.onboarding_completed = bool(val)
        if 'password' in data and data['password']:
            try:
                validate_password(data['password'], user)
            except ValidationError as e:
                return Response({'error': ', '.join(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(data['password'])
        if 'skills' in data:
            user.skills = data['skills']
        user.save()
        SkillProfiler.update_user_skills(user)
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
        queryset = queryset.exclude(title__startswith='[SQL-').exclude(title__startswith='[RE-').exclude(title__startswith='[FE-')

    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(category__icontains=search) |
            Q(technology__icontains=search)
        )

    is_personalized_param = request.query_params.get('personalized', '').lower()
    is_personalized = is_personalized_param == 'true' or (is_personalized_param != 'false' and user is not None and user.is_authenticated)

    if is_personalized:
        challenges = ChallengeRecommender.get_personalized_challenges(
            user=user,
            arena=arena,
            difficulty=difficulty,
            technology=technology,
            category=category,
            search=search
        )
        return Response(challenges)

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
        'test_cases': [
            { 'id': 1, 'name': 'Completed Orders Filter', 'input': '', 'expected': 'Filters query results to include only completed status orders', 'passed': False },
            { 'id': 2, 'name': 'Query Output Format', 'input': '', 'expected': 'Returns correct order columns and matching record rows', 'passed': False },
            { 'id': 3, 'name': 'Excludes Non-Completed Records', 'input': '', 'expected': 'Excludes pending and cancelled orders from output set', 'passed': False }
        ],
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
        'test_cases': [
            { 'id': 1, 'name': 'Price Sort Order', 'input': '', 'expected': 'Sorts product list by price in ascending order', 'passed': False },
            { 'id': 2, 'name': 'Column Projection', 'input': '', 'expected': 'Returns product name and price columns', 'passed': False },
            { 'id': 3, 'name': 'Ordering Consistency', 'input': '', 'expected': 'Ensures lowest priced products appear at top of result set', 'passed': False }
        ],
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
        'test_cases': [
            { 'id': 1, 'name': 'Primary Key Definition', 'input': '', 'expected': 'Enforces unique user identification on primary key column', 'passed': False },
            { 'id': 2, 'name': 'Schema Structure', 'input': '', 'expected': 'Creates users table with id, username, and email columns', 'passed': False },
            { 'id': 3, 'name': 'Duplicate Row Prevention', 'input': '', 'expected': 'Prevents duplicate row insertions into database', 'passed': False }
        ],
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
        'test_cases': [
            { 'id': 1, 'name': 'Username Uniqueness', 'input': '', 'expected': 'Enforces unique constraint on username field', 'passed': False },
            { 'id': 2, 'name': 'Database Table Creation', 'input': '', 'expected': 'Defines primary key and valid user table schema', 'passed': False },
            { 'id': 3, 'name': 'Constraint Assertion', 'input': '', 'expected': 'Rejects insertion of duplicate username records', 'passed': False }
        ],
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
        'test_cases': [
            { 'id': 1, 'name': 'Region Aggregation', 'input': '', 'expected': 'Groups sales totals by region column', 'passed': False },
            { 'id': 2, 'name': 'Sum Metric Calculation', 'input': '', 'expected': 'Calculates accurate sum of sales amount per region', 'passed': False },
            { 'id': 3, 'name': 'Group Column Matching', 'input': '', 'expected': 'Includes non-aggregated SELECT columns in GROUP BY', 'passed': False }
        ],
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
        'test_cases': [
            { 'id': 1, 'name': 'Explicit Join Condition', 'input': '', 'expected': 'Links order records to customer table on matching customer IDs', 'passed': False },
            { 'id': 2, 'name': 'Duplicate Row Prevention', 'input': '', 'expected': 'Avoids cartesian product and duplicate rows', 'passed': False },
            { 'id': 3, 'name': 'Relational Key Matching', 'input': '', 'expected': 'Returns combined order ID and customer name dataset', 'passed': False }
        ],
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
        'test_cases': [
            { 'id': 1, 'name': 'Pre-Aggregation Filter', 'input': '', 'expected': 'Filters individual order quantities before grouping', 'passed': False },
            { 'id': 2, 'name': 'Product Grouping Totals', 'input': '', 'expected': 'Aggregates total quantities per product ID', 'passed': False },
            { 'id': 3, 'name': 'Clause Order Assertion', 'input': '', 'expected': 'Applies filtering prior to aggregate calculation', 'passed': False }
        ],
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

# Alias FE- keys to RE- keys in SPECIAL_CHALLENGE_CATALOG
for key in ['E01', 'E02', 'E03', 'E04', 'M01', 'M02', 'M03', 'H01', 'H02', 'H03']:
    if f'RE-{key}' in SPECIAL_CHALLENGE_CATALOG:
        SPECIAL_CHALLENGE_CATALOG[f'FE-{key}'] = SPECIAL_CHALLENGE_CATALOG[f'RE-{key}']

def get_challenge_or_none(pk):
    pk_str = str(pk).strip()
    
    # 1. Direct PK lookup if integer
    if pk_str.isdigit():
        chal = Challenge.objects.filter(pk=int(pk_str)).first()
        if chal:
            return chal

    # 2. Look up by title containing pk_str or prefix alias (handles FE- vs RE-)
    chal = Challenge.objects.filter(title__icontains=pk_str).first()
    if chal:
        return chal

    alt_pk = pk_str.replace('FE-', 'RE-') if pk_str.startswith('FE-') else (pk_str.replace('RE-', 'FE-') if pk_str.startswith('RE-') else pk_str)
    if alt_pk != pk_str:
        chal = Challenge.objects.filter(title__icontains=alt_pk).first()
        if chal:
            return chal

    # 3. Look up in SPECIAL_CHALLENGE_CATALOG
    catalog_item = SPECIAL_CHALLENGE_CATALOG.get(pk_str) or SPECIAL_CHALLENGE_CATALOG.get(alt_pk)
    if catalog_item:
        chal = Challenge.objects.create(
            title=f"[{pk_str}] {catalog_item['title']}",
            description=catalog_item['description'],
            status='published',
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

    # 4. Fallback to first published challenge in DB
    published_chal = Challenge.objects.filter(status='published').first()
    if published_chal:
        return published_chal

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
    today = timezone.localdate() if hasattr(timezone, 'localdate') else datetime.date.today()
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

            # Calculate BugBytes reward
            diff_lower = (challenge.difficulty or 'Easy').lower()
            if diff_lower == 'hard':
                bb_reward = HARD_BUGBYTE_REWARD
            elif diff_lower == 'medium':
                bb_reward = MEDIUM_BUGBYTE_REWARD
            else:
                bb_reward = EASY_BUGBYTE_REWARD

            if attempt_number == 1:
                bb_reward += FIRST_ATTEMPT_BONUS

            tests_passed = eval_res.get('tests_passed', 0)
            tests_total = eval_res.get('tests_total', 0)
            if tests_total > 0 and tests_passed == tests_total:
                bb_reward += FULL_TEST_PASS_BONUS

            user.bugbytes_balance += bb_reward

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

            BugBytesTransaction.objects.create(
                user=user,
                amount=bb_reward,
                transaction_type='EARN_CHALLENGE',
                reason=f'Completed challenge "{challenge.title}" ({challenge.difficulty})',
                challenge=challenge
            )

            summary = eval_res['ai_summary']
        else:
            awarded_score = 0
            summary = 'Already solved previously. Solution verified without additional XP or BugBytes.'
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

    # Check and update active Money-Back Reward Missions
    mission_updated = False
    if is_success:
        now_ts = timezone.now()
        active_missions = RewardMission.objects.filter(
            user=user,
            status='ACTIVE',
            deadline__gt=now_ts
        )
        for mission in active_missions:
            if mission.is_challenge_eligible(challenge):
                if not MissionChallengeCompletion.objects.filter(mission=mission, challenge=challenge).exists():
                    MissionChallengeCompletion.objects.create(
                        mission=mission,
                        user=user,
                        challenge=challenge,
                        submission=sub_record
                    )
                    mission.completed_count += 1
                    if mission.completed_count >= mission.required_count:
                        mission.status = 'COMPLETED'
                        mission.completed_at = now_ts
                    mission.save()
                    mission_updated = True

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
        'missionUpdated': mission_updated,
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
        all_user_subs = Submission.objects.filter(user=user)
        total_attempts = all_user_subs.count()
        successful_attempts = all_user_subs.filter(success=True).count()
        accuracy = int(round((successful_attempts / total_attempts) * 100)) if total_attempts > 0 else (100 if total_solved > 0 else 0)

        solved_subs = all_user_subs.filter(success=True).select_related('challenge')
        easy_count = len({s.challenge_id for s in solved_subs if s.challenge and s.challenge.difficulty.lower() == 'easy'})
        medium_count = len({s.challenge_id for s in solved_subs if s.challenge and s.challenge.difficulty.lower() == 'medium'})
        hard_count = len({s.challenge_id for s in solved_subs if s.challenge and s.challenge.difficulty.lower() == 'hard'})

        # Calculate average execution / solve time
        avg_exec_time = solved_subs.aggregate(Avg('execution_time'))['execution_time__avg'] or 0.0
        avg_mins = max(1, int(round(avg_exec_time * 2))) if total_solved > 0 else 0
        avg_secs = int((avg_exec_time * 60) % 60)
        formatted_avg_time = f"{avg_mins}m {avg_secs:02d}s" if total_solved > 0 else "0m 00s"

        # Calculate 7-day weekly solve progress
        from django.utils import timezone
        import datetime
        now = timezone.now()
        days_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
        weekly_progress_data = []
        for i in range(6, -1, -1):
            day_date = (now - datetime.timedelta(days=i)).date()
            day_name = days_map[day_date.weekday()]
            day_solved = all_user_subs.filter(success=True, created_at__date=day_date).values('challenge_id').distinct().count()
            weekly_progress_data.append({
                'day': day_name,
                'name': day_name,
                'solved': day_solved,
                'mins': day_solved * 12
            })

        # Category bug type breakdown
        cat_counts = {}
        for s in solved_subs:
            if s.challenge and s.challenge.category:
                cat = s.challenge.category
                cat_counts[cat] = cat_counts.get(cat, 0) + 1

        bug_stats_data = []
        for cat_name, count_val in cat_counts.items():
            bug_stats_data.append({'name': cat_name, 'count': count_val})

        if not bug_stats_data and total_solved > 0:
            bug_stats_data = [
                { 'name': 'State Management', 'count': easy_count },
                { 'name': 'Styling & CSS', 'count': medium_count },
                { 'name': 'APIs & Joins', 'count': hard_count }
            ]

        return Response({
            'solvedCount': total_solved,
            'totalSolved': total_solved,
            'total_solved': total_solved,
            'totalAttempts': total_attempts,
            'total_attempts': total_attempts,
            'accuracyRate': accuracy,
            'accuracy': accuracy,
            'accuracy_rate': accuracy,
            'avgTime': formatted_avg_time,
            'avg_time': formatted_avg_time,
            'streakDays': user.current_streak,
            'streak': user.current_streak,
            'streak_days': user.current_streak,
            'totalScore': user.total_score,
            'total_score': user.total_score,
            'weeklyProgress': weekly_progress_data,
            'timeTrend': weekly_progress_data,
            'bugStats': bug_stats_data,
            'difficultyProgression': [
                { 'name': 'Easy', 'completed': easy_count },
                { 'name': 'Medium', 'completed': medium_count },
                { 'name': 'Hard', 'completed': hard_count }
            ]
        })

    return Response({
        'solvedCount': 0,
        'totalSolved': 0,
        'totalAttempts': 0,
        'accuracyRate': 0,
        'accuracy': 0,
        'avgTime': '0m 00s',
        'streakDays': 0,
        'streak': 0,
        'totalScore': 0,
        'weeklyProgress': [],
        'timeTrend': [],
        'bugStats': [],
        'difficultyProgression': [
            { 'name': 'Easy', 'completed': 0 },
            { 'name': 'Medium', 'completed': 0 },
            { 'name': 'Hard', 'completed': 0 }
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
    from django.conf import settings
    import datetime
    import logging

    logger = logging.getLogger(__name__)

    lim = apply_rate_limit(request, 'forgot_password', limit=5, window_seconds=300)
    if lim:
        return lim

    email = (request.data.get('email') or '').strip().lower()
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        from buggyman.validators import validate_legitimate_email
        email = validate_legitimate_email(email)
    except ValidationError as e:
        return Response({'error': ', '.join(e.messages) if hasattr(e, 'messages') else str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        # Prevent user enumeration attack by responding with the same success message
        return Response({
            'message': 'If an account with this email exists, a verification code has been sent.'
        }, status=status.HTTP_200_OK)
        
    otp = str(random.randint(100000, 999999))
    user.otp_code = otp
    user.otp_expiry = timezone.now() + datetime.timedelta(minutes=10)
    user.save(update_fields=['otp_code', 'otp_expiry'])

    # Send real email via SMTP if configured
    email_user = getattr(settings, 'EMAIL_HOST_USER', '')
    if email_user:
        try:
            from django.core.mail import send_mail
            subject = 'BuggyMan - Password Reset Verification Code'
            message = (
                f"Hello {user.display_name or user.username},\n\n"
                f"You requested a password reset for your BuggyMan account.\n\n"
                f"Your 6-digit verification code is: {otp}\n\n"
                f"This code will expire in 10 minutes.\n"
                f"If you did not request this reset, you can safely ignore this email.\n\n"
                f"- The BuggyMan Team"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL or email_user,
                [email],
                fail_silently=False
            )
        except Exception as mail_err:
            logger.error(f"Failed to deliver reset email to {email}: {mail_err}")
            return Response({'error': f"Failed to deliver reset code to {email}. Please check that the email exists and is valid."}, status=status.HTTP_400_BAD_REQUEST)
    
    # In development/DEBUG mode only, log to server terminal for developer convenience
    if getattr(settings, 'DEBUG', False):
        logger.info(f"[DEV DEBUG] OTP verification code for {email}: {otp}")
        print(f"[DEV DEBUG] OTP verification code for {email}: {otp}")

    return Response({
        'message': f"A 6-digit verification code has been sent to {email}. Check your inbox.",
        # Include code as fallback if SMTP credentials aren't supplied in environment
        'devCode': otp if not email_user else None
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_reset_view(request):
    from django.utils import timezone

    lim = apply_rate_limit(request, 'forgot_password_reset', limit=5, window_seconds=300)
    if lim:
        return lim

    email = (request.data.get('email') or '').strip().lower()
    otp = (request.data.get('otp') or '').strip()
    new_password = request.data.get('password')
    
    if not email or not otp or not new_password:
        return Response({'error': 'Email, OTP, and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
    user = User.objects.filter(email__iexact=email).first()
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
        'version': '1.0.3-timeout-guard',
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


@api_view(['GET'])
@permission_classes([AllowAny])
def career_insights_view(request):
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    role_id = request.query_params.get('role')
    insights = CareerEngine.calculate_role_insights(user)

    if role_id:
        matched_role = next((r for r in insights['roles'] if r['id'] == role_id), None)
        if not matched_role:
            return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(matched_role, status=status.HTTP_200_OK)

    return Response(insights, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def bugbytes_summary_view(request):
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    earned = BugBytesTransaction.objects.filter(user=user, amount__gt=0).aggregate(total=Sum('amount'))['total'] or 0
    spent = abs(BugBytesTransaction.objects.filter(user=user, amount__lt=0).aggregate(total=Sum('amount'))['total'] or 0)
    hints_unlocked = UnlockedHint.objects.filter(user=user).count()

    return Response({
        'balance': user.bugbytes_balance,
        'bugbytes_balance': user.bugbytes_balance,
        'earned': earned,
        'spent': spent,
        'hints_unlocked': hints_unlocked
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def bugbytes_history_view(request):
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    txs = BugBytesTransaction.objects.filter(user=user).order_by('-created_at')[:50]
    return Response([t.to_dict() for t in txs], status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def challenge_hints_view(request, pk):
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    challenge = get_challenge_or_none(pk)
    if not challenge:
        return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        unlocked = UnlockedHint.objects.filter(user=user, challenge=challenge).order_by('hint_level')
        return Response([u.to_dict() for u in unlocked], status=status.HTTP_200_OK)

    if request.method == 'POST':
        lim = apply_rate_limit(request, 'ai_hint', limit=15)
        if lim:
            return lim

        try:
            level = int(request.data.get('level', 1))
        except (ValueError, TypeError):
            return Response({'error': 'Invalid hint level'}, status=status.HTTP_400_BAD_REQUEST)

        if level not in [1, 2, 3]:
            return Response({'error': 'Hint level must be 1, 2, or 3'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already unlocked
        existing = UnlockedHint.objects.filter(user=user, challenge=challenge, hint_level=level).first()
        if existing:
            return Response({
                'level': level,
                'cost': 0,
                'already_unlocked': True,
                'remaining_bugbytes': user.bugbytes_balance,
                'hint': existing.hint_content
            }, status=status.HTTP_200_OK)

        cost = HINT_COSTS.get(level, 5)

        # Use atomic transaction to verify balance and prevent double-spend
        with transaction.atomic():
            user_db = User.objects.select_for_update().get(id=user.id)
            if user_db.bugbytes_balance < cost:
                return Response({
                    'error': f'You need {cost} BugBytes to unlock this hint.'
                }, status=status.HTTP_400_BAD_REQUEST)

            user_code = request.data.get('code', '')
            test_results = request.data.get('testResults') or request.data.get('test_results') or []

            ai_res = AIHintService.generate_hint(challenge, user_code, test_results, level)
            if not ai_res.get('success'):
                return Response({
                    'error': ai_res.get('error', 'AI assistance is temporarily unavailable. Your BugBytes were not deducted.')
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            hint_text = ai_res.get('hint', '')

            # Deduct BugBytes and record transaction
            user_db.bugbytes_balance -= cost
            user_db.save()

            BugBytesTransaction.objects.create(
                user=user_db,
                amount=-cost,
                transaction_type='SPEND_HINT',
                reason=f'Unlocked Hint Level {level} for "{challenge.title}"',
                challenge=challenge,
                hint_level=level
            )

            unlocked_obj = UnlockedHint.objects.create(
                user=user_db,
                challenge=challenge,
                hint_level=level,
                hint_content=hint_text,
                cost=cost
            )

            return Response({
                'level': level,
                'cost': cost,
                'remaining_bugbytes': user_db.bugbytes_balance,
                'hint': hint_text,
                'unlockedHint': unlocked_obj.to_dict()
            }, status=status.HTTP_200_OK)


# ============================================================================
# BUGBYTES STORE & MONEY-BACK REWARD MISSIONS (DEMO PROTOTYPE)
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def store_packages_view(request):
    """
    Lists available BugBytes Store packages, user balance, and active mission count.
    """
    user = get_authenticated_user(request)
    packages = BugBytesPackage.objects.filter(is_active=True).order_by('order_priority', 'price_inr')
    
    balance = user.bugbytes_balance if user else 0
    active_missions_count = 0
    if user:
        active_missions_count = RewardMission.objects.filter(user=user, status='ACTIVE', deadline__gt=timezone.now()).count()

    return Response({
        'packages': [p.to_dict() for p in packages],
        'userBalance': balance,
        'activeMissionsCount': active_missions_count,
        'isDemo': True,
        'disclaimer': 'Demonstration Prototype for Academic Evaluation Only. All transactions and refunds are simulated — no real money charged.'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def store_checkout_view(request):
    """
    Initiates a mock checkout session for purchasing BugBytes.
    Generates a unique transaction reference and returns order summary.
    """
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required to make a purchase.'}, status=status.HTTP_401_UNAUTHORIZED)

    pkg_id = request.data.get('packageId') or request.data.get('package_id')
    if not pkg_id:
        return Response({'error': 'Package ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    package = BugBytesPackage.objects.filter(id=pkg_id, is_active=True).first()
    if not package:
        return Response({'error': 'Selected package not found or inactive.'}, status=status.HTTP_404_NOT_FOUND)

    idempotency_key = request.data.get('idempotencyKey') or request.data.get('idempotency_key')
    if idempotency_key:
        existing_order = BugBytesPurchase.objects.filter(user=user, idempotency_key=idempotency_key).first()
        if existing_order:
            return Response({
                'purchase': existing_order.to_dict(),
                'package': package.to_dict(),
                'demoNotice': 'Mock checkout session restored from idempotency key.'
            }, status=status.HTTP_200_OK)

    tx_ref = f"DEMO-PUR-{uuid.uuid4().hex[:10].upper()}"
    purchase = BugBytesPurchase.objects.create(
        user=user,
        package=package,
        package_name=package.name,
        bugbytes_amount=package.bugbytes,
        price_inr=package.price_inr,
        status='PENDING',
        transaction_reference=tx_ref,
        idempotency_key=idempotency_key,
        payment_method='DEMO_SIMULATOR'
    )

    return Response({
        'purchase': purchase.to_dict(),
        'package': package.to_dict(),
        'orderSummary': {
            'packageName': package.name,
            'bugbytesAmount': package.bugbytes,
            'priceInr': float(package.price_inr),
            'currency': 'INR',
            'transactionReference': tx_ref,
        },
        'rewardMissionPreview': {
            'title': package.mission_title,
            'requiredDifficulty': package.mission_difficulty,
            'requiredCount': package.mission_challenge_count,
            'durationDays': package.mission_days,
            'rewardAmountInr': float(package.reward_amount_inr),
        },
        'demoNotice': 'Academic Evaluation Only — No Real Money Charged.'
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def store_confirm_payment_view(request):
    """
    Simulates payment outcome (SUCCESS or FAILURE).
    Credits BugBytes exactly once on simulated SUCCESS with atomic lock.
    Optionally starts the associated Money-Back Reward Mission.
    """
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    tx_ref = request.data.get('transactionReference') or request.data.get('transaction_reference')
    purchase_id = request.data.get('purchaseId') or request.data.get('purchase_id')
    outcome = str(request.data.get('simulateOutcome') or request.data.get('simulate_outcome') or 'SUCCESS').upper()
    start_mission = request.data.get('startMission', True)

    query = Q(user=user)
    if tx_ref:
        query &= Q(transaction_reference=tx_ref)
    elif purchase_id:
        query &= Q(id=purchase_id)
    else:
        return Response({'error': 'Transaction reference or purchase ID required.'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        purchase = BugBytesPurchase.objects.select_for_update().filter(query).first()
        if not purchase:
            return Response({'error': 'Purchase transaction not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Idempotency / Duplicate Protection
        if purchase.status == 'COMPLETED':
            existing_mission = RewardMission.objects.filter(purchase=purchase).first()
            return Response({
                'success': True,
                'alreadyProcessed': True,
                'message': 'This purchase was already completed. BugBytes were already credited.',
                'purchase': purchase.to_dict(),
                'userBalance': user.bugbytes_balance,
                'rewardMission': existing_mission.to_dict() if existing_mission else None,
            }, status=status.HTTP_200_OK)

        if purchase.status == 'FAILED':
            return Response({
                'success': False,
                'alreadyProcessed': True,
                'error': f'This purchase previously failed: {purchase.failure_reason}',
                'purchase': purchase.to_dict(),
            }, status=status.HTTP_400_BAD_REQUEST)

        # Handle Simulated Outcome
        if outcome == 'SUCCESS':
            purchase.status = 'COMPLETED'
            purchase.completed_at = timezone.now()
            purchase.save()

            # Credit BugBytes to user
            user_db = User.objects.select_for_update().get(id=user.id)
            user_db.bugbytes_balance += purchase.bugbytes_amount
            user_db.save()

            # Audit ledger
            BugBytesTransaction.objects.create(
                user=user_db,
                amount=purchase.bugbytes_amount,
                transaction_type='STORE_PURCHASE',
                reason=f'Purchased {purchase.package_name} (+{purchase.bugbytes_amount} BugBytes) [Ref: {purchase.transaction_reference}]'
            )

            # Auto-activate Reward Mission if requested
            created_mission = None
            if start_mission and purchase.package:
                pkg = purchase.package
                deadline = timezone.now() + timezone.timedelta(days=pkg.mission_days)
                created_mission, _ = RewardMission.objects.get_or_create(
                    purchase=purchase,
                    defaults={
                        'user': user_db,
                        'title': pkg.mission_title,
                        'required_difficulty': pkg.mission_difficulty,
                        'required_count': pkg.mission_challenge_count,
                        'duration_days': pkg.mission_days,
                        'deadline': deadline,
                        'reward_amount_inr': pkg.reward_amount_inr,
                        'status': 'ACTIVE',
                    }
                )

            return Response({
                'success': True,
                'message': f'Simulated Payment Successful! {purchase.bugbytes_amount} BugBytes credited.',
                'purchase': purchase.to_dict(),
                'newBalance': user_db.bugbytes_balance,
                'rewardMission': created_mission.to_dict() if created_mission else None,
                'demoNotice': 'Academic Demonstration: No real money was charged.'
            }, status=status.HTTP_200_OK)

        else:
            # Simulated Failure
            failure_reason = request.data.get('failureReason') or 'Simulated Card/UPI Decline or User Cancellation'
            purchase.status = 'FAILED'
            purchase.failure_reason = failure_reason
            purchase.save()

            return Response({
                'success': False,
                'message': 'Simulated payment failed. No BugBytes were credited.',
                'purchase': purchase.to_dict(),
                'failureReason': failure_reason,
            }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def store_purchases_history_view(request):
    """
    Retrieves the authenticated user's mock purchase history.
    """
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    purchases = BugBytesPurchase.objects.filter(user=user).order_by('-created_at')
    return Response({
        'purchases': [p.to_dict() for p in purchases],
        'totalCount': purchases.count()
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def store_refund_purchase_view(request, pk):
    """
    Simulates refunding an eligible BugBytes purchase.
    STRICT BUSINESS RULE:
    1. Refund is granted ONLY if the user solved the required challenge(s) within the deadline.
    2. Refund is ONLY user's real money (INR) returned to original payment source.
    3. User's BugBytes are NOT deducted — they keep their BugBytes as their learning reward!
    """
    lim = apply_rate_limit(request, 'store', limit=15)
    if lim:
        return lim

    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    purchase = BugBytesPurchase.objects.filter(pk=pk, user=user).first()
    if not purchase:
        return Response({'error': 'Purchase record not found.'}, status=status.HTTP_404_NOT_FOUND)

    if purchase.status == 'REFUNDED' or purchase.refunded_at:
        return Response({'error': 'This purchase has already been refunded.'}, status=status.HTTP_400_BAD_REQUEST)

    if purchase.status != 'COMPLETED':
        return Response({'error': 'Only completed purchases are eligible for refund.'}, status=status.HTTP_400_BAD_REQUEST)

    mission = getattr(purchase, 'reward_mission', None)
    if not mission:
        return Response({
            'error': 'Refund ineligible: Refunds are only granted when you complete the 100% Money-Back Coding Mission within the time limit.'
        }, status=status.HTTP_400_BAD_REQUEST)

    mission.check_and_update_status()

    if mission.status == 'EXPIRED':
        return Response({
            'error': f"Refund ineligible: The coding mission expired on {mission.deadline.strftime('%Y-%m-%d %H:%M')} without completing the required challenges ({mission.completed_count}/{mission.required_count}). Refunds are only granted when challenges are solved within the time limit."
        }, status=status.HTTP_400_BAD_REQUEST)

    if mission.status == 'ACTIVE':
        return Response({
            'error': f"Refund not yet eligible: You must complete the coding mission first! You have solved {mission.completed_count}/{mission.required_count} required challenge(s). Solve {mission.required_count - mission.completed_count} more before the deadline to claim your 100% money-back refund.",
            'completedCount': mission.completed_count,
            'requiredCount': mission.required_count,
            'status': 'ACTIVE'
        }, status=status.HTTP_400_BAD_REQUEST)

    if mission.status == 'CLAIMED':
        return Response({'error': 'The 100% money-back refund has already been claimed for this purchase.'}, status=status.HTTP_400_BAD_REQUEST)

    if mission.status != 'COMPLETED':
        return Response({
            'error': 'Requirements not met: You must solve all required challenges within the deadline to receive your refund.'
        }, status=status.HTTP_400_BAD_REQUEST)

    data = request.data or {}
    reason = str(data.get('reason', '')).strip() or f"100% Money-Back Guarantee: Completed {mission.completed_count}/{mission.required_count} challenges on time"

    with transaction.atomic():
        # Update mission status to CLAIMED
        mission.status = 'CLAIMED'
        mission.claimed_at = timezone.now()
        mission.save(update_fields=['status', 'claimed_at'])

        # Update purchase: REFUND USER MONEY ONLY — DO NOT TOUCH BUGBYTES!
        purchase.status = 'REFUNDED'
        purchase.refund_amount_inr = purchase.price_inr
        purchase.refund_reason = reason
        purchase.refunded_at = timezone.now()
        purchase.save()

        # Log simulated refund transaction
        ref_id = f"DEMO-REW-{uuid.uuid4().hex[:10].upper()}"
        reward_tx = SimulatedRewardTransaction.objects.create(
            mission=mission,
            user=user,
            purchase=purchase,
            reward_amount_inr=purchase.price_inr,
            transaction_reference=ref_id,
            status='SUCCESS',
            mock_processing_time_ms=1200,
            notes=f'100% Money-Back Refund for "{purchase.package_name}". User completed {mission.completed_count}/{mission.required_count} challenges on time. BugBytes retained in full.'
        )

        # Notify user: Money refunded, BugBytes retained!
        Notification.objects.create(
            user=user,
            title='100% Money-Back Refund Issued!',
            message=f"Congratulations! You solved all required challenges on time. A full refund of ₹{purchase.price_inr} has been processed back to your payment method. You keep all {purchase.bugbytes_amount} BugBytes as your learning reward!",
            type='system'
        )

    return Response({
        'success': True,
        'message': f"Successfully refunded ₹{purchase.price_inr} to your account! You keep all {purchase.bugbytes_amount} BugBytes for solving the challenges within the deadline.",
        'purchase': purchase.to_dict(),
        'refundAmountInr': float(purchase.price_inr),
        'keptBugbytes': purchase.bugbytes_amount,
        'newBalance': user.bugbytes_balance,
        'rewardTransaction': reward_tx.to_dict()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def store_missions_view(request):
    """
    Retrieves all Money-Back Reward Missions for the authenticated user.
    """
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    missions = RewardMission.objects.filter(user=user).order_by('-start_date')
    for m in missions:
        m.check_and_update_status()

    missions_list = [m.to_dict() for m in missions]
    active = [m for m in missions_list if m['status'] == 'ACTIVE']
    completed = [m for m in missions_list if m['status'] == 'COMPLETED']
    claimed = [m for m in missions_list if m['status'] == 'CLAIMED']
    expired = [m for m in missions_list if m['status'] == 'EXPIRED']

    total_rewards_claimed = sum(m['reward_amount_inr'] for m in claimed)
    total_potential_rewards = sum(m['reward_amount_inr'] for m in active + completed)

    return Response({
        'missions': missions_list,
        'activeMissions': active,
        'completedMissions': completed,
        'claimedMissions': claimed,
        'expiredMissions': expired,
        'stats': {
            'totalMissions': len(missions_list),
            'activeCount': len(active),
            'claimableCount': len(completed),
            'claimedCount': len(claimed),
            'expiredCount': len(expired),
            'totalRewardsClaimedInr': total_rewards_claimed,
            'totalPotentialRewardsInr': total_potential_rewards,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def store_mission_detail_view(request, pk):
    """
    Retrieves detailed mission information including all completed challenges.
    """
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    mission = RewardMission.objects.filter(id=pk, user=user).first()
    if not mission:
        return Response({'error': 'Mission not found.'}, status=status.HTTP_404_NOT_FOUND)

    mission.check_and_update_status()
    completions = mission.completions.select_related('challenge').order_by('completed_at')

    return Response({
        'mission': mission.to_dict(),
        'completions': [c.to_dict() for c in completions],
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def store_claim_reward_view(request, pk):
    """
    Claims an eligible Money-Back Reward for a satisfied mission.
    Generates a simulated refund transaction record and updates mission status.
    Guarantees one-time claiming per mission via atomic locks.
    """
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    with transaction.atomic():
        mission = RewardMission.objects.select_for_update().filter(id=pk, user=user).first()
        if not mission:
            return Response({'error': 'Mission not found.'}, status=status.HTTP_404_NOT_FOUND)

        mission.check_and_update_status()

        if mission.status == 'CLAIMED':
            existing_tx = SimulatedRewardTransaction.objects.filter(mission=mission).first()
            return Response({
                'error': 'Reward has already been claimed for this mission.',
                'alreadyClaimed': True,
                'rewardTransaction': existing_tx.to_dict() if existing_tx else None,
            }, status=status.HTTP_400_BAD_REQUEST)

        if mission.status == 'EXPIRED':
            return Response({
                'error': 'This mission has expired. The deadline was not met.',
                'status': 'EXPIRED'
            }, status=status.HTTP_400_BAD_REQUEST)

        if mission.status != 'COMPLETED' and mission.completed_count < mission.required_count:
            return Response({
                'error': f'Requirements not met: {mission.completed_count}/{mission.required_count} challenges completed.',
                'status': mission.status,
                'completedCount': mission.completed_count,
                'requiredCount': mission.required_count,
            }, status=status.HTTP_400_BAD_REQUEST)

        # Mark as CLAIMED
        mission.status = 'CLAIMED'
        mission.claimed_at = timezone.now()
        mission.save(update_fields=['status', 'claimed_at'])

        # Mark purchase as REFUNDED (Money refunded, BugBytes retained)
        if mission.purchase:
            p = mission.purchase
            p.status = 'REFUNDED'
            p.refund_amount_inr = mission.reward_amount_inr
            p.refund_reason = f"100% Money-Back Guarantee: Completed {mission.completed_count}/{mission.required_count} challenges on time"
            p.refunded_at = timezone.now()
            p.save()

        # Create Simulated Refund/Reward Transaction
        ref_id = f"DEMO-REW-{uuid.uuid4().hex[:10].upper()}"
        reward_tx = SimulatedRewardTransaction.objects.create(
            mission=mission,
            user=user,
            purchase=mission.purchase,
            reward_amount_inr=mission.reward_amount_inr,
            transaction_reference=ref_id,
            status='SUCCESS',
            mock_processing_time_ms=1200,
            notes=f'100% Money-Back Refund for mission "{mission.title}" ({mission.completed_count}/{mission.required_count} challenges).'
        )

        # Notify user: Money refunded, BugBytes retained!
        Notification.objects.create(
            user=user,
            title='100% Money-Back Refund Issued!',
            message=f"Congratulations! You solved all required challenges within the deadline. ₹{mission.reward_amount_inr} has been refunded to your original payment method. You keep all your BugBytes!",
            type='system'
        )

        return Response({
            'success': True,
            'message': f'Congratulations! Your 100% money-back refund of ₹{mission.reward_amount_inr} has been processed. You keep all your BugBytes!',
            'rewardTransaction': reward_tx.to_dict(),
            'mission': mission.to_dict(),
            'purchase': mission.purchase.to_dict() if mission.purchase else None,
            'demoNotice': 'Academic Evaluation: Virtual reward only. No actual banking or payment gateway transfer.'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def store_rewards_summary_view(request):
    """
    Summary of all mock purchases, simulated refunds, and net simulated costs.
    """
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    rewards = SimulatedRewardTransaction.objects.filter(user=user).order_by('-created_at')
    purchases = BugBytesPurchase.objects.filter(user=user, status='COMPLETED')

    total_purchased_inr = float(purchases.aggregate(total=Sum('price_inr'))['total'] or 0)
    total_rewarded_inr = float(rewards.aggregate(total=Sum('reward_amount_inr'))['total'] or 0)
    net_simulated_cost_inr = max(0.0, total_purchased_inr - total_rewarded_inr)

    return Response({
        'totalPurchasedInr': total_purchased_inr,
        'totalRewardedInr': total_rewarded_inr,
        'netSimulatedCostInr': net_simulated_cost_inr,
        'rewardsCount': rewards.count(),
        'rewards': [r.to_dict() for r in rewards],
        'demoNotice': 'All figures represent simulated demonstration credits for academic evaluation.'
    }, status=status.HTTP_200_OK)


# =============================================================================
# PvP Battle Views & Helpers
# =============================================================================

def _finalize_pvp_battle(battle, winner=None, is_draw=False):
    """
    Finalizes a PvP battle, assigns winner/draw, awards rewards, and sends notifications.
    """
    if battle.status in ['COMPLETED', 'CANCELLED', 'EXPIRED']:
        return battle

    battle.status = 'COMPLETED'
    battle.ended_at = timezone.now()
    battle.winner = winner
    battle.is_draw = is_draw

    if winner:
        winner.total_score += battle.xp_reward
        winner.bugbytes_balance += battle.bugbytes_reward
        winner.save(update_fields=['total_score', 'bugbytes_balance', 'updated_at'])

        opponent = battle.player2 if winner.id == battle.player1_id else battle.player1

        BugBytesTransaction.objects.create(
            user=winner,
            amount=battle.bugbytes_reward,
            transaction_type='EARN_BONUS',
            reason=f'PvP Victory reward (Room: {battle.room_code})',
            challenge=battle.challenge
        )

        Notification.objects.create(
            user=winner,
            title='PvP Battle Victory! 🏆',
            message=f'You defeated {opponent.display_name or opponent.username if opponent else "your opponent"}! +{battle.xp_reward} XP and +{battle.bugbytes_reward} BugBytes awarded.',
            type='achievement'
        )

        if opponent:
            Notification.objects.create(
                user=opponent,
                title='PvP Battle Defeat',
                message=f'Battle finished. {winner.display_name or winner.username} won the match in room {battle.room_code}.',
                type='system'
            )
    elif is_draw:
        for player in [battle.player1, battle.player2]:
            if player:
                Notification.objects.create(
                    user=player,
                    title='PvP Battle Draw ⚔️',
                    message=f'The battle in room {battle.room_code} ended in a draw!',
                    type='system'
                )

    battle.save()
    return battle


def _finish_battle_on_timeout(battle):
    """
    Determines winner and completes battle when time limit expires.
    """
    p1_prog = battle.player1_progress or {}
    p2_prog = battle.player2_progress or {}

    p1_success = bool(p1_prog.get('success', False))
    p2_success = bool(p2_prog.get('success', False))
    p1_tests = int(p1_prog.get('tests_passed', 0))
    p2_tests = int(p2_prog.get('tests_passed', 0))
    p1_time = p1_prog.get('solve_time')
    p2_time = p2_prog.get('solve_time')

    if p1_success and not p2_success:
        return _finalize_pvp_battle(battle, winner=battle.player1)
    elif p2_success and not p1_success:
        return _finalize_pvp_battle(battle, winner=battle.player2)
    elif p1_success and p2_success:
        t1 = p1_time if p1_time is not None else 999999
        t2 = p2_time if p2_time is not None else 999999
        if t1 < t2:
            return _finalize_pvp_battle(battle, winner=battle.player1)
        elif t2 < t1:
            return _finalize_pvp_battle(battle, winner=battle.player2)
        else:
            return _finalize_pvp_battle(battle, is_draw=True)
    else:
        if p1_tests > p2_tests:
            return _finalize_pvp_battle(battle, winner=battle.player1)
        elif p2_tests > p1_tests:
            return _finalize_pvp_battle(battle, winner=battle.player2)
        else:
            return _finalize_pvp_battle(battle, is_draw=True)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pvp_create_battle_view(request):
    lim = apply_rate_limit(request, 'pvp', limit=30)
    if lim:
        return lim
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    difficulty = (request.data.get('difficultyFilter') or request.data.get('difficulty_filter') or '').strip()
    raw_time_limit = request.data.get('timeLimitSeconds') or request.data.get('time_limit_seconds') or 600
    try:
        time_limit = int(raw_time_limit)
        if time_limit <= 0:
            time_limit = 600
    except (ValueError, TypeError):
        time_limit = 600

    challenges = Challenge.objects.filter(status='published')
    if difficulty and difficulty.lower() != 'all':
        filtered = challenges.filter(difficulty__iexact=difficulty)
        if filtered.exists():
            challenges = filtered

    challenge_pool = list(challenges)
    if not challenge_pool:
        challenge_pool = list(Challenge.objects.all())
    if not challenge_pool:
        return Response({'error': 'No challenges available for battle'}, status=status.HTTP_400_BAD_REQUEST)

    challenge = random.choice(challenge_pool)

    for _ in range(50):
        room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not PvPBattle.objects.filter(room_code=room_code).exists():
            break
    else:
        room_code = uuid.uuid4().hex[:6].upper()

    total_tests = len(challenge.test_cases or [])
    p1_prog = {'tests_passed': 0, 'tests_total': total_tests, 'submitted': False, 'solve_time': None}
    p2_prog = {'tests_passed': 0, 'tests_total': total_tests, 'submitted': False, 'solve_time': None}

    battle = PvPBattle.objects.create(
        player1=user,
        challenge=challenge,
        status='WAITING',
        room_code=room_code,
        difficulty_filter=difficulty,
        time_limit_seconds=time_limit,
        player1_progress=p1_prog,
        player2_progress=p2_prog,
        xp_reward=50,
        bugbytes_reward=15
    )

    return Response(battle.to_dict(), status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pvp_join_battle_view(request):
    lim = apply_rate_limit(request, 'pvp', limit=30)
    if lim:
        return lim
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    room_code = (request.data.get('roomCode') or request.data.get('room_code') or '').strip().upper()
    if not room_code:
        return Response({'error': 'Room code is required'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        battle = PvPBattle.objects.select_for_update().filter(room_code=room_code).first()
        if not battle:
            return Response({'error': 'Battle room not found'}, status=status.HTTP_404_NOT_FOUND)

        if battle.player1_id == user.id:
            return Response({'error': 'You cannot join your own battle room'}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        if battle.status == 'WAITING' and (now - battle.created_at).total_seconds() > 300:
            battle.status = 'EXPIRED'
            battle.ended_at = now
            battle.save()
            return Response({'error': 'Battle room has expired'}, status=status.HTTP_400_BAD_REQUEST)

        if battle.status != 'WAITING':
            return Response({'error': f'Cannot join battle with status {battle.status}'}, status=status.HTTP_400_BAD_REQUEST)

        if battle.player2_id is not None:
            return Response({'error': 'Battle room is already full'}, status=status.HTTP_400_BAD_REQUEST)

        battle.player2 = user
        battle.status = 'MATCHED'
        battle.save()

    return Response(battle.to_dict(), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pvp_quick_match_view(request):
    lim = apply_rate_limit(request, 'pvp', limit=30)
    if lim:
        return lim
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    difficulty = (request.data.get('difficultyFilter') or request.data.get('difficulty_filter') or '').strip()
    raw_time_limit = request.data.get('timeLimitSeconds') or request.data.get('time_limit_seconds') or 600
    try:
        time_limit = int(raw_time_limit)
        if time_limit <= 0:
            time_limit = 600
    except (ValueError, TypeError):
        time_limit = 600

    now = timezone.now()
    PvPBattle.objects.filter(
        status='WAITING',
        created_at__lt=now - timezone.timedelta(minutes=5)
    ).update(status='EXPIRED')

    waiting_qs = PvPBattle.objects.filter(status='WAITING').exclude(player1=user)
    if difficulty and difficulty.lower() != 'all':
        diff_qs = waiting_qs.filter(difficulty_filter__iexact=difficulty)
        if diff_qs.exists():
            waiting_qs = diff_qs

    matched_battle = None
    for candidate in waiting_qs.order_by('created_at'):
        with transaction.atomic():
            locked = PvPBattle.objects.select_for_update().filter(id=candidate.id, status='WAITING').first()
            if locked and locked.player2 is None and locked.player1_id != user.id:
                locked.player2 = user
                locked.status = 'MATCHED'
                locked.save()
                matched_battle = locked
                break

    if matched_battle:
        res = matched_battle.to_dict()
        res['action'] = 'joined'
        return Response(res, status=status.HTTP_200_OK)

    challenges = Challenge.objects.filter(status='published')
    if difficulty and difficulty.lower() != 'all':
        filtered = challenges.filter(difficulty__iexact=difficulty)
        if filtered.exists():
            challenges = filtered

    challenge_pool = list(challenges)
    if not challenge_pool:
        challenge_pool = list(Challenge.objects.all())
    if not challenge_pool:
        return Response({'error': 'No challenges available for battle'}, status=status.HTTP_400_BAD_REQUEST)

    challenge = random.choice(challenge_pool)

    for _ in range(50):
        room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not PvPBattle.objects.filter(room_code=room_code).exists():
            break
    else:
        room_code = uuid.uuid4().hex[:6].upper()

    total_tests = len(challenge.test_cases or [])
    p1_prog = {'tests_passed': 0, 'tests_total': total_tests, 'submitted': False, 'solve_time': None}
    p2_prog = {'tests_passed': 0, 'tests_total': total_tests, 'submitted': False, 'solve_time': None}

    new_battle = PvPBattle.objects.create(
        player1=user,
        challenge=challenge,
        status='WAITING',
        room_code=room_code,
        difficulty_filter=difficulty,
        time_limit_seconds=time_limit,
        player1_progress=p1_prog,
        player2_progress=p2_prog,
        xp_reward=50,
        bugbytes_reward=15
    )

    res = new_battle.to_dict()
    res['action'] = 'created'
    return Response(res, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pvp_battle_status_view(request, pk):
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    battle = PvPBattle.objects.filter(id=pk).first()
    if not battle:
        return Response({'error': 'Battle not found'}, status=status.HTTP_404_NOT_FOUND)

    now = timezone.now()
    if battle.status == 'WAITING' and (now - battle.created_at).total_seconds() > 300:
        battle.status = 'EXPIRED'
        battle.ended_at = now
        battle.save()
    elif battle.status == 'IN_PROGRESS' and battle.started_at:
        elapsed = (now - battle.started_at).total_seconds()
        if elapsed >= battle.time_limit_seconds:
            _finish_battle_on_timeout(battle)

    return Response(battle.to_dict(), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pvp_start_battle_view(request, pk):
    lim = apply_rate_limit(request, 'pvp', limit=30)
    if lim:
        return lim
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    battle = PvPBattle.objects.filter(id=pk).first()
    if not battle:
        return Response({'error': 'Battle not found'}, status=status.HTTP_404_NOT_FOUND)

    if user.id not in [battle.player1_id, battle.player2_id]:
        return Response({'error': 'You are not a participant in this battle'}, status=status.HTTP_403_FORBIDDEN)

    if battle.status == 'IN_PROGRESS':
        return Response(battle.to_dict(), status=status.HTTP_200_OK)

    if battle.status != 'MATCHED' or not battle.player1 or not battle.player2:
        return Response({'error': f'Battle is not ready to start (status: {battle.status})'}, status=status.HTTP_400_BAD_REQUEST)

    battle.status = 'IN_PROGRESS'
    battle.started_at = timezone.now()
    battle.save()

    return Response(battle.to_dict(), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pvp_update_progress_view(request, pk):
    lim = apply_rate_limit(request, 'pvp', limit=60)
    if lim:
        return lim
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    battle = PvPBattle.objects.filter(id=pk).first()
    if not battle:
        return Response({'error': 'Battle not found'}, status=status.HTTP_404_NOT_FOUND)

    if user.id not in [battle.player1_id, battle.player2_id]:
        return Response({'error': 'You are not a participant in this battle'}, status=status.HTTP_403_FORBIDDEN)

    if battle.status != 'IN_PROGRESS':
        return Response({'error': f'Cannot update progress for battle with status {battle.status}'}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data
    tests_passed = data.get('testsPassed', data.get('tests_passed', 0))
    tests_total = data.get('testsTotal', data.get('tests_total', len(battle.challenge.test_cases or [])))
    submitted = data.get('submitted', False)

    try:
        tests_passed = int(tests_passed)
    except (ValueError, TypeError):
        tests_passed = 0

    try:
        tests_total = int(tests_total)
    except (ValueError, TypeError):
        tests_total = 0

    progress_update = {
        'tests_passed': tests_passed,
        'tests_total': tests_total,
        'submitted': bool(submitted),
    }

    if user.id == battle.player1_id:
        current = battle.player1_progress or {}
        current.update(progress_update)
        battle.player1_progress = current
    else:
        current = battle.player2_progress or {}
        current.update(progress_update)
        battle.player2_progress = current

    battle.save(update_fields=['player1_progress', 'player2_progress', 'updated_at'])
    return Response(battle.to_dict(), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pvp_submit_solution_view(request, pk):
    lim = apply_rate_limit(request, 'pvp', limit=30)
    if lim:
        return lim
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    battle = PvPBattle.objects.filter(id=pk).first()
    if not battle:
        return Response({'error': 'Battle not found'}, status=status.HTTP_404_NOT_FOUND)

    if user.id not in [battle.player1_id, battle.player2_id]:
        return Response({'error': 'You are not a participant in this battle'}, status=status.HTTP_403_FORBIDDEN)

    if battle.status != 'IN_PROGRESS':
        return Response({'error': f'Battle is not in progress (current status: {battle.status})'}, status=status.HTTP_400_BAD_REQUEST)

    now = timezone.now()
    if battle.started_at:
        elapsed = (now - battle.started_at).total_seconds()
        if elapsed > battle.time_limit_seconds:
            _finish_battle_on_timeout(battle)
            return Response({'error': 'Battle time limit has expired', 'battle': battle.to_dict()}, status=status.HTTP_400_BAD_REQUEST)
        solve_time = round(elapsed, 2)
    else:
        solve_time = 0.0

    code = request.data.get('code', '')
    files = request.data.get('files', None)

    eval_res = evaluation_engine.evaluate(battle.challenge, files=files, code=code)
    is_success = bool(eval_res.get('success', False))
    tests_passed = eval_res.get('tests_passed', 0)
    tests_total = eval_res.get('tests_total', len(battle.challenge.test_cases or []))

    # Log Submission
    existing_count = Submission.objects.filter(user=user, challenge=battle.challenge).count()
    Submission.objects.create(
        user=user,
        challenge=battle.challenge,
        submitted_code=code,
        submitted_files=files or [],
        success=is_success,
        score=battle.xp_reward if is_success else 0,
        test_results=eval_res.get('test_results', []),
        execution_time=eval_res.get('execution_time', 0.0),
        attempt_number=existing_count + 1,
        stdout=eval_res.get('stdout', ''),
        stderr=eval_res.get('stderr', ''),
        ai_summary=eval_res.get('ai_summary', '')
    )

    is_p1 = (user.id == battle.player1_id)
    my_progress = {
        'tests_passed': tests_passed,
        'tests_total': tests_total,
        'submitted': True,
        'success': is_success,
        'solve_time': solve_time if is_success else None
    }

    if is_p1:
        current_p1 = battle.player1_progress or {}
        current_p1.update(my_progress)
        battle.player1_progress = current_p1
        other_progress = battle.player2_progress or {}
        other_player = battle.player2
    else:
        current_p2 = battle.player2_progress or {}
        current_p2.update(my_progress)
        battle.player2_progress = current_p2
        other_progress = battle.player1_progress or {}
        other_player = battle.player1

    other_submitted = bool(other_progress.get('submitted', False))
    other_success = bool(other_progress.get('success', False))

    if is_success:
        if other_success:
            other_time = other_progress.get('solve_time') or 999999
            if solve_time < other_time:
                _finalize_pvp_battle(battle, winner=user)
            elif other_time < solve_time:
                _finalize_pvp_battle(battle, winner=other_player)
            else:
                _finalize_pvp_battle(battle, is_draw=True)
        else:
            _finalize_pvp_battle(battle, winner=user)
    elif other_submitted:
        if other_success:
            _finalize_pvp_battle(battle, winner=other_player)
        else:
            my_tests = tests_passed
            other_tests = int(other_progress.get('tests_passed', 0))
            if my_tests > other_tests:
                _finalize_pvp_battle(battle, winner=user)
            elif other_tests > my_tests:
                _finalize_pvp_battle(battle, winner=other_player)
            else:
                _finalize_pvp_battle(battle, is_draw=True)
    else:
        battle.save(update_fields=['player1_progress', 'player2_progress', 'updated_at'])

    res = battle.to_dict()
    res['evaluation'] = eval_res
    return Response(res, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pvp_cancel_battle_view(request, pk):
    lim = apply_rate_limit(request, 'pvp', limit=30)
    if lim:
        return lim
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    battle = PvPBattle.objects.filter(id=pk).first()
    if not battle:
        return Response({'error': 'Battle not found'}, status=status.HTTP_404_NOT_FOUND)

    if battle.player1_id != user.id:
        return Response({'error': 'Only the creator can cancel this battle'}, status=status.HTTP_403_FORBIDDEN)

    if battle.status not in ['WAITING', 'MATCHED']:
        return Response({'error': f'Cannot cancel battle with status {battle.status}'}, status=status.HTTP_400_BAD_REQUEST)

    battle.status = 'CANCELLED'
    battle.ended_at = timezone.now()
    battle.save()

    return Response(battle.to_dict(), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pvp_history_view(request):
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    status_filter = request.query_params.get('status')
    qs = PvPBattle.objects.filter(Q(player1=user) | Q(player2=user))
    if status_filter:
        qs = qs.filter(status__iexact=status_filter)
    else:
        qs = qs.filter(status__in=['COMPLETED', 'CANCELLED', 'EXPIRED'])

    battles = qs.order_by('-created_at')[:20]
    return Response([b.to_dict() for b in battles], status=status.HTTP_200_OK)


# ==============================================================================
# OAuth 2.0 / SSO AUTHENTICATION (Google, GitHub)
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def oauth_config_view(request):
    """
    Returns public OAuth configuration and status for Google and GitHub.
    """
    frontend_base = os.environ.get('FRONTEND_BASE_URL', '').strip().rstrip('/')
    if not frontend_base:
        referer = request.META.get('HTTP_REFERER')
        if referer:
            from urllib.parse import urlparse
            p = urlparse(referer)
            frontend_base = f"{p.scheme}://{p.netloc}"
        else:
            frontend_base = 'http://localhost:3000'

    redirect_uri = f"{frontend_base}/auth/callback"

    google_client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
    google_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()

    github_client_id = os.environ.get('GITHUB_CLIENT_ID', '').strip()
    github_secret = os.environ.get('GITHUB_CLIENT_SECRET', '').strip()

    return Response({
        'redirectUri': redirect_uri,
        'providers': {
            'google': {
                'id': 'google',
                'name': 'Google',
                'configured': bool(google_client_id and google_secret),
                'clientId': google_client_id,
                'authUrl': 'https://accounts.google.com/o/oauth2/v2/auth',
                'scope': 'openid email profile',
            },
            'github': {
                'id': 'github',
                'name': 'GitHub',
                'configured': bool(github_client_id and github_secret),
                'clientId': github_client_id,
                'authUrl': 'https://github.com/login/oauth/authorize',
                'scope': 'read:user user:email',
            }
        }
    })


def _provision_or_login_oauth_user(provider, data):
    email = str(data.get('email', '')).strip().lower()
    if not email or '@' not in email:
        return Response({'error': 'Valid email address is required for SSO authentication'}, status=status.HTTP_400_BAD_REQUEST)

    oauth_id = str(data.get('oauth_id') or data.get('id') or data.get('sub') or '').strip()
    if not oauth_id:
        oauth_id = f"{provider}_{uuid.uuid5(uuid.NAMESPACE_DNS, email).hex[:16]}"

    display_name = str(data.get('name') or data.get('displayName') or data.get('display_name') or '').strip()
    avatar = str(data.get('avatar') or '').strip()
    college = str(data.get('college') or '').strip()

    if not avatar:
        if provider == 'github':
            avatar = 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'
        else:
            avatar = 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150'

    is_new_user = False
    with transaction.atomic():
        user = User.objects.filter(auth_provider=provider, oauth_id=oauth_id).first()

        if not user:
            user = User.objects.filter(email__iexact=email).first()
            if user:
                user.auth_provider = provider
                user.oauth_id = oauth_id
                if not user.avatar or 'unsplash' in user.avatar:
                    user.avatar = avatar
                if display_name and (not user.display_name or user.display_name == user.username):
                    user.display_name = display_name
                user.save()
            else:
                is_new_user = True
                preferred_username = str(data.get('username', '')).strip().lower()
                if not preferred_username:
                    preferred_username = email.split('@')[0].lower()

                clean_username = ''.join(c for c in preferred_username if c.isalnum() or c in '_-')
                if not clean_username or len(clean_username) < 3:
                    clean_username = f"{provider}_user"

                candidate_username = clean_username
                counter = 1
                while User.objects.filter(username__iexact=candidate_username).exists():
                    candidate_username = f"{clean_username}_{counter}"
                    counter += 1

                name_parts = display_name.split(' ', 1) if display_name else []
                first_name = name_parts[0] if name_parts else ''
                last_name = name_parts[1] if len(name_parts) > 1 else ''

                provider_display = provider.capitalize()
                user = User.objects.create_user(
                    username=candidate_username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    display_name=display_name or candidate_username,
                    college=college or 'Tech Institute of Engineering',
                    bio=f'Software engineer exploring debugging challenges. Joined via {provider_display} SSO.',
                    avatar=avatar,
                    theme='dark',
                    accent_color='blue',
                    country=data.get('country', 'United States'),
                    timezone=data.get('timezone', 'America/New_York'),
                    auth_provider=provider,
                    oauth_id=oauth_id,
                    bugbytes_balance=50,
                    skills={'React': 75, 'Django': 65, 'NodeJS': 50, 'SQL': 60},
                    activities=[{
                        'id': int(time.time()),
                        'text': f'Joined BuggyMan via {provider_display} SSO',
                        'time': 'Just now',
                        'xp': 50
                    }],
                    badges=[{
                        'name': 'SSO Connected',
                        'desc': f'Signed up with verified {provider_display} account',
                        'icon': '🔗',
                        'date': 'Today'
                    }, {
                        'name': 'First Bug Defeated',
                        'desc': 'Ready to resolve your first bug',
                        'icon': '🐞',
                        'date': 'Today'
                    }]
                )
                user.set_unusable_password()
                user.save()

    update_user_streak(user)
    user.save()

    token = generate_jwt_token(user)

    log_security_event(
        event_name=f'oauth_{provider}_success',
        message=f'User {user.username} authenticated via {provider} SSO',
        extra={
            'email': email,
            'is_new_user': is_new_user,
            'provider': provider
        }
    )

    user_dict = user.to_dict()
    is_new = bool(is_new_user or not user.is_onboarded)

    return Response({
        'token': token,
        'user': user_dict,
        'isNewUser': is_new,
        'provider': provider,
        'message': f'Successfully authenticated with {provider.capitalize()}'
    }, status=status.HTTP_200_OK if not is_new else status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def oauth_login_view(request):
    """
    Direct SSO OAuth login / registration endpoint.
    """
    lim = apply_rate_limit(request, 'auth', limit=15)
    if lim:
        return lim

    data = request.data or {}
    provider = str(data.get('provider', '')).strip().lower()
    allowed_providers = {'google', 'github'}
    if provider not in allowed_providers:
        return Response({
            'error': f"Unsupported authentication provider '{provider}'. Must be one of: google, github"
        }, status=status.HTTP_400_BAD_REQUEST)

    return _provision_or_login_oauth_user(provider, data)


@api_view(['POST'])
@permission_classes([AllowAny])
def oauth_callback_view(request):
    """
    Real OAuth 2.0 authorization code exchange.
    Exchanges code for access token with Google or GitHub token servers,
    retrieves user profile, and returns BuggyMan JWT.
    """
    lim = apply_rate_limit(request, 'auth', limit=20)
    if lim:
        return lim

    data = request.data or {}
    provider = str(data.get('provider', '')).strip().lower()
    code = str(data.get('code', '')).strip()
    redirect_uri = str(data.get('redirect_uri') or data.get('redirectUri') or '').strip()

    if not provider or provider not in {'google', 'github'}:
        return Response({'error': f"Invalid or missing OAuth provider '{provider}'"}, status=status.HTTP_400_BAD_REQUEST)

    if not code:
        return Response({'error': 'Authorization code is required'}, status=status.HTTP_400_BAD_REQUEST)

    user_info = {}

    try:
        # ======================================================================
        # 1. GOOGLE OAUTH 2.0 CODE EXCHANGE
        # ======================================================================
        if provider == 'google':
            client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
            client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()
            if not client_id or not client_secret:
                return Response({
                    'error': 'Google OAuth credentials (GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET) are not configured in backend/.env'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            token_res = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': redirect_uri or 'http://localhost:3000/auth/callback'
                },
                headers={'Accept': 'application/json'},
                timeout=10
            )

            token_data = token_res.json()
            if token_res.status_code != 200 or 'access_token' not in token_data:
                err_msg = token_data.get('error_description') or token_data.get('error') or 'Failed to exchange Google authorization code'
                return Response({'error': f"Google OAuth Error: {err_msg}"}, status=status.HTTP_400_BAD_REQUEST)

            access_token = token_data['access_token']
            profile_res = requests.get(
                'https://www.googleapis.com/oauth2/v3/userinfo',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            profile_data = profile_res.json()
            if profile_res.status_code != 200:
                return Response({'error': 'Failed to retrieve Google user profile'}, status=status.HTTP_400_BAD_REQUEST)

            user_info = {
                'oauth_id': str(profile_data.get('sub')),
                'email': profile_data.get('email'),
                'name': profile_data.get('name') or profile_data.get('given_name') or '',
                'avatar': profile_data.get('picture') or ''
            }

        # ======================================================================
        # 2. GITHUB OAUTH 2.0 CODE EXCHANGE
        # ======================================================================
        elif provider == 'github':
            client_id = os.environ.get('GITHUB_CLIENT_ID', '').strip()
            client_secret = os.environ.get('GITHUB_CLIENT_SECRET', '').strip()
            if not client_id or not client_secret:
                return Response({
                    'error': 'GitHub OAuth credentials (GITHUB_CLIENT_ID / GITHUB_CLIENT_SECRET) are not configured in backend/.env'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            token_res = requests.post(
                'https://github.com/login/oauth/access_token',
                json={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'code': code,
                    'redirect_uri': redirect_uri or 'http://localhost:3000/auth/callback'
                },
                headers={'Accept': 'application/json'},
                timeout=10
            )

            token_data = token_res.json()
            if token_res.status_code != 200 or 'access_token' not in token_data:
                err_msg = token_data.get('error_description') or token_data.get('error') or 'Failed to exchange GitHub authorization code'
                return Response({'error': f"GitHub OAuth Error: {err_msg}"}, status=status.HTTP_400_BAD_REQUEST)

            access_token = token_data['access_token']
            profile_res = requests.get(
                'https://api.github.com/user',
                headers={'Authorization': f'Bearer {access_token}', 'User-Agent': 'BuggyMan-App'},
                timeout=10
            )
            profile_data = profile_res.json()
            if profile_res.status_code != 200:
                return Response({'error': 'Failed to retrieve GitHub user profile'}, status=status.HTTP_400_BAD_REQUEST)

            user_email = profile_data.get('email')
            if not user_email:
                emails_res = requests.get(
                    'https://api.github.com/user/emails',
                    headers={'Authorization': f'Bearer {access_token}', 'User-Agent': 'BuggyMan-App'},
                    timeout=10
                )
                if emails_res.status_code == 200:
                    emails_data = emails_res.json()
                    for item in emails_data:
                        if item.get('primary') and item.get('verified'):
                            user_email = item.get('email')
                            break
                    if not user_email and emails_data:
                        user_email = emails_data[0].get('email')

            if not user_email:
                user_email = f"{profile_data.get('login')}@users.noreply.github.com"

            user_info = {
                'oauth_id': str(profile_data.get('id')),
                'email': user_email,
                'name': profile_data.get('name') or profile_data.get('login') or '',
                'username': profile_data.get('login') or '',
                'avatar': profile_data.get('avatar_url') or ''
            }

    except requests.RequestException as e:
        log_error_event('oauth_network_error', f"Network error connecting to {provider}: {str(e)}")
        return Response({'error': f"Failed to connect to {provider} authentication server. Check network connection."}, status=status.HTTP_502_BAD_GATEWAY)

    if not user_info.get('email'):
        return Response({'error': f"Could not retrieve verified email from {provider}."}, status=status.HTTP_400_BAD_REQUEST)

    return _provision_or_login_oauth_user(provider, user_info)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def oauth_disconnect_view(request):
    """
    Unlinks the social OAuth provider from the user profile, allowing fallback to password login.
    """
    user = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.has_usable_password():
        return Response({
            'error': 'Cannot disconnect SSO account without setting an account password first. Please set a password in Settings.'
        }, status=status.HTTP_400_BAD_REQUEST)

    user.auth_provider = 'local'
    user.oauth_id = ''
    user.save()

    return Response({
        'success': True,
        'message': 'Social account disconnected successfully.',
        'user': user.to_dict()
    }, status=status.HTTP_200_OK)


# ==============================================================================
# OTP AUTHENTICATION SYSTEM (EMAIL & PHONE NUMBER OTP)
# ==============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp_view(request):
    """
    Sends a 6-digit OTP code to the provided email or phone number.
    Works for both registration verification and OTP instant login.
    """
    try:
        lim = apply_rate_limit(request, 'otp_send', limit=20, window_seconds=60)
        if lim:
            return lim
        identifier = (request.data.get('identifier') or request.data.get('email') or request.data.get('phone') or '').strip()
        purpose = (request.data.get('purpose') or 'login').strip().lower()

        if not identifier:
            return Response({'error': 'Email address or phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        is_email = '@' in identifier
        if is_email:
            try:
                from buggyman.validators import validate_legitimate_email
                clean_identifier = validate_legitimate_email(identifier)
            except ValidationError as e:
                return Response({'error': ', '.join(e.messages) if hasattr(e, 'messages') else str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            clean_identifier = ''.join(c for c in identifier if c.isdigit() or c == '+')

        # Find existing user if purpose is login
        user = None
        if is_email:
            user = User.objects.filter(email__iexact=clean_identifier).first()
        else:
            user = User.objects.filter(phone=clean_identifier).first()

        # Generate secure 6-digit OTP
        otp = str(random.randint(100000, 999999))
        expiry = timezone.now() + datetime.timedelta(minutes=10)

        from django.core.cache import cache
        cache.set(f"reg_otp_{clean_identifier}", otp, timeout=600)

        if user:
            user.otp_code = otp
            user.otp_expiry = expiry
            user.save(update_fields=['otp_code', 'otp_expiry'])
        else:
            # Cache registration OTP on request session / temporary store if session exists
            if hasattr(request, 'session'):
                try:
                    request.session[f"reg_otp_{clean_identifier}"] = {
                        'otp': otp,
                        'expiry': expiry.isoformat()
                    }
                    request.session.modified = True
                except Exception:
                    pass

        email_user = getattr(settings, 'EMAIL_HOST_USER', '')
        email_delivered = False
        if is_email and email_user:
            try:
                from django.core.mail import send_mail
                subject = 'BuggyMan - Your 6-Digit Email Verification Code'
                message = (
                    f"Hello,\n\n"
                    f"Your 6-digit verification code for BuggyMan is: {otp}\n\n"
                    f"This code will expire in 10 minutes.\n"
                    f"Please enter this code on the registration page to verify your email.\n\n"
                    f"If you did not request this verification, please safely ignore this email.\n\n"
                    f"- The BuggyMan Team"
                )
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL or email_user,
                    [clean_identifier],
                    fail_silently=False
                )
                email_delivered = True
            except Exception as mail_err:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to deliver verification email to {clean_identifier}: {mail_err}")
                email_delivered = False

        msg = f"OTP verification code sent to {clean_identifier}."
        response_data = {
            'success': True,
            'message': msg,
            'identifier': clean_identifier,
            'isEmail': is_email,
            'userExists': bool(user),
            'emailDelivered': email_delivered,
            'otpCode': otp if not email_delivered else None
        }

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as exc:
        import logging, traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Unhandled error in send_otp_view: {traceback.format_exc()}")
        return Response({'error': f"Unable to process OTP request: {str(exc)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_login_view(request):
    """
    Verifies OTP and signs the user in, returning a JWT authentication token.
    If user doesn't exist yet, can auto-create or prompt registration.
    """
    lim = apply_rate_limit(request, 'otp_verify', limit=10, window_seconds=60)
    if lim:
        return lim

    identifier = (request.data.get('identifier') or request.data.get('email') or request.data.get('phone') or '').strip()
    otp = (request.data.get('otp') or '').strip()

    if not identifier or not otp:
        return Response({'error': 'Identifier and OTP code are required.'}, status=status.HTTP_400_BAD_REQUEST)

    is_email = '@' in identifier
    clean_identifier = identifier.lower() if is_email else ''.join(c for c in identifier if c.isdigit() or c == '+')

    user = None
    if is_email:
        user = User.objects.filter(email__iexact=clean_identifier).first()
    else:
        user = User.objects.filter(phone=clean_identifier).first()

    if not user:
        # Check cache or session if this was a registration OTP
        from django.core.cache import cache
        cached_otp = cache.get(f"reg_otp_{clean_identifier}")
        session_saved = request.session.get(f"reg_otp_{clean_identifier}") if hasattr(request, 'session') else None
        
        if (cached_otp and cached_otp == otp) or (session_saved and session_saved.get('otp') == otp):
            # Registration OTP verified!
            return Response({
                'verified': True,
                'isNewUser': True,
                'message': 'OTP verified successfully. Complete profile setup.'
            })
        return Response({'error': 'No account found with this email/phone. Please sign up.'}, status=status.HTTP_404_NOT_FOUND)

    if not user.otp_code or user.otp_code != otp:
        return Response({'error': 'Invalid verification code. Please check and try again.'}, status=status.HTTP_400_BAD_REQUEST)

    if user.otp_expiry and user.otp_expiry < timezone.now():
        return Response({'error': 'Verification code has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validated! Clear OTP
    user.otp_code = ''
    user.otp_expiry = None
    update_user_streak(user)
    user.save()

    token = generate_jwt_token(user)
    user_dict = user.to_dict()
    is_new = not bool(user.onboarding_completed or user.is_onboarded)

    return Response({
        'token': token,
        'user': user_dict,
        'isNewUser': is_new,
        'message': 'Successfully authenticated with OTP.'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_with_otp_view(request):
    """
    Registers a new account with email/phone after OTP validation.
    """
    lim = apply_rate_limit(request, 'auth', limit=10)
    if lim:
        return lim

    data = request.data or {}
    email = str(data.get('email', '')).strip().lower()
    phone = ''.join(c for c in str(data.get('phone', '')) if c.isdigit() or c == '+')
    username = str(data.get('username', '')).strip().lower()
    display_name = str(data.get('displayName') or data.get('name') or username).strip()
    password = str(data.get('password', '')).strip()
    otp = str(data.get('otp', '')).strip()

    if not email and not phone:
        return Response({'error': 'Email or phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

    if email:
        try:
            from buggyman.validators import validate_legitimate_email
            email = validate_legitimate_email(email)
        except ValidationError as e:
            return Response({'error': ', '.join(e.messages) if hasattr(e, 'messages') else str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Verify OTP strictly against cache, session, or pre-registered user
    identifier = email if email else phone
    from django.core.cache import cache
    cached_otp = cache.get(f"reg_otp_{identifier}")
    sess_val = request.session.get(f"reg_otp_{identifier}") if hasattr(request, 'session') else None
    session_otp = sess_val.get('otp') if isinstance(sess_val, dict) else sess_val
    user_with_otp = User.objects.filter(email__iexact=email).first() if email else User.objects.filter(phone=phone).first()

    expected_otp = cached_otp or session_otp or (user_with_otp.otp_code if user_with_otp else None)

    if not otp or not expected_otp or str(expected_otp).strip() != str(otp).strip():
        return Response({'error': 'Valid verification code is required. Please check your inbox or request a new code.'}, status=status.HTTP_400_BAD_REQUEST)

    # Invalidate OTP once verified
    cache.delete(f"reg_otp_{identifier}")
    if hasattr(request, 'session'):
        try:
            request.session.pop(f"reg_otp_{identifier}", None)
        except Exception:
            pass

    if not username:
        username = (email.split('@')[0] if email else f"user_{phone[-4:]}").lower()

    # Generate unique username
    clean_username = ''.join(c for c in username if c.isalnum() or c in '_-')
    if not clean_username or len(clean_username) < 3:
        clean_username = 'coder'

    candidate = clean_username
    counter = 1
    while User.objects.filter(username__iexact=candidate).exists():
        candidate = f"{clean_username}_{counter}"
        counter += 1
    username = candidate

    if email and User.objects.filter(email__iexact=email).exists():
        return Response({'error': 'Email is already registered.'}, status=status.HTTP_400_BAD_REQUEST)

    if phone and User.objects.filter(phone=phone).exists():
        return Response({'error': 'Phone number is already registered.'}, status=status.HTTP_400_BAD_REQUEST)

    name_parts = display_name.split(' ', 1) if display_name else []
    first_name = name_parts[0] if name_parts else ''
    last_name = name_parts[1] if len(name_parts) > 1 else ''

    user = User.objects.create_user(
        username=username,
        email=email or f"{username}@buggyman.dev",
        first_name=first_name,
        last_name=last_name,
        display_name=display_name or username,
        phone=phone,
        college=data.get('college', ''),
        bio=data.get('bio', ''),
        avatar=data.get('avatar', 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'),
        theme='dark',
        accent_color='blue',
        country=data.get('country', ''),
        timezone=data.get('timezone', ''),
        skills={},
        total_score=0,
        challenges_solved=0,
        streak=0,
        bugbytes_balance=50,
        activities=[{
            'id': int(time.time()),
            'text': 'Joined BuggyMan community',
            'time': 'Just now',
            'xp': 0
        }],
        badges=[]
    )

    if password:
        user.set_password(password)
    else:
        user.set_unusable_password()

    user.otp_code = ''
    user.otp_expiry = None
    user.save()

    Notification.objects.create(
        user=user,
        title='Welcome to BuggyMan!',
        message='Welcome aboard! Solve your first debugging challenge to earn badges and XP.',
        type='system',
        time='Just now'
    )

    token = generate_jwt_token(user)
    return Response({
        'token': token,
        'user': user.to_dict(),
        'isNewUser': True,
        'message': 'Account created and verified successfully!'
    }, status=status.HTTP_201_CREATED)



