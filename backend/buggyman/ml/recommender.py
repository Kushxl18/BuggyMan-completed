"""
Personalized Challenge Recommender for BuggyMan ML Layer (Phase 4 Task 4)
"""
from django.core.cache import cache
from buggyman.models import Challenge, Submission
from buggyman.ml.difficulty_predictor import DifficultyPredictor
from buggyman.ml.analytics_collector import AnalyticsCollector
from buggyman.ml.adaptive_difficulty import AdaptiveDifficultyManager

class ChallengeRecommender:
    @classmethod
    def get_recommendations(cls, user, limit: int = 5) -> list:
        """
        Returns a ranked list of recommended challenges with human-readable explanations.
        """
        if user and user.is_authenticated:
            cache_key = f"ml_recom:user_{user.id}:lim_{limit}"
            cached = cache.get(cache_key)
            if cached:
                return cached

        all_challenges = list(Challenge.objects.all())
        if not all_challenges:
            return []

        if not user or not user.is_authenticated:
            return [
                {
                    'challenge': c.to_dict(),
                    'recommendationScore': 80,
                    'predictedCategory': 'appropriate',
                    'expectedSuccessProbability': 0.70,
                    'reason': f"Great beginner challenge in {c.technology} ({c.difficulty} difficulty)."
                }
                for c in all_challenges[:limit]
            ]

        analytics = AnalyticsCollector.get_user_analytics_data(user)
        tech_perf = analytics.get('technologyPerformance', {})
        cat_perf = analytics.get('categoryPerformance', {})
        adaptive_state = AdaptiveDifficultyManager.get_user_adaptive_state(user)
        recommended_tier = adaptive_state.get('recommendedTier', 'Easy')
        
        solved_ids = {str(s.challenge_id) for s in Submission.objects.filter(user=user, success=True)}
        
        # Filter out already solved challenges unless all challenges are solved
        unsolved = [c for c in all_challenges if str(c.id) not in solved_ids]
        candidates = unsolved if unsolved else all_challenges

        scored_list = []
        for c in candidates:
            pred = DifficultyPredictor.predict_difficulty(user, c)
            prob = pred.get('expectedSuccessProbability', 0.5)

            # Adaptive tier match bonus
            tier_bonus = 20 if (c.difficulty or 'Easy').lower() == recommended_tier.lower() else 0

            # Difficulty suitability score (peaks in 0.55 - 0.78 zone)
            if 0.55 <= prob <= 0.78:
                suitability_score = 100
            elif 0.40 <= prob < 0.55 or 0.78 < prob <= 0.85:
                suitability_score = 75
            elif prob > 0.85:
                suitability_score = 40
            else:
                suitability_score = 30

            # Weakness alignment score
            tech_stat = tech_perf.get(c.technology, {})
            cat_stat = cat_perf.get(c.category, {})
            tech_acc = tech_stat.get('accuracyRate', 100.0) if tech_stat else 50.0
            cat_acc = cat_stat.get('accuracyRate', 100.0) if cat_stat else 50.0

            weakness_score = round(max(0, 100 - min(tech_acc, cat_acc)))

            composite_score = min(100, round((suitability_score * 0.5) + (weakness_score * 0.35) + (tier_bonus * 0.8)))

            # Human-readable reasoning explanation
            if str(c.id) in solved_ids:
                reason = f"Review challenge to reinforce your {c.technology} skills."
            elif tech_acc < 60:
                reason = f"Targeted practice for {c.technology} (your current accuracy is {tech_acc}%). Fits your optimal learning zone."
            elif 0.55 <= prob <= 0.78:
                reason = f"Ideal match for your skill level. Expected success probability is {int(prob*100)}%."
            elif c.difficulty == 'Medium' and tech_acc >= 75:
                reason = f"Level-up challenge in {c.technology} to transition from Easy to Medium mastery."
            else:
                reason = f"Recommended practice in {c.category} to expand your debugging breadth."

            scored_list.append({
                'challenge': c.to_dict(),
                'recommendationScore': composite_score,
                'predictedCategory': pred.get('predictedCategory'),
                'expectedSuccessProbability': prob,
                'reason': reason
            })

        scored_list.sort(key=lambda x: x['recommendationScore'], reverse=True)
        result = scored_list[:limit]
        if user and user.is_authenticated:
            cache.set(cache_key, result, timeout=15)
        return result
