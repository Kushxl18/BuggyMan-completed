"""
Aggregator of all 120 reference solutions for BuggyMan challenges.
- Code Arena: IDs 1 to 50
- SQL Lab: IDs 51 to 85
- Frontend Studio: IDs 86 to 120
"""
from .code_solutions import get_code_solutions
from .sql_solutions import get_sql_solutions
from .frontend_solutions import get_frontend_solutions

def get_all_120_solutions():
    solutions = {}
    solutions.update(get_code_solutions())
    solutions.update(get_sql_solutions())
    solutions.update(get_frontend_solutions())
    return solutions
