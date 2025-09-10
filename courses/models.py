from django.db import models
from django.contrib.auth.models import User

# 📦 User Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# 📦 Course Model
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes", default=30)
    level = models.CharField(max_length=50, choices=[
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced')
    ], default='Beginner')
    content = models.TextField(blank=True, null=True, help_text="Full HTML content for this course")

    def __str__(self):
        return self.title

# 📦 Player Profile to track points
class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(blank=True, null=True)
    
    # Special effects from shop items
    streak_freeze_count = models.IntegerField(default=0, help_text="Number of streak freeze items")
    fired_up_streak_until = models.DateTimeField(blank=True, null=True, help_text="Fired up streak active until")
    experience_festival_until = models.DateTimeField(blank=True, null=True, help_text="Experience festival active until")

    def __str__(self):
        return f"{self.user.username}'s Player Profile"

# 📦 Shop Item Model
class ShopItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField(help_text="Cost in points")
    icon = models.CharField(max_length=100, blank=True, help_text="Emoji or image filename")

    def __str__(self):
        return self.name

# 📦 Purchase History Model
class Purchase(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    item = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user.username} bought {self.item.name} on {self.purchased_at.strftime('%Y-%m-%d')}"

# 📦 Quiz Model (one quiz per course)
class Quiz(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200, default="Course Quiz")

    def __str__(self):
        return f"Quiz for {self.course.title}"

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

# 📦 Quiz Question Model
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

# 📦 Quiz Option Model
class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"

class CompletedQuiz(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='completed_quizzes')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'course')

    def __str__(self):
        return f"{self.player.user.username} completed {self.course.title}"


class LeaderboardEntry(models.Model):
    name = models.CharField(max_length=100, unique=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}: {self.score}"


# 📦 User Settings Model
class UserSettings(models.Model):
    THEME_CHOICES = [
        ('system', 'System'),
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='system')
    email_notifications = models.BooleanField(default=True)
    profile_visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')

    def __str__(self):
        return f"Settings for {self.user.username}"