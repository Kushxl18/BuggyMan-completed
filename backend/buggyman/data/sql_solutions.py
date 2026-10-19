"""
Reference solutions for all 35 SQL Lab challenges (IDs 51 to 85).
"""
from .sql_challenges import get_sql_challenges

def get_sql_solutions():
    solutions = {}
    for c in get_sql_challenges():
        cid = c['id']
        expected = c.get('expected_query', '')
        solutions[cid] = [{
            'name': 'query.sql',
            'content': expected
        }]
    return solutions
