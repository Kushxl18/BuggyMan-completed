"""
Analytics Collector for BuggyMan Adaptive Learning & ML Layer (Phase 4 Task 1)
"""
import re
from buggyman.models import Submission, Challenge

class AnalyticsCollector:
    @staticmethod
    def classify_errors(stderr: str = '', stdout: str = '', test_results: list = None) -> list:
        """
        Classifies execution logs and test outputs into standardized error categories.
        """
        errors = set()
        stderr_text = (stderr or '').lower()
        stdout_text = (stdout or '').lower()
        combined_text = f"{stderr_text}\n{stdout_text}"

        if any(kw in combined_text for kw in ['syntaxerror', 'indentationerror', 'unexpected token', 'parsing error']):
            errors.add('syntax_error')
        if any(kw in combined_text for kw in ['typeerror', 'valueerror', 'referenceerror', 'nameerror', 'attributeerror', 'keyerror', 'indexerror']):
            errors.add('runtime_error')
        if any(kw in combined_text for kw in ['operationalerror', 'sqlite3', 'no such table', 'no such column', 'sql syntax']):
            errors.add('database_error')
        if any(kw in combined_text for kw in ['state mutation', 'direct assignment', 'uncontrolled component', 're-render']):
            errors.add('state_mutation_error')
        if any(kw in combined_text for kw in ['timed out', 'timeout']):
            errors.add('timeout_error')

        if test_results:
            failed_tests = [t for t in test_results if not t.get('passed')]
            if failed_tests:
                errors.add('assertion_failure')

        if not errors and test_results:
            failed = [t for t in test_results if not t.get('passed')]
            if failed:
                errors.add('logic_error')

        return list(errors)

    @classmethod
    def record_submission(cls, submission: Submission, hints_used: int = 0) -> Submission:
        """
        Enriches submission instance with calculated learning performance data.
        """
        test_results = submission.test_results or []
        failed_count = len([t for t in test_results if not t.get('passed')])
        error_types = cls.classify_errors(submission.stderr, submission.stdout, test_results)

        submission.hints_used = max(0, int(hints_used or 0))
        submission.tests_failed = failed_count
        submission.error_types = error_types
        submission.save()

        return submission

    @classmethod
    def get_user_analytics_data(cls, user) -> dict:
        """
        Collects comprehensive, unadulterated learning performance data for a user.
        """
        submissions = Submission.objects.filter(user=user).select_related('challenge').order_by('created_at')
        total_submissions = submissions.count()

        if total_submissions == 0:
            return {
                'userId': user.id,
                'username': user.username,
                'totalSubmissions': 0,
                'solvedCount': 0,
                'successRate': 0.0,
                'avgExecutionTime': 0.0,
                'hintsUsedTotal': 0,
                'errorTypesSummary': {},
                'technologyPerformance': {},
                'categoryPerformance': {},
                'difficultyPerformance': {'Easy': {'solved': 0, 'attempts': 0}, 'Medium': {'solved': 0, 'attempts': 0}, 'Hard': {'solved': 0, 'attempts': 0}},
                'completionHistory': []
            }

        solved_submissions = submissions.filter(success=True)
        solved_count = len({s.challenge_id for s in solved_submissions})
        success_rate = round((solved_submissions.count() / total_submissions) * 100, 1)
        avg_exec_time = round(sum(s.execution_time for s in submissions) / total_submissions, 2)
        hints_used_total = sum(s.hints_used for s in submissions)

        error_types_summary = {}
        tech_perf = {}
        cat_perf = {}
        diff_perf = {'Easy': {'solved': 0, 'attempts': 0}, 'Medium': {'solved': 0, 'attempts': 0}, 'Hard': {'solved': 0, 'attempts': 0}}
        history = []

        for sub in submissions:
            # Aggregate error types
            for err in (sub.error_types or []):
                error_types_summary[err] = error_types_summary.get(err, 0) + 1

            chal = sub.challenge
            if not chal:
                continue

            tech = chal.technology or 'General'
            cat = chal.category or 'General'
            diff = chal.difficulty or 'Easy'

            # Tech performance
            if tech not in tech_perf:
                tech_perf[tech] = {'attempts': 0, 'solved': False, 'submissionsCount': 0, 'successCount': 0, 'failedTests': 0, 'totalExecTime': 0.0}
            tech_perf[tech]['submissionsCount'] += 1
            if sub.success:
                tech_perf[tech]['successCount'] += 1
                tech_perf[tech]['solved'] = True
            tech_perf[tech]['failedTests'] += sub.tests_failed
            tech_perf[tech]['totalExecTime'] += sub.execution_time

            # Category performance
            if cat not in cat_perf:
                cat_perf[cat] = {'attempts': 0, 'solved': False, 'submissionsCount': 0, 'successCount': 0, 'failedTests': 0}
            cat_perf[cat]['submissionsCount'] += 1
            if sub.success:
                cat_perf[cat]['successCount'] += 1
                cat_perf[cat]['solved'] = True
            cat_perf[cat]['failedTests'] += sub.tests_failed

            # Difficulty performance
            if diff in diff_perf:
                diff_perf[diff]['attempts'] += 1
                if sub.success:
                    diff_perf[diff]['solved'] += 1

            # History entry
            history.append({
                'submissionId': sub.id,
                'challengeId': str(chal.id),
                'challengeTitle': chal.title,
                'technology': tech,
                'category': cat,
                'difficulty': diff,
                'success': sub.success,
                'attemptNumber': sub.attempt_number,
                'executionTime': sub.execution_time,
                'testsFailed': sub.tests_failed,
                'hintsUsed': sub.hints_used,
                'errorTypes': sub.error_types,
                'timestamp': sub.created_at.isoformat() if sub.created_at else None
            })

        # Calculate percentages for tech & category
        for tech, p in tech_perf.items():
            p['accuracyRate'] = round((p['successCount'] / p['submissionsCount']) * 100, 1)
            p['avgExecutionTime'] = round(p['totalExecTime'] / p['submissionsCount'], 2)

        for cat, p in cat_perf.items():
            p['accuracyRate'] = round((p['successCount'] / p['submissionsCount']) * 100, 1)

        return {
            'userId': user.id,
            'username': user.username,
            'totalSubmissions': total_submissions,
            'solvedCount': solved_count,
            'successRate': success_rate,
            'avgExecutionTime': avg_exec_time,
            'hintsUsedTotal': hints_used_total,
            'errorTypesSummary': error_types_summary,
            'technologyPerformance': tech_perf,
            'categoryPerformance': cat_perf,
            'difficultyPerformance': diff_perf,
            'completionHistory': history
        }
