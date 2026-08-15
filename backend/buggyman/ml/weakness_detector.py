"""
Weakness Detector Engine for BuggyMan ML Layer (Phase 4 Task 6)
"""
from buggyman.models import Submission
from buggyman.ml.analytics_collector import AnalyticsCollector

class WeaknessDetector:
    @classmethod
    def detect_weaknesses(cls, user) -> dict:
        """
        Analyzes user's submission history, error logs, and category failure rates
        to identify recurring weakness areas.
        """
        if not user or not user.is_authenticated:
            return {
                'userId': None,
                'username': 'Guest',
                'weaknessCount': 0,
                'topWeaknesses': [],
                'summary': 'No weakness data available for unauthenticated user.'
            }

        analytics = AnalyticsCollector.get_user_analytics_data(user)
        cat_perf = analytics.get('categoryPerformance', {})
        error_summary = analytics.get('errorTypesSummary', {})

        detected = []

        # 1. Analyze Category Failure Rates
        for cat, perf in cat_perf.items():
            subs = perf.get('submissionsCount', 0)
            succ = perf.get('successCount', 0)
            acc = perf.get('accuracyRate', 100.0)

            if subs >= 2 and acc < 60.0:
                severity = 'high' if acc < 40.0 else 'medium'
                detected.append({
                    'name': f"{cat} Logic & Implementation",
                    'type': 'category_weakness',
                    'category': cat,
                    'severity': severity,
                    'accuracyRate': acc,
                    'failedAttempts': subs - succ,
                    'description': f"Lower accuracy rate ({acc}%) across {subs} attempts in {cat} challenges."
                })

        # 2. Analyze Error Classifications
        for err_type, count in error_summary.items():
            if count >= 2:
                if err_type == 'state_mutation_error':
                    detected.append({
                        'name': 'React Immutability & State Setter Usage',
                        'type': 'error_pattern',
                        'severity': 'high' if count >= 4 else 'medium',
                        'errorType': err_type,
                        'occurrenceCount': count,
                        'description': f"Encountered direct state object mutations or un-upgraded state setters in {count} submissions."
                    })
                elif err_type == 'database_error':
                    detected.append({
                        'name': 'SQL Query Predicates & Filter Clause Syntax',
                        'type': 'error_pattern',
                        'severity': 'high' if count >= 3 else 'medium',
                        'errorType': err_type,
                        'occurrenceCount': count,
                        'description': f"Encountered SQL table query execution errors or missing predicate clauses in {count} submissions."
                    })
                elif err_type == 'syntax_error':
                    detected.append({
                        'name': 'Syntax & Statement Parsing Integrity',
                        'type': 'error_pattern',
                        'severity': 'medium',
                        'errorType': err_type,
                        'occurrenceCount': count,
                        'description': f"Encountered syntax parsing or unclosed brace errors in {count} submissions."
                    })

        # Deduplicate and sort by severity
        seen_names = set()
        unique_weaknesses = []
        for w in detected:
            if w['name'] not in seen_names:
                seen_names.add(w['name'])
                unique_weaknesses.append(w)

        sev_rank = {'high': 1, 'medium': 2, 'low': 3}
        unique_weaknesses.sort(key=lambda x: sev_rank.get(x['severity'], 3))

        top_3 = unique_weaknesses[:3]

        if not top_3:
            summary = "No significant recurring weakness patterns detected. Excellent problem-solving accuracy!"
        else:
            names = [w['name'] for w in top_3]
            summary = f"Identified {len(top_3)} primary focus areas: {', '.join(names)}."

        return {
            'userId': user.id,
            'username': user.username,
            'weaknessCount': len(top_3),
            'topWeaknesses': top_3,
            'summary': summary
        }
