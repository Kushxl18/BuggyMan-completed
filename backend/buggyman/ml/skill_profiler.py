"""
Skill Profiler for BuggyMan Personalized Recommendation System
Maintains dynamic skill profile matrices based on registration preferences and real performance data.
"""
from buggyman.models import Submission, Challenge
from buggyman.ml.analytics_collector import AnalyticsCollector

class SkillProfiler:
    CATEGORIES_BENCHMARK = [
        'Backend', 'SQL', 'Frontend', 'APIs', 'Security', 'Testing', 'DevOps', 'Database'
    ]
    TECH_BENCHMARKS = ['Python', 'JavaScript', 'React', 'SQL', 'HTML/CSS', 'Django']

    @classmethod
    def calculate_skill_matrix(cls, user) -> dict:
        """
        Calculates dynamic proficiency scores (0-100) across technologies, broad skill categories,
        and specific topics using user preferences and actual submission performance.
        """
        if not user or not user.is_authenticated:
            return cls._get_empty_matrix()

        analytics = AnalyticsCollector.get_user_analytics_data(user)
        submissions = list(Submission.objects.filter(user=user).select_related('challenge'))
        total_user_submissions = len(submissions)

        user_strengths = [s.strip() for s in getattr(user, 'strengths', []) or []]
        user_weaknesses = [w.strip() for w in getattr(user, 'weaknesses', []) or []]

        # Cold start unseeded user with 0 submissions
        if total_user_submissions == 0 and not user_strengths and not user_weaknesses:
            return {
                'userId': user.id,
                'username': user.username,
                'overallProficiency': 0,
                'proficiencyLevel': 'Novice',
                'strengths': [],
                'weaknesses': [],
                'categorySkills': {cat: 0 for cat in cls.CATEGORIES_BENCHMARK},
                'technologySkills': {tech: 0 for tech in cls.TECH_BENCHMARKS},
                'topicSkills': {},
                'totalSolved': 0,
                'totalSubmissions': 0
            }

        category_skills = {}
        for cat in cls.CATEGORIES_BENCHMARK:
            cat_subs = [
                s for s in submissions
                if s.challenge and cls._matches_category(s.challenge, cat)
            ]
            
            baseline = 50
            for str_item in user_strengths:
                if cls._normalized(str_item) in cls._normalized(cat) or cls._normalized(cat) in cls._normalized(str_item):
                    baseline = 75
                    break
            for wk_item in user_weaknesses:
                if cls._normalized(wk_item) in cls._normalized(cat) or cls._normalized(cat) in cls._normalized(wk_item):
                    baseline = 35
                    break

            if not cat_subs:
                category_skills[cat] = baseline if (user_strengths or user_weaknesses) else 0
            else:
                solved_subs = [s for s in cat_subs if s.success]
                solved_count = len({s.challenge_id for s in solved_subs})
                attempts_count = len(cat_subs)

                accuracy = (solved_count / max(1, attempts_count)) * 100
                vol_bonus = min(30, solved_count * 10)
                perf_score = min(100, round((accuracy * 0.7) + vol_bonus))

                actual_weight = min(1.0, attempts_count * 0.25)
                bl_weight = 1.0 - actual_weight
                final_cat_score = round((perf_score * actual_weight) + (baseline * bl_weight))
                category_skills[cat] = min(100, max(5, final_cat_score))

        tech_skills = {}
        for tech in cls.TECH_BENCHMARKS:
            tech_subs = [
                s for s in submissions
                if s.challenge and cls._normalize_tech(s.challenge.technology) == cls._normalize_tech(tech)
            ]
            if not tech_subs:
                matched_cat = cls._tech_to_category(tech)
                tech_skills[tech] = category_skills.get(matched_cat, 50 if (user_strengths or user_weaknesses) else 0)
            else:
                solved_challenges = {s.challenge_id for s in tech_subs if s.success}
                total_attempts = len(tech_subs)
                solved_count = len(solved_challenges)

                if solved_count == 0:
                    tech_skills[tech] = 20
                    continue

                weighted_points = 0.0
                for s in tech_subs:
                    if s.success:
                        diff = (s.challenge.difficulty or 'Easy').lower()
                        diff_weight = 1.0 if diff == 'easy' else 1.5 if diff == 'medium' else 2.0
                        penalty = (max(0, s.attempt_number - 1) * 0.05) + (s.hints_used * 0.05)
                        weighted_points += max(0.5, diff_weight - penalty)

                accuracy_ratio = solved_count / max(1, total_attempts)
                volume_multiplier = min(1.0, 0.4 + (solved_count * 0.2))
                raw_score = (accuracy_ratio * 60) + (volume_multiplier * 40) + (weighted_points * 5)
                tech_skills[tech] = min(100, max(15, round(raw_score)))

        topic_skills = {}
        all_challenges = Challenge.objects.all()
        for c in all_challenges:
            c_dict = c.to_dict()
            topics = c_dict.get('topics', [])
            for t in topics:
                if not t:
                    continue
                t_subs = [s for s in submissions if s.challenge and t in s.challenge.to_dict().get('topics', [])]
                if not t_subs:
                    cat_name = cls._tech_to_category(c.technology)
                    topic_skills[t] = category_skills.get(cat_name, 50 if (user_strengths or user_weaknesses) else 0)
                else:
                    t_solved = [s for s in t_subs if s.success]
                    acc = len(t_solved) / len(t_subs)
                    topic_skills[t] = min(100, max(10, round(acc * 100)))

        active_scores = list(category_skills.values())
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
            'strengths': user_strengths,
            'weaknesses': user_weaknesses,
            'categorySkills': category_skills,
            'technologySkills': tech_skills,
            'topicSkills': topic_skills,
            'totalSolved': analytics.get('solvedCount', 0),
            'totalSubmissions': total_user_submissions
        }

    @classmethod
    def update_user_skills(cls, user) -> dict:
        """
        Recalculates user proficiency matrix and updates user.skills in DB.
        """
        matrix = cls.calculate_skill_matrix(user)
        if user and user.is_authenticated:
            combined = {**matrix['technologySkills'], **matrix['categorySkills']}
            user.skills = combined
            user.save(update_fields=['skills'])
        return matrix

    @classmethod
    def _get_empty_matrix(cls) -> dict:
        empty_cats = {cat: 0 for cat in cls.CATEGORIES_BENCHMARK}
        empty_techs = {tech: 0 for tech in cls.TECH_BENCHMARKS}
        return {
            'userId': None,
            'username': 'Guest',
            'overallProficiency': 0,
            'proficiencyLevel': 'Novice',
            'strengths': [],
            'weaknesses': [],
            'categorySkills': empty_cats,
            'technologySkills': empty_techs,
            'topicSkills': {},
            'totalSolved': 0,
            'totalSubmissions': 0
        }

    @classmethod
    def _matches_category(cls, challenge: Challenge, target_category: str) -> bool:
        t_norm = cls._normalized(target_category)
        c_tech = cls._normalized(challenge.technology)
        c_cat = cls._normalized(challenge.category)

        if t_norm in c_tech or c_tech in t_norm or t_norm in c_cat or c_cat in t_norm:
            return True

        if t_norm == 'backend' and any(k in c_tech or k in c_cat for k in ['python', 'django', 'node', 'express', 'backend', 'logic']):
            return True
        if t_norm in ['sql', 'database'] and any(k in c_tech or k in c_cat for k in ['sql', 'database', 'schema', 'query', 'join']):
            return True
        if t_norm == 'frontend' and any(k in c_tech or k in c_cat for k in ['react', 'css', 'html', 'frontend', 'ui', 'form', 'events']):
            return True

        return False

    @classmethod
    def _tech_to_category(cls, tech_name: str) -> str:
        t = cls._normalized(tech_name)
        if 'sql' in t or 'db' in t or 'database' in t:
            return 'SQL'
        if 'react' in t or 'css' in t or 'html' in t or 'front' in t:
            return 'Frontend'
        return 'Backend'

    @staticmethod
    def _normalized(s: str) -> str:
        return (s or '').lower().strip()

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
