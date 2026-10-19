from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    college = models.CharField(max_length=255, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    avatar = models.TextField(blank=True, default='https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150')
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
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    notifications_config = models.JSONField(default=dict, blank=True)
    phone = models.CharField(max_length=30, blank=True, default='')
    otp_code = models.CharField(max_length=10, blank=True, default='')
    otp_expiry = models.DateTimeField(null=True, blank=True)
    last_active_date = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=20, default='user')
    bugbytes_balance = models.IntegerField(default=50)
    auth_provider = models.CharField(max_length=50, blank=True, default='local')
    oauth_id = models.CharField(max_length=255, blank=True, default='')
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_onboarded(self):
        if self.onboarding_completed:
            return True
        if self.total_score > 0 or self.challenges_solved > 0:
            return True
        if self.strengths and len(self.strengths) > 0 and self.weaknesses and len(self.weaknesses) > 0:
            return True
        return False

    @property
    def current_streak(self):
        if not self.last_active_date:
            return 0
        import datetime
        today = timezone.localdate() if hasattr(timezone, 'localdate') else datetime.date.today()
        # Streak remains active if user was active today or yesterday
        if self.last_active_date >= today - datetime.timedelta(days=1):
            return self.streak
        return 0

    def to_dict(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        display_name = self.display_name if self.display_name else (full_name if full_name else (self.username or "Anonymous User"))
        is_admin = bool(self.is_staff or self.is_superuser or self.role == 'admin')
        is_onboarded = bool(self.onboarding_completed or self.is_onboarded)
        active_streak = self.current_streak

        # Build dynamic skills matrix respecting user's declared strengths & weaknesses
        user_skills = self.skills
        if not user_skills:
            str_set = {s.strip().lower() for s in (self.strengths or []) if s.strip()}
            wk_set = {w.strip().lower() for w in (self.weaknesses or []) if w.strip()}
            base_skills = {}
            for cat in ['Backend', 'SQL', 'Frontend', 'APIs', 'Security', 'Testing', 'DevOps']:
                if any(s in cat.lower() or cat.lower() in s for s in str_set):
                    base_skills[cat] = 75
                elif any(w in cat.lower() or cat.lower() in w for w in wk_set):
                    base_skills[cat] = 35
                else:
                    base_skills[cat] = 50
            user_skills = base_skills

        return {
            'id': self.id,
            'name': display_name,
            'display_name': display_name,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'role': 'admin' if is_admin else 'user',
            'isAdmin': is_admin,
            'college': self.college or '',
            'bio': self.bio or '',
            'avatar': self.avatar or 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150',
            'totalScore': self.total_score,
            'challengesSolved': self.challenges_solved,
            'streak': active_streak,
            'streakDays': active_streak,
            'streak_days': active_streak,
            'bestStreak': self.streak,
            'bugbytesBalance': self.bugbytes_balance,
            'bugbytes_balance': self.bugbytes_balance,
            'authProvider': self.auth_provider,
            'auth_provider': self.auth_provider,
            'oauthId': self.oauth_id,
            'oauth_id': self.oauth_id,
            'skills': user_skills,
            'activities': self.activities if self.activities is not None else [],
            'badges': self.badges if self.badges is not None else [],
            'theme': self.theme,
            'accent_color': self.accent_color,
            'country': self.country,
            'timezone': self.timezone,
            'interests': self.interests or [],
            'strengths': self.strengths or [],
            'weaknesses': self.weaknesses or [],
            'notifications_config': self.notifications_config,
            'onboardingCompleted': is_onboarded,
            'onboarding_completed': is_onboarded,
            'isNewUser': not is_onboarded,
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
    topics = models.JSONField(default=list, blank=True)
    skills_tested = models.JSONField(default=list, blank=True)
    prerequisites = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, default='published')
    created_at = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        tech_lower = (self.technology or '').lower()
        if 'sql' in tech_lower or 'database' in tech_lower:
            page = 'SQL Lab'
        elif 'css' in tech_lower or 'html' in tech_lower or 'frontend' in tech_lower:
            page = 'Frontend Studio'
        else:
            page = 'Code Challenges'

        computed_topics = self.topics if self.topics else ([self.category] if self.category else [])
        computed_skills = self.skills_tested if self.skills_tested else ([self.technology, self.category] if self.technology else [])

        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'difficulty': self.difficulty,
            'technology': self.technology,
            'category': self.category,
            'page': page,
            'arenaType': page,
            'topics': computed_topics,
            'skillsTested': computed_skills,
            'skills_tested': computed_skills,
            'prerequisites': self.prerequisites or [],
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


class BugBytesTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('EARN_CHALLENGE', 'Earned from Challenge Completion'),
        ('EARN_BONUS', 'Earned from Bonus'),
        ('SPEND_HINT', 'Spent on AI Hint'),
        ('STORE_PURCHASE', 'Purchased from BugBytes Store (Demo)'),
        ('STORE_REFUND', 'Refunded BugBytes Purchase (Demo)'),
        ('ADMIN_ADJUSTMENT', 'Admin Adjustment'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bugbytes_transactions')
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    reason = models.TextField(blank=True, default='')
    challenge = models.ForeignKey(Challenge, on_delete=models.SET_NULL, null=True, blank=True, related_name='bugbytes_transactions')
    hint_level = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'amount': self.amount,
            'transactionType': self.transaction_type,
            'transaction_type': self.transaction_type,
            'reason': self.reason,
            'challengeId': str(self.challenge_id) if self.challenge_id else None,
            'challengeTitle': self.challenge.title if self.challenge else None,
            'hintLevel': self.hint_level,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class UnlockedHint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unlocked_hints')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='unlocked_hints')
    hint_level = models.IntegerField()
    hint_content = models.TextField()
    cost = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'challenge', 'hint_level')

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'challengeId': str(self.challenge_id),
            'hintLevel': self.hint_level,
            'hint_level': self.hint_level,
            'hintContent': self.hint_content,
            'hint_content': self.hint_content,
            'cost': self.cost,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class BugBytesPackage(models.Model):
    name = models.CharField(max_length=100)
    bugbytes = models.IntegerField()
    price_inr = models.DecimalField(max_digits=10, decimal_places=2)
    is_best_value = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order_priority = models.IntegerField(default=0)

    # Configurable Money-Back Reward Mission Parameters
    mission_title = models.CharField(max_length=255, default='Earn Your Money Back Mission')
    mission_days = models.IntegerField(default=7)
    mission_challenge_count = models.IntegerField(default=5)
    mission_difficulty = models.CharField(max_length=50, default='Medium') # 'Medium', 'Hard', 'Medium or Hard'
    reward_amount_inr = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)

    class Meta:
        ordering = ['order_priority', 'price_inr']

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'bugbytes': self.bugbytes,
            'priceInr': float(self.price_inr),
            'price_inr': float(self.price_inr),
            'isBestValue': self.is_best_value,
            'is_best_value': self.is_best_value,
            'isActive': self.is_active,
            'orderPriority': self.order_priority,
            'missionTitle': self.mission_title,
            'missionDays': self.mission_days,
            'missionChallengeCount': self.mission_challenge_count,
            'missionDifficulty': self.mission_difficulty,
            'rewardAmountInr': float(self.reward_amount_inr),
            'reward_amount_inr': float(self.reward_amount_inr),
        }


