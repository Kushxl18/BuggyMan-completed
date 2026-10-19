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
    testCases = serializers.SerializerMethodField()
    bugSignature = serializers.SerializerMethodField()
    suspectedComponent = serializers.CharField(source='suspected_component', required=False, allow_blank=True)
    aiSuggestions = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'difficulty', 'technology', 'category',
            'timeEstimate', 'points', 'files', 'testCases', 'bugSignature',
            'suspectedComponent', 'aiSuggestions'
        ]

    def get_testCases(self, obj):
        return obj.to_dict().get('testCases', [])

    def get_bugSignature(self, obj):
        return ""

    def get_aiSuggestions(self, obj):
        return []

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'type', 'read', 'time']
