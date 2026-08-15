"""
Structured Observability & Error Logging Module for BuggyMan (Phase 5 Task 7)
"""
import logging
import json
import time

logger = logging.getLogger('buggyman')

SENSITIVE_KEYS = {'password', 'token', 'secret', 'authorization', 'api_key', 'apikey', 'otp_code', 'jwt'}

def sanitize_data(data):
    """
    Recursively scrubs sensitive keys (passwords, tokens, keys) from dicts before logging.
    """
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(s_key in str(k).lower() for s_key in SENSITIVE_KEYS):
                sanitized[k] = '[REDACTED]'
            else:
                sanitized[k] = sanitize_data(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    return data

def log_event(level: str, event_name: str, message: str, extra: dict = None):
    payload = {
        'event': event_name,
        'message': message,
        'timestamp': time.time(),
        'details': sanitize_data(extra or {})
    }
    msg_str = json.dumps(payload)
    if level.lower() == 'error':
        logger.error(msg_str)
    elif level.lower() == 'warning':
        logger.warning(msg_str)
    else:
        logger.info(msg_str)
    return payload

def log_security_event(event_name: str, message: str, extra: dict = None):
    return log_event('warning', f"SECURITY:{event_name}", message, extra)

def log_evaluator_event(event_name: str, message: str, extra: dict = None):
    return log_event('info', f"EVALUATOR:{event_name}", message, extra)

def log_error_event(event_name: str, message: str, extra: dict = None):
    return log_event('error', f"ERROR:{event_name}", message, extra)