class BugBytesPurchase(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Demo Payment'),
        ('COMPLETED', 'Simulated Payment Success'),
        ('FAILED', 'Simulated Payment Failure'),
        ('REFUNDED', 'Simulated Refund Success'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_purchases')
    package = models.ForeignKey(BugBytesPackage, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases')
    package_name = models.CharField(max_length=100)
    bugbytes_amount = models.IntegerField()
    price_inr = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    transaction_reference = models.CharField(max_length=100, unique=True)
    idempotency_key = models.CharField(max_length=120, null=True, blank=True)
    payment_method = models.CharField(max_length=50, default='DEMO_SIMULATOR')
    failure_reason = models.TextField(blank=True, default='')
    refund_amount_inr = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    refund_reason = models.TextField(blank=True, default='')
    refunded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def to_dict(self):
        mission_dict = None
        can_refund = False
        if hasattr(self, 'reward_mission'):
            try:
                m = self.reward_mission
                m.check_and_update_status()
                mission_dict = m.to_dict()
                can_refund = (m.status == 'COMPLETED') and not self.refunded_at
            except Exception:
                pass

        return {
            'id': self.id,
            'userId': self.user_id,
            'packageId': self.package_id,
            'packageName': self.package_name,
            'package_name': self.package_name,
            'bugbytesAmount': self.bugbytes_amount,
            'bugbytes_amount': self.bugbytes_amount,
            'priceInr': float(self.price_inr),
            'price_inr': float(self.price_inr),
            'status': self.status,
            'transactionReference': self.transaction_reference,
            'transaction_reference': self.transaction_reference,
            'idempotencyKey': self.idempotency_key,
            'paymentMethod': self.payment_method,
            'failureReason': self.failure_reason,
            'refundAmountInr': float(self.refund_amount_inr) if self.refund_amount_inr else 0.0,
            'refund_amount_inr': float(self.refund_amount_inr) if self.refund_amount_inr else 0.0,
            'refundReason': self.refund_reason,
            'refundedAt': self.refunded_at.isoformat() if self.refunded_at else None,
            'canRefund': can_refund,
            'rewardMission': mission_dict,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None,
            'hasMission': hasattr(self, 'reward_mission'),
        }


class RewardMission(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active Mission'),
        ('COMPLETED', 'Requirements Satisfied'),
        ('CLAIMED', 'Reward Claimed'),
        ('EXPIRED', 'Mission Expired'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reward_missions')
    purchase = models.OneToOneField(BugBytesPurchase, on_delete=models.CASCADE, related_name='reward_mission')
    title = models.CharField(max_length=255)
    required_difficulty = models.CharField(max_length=50) # 'Medium', 'Hard', 'Medium or Hard'
    required_count = models.IntegerField()
    completed_count = models.IntegerField(default=0)
    duration_days = models.IntegerField()
    start_date = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    reward_amount_inr = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    completed_at = models.DateTimeField(null=True, blank=True)
    claimed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-start_date']

    def check_and_update_status(self):
        """Auto-expires mission if deadline passed and still in ACTIVE state."""
        if self.status == 'ACTIVE' and timezone.now() > self.deadline:
            self.status = 'EXPIRED'
            self.save(update_fields=['status'])
        return self.status

    def is_challenge_eligible(self, challenge):
        """Validates challenge difficulty according to mission rules."""
        diff = (challenge.difficulty or '').strip().title()
        req = self.required_difficulty.strip()
        if req == 'Medium':
            return diff == 'Medium'
        elif req == 'Hard':
            return diff == 'Hard'
        elif 'Medium' in req and 'Hard' in req:
            return diff in ['Medium', 'Hard']
        return diff.lower() == req.lower()

    def get_remaining_seconds(self):
        now = timezone.now()
        if self.deadline > now:
            return max(0, int((self.deadline - now).total_seconds()))
        return 0

    def to_dict(self):
        self.check_and_update_status()
        remaining_secs = self.get_remaining_seconds()
        days_left = remaining_secs // 86400
        hours_left = (remaining_secs % 86400) // 3600
        mins_left = (remaining_secs % 3600) // 60

        return {
            'id': self.id,
            'userId': self.user_id,
            'purchaseId': self.purchase_id,
            'purchaseReference': self.purchase.transaction_reference if self.purchase else None,
            'title': self.title,
            'requiredDifficulty': self.required_difficulty,
            'required_difficulty': self.required_difficulty,
            'requiredCount': self.required_count,
            'required_count': self.required_count,
            'completedCount': self.completed_count,
            'completed_count': self.completed_count,
            'durationDays': self.duration_days,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'rewardAmountInr': float(self.reward_amount_inr),
            'reward_amount_inr': float(self.reward_amount_inr),
            'status': self.status,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None,
            'claimedAt': self.claimed_at.isoformat() if self.claimed_at else None,
            'remainingSeconds': remaining_secs,
            'remainingTimeFormatted': f"{days_left}d {hours_left}h {mins_left}m" if remaining_secs > 0 else "Expired",
            'isClaimable': self.status == 'COMPLETED',
            'hasRewardClaimed': self.status == 'CLAIMED',
            'rewardTransaction': self.reward_transaction.to_dict() if hasattr(self, 'reward_transaction') else None,
        }


class MissionChallengeCompletion(models.Model):
    mission = models.ForeignKey(RewardMission, on_delete=models.CASCADE, related_name='completions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.SET_NULL, null=True, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('mission', 'challenge')
        ordering = ['-completed_at']

    def to_dict(self):
        return {
            'id': self.id,
            'missionId': self.mission_id,
            'challengeId': str(self.challenge_id),
            'challengeTitle': self.challenge.title if self.challenge else '',
            'challengeDifficulty': self.challenge.difficulty if self.challenge else '',
            'challengeTechnology': self.challenge.technology if self.challenge else '',
            'submissionId': self.submission_id,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None,
        }


class SimulatedRewardTransaction(models.Model):
    mission = models.OneToOneField(RewardMission, on_delete=models.CASCADE, related_name='reward_transaction')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='simulated_rewards')
    purchase = models.ForeignKey(BugBytesPurchase, on_delete=models.SET_NULL, null=True, blank=True)
    reward_amount_inr = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='SUCCESS')
    mock_processing_time_ms = models.IntegerField(default=1200)
    notes = models.TextField(default='Demonstration prototype refund. Simulated academic evaluation only — no real money charged or transferred.')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def to_dict(self):
        return {
            'id': self.id,
            'missionId': self.mission_id,
            'userId': self.user_id,
            'purchaseId': self.purchase_id,
            'purchaseReference': self.purchase.transaction_reference if self.purchase else None,
            'rewardAmountInr': float(self.reward_amount_inr),
            'reward_amount_inr': float(self.reward_amount_inr),
            'transactionReference': self.transaction_reference,
            'transaction_reference': self.transaction_reference,
            'status': self.status,
            'mockProcessingTimeMs': self.mock_processing_time_ms,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class PvPBattle(models.Model):
    STATUS_CHOICES = (
        ('WAITING', 'Waiting for Opponent'),
        ('MATCHED', 'Matched - Starting'),
        ('IN_PROGRESS', 'Battle In Progress'),
        ('COMPLETED', 'Battle Completed'),
        ('CANCELLED', 'Battle Cancelled'),
        ('EXPIRED', 'Battle Expired'),
    )

    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pvp_battles_as_p1')
    player2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pvp_battles_as_p2')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='pvp_battles')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WAITING')
    room_code = models.CharField(max_length=10, unique=True)
    difficulty_filter = models.CharField(max_length=50, blank=True, default='')

    # Battle timing
    time_limit_seconds = models.IntegerField(default=600)  # 10 minutes default
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    # Results
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pvp_wins')
    is_draw = models.BooleanField(default=False)

    # Player progress tracking (JSON fields)
    player1_progress = models.JSONField(default=dict, blank=True)  # {tests_passed: 0, tests_total: 0, submitted: false, solve_time: null}
    player2_progress = models.JSONField(default=dict, blank=True)

    xp_reward = models.IntegerField(default=50)
    bugbytes_reward = models.IntegerField(default=15)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def to_dict(self):
        now = timezone.now()
        remaining = 0
        if self.status == 'IN_PROGRESS' and self.started_at:
            elapsed = (now - self.started_at).total_seconds()
            remaining = max(0, self.time_limit_seconds - int(elapsed))

        return {
            'id': self.id,
            'roomCode': self.room_code,
            'room_code': self.room_code,
            'status': self.status,
            'player1': {
                'id': self.player1.id,
                'username': self.player1.username,
                'name': self.player1.display_name or self.player1.username,
                'avatar': self.player1.avatar or '',
                'totalScore': self.player1.total_score,
            },
            'player2': {
                'id': self.player2.id,
                'username': self.player2.username,
                'name': self.player2.display_name or self.player2.username,
                'avatar': self.player2.avatar or '',
                'totalScore': self.player2.total_score,
            } if self.player2 else None,
            'challenge': self.challenge.to_dict() if self.challenge else None,
            'timeLimitSeconds': self.time_limit_seconds,
            'time_limit_seconds': self.time_limit_seconds,
            'remainingSeconds': remaining,
            'remaining_seconds': remaining,
            'startedAt': self.started_at.isoformat() if self.started_at else None,
            'endedAt': self.ended_at.isoformat() if self.ended_at else None,
            'winner': {
                'id': self.winner.id,
                'username': self.winner.username,
                'name': self.winner.display_name or self.winner.username,
            } if self.winner else None,
            'isDraw': self.is_draw,
            'player1Progress': self.player1_progress or {},
            'player2Progress': self.player2_progress or {},
            'xpReward': self.xp_reward,
            'bugbytesReward': self.bugbytes_reward,
            'difficultyFilter': self.difficulty_filter,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
