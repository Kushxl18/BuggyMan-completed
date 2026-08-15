"""
Skill Profiler for BuggyMan Adaptive Learning & ML Layer (Phase 4 Task 2)
"""
from buggyman.models import Submission, Challenge
from buggyman.ml.analytics_collector import AnalyticsCollector

class SkillProfiler:
    TECH_BENCHMARKS = ['Python', 'JavaScript', 'React', 'SQL', 'HTML/CSS', 'Django']
    
    @classmethod
    def calculate_skill_matrix(cls, user) -> dict:
        """
        Calculates dynamic proficiency scores (0-100) across technologies and categories
        using actual user performance data.
        """
        analytics = AnalyticsCollector.get_user_analytics_data(user)
        tech_perf = analytics.get('technologyPerformance', {})
        cat_perf = analytics.get('categoryPerformance', {})
        submissions = Submission.objects.filter(user=user).select_related('challenge')

        tech_skills = {}
        # Calculate technology proficiency
        for tech in cls.TECH_BENCHMARKS:
            # Check matching submissions
            tech_subs = [s for s in submissions if s.challenge and cls._normalize_tech(s.challenge.technology) == cls._normalize_tech(tech)]
            if not tech_subs:
                tech_skills[tech] = 0
                continue

            solved_challenges = {s.challenge_id for s in tech_subs if s.success}
            total_attempts = len(tech_subs)
            solved_count = len(solved_challenges)

            if solved_count == 0:
                tech_skills[tech] = 10  # Attempted but not yet solved
                continue

            # Weight by difficulty
            weighted_points = 0.0
            for s in tech_subs:
                if s.success:
                    diff = (s.challenge.difficulty or 'Easy').lower()
                    diff_weight = 1.0 if diff == 'easy' else 1.5 if diff == 'medium' else 2.0
                    # Deduct small penalty for repeated attempts & hints
                    penalty = (max(0, s.attempt_number - 1) * 0.05) + (s.hints_used * 0.05)
                    weighted_points += max(0.5, diff_weight - penalty)

            accuracy_ratio = solved_count / max(1, total_attempts)
            volume_multiplier = min(1.0, 0.4 + (solved_count * 0.2))
            
            # Raw score formula
            raw_score = (accuracy_ratio * 60) + (volume_multiplier * 40) + (weighted_points * 5)
            tech_skills[tech] = min(100, max(15, round(raw_score)))

        # Calculate category proficiency
        cat_skills = {}
        for cat, perf in cat_perf.items():
            if not cat:
                continue
            subs_count = perf.get('submissionsCount', 0)
            succ_count = perf.get('successCount', 0)
            acc = perf.get('accuracyRate', 0.0)
            vol = min(1.0, 0.3 + (succ_count * 0.25))
            score = round((acc * 0.7) + (vol * 30))
            cat_skills[cat] = min(100, max(10, score))

        # Overall Mastery Score
        active_scores = [v for v in tech_skills.values() if v > 0]
        overall_score = round(sum(active_scores) / len(active_scores)) if active_scores else 0

        level = 'Novice'
        if overall_score >= 85:
            level = 'Master'
        elif overall_score >= 70:
            level = 'Expert'
        elif overall_score >= 50:
            level = 'Practitioner'
        elif overall_score >= 25:
            level = 'Apprentice'

        return {
            'userId': user.id,
            'username': user.username,
            'overallProficiency': overall_score,
            'proficiencyLevel': level,
            'technologySkills': tech_skills,
            'categorySkills': cat_skills,
            'totalSolved': analytics.get('solvedCount', 0),
            'totalSubmissions': analytics.get('totalSubmissions', 0)
        }

    @classmethod
    def update_user_skills(cls, user) -> dict:
        """
        Recalculates user proficiency and updates user.skills in database.
        """
        matrix = cls.calculate_skill_matrix(user)
        user.skills = matrix['technologySkills']
        user.save(update_fields=['skills'])
        return matrix

    @staticmethod
    def _normalize_tech(tech_name: str) -> str:
        t = (tech_name or '').lower().strip()
        if 'py' in t:
            return 'python'
        if 'react' in t:
            return 'react'
        if 'sql' in t:
            return 'sql'
        if 'css' in t or 'html' in t:
            return 'html/css'
        if 'django' in t:
            return 'django'
        if 'js' in t or 'javascript' in t:
            return 'javascript'
        return t
