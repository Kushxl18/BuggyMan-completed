import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,24}$')

JUNK_LABELS = {'localhost', 'bar', 'xyz', 'asdf', 'fake', 'invalid'}

def is_valid_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    email = email.strip()

    if '..' in email:
        return False

    if not EMAIL_REGEX.match(email):
        return False

    try:
        django_validate_email(email)
    except ValidationError:
        return False

    parts = email.split('@')
    if len(parts) != 2:
        return False

    local_part, domain_part = parts
    if local_part.startswith('.') or local_part.endswith('.'):
        return False

    domain_parts = domain_part.split('.')
    if len(domain_parts) < 2:
        return False

    for part in domain_parts:
        if not part or part.startswith('-') or part.endswith('-'):
            return False

    tld = domain_parts[-1].lower()
    if len(tld) < 2 or not tld.isalpha():
        return False

    if domain_parts[0].lower() in JUNK_LABELS and not domain_part.endswith(('.edu', '.gov', '.org')):
        return False

    if tld in JUNK_LABELS:
        return False

    return True

def validate_legitimate_email(email: str) -> str:
    """
    Validates that the provided email is a legitimate, well-structured email address.
    Raises ValidationError if invalid. Returns cleaned lowercase email.
    """
    if not email or not isinstance(email, str) or not email.strip():
        raise ValidationError('Email address is required.')

    cleaned = email.strip()
    if not is_valid_email(cleaned):
        raise ValidationError('Please provide a valid, legitimate email address (e.g., user@gmail.com or an institutional domain).')

    return cleaned.lower()
