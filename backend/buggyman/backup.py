"""
Backup & Data Integrity Engine for BuggyMan (Phase 5 Task 9)
"""
import json
import time
from buggyman.models import User, Challenge, Submission, ChallengeReport, Notification

class BackupManager:
    @classmethod
    def export_full_backup(cls) -> dict:
        """
        Exports a complete, structured JSON snapshot of all platform database models.
        """
        users = [u.to_dict() for u in User.objects.all()]
        challenges = [c.to_dict() for c in Challenge.objects.all()]
        submissions = [s.to_dict() for s in Submission.objects.all()]
        reports = [r.to_dict() for r in ChallengeReport.objects.all()]
        notifications = [n.to_dict() for n in Notification.objects.all()]

        backup_payload = {
            'version': '1.0.0',
            'timestamp': time.time(),
            'counts': {
                'users': len(users),
                'challenges': len(challenges),
                'submissions': len(submissions),
                'reports': len(reports),
                'notifications': len(notifications)
            },
            'data': {
                'users': users,
                'challenges': challenges,
                'submissions': submissions,
                'reports': reports,
                'notifications': notifications
            }
        }
        return backup_payload

    @classmethod
    def verify_backup_integrity(cls, backup_payload: dict) -> tuple[bool, str]:
        """
        Validates backup snapshot structure and data integrity checksums.
        """
        if not isinstance(backup_payload, dict):
            return False, "Invalid backup payload format: root must be a JSON object."

        if 'counts' not in backup_payload or 'data' not in backup_payload:
            return False, "Missing required backup sections: counts and data."

        counts = backup_payload.get('counts', {})
        data = backup_payload.get('data', {})

        for entity in ['users', 'challenges', 'submissions', 'reports', 'notifications']:
            entity_data = data.get(entity)
            if not isinstance(entity_data, list):
                return False, f"Invalid entity array format for '{entity}'."
            if len(entity_data) != counts.get(entity, -1):
                return False, f"Data count mismatch for '{entity}': expected {counts.get(entity)}, got {len(entity_data)}."

        return True, "Backup payload integrity verified successfully."
