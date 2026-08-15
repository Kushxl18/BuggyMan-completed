"""
Adaptive Difficulty Engine for BuggyMan ML Layer (Phase 4 Task 5)
"""
from buggyman.models import Submission

class AdaptiveDifficultyManager:
    @classmethod
    def get_user_adaptive_state(cls, user) -> dict:
        """
        Evaluates user's recent submission trajectory and computes recommended target difficulty level
        (Easy, Medium, Hard) and adjustment trend without modifying database challenge attributes.
        """
        if not user or not user.is_authenticated:
            return {
                'recommendedTier': 'Easy',
                'trend': 'steady',
                'consecutiveSuccesses': 0,
                'consecutiveFailures': 0,
                'recentAccuracy': 0.0,
                'explanation': 'New user baseline starting at Easy difficulty.'
            }

        recent_subs = list(Submission.objects.filter(user=user).order_by('-created_at')[:5])
        if not recent_subs:
            return {
                'recommendedTier': 'Easy',
                'trend': 'steady',
                'consecutiveSuccesses': 0,
                'consecutiveFailures': 0,
                'recentAccuracy': 0.0,
                'explanation': 'No recent submission history. Recommending Easy tier.'
            }

        consec_success = 0
        for s in recent_subs:
            if s.success:
                consec_success += 1
            else:
                break

        consec_failure = 0
        for s in recent_subs:
            if not s.success:
                consec_failure += 1
            else:
                break

        recent_success_count = sum(1 for s in recent_subs if s.success)
        recent_acc = round((recent_success_count / len(recent_subs)) * 100, 1)

        if consec_failure >= 2 or recent_acc < 40.0:
            recommended_tier = 'Easy'
            trend = 'regressing'
            explanation = f"Detected {consec_failure} consecutive failures. Recommending targeted Easy foundation challenges to rebuild mastery."
        elif consec_success >= 3 or (len(recent_subs) >= 4 and recent_acc >= 75.0):
            recommended_tier = 'Hard'
            trend = 'escalating'
            explanation = f"Strong performance! {consec_success} consecutive solves. Elevating target difficulty to Hard tier."
        elif consec_success >= 2 or recent_acc >= 60.0:
            recommended_tier = 'Medium'
            trend = 'escalating' if consec_success >= 2 else 'steady'
            explanation = f"Solid accuracy ({recent_acc}%). Recommending Medium tier challenges."
        else:
            recommended_tier = 'Medium' if recent_acc >= 50.0 else 'Easy'
            trend = 'steady'
            explanation = f"Balanced solve rate ({recent_acc}%). Maintaining {recommended_tier} tier."

        return {
            'recommendedTier': recommended_tier,
            'trend': trend,
            'consecutiveSuccesses': consec_success,
            'consecutiveFailures': consec_failure,
            'recentAccuracy': recent_acc,
            'recentSubmissionsCount': len(recent_subs),
            'explanation': explanation
        }
