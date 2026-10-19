import os
import sys
import re
import django

backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from buggyman.data import get_all_120_challenges

def audit():
    challenges = get_all_120_challenges()
    print(f"Auditing {len(challenges)} challenges for answer leakage...\n")

    starter_bug_comments = []
    desc_fix_leaks = []
    ai_suggestion_leaks = []
    test_case_leaks = []

    for c in challenges:
        cid = c['id']
        title = c['title']
        files = c.get('files', [])
        desc = c.get('description', '')
        ai_suggs = c.get('ai_suggestions', [])
        test_cases = c.get('test_cases', [])

        # 1. Check starter code for bug comments
        for f in files:
            content = f.get('content', '')
            for line_no, line in enumerate(content.splitlines(), 1):
                if re.search(r'(//|#|--)\s*(BUG|FIX|TODO|DEFECT):', line, re.IGNORECASE):
                    starter_bug_comments.append((cid, f.get('name'), line_no, line.strip()))

        # 2. Check description for code leakage (e.g. `where ...`, exact statements in Requirements or Actual)
        if 'WHERE opt_out' in desc or 'Change `end' in desc or 'setCount(prev =>' in desc:
            desc_fix_leaks.append((cid, title, "Contains exact code replacement syntax in description"))

        # Check for code blocks in Requirements
        req_match = re.search(r'### Requirements(.*?)(###|\Z)', desc, re.DOTALL | re.IGNORECASE)
        if req_match:
            req_text = req_match.group(1)
            # Find any code backticks with SQL statements or assignment syntax
            leaks = re.findall(r'`([^`]+)`', req_text)
            for l in leaks:
                if any(k in l.lower() for k in ['select ', 'where ', 'coalesce', 'join ', ' = ', 'prev =>', 'setcount(', 'item * tax_rate']):
                    desc_fix_leaks.append((cid, title, f"Requirement leaks code: `{l}`"))

        # 3. Check AI suggestions for direct code replacement
        for s in ai_suggs:
            if 'change `' in s.lower() or 'replace `' in s.lower() or 'update to `' in s.lower():
                ai_suggestion_leaks.append((cid, title, s))

        # 4. Check test cases for SQL queries in expected
        for tc in test_cases:
            exp = str(tc.get('expected', ''))
            if exp.strip().upper().startswith('SELECT ') or exp.strip().upper().startswith('WITH '):
                test_case_leaks.append((cid, tc.get('name'), exp))

    print(f"=== AUDIT RESULTS ===")
    print(f"1. Starter files with BUG/FIX comments: {len(starter_bug_comments)}")
    for item in starter_bug_comments[:15]:
        print(f"   - [ID {item[0]}] {item[1]}:{item[2]} -> {item[3]}")
    if len(starter_bug_comments) > 15:
        print(f"   ... and {len(starter_bug_comments) - 15} more.")

    print(f"\n2. Description requirements leaking exact code: {len(desc_fix_leaks)}")
    for item in desc_fix_leaks[:15]:
        print(f"   - [ID {item[0]}] {item[1]} -> {item[2]}")
    if len(desc_fix_leaks) > 15:
        print(f"   ... and {len(desc_fix_leaks) - 15} more.")

    print(f"\n3. AI suggestions handing out code: {len(ai_suggestion_leaks)}")
    for item in ai_suggestion_leaks[:15]:
        print(f"   - [ID {item[0]}] {item[1]} -> {item[2]}")
    if len(ai_suggestion_leaks) > 15:
        print(f"   ... and {len(ai_suggestion_leaks) - 15} more.")

    print(f"\n4. Test cases with query leaks in expected: {len(test_case_leaks)}")
    for item in test_case_leaks[:15]:
        print(f"   - [ID {item[0]}] {item[1]} -> {item[2][:60]}...")
    if len(test_case_leaks) > 15:
        print(f"   ... and {len(test_case_leaks) - 15} more.")

if __name__ == '__main__':
    audit()
