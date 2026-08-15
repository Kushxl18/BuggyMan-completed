"""
Difficulty Predictor for BuggyMan Adaptive Learning & ML Layer (Phase 4 Task 3)
"""
import math
from buggyman.models import Submission, Challenge
from buggyman.ml.skill_profiler import SkillProfiler
from buggyman.ml.analytics_collector import AnalyticsCollector

class DifficultyPredictor:
    DIFFICULTY_NUMERICAL = {
        'easy': 30,
        'medium': 60,
        'hard': 85
    }

    @classmethod
    def predict_difficulty(cls, user, challenge: Challenge) -> dict:
        """
        Estimates whether a challenge is 'too_easy', 'appropriate', or 'too_difficult'
        for a particular user based on technology skills, category history, and attempts.
        """
        if not user or not user.is_authenticated:
            return {
                'challengeId': str(challenge.id),
                'challengeTitle': challenge.title,
                'difficulty': challenge.difficulty,
                'technology': challenge.technology,
                'predictedCategory': 'appropriate',
                'expectedSuccessProbability': 0.70,
                'confidenceScore': 0.50,
                'userTechSkill': 50,
                'reasoning': 'Default baseline prediction for guest/unauthenticated user.'
            }

        matrix = SkillProfiler.calculate_skill_matrix(user)
        tech_skills = matrix.get('technologySkills', {})
        cat_skills = matrix.get('categorySkills', {})

        normalized_tech = SkillProfiler._normalize_tech(challenge.technology)
        user_tech_skill = tech_skills.get(challenge.technology, tech_skills.get(normalized_tech, 50))
        user_cat_skill = cat_skills.get(challenge.category, user_tech_skill)

        # Baseline difficulty threshold
        diff_str = (challenge.difficulty or 'Easy').lower().strip()
        challenge_diff_val = cls.DIFFICULTY_NUMERICAL.get(diff_str, 45)

        # Prior history on this specific challenge
        prior_subs = Submission.objects.filter(user=user, challenge=challenge)
        prior_attempts = prior_subs.count()
        already_solved = prior_subs.filter(success=True).exists()

        # Skill delta equation
        combined_skill = (user_tech_skill * 0.6) + (user_cat_skill * 0.4)
        delta = (combined_skill - challenge_diff_val) / 35.0

        # Sigmoid probability
        prob = 1.0 / (1.0 + math.exp(-2.2 * delta))

        # Adjust for prior performance on this challenge
        if already_solved:
            prob = min(0.98, prob + 0.20)
        elif prior_attempts >= 3:
            prob = max(0.10, prob - 0.25)
        elif prior_attempts > 0:
            prob = max(0.15, prob - 0.10)

        prob = round(min(0.99, max(0.05, prob)), 2)

        # Classification rules
        if prob > 0.82:
            predicted_category = 'too_easy'
            reasoning = f"High probability of success ({int(prob*100)}%). Your {challenge.technology} proficiency ({user_tech_skill}/100) comfortably exceeds this {challenge.difficulty} challenge."
        elif prob >= 0.40:
            predicted_category = 'appropriate'
            reasoning = f"Optimal learning zone ({int(prob*100)}% expected success rate). Ideal match for your current {challenge.technology} skill level."
        else:
            predicted_category = 'too_difficult'
            reasoning = f"High challenge curve ({int(prob*100)}% expected success rate). Your {challenge.technology} skill ({user_tech_skill}/100) is below the recommended threshold for this {challenge.difficulty} problem."

        confidence = 0.85 if prior_attempts > 0 else 0.70

        return {
            'challengeId': str(challenge.id),
            'challengeTitle': challenge.title,
            'difficulty': challenge.difficulty,
            'technology': challenge.technology,
            'category': challenge.category,
            'predictedCategory': predicted_category,
            'expectedSuccessProbability': prob,
            'confidenceScore': confidence,
            'userTechSkill': user_tech_skill,
            'alreadySolved': already_solved,
            'priorAttempts': prior_attempts,
            'reasoning': reasoning
        }
