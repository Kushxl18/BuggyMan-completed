from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    college = models.CharField(max_length=255, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    avatar = models.URLField(max_length=500, blank=True, default='https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150')
    total_score = models.IntegerField(default=0)
    challenges_solved = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    skills = models.JSONField(default=dict, blank=True)
    activities = models.JSONField(default=list, blank=True)
    badges = models.JSONField(default=list, blank=True)

    # Added fields
    display_name = models.CharField(max_length=255, blank=True, default='')
    theme = models.CharField(max_length=50, default='dark')
    accent_color = models.CharField(max_length=50, default='blue')
    country = models.CharField(max_length=100, blank=True, default='')
    timezone = models.CharField(max_length=100, blank=True, default='')
    interests = models.JSONField(default=list, blank=True)
    notifications_config = models.JSONField(default=dict, blank=True)
    otp_code = models.CharField(max_length=10, blank=True, default='')
    otp_expiry = models.DateTimeField(null=True, blank=True)
    last_active_date = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=20, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_dict(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        display_name = self.display_name if self.display_name else (full_name if full_name else (self.username or "Anonymous User"))
        is_admin = bool(self.is_staff or self.is_superuser or self.role == 'admin')
        return {
            'id': self.id,
            'name': display_name,
            'display_name': display_name,
            'username': self.username,
            'email': self.email,
            'role': 'admin' if is_admin else 'user',
            'isAdmin': is_admin,
            'college': self.college or 'State Technical University',
            'bio': self.bio or 'Aspiring Full Stack Engineer. Lover of logic puzzles and debugging challenge marathons.',
            'avatar': self.avatar or 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150',
            'totalScore': self.total_score,
            'challengesSolved': self.challenges_solved,
            'streak': self.streak,
            'skills': self.skills if self.skills else {'React': 80, 'Django': 60, 'NodeJS': 45, 'CSS': 70},
            'activities': self.activities if self.activities is not None else [],
            'badges': self.badges if self.badges is not None else [],
            'theme': self.theme,
            'accent_color': self.accent_color,
            'country': self.country,
            'timezone': self.timezone,
            'interests': self.interests,
            'notifications_config': self.notifications_config,
            'lastActiveDate': self.last_active_date.isoformat() if self.last_active_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class Challenge(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=50, default='Easy')
    technology = models.CharField(max_length=100, default='React')
    category = models.CharField(max_length=100, default='State Management')
    time_estimate = models.CharField(max_length=50, default='10 mins')
    points = models.IntegerField(default=100)
    files = models.JSONField(default=list)
    test_cases = models.JSONField(default=list)
    bug_signature = models.TextField(blank=True, default='')
    suspected_component = models.CharField(max_length=255, blank=True, default='')
    ai_suggestions = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, default='published')
    created_at = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'difficulty': self.difficulty,
            'technology': self.technology,
            'category': self.category,
            'timeEstimate': self.time_estimate,
            'time_estimate': self.time_estimate,
            'points': self.points,
            'files': self.files or [],
            'testCases': self.test_cases or [],
            'test_cases': self.test_cases or [],
            'bugSignature': self.bug_signature,
            'bug_signature': self.bug_signature,
            'suspectedComponent': self.suspected_component,
            'suspected_component': self.suspected_component,
            'aiSuggestions': self.ai_suggestions or [],
            'ai_suggestions': self.ai_suggestions or []
        }

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=50, default='system')
    read = models.BooleanField(default=False)
    time = models.CharField(max_length=100, default='Just now')
    created_at = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'read': self.read,
            'time': self.time
        }

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    submitted_code = models.TextField()
    submitted_files = models.JSONField(default=list, blank=True)
    success = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    test_results = models.JSONField(default=list, blank=True)
    execution_time = models.FloatField(default=0.0)
    attempt_number = models.IntegerField(default=1)
    stdout = models.TextField(blank=True, default='')
    stderr = models.TextField(blank=True, default='')
    ai_summary = models.TextField(blank=True, default='')
    hints_used = models.IntegerField(default=0)
    error_types = models.JSONField(default=list, blank=True)
    tests_failed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'user': self.user.username if self.user else '',
            'challengeId': str(self.challenge_id),
            'challengeTitle': self.challenge.title if self.challenge else '',
            'submittedCode': self.submitted_code,
            'submittedFiles': self.submitted_files or [],
            'success': self.success,
            'score': self.score,
            'testResults': self.test_results or [],
            'executionTime': self.execution_time,
            'attemptNumber': self.attempt_number,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'aiSummary': self.ai_summary,
            'hintsUsed': self.hints_used,
            'errorTypes': self.error_types or [],
            'testsFailed': self.tests_failed,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

class ChallengeReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='reports')
    submission = models.ForeignKey(Submission, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    report_type = models.CharField(max_length=50, default='broken_challenge')
    description = models.TextField()
    status = models.CharField(max_length=20, default='open')
    admin_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'user': self.user.username if self.user else 'Anonymous',
            'challengeId': str(self.challenge_id),
            'challengeTitle': self.challenge.title if self.challenge else '',
            'submissionId': self.submission_id,
            'reportType': self.report_type,
            'description': self.description,
            'status': self.status,
            'adminNotes': self.admin_notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

