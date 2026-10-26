"""
Personalized Challenge Recommender for BuggyMan (Strength/Weakness Adaptive, Curated Deck & Interleaved)
Curates a tailored subset of challenges for each user rather than showing all 120 questions at once.
Interleaves difficulties (e.g. majority Hard + some Medium + few Easy for strong domains;
mostly Easy to Medium with rare Hard for weak domains until milestone of 20 solved).
"""
import hashlib
from django.core.cache import cache
from django.db.models import Q
from buggyman.models import Challenge, Submission


class ChallengeRecommender:
    ARENA_DOMAINS = {
        'sql': 'SQL',
        'database': 'SQL',
        'frontend': 'Frontend',
        'studio': 'Frontend',
        'design': 'Frontend',
        'code': 'Backend',
        'debugging': 'Backend',
        'backend': 'Backend'
    }

    @classmethod
    def get_challenge_domain(cls, c_tech: str, c_cat: str, c_title: str, c_id) -> str:
        """Determines the primary domain (SQL, Frontend, Backend) of a challenge."""
        tech_low = (c_tech or '').lower()
        cat_low = (c_cat or '').lower()
        title_low = (c_title or '').lower()
        try:
            c_id_int = int(c_id)
        except (ValueError, TypeError):
            c_id_int = 0

        if 'sql' in tech_low or 'database' in cat_low or title_low.startswith('[sql-') or (51 <= c_id_int <= 85):
            return 'SQL'
        if (
            any(k in tech_low or k in cat_low for k in ['react', 'css', 'html', 'frontend', 'ui', 'styling', 'components']) or
            title_low.startswith('[fe-') or title_low.startswith('[re-') or (86 <= c_id_int <= 120)
        ):
            return 'Frontend'
        return 'Backend'

    @classmethod
    def matches_skill_set(cls, c_tech: str, c_cat: str, c_topics: list, c_domain: str, skills_list: list) -> bool:
        """Checks if a challenge relates to any of the user's registered skills."""
        if not skills_list:
            return False
        tech_low = (c_tech or '').lower()
        cat_low = (c_cat or '').lower()
        dom_low = c_domain.lower()
        topics_low = [t.lower() for t in (c_topics or [])]

        for s in skills_list:
            s_low = (s or '').strip().lower()
            if not s_low:
                continue
            if s_low in tech_low or s_low in cat_low or any(s_low in t for t in topics_low):
                return True
            if s_low in ('sql', 'database') and dom_low == 'sql':
                return True
            if s_low in ('frontend', 'react', 'ui', 'web') and dom_low == 'frontend':
                return True
            if s_low in ('backend', 'python', 'django', 'nodejs', 'javascript', 'apis', 'algorithms', 'security', 'devops') and dom_low == 'backend':
                return True
        return False

    @classmethod
    def get_user_challenge_jitter(cls, user_id: int, challenge_id: int, arena_key: str) -> float:
        """
        Produces a stable, deterministic pseudo-random jitter in range [-3.0, +3.0]
        ensuring that every user gets a unique personal challenge order.
        """
        seed_str = f"usr_{user_id}_chl_{challenge_id}_arn_{arena_key}"
        digest = hashlib.md5(seed_str.encode('utf-8')).hexdigest()
        val = int(digest[:6], 16)
        jitter = ((val % 1000) / 1000.0) * 6.0 - 3.0
        return round(jitter, 2)

    @classmethod
    def user_deterministic_pick(cls, user_id: int, items_list: list, count: int, seed_key: str) -> list:
        """
        Selects a deterministic subset of challenges uniquely for this user.
        """
        if not items_list or count <= 0:
            return []
        if len(items_list) <= count:
            return list(items_list)

        scored = []
        for item in items_list:
            item_id = getattr(item, 'id', None) or item.get('id', 0)
            seed_str = f"usr_{user_id}_{seed_key}_{item_id}"
            hash_val = int(hashlib.md5(seed_str.encode('utf-8')).hexdigest()[:6], 16)
            scored.append((hash_val, item))

        scored.sort(key=lambda x: x[0])
        return [x[1] for x in scored[:count]]

    @classmethod
    def interleave_deck(cls, hard_list: list, medium_list: list, easy_list: list, mode: str = 'neutral') -> list:
        """
        Interleaves difficulties into a non-monolithic, natural progression feed:
        - strength / weakness_mastered: majority Hard, with Medium every 3 items and Easy every 6 items.
        - weakness: mostly Easy, with Medium every 3 items and Hard rarely (every 8-9 items).
        - neutral: balanced alternating flow [Medium, Easy, Medium, Hard].
        """
        h_idx, m_idx, e_idx = 0, 0, 0
        result = []
        total_count = len(hard_list) + len(medium_list) + len(easy_list)

        if mode in ('strength', 'weakness_mastered'):
            cycle = ['H', 'H', 'M', 'H', 'H', 'E']
        elif mode == 'weakness':
            cycle = ['E', 'E', 'M', 'E', 'E', 'M', 'E', 'H'] if hard_list else ['E', 'E', 'M', 'E', 'E', 'M']
        else: # neutral
            cycle = ['M', 'E', 'M', 'H']

        cycle_idx = 0
        while len(result) < total_count:
            target_type = cycle[cycle_idx % len(cycle)]
            cycle_idx += 1

            added = False
            if target_type == 'H' and h_idx < len(hard_list):
                result.append(hard_list[h_idx])
                h_idx += 1
                added = True
            elif target_type == 'M' and m_idx < len(medium_list):
                result.append(medium_list[m_idx])
                m_idx += 1
                added = True
            elif target_type == 'E' and e_idx < len(easy_list):
                result.append(easy_list[e_idx])
                e_idx += 1
                added = True

            if not added:
                # Fallback to whatever remains
                if mode in ('strength', 'weakness_mastered'):
                    fallback = [('H', hard_list, h_idx), ('M', medium_list, m_idx), ('E', easy_list, e_idx)]
                elif mode == 'weakness':
                    fallback = [('E', easy_list, e_idx), ('M', medium_list, m_idx), ('H', hard_list, h_idx)]
                else:
                    fallback = [('M', medium_list, m_idx), ('E', easy_list, e_idx), ('H', hard_list, h_idx)]

                for t, lst, idx in fallback:
                    if idx < len(lst):
                        result.append(lst[idx])
                        if t == 'H': h_idx += 1
                        elif t == 'M': m_idx += 1
                        elif t == 'E': e_idx += 1
                        break

        return result

    @classmethod
    def get_recommendations(cls, user, limit: int = 5) -> list:
        """
        Dashboard helper: returns top recommended unsolved challenges across all categories.
        """
        if user and user.is_authenticated:
            cache_key = f"ml_recom:user_{user.id}:lim_{limit}"
            cached = cache.get(cache_key)
            if cached:
                return cached

        # Get full personalized pool without deck truncation for dashboard diversity
        recs = cls.get_personalized_challenges(user, limit=limit * 2, apply_diversity_filter=True, is_dashboard=True)
        unsolved_recs = [r for r in recs if not r.get('isSolved')]
        candidates_to_use = unsolved_recs if unsolved_recs else recs

        dashboard_recs = []
        for r in candidates_to_use:
            dashboard_recs.append({
                'challenge': r,
                'recommendationScore': r.get('recommendationScore', 75),
                'predictedCategory': r.get('predictedCategory', 'appropriate'),
                'expectedSuccessProbability': r.get('expectedSuccessProbability', 0.70),
                'reason': r.get('reason', 'Recommended practice based on your skill profile.')
            })

        result = dashboard_recs[:limit]
        if user and user.is_authenticated:
            cache.set(f"ml_recom:user_{user.id}:lim_{limit}", result, timeout=15)
        return result

    @classmethod
    def get_personalized_challenges(
        cls, 
        user, 
        arena: str = None, 
        difficulty: str = None, 
        technology: str = None, 
        category: str = None, 
        search: str = None, 
        limit: int = None,
        apply_diversity_filter: bool = False,
        is_dashboard: bool = False
    ) -> list:
        """
        Core Personalization Engine:
        Instead of showing all 120 questions at once or dumping pure blocks of one difficulty:
        1. Curates a personalized subset (~20-26 questions) for this user.
        2. Tailors the quota according to registered strengths and weaknesses:
           - Strength: Majority Hard (e.g. 14 H), some Medium (8 M), few Easy (4 E).
           - Weakness: Mostly Easy to Medium (e.g. 14 E, 9 M, 3 H) until milestone of 20 solved.
           - Neutral: Balanced distribution.
        3. Interleaves them naturally: [Hard, Hard, Medium, Hard, Hard, Easy, ...] so the user
           is never presented with a monotonous single-difficulty block!
        """
        queryset = Challenge.objects.all().order_by('id')

        # Filter by arena / type
        if arena and arena.lower() != 'all':
            arena_low = arena.lower()
            if arena_low in ('sql', 'database'):
                queryset = queryset.filter(
                    Q(technology__iexact='SQL') | Q(title__startswith='[SQL-') | Q(id__gte=51, id__lte=85)
                )
            elif arena_low in ('frontend', 'studio', 'design'):
                queryset = queryset.filter(
                    Q(technology__in=['React', 'React Router', 'Web', 'CSS', 'HTML', 'Styling', 'Controlled Components']) |
                    Q(title__startswith='[FE-') | Q(title__startswith='[RE-') | Q(id__gte=86, id__lte=120)
                )
            elif arena_low in ('debugging', 'backend', 'code'):
                queryset = queryset.filter(
                    (
                        Q(technology__in=['Python', 'Django', 'NodeJS', 'JavaScript', 'Backend', 'FastAPI']) |
                        Q(title__startswith='[CODE-') | Q(title__startswith='[PY-') | Q(title__startswith='[JS-') |
                        Q(id__lte=50)
                    ) &
                    ~Q(title__startswith='[FE-') & ~Q(title__startswith='[RE-') & ~Q(title__startswith='[SQL-') &
                    ~Q(technology__iexact='SQL') &
                    ~Q(technology__in=['React', 'React Router', 'Web', 'CSS', 'HTML', 'Styling', 'Controlled Components'])
                )

        if difficulty and difficulty.lower() != 'all':
            queryset = queryset.filter(difficulty__iexact=difficulty)
        if technology and technology.lower() != 'all':
            queryset = queryset.filter(technology__iexact=technology)
        if category and category.lower() != 'all':
            queryset = queryset.filter(category__iexact=category)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(category__icontains=search) |
                Q(technology__icontains=search)
            )

        all_candidates = list(queryset)
        if not all_candidates:
            return []

        # If guest / unauthenticated, return plain listing
        if not user or not user.is_authenticated:
            results = []
            for c in all_candidates:
                c_dict = c.to_dict() if hasattr(c, 'to_dict') else c
                c_dict['isSolved'] = False
                c_dict['isPersonalized'] = False
                c_dict['recommendationScore'] = 50
                c_dict['reason'] = f"Practice challenge in {c_dict.get('category', c_dict.get('technology'))}."
                results.append(c_dict)
            return results[:limit] if limit else results

        # Authenticated User Processing
        user_submissions = list(Submission.objects.filter(user=user).select_related('challenge'))
        solved_challenge_ids = {s.challenge_id for s in user_submissions if s.success}
        solved_str_ids = {str(cid) for cid in solved_challenge_ids}

        # Calculate domain-specific solved counts
        domain_solved_counts = {'SQL': 0, 'Frontend': 0, 'Backend': 0}
        for s in user_submissions:
            if s.success and s.challenge:
                dom = cls.get_challenge_domain(s.challenge.technology, s.challenge.category, s.challenge.title, s.challenge.id)
                domain_solved_counts[dom] = domain_solved_counts.get(dom, 0) + 1

        user_strengths = getattr(user, 'strengths', []) or []
        user_weaknesses = getattr(user, 'weaknesses', []) or []

        # Determine the user's domain mode
        arena_target_domain = cls.ARENA_DOMAINS.get((arena or '').lower(), 'Backend')
        dom_solved = domain_solved_counts.get(arena_target_domain, 0)

        # Check if the overall arena matches weakness or strength
        arena_is_weakness = any(
            w.lower() in arena_target_domain.lower() or arena_target_domain.lower() in w.lower()
            for w in user_weaknesses
        )
        arena_is_strength = any(
            s.lower() in arena_target_domain.lower() or arena_target_domain.lower() in s.lower()
            for s in user_strengths
        )

        if arena_is_weakness:
            deck_mode = 'weakness' if dom_solved < 20 else 'weakness_mastered'
        elif arena_is_strength:
            deck_mode = 'strength'
        else:
            deck_mode = 'neutral'

        # If a specific difficulty filter was passed by the user (e.g. difficulty='Hard') or dashboard call,
        # do not truncate by quota; score all candidates directly.
        is_curated_deck = (not difficulty or difficulty.lower() == 'all') and not is_dashboard

        if is_curated_deck and len(all_candidates) > 10:
            # Separate by difficulty pool
            hard_pool = [c for c in all_candidates if (c.difficulty or '').capitalize() == 'Hard']
            med_pool = [c for c in all_candidates if (c.difficulty or '').capitalize() == 'Medium']
            easy_pool = [c for c in all_candidates if (c.difficulty or '').capitalize() == 'Easy']

            # Target quota based on arena and mode:
            if arena_target_domain in ('SQL', 'Frontend'):
                if deck_mode in ('strength', 'weakness_mastered'):
                    q_h, q_m, q_e = 9, 8, 3
                elif deck_mode == 'weakness':
                    q_h, q_m, q_e = 2, 8, 9
                else: # neutral
                    q_h, q_m, q_e = 5, 9, 6
            else: # Backend / Code Challenges
                if deck_mode in ('strength', 'weakness_mastered'):
                    q_h, q_m, q_e = 14, 8, 4 # 26 total: majority Hard!
                elif deck_mode == 'weakness':
                    q_h, q_m, q_e = 3, 9, 14 # 26 total: majority Easy!
                else: # neutral
                    q_h, q_m, q_e = 6, 12, 8 # 26 total: balanced!

            # Deterministically select subset for this user
            sel_hard = cls.user_deterministic_pick(user.id, hard_pool, min(q_h, len(hard_pool)), 'hard')
            sel_med = cls.user_deterministic_pick(user.id, med_pool, min(q_m, len(med_pool)), 'med')
            sel_easy = cls.user_deterministic_pick(user.id, easy_pool, min(q_e, len(easy_pool)), 'easy')

            # Interleave them into a non-monolithic, natural sequence
            interleaved_candidates = cls.interleave_deck(sel_hard, sel_med, sel_easy, mode=deck_mode)
        else:
            interleaved_candidates = all_candidates

        # Score and annotate candidates
        scored_results = []
        for rank_idx, c in enumerate(interleaved_candidates):
            c_dict = c.to_dict() if hasattr(c, 'to_dict') else c
            c_id = c.id
            c_id_str = str(c_id)
            c_diff = (c.difficulty or 'Easy').capitalize()
            c_tech = c.technology or 'General'
            c_cat = c.category or 'General'
            c_title = c.title or ''
            c_topics = c_dict.get('topics', [c_cat]) if hasattr(c, 'to_dict') else (getattr(c, 'topics', []) or [c_cat])
            c_domain = cls.get_challenge_domain(c_tech, c_cat, c_title, c_id)

            is_solved = c_id_str in solved_str_ids
            is_weakness = cls.matches_skill_set(c_tech, c_cat, c_topics, c_domain, user_weaknesses)
            is_strength = cls.matches_skill_set(c_tech, c_cat, c_topics, c_domain, user_strengths)

            c_dom_solved = domain_solved_counts.get(c_domain, 0)

            # Assign meaningful reasons and badges
            if is_weakness:
                if c_dom_solved < 10:
                    if c_diff == 'Easy':
                        base_score = 98.0
                        reason = f"Foundational {c_domain} challenge to build confidence in your growth area."
                        badge = "Growth: Foundation"
                    elif c_diff == 'Medium':
                        base_score = 80.0
                        reason = f"Intermediate {c_domain} challenge to step up your practice."
                        badge = "Growth: Intermediate"
                    else:
                        base_score = 55.0
                        reason = f"Advanced {c_domain} challenge (Solve 20 challenges to unlock mastery, currently {c_dom_solved}/20)."
                        badge = f"Growth: Mastery ({c_dom_solved}/20)"
                elif c_dom_solved < 20:
                    if c_diff == 'Medium':
                        base_score = 98.0
                        reason = f"Targeted {c_domain} challenge: Advanced from Easy as your skill improves ({c_dom_solved}/20 solved)."
                        badge = f"Growth: Targeted ({c_dom_solved}/20)"
                    elif c_diff == 'Easy':
                        base_score = 78.0
                        reason = f"Foundation practice in {c_domain}."
                        badge = "Growth: Foundation"
                    else:
                        base_score = 68.0
                        reason = f"Advanced challenge (Almost unlocked! Solve {20 - c_dom_solved} more to reach mastery)."
                        badge = f"Growth: Upcoming ({c_dom_solved}/20)"
                else: # c_dom_solved >= 20
                    if c_diff == 'Hard':
                        base_score = 99.0
                        reason = f"Mastery unlocked! Conquered 20+ {c_domain} challenges, now ready for hard debugging."
                        badge = "Growth: Mastery Unlocked"
                    elif c_diff == 'Medium':
                        base_score = 80.0
                        reason = f"Solidifying intermediate skills in {c_domain}."
                        badge = "Growth: Solidify"
                    else:
                        base_score = 52.0
                        reason = f"Quick review problem in {c_domain}."
                        badge = "Growth: Warmup"
            elif is_strength:
                if c_diff == 'Hard':
                    base_score = 95.0
                    reason = f"High-difficulty challenge recommended for your strength in {c_domain}."
                    badge = "Strength: Hard Focus"
                elif c_diff == 'Medium':
                    base_score = 78.0
                    reason = f"Intermediate challenge to maintain fast debugging in your {c_domain} strength."
                    badge = "Strength: Practice"
                else:
                    base_score = 50.0
                    reason = f"Refresher problem in {c_domain} (less prioritized for your strong background)."
                    badge = "Strength: Refresher"
            else:
                if c_diff == 'Medium':
                    base_score = 88.0
                    reason = f"Recommended practice challenge in {c_domain}."
                    badge = "Recommended: Medium"
                elif c_diff == 'Easy':
                    base_score = 82.0
                    reason = f"Starter practice challenge in {c_domain}."
                    badge = "Recommended: Easy"
                else:
                    base_score = 65.0
                    reason = f"Advanced challenge in {c_domain}."
                    badge = "Recommended: Hard"

            jitter = cls.get_user_challenge_jitter(user.id, c_id, arena or c_domain)
            final_score = round(base_score + jitter, 1)

            c_dict['recommendationScore'] = max(10, min(100, int(final_score)))
            c_dict['reason'] = reason
            c_dict['recommendationReason'] = reason
            c_dict['personalizedBadge'] = badge
            c_dict['isSolved'] = is_solved
            c_dict['isPersonalized'] = True
            c_dict['predictedCategory'] = 'appropriate' if base_score >= 70 else 'stretch'
            c_dict['expectedSuccessProbability'] = 0.85 if c_diff == 'Easy' else 0.65 if c_diff == 'Medium' else 0.45
            c_dict['domainSolvedCount'] = c_dom_solved
            c_dict['feedIndex'] = rank_idx

            if is_solved:
                c_dict['reason'] = f"Review challenge: You've already solved this {c_domain} challenge."
                c_dict['personalizedBadge'] = "Completed"

            scored_results.append(c_dict)

        if apply_diversity_filter:
            # Sort for dashboard recommendations by score
            unsolved_pool = [c for c in scored_results if not c['isSolved']]
            pool_to_filter = unsolved_pool if unsolved_pool else scored_results
            pool_to_filter.sort(key=lambda x: x['recommendationScore'], reverse=True)

            selected_div = []
            seen_domains = {}
            for item in pool_to_filter:
                dom = cls.get_challenge_domain(item.get('technology'), item.get('category'), item.get('title'), item.get('id'))
                seen_domains[dom] = seen_domains.get(dom, 0)
                if seen_domains[dom] < 2:
                    selected_div.append(item)
                    seen_domains[dom] += 1
                if limit and len(selected_div) >= limit:
                    break
            if limit and len(selected_div) < limit:
                sel_ids = {s['id'] for s in selected_div}
                for item in pool_to_filter:
                    if item['id'] not in sel_ids:
                        selected_div.append(item)
                    if len(selected_div) >= limit:
                        break
            return selected_div[:limit] if limit else selected_div

        if is_curated_deck and len(all_candidates) > 10:
            # Already curated and interleaved according to strength/weakness ratios
            return scored_results[:limit] if limit else scored_results

        # Non-deck or small test dataset: sort by recommendationScore descending
        unsolved_items = [c for c in scored_results if not c['isSolved']]
        solved_items = [c for c in scored_results if c['isSolved']]
        unsolved_items.sort(key=lambda x: x['recommendationScore'], reverse=True)
        solved_items.sort(key=lambda x: x['recommendationScore'], reverse=True)
        combined_sorted = unsolved_items + solved_items
        return combined_sorted[:limit] if limit else combined_sorted
