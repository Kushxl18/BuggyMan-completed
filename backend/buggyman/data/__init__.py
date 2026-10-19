"""
BuggyMan Challenge Data Package
Exports all 120 challenges and solutions.
"""
from .code_challenges import get_code_challenges
from .sql_challenges import get_sql_challenges
from .frontend_challenges import get_frontend_challenges
from .solutions_120 import get_all_120_solutions

def get_all_120_challenges():
    code = get_code_challenges()
    sql = get_sql_challenges()
    fe = get_frontend_challenges()
    return code + sql + fe

__all__ = [
    'get_code_challenges',
    'get_sql_challenges',
    'get_frontend_challenges',
    'get_all_120_challenges',
    'get_all_120_solutions',
]
