from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Profile, Course, PlayerProfile, ShopItem, Purchase,
    Quiz, Question, Option, CompletedQuiz, LeaderboardEntry
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class PlayerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = PlayerProfile
        fields = '__all__'

class ShopItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopItem
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    player = PlayerProfileSerializer()
    item = ShopItemSerializer()

    class Meta:
        model = Purchase
        fields = '__all__'

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    course = CourseSerializer()

    class Meta:
        model = Quiz
        fields = '__all__'

class CompletedQuizSerializer(serializers.ModelSerializer):
    player = PlayerProfileSerializer()
    course = CourseSerializer()

    class Meta:
        model = CompletedQuiz
        fields = '__all__'

class LeaderboardEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderboardEntry
        fields = '__all__'
