class AIClient:
    """
    AI Service client for generating code explanations, hints, and bug evaluation summaries.
    """
    @staticmethod
    def generate_hint(challenge_title, user_code, bug_signature):
        return [
            f"Review the logic around: {bug_signature if bug_signature else 'state mutations'}.",
            "Ensure object/array state immutability in React or validate input before saving in Django."
        ]

    @staticmethod
    def evaluate_solution(challenge, user_code):
        bug_signature = challenge.get('bugSignature', '').strip()
        is_fixed = (bug_signature not in user_code) if bug_signature else True
        if is_fixed:
            return {
                'success': True,
                'summary': f"Great job! You successfully resolved the bug in '{challenge.get('title')}'."
            }
        return {
            'success': False,
            'summary': f"Bug signature still detected in '{challenge.get('title')}'. Please check your state or serializer logic."
        }
