"""
Personalized Learning Path Generator for BuggyMan ML Layer (Phase 4 Task 7)
"""
from buggyman.models import Challenge, Submission
from buggyman.ml.weakness_detector import WeaknessDetector

class LearningPathGenerator:
    @classmethod
    def generate_learning_path(cls, user) -> dict:
        """
        Builds a 5-stage personalized progression path using existing challenges:
        Weak Concept -> Easy Targeted -> Medium Challenge -> Mixed Challenge -> Hard Benchmark -> Reassessment
        """
        all_challenges = list(Challenge.objects.all())
        if not all_challenges:
            return {
                'userId': None,
                'targetConcept': 'General Debugging',
                'stages': [],
                'completionPercentage': 0,
                'currentStageIndex': 0
            }

        if not user or not user.is_authenticated:
            easy_chal = [c for c in all_challenges if (c.difficulty or '').lower() == 'easy'][:2]
            med_chal = [c for c in all_challenges if (c.difficulty or '').lower() == 'medium'][:2]
            hard_chal = [c for c in all_challenges if (c.difficulty or '').lower() == 'hard'][:1]
            
            stages = []
            if easy_chal:
                stages.append({'stageNumber': 1, 'title': 'Foundation Practice', 'difficulty': 'Easy', 'challenge': easy_chal[0].to_dict(), 'completed': False})
            if len(easy_chal) > 1:
                stages.append({'stageNumber': 2, 'title': 'Concept Reinforcement', 'difficulty': 'Easy', 'challenge': easy_chal[1].to_dict(), 'completed': False})
            if med_chal:
                stages.append({'stageNumber': 3, 'title': 'Intermediate Challenge', 'difficulty': 'Medium', 'challenge': med_chal[0].to_dict(), 'completed': False})
            if len(med_chal) > 1:
                stages.append({'stageNumber': 4, 'title': 'Mixed Challenge', 'difficulty': 'Medium', 'challenge': med_chal[1].to_dict(), 'completed': False})
            if hard_chal:
                stages.append({'stageNumber': 5, 'title': 'Mastery Benchmark', 'difficulty': 'Hard', 'challenge': hard_chal[0].to_dict(), 'completed': False})

            return {
                'userId': None,
                'targetConcept': 'Full Stack Debugging Fundamentals',
                'targetCategory': 'General',
                'stages': stages,
                'completedStages': 0,
                'totalStages': len(stages),
                'completionPercentage': 0,
                'currentStageIndex': 0
            }

        weakness_data = WeaknessDetector.detect_weaknesses(user)
        top_weaknesses = weakness_data.get('topWeaknesses', [])
        
        target_weakness = top_weaknesses[0] if top_weaknesses else None
        target_concept = target_weakness.get('name', 'General Software Quality') if target_weakness else 'React & Database Logic'
        target_category = target_weakness.get('category', 'State Management') if target_weakness else 'State Management'

        solved_ids = {str(s.challenge_id) for s in Submission.objects.filter(user=user, success=True)}

        category_chals = [c for c in all_challenges if (c.category or '').lower() == target_category.lower()]
        if not category_chals:
            category_chals = all_challenges

        easy_pool = [c for c in category_chals if (c.difficulty or '').lower() == 'easy'] or [c for c in all_challenges if (c.difficulty or '').lower() == 'easy']
        med_pool = [c for c in category_chals if (c.difficulty or '').lower() == 'medium'] or [c for c in all_challenges if (c.difficulty or '').lower() == 'medium']
        hard_pool = [c for c in category_chals if (c.difficulty or '').lower() == 'hard'] or [c for c in all_challenges if (c.difficulty or '').lower() == 'hard']

        def pick_challenge(pool, exclude_ids=None):
            exclude_ids = exclude_ids or set()
            available = [c for c in pool if str(c.id) not in exclude_ids]
            if not available:
                available = [c for c in all_challenges if str(c.id) not in exclude_ids] or all_challenges
            unsolved = [c for c in available if str(c.id) not in solved_ids]
            return unsolved[0] if unsolved else available[0]

        used_ids = set()
        stage1_c = pick_challenge(easy_pool, used_ids)
        used_ids.add(str(stage1_c.id))

        stage2_c = pick_challenge(med_pool if med_pool else easy_pool, used_ids)
        used_ids.add(str(stage2_c.id))

        stage3_c = pick_challenge(all_challenges, used_ids)
        used_ids.add(str(stage3_c.id))

        stage4_c = pick_challenge(hard_pool if hard_pool else med_pool, used_ids)
        used_ids.add(str(stage4_c.id))

        stage5_c = pick_challenge(all_challenges, used_ids)

        raw_stages = [
            {'stageNumber': 1, 'title': 'Diagnostic Foundation', 'difficulty': stage1_c.difficulty, 'challenge': stage1_c},
            {'stageNumber': 2, 'title': 'Intermediate Concept Practice', 'difficulty': stage2_c.difficulty, 'challenge': stage2_c},
            {'stageNumber': 3, 'title': 'Mixed Architecture Challenge', 'difficulty': stage3_c.difficulty, 'challenge': stage3_c},
            {'stageNumber': 4, 'title': 'Mastery Benchmark', 'difficulty': stage4_c.difficulty, 'challenge': stage4_c},
            {'stageNumber': 5, 'title': 'Reassessment Milestone', 'difficulty': stage5_c.difficulty, 'challenge': stage5_c}
        ]

        completed_count = 0
        current_index = 0
        formatted_stages = []

        for idx, st in enumerate(raw_stages):
            c_obj = st['challenge']
            is_done = str(c_obj.id) in solved_ids
            if is_done:
                completed_count += 1
            elif completed_count == idx:
                current_index = idx

            formatted_stages.append({
                'stageNumber': st['stageNumber'],
                'title': st['title'],
                'difficulty': st['difficulty'],
                'challenge': c_obj.to_dict(),
                'completed': is_done
            })

        total = len(formatted_stages)
        completion_pct = round((completed_count / max(1, total)) * 100)

        return {
            'userId': user.id,
            'username': user.username,
            'targetConcept': target_concept,
            'targetCategory': target_category,
            'stages': formatted_stages,
            'completedStages': completed_count,
            'totalStages': total,
            'completionPercentage': completion_pct,
            'currentStageIndex': min(current_index, total - 1)
        }
