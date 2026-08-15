"""
Rate Limiting & Abuse Protection Module for BuggyMan (Phase 5 Task 5)
"""
import time
from collections import defaultdict
from rest_framework.response import Response
from rest_framework import status

_REQUEST_HISTORY = defaultdict(list)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')

def apply_rate_limit(request, scope: str, limit: int, window_seconds: int = 60):
    """
    Applies sliding window rate limit. Returns Response(429) if exceeded, else None.
    """
    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        ident = f"user_{user.id}"
    else:
        ident = f"ip_{get_client_ip(request)}"

    key = f"{scope}:{ident}"
    now = time.time()
    timestamps = _REQUEST_HISTORY[key]
    
    valid_timestamps = [t for t in timestamps if now - t < window_seconds]
    _REQUEST_HISTORY[key] = valid_timestamps

    if len(valid_timestamps) >= limit:
        oldest = valid_timestamps[0]
        retry_after = max(1, int(window_seconds - (now - oldest)))
        return Response({
            'error': f'Rate limit exceeded for {scope}. Too many requests.',
            'scope': scope,
            'retryAfterSeconds': retry_after
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    _REQUEST_HISTORY[key].append(now)
    return None

def clear_rate_limits():
    """Utility to reset rate limits for test cases."""
    _REQUEST_HISTORY.clear()
