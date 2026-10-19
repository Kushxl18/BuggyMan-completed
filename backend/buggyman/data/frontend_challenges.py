"""
Aggregator for all 35 Frontend Studio challenges (IDs 86 to 120).
- Easy: 10 (86 to 95)
- Medium: 15 (96 to 110)
- Hard: 10 (111 to 120)
"""
from .frontend_easy import get_frontend_easy
from .frontend_medium import get_frontend_medium
from .frontend_hard import get_frontend_hard

def get_frontend_challenges():
    easy = get_frontend_easy()
    medium = get_frontend_medium()
    hard = get_frontend_hard()
    all_challenges = easy + medium + hard
    return all_challenges
