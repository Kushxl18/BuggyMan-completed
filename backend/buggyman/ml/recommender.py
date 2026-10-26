"""
Personalized Challenge Recommender for BuggyMan (Strength/Weakness Adaptive & Unique per User)
Tailors challenges in Code Challenges, SQL Lab, and Frontend Studio according to user's registered
strengths and weaknesses and solves milestones, ensuring every user gets a unique, personalized feed.
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
        ensuring that every user gets a unique personal challenge order while preserving
        difficulty tier ranking.
        """
        seed_str = f"usr_{user_id}_chl_{challenge_id}_arn_{arena_key}"
        digest = hashlib.md5(seed_str.encode('utf-8')).hexdigest()
        val = int(digest[:6], 16)
        jitter = ((val % 1000) / 1000.0) * 6.0 - 3.0
        return round(jitter, 2)

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

        recs = cls.get_personalized_challenges(user, limit=limit * 2, apply_diversity_filter=True)
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
        apply_diversity_filter: bool = False
    ) -> list:
        """
        Core Personalization Engine:
        Orders challenges uniquely for each user according to registered strengths and weaknesses:
        - Weakness: Easy questions first, Medium next, Hard questions held back until milestone of 20 solved.
        - Strength: Hard questions first (more hard questions), Medium next, less Easy questions.
        - Neutral: Natural progression calibrated to solve count.
        - Deterministic user jitter ensures unique challenge sequence per user.
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

        unsolved_scored = []
        solved_scored = []

        for c in all_candidates:
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

            dom_solved = domain_solved_counts.get(c_domain, 0)

            # SCORING & REASONING RULES:
            if is_weakness:
                # Weakness progression: Easy -> Medium -> Hard unlocked after 20 solved
                if dom_solved < 10:
                    if c_diff == 'Easy':
                        base_score = 98.0
                        reason = f"Foundational {c_domain} challenge to build confidence in your growth area."
                        badge = "Growth: Foundation"
                    elif c_diff == 'Medium':
                        base_score = 78.0
                        reason = f"Intermediate {c_domain} challenge to advance your skills as you practice."
                        badge = "Growth: Intermediate"
                    else: # Hard
                        base_score = 42.0
                        reason = f"Advanced {c_domain} challenge (Solve 20 {c_domain} challenges to unlock mastery, currently {dom_solved}/20)."
                        badge = f"Growth: Mastery ({dom_solved}/20)"
                elif dom_solved < 20:
                    if c_diff == 'Medium':
                        base_score = 98.0
                        reason = f"Targeted {c_domain} challenge: Stepped up to Medium based on your progress ({dom_solved}/20 solved)."
                        badge = f"Growth: Targeted ({dom_solved}/20)"
                    elif c_diff == 'Easy':
                        base_score = 75.0
                        reason = f"Foundation practice in {c_domain}."
                        badge = "Growth: Foundation"
                    else: # Hard
                        base_score = 66.0
                        reason = f"Advanced challenge (Almost unlocked! Solve {20 - dom_solved} more to reach mastery)."
                        badge = f"Growth: Upcoming ({dom_solved}/20)"
                else: # dom_solved >= 20
                    if c_diff == 'Hard':
                        base_score = 99.0
                        reason = f"Mastery unlocked! Conquered 20+ {c_domain} challenges, now ready for hard debugging."
                        badge = "Growth: Mastery Unlocked"
                    elif c_diff == 'Medium':
                        base_score = 78.0
                        reason = f"Solidifying intermediate skills in {c_domain}."
                        badge = "Growth: Solidify"
                    else: # Easy
                        base_score = 50.0
                        reason = f"Quick review problem in {c_domain}."
                        badge = "Growth: Warmup"

            elif is_strength:
                # Strength focus: Hard first (more hard questions), then Medium, less Easy
                if c_diff == 'Hard':
                    base_score = 94.0
                    reason = f"High-difficulty challenge recommended for your strength in {c_domain}."
                    badge = "Strength: Hard Focus"
                elif c_diff == 'Medium':
                    base_score = 76.0
                    reason = f"Intermediate challenge to maintain fast debugging in your {c_domain} strength."
                    badge = "Strength: Practice"
                else: # Easy
                    base_score = 45.0
                    reason = f"Refresher problem in {c_domain} (less prioritized for your strong background)."
                    badge = "Strength: Refresher"

            else:
                # Neutral balanced progression
                if dom_solved < 5:
                    if c_diff == 'Easy':
                        base_score = 88.0
                        reason = f"Recommended starter challenge in {c_domain}."
                        badge = "Recommended: Easy"
                    elif c_diff == 'Medium':
                        base_score = 70.0
                        reason = f"Recommended intermediate practice in {c_domain}."
                        badge = "Recommended: Medium"
                    else:
                        base_score = 48.0
                        reason = f"Advanced practice challenge in {c_domain}."
                        badge = "Recommended: Hard"
                elif dom_solved < 15:
                    if c_diff == 'Medium':
                        base_score = 88.0
                        reason = f"Recommended challenge calibrated to your experience in {c_domain} ({dom_solved} solved)."
                        badge = "Recommended: Medium"
                    elif c_diff == 'Easy':
                        base_score = 72.0
                        reason = f"Quick practice challenge in {c_domain}."
                        badge = "Recommended: Easy"
                    else:
                        base_score = 60.0
                        reason = f"Stretch challenge in {c_domain}."
                        badge = "Recommended: Hard"
                else:
                    if c_diff == 'Hard':
                        base_score = 88.0
                        reason = f"Advanced challenge for experienced solver in {c_domain} ({dom_solved} solved)."
                        badge = "Recommended: Hard"
                    elif c_diff == 'Medium':
                        base_score = 74.0
                        reason = f"Intermediate practice in {c_domain}."
                        badge = "Recommended: Medium"
                    else:
                        base_score = 52.0
                        reason = f"Warmup challenge in {c_domain}."
                        badge = "Recommended: Easy"

            # Compute user-unique deterministic jitter
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
            c_dict['domainSolvedCount'] = dom_solved

            if is_solved:
                c_dict['recommendationScore'] = max(10, int(final_score - 40))
                c_dict['reason'] = f"Review challenge: You've already solved this {c_domain} challenge."
                c_dict['personalizedBadge'] = "Completed"
                solved_scored.append(c_dict)
            else:
                unsolved_scored.append(c_dict)

        # Sort unsolved descending by score
        unsolved_scored.sort(key=lambda x: x['recommendationScore'], reverse=True)
        # Sort solved descending by score
        solved_scored.sort(key=lambda x: x['recommendationScore'], reverse=True)

        if apply_diversity_filter:
            selected_unsolved = []
            seen_domains = {}
            for item in unsolved_scored:
                dom = cls.get_challenge_domain(item.get('technology'), item.get('category'), item.get('title'), item.get('id'))
                seen_domains[dom] = seen_domains.get(dom, 0)
                if seen_domains[dom] < 2:
                    selected_unsolved.append(item)
                    seen_domains[dom] += 1
                if limit and len(selected_unsolved) >= limit:
                    break
            if limit and len(selected_unsolved) < limit:
                selected_ids = {s['id'] for s in selected_unsolved}
                for item in unsolved_scored:
                    if item['id'] not in selected_ids:
                        selected_unsolved.append(item)
                    if len(selected_unsolved) >= limit:
                        break
            unsolved_scored = selected_unsolved

        combined = unsolved_scored + solved_scored
        return combined[:limit] if limit else combined
