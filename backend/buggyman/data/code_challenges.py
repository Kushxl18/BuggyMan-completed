"""
Code Arena Challenges (50 Total: 15 Easy, 20 Medium, 15 Hard)
"""
from .code_easy import get_code_easy
from .code_medium import get_code_medium
from .code_hard import get_code_hard

def get_code_challenges():
    easy = get_code_easy()
    medium = get_code_medium()
    hard = get_code_hard()
    total = easy + medium + hard
    assert len(total) == 50, f"Expected 50 code challenges, got {len(total)}"
    return total
