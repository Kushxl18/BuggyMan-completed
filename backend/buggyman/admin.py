from django.contrib import admin
from .models import (
    User,
    Challenge,
    Submission,
    ChallengeReport,
    ChallengeReaction,
    BugBytesTransaction,
    UnlockedHint,
    BugBytesPackage,
    BugBytesPurchase,
    RewardMission,
    PvPBattle,
    FeatureChallenge,
    FeatureSubmission,
    Notification
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'display_name', 'challenges_solved', 'total_score', 'role', 'is_staff')
    search_fields = ('username', 'email', 'display_name')
    list_filter = ('role', 'is_staff', 'is_superuser', 'created_at')

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'difficulty', 'technology', 'category', 'points', 'status')
    search_fields = ('title', 'technology', 'category')
    list_filter = ('difficulty', 'technology', 'status')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'challenge', 'success', 'score', 'execution_time', 'created_at')
    search_fields = ('user__username', 'challenge__title')
    list_filter = ('success', 'created_at')

@admin.register(ChallengeReport)
class ChallengeReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'challenge', 'report_type', 'status', 'created_at')
    search_fields = ('user__username', 'challenge__title', 'report_type')
    list_filter = ('status', 'report_type')

@admin.register(ChallengeReaction)
class ChallengeReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'challenge', 'is_like', 'is_starred', 'created_at')
    list_filter = ('is_like', 'is_starred')

@admin.register(PvPBattle)
class PvPBattleAdmin(admin.ModelAdmin):
    list_display = ('id', 'room_code', 'status', 'player1', 'player2', 'winner', 'started_at')
    search_fields = ('room_code', 'player1__username', 'player2__username')
    list_filter = ('status',)

@admin.register(FeatureChallenge)
class FeatureChallengeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'difficulty', 'category', 'points', 'status')
    search_fields = ('title', 'category')
    list_filter = ('difficulty', 'status')

@admin.register(FeatureSubmission)
class FeatureSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'challenge', 'success', 'created_at')
    search_fields = ('user__username', 'challenge__title')
    list_filter = ('success',)

@admin.register(BugBytesTransaction)
class BugBytesTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'transaction_type', 'created_at')
    search_fields = ('user__username', 'transaction_type')
    list_filter = ('transaction_type',)

@admin.register(BugBytesPackage)
class BugBytesPackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'bugbytes', 'price_inr', 'is_active')
    list_filter = ('is_active',)

@admin.register(RewardMission)
class RewardMissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'required_difficulty', 'required_count', 'completed_count', 'status')
    list_filter = ('status', 'required_difficulty')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'type', 'read', 'created_at')
    list_filter = ('read', 'type')
