"""
Test Suite: Unified Challenge Listing Metadata Consistency & UI Audit
Verifies:
1. Stable question numbering across all 3 Arenas:
   - Code Arena: IDs 1-50 -> Q1 to Q50
   - SQL Lab: IDs 51-85 -> Q1 to Q35
   - Frontend Studio: IDs 86-120 -> Q1 to Q35
2. Authoritative metadata serialization in Challenge.to_dict():
   - canonicalTitle stripped of tag prefixes
   - displayTitle = "Q{n}. {canonicalTitle}"
   - arenaKey matching respective arena
   - tables extracted for SQL challenges
   - previewTarget extracted for Frontend challenges
3. Arena recommendation filtering:
   - arena='code' -> exactly 50
   - arena='sql' -> exactly 35
   - arena='frontend' -> exactly 35
   - Total = 120
4. UI Source code audit:
   - Verify ChallengeSelection.jsx, SQLChallenges.jsx, and FrontendDesignChallenges.jsx
     do NOT render chal.description on listing cards.
"""
import os
import sys
import re

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from buggyman.models import Challenge
from buggyman.ml.recommender import ChallengeRecommender

def test_120_challenge_metadata_consistency():
    print("--> Test 1: Testing 120 challenge metadata consistency & stable question numbering...")
    challenges = list(Challenge.objects.order_by('id'))
    assert len(challenges) == 120, f"Expected 120 challenges, found {len(challenges)}"

    code_count = 0
    sql_count = 0
    fe_count = 0

    for c in challenges:
        d = c.to_dict()
        cid = c.id
        q_num = d.get('questionNumber')
        disp_num = d.get('displayNumber')
        disp_title = d.get('displayTitle')
        canon_title = d.get('canonicalTitle')
        arena_key = d.get('arenaKey')

        # Check canonical title does not have bracketed prefixes like [CODE-E01]
        assert not re.match(r'^\[(?:CODE|SQL|FE|RE|PY|JS)-[EMH]\d+\]', canon_title), \
            f"ID {cid} canonicalTitle '{canon_title}' still contains tag prefix!"

        # Check display title matches pattern "Q{q_num}. {canon_title}"
        expected_disp_title = f"{disp_num}. {canon_title}"
        assert disp_title == expected_disp_title, \
            f"ID {cid} displayTitle '{disp_title}' != expected '{expected_disp_title}'"

        if 1 <= cid <= 50:
            code_count += 1
            assert arena_key == 'code', f"ID {cid} arenaKey is {arena_key}, expected 'code'"
            assert q_num == cid, f"ID {cid} q_num is {q_num}, expected {cid}"
            assert disp_num == f"Q{cid}", f"ID {cid} disp_num is {disp_num}, expected Q{cid}"
        elif 51 <= cid <= 85:
            sql_count += 1
            expected_q = cid - 50
            assert arena_key == 'sql', f"ID {cid} arenaKey is {arena_key}, expected 'sql'"
            assert q_num == expected_q, f"ID {cid} q_num is {q_num}, expected {expected_q}"
            assert disp_num == f"Q{expected_q}", f"ID {cid} disp_num is {disp_num}, expected Q{expected_q}"
            # Check tables are populated
            tables = d.get('tables', [])
            assert len(tables) > 0, f"SQL ID {cid} has empty tables list!"
        elif 86 <= cid <= 120:
            fe_count += 1
            expected_q = cid - 85
            assert arena_key == 'frontend', f"ID {cid} arenaKey is {arena_key}, expected 'frontend'"
            assert q_num == expected_q, f"ID {cid} q_num is {q_num}, expected {expected_q}"
            assert disp_num == f"Q{expected_q}", f"ID {cid} disp_num is {disp_num}, expected Q{expected_q}"
            # Check previewTarget is populated
            preview_target = d.get('previewTarget', '')
            assert len(preview_target) > 0, f"Frontend ID {cid} has empty previewTarget!"

    assert code_count == 50, f"Expected 50 code challenges, got {code_count}"
    assert sql_count == 35, f"Expected 35 SQL challenges, got {sql_count}"
    assert fe_count == 35, f"Expected 35 Frontend challenges, got {fe_count}"
    print(f"    [PASSED] All 120 challenges verified: Code (50), SQL (35), Frontend (35)")

def test_recommender_arena_counts():
    print("--> Test 2: Testing recommender arena isolation and candidate counts...")
    code_candidates = ChallengeRecommender.get_personalized_challenges(None, arena='code')
    sql_candidates = ChallengeRecommender.get_personalized_challenges(None, arena='sql')
    fe_candidates = ChallengeRecommender.get_personalized_challenges(None, arena='frontend')

    assert len(code_candidates) == 50, f"Expected 50 code candidates, got {len(code_candidates)}"
    assert len(sql_candidates) == 35, f"Expected 35 SQL candidates, got {len(sql_candidates)}"
    assert len(fe_candidates) == 35, f"Expected 35 Frontend candidates, got {len(fe_candidates)}"

    # Verify no ID overlap between the three arenas
    code_ids = {c['id'] for c in code_candidates}
    sql_ids = {c['id'] for c in sql_candidates}
    fe_ids = {c['id'] for c in fe_candidates}

    assert code_ids.isdisjoint(sql_ids), "Code and SQL candidates overlap!"
    assert code_ids.isdisjoint(fe_ids), "Code and Frontend candidates overlap!"
    assert sql_ids.isdisjoint(fe_ids), "SQL and Frontend candidates overlap!"

    print("    [PASSED] Strict arena isolation verified (50 Code, 35 SQL, 35 Frontend, 0 overlaps)")

def test_ui_listing_cards_no_descriptions():
    print("--> Test 3: Auditing frontend listing pages to ensure problem statements are removed...")
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    files_to_check = [
        os.path.join(project_root, 'frontend', 'src', 'pages', 'ChallengeSelection.jsx'),
        os.path.join(project_root, 'frontend', 'src', 'pages', 'SQLChallenges.jsx'),
        os.path.join(project_root, 'frontend', 'src', 'pages', 'FrontendDesignChallenges.jsx')
    ]

    for fpath in files_to_check:
        fname = os.path.basename(fpath)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for card description leakage
        assert '{chal.description}' not in content, f"Leakage: {fname} still renders {{chal.description}}!"
        assert '{c.description}' not in content, f"Leakage: {fname} still renders {{c.description}}!"
        print(f"    [PASSED] {fname}: Verified zero problem statement leakage on cards.")

def test_detail_page_title_consistency():
    print("--> Test 4: Verifying detail page header uses authoritative displayTitle...")
    problem_panel_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'frontend', 'src', 'pages', 'Challenge', 'ProblemStatementPanel.jsx'
    ))
    with open(problem_panel_path, 'r', encoding='utf-8') as f:
        content = f.read()

    assert 'challenge.displayTitle' in content or 'challenge.display_title' in content, \
        "ProblemStatementPanel does not check challenge.displayTitle!"
    print("    [PASSED] ProblemStatementPanel aligns with authoritative displayTitle.")

if __name__ == '__main__':
    print("=" * 70)
    print("RUNNING LISTING METADATA CONSISTENCY & UI AUDIT TEST SUITE")
    print("=" * 70)
    test_120_challenge_metadata_consistency()
    test_recommender_arena_counts()
    test_ui_listing_cards_no_descriptions()
    test_detail_page_title_consistency()
    print("=" * 70)
    print("ALL TESTS PASSED SUCCESSFULLY! (100% COMPLIANT)")
    print("=" * 70)
