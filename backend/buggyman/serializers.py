from rest_framework import serializers
from .models import User, Challenge, Notification, Submission

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    totalScore = serializers.IntegerField(source='total_score')
    challengesSolved = serializers.IntegerField(source='challenges_solved')

    class Meta:
        model = User
        fields = [
            'id', 'name', 'username', 'email', 'college', 'bio', 'avatar',
            'totalScore', 'challengesSolved', 'streak', 'skills', 'activities', 'badges'
        ]

    def get_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else (obj.username or "Anonymous User")

class ChallengeSerializer(serializers.ModelSerializer):
    timeEstimate = serializers.CharField(source='time_estimate')
    testCases = serializers.JSONField(source='test_cases')
    bugSignature = serializers.CharField(source='bug_signature', required=False, allow_blank=True)
    suspectedComponent = serializers.CharField(source='suspected_component', required=False, allow_blank=True)
    aiSuggestions = serializers.JSONField(source='ai_suggestions', required=False)

    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'difficulty', 'technology', 'category',
            'timeEstimate', 'points', 'files', 'testCases', 'bugSignature',
            'suspectedComponent', 'aiSuggestions'
        ]

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'type', 'read', 'time']
