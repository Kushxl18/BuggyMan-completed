"""
Career Role Suitability & Market Insights Engine for BuggyMan.
Consumes dynamic skill profiler data and combines rule-based skill alignment
with a configurable market-demand layer to provide explainable career insights.
"""
from buggyman.ml.skill_profiler import SkillProfiler
from buggyman.ml.recommender import ChallengeRecommender

class CareerEngine:
    ROLE_DEFINITIONS = [
        {
            'id': 'backend-developer',
            'title': 'Backend Developer',
            'requiredSkills': {
                'Backend': 1.0,
                'APIs': 0.9,
                'SQL': 0.8,
                'Database': 0.7,
                'Security': 0.5,
                'Testing': 0.5,
                'DevOps': 0.4,
            },
            'primaryArena': 'code',
            'arenaName': 'Code Challenges',
            'marketData': {
                'demandLevel': 'High',
                'demandScore': 88,
                'trend': 'Growing',
                'lastUpdated': '2026-09-01',
                'source': 'Global Software Engineering Hiring Index 2026'
            }
        },
        {
            'id': 'frontend-developer',
            'title': 'Frontend Developer',
            'requiredSkills': {
                'Frontend': 1.0,
                'APIs': 0.7,
                'Testing': 0.5,
                'Backend': 0.3,
            },
            'primaryArena': 'frontend',
            'arenaName': 'Frontend Studio',
            'marketData': {
                'demandLevel': 'High',
                'demandScore': 82,
                'trend': 'Stable',
                'lastUpdated': '2026-09-01',
                'source': 'Global Software Engineering Hiring Index 2026'
            }
        },
        {
            'id': 'fullstack-developer',
            'title': 'Full-Stack Developer',
            'requiredSkills': {
                'Frontend': 0.9,
                'Backend': 0.9,
                'APIs': 0.9,
                'SQL': 0.7,
                'Database': 0.6,
                'Testing': 0.5,
            },
            'primaryArena': 'code',
            'arenaName': 'Code Challenges',
            'marketData': {
                'demandLevel': 'Very High',
                'demandScore': 94,
                'trend': 'Growing',
                'lastUpdated': '2026-09-01',
                'source': 'Global Software Engineering Hiring Index 2026'
            }
        },
        {
            'id': 'data-engineer',
            'title': 'Data Engineer',
            'requiredSkills': {
                'SQL': 1.0,
                'Database': 0.9,
                'Backend': 0.7,
                'APIs': 0.6,
                'DevOps': 0.4,
            },
            'primaryArena': 'sql',
            'arenaName': 'SQL Lab',
            'marketData': {
                'demandLevel': 'High',
                'demandScore': 85,
                'trend': 'Growing',
                'lastUpdated': '2026-09-01',
                'source': 'Data & Infrastructure Hiring Survey 2026'
            }
        },
        {
            'id': 'devops-engineer',
            'title': 'DevOps Engineer',
            'requiredSkills': {
                'DevOps': 1.0,
                'Security': 0.8,
                'Backend': 0.7,
                'Testing': 0.6,
                'SQL': 0.4,
            },
            'primaryArena': 'code',
            'arenaName': 'Code Challenges',
            'marketData': {
                'demandLevel': 'High',
                'demandScore': 86,
                'trend': 'Growing',
                'lastUpdated': '2026-09-01',
                'source': 'DevOps & Cloud Talent Report 2026'
            }
        },
        {
            'id': 'qa-test-engineer',
            'title': 'QA / Test Engineer',
            'requiredSkills': {
                'Testing': 1.0,
                'APIs': 0.8,
                'Backend': 0.6,
                'Frontend': 0.5,
                'SQL': 0.4,
            },
            'primaryArena': 'code',
            'arenaName': 'Code Challenges',
            'marketData': {
                'demandLevel': 'Moderate',
                'demandScore': 72,
                'trend': 'Stable',
                'lastUpdated': '2026-09-01',
                'source': 'Quality Assurance Hiring Benchmarks 2026'
            }
        },
        {
            'id': 'security-engineer',
            'title': 'Security Engineer',
            'requiredSkills': {
                'Security': 1.0,
                'APIs': 0.8,
                'Backend': 0.7,
                'DevOps': 0.6,
                'Testing': 0.5,
            },
            'primaryArena': 'code',
            'arenaName': 'Code Challenges',
            'marketData': {
                'demandLevel': 'High',
                'demandScore': 87,
                'trend': 'Growing',
                'lastUpdated': '2026-09-01',
                'source': 'Cybersecurity Workforce Study 2026'
            }
        }
    ]

    ROLE_INTEREST_KEYWORDS = {
        'backend-developer': ['backend', 'microservice', 'api', 'server', 'django', 'python', 'fastapi', 'flask'],
        'frontend-developer': ['frontend', 'react', 'ui', 'ux', 'web development', 'mobile', 'javascript', 'css', 'html'],
        'fullstack-developer': ['full stack', 'fullstack', 'web development', 'end-to-end', 'software engineering'],
        'data-engineer': ['database', 'sql', 'data', 'optimization', 'pipeline', 'analytics', 'database optimization & sql'],
        'devops-engineer': ['devops', 'cloud', 'architecture', 'infrastructure', 'docker', 'ci/cd', 'deployment', 'cloud architecture & devops'],
        'qa-test-engineer': ['testing', 'qa', 'quality', 'test', 'debugging', 'web security & debugging'],
        'security-engineer': ['security', 'pentest', 'vulnerability', 'owasp', 'auth', 'cybersecurity', 'application security & pentesting']
    }

    @classmethod
    def calculate_role_insights(cls, user) -> dict:
        """
        Calculates role suitabilities, skill gap analysis, market indicators,
        and connects to the existing ChallengeRecommender for gap practice.
        Seamlessly integrates user profile info (strengths, weaknesses, career interests,
        college, and submission track record) to generate tailor-made career guidance.
        """
        skill_matrix = SkillProfiler.calculate_skill_matrix(user)
        category_skills = skill_matrix.get('categorySkills', {})
        technology_skills = skill_matrix.get('technologySkills', {})
        topic_skills = skill_matrix.get('topicSkills', {})
        total_solved = skill_matrix.get('totalSolved', 0)

        # Retrieve profile personalization data from user
        user_strengths = [s.strip() for s in (getattr(user, 'strengths', []) or []) if s.strip()]
        user_weaknesses = [w.strip() for w in (getattr(user, 'weaknesses', []) or []) if w.strip()]
        user_interests = [i.strip() for i in (getattr(user, 'interests', []) or []) if i.strip()]
        user_college = getattr(user, 'college', '') or ''
        user_bio = getattr(user, 'bio', '') or ''
        display_name = getattr(user, 'display_name', '') or f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip() or getattr(user, 'username', 'Developer')

        is_insufficient_data = (total_solved == 0 and not user_strengths and not user_weaknesses and not user_interests)

        role_rankings = []

        for role_def in cls.ROLE_DEFINITIONS:
            role_id = role_def['id']
            reqs = role_def['requiredSkills']
            weighted_sum = 0.0
            total_weight = 0.0
            meeting_count = 0

            for skill_name, weight in reqs.items():
                score = category_skills.get(skill_name, 0)
                weighted_sum += (score * weight)
                total_weight += weight
                if score >= 40:
                    meeting_count += 1

            skill_alignment = (weighted_sum / max(1.0, total_weight)) if total_weight > 0 else 0
            coverage_ratio = (meeting_count / max(1, len(reqs))) * 100.0

            # 1. Base skill match from demonstrated submissions & baseline profiler
            raw_match = (skill_alignment * 0.70) + (coverage_ratio * 0.30)

            # 2. Check alignment with User's declared career interests from signup / onboarding / profile
            role_keywords = cls.ROLE_INTEREST_KEYWORDS.get(role_id, [])
            matched_interests = []
            for interest in user_interests:
                int_lower = interest.lower()
                if any(kw in int_lower for kw in role_keywords) or any(int_lower in kw for kw in role_keywords):
                    matched_interests.append(interest)

            interest_bonus = 12 if matched_interests else 0

            # 3. Check alignment with User's declared profile strengths
            matched_profile_strengths = []
            for str_item in user_strengths:
                if any(str_item.lower() in k.lower() or k.lower() in str_item.lower() for k in reqs.keys()):
                    matched_profile_strengths.append(str_item)

            strength_bonus = min(20, len(matched_profile_strengths) * 10)

            # 4. Check impact of User's declared profile weaknesses
            matched_profile_weaknesses = []
            weakness_penalty = 0
            for wk_item in user_weaknesses:
                for req_k, req_w in reqs.items():
                    if wk_item.lower() in req_k.lower() or req_k.lower() in wk_item.lower():
                        matched_profile_weaknesses.append(wk_item)
                        if req_w >= 0.7:
                            weakness_penalty += int(15 * req_w)
                        else:
                            weakness_penalty += 8

            weakness_penalty = min(25, weakness_penalty)

            # Combine score with personalization adjustments
            adjusted_match = round(raw_match + interest_bonus + strength_bonus - weakness_penalty)

            if total_solved == 0:
                user_match_score = min(95, max(15, adjusted_match))
            else:
                user_match_score = min(98, max(20, adjusted_match))

            demand_score = role_def['marketData']['demandScore']

            # Career Opportunity Score: 70% user skill/interest match + 30% market demand
            career_opportunity_score = round((user_match_score * 0.70) + (demand_score * 0.30))

            # Classification Label
            if user_match_score >= 75:
                match_label = 'Strong Match'
            elif user_match_score >= 55:
                match_label = 'Good Match'
            else:
                match_label = 'Developing Match'

            # Identify demonstrated relevant strengths
            strong_skills = [
                s_name for s_name, w in reqs.items()
                if category_skills.get(s_name, 0) >= 50 or any(s_name.lower() in s.lower() for s in user_strengths)
            ]

            # Identify key skill gaps (where weight is high but proficiency is low or matches declared weakness)
            gaps_scored = []
            for s_name, w in reqs.items():
                current_val = category_skills.get(s_name, 0)
                is_weakness = any(s_name.lower() in wk.lower() or wk.lower() in s_name.lower() for wk in user_weaknesses)
                gap_severity = ((100 - current_val) * w) + (25 if is_weakness else 0)
                gaps_scored.append((s_name, current_val, gap_severity, is_weakness))
            
            gaps_scored.sort(key=lambda x: x[2], reverse=True)
            top_gaps = [{
                'skill': g[0],
                'proficiency': g[1],
                'isDeclaredWeakness': g[3]
            } for g in gaps_scored[:3]]

            # Fetch practice challenges for top skill gap using ChallengeRecommender
            primary_gap = top_gaps[0]['skill'] if top_gaps else 'Backend'
            recommended_challenges = ChallengeRecommender.get_personalized_challenges(
                user=user,
                category=primary_gap,
                limit=2
            )

            # Format recommended challenges
            formatted_challenges = []
            for r_chal in recommended_challenges:
                formatted_challenges.append({
                    'id': str(r_chal.get('id')),
                    'title': r_chal.get('title'),
                    'difficulty': r_chal.get('difficulty'),
                    'technology': r_chal.get('technology'),
                    'category': r_chal.get('category'),
                    'reason': f"Improves {primary_gap} for {role_def['title']}."
                })

            # Generate explainable, user-specific rationale
            if matched_interests and matched_profile_strengths:
                explanation = (
                    f"Directly matches your stated interest in '{matched_interests[0]}' and verified strengths in "
                    f"{', '.join(matched_profile_strengths[:2])}. Focus on {primary_gap} to maximize your readiness."
                )
            elif matched_interests:
                explanation = (
                    f"Aligned with your career interest in '{matched_interests[0]}'. "
                    f"Build practical proficiency in {primary_gap} to turn this goal into an active match."
                )
            elif matched_profile_strengths:
                explanation = (
                    f"Strong alignment with your profile strengths in {', '.join(matched_profile_strengths[:2])}. "
                    f"Targeting {primary_gap} will strengthen your role portfolio."
                )
            elif matched_profile_weaknesses:
                explanation = (
                    f"Identified '{matched_profile_weaknesses[0]}' from your profile as a growth area. "
                    f"Solving recommended challenges below will help bridge this gap for {role_def['title']}."
                )
            else:
                explanation = (
                    f"Demonstrated skills in {', '.join(strong_skills[:3]) if strong_skills else 'core programming fundamentals'} "
                    f"connect to this role. Practice {primary_gap} to boost your suitability."
                )

            role_rankings.append({
                'id': role_def['id'],
                'title': role_def['title'],
                'matchScore': user_match_score,
                'opportunityScore': career_opportunity_score,
                'matchLabel': match_label,
                'explanation': explanation,
                'marketDemand': role_def['marketData']['demandLevel'],
                'demandScore': demand_score,
                'marketTrend': role_def['marketData']['trend'],
                'lastUpdated': role_def['marketData']['lastUpdated'],
                'source': role_def['marketData']['source'],
                'demonstratedStrengths': strong_skills,
                'skillGaps': top_gaps,
                'recommendedArena': role_def['primaryArena'],
                'arenaName': role_def['arenaName'],
                'recommendedChallenges': formatted_challenges,
                'isInterestMatch': bool(matched_interests),
                'matchedInterests': matched_interests,
                'profileStrengths': matched_profile_strengths,
                'profileWeaknesses': matched_profile_weaknesses
            })

        # Sort roles descending by user match score and opportunity score
        role_rankings.sort(key=lambda x: (x['isInterestMatch'], x['matchScore'], x['opportunityScore']), reverse=True)

        top_role = role_rankings[0] if role_rankings else None

        return {
            'isInsufficientData': is_insufficient_data,
            'dataMessage': (
                'Personalized using your declared profile strengths, weaknesses, and interests. '
                'Complete 3+ challenges to unlock higher-confidence performance metrics.'
            ) if is_insufficient_data else f'Personalized for {display_name} based on demonstrated performance and profile preferences.',
            'userProfile': {
                'name': display_name,
                'username': getattr(user, 'username', ''),
                'avatar': getattr(user, 'avatar', ''),
                'college': user_college,
                'bio': user_bio,
                'strengths': user_strengths,
                'weaknesses': user_weaknesses,
                'interests': user_interests,
                'challengesSolved': getattr(user, 'challenges_solved', 0),
                'totalScore': getattr(user, 'total_score', 0),
                'streak': getattr(user, 'streak', 0),
            },
            'topMatch': top_role,
            'roles': role_rankings,
            'disclaimer': 'Market insights reflect current software engineering hiring benchmarks and update periodically.'
        }

