import uuid
from django.db import models
from django.conf import settings


class Game(models.Model):
    TYPE_CHOICES = [('memory', 'Memory Match'), ('puzzle', 'Puzzle'), ('logic', 'Logic Challenge'), ('word', 'Word Game'), ('math', 'Math Challenge')]
    DIFFICULTY_CHOICES = [('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    game_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    description = models.TextField()
    instructions = models.TextField()
    points_reward = models.IntegerField(default=25)
    time_limit_seconds = models.IntegerField(default=60)
    is_active = models.BooleanField(default=True)
    total_plays = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class GameSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='game_sessions')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='sessions')
    score = models.IntegerField(default=0)
    level_reached = models.IntegerField(default=1)
    points_earned = models.IntegerField(default=0)
    time_taken_seconds = models.IntegerField(default=0)
    is_complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.game.title}"
