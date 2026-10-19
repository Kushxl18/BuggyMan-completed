"""
SQL Lab Challenges (35 Total: 10 Easy, 15 Medium, 10 Hard)
"""
from .sql_easy import get_sql_easy
from .sql_medium import get_sql_medium
from .sql_hard import get_sql_hard

def get_sql_challenges():
    easy = get_sql_easy()
    medium = get_sql_medium()
    hard = get_sql_hard()
    total = easy + medium + hard
    assert len(total) == 35, f"Expected 35 SQL challenges, got {len(total)}"
    return total
