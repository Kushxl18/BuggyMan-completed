import os
import sys

# Ensure backend directory is in path to import buggyman evaluator
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

try:
    from buggyman.evaluator.engine import EvaluationEngine
    _engine = EvaluationEngine()
except Exception:
    _engine = None

class SolutionEvaluator:
    @staticmethod
    def evaluate(challenge_dict, submitted_code=None, files=None):
        if _engine:
            return _engine.evaluate(challenge_dict, files=files, code=submitted_code)
        
        # Fallback if engine unavailable
        bug_sig = challenge_dict.get('bugSignature', '').strip() if isinstance(challenge_dict, dict) else ''
        is_fixed = (bug_sig not in (submitted_code or '')) if bug_sig else True
        return {
            'success': is_fixed,
            'summary': "Evaluation complete." if is_fixed else "Bug signature detected."
        }

