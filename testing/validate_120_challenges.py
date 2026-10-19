"""
Validation Script for BuggyMan 120 Real-World Software Bug Challenge System.
Verifies:
1. All 120 challenges exist in exact distribution (35 Easy, 50 Medium, 35 Hard).
2. All 120 starter challenges fail evaluation (realistic defect verification).
3. All 120 reference solutions pass evaluation with 100% test success rate.
4. Generates testing/CHALLENGE_SOLUTIONS_120.json and testing/CHALLENGE_SOLUTIONS_GUIDE.md.
"""
import os
import sys
import json
import django

# Setup backend Django environment
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from buggyman.models import Challenge
from buggyman.evaluator.engine import EvaluationEngine
from buggyman.data import (
    get_all_120_challenges,
    get_all_120_solutions,
    get_code_challenges,
    get_sql_challenges,
    get_frontend_challenges
)

def run_validation():
    print("=" * 80)
    print("BUGGYMAN 120 REAL-WORLD CHALLENGE SYSTEM VALIDATION")
    print("=" * 80)

    engine = EvaluationEngine()
    challenges = get_all_120_challenges()
    solutions = get_all_120_solutions()

    total_count = len(challenges)
    print(f"Total challenges loaded: {total_count}")
    assert total_count == 120, f"Expected exactly 120 challenges, got {total_count}"

    # Distribution checks
    code_chs = get_code_challenges()
    sql_chs = get_sql_challenges()
    fe_chs = get_frontend_challenges()

    assert len(code_chs) == 50, f"Expected 50 Code Arena challenges, got {len(code_chs)}"
    assert len(sql_chs) == 35, f"Expected 35 SQL Lab challenges, got {len(sql_chs)}"
    assert len(fe_chs) == 35, f"Expected 35 Frontend Studio challenges, got {len(fe_chs)}"

    easy_chs = [c for c in challenges if c['difficulty'] == 'Easy']
    med_chs = [c for c in challenges if c['difficulty'] == 'Medium']
    hard_chs = [c for c in challenges if c['difficulty'] == 'Hard']

    print(f"Distribution: Easy={len(easy_chs)}, Medium={len(med_chs)}, Hard={len(hard_chs)}")
    assert len(easy_chs) == 35, f"Expected 35 Easy, got {len(easy_chs)}"
    assert len(med_chs) == 50, f"Expected 50 Medium, got {len(med_chs)}"
    assert len(hard_chs) == 35, f"Expected 35 Hard, got {len(hard_chs)}"

    print("\nPhase 1: Validating Starter Codes Fail (Realistic Bug Defect Check)...")
    starter_failures = 0
    starter_passes = []
    for c in challenges:
        res = engine.evaluate(c, files=c['files'])
        if not res.get('success', False):
            starter_failures += 1
        else:
            starter_passes.append(c['id'])

    print(f"Starter Codes: {starter_failures}/120 failed (Expected: 120/120)")
    if starter_passes:
        print(f"WARNING: Starters unexpectedly passed for IDs: {starter_passes}")
    assert starter_failures == 120, f"Expected all 120 starters to fail, but {len(starter_passes)} passed"

    print("\nPhase 2: Validating Reference Solutions Pass (100% Success Rate)...")
    sol_passes = 0
    sol_failures = []
    for c in challenges:
        cid = c['id']
        sol_files = solutions.get(cid)
        if not sol_files:
            sol_failures.append((cid, "Missing solution definition"))
            continue
        res = engine.evaluate(c, files=sol_files)
        if res.get('success', False):
            sol_passes += 1
        else:
            sol_failures.append((cid, res.get('error') or res.get('ai_summary')))

    print(f"Reference Solutions: {sol_passes}/120 passed (Expected: 120/120)")
    if sol_failures:
        print(f"WARNING: Solutions failed for IDs: {sol_failures}")
    assert sol_passes == 120, f"Expected all 120 solutions to pass, but {len(sol_failures)} failed"

    # Phase 3: Export CHALLENGE_SOLUTIONS_120.json
    print("\nPhase 3: Exporting testing/CHALLENGE_SOLUTIONS_120.json...")
    export_data = []
    for c in challenges:
        cid = c['id']
        export_data.append({
            'id': cid,
            'title': c['title'],
            'difficulty': c['difficulty'],
            'technology': c['technology'],
            'category': c.get('category', ''),
            'points': c.get('points', 100),
            'bug_signature': c.get('bug_signature', ''),
            'starter_files': c['files'],
            'solution_files': solutions[cid],
            'test_cases': c.get('test_cases', [])
        })

    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CHALLENGE_SOLUTIONS_120.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2)
    print(f"Exported {len(export_data)} solutions to {json_path}")

    # Phase 4: Export CHALLENGE_SOLUTIONS_GUIDE.md
    print("\nPhase 4: Exporting testing/CHALLENGE_SOLUTIONS_GUIDE.md...")
    guide_lines = [
        "# BuggyMan — 120 Real-World Software Bug Challenges & Solution Guide",
        "",
        "This guide documents all 120 verified real-world engineering defects across Code Arena, SQL Lab, and Frontend Studio.",
        "",
        "## Summary Distribution",
        "",
        "| Arena | Easy | Medium | Hard | Total |",
        "|---|---:|---:|---:|---:|",
        "| **Code Arena (Python)** | 15 | 20 | 15 | **50** |",
        "| **SQL Lab (SQLite / Relational)** | 10 | 15 | 10 | **35** |",
        "| **Frontend Studio (React / CSS)** | 10 | 15 | 10 | **35** |",
        "| **Total** | **35** | **50** | **35** | **120** |",
        "",
        "---",
        ""
    ]

    for c in challenges:
        cid = c['id']
        sol = solutions[cid]
        guide_lines.append(f"### Challenge {cid}: {c['title']}")
        guide_lines.append(f"- **Difficulty:** {c['difficulty']} ({c.get('points', 100)} pts)")
        guide_lines.append(f"- **Technology:** {c['technology']}")
        guide_lines.append(f"- **Category:** {c.get('category', '')}")
        guide_lines.append("")
        guide_lines.append("**Bug Description & Root Cause:**")
        desc_preview = c['description'].split('### Bug Report')[-1].split('### Steps to Reproduce')[0].strip() if '### Bug Report' in c['description'] else c['description']
        guide_lines.append(desc_preview.replace('\n', ' ').strip())
        guide_lines.append("")
        guide_lines.append("**Reference Solution Implementation:**")
        for sf in sol:
            ext = sf['name'].split('.')[-1]
            lang = 'python' if ext == 'py' else ('sql' if ext == 'sql' else ('javascript' if ext in ('js', 'jsx') else 'css'))
            guide_lines.append(f"*{sf['name']}*:")
            guide_lines.append(f"```{lang}")
            guide_lines.append(sf['content'].strip())
            guide_lines.append("```")
        guide_lines.append("")
        guide_lines.append("---")
        guide_lines.append("")

    guide_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CHALLENGE_SOLUTIONS_GUIDE.md')
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(guide_lines))
    print(f"Exported guide to {guide_path}")

    print("\n" + "=" * 80)
    print("ALL 120 REAL-WORLD CHALLENGES VALIDATED SUCCESSFULLY (100% PASS RATE)!")
    print("=" * 80)

if __name__ == '__main__':
    run_validation()
