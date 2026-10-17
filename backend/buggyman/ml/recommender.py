"""
Personalized Challenge Recommender for BuggyMan (Rule-Based & Explainable)
Computes personalized recommendation scores for challenges per user across all pages.
"""
from django.core.cache import cache
from django.db.models import Q
from buggyman.models import Challenge, Submission
from buggyman.ml.skill_profiler import SkillProfiler
from buggyman.ml.analytics_collector import AnalyticsCollector

class ChallengeRecommender:
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

        # Fetch personalized challenges across all categories
        recs = cls.get_personalized_challenges(user, limit=limit * 2, apply_diversity_filter=True)
        
        # Format for Dashboard UI compatibility: filter out solved challenges unless all are solved
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
        Core Reusable Personalization Engine:
        Calculates weighted personalized scores for challenges matching filters,
        annotating each candidate dictionary with:
        - recommendationScore
        - reason / recommendationReason
        - isSolved (True if solved by user, False otherwise)
        - isPersonalized (True if authenticated, False if guest)

        Orders candidates: Unsolved candidates ranked by recommendationScore descending,
        followed by solved candidates ranked by recommendationScore.
        """
        queryset = Challenge.objects.all().order_by('id')

        # Filter by arena / type
        if arena and arena.lower() != 'all':
            arena_low = arena.lower()
            if arena_low in ('sql', 'database'):
                queryset = queryset.filter(Q(technology__iexact='SQL') | Q(title__startswith='[SQL-'))
            elif arena_low in ('frontend', 'studio', 'design'):
                queryset = queryset.filter(
                    Q(technology__in=['React', 'React Router', 'Web', 'CSS', 'HTML', 'Styling', 'Controlled Components']) |
                    Q(title__startswith='[RE-') | Q(title__startswith='[FE-')
                )
            elif arena_low in ('debugging', 'backend', 'code'):
                queryset = queryset.filter(
                    Q(technology__in=['Python', 'Django', 'NodeJS', 'JavaScript', 'Backend', 'FastAPI']) |
                    Q(title__startswith='[PY-') | Q(title__startswith='[JS-')
                )

        # Filter by difficulty, technology, category, search
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

        # If user is guest/unauthenticated, return plain listing with default metadata
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

        # Authenticated User Personalization Pipeline
        solved_challenge_ids = set(
            Submission.objects.filter(user=user, success=True).values_list('challenge_id', flat=True)
        )
        solved_str_ids = {str(cid) for cid in solved_challenge_ids}

        skill_profile = SkillProfiler.calculate_skill_matrix(user)
        cat_skills = skill_profile.get('categorySkills', {})
        topic_skills = skill_profile.get('topicSkills', {})
        overall_prof = skill_profile.get('overallProficiency', 0)
        user_strengths = skill_profile.get('strengths', [])
        user_weaknesses = skill_profile.get('weaknesses', [])

        analytics = AnalyticsCollector.get_user_analytics_data(user)
        recent_history = analytics.get('completionHistory', [])[-5:]
        recent_failed_cats = {
            h.get('category') for h in recent_history if not h.get('success')
        }

        # Target difficulty tuning based on proficiency
        if overall_prof < 45:
            target_diff = 'Easy'
        elif overall_prof < 75:
            target_diff = 'Medium'
        else:
            target_diff = 'Hard'

        unsolved_scored = []
        solved_scored = []

        for c in all_candidates:
            c_dict = c.to_dict() if hasattr(c, 'to_dict') else c
            c_id_str = str(c_dict.get('id', ''))
            c_diff = (c_dict.get('difficulty') or 'Easy').capitalize()
            c_tech = c_dict.get('technology') or 'General'
            c_cat = c_dict.get('category') or 'General'
            c_topics = c_dict.get('topics', [c_cat])
            is_solved = c_id_str in solved_str_ids

            # A. Difficulty Suitability Score (30 pts max)
            if c_diff == target_diff:
                diff_score = 30
            elif (target_diff == 'Medium' and c_diff in ['Easy', 'Hard']) or (target_diff == 'Easy' and c_diff == 'Medium') or (target_diff == 'Hard' and c_diff == 'Medium'):
                diff_score = 20
            else:
                diff_score = 10

            # B. Topic & Skill Gap Score (40 pts max)
            relevant_scores = []
            for t in c_topics:
                if t in topic_skills:
                    relevant_scores.append(topic_skills[t])

            cat_name = SkillProfiler._tech_to_category(c_tech)
            relevant_scores.append(cat_skills.get(cat_name, 50 if (user_strengths or user_weaknesses) else 0))
            relevant_scores.append(cat_skills.get(c_cat, 50 if (user_strengths or user_weaknesses) else 0))

            min_skill = min(relevant_scores) if relevant_scores else 0
            weakness_gap_score = round((100 - min_skill) * 0.4)

            # Registration Weakness Bonus (+20 pts)
            is_reg_weakness = any(
                SkillProfiler._matches_category(c, w) or
                w.lower() in c_tech.lower() or w.lower() in c_cat.lower() or any(w.lower() in t.lower() for t in c_topics)
                for w in user_weaknesses
            )
            reg_weakness_bonus = 20 if is_reg_weakness else 0

            # Recency Failure Bonus (+10 pts)
            recent_fail_bonus = 10 if c_cat in recent_failed_cats else 0

            # Registration Strength Bonus (+5 pts)
            is_reg_strength = any(
                SkillProfiler._matches_category(c, s) or
                s.lower() in c_tech.lower() or s.lower() in c_cat.lower() or any(s.lower() in t.lower() for t in c_topics)
                for s in user_strengths
            )
            reg_strength_bonus = 5 if is_reg_strength else 0

            total_score = min(100, max(10, diff_score + weakness_gap_score + reg_weakness_bonus + recent_fail_bonus + reg_strength_bonus))

            # Reasoning Explanation
            primary_topic = c_topics[0] if c_topics else c_cat
            if is_solved:
                reason = f"Review challenge to reinforce your {c_tech} skills."
            elif is_reg_weakness or min_skill < 50:
                reason = f"Recommended for your {primary_topic} skill gap ({min_skill}% mastery)."
            elif recent_fail_bonus > 0:
                reason = f"Targeted practice for {c_cat} based on your recent attempt."
            elif is_reg_strength:
                reason = f"Recommended based on your strength in {c_tech} to build advanced mastery."
            elif c_diff == 'Medium' and min_skill >= 60:
                reason = f"Level-up challenge in {c_tech} from Easy to Medium."
            else:
                reason = f"Recommended practice in {c_cat} adapted to your profile."

            c_dict['recommendationScore'] = total_score
            c_dict['reason'] = reason
            c_dict['recommendationReason'] = reason
            c_dict['isSolved'] = is_solved
            c_dict['isPersonalized'] = True
            c_dict['predictedCategory'] = 'appropriate' if diff_score >= 20 else 'stretch'
            c_dict['expectedSuccessProbability'] = round(min_skill / 100.0, 2)

            if is_solved:
                solved_scored.append(c_dict)
            else:
                unsolved_scored.append(c_dict)

        # Sort unsolved candidates descending by score
        unsolved_scored.sort(key=lambda x: x['recommendationScore'], reverse=True)
        # Sort solved candidates descending by score
        solved_scored.sort(key=lambda x: x['recommendationScore'], reverse=True)

        if apply_diversity_filter:
            selected_unsolved = []
            seen_pages = {}
            for item in unsolved_scored:
                page = item.get('page', 'Code Challenges')
                seen_pages[page] = seen_pages.get(page, 0)
                if seen_pages[page] < 2:
                    selected_unsolved.append(item)
                    seen_pages[page] += 1
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
